"""Candado placebo: sin política, la simulación no inventa movimiento."""

import pytest

from behavior.ablacion import ClienteReglas
from behavior.arquetipos import desde_empresas, informalidad_observada
from behavior.rondas import correr


def test_alza_cero_no_mueve_informalidad_ni_empleo():
    arquetipos = desde_empresas("data/empresas.parquet")
    rondas = correr(
        arquetipos,
        ClienteReglas(),
        aumento_pct=0.0,
        tasa_informalidad_inicial=informalidad_observada(),
        paralelismo=1,
    )

    assert rondas[-1].tasa_informalidad == pytest.approx(
        rondas[0].tasa_informalidad, abs=0.001
    )
    assert rondas[-1].empleo_relativo == pytest.approx(1.0, abs=0.001)
