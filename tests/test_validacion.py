"""Pruebas de las tres compuertas pre-registradas.

Un BLOQUEADO es un resultado válido del ejecutor: estos tests impiden que una
pieza ausente se convierta accidentalmente en un PASA o en exit 0.
"""

from scripts.validate import Estado, candado_g1, candado_g2, candado_g3


def test_g1_no_pasa_sin_entorno_y_corrida_completa_reproducibles():
    estado, detalle = candado_g1()
    assert estado is Estado.BLOQUEADO
    assert "anthropic" in detalle or "corrida" in detalle


def test_g2_higiene_no_sustituye_el_reskinning():
    estado, detalle = candado_g2()
    assert estado is Estado.BLOQUEADO
    assert "re-skinning" in detalle


def test_g3_no_confunde_los_momentos_observados_con_calibracion():
    estado, detalle = candado_g3()
    assert estado is Estado.BLOQUEADO
    assert "calibracion_base.json" in detalle
