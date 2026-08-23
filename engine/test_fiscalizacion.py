"""Tests de la fiscalización endógena. Corren con pytest o solos.

    python3 -m pytest engine/test_fiscalizacion.py -q
    python3 -m engine.test_fiscalizacion

Los dos tests que la ADR 0007 declara obligatorios son
`test_p_es_estrictamente_decreciente_en_e` y `test_p_siempre_es_una_probabilidad`.

Lo que NO se prueba acá, y se declara: **la corrida de control con `p` fijo**
(con `p` exógeno la cascada tiene que desaparecer; si no desaparece, viene de
otra parte). Necesita el bucle de rondas, que es de `engine/rondas.py` y no está
escrito. Queda como límite en `VALIDATION.md`, no como test ausente en silencio.
"""

from __future__ import annotations

import math

from engine.fiscalizacion import (
    INSPECTORES_NACIONALES,
    PROB_ANUAL_REFERENCIA_EEUU,
    EstadoFiscalizacion,
    es_degenerado,
    prob_por_celda,
    prob_sancion,
    satura,
    tasa_anual_implicita,
)

UNIVERSO = 400_000


def _estado(**kw) -> EstadoFiscalizacion:
    return EstadoFiscalizacion(universo=UNIVERSO, **kw)


# --- Los dos obligatorios de la ADR 0007 -------------------------------------


def test_p_es_estrictamente_decreciente_en_e():
    """La cascada en una línea: más unidades fuera de regla, menos riesgo.

    Se prueba fuera de la meseta de saturación, que es donde `p` es
    representable. La meseta tiene su propio test, abajo.
    """
    C = _estado().capacidad()
    anterior = 1.0
    for E in (1_000, 10_000, 100_000, 168_000, 400_000, 4_000_000):
        assert not satura(C, E), f"E={E} cayó en la meseta y este test no la cubre"
        p = prob_sancion(C, E)
        assert p < anterior, f"p no bajó al pasar a E={E}"
        anterior = p


def test_la_meseta_de_saturacion_esta_lejos_del_regimen_real():
    """El límite del double, medido y acotado en vez de escondido.

    Con la C del caso demo, `p` sale 1,0 exacto hasta unas 108 unidades fuera de
    regla: 0,027% del universo. La acción ocurre entre 10% y 100%.
    """
    estado = _estado()
    C = estado.capacidad()
    assert satura(C, 100)
    assert not satura(C, 200)
    # En fracción del universo, la meseta es despreciable.
    assert not satura(C, estado.evasores(0.001))


def test_p_siempre_es_una_probabilidad():
    C = _estado().capacidad()
    for E in (0, 0.5, 1, 7, 1_000, 10**9):
        p = prob_sancion(C, E)
        assert 0.0 <= p <= 1.0, f"p={p} para E={E} no es una probabilidad"
    # Estrictamente menor que 1 en todo el régimen real. En el borde `E → 0` el
    # exponente se va tan abajo que `exp()` devuelve 0.0 y `p` sale exactamente
    # 1,0: es el límite del double, no del modelo, y por eso ese régimen se
    # reporta marcado en vez de creerse.
    assert prob_sancion(C, 1_000) < 1.0
    assert prob_sancion(C, 0) == 1.0
    assert es_degenerado(0)


def test_alfa_cero_recupera_exactamente_la_probabilidad_uniforme():
    """La calibración se puede apagar sin cambiar el motor anterior."""
    capacidad = 3_900.0
    celdas = [
        ("micro", 3, 100_000.0),
        ("pyme", 25, 20_000.0),
        ("grande", 300, 2_000.0),
        ("sin_evasores", 8, 0.0),
    ]

    esperado = prob_sancion(capacidad, 122_000.0)
    resultado = prob_por_celda(capacidad, celdas, alfa=0.0)

    assert all(p == esperado for p in resultado.values())


def test_coincide_con_la_formula_abreviada_del_plan_en_el_regimen_real():
    """`p ≈ C/E` donde ocurre la acción: pocas inspecciones, muchos evasores."""
    C = _estado().capacidad()
    for E in (100_000, 200_000, 400_000):
        exacta = prob_sancion(C, E)
        abreviada = C / E
        assert abs(exacta - abreviada) / abreviada < 0.02, f"divergen en E={E}"


def test_en_el_borde_la_abreviada_se_rompe_y_la_exponencial_no():
    """El motivo de la ADR: `C/E` con pocos evasores devuelve algo que no es una
    probabilidad."""
    C = _estado().capacidad()
    E = 500  # 0,125% del universo: fuera de la meseta y aun así C/E > 1
    assert C / E > 1.0
    assert prob_sancion(C, E) < 1.0


# --- El borde, que es la decisión de esta sesión -----------------------------


def test_el_regimen_degenerado_se_marca_en_vez_de_parcharse():
    assert es_degenerado(0.0)
    assert es_degenerado(0.99)
    assert not es_degenerado(1.0)
    assert not es_degenerado(168_000)


def test_con_nadie_fuera_de_regla_salirse_es_casi_seguro_que_se_castiga():
    """El estado absorbente es el espejo de la cascada, no un artefacto."""
    estado = _estado()
    assert estado.prob(0.0) > estado.prob(0.01) > estado.prob(0.42)


# --- La capacidad ------------------------------------------------------------


def test_la_capacidad_es_el_producto_de_sus_tres_factores():
    estado = _estado(inspectores=1_000, inspecciones_por_inspector=10.0, fraccion_universo=0.5)
    assert estado.capacidad() == 1_000 * 10.0 * 0.5


def test_el_default_de_inspectores_es_la_cifra_con_fuente():
    """Si alguien la cambia sin cambiar la cita de la OIT, esto lo dice."""
    assert INSPECTORES_NACIONALES == 1_300
    assert _estado().inspectores == 1_300


def test_la_conversion_de_fraccion_a_conteo_es_explicita_y_valida_su_entrada():
    estado = _estado()
    assert estado.evasores(0.42) == 0.42 * UNIVERSO
    for mala in (-0.01, 1.01):
        try:
            estado.evasores(mala)
        except ValueError:
            continue
        raise AssertionError(f"una fracción de {mala} debió rechazarse")


def test_un_universo_vacio_o_una_fraccion_imposible_no_se_construyen():
    for kw in ({"universo": 0}, {"universo": -3}):
        try:
            EstadoFiscalizacion(**kw)
        except ValueError:
            continue
        raise AssertionError(f"debió rechazarse: {kw}")
    try:
        EstadoFiscalizacion(universo=10, fraccion_universo=1.5)
    except ValueError:
        pass
    else:
        raise AssertionError("una fracción del universo de 1,5 debió rechazarse")


def test_una_capacidad_o_un_conteo_negativos_revientan():
    for args in ((-1.0, 10.0), (10.0, -1.0)):
        try:
            prob_sancion(*args)
        except ValueError:
            continue
        raise AssertionError(f"debió rechazarse: {args}")


# --- Que no sea una perilla --------------------------------------------------


def test_el_estado_de_fiscalizacion_es_inmutable():
    """ADR 0006: se construye una vez y NO se ajusta entre rondas."""
    estado = _estado()
    try:
        estado.inspectores = 99_999  # type: ignore[misc]
    except Exception:
        pass
    else:
        raise AssertionError("se pudo mover la capacidad a mano")
    assert estado.inspectores == INSPECTORES_NACIONALES


def test_el_barrido_no_toca_el_estado_original():
    estado = _estado()
    alterno = estado.con(inspecciones_por_inspector=60.0)
    assert alterno.inspecciones_por_inspector == 60.0
    assert estado.inspecciones_por_inspector == 20.0
    assert alterno.prob(0.42) > estado.prob(0.42)


# --- Cordura -----------------------------------------------------------------


def test_la_anualizada_queda_en_el_mismo_orden_que_la_referencia_de_eeuu():
    """Cordura, NO calibración: nunca se ajusta C para pegarle a este número.

    Si alguien mueve S2 o S10 lo suficiente para sacar la probabilidad de un
    dígito porcentual, este test lo dice antes de que salga en un pitch.
    """
    anual = tasa_anual_implicita(_estado().prob(0.42))
    assert anual < 0.10, f"anualizada {anual:.1%}: revisar C, no el fenómeno"
    assert anual / PROB_ANUAL_REFERENCIA_EEUU < 20


def test_la_anualizacion_es_la_de_cuatro_trimestres_independientes():
    assert math.isclose(tasa_anual_implicita(0.02), 1 - 0.98**4)
    assert tasa_anual_implicita(0.0) == 0.0


def test_prob_sancion_es_pura():
    C = _estado().capacidad()
    assert prob_sancion(C, 1_000) == prob_sancion(C, 1_000)


if __name__ == "__main__":  # pragma: no cover
    import sys
    import traceback

    fallidos = 0
    for nombre, fn in sorted(dict(globals()).items()):
        if not nombre.startswith("test_") or not callable(fn):
            continue
        try:
            fn()
            print(f"ok    {nombre}")
        except Exception:
            fallidos += 1
            print(f"FALLA {nombre}")
            traceback.print_exc()
    print(f"\n{fallidos} fallas")
    sys.exit(1 if fallidos else 0)
