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

import math
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Any, Callable

from behavior import contrato
from behavior.ablacion import ClienteReglas
from behavior.arquetipos import Arquetipo, particionar_por_peso
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
    # Qué fracción de la población expandida fue decidida por LLM (el resto salió
    # de reglas fijas por el modo top-K). NO va en `a_contrato()`: `ronda.json`
    # está congelado desde H+4 y agregarle un campo exige avisar en el grupo ANTES.
    fraccion_poblacion_llm: float = 1.0
    # Peso poblacional de cada arquetipo (suma de factores de expansión). Sin
    # esto el dato A4 no se puede ponderar, y sin ponderar dice lo contrario.
    pesos: dict[str, float] = field(default_factory=dict)

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

    def desglose_estrategias(self) -> dict[str, float]:
        """Dato A4: qué estrategia domina, **ponderado por factor de expansión**.

        Devuelve fracciones de la población, no conteos de arquetipos. Es la
        misma regla que `MODELO.md` le impone a `tasa_informalidad` —*"siempre
        ponderada; sin el factor no es la informalidad de la GEIH, es la de la
        muestra"*— y aplica igual acá: sin ponderar, este desglose dice lo
        CONTRARIO de lo que dice ponderado. Medido en la corrida del 23%:
        por conteo domina `cumplir` (44 de 101 arquetipos), ponderado domina
        `informalizar` (51,0% de la población) y `cumplir` cae a 18,1%.

        Un arquetipo de microempresa informal representa a muchísima más gente
        que uno de empresa mediana formal, y contar arquetipos los iguala.
        """
        total: Counter[str] = Counter()
        peso_total = sum(self.pesos.values())
        if not peso_total:
            return {}
        for aid, r in self.por_arquetipo.items():
            peso = self.pesos.get(aid, 0.0)
            votos = sum(r.distribucion.values()) or 1
            for estrategia, n in r.distribucion.items():
                total[estrategia] += peso * n / votos
        return {k: v / peso_total for k, v in total.most_common()}

    def desglose_estrategias_conteo(self) -> dict[str, int]:
        """El conteo crudo de arquetipos. Para el feed y el diagnóstico, NO para
        el dato A4: para eso hay que ponderar (ver `desglose_estrategias`)."""
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

    Acá nace la cascada. Forma funcional de la [ADR 0007](../docs/adr/0007-forma-funcional-prob-sancion.md):

        p(E) = 1 − exp(−C / max(E, 1))

    con `C` = inspecciones esperadas en el periodo sobre el universo del modelo
    y `E` = unidades fuera de regla en la ronda anterior. Tiene micro-fundamento
    (repartir C inspecciones al azar entre E evasores es Poisson de media C/E; la
    probabilidad de recibir al menos una es 1 − e^(−C/E)), y no una curva elegida
    para que la gráfica quede bonita.

    Reemplaza a la forma abreviada `p ≈ C/E` que esta capa usaba antes. Las dos
    coinciden donde ocurre la acción —a 63,2% de informalidad, 3,12% vs 3,16%—
    pero la abreviada se rompe en el borde: con 2% de evasores daba 100% y esta
    da 63,2%. El motor de Manuel usa la misma fórmula; si difieren, manda el motor.
    """
    if peso_fuera_de_regla <= 0:
        # E → 0: por continuidad p → 1. Irrelevante en la práctica, no hay a
        # quién aplicársela (ADR 0007).
        return 1.0
    inspecciones = capacidad * peso_total
    return 1.0 - math.exp(-inspecciones / max(peso_fuera_de_regla, 1.0))


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
    cobertura_llm: float | None = None,
    al_terminar_ronda: Callable[[Ronda], None] | None = None,
) -> list[Ronda]:
    """Corre las rondas de mejor respuesta y devuelve el agregado de cada una.

    `capacidad_fiscalizacion` es la fracción del universo que se alcanza a
    inspeccionar por periodo. Es FIJA: no se ajusta a mano entre rondas. Ese es
    el compromiso metodológico que hace la cascada un resultado y no un supuesto.

    El calendario es el de la [ADR 0005](../docs/adr/0005-el-reloj-de-la-simulacion.md):
    una ronda es un trimestre, la **ronda 0 es la reacción ingenua** —la
    proyección oficial, que asume cumplimiento total y no gasta LLM— y las
    rondas 1..`rondas_totales`-1 son mejor respuesta. Con el valor por defecto
    son 3 rondas de LLM, no 4.

    `cobertura_llm` activa el modo top-K: si se le da (p. ej. `0.80`), solo los
    arquetipos que suman esa fracción de la población van al LLM y el resto se
    resuelve con las reglas fijas de `ablacion.ClienteReglas`. `None` = todos al
    LLM. Cada `Ronda` reporta `fraccion_poblacion_llm`.
    """
    peso_total = sum(a.peso for a in arquetipos) or 1.0
    tasa = tasa_informalidad_inicial
    historial: dict[str, list[str]] = {a.id: [] for a in arquetipos}
    salida: list[Ronda] = []

    # Ruteo del top-K. `ClienteReglas` es un reemplazo directo de la firma de
    # `proponer()`, así que el resto del bucle no distingue entre los dos.
    if cobertura_llm is None:
        cabeza_ids = {a.id for a in arquetipos}
        cliente_cola = None
    else:
        cabeza, _cola = particionar_por_peso(arquetipos, cobertura_llm)
        cabeza_ids = {a.id for a in cabeza}
        cliente_cola = ClienteReglas()
    fraccion_llm = (
        sum(a.peso for a in arquetipos if a.id in cabeza_ids) / peso_total
    )

    # RONDA 0 — la proyección oficial (ADR 0005). No se llama al LLM: por
    # definición asume cumplimiento total, así que la informalidad se queda en la
    # observada y nadie pierde el empleo. Es el punto contra el que se mide
    # `brecha = ronda 3 − ronda 0`, que es el producto entero (dato A1).
    r0 = Ronda(
        simulacion_id=simulacion_id,
        seed=seed,
        ronda=0,
        politica={"tipo": "cambio_costo_laboral", "aumento_pct": aumento_pct},
        tasa_informalidad=tasa,
        prob_fiscalizacion=_prob_fiscalizacion(
            capacidad_fiscalizacion, tasa * peso_total, peso_total
        ),
        empleo_relativo=1.0,
        # La proyección oficial es un punto, no una distribución: no tiene banda
        # porque no hay nada estocástico que la genere. Se marca degenerada en
        # vez de inventarle un intervalo.
        banda={"p10": tasa, "p90": tasa, "degenerada": True},
        por_arquetipo={},
        fraccion_poblacion_llm=0.0,
    )
    salida.append(r0)
    if al_terminar_ronda:
        al_terminar_ronda(r0)

    for n in range(1, rondas_totales):
        prob = _prob_fiscalizacion(capacidad_fiscalizacion, tasa * peso_total, peso_total)

        # Las RONDAS son secuenciales por definición (cada una responde al
        # agregado de la anterior), pero los ARQUETIPOS dentro de una ronda son
        # independientes: se resuelven en paralelo. Con 48 arquetipos eso baja
        # una corrida en frío de ~10 min a ~1,5 min sin cambiar el resultado —
        # el orden de recorrido no entra en ninguna semilla (ver
        # `arquetipos._semilla`), así que sigue siendo determinista.
        def _uno(a: Arquetipo) -> tuple[str, ResultadoArquetipo]:
            # Top-K: la cabeza al LLM, la cola a reglas fijas. Misma firma.
            cli = cliente if (cliente_cola is None or a.id in cabeza_ids) else cliente_cola
            previo = historial[a.id]
            texto_historial = (
                "\n- Lo que hiciste en periodos anteriores: " + ", ".join(previo)
                if previo
                else ""
            )
            return a.id, decidir_arquetipo(
                a,
                cli,
                veto,
                aumento_pct=aumento_pct,
                ronda=n,
                # El agente decide en los periodos 1..rondas_totales-1: la ronda
                # 0 es la proyección oficial y él no participa en ella. Se le
                # dice "periodo 1 de 3", no "de 4".
                rondas_totales=rondas_totales - 1,
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
            fraccion_poblacion_llm=fraccion_llm,
            pesos={a.id: a.peso for a in arquetipos},
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
