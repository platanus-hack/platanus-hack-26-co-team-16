"""Tests de las cifras derivadas que `api/serializar.py` publica. $0, sin red.

    python3 -m pytest api/test_serializar.py -q

Qué prueban: S2-8. La única cifra en pesos absolutos de la pantalla
—"$ 8,15 billones/mes · proxy de PIB laboral"— la calculaba el NAVEGADOR,
rearmando la masa salarial base desde `poblacion.arquetipos` y multiplicándola
por el índice relativo. Nacía fuera de la capa que declara "cero números
inventados" y sin un `# SUPUESTO:` que la respaldara, justo la cifra que más
fácil se cita en un pitch.

Acá se prueban dos cosas distintas y las dos importan:

1. Que el número del servidor es EL MISMO que salía del navegador, o sea que
   mover el cálculo no cambia el resultado, solo dónde vive y quién lo audita.
2. Que la diferencia que sí queda —el `round(relativa, 4)` con el que el índice
   viaja por el alambre— no alcanza a mover lo que se ve: 1,6e-05 relativo,
   invisible a los dos decimales de billón que muestra `copBillones()`.

El estado por arquetipo de estos tests es sintético (fracciones fijas elegidas a
mano). No es una corrida y sus cifras NO son un resultado del proyecto: lo que se
está midiendo es aritmética de serialización, no el modelo.
"""

from __future__ import annotations

import sys

from behavior.rondas import Ronda

from api import serializar
from api.servidor import _grilla

AUMENTO_PCT = 23.0


def _ronda_con_estado() -> tuple[Ronda, list]:
    """Una ronda con estado vivo plausible sobre la grilla REAL de 81 celdas."""
    grilla = _grilla()
    estado = {
        a.id: {"fraccion_informal": 0.31, "fraccion_empleada": 0.95, "horas": 0.98}
        for a in grilla
    }
    r = Ronda(
        simulacion_id="test-serializar",
        seed=42,
        ronda=3,
        politica={"tipo": "cambio_costo_laboral", "aumento_pct": AUMENTO_PCT},
        tasa_informalidad=0.31,
        prob_fiscalizacion=0.016,
        empleo_relativo=0.949,
        banda={"p10": 0.31, "p90": 0.31, "degenerada": True},
        estado_por_arquetipo=estado,
    )
    return r, grilla


def _cop_como_lo_hacia_el_navegador(grilla, relativa_del_alambre: float) -> float:
    """La fórmula EXACTA que corría en `Metricas.tsx:27,45`.

    La base se rearmaba desde los arquetipos ya serializados, o sea con `peso` y
    `ingreso_por_trabajador` redondeados por `arquetipo_a_dict()`, y se
    multiplicaba por el índice relativo tal como viaja (4 decimales).
    """
    dicts = [serializar.arquetipo_a_dict(a) for a in grilla]
    base = sum(d["peso"] * d["ingreso_por_trabajador"] for d in dicts)
    return base * relativa_del_alambre


def test_el_servidor_publica_la_cifra_en_pesos() -> None:
    r, grilla = _ronda_con_estado()
    ev = serializar.evento_ronda(r, grilla, AUMENTO_PCT)
    assert ev["masa_salarial_cop"] is not None
    # Redondeada al peso: la pantalla la muestra en billones.
    assert ev["masa_salarial_cop"] == round(ev["masa_salarial_cop"])


def test_relativa_y_pesos_salen_de_la_misma_pasada() -> None:
    """Una sola fuente: los pesos divididos por la base dan el índice.

    Es la propiedad que S2-9 enseñó a exigir. Si mañana alguien toca el
    `# SUPUESTO:` del alza en t1 y solo lo toca en una de las dos cifras, esto
    falla acá y no en el escenario.
    """
    r, grilla = _ronda_con_estado()
    total, base = serializar._masa_salarial(r, grilla, AUMENTO_PCT)
    assert serializar.masa_salarial_cop(r, grilla, AUMENTO_PCT) == total
    assert serializar.masa_salarial_relativa(r, grilla, AUMENTO_PCT) == total / base


def test_es_el_mismo_numero_que_calculaba_el_navegador() -> None:
    """Mover el cálculo no cambia el resultado. Es el permiso para que Dani borre."""
    r, grilla = _ronda_con_estado()
    ev = serializar.evento_ronda(r, grilla, AUMENTO_PCT)
    del_navegador = _cop_como_lo_hacia_el_navegador(
        grilla, ev["masa_salarial_relativa"]
    )
    del_servidor = ev["masa_salarial_cop"]
    # Medido: 1,6e-05. Toda la diferencia es el `round(relativa, 4)` del alambre.
    assert abs(del_navegador - del_servidor) / del_servidor < 1e-4
    # Y lo que de verdad importa: en pantalla son el MISMO texto.
    assert f"{del_navegador / 1e12:.2f}" == f"{del_servidor / 1e12:.2f}"


def test_sin_estado_vivo_no_se_inventa_la_cifra() -> None:
    """Ronda sin `estado_por_arquetipo` -> `None`, no un 0 que parezca un dato."""
    grilla = _grilla()
    r = Ronda(
        simulacion_id="test-serializar-vacia",
        seed=42,
        ronda=0,
        politica={"tipo": "cambio_costo_laboral", "aumento_pct": AUMENTO_PCT},
        tasa_informalidad=0.31,
        prob_fiscalizacion=0.016,
        empleo_relativo=1.0,
        banda={"p10": 0.31, "p90": 0.31, "degenerada": True},
    )
    assert serializar.masa_salarial_cop(r, grilla, AUMENTO_PCT) is None
    assert serializar.evento_ronda(r, grilla, AUMENTO_PCT)["masa_salarial_cop"] is None


if __name__ == "__main__":
    fallos = 0
    for nombre, fn in sorted(globals().items()):
        if nombre.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"ok   {nombre}")
            except AssertionError as e:
                fallos += 1
                print(f"FALLA {nombre}: {e}")
    sys.exit(1 if fallos else 0)
