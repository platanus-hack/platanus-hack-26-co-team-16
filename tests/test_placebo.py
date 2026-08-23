"""Candado placebo: sin política, la simulación no inventa movimiento.

Por qué la tolerancia es 1 pp y no 0,1 pp
-----------------------------------------
Este candado nació midiendo −13,50 pp: con alza 0% el modelo formalizaba a
13,5 pp de la ciudad. Casi todo era un cambio de denominador —la ronda 0
declaraba `tasa_informalidad_total` (30,57%, TODOS los ocupados) y la ronda 1
calculaba 17,99% desde la grilla, que solo tiene empleados de firma— y eso ya
está corregido en `informalidad_observada()`.

Lo que queda NO es calibración: es el piso de granularidad del modelo. Con 81
celdas homogéneas y una regla determinista, cada celda solo puede salir 0% o 100%
informal, así que el agregado únicamente puede tomar un puñado de valores
discretos y 17,99% no está entre ellos. No hay α que dé cero.

EL PISO SUBIÓ DE 0,92 pp A 3,25 pp, Y HAY QUE DECIR POR QUÉ
-----------------------------------------------------------
El −0,92 pp de antes se medía sobre una ablación que sumaba COP/mes con
COP/trimestre (`behavior/ablacion.py`: la mitad del arreglo A3 que había quedado
sin hacer, con la caja ya en trimestres y los costos todavía en meses). Ese
defecto tenía DOS efectos de signo contrario —el sobrecosto entraba 3× chico, así
que se despedía de menos; y la sanción esperada pesaba 3× de más contra el
salario, así que se formalizaba de más— y **se cancelaban parcialmente**. Al poner
las tres cifras en la unidad del motor (`engine/veto.py` multiplica por
`MESES_POR_RONDA` en :297, :420 y :444), la cancelación desaparece y el piso real
del modelo queda a la vista: **+3,25 pp**.

O sea que el ajuste del placebo era mejor cuando la aritmética estaba mal. Es
incómodo y es el dato: se declara en vez de recuperarse re-calibrando α, porque un
parámetro que se re-ajusta cada vez que se arregla un bug es un parámetro que tapa
bugs (el razonamiento completo, con el barrido, está en `engine/fiscalizacion.py`
sobre `ELASTICIDAD_VISIBILIDAD`).

Barrido de α con las unidades ya corregidas: 95,67% (α=0), 32,78% (α=1),
**21,24% (α ∈ [1,5; 1,875], el mínimo empatado)**, 27,15% (α=2,5), 32,71% (α=3).
Ninguna α baja de +3,25 pp, así que la tolerancia no se puede recuperar moviendo α.

La tolerancia es el piso medido más un margen, para que el candado atrape una
regresión real sin quedarse rojo por un límite estructural ya declarado. Si alguien
agrega heterogeneidad DENTRO de la celda, este número debe bajar y la tolerancia
con él.
"""

import pytest

from behavior.ablacion import ClienteReglas
from behavior.arquetipos import desde_empresas, informalidad_observada
from behavior.rondas import correr

# El piso de granularidad medido hoy (+3,25 pp) más un margen chico. Bajarlo exige
# heterogeneidad intra-celda, no una α distinta: ninguna baja de 3,25 (ver arriba).
PISO_GRANULARIDAD_PP = 3.5


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
