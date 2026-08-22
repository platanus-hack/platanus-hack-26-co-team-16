"""El bucle de mejor respuesta: 4 rondas, no una prueba de convergencia.

Qué modela: la dinámica de mejor respuesta entre arquetipos. Cada ronda, cada
  arquetipo ve el agregado de la ronda anterior y decide de nuevo.
Entradas: los arquetipos, la política (aumento_pct), y el motor de Manuel.
Salidas: una lista de `ronda.json` (`docs/PLAN.md` §4) + el desglose por arquetipo.
Supuestos: el agregado que ve un arquetipo es el de la ronda anterior completa
  (mejor respuesta simultánea, no secuencial). Declarado en `VALIDATION.md`.

Honestidad de vocabulario (decisión D5 del plan)
------------------------------------------------
Esto es **dinámica de mejor respuesta a 3-4 rondas**. NO es una prueba de
existencia ni de convergencia a un equilibrio de Nash. Puede no converger, y si
no converge lo reportamos: `converge()` mira si la última ronda movió la tasa de
informalidad menos que un umbral, y esa respuesta va al pitch tal como salga.

La cascada sale de acá: la capacidad de fiscalización es fija, así que cuando
más arquetipos se salen de regla, la probabilidad de sanción de cada uno baja, y
eso vuelve a entrar como insumo de la siguiente ronda.
"""

from __future__ import annotations

from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Any, Callable

from behavior import contrato
from behavior.arquetipos import Arquetipo
from behavior.capa import ResultadoArquetipo, Veto, decidir_arquetipo, veto_permisivo

# Quién queda fuera de regla lo decide `contrato.fraccion_fuera_de_regla()`,
# que trabaja sobre la FAMILIA canónica de la estrategia y sobre el estado del
# que viene el agente. El motor tiene la última palabra sobre el estado del
# mundo; esto es solo el agregado que vuelve a los agentes la ronda siguiente.


@dataclass
class Ronda:
    """Un `contracts/ronda.json` más el desglose por arquetipo (dato A4)."""

    simulacion_id: str
    seed: int
    ronda: int
    politica: dict[str, Any]
    tasa_informalidad: float
    prob_fiscalizacion: float
    empleo_relativo: float
    banda: dict[str, float]
    por_arquetipo: dict[str, ResultadoArquetipo] = field(default_factory=dict)

    def a_contrato(self) -> dict[str, Any]:
        """Solo los campos de `contracts/ronda.json`, para la API y el frontend."""
        return {
            "simulacion_id": self.simulacion_id,
            "seed": self.seed,
            "ronda": self.ronda,
            "politica": self.politica,
            "tasa_informalidad": round(self.tasa_informalidad, 4),
            "prob_fiscalizacion": round(self.prob_fiscalizacion, 4),
            "empleo_relativo": round(self.empleo_relativo, 4),
            "banda": {
                k: (v if isinstance(v, bool) else round(v, 4))
                for k, v in self.banda.items()
            },
        }

    def desglose_estrategias(self) -> dict[str, int]:
        """Dato A4: qué estrategia domina, agregado sobre todos los arquetipos."""
        total: Counter[str] = Counter()
        for r in self.por_arquetipo.values():
            total.update(r.distribucion)
        return dict(total.most_common())

    @property
    def varianza_media(self) -> float:
        """¿Colapsó la varianza? 0 = todos los arquetipos hicieron una sola cosa."""
        vs = [r.varianza for r in self.por_arquetipo.values()]
        return sum(vs) / len(vs) if vs else 0.0


def _prob_fiscalizacion(capacidad: float, peso_fuera_de_regla: float, peso_total: float) -> float:
    """Fiscalización endógena: capacidad FIJA repartida entre los evasores.

    Acá nace la cascada. El motor de Manuel tiene la versión que manda; esta es
    la que la capa usa para armar el agregado que ven los agentes.
    """
    if peso_fuera_de_regla <= 0:
        return 1.0
    return min(1.0, capacidad * peso_total / peso_fuera_de_regla)


def correr(
    arquetipos: list[Arquetipo],
    cliente,
    *,
    aumento_pct: float,
    seed: int = 42,
    simulacion_id: str = "sim-local",
    rondas_totales: int = 4,
    veto: Veto = veto_permisivo,
    capacidad_fiscalizacion: float = 0.02,
    multa_factor: float = 12.0,
    tasa_informalidad_inicial: float = 0.42,
    n_parafrasis: int = 1,
    paralelismo: int = 8,
    al_terminar_ronda: Callable[[Ronda], None] | None = None,
) -> list[Ronda]:
    """Corre las rondas de mejor respuesta y devuelve el agregado de cada una.

    `capacidad_fiscalizacion` es la fracción del universo que se alcanza a
    inspeccionar por periodo. Es FIJA: no se ajusta a mano entre rondas. Ese es
    el compromiso metodológico que hace la cascada un resultado y no un supuesto.
    """
    peso_total = sum(a.peso for a in arquetipos) or 1.0
    tasa = tasa_informalidad_inicial
    historial: dict[str, list[str]] = {a.id: [] for a in arquetipos}
    salida: list[Ronda] = []

    for n in range(rondas_totales):
        prob = _prob_fiscalizacion(capacidad_fiscalizacion, tasa * peso_total, peso_total)

        # Las RONDAS son secuenciales por definición (cada una responde al
        # agregado de la anterior), pero los ARQUETIPOS dentro de una ronda son
        # independientes: se resuelven en paralelo. Con 48 arquetipos eso baja
        # una corrida en frío de ~10 min a ~1,5 min sin cambiar el resultado —
        # el orden de recorrido no entra en ninguna semilla (ver
        # `arquetipos._semilla`), así que sigue siendo determinista.
        def _uno(a: Arquetipo) -> tuple[str, ResultadoArquetipo]:
            previo = historial[a.id]
            texto_historial = (
                "\n- Lo que hiciste en periodos anteriores: " + ", ".join(previo)
                if previo
                else ""
            )
            return a.id, decidir_arquetipo(
                a,
                cliente,
                veto,
                aumento_pct=aumento_pct,
                ronda=n,
                rondas_totales=rondas_totales,
                tasa_informalidad=tasa,
                prob_fiscalizacion=prob,
                # SUPUESTO: la sanción equivale a `multa_factor` meses de
                # ingreso por trabajador (por defecto 12). Es el parámetro que
                # decide si evadir paga, así que es de los primeros que R5 debe
                # someter a análisis de sensibilidad. El valor que manda es el
                # del motor de Manuel; acá entra como dato.
                multa=a.ingreso_por_trabajador * multa_factor,
                historial=texto_historial,
                n_parafrasis=n_parafrasis,
            )

        if paralelismo > 1:
            with ThreadPoolExecutor(max_workers=paralelismo) as pool:
                pares = list(pool.map(_uno, arquetipos))
        else:
            pares = [_uno(a) for a in arquetipos]

        # Se reconstruye en el orden de `arquetipos`, no en el de terminación:
        # el paralelismo no puede filtrarse al resultado.
        resultados: dict[str, ResultadoArquetipo] = dict(pares)
        for a in arquetipos:
            historial[a.id].append(resultados[a.id].estrategia_dominante)

        # Nuevo agregado: para cada arquetipo, qué fracción de SU planta queda
        # fuera de regla; después se pondera por cuánta gente representa.
        # Se promedia primero entre paráfrasis, después entre arquetipos.
        fuera = 0.0
        for a in arquetipos:
            ds = resultados[a.id].decisiones
            frac = sum(
                contrato.fraccion_fuera_de_regla(d, a.n_trabajadores, not a.formal)
                for d in ds
            ) / max(1, len(ds))
            fuera += a.peso * frac
        tasa = min(1.0, fuera / peso_total)

        # Empleo relativo: 1 - fracción ponderada de trabajadores despedidos.
        # Promedia primero DENTRO del arquetipo (entre paráfrasis), después
        # pondera ENTRE arquetipos por factor de expansión.
        despedidos = 0.0
        for a in arquetipos:
            ds = resultados[a.id].decisiones
            frac = sum(
                min(1.0, d["detalle"].get("empleados_a_despedir", 0) / max(1, a.n_trabajadores))
                for d in ds
            ) / max(1, len(ds))
            despedidos += a.peso * frac

        r = Ronda(
            simulacion_id=simulacion_id,
            seed=seed,
            ronda=n,
            politica={"tipo": "cambio_costo_laboral", "aumento_pct": aumento_pct},
            tasa_informalidad=tasa,
            prob_fiscalizacion=prob,
            empleo_relativo=max(0.0, 1.0 - despedidos / peso_total),
            # SUPUESTO: sin N paráfrasis la banda es degenerada (p10 = p90 = media).
            # Con n_parafrasis>=5 se llena de verdad; hasta entonces se reporta
            # como banda vacía en vez de inventar una.
            banda=_banda(resultados, tasa, arquetipos, peso_total),
            por_arquetipo=resultados,
        )
        salida.append(r)
        if al_terminar_ronda:
            al_terminar_ronda(r)

    return salida


def _banda(resultados, tasa: float, arquetipos, peso_total: float) -> dict[str, float]:
    """p10/p90 de la tasa entre paráfrasis. Degenerada si solo hubo una."""
    n_votos = max(len(r.decisiones) for r in resultados.values())
    if n_votos < 2:
        return {"p10": tasa, "p90": tasa, "degenerada": True}
    tasas = []
    for i in range(n_votos):
        fuera = sum(
            a.peso
            * contrato.fraccion_fuera_de_regla(
                resultados[a.id].decisiones[i], a.n_trabajadores, not a.formal
            )
            for a in arquetipos
        )
        tasas.append(min(1.0, fuera / peso_total))
    tasas.sort()
    k10 = max(0, int(0.10 * (len(tasas) - 1)))
    k90 = min(len(tasas) - 1, int(round(0.90 * (len(tasas) - 1))))
    return {"p10": tasas[k10], "p90": tasas[k90], "degenerada": False}


def converge(rondas: list[Ronda], umbral: float = 0.01) -> bool:
    """¿La última ronda movió la informalidad menos que `umbral`?

    NO es una prueba de equilibrio. Es una observación sobre esta corrida, y se
    reporta como tal: "en esta corrida el movimiento de la última ronda fue de
    X pp". Si alguien la cita como convergencia a Nash, está mintiendo.
    """
    if len(rondas) < 2:
        return False
    return abs(rondas[-1].tasa_informalidad - rondas[-2].tasa_informalidad) < umbral
