"""Cliente de la API: ruteo de modelo, caché, presupuesto y guardia de higiene.

Qué modela: nada. Es la plomería entre los prompts y la API.
Entradas: sistema + usuario ya renderizados.
Salidas: dict con la propuesta cruda del modelo.
Supuestos: los de `presupuesto.PRECIOS`.

Tres cosas pasan en cada llamada, en este orden y sin excepción:
  1. `higiene.verificar()` sobre sistema Y usuario. Si nombra la política, muere acá.
  2. Caché en disco por hash. Si hay acierto, no se llama a la API.
  3. `presupuesto.registrar()`. Si se pasó del tope, muere acá.
"""

from __future__ import annotations

import threading
from pathlib import Path
from typing import Any

from behavior import contrato, higiene
from behavior.cache import Cache, clave
from behavior.presupuesto import Presupuesto

# Ruteo de modelos (decisión D4 del plan): el chico para los ~250 llamados de la
# masa, el grande SOLO para las 3-4 historias narradas del pitch.
MODELO_MASA = "claude-haiku-4-5"
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
            return anthropic.Anthropic(default_headers={"Accept-Encoding": "identity"})
        except Exception:  # noqa: BLE001 — sin key o sin SDK: se sigue con caché
            return None

    def proponer(
        self,
        sistema: str,
        usuario: str,
        modelo: str = MODELO_MASA,
        max_tokens: int = 1024,
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

        # 3. Presupuesto: comprobar antes, registrar después.
        with self._lock:
            self.presupuesto.comprobar()
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
        with self._lock:
            self.presupuesto.registrar(modelo, respuesta.usage)
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
        return salida

    def _llamar(self, sistema: str, usuario: str, modelo: str, max_tokens: int):
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
