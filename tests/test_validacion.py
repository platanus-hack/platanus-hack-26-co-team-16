"""Pruebas de las tres compuertas pre-registradas.

Un BLOQUEADO es un resultado válido del ejecutor: estos tests impiden que una
pieza ausente se convierta accidentalmente en un PASA o en exit 0.
"""

from scripts.validate import Estado, candado_g1, candado_g2, candado_g3


def test_g1_mide_reproducibilidad_en_vez_de_declararla_pendiente():
    """G1 ya no es un BLOQUEADO incondicional: se mide.

    Este test decía `assert estado is Estado.BLOQUEADO`, y pasaba porque
    `candado_g1()` hacía un `faltan.append(...)` sin condición seguido de un
    `return BLOQUEADO`: la compuerta no podía dar verde ni con el artefacto en
    disco. O sea que el test verificaba que un candado imposible siguiera siendo
    imposible.

    Ahora la compuerta corre `scripts/run_simulacion.py` dos veces en modo reglas
    (determinista, sin API key) y compara los dos artefactos byte a byte. Lo que
    este test cuida es que **el resultado salga de medir**, no de un literal: si
    algún día dos corridas dejan de coincidir, tiene que ser FALLA y no PASA.
    """
    estado, detalle = candado_g1()
    assert estado in (Estado.PASA, Estado.FALLA, Estado.BLOQUEADO)
    if estado is Estado.PASA:
        # La única forma de pasar es habiendo comparado dos corridas de verdad.
        assert "idénticas byte a byte" in detalle
        assert "seed=" in detalle and "manifiesto=" in detalle
    elif estado is Estado.FALLA:
        assert "NO dieron" in detalle
    else:
        assert "falta" in detalle or "salió" in detalle


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
