"""Candado placebo: sin política, la simulación no inventa movimiento.

Por qué la tolerancia es 1 pp y no 0,1 pp
-----------------------------------------
Este candado nació midiendo −13,50 pp: con alza 0% el modelo formalizaba a
13,5 pp de la ciudad. Casi todo era un cambio de denominador —la ronda 0
declaraba `tasa_informalidad_total` (30,57%, TODOS los ocupados) y la ronda 1
calculaba 17,99% desde la grilla, que solo tiene empleados de firma— y eso ya
está corregido en `informalidad_observada()`.

Lo que queda es −0,92 pp y NO es calibración: es el piso de granularidad del
modelo. Con 81 celdas homogéneas y una regla determinista, cada celda solo puede
salir 0% o 100% informal, así que el agregado únicamente puede tomar un puñado
de valores discretos y 17,99% no está entre ellos. Barrido de α ∈ [0, 3]:
16,31% (α∈[1;1,75]), 17,07% (α=1,875), 21,24% (α∈[2;2,5]). No hay α que dé cero.

La tolerancia es 1 pp para que el candado atrape una regresión real sin quedarse
rojo por un límite estructural ya declarado. Si alguien agrega heterogeneidad
DENTRO de la celda, este número debe bajar y la tolerancia con él.
"""

import pytest

from behavior.ablacion import ClienteReglas
from behavior.arquetipos import desde_empresas, informalidad_observada
from behavior.rondas import correr

# El piso de granularidad medido hoy. Bajarlo exige heterogeneidad intra-celda.
PISO_GRANULARIDAD_PP = 1.0


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
        rondas[0].tasa_informalidad, abs=PISO_GRANULARIDAD_PP / 100.0
    )
    # El empleo SÍ es exacto: sin sobrecosto no hay nada que financiar, así que
    # nadie despide. Acá no hay piso de granularidad que valga.
    assert rondas[-1].empleo_relativo == pytest.approx(1.0, abs=0.001)
