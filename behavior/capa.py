"""La capa conductual: propone estrategias, encaja el veto, reintenta, agrega.

Qué modela: la decisión de mejor respuesta de UN arquetipo en UNA ronda.
Entradas: un `Arquetipo`, el agregado de la ronda anterior, y el veto del motor.
Salidas: `ResultadoArquetipo` — distribución de estrategias + decisiones vetadas.
Supuestos: máximo 3 reintentos por arquetipo; luego `cumplir` (contrato con R2).

El ciclo, que es la tesis del proyecto en 20 líneas:

    propuesta del LLM  ->  veto del motor  ->  ¿factible?
                                              sí -> entra al agregado
                                              no -> reintento con la razón encima
                                                    (máximo 3, luego cumplir)

Yo NO aplico nada al estado del mundo. Propongo; Manuel veta y aplica.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Any, Callable, Protocol

from behavior import contrato
from behavior.arquetipos import Arquetipo, varianza_estrategias
from behavior.cliente import (
    ClienteConductual,
    RespuestaInvalida,
    cargar_prompt,
    parafrasis,
)
# A3: la caja se habla en UNA sola unidad, la del reloj del proyecto (una ronda
# es un trimestre, ADR 0005). `MESES_POR_RONDA` se importa del motor en vez de
# redefinirse acá: era la tercera definición de la misma cantidad.
from engine.veto import MESES_POR_RONDA

MAX_REINTENTOS = 3


class Veto(Protocol):
    """La interfaz con `engine/` (Manuel). Yo la consumo, no la implemento.

    Dos cosas que R2 necesita saber de esta firma:

    1. **`arquetipo.formal` es el estado INICIAL**, no el de la ronda en curso.
       Una unidad que se informalizó en la ronda 1 llega acá en la ronda 2 con
       `formal=True`. Si el veto necesita juzgar *"esta unidad ya opera fuera de
       regla"*, tiene que sacarlo de su propio estado del mundo, no de este
       objeto — o la firma tiene que llevarlo. Hoy `behavior/` lleva el estado
       vivo por su cuenta (`rondas.correr()`), así que **hay dos estados que
       pueden divergir** y conviene cerrar de dónde sale el que manda.
    2. **`razon` sale hacia el modelo** en el reintento, así que pasa por
       `higiene.verificar()`. Una razón con `$`, un año de 4 dígitos o la palabra
       "gobierno" mata la corrida entera. R2 se comprometió a producir razones
       que pasan limpias y a probarlo con un test.
    """

    def __call__(self, decision: dict[str, Any], arquetipo: Arquetipo) -> dict[str, Any]:
        """Devuelve {'factible': bool, 'razon': str|None}."""
        ...


def veto_permisivo(decision: dict[str, Any], arquetipo: Arquetipo) -> dict[str, Any]:
    """Doble de prueba: acepta todo. Solo para construir antes de que exista el
    motor. NO es el veto — el veto vive en `engine/` y lo escribe Manuel."""
    return {"factible": True, "razon": None}


def situacion_planta(fraccion_informal: float) -> str:
    """El texto que ve el agente sobre su propia planta, según su estado VIVO.

    No sale del `Arquetipo`: sale del estado que dejó la ronda anterior. Un
    arquetipo que informalizó su planta en la ronda 1 leía "toda formal" en la
    ronda 2 —en la misma pantalla donde su historial decía "informalizar"—, y
    respondiendo "mantener" volvía a contar como cumpliendo. Eso hacía bajar la
    tasa de informalidad por una razón espuria.
    """
    if fraccion_informal <= 0.0:
        return "toda formal"
    if fraccion_informal >= 1.0:
        return "toda informal"
    return f"parte formal, parte informal ({fraccion_informal:.0%} fuera de regla)"


def _plata(x: float) -> str:
    """Miles con punto: evita que un monto de 4 dígitos parezca un año y
    dispare la guardia de higiene."""
    return f"{x:,.0f}".replace(",", ".")


@dataclass
class ResultadoArquetipo:
    arquetipo_id: str
    distribucion: dict[str, int] = field(default_factory=dict)
    decisiones: list[dict[str, Any]] = field(default_factory=list)
    distribucion_cruda: dict[str, int] = field(default_factory=dict)
    vetadas: list[dict[str, Any]] = field(default_factory=list)
    fallbacks: int = 0
    fallos_tecnicos: int = 0
    # A2: decisiones en las que NINGUNA opción del orden de fallback resultó
    # factible. No es un error: dice que la política es impagable para esta
    # celda con cualquier jugada disponible, y por eso se cuenta y se publica.
    sin_salida: int = 0

    @property
    def varianza(self) -> float:
        return varianza_estrategias({k: float(v) for k, v in self.distribucion.items()})

    @property
    def estrategia_dominante(self) -> str:
        return max(self.distribucion, key=self.distribucion.get)


# --- C6: el candado 3(b), el test de re-skinning -----------------------------


@dataclass(frozen=True)
class Reskin:
    """Renombra los sectores y reescala TODOS los montos por un factor arbitrario.

    Por qué existe: `VALIDATION.md` promete el candado 3(b) y no había una línea
    de código. La guardia de `higiene.py` filtra TÉRMINOS —"salario mínimo",
    "decreto", años de cuatro dígitos— pero no MAGNITUDES, y los montos viajan
    en pesos reales: la moda del parquet es 1.750.000, que es exactamente el
    piso salarial de 2026. Un modelo con memoria del país puede reconocer el
    escenario por los números aunque nunca lea su nombre.

    Como todo lo que ve el agente está en unidades abstractas ("u"), multiplicar
    cada monto por un factor arbitrario no debería cambiar NINGUNA decisión: las
    razones de precios entre opciones son idénticas. Si el agregado se mueve,
    hubo memorización, y lo reportamos nosotros antes de que lo pregunten.

    El factor y las etiquetas se derivan del `seed` para que la corrida siga
    siendo reproducible: mismo seed, mismo re-skin, mismo resultado.
    """

    factor: float = 1.0
    etiquetas: dict[str, str] = field(default_factory=dict)

    @classmethod
    def desde_seed(cls, sectores: list[str], seed: int = 42) -> Reskin:
        """Un re-skin determinista: mismo seed, mismas etiquetas y mismo factor."""
        import hashlib

        crudo = hashlib.blake2b(str(seed).encode(), digest_size=8).digest()
        # Un factor entre 0,1 y 10 en escala logarítmica: cambia el orden de
        # magnitud de los montos sin volverlos absurdos ni cero.
        bruto = int.from_bytes(crudo, "big") / 2**64
        factor = float(10 ** (bruto * 2 - 1))
        nombres = [f"actividad-{chr(ord('A') + i)}" for i in range(len(sectores))]
        return cls(factor=factor, etiquetas=dict(zip(sorted(set(sectores)), nombres)))

    def monto(self, x: float) -> float:
        return x * self.factor

    def sector(self, nombre: str) -> str:
        return self.etiquetas.get(nombre, nombre)


def renderizar(
    arquetipo: Arquetipo,
    aumento_pct: float,
    ronda: int,
    rondas_totales: int,
    tasa_informalidad: float,
    prob_fiscalizacion: float,
    multa: float,
    historial: str = "",
    fraccion_informal_previa: float | None = None,
    reskin: Reskin | None = None,
) -> str:
    """Rellena `prompts/arquetipo.md`. Solo mecánica; jamás el nombre.

    `reskin` (C6) renombra el sector y reescala todos los montos. Como el agente
    solo ve unidades abstractas, el agregado no debería moverse: es el candado
    3(b) de `VALIDATION.md`.

    `fraccion_informal_previa` es el estado VIVO de la planta al empezar esta
    ronda. Si no se da, se cae al estado inicial del arquetipo — que es correcto
    solo en la primera ronda.
    """
    if fraccion_informal_previa is None:
        fraccion_informal_previa = 0.0 if arquetipo.formal else 1.0
    plantilla = cargar_prompt("arquetipo.md")
    r = reskin or Reskin()
    return plantilla.format(
        sector=r.sector(arquetipo.sector),
        n_trabajadores=arquetipo.n_trabajadores,
        situacion_planta=situacion_planta(fraccion_informal_previa),
        ingreso_por_trabajador=_plata(r.monto(arquetipo.ingreso_por_trabajador)),
        # A3: la MISMA cifra que usa `engine.veto.caja_de_la_ronda()`. Antes al
        # agente se le mostraba el flujo mensual y el veto lo juzgaba con tres
        # meses de ese flujo, así que sus justificaciones ("no me alcanza para
        # indemnizar") contradecían al árbitro con toda la razón: estaban
        # mirando billeteras distintas.
        flujo_caja=_plata(r.monto(arquetipo.flujo_caja * MESES_POR_RONDA)),
        costo_despido=_plata(r.monto(arquetipo.costo_despido)),
        aumento_pct=f"{aumento_pct:g}",
        tasa_informalidad_pct=f"{tasa_informalidad * 100:.1f}",
        prob_fiscalizacion_pct=f"{prob_fiscalizacion * 100:.1f}",
        multa=_plata(r.monto(multa)),
        ronda=ronda,
        rondas_totales=rondas_totales,
        historial=historial,
    )


def decidir_arquetipo(
    arquetipo: Arquetipo,
    cliente: ClienteConductual,
    veto: Veto = veto_permisivo,
    *,
    aumento_pct: float,
    ronda: int,
    rondas_totales: int = 4,
    tasa_informalidad: float,
    prob_fiscalizacion: float,
    multa: float,
    historial: str = "",
    n_parafrasis: int = 1,
    parafrasis_fija: str | None = None,
    fraccion_informal_previa: float | None = None,
    reskin: Reskin | None = None,
) -> ResultadoArquetipo:
    """Una ronda para un arquetipo: N paráfrasis, cada una con su reintento.

    `n_parafrasis=1` para una corrida normal; `n_parafrasis=5` para la corrida
    con barra de error (regla del plan §5: la banda se construye sobre
    paráfrasis del prompt, no sobre temperatura).

    `parafrasis_fija` define una trayectoria completa desde afuera. En ese caso
    `n_parafrasis` se ignora: pedir N redacciones dentro de una trayectoria no
    tiene significado porque la trayectoria está definida por UNA redacción.
    Esta costura reemplaza el parche al global de módulo que obligaba a ejecutar
    las trayectorias en serie en `api/trayectorias.py`.

    `fraccion_informal_previa` es el estado vivo de la planta al empezar la
    ronda: entra al texto del prompt y al `contexto` que consume la ablación.
    """
    if fraccion_informal_previa is None:
        fraccion_informal_previa = 0.0 if arquetipo.formal else 1.0
    sistema = cargar_prompt("sistema.md")
    base = renderizar(
        arquetipo,
        aumento_pct,
        ronda,
        rondas_totales,
        tasa_informalidad,
        prob_fiscalizacion,
        multa,
        historial,
        fraccion_informal_previa,
        reskin,
    )
    res = ResultadoArquetipo(arquetipo_id=arquetipo.id)

    # Una trayectoria está DEFINIDA por su paráfrasis. Si viene fijada, pedir N
    # paráfrasis adentro no significa nada y `n_parafrasis` queda neutralizado;
    # sin ella se conserva exactamente el camino histórico de esta función.
    instrucciones = (
        [parafrasis_fija]
        if parafrasis_fija is not None
        else parafrasis(n_parafrasis)
    )
    for instruccion in instrucciones:
        # Dos listas a propósito. `razones_veto` SÍ se le muestra al agente: es
        # la razón física por la que no pudo, y es justo lo que un economista no
        # le daría. `fallos_tecnicos` NO se le muestra nunca: decirle "tu
        # respuesta no parseó" le revelaría que es un modelo respondiendo a un
        # prompt, y eso es una meta-fuga aunque no nombre la política.
        razones_veto: list[str] = []
        fallos_tecnicos: list[str] = []
        aceptada = None
        for intento in range(MAX_REINTENTOS):
            usuario = f"{base}\n\n## Tu decisión\n\n{instruccion}"
            if razones_veto:
                # El reintento NO repite la propuesta: le dice al agente por qué
                # no pudo, que es la información que un economista no le daría.
                usuario += (
                    "\n\nYa intentaste otra salida y no fue posible:\n"
                    + "\n".join(f"- {r}" for r in razones_veto)
                    + "\nElige una estrategia distinta que sí puedas pagar."
                )
            try:
                cruda = cliente.proponer(
                    sistema,
                    usuario,
                    # Solo lo usa la ablación (`behavior/ablacion.py`); el cliente
                    # real lo ignora. Así las dos corridas comparten este archivo.
                    contexto={
                        "arquetipo": arquetipo,
                        "aumento_pct": aumento_pct,
                        "tasa_informalidad": tasa_informalidad,
                        "prob_fiscalizacion": prob_fiscalizacion,
                        "multa": multa,
                        "ronda": ronda,
                        "fraccion_informal_previa": fraccion_informal_previa,
                        "estrategias_vetadas": tuple(
                            d["estrategia_propuesta"] for d in res.vetadas
                        ),
                    },
                )
                # `construir()` y `validar()` van DENTRO del try a propósito.
                # Afuera, un `estrategia_propuesta` vacío —que el esquema JSON
                # permite, no tiene `minLength`— escapaba del `for intento`, del
                # `for instruccion` y de esta función entera, y mataba la corrida
                # en el primer fallo. Adentro es un intento perdido, como un veto.
                propuesta = contrato.validar(
                    contrato.construir(arquetipo.id, ronda, cruda)
                )
                # La familia canónica se calcula ANTES del veto, no después.
                # El veto de A1 la necesita para costear `cumplir` y `absorber`
                # —las dos jugadas que no traen detalle numérico— y no puede
                # derivarla él mismo: `familia()` es de esta capa y duplicarla
                # en `engine/` daría dos canonicalizaciones que pueden divergir.
                # Calcularla aquí es también lo que hace que el veto siga sin
                # leer nombres: recibe una etiqueta ya canónica, no una cadena
                # que el modelo inventó.
                propuesta["familia"] = contrato.familia(
                    propuesta["estrategia_propuesta"]
                )
            except (RespuestaInvalida, ValueError, TypeError) as e:
                # Una respuesta mala es un intento perdido, no una corrida
                # perdida. Se anota y se reintenta como si la hubiera vetado.
                fallos_tecnicos.append(str(e))
                continue
            veredicto = veto(propuesta, arquetipo)
            propuesta["veto"] = veredicto
            propuesta["intento"] = intento + 1
            if veredicto.get("factible"):
                aceptada = propuesta
                break
            res.vetadas.append(propuesta)
            razones_veto.append(str(veredicto.get("razon") or "sin razón declarada"))

        # Fuera del `if`: el caso común es un fallo seguido de un reintento que
        # SÍ funciona, y contándolo solo al llegar al fallback ese caso quedaba
        # en cero. La tasa de fallo del modelo que reporta el README salía
        # subcontada por ese camino.
        res.fallos_tecnicos += len(fallos_tecnicos)
        if aceptada is None:
            # A2: el fallback consulta al veto en vez de mandar a `cumplir` a
            # ciegas. Se le pasan el veto y el arquetipo justamente para que la
            # opción terminal sea una que la firma pueda pagar.
            aceptada = contrato.decision_fallback(
                arquetipo.id,
                ronda,
                razones_veto or fallos_tecnicos,
                veto=veto,
                arquetipo=arquetipo,
            )
            aceptada["fallos_tecnicos"] = fallos_tecnicos
            res.fallbacks += 1
            if aceptada.get("sin_salida"):
                res.sin_salida += 1
        # Se guardan las dos: la cruda (lo que inventó el modelo) y la familia
        # canónica (para agregar sin fragmentar en sinónimos). Las propuestas
        # que pasaron por el veto ya la traen; esto cubre al fallback, que no
        # pasa por ahí.
        aceptada.setdefault(
            "familia", contrato.familia(aceptada["estrategia_propuesta"])
        )
        res.decisiones.append(aceptada)

    res.distribucion = dict(Counter(d["familia"] for d in res.decisiones))
    res.distribucion_cruda = dict(
        Counter(d["estrategia_propuesta"] for d in res.decisiones)
    )
    return res
