"""La capa conductual: propone estrategias, encaja el veto, reintenta, agrega.

Qué modela: la decisión de mejor respuesta de UN arquetipo en UNA ronda.
Entradas: un `Arquetipo`, el agregado de la ronda anterior, y el veto del motor.
Salidas: `ResultadoArquetipo` — distribución de estrategias + decisiones vetadas.
Supuestos: máximo 3 reintentos por arquetipo; luego `absorber` (contrato con R2).

El ciclo, que es la tesis del proyecto en 20 líneas:

    propuesta del LLM  ->  veto del motor  ->  ¿factible?
                                              sí -> entra al agregado
                                              no -> reintento con la razón encima
                                                    (máximo 3, luego absorber)

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

MAX_REINTENTOS = 3


class Veto(Protocol):
    """La interfaz con `engine/` (Manuel). Yo la consumo, no la implemento."""

    def __call__(self, decision: dict[str, Any], arquetipo: Arquetipo) -> dict[str, Any]:
        """Devuelve {'factible': bool, 'razon': str|None}."""
        ...


def veto_permisivo(decision: dict[str, Any], arquetipo: Arquetipo) -> dict[str, Any]:
    """Doble de prueba: acepta todo. Solo para construir antes de que exista el
    motor. NO es el veto — el veto vive en `engine/` y lo escribe Manuel."""
    return {"factible": True, "razon": None}


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

    @property
    def varianza(self) -> float:
        return varianza_estrategias({k: float(v) for k, v in self.distribucion.items()})

    @property
    def estrategia_dominante(self) -> str:
        return max(self.distribucion, key=self.distribucion.get)


def renderizar(
    arquetipo: Arquetipo,
    aumento_pct: float,
    ronda: int,
    rondas_totales: int,
    tasa_informalidad: float,
    prob_fiscalizacion: float,
    multa: float,
    historial: str = "",
) -> str:
    """Rellena `prompts/arquetipo.md`. Solo mecánica; jamás el nombre."""
    plantilla = cargar_prompt("arquetipo.md")
    return plantilla.format(
        sector=arquetipo.sector,
        n_trabajadores=arquetipo.n_trabajadores,
        situacion_planta=arquetipo.situacion_planta,
        ingreso_por_trabajador=_plata(arquetipo.ingreso_por_trabajador),
        flujo_caja=_plata(arquetipo.flujo_caja),
        costo_despido=_plata(arquetipo.costo_despido),
        aumento_pct=f"{aumento_pct:g}",
        tasa_informalidad_pct=f"{tasa_informalidad * 100:.1f}",
        prob_fiscalizacion_pct=f"{prob_fiscalizacion * 100:.1f}",
        multa=_plata(multa),
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
) -> ResultadoArquetipo:
    """Una ronda para un arquetipo: N paráfrasis, cada una con su reintento.

    `n_parafrasis=1` para una corrida normal; `n_parafrasis=5` para la corrida
    con barra de error (regla del plan §5: la banda se construye sobre
    paráfrasis del prompt, no sobre temperatura).
    """
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
    )
    res = ResultadoArquetipo(arquetipo_id=arquetipo.id)

    for instruccion in parafrasis(n_parafrasis):
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
                        "estrategias_vetadas": tuple(
                            d["estrategia_propuesta"] for d in res.vetadas
                        ),
                    },
                )
            except (RespuestaInvalida, ValueError) as e:
                # Una respuesta mala es un intento perdido, no una corrida
                # perdida. Se anota y se reintenta como si la hubiera vetado.
                fallos_tecnicos.append(str(e))
                continue
            propuesta = contrato.validar(contrato.construir(arquetipo.id, ronda, cruda))
            veredicto = veto(propuesta, arquetipo)
            propuesta["veto"] = veredicto
            propuesta["intento"] = intento + 1
            if veredicto.get("factible"):
                aceptada = propuesta
                break
            res.vetadas.append(propuesta)
            razones_veto.append(str(veredicto.get("razon") or "sin razón declarada"))

        if aceptada is None:
            aceptada = contrato.decision_fallback(
                arquetipo.id, ronda, razones_veto or fallos_tecnicos
            )
            aceptada["fallos_tecnicos"] = fallos_tecnicos
            res.fallbacks += 1
            res.fallos_tecnicos += len(fallos_tecnicos)
        # Se guardan las dos: la cruda (lo que inventó el modelo) y la familia
        # canónica (para agregar sin fragmentar en sinónimos).
        aceptada["familia"] = contrato.familia(aceptada["estrategia_propuesta"])
        res.decisiones.append(aceptada)

    res.distribucion = dict(Counter(d["familia"] for d in res.decisiones))
    res.distribucion_cruda = dict(
        Counter(d["estrategia_propuesta"] for d in res.decisiones)
    )
    return res
