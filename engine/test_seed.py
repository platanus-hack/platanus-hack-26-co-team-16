"""Tests del determinismo del motor. Corren con pytest o solos.

    python3 -m pytest engine/test_seed.py -q
    python3 -m engine.test_seed

El test que importa es `test_la_derivacion_por_nombre_es_estable_entre_procesos`:
es el único que puede atrapar el modo de falla que rompe el determinismo **sin
fallar nunca dentro de una sola corrida**.

Lo que NO se prueba acá, y se declara: el nivel 2 de la ADR 0009 (la corrida
completa con caché) y el nivel 3 (la ablación en una máquina limpia). Los dos
necesitan el bucle de rondas y la caché de `behavior/`; son de `make run` y
`make validate`, que cablea R5.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from engine.seed import (
    SEED_POR_DEFECTO,
    generador_raiz,
    manifiesto,
    semilla_raiz,
    stream_de_ronda,
    stream_nombrado,
)

RAIZ = Path(__file__).resolve().parents[1]


def _tirada(rng, n: int = 5) -> list[int]:
    return [int(x) for x in rng.integers(0, 10**9, size=n)]


# --- Lo mínimo: que el seed siembre ------------------------------------------


def test_mismo_seed_mismo_resultado():
    assert _tirada(generador_raiz(42)) == _tirada(generador_raiz(42))
    assert _tirada(stream_de_ronda(42, 2)) == _tirada(stream_de_ronda(42, 2))


def test_el_seed_no_es_decorativo():
    """Lo que hoy NO pasa en `behavior/`: 42 y 99 dan salida idéntica.

    Este test es la razón de existir del archivo. Si algún día vuelve a pasar
    que el seed no cambia nada, falla acá y no en el pitch.
    """
    assert _tirada(generador_raiz(42)) != _tirada(generador_raiz(99))
    for ronda in range(4):
        assert _tirada(stream_de_ronda(42, ronda)) != _tirada(stream_de_ronda(99, ronda))


def test_cada_ronda_tiene_su_propio_stream():
    tiradas = [tuple(_tirada(stream_de_ronda(SEED_POR_DEFECTO, k))) for k in range(6)]
    assert len(set(tiradas)) == len(tiradas), "dos rondas comparten stream"


# --- La decisión del archivo: derivar por clave, no por spawn secuencial ------


def test_el_orden_en_que_se_piden_los_streams_no_cambia_nada():
    """La carrera que introduciría `spawn()`: con 8 hilos, el orden de
    terminación no puede filtrarse al resultado."""
    en_orden = [_tirada(stream_de_ronda(7, k)) for k in range(4)]
    al_reves = [_tirada(stream_de_ronda(7, k)) for k in (3, 2, 1, 0)]
    assert en_orden == list(reversed(al_reves))


def test_pedir_un_stream_no_gasta_los_demas():
    """No hay estado compartido: pedir mil veces la ronda 0 no mueve la ronda 1."""
    esperado = _tirada(stream_de_ronda(7, 1))
    for _ in range(1000):
        stream_de_ronda(7, 0)
    assert _tirada(stream_de_ronda(7, 1)) == esperado


def test_cada_nombre_tiene_su_propio_stream_y_es_estable():
    a = _tirada(stream_nombrado(42, 1, "com-micr-for-t1"))
    b = _tirada(stream_nombrado(42, 1, "com-micr-inf-t1"))
    assert a != b
    assert a == _tirada(stream_nombrado(42, 1, "com-micr-for-t1"))
    # La ronda también separa: el mismo arquetipo en otra ronda es otro stream.
    assert a != _tirada(stream_nombrado(42, 2, "com-micr-for-t1"))


def test_la_derivacion_por_nombre_es_estable_entre_procesos():
    """El bug que no falla dentro de una corrida y rompe el determinismo igual.

    `hash()` de Python está salado por proceso (`PYTHONHASHSEED`), así que usarlo
    para derivar una semilla daría streams distintos en cada ejecución del mismo
    comando — y todos los tests de una sola corrida pasarían.
    """
    guion = (
        "from engine.seed import stream_nombrado;"
        "print([int(x) for x in stream_nombrado(42, 1, 'com-micr-for-t1')"
        ".integers(0, 10**9, size=5)])"
    )
    salidas = set()
    for semilla_de_hash in ("0", "1", "12345"):
        entorno = {**os.environ, "PYTHONHASHSEED": semilla_de_hash, "PYTHONPATH": str(RAIZ)}
        proceso = subprocess.run(
            [sys.executable, "-c", guion],
            cwd=RAIZ, env=entorno, capture_output=True, text=True, check=True,
        )
        salidas.add(proceso.stdout.strip())
    assert len(salidas) == 1, f"la derivación depende del proceso: {salidas}"


# --- Entradas imposibles ------------------------------------------------------


def test_una_ronda_negativa_o_un_nombre_vacio_revientan():
    for llamada in (
        lambda: stream_de_ronda(42, -1),
        lambda: stream_nombrado(42, -1, "x"),
        lambda: stream_nombrado(42, 0),
    ):
        try:
            llamada()
        except ValueError:
            continue
        raise AssertionError("debió rechazarse")


# --- El manifiesto ------------------------------------------------------------


def test_el_manifiesto_trae_lo_que_hace_falta_para_comparar_dos_corridas():
    m = manifiesto(99)
    assert m["seed"] == 99
    for clave in ("python", "numpy", "plataforma", "implementacion"):
        assert m[clave], f"falta {clave} en el manifiesto"


def test_la_semilla_raiz_es_reconstruible_desde_el_entero():
    assert semilla_raiz(42).entropy == semilla_raiz(42).entropy == 42


if __name__ == "__main__":  # pragma: no cover
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
