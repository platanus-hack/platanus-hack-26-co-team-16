"""Tests del muestreo por arquetipo. Corren con pytest o solos.

    python3 -m pytest engine/test_arquetipos.py -q
    python3 -m engine.test_arquetipos
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pytest

from engine.arquetipos import muestrear
from engine.seed import stream_nombrado


@dataclass(frozen=True)
class ArquetipoPrueba:
    arquetipo_id: str
    distribucion: dict[str, float]


def _arq(**distribucion: float) -> ArquetipoPrueba:
    return ArquetipoPrueba("com-micro-informal-t2", distribucion)


def test_mismo_seed_misma_muestra():
    arq = _arq(cumplir=3, informalizar=2, despedir=1)
    primera = muestrear(arq, 100, np.random.default_rng(42))
    segunda = muestrear(arq, 100, np.random.default_rng(42))
    assert primera == segunda


def test_resultado_real_de_behavior_satisface_el_protocolo():
    """Atrapa una deriva de nombres entre las dos carpetas del contrato."""
    from behavior.capa import ResultadoArquetipo

    resultado = ResultadoArquetipo(
        arquetipo_id="com-micro-informal-t2",
        distribucion={"cumplir": 1, "informalizar": 1},
    )
    assert len(muestrear(resultado, 10, np.random.default_rng(2))) == 10

    vacio = ResultadoArquetipo(arquetipo_id="sin-decision")
    with pytest.raises(ValueError, match="sin-decision"):
        muestrear(vacio, 1, np.random.default_rng(2))


def test_el_orden_del_diccionario_no_cambia_la_muestra():
    una = ArquetipoPrueba("a", {"cumplir": 3, "despedir": 1, "informalizar": 2})
    otra = ArquetipoPrueba("a", {"informalizar": 2, "cumplir": 3, "despedir": 1})
    assert muestrear(una, 100, np.random.default_rng(7)) == muestrear(
        otra, 100, np.random.default_rng(7)
    )


def test_reescalar_pesos_incluso_extremos_no_cambia_la_muestra():
    pequenos = ArquetipoPrueba("a", {"cumplir": 1, "informalizar": 1})
    extremos = ArquetipoPrueba("a", {"cumplir": 1e308, "informalizar": 1e308})
    assert muestrear(pequenos, 100, np.random.default_rng(7)) == muestrear(
        extremos, 100, np.random.default_rng(7)
    )


def test_stream_por_nombre_hace_independiente_el_orden_de_arquetipos():
    a = ArquetipoPrueba("a", {"cumplir": 1, "informalizar": 1})
    b = ArquetipoPrueba("b", {"cumplir": 1, "despedir": 1})

    directo = {
        arq.arquetipo_id: muestrear(
            arq, 40, stream_nombrado(42, 2, arq.arquetipo_id)
        )
        for arq in (a, b)
    }
    al_reves = {
        arq.arquetipo_id: muestrear(
            arq, 40, stream_nombrado(42, 2, arq.arquetipo_id)
        )
        for arq in (b, a)
    }
    assert directo == al_reves


def test_distribucion_degenerada_asigna_la_unica_estrategia():
    assert muestrear(_arq(cumplir=9), 25, np.random.default_rng(1)) == [
        "cumplir"
    ] * 25


def test_las_proporciones_respetan_los_pesos_normalizados():
    muestra = muestrear(
        _arq(cumplir=6, informalizar=3, despedir=1),
        50_000,
        np.random.default_rng(2026),
    )
    proporciones = {
        nombre: muestra.count(nombre) / len(muestra) for nombre in set(muestra)
    }
    assert proporciones["cumplir"] == pytest.approx(0.6, abs=0.01)
    assert proporciones["informalizar"] == pytest.approx(0.3, abs=0.01)
    assert proporciones["despedir"] == pytest.approx(0.1, abs=0.01)


def test_cero_agentes_no_consume_rng_ni_exige_distribucion():
    vacio = ArquetipoPrueba("vacio", {})
    rng = np.random.default_rng(11)
    assert muestrear(vacio, 0, rng) == []
    assert int(rng.integers(0, 10**9)) == int(
        np.random.default_rng(11).integers(0, 10**9)
    )


@pytest.mark.parametrize("n", [-1, 1.5, True])
def test_rechaza_tamanos_invalidos(n):
    with pytest.raises((TypeError, ValueError)):
        muestrear(_arq(cumplir=1), n, np.random.default_rng(1))


@pytest.mark.parametrize(
    ("distribucion", "mensaje"),
    [
        ({}, "vacía"),
        ({"cumplir": 0, "despedir": 0}, "peso positivo"),
        ({"cumplir": 1, "despedir": -1}, "negativos"),
        ({"cumplir": float("nan")}, "no finitos"),
        ({"cumplir": float("inf")}, "no finitos"),
        ({"cumplir": "mucho"}, "ilegibles"),
    ],
)
def test_rechaza_distribuciones_invalidas(distribucion, mensaje):
    with pytest.raises(ValueError, match=mensaje):
        muestrear(
            ArquetipoPrueba("invalido", distribucion),
            1,
            np.random.default_rng(1),
        )


def test_rechaza_un_rng_que_no_es_de_numpy():
    with pytest.raises(TypeError, match="numpy.random.Generator"):
        muestrear(_arq(cumplir=1), 1, object())


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(pytest.main([__file__, "-q"]))
