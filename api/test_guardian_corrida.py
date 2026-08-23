"""Regresiones del guardián de corrida. $0, sin red ni esperas reales.

El reloj mutable permite llevar el candado de segundos a minutos en memoria:
estos tests prueban la recuperación y sus carreras sin dormir el proceso ni
acercarse al camino que instancia un cliente LLM.
"""

from __future__ import annotations

import threading

from api.servidor import GuardianCorrida


class _RelojMutable:
    """Reloj monotónico controlado por el test; solo avanza cuando se le ordena."""

    def __init__(self) -> None:
        self.ahora = 0.0

    def __call__(self) -> float:
        return self.ahora


def test_orphan_is_recovered_only_after_threshold() -> None:
    reloj = _RelojMutable()
    guardian = GuardianCorrida(umbral_segundos=900.0, reloj=reloj)

    turno_inicial, _ = guardian.adquirir()
    reloj.ahora = 900.0
    turno_en_umbral, _ = guardian.adquirir()
    reloj.ahora = 901.0
    turno_recuperado, antiguedad = guardian.adquirir()

    assert turno_inicial is not None
    assert turno_en_umbral is None
    assert turno_recuperado is not None
    assert turno_recuperado is not turno_inicial
    assert antiguedad == 901.0


def test_two_threads_cannot_recover_same_orphan() -> None:
    reloj = _RelojMutable()
    guardian = GuardianCorrida(umbral_segundos=900.0, reloj=reloj)
    guardian.adquirir()
    reloj.ahora = 901.0
    barrera = threading.Barrier(3)
    resultados: list[object | None] = []

    def intentar_recuperar() -> None:
        barrera.wait()
        turno, _ = guardian.adquirir()
        resultados.append(turno)

    hilos = [threading.Thread(target=intentar_recuperar) for _ in range(2)]
    for hilo in hilos:
        hilo.start()
    barrera.wait()
    for hilo in hilos:
        hilo.join()

    assert sum(turno is not None for turno in resultados) == 1


def test_stale_owner_release_does_not_raise_or_unlock_new_owner() -> None:
    reloj = _RelojMutable()
    guardian = GuardianCorrida(umbral_segundos=900.0, reloj=reloj)
    turno_huerfano, _ = guardian.adquirir()
    reloj.ahora = 901.0
    turno_nuevo, _ = guardian.adquirir()

    guardian.soltar(turno_huerfano)
    turno_intruso, _ = guardian.adquirir()
    guardian.soltar(turno_nuevo)
    turno_despues_de_soltar, _ = guardian.adquirir()

    assert turno_nuevo is not None
    assert turno_intruso is None
    assert turno_despues_de_soltar is not None
