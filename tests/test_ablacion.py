"""Regresiones de la regla fija que alteraban el placebo."""

from behavior.ablacion import ClienteReglas
from behavior.arquetipos import Arquetipo


def _firma() -> Arquetipo:
    return Arquetipo(
        id="micro-mixta",
        sector="comercio",
        tamano="micro",
        formal=True,
        tramo_ingreso="t1",
        n_trabajadores=4,
        ingreso_por_trabajador=1_000_000.0,
        flujo_caja=100_000.0,
        costo_despido=1_000_000.0,
        factor_prestacional=1.4,
        fraccion_informal_inicial=0.25,
    )


def _contexto(**cambios):
    base = {
        "arquetipo": _firma(),
        "aumento_pct": 0.0,
        "prob_fiscalizacion": 0.0,
        "multa": 12_000_000.0,
        "fraccion_informal_previa": 0.25,
        "estrategias_vetadas": ("informalizar_total",),
    }
    base.update(cambios)
    return base


def test_sin_sobrecosto_no_despide_al_caer_por_la_escalera():
    decision = ClienteReglas().proponer("", "", contexto=_contexto())

    assert decision["estrategia_propuesta"] == "absorber"


def test_informaliza_solo_la_parte_de_la_planta_que_sigue_en_regla():
    decision = ClienteReglas().proponer(
        "",
        "",
        contexto=_contexto(aumento_pct=23.0, estrategias_vetadas=()),
    )

    assert decision["detalle"]["empleados_a_informalizar"] == 3
