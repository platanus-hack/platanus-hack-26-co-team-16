"""Cliente de la API: ruteo de modelo, caché, presupuesto y guardia de higiene.

Qué modela: nada. Es la plomería entre los prompts y la API.
Entradas: sistema + usuario ya renderizados.
Salidas: dict con la propuesta cruda del modelo.
Supuestos: los de `presupuesto.PRECIOS`.

Cuatro cosas pasan en cada llamada, en este orden y sin excepción:
  1. `higiene.verificar()` sobre sistema Y usuario. Si nombra la política, muere acá.
  2. Caché en disco por hash. Si hay acierto, no se llama a la API.
  3. La salida se valida ANTES de cachearse. Una respuesta inválida no toca el disco.
  4. `presupuesto.registrar()`, después de cachear. Si se pasó del tope, muere acá.
     La plata se APARTA antes de llamar (`reservar()`) para que N llamadas en
     vuelo no puedan pasarse del tope entre todas (DEFECTOS.md §3.7).
"""

from __future__ import annotations

import threading
from pathlib import Path
from typing import Any

from behavior import contrato, higiene
from behavior.cache import Cache, clave
from behavior.presupuesto import Presupuesto

# Ruteo de modelos (decisión D4 del plan): un modelo para los ~250 llamados de
# la masa, el grande SOLO para las 3-4 historias narradas del pitch.
#
# La masa pasó de Haiku 4.5 a Sonnet 5. Cuesta 3x más por token (3,00/15,00
# contra 1,00/5,00 por millón), así que una corrida de 121 llamadas sube de
# ~USD 0,33 a ~USD 1,00 y el tope duro de `presupuesto.py` sigue mandando.
# OJO: cambiar el modelo CAMBIA LA CLAVE DE CACHÉ (`cache.clave()` la incluye),
# así que las respuestas cacheadas con Haiku no se reutilizan: la primera
# corrida con Sonnet se paga entera.
MODELO_MASA = "claude-sonnet-5"
MODELO_RELATO = "claude-opus-5"

_PROMPTS = Path(__file__).parent / "prompts"


def cargar_prompt(nombre: str) -> str:
    return (_PROMPTS / nombre).read_text(encoding="utf-8").strip()


def parafrasis(n: int = 5) -> list[str]:
    """Las N paráfrasis de la instrucción. La barra de error se construye sobre
    esto, no sobre temperatura (regla del plan §5, insumo de Daniel)."""
    rutas = sorted((_PROMPTS / "parafrasis").glob("*.md"))
    if len(rutas) < n:
        raise ValueError(f"se pidieron {n} paráfrasis y solo hay {len(rutas)} en {_PROMPTS}")
    return [r.read_text(encoding="utf-8").strip() for r in rutas[:n]]


class SinCredenciales(RuntimeError):
    """No hay API key y el prompt no estaba en el caché."""


class RespuestaInvalida(RuntimeError):
    """El modelo respondió algo que no es una propuesta usable.

    Se trata como intento fallido y se reintenta; no tumba la corrida.
    """


class ClienteConductual:
    """Envuelve la API de Anthropic con las tres reglas de oro de `behavior/`."""

    def __init__(
        self,
        presupuesto: Presupuesto | None = None,
        cache: Cache | None = None,
        cliente_api: Any = None,
    ):
        self.presupuesto = presupuesto or Presupuesto()
        self.cache = cache or Cache()
        self._api = cliente_api
        self._api_intentada = cliente_api is not None
        # Los arquetipos de una ronda se resuelven en paralelo: el caché y el
        # presupuesto son estado compartido y se tocan bajo candado.
        self._lock = threading.Lock()
        # Candado aparte para la construcción perezosa del cliente: sin él, dos
        # hilos entran a la vez, el primero marca `_api_intentada` y el segundo
        # ve `_api=None` y cree que no hay credenciales.
        self._lock_api = threading.Lock()

    @property
    def api(self):
        """Cliente perezoso: sin key, el caché todavía sirve para reproducir."""
        with self._lock_api:
            if not self._api_intentada:
                self._api_intentada = True
                self._api = self._construir_api()
        return self._api

    @staticmethod
    def _construir_api():
        try:
            import anthropic

            # `Accept-Encoding: identity` desactiva la compresión de la
            # respuesta. No es una decisión de diseño: algunas instalaciones
            # (anaconda + httpx2) traen un decodificador roto que revienta con
            # `TypeError: process() takes no keyword arguments` antes de que la
            # respuesta llegue al SDK. Sin compresión el camino funciona; el
            # costo es unos KB más de red por llamada.
            # SUPUESTO: 90 s es tiempo de sobra para una respuesta sana y sigue
            # siendo un corte, no una espera.
            #
            # Sin esto el SDK hereda su default: 600 s de read timeout y 2
            # reintentos, o sea que UNA llamada colgada retiene un worker del
            # pool hasta 20 minutos. En una corrida de 12 olas eso no es lentitud,
            # es la demo muerta.
            #
            # Por qué 90 y no 60. Un timeout acá NO cae al fallback: no lo atrapa
            # `capa.py:322` (que solo mira `RespuestaInvalida/ValueError/
            # TypeError`) ni `trayectorias.py` (que solo mira
            # `PresupuestoAgotado`), así que se propaga y mata la trayectoria
            # completa. O sea que un timeout corto de más no degrada el
            # resultado: cancela la corrida en vivo. La latencia medida es 23,3 s
            # por OLA con paralelismo 8, y la maqueta sube a 18 conexiones
            # simultáneas (9 celdas x 2 trayectorias), donde la latencia por
            # llamada sube. 90 s deja ~4x de margen sobre lo medido en vez de
            # 2,6x, y aun así corta un worker colgado 6,7x antes que el default.
            #
            # `max_retries=1` y no 2: el reintento del SDK es sobre errores de
            # red, y encima de él ya existe el reintento del veto
            # (`MAX_REINTENTOS = 3`), que es el que de verdad cuesta plata y ya
            # está contado en `FACTOR_REINTENTO`. Dos capas de reintento
            # multiplican el peor caso sin multiplicar la información.
            return anthropic.Anthropic(
                default_headers={"Accept-Encoding": "identity"},
                timeout=90.0,
                max_retries=1,
            )
        except Exception:  # noqa: BLE001 — sin key o sin SDK: se sigue con caché
            return None

    def proponer(
        self,
        sistema: str,
        usuario: str,
        modelo: str = MODELO_MASA,
        # 2048 y no 1024: con Sonnet 5 las respuestas que SÍ pasaron llegaron a
        # 1012 tokens de salida (mediana 735, p90 939), o sea pegadas al techo
        # anterior. Las que lo cruzaban volvían con el JSON cortado, `_extraer_json`
        # las tumbaba como `RespuestaInvalida` y la decisión se iba al fallback:
        # 44 de 156 intentos (28%) en la primera corrida con Sonnet, contra 0 de
        # 121 con Haiku. El techo no cambia la clave de caché, así que subirlo no
        # invalida lo ya cacheado.
        max_tokens: int = 2048,
        contexto: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Una propuesta de estrategia. Devuelve el JSON crudo del modelo.

        `contexto` lo ignora este cliente; existe para que la ablación
        (`behavior/ablacion.py`) sea un reemplazo directo sin tocar `capa.py`.
        """
        # 1. Higiene. Antes que nada, siempre, sin bandera para desactivarlo.
        higiene.verificar(sistema, "prompt de sistema")
        higiene.verificar(usuario, "prompt de arquetipo")

        # 2. Caché en disco.
        k = clave(modelo, sistema, usuario, contrato.ESQUEMA_SALIDA)
        with self._lock:
            guardado = self.cache.leer(k)
        if guardado is not None:
            return guardado["salida"]

        if self.api is None:
            raise SinCredenciales(
                "sin ANTHROPIC_API_KEY y el prompt no está en el caché "
                f"({self.cache.dir}). Corre `ant auth login` o exporta la key, "
                "o importa un caché con `Cache().importar(...)`."
            )

        # 3. Presupuesto: RESERVAR antes, registrar después.
        #
        # Antes acá decía `comprobar()`, que solo mira lo ya gastado. Con N
        # llamadas en vuelo —hasta `paralelismo x trayectorias`, o sea 40— los N
        # hilos pasaban la comprobación mientras el gasto todavía era cero y
        # después registraban todos: el tope se pasaba por N veces el costo de
        # una llamada y el «corte duro» no cortaba (DEFECTOS.md §3.7).
        # `reservar()` aparta la plata dentro del mismo `with self._lock` que la
        # comprueba, así que dos hilos no pueden ver el mismo margen libre.
        with self._lock:
            reservado = self.presupuesto.reservar()
        # La reserva se mantiene VIVA hasta que `registrar()` la absorba, y el
        # `finally` de más abajo la devuelve por cualquier otro camino: timeout,
        # red, JSON ilegible o respuesta que no construye una decisión. Si no se
        # devolviera, una corrida con fallos se estrangularía sola sin haber
        # gastado un peso.
        try:
            try:
                respuesta = self._llamar(sistema, usuario, modelo, max_tokens)
            except TypeError as e:  # el SDK no resuelve credenciales sino al pedir
                if "authentication" in str(e).lower():
                    raise SinCredenciales(
                        "sin credenciales de Anthropic y el prompt no está en el caché "
                        f"({self.cache.dir}). Corre `ant auth login` o exporta ANTHROPIC_API_KEY."
                    ) from e
                raise
            salida = self._extraer_json(respuesta)
            # 4. Validar ANTES de cachear. Una salida que no construye una
            # decisión usable no puede llegar al disco: si se cachea, la falla
            # queda grabada y **toda re-corrida determinista revienta en el
            # mismo punto**, sin gastar una llamada que la arregle. O sea que se
            # dispara justo donde más duele, en la re-corrida barata sin API. Se
            # valida con el mismo `contrato.construir()` que consume `capa.py`,
            # para que no existan dos definiciones distintas de "respuesta usable".
            try:
                contrato.construir("_validacion", 0, salida)
            except (ValueError, TypeError) as e:
                raise RespuestaInvalida(
                    f"la salida del modelo no construye una decisión válida: {e}; "
                    f"cruda: {salida!r}"
                ) from e

            with self._lock:
                # Cachear antes de registrar, no al revés: si el corte duro del
                # presupuesto dispara acá, esta respuesta YA está pagada. Con el
                # orden inverso se descartaba y se volvía a pagar en la corrida
                # siguiente.
                self.cache.escribir(
                    k,
                    {
                        "modelo": modelo,
                        "salida": salida,
                        "usage": {
                            "input_tokens": respuesta.usage.input_tokens,
                            "output_tokens": respuesta.usage.output_tokens,
                            "cache_read_input_tokens": getattr(
                                respuesta.usage, "cache_read_input_tokens", 0
                            ),
                        },
                    },
                )
                # `registrar()` absorbe la reserva: a partir de acá el gasto es
                # real y no estimado. Se pone en 0 para que el `finally` no la
                # devuelva otra vez y el bote quede inflado.
                self.presupuesto.registrar(modelo, respuesta.usage, reservado)
                reservado = 0.0
            return salida
        finally:
            if reservado:
                with self._lock:
                    self.presupuesto.liberar(reservado)

    def _llamar(self, sistema: str, usuario: str, modelo: str, max_tokens: int):
        # NO se pasa `temperature` (ni `top_p` ni `top_k`), y no es un olvido.
        # Sonnet 5 —el `MODELO_MASA` de arriba— eliminó los parámetros de
        # sampling: mandarlos devuelve 400 y tumba las 465 llamadas de la
        # corrida entera, no una. `temperature=0` era la forma de comprar
        # determinismo en modelos viejos; acá el determinismo lo da el caché en
        # disco (ver `behavior/cache.py`), que es de dónde sale el nivel 2 de la
        # ADR 0009. Y la banda del proyecto se mide sobre N trayectorias
        # completas, nunca sobre temperatura — es una restricción declarada en
        # AGENTS.md, no una preferencia.
        return self.api.messages.create(
            model=modelo,
            max_tokens=max_tokens,
            # El contexto del mundo se repite en las ~250 llamadas: se marca
            # para prompt caching de la API. OJO: en Haiku 4.5 el mínimo
            # cacheable es 4096 tokens, y nuestro prefijo es más corto — así que
            # esto probablemente NO cachee. Lo dejamos porque es gratis y se
            # mide en `usage.cache_read_input_tokens`; la palanca real de costo
            # es el caché en disco de arriba. Está medido, no supuesto.
            system=[{"type": "text", "text": sistema, "cache_control": {"type": "ephemeral"}}],
            messages=[{"role": "user", "content": usuario}],
            output_config={"format": {"type": "json_schema", "schema": contrato.ESQUEMA_SALIDA}},
        )

    @staticmethod
    def _extraer_json(respuesta) -> dict[str, Any]:
        """Saca el JSON de la respuesta, con errores que dicen qué pasó.

        En una corrida de ~1.160 llamadas apareció una respuesta que no
        parseaba y tumbó la corrida entera. Un modelo que falla 1 de cada mil
        veces es normal; que eso mate 20 minutos de trabajo no lo es. Ahora el
        error es `RespuestaInvalida`, que `capa.py` trata como intento fallido y
        reintenta.
        """
        import json

        if getattr(respuesta, "stop_reason", None) == "refusal":
            raise RespuestaInvalida(
                f"el modelo rechazó el prompt: {getattr(respuesta, 'stop_details', None)}"
            )
        if getattr(respuesta, "stop_reason", None) == "max_tokens":
            raise RespuestaInvalida(
                "respuesta cortada por max_tokens: el JSON quedó incompleto"
            )
        texto = next((b.text for b in respuesta.content if b.type == "text"), "")
        if not texto.strip():
            raise RespuestaInvalida(
                f"respuesta vacía (stop_reason={getattr(respuesta, 'stop_reason', None)})"
            )
        try:
            return json.loads(texto)
        except json.JSONDecodeError as e:
            raise RespuestaInvalida(
                f"el modelo no devolvió JSON válido ({e}); texto: {texto[:200]!r}"
            ) from e
