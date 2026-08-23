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
    """La higiene sola no cierra G2: hace falta la corrida comparativa.

    `behavior.capa.Reskin` ya existe (lo trajo `rol/correcciones-simulacion`),
    así que el bloqueo dejó de ser "no está implementado" y pasó a ser "está
    implementado y no se ha corrido". La compuerta sigue cerrada hasta que
    exista el par canónica/re-skinneada para comparar.
    """
    estado, detalle = candado_g2()
    assert estado is Estado.BLOQUEADO
    assert "higiene PASA" in detalle
    assert "comparar" in detalle or "registrar" in detalle


def test_g3_no_confunde_los_momentos_observados_con_calibracion():
    estado, detalle = candado_g3()
    assert estado is Estado.BLOQUEADO
    assert "calibracion_base.json" in detalle
