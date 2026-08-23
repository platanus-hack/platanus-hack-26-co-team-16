"""Pruebas de las tres compuertas pre-registradas.

Estos tests afirmaban el ESTADO del proyecto —"G1 sigue bloqueado", "G3 sigue
bloqueado"— y por eso se cayeron los tres el día que ese estado cambió. Un test
que codifica el pendiente de hoy caduca cuando el pendiente se cierra, y en el
camino no protege nada: no distingue "se cerró bien" de "alguien lo forzó".

Ahora prueban el COMPORTAMIENTO que tiene que seguir siendo cierto pase lo que
pase con los pendientes:

  * G1 sólo pasa si dos corridas de verdad coinciden, y se bloquea si le falta
    el productor o si le prohíben correr (`--dry`);
  * G2 no se cierra con la higiene sola;
  * G3 mide contra el denominador de EMPLEADOS DE FIRMA y exige orden estricto;
  * una medición nunca decide el código de salida.
"""

import json

import pytest

from scripts import validate
from scripts.validate import Estado, candado_g1, candado_g2, candado_g3


# --- G1 · reproducibilidad ---------------------------------------------------


def test_g1_pasa_cuando_dos_corridas_dan_el_mismo_artefacto():
    """La promesa de `AGENTS.md`: mismo seed, mismo resultado.

    Corre el productor de verdad (dos veces, por la ablación determinista: $0,
    sin API key y sin red). Es lento comparado con el resto de la suite y vale
    la pena: es la única afirmación del repo que un jurado va a intentar
    reproducir a mano.
    """
    estado, detalle = candado_g1()
    assert estado is Estado.PASA, detalle
    assert "idéntico" in detalle


def test_g1_se_bloquea_si_falta_el_productor(monkeypatch, tmp_path):
    monkeypatch.setattr(validate, "PRODUCTOR", tmp_path / "no_existe.py")
    estado, detalle = candado_g1()
    assert estado is Estado.BLOQUEADO
    assert "run_simulacion.py" in detalle


def test_g1_no_pasa_en_pasada_seca():
    """`--dry` no puede regalar un PASA: no corrió lo que decide el candado."""
    estado, detalle = candado_g1(seco=True)
    assert estado is Estado.BLOQUEADO
    assert "--dry" in detalle


# --- G2 · no contaminación ---------------------------------------------------


def test_g2_higiene_no_sustituye_el_reskinning():
    """La higiene sola no cierra G2: hace falta el par canónica/re-skinneada.

    Y ese par exige el camino LLM. Por la ablación el re-skin mueve 0,000000 pp
    —las reglas fijas no leen el texto del prompt, que es lo único que `Reskin`
    reescribe—, así que cerrar la compuerta por ahí sería medir un canal por el
    que la contaminación no puede viajar.
    """
    estado, detalle = candado_g2()
    assert estado is Estado.BLOQUEADO
    assert "higiene PASA" in detalle
    assert "LLM" in detalle


# --- G3 · calibración base ---------------------------------------------------


def _calibracion(tmp_path, monkeypatch, *, total, micro, pyme, grande):
    (tmp_path / "calibracion_base.json").write_text(
        json.dumps({
            "tasa_informalidad_total": total,
            "tasa_informalidad_por_tamano": {
                "micro": micro, "pyme": pyme, "grande": grande,
            },
        }),
        encoding="utf-8",
    )
    monkeypatch.setattr(validate, "ARTEFACTOS", tmp_path)


def test_g3_mide_contra_empleados_de_firma_no_contra_todos_los_ocupados(
    tmp_path, monkeypatch
):
    """El defecto que este candado tenía: dos denominadores para una tasa.

    `data/empresas.parquet` excluye a los cuenta propia a propósito —una unidad
    sin empleados no puede despedir ni informalizar a nadie—, así que la corrida
    vive en el universo de empleados de firma (17,99%) y no en el de todos los
    ocupados de Bogotá (30,57%). Comparando contra el equivocado, un modelo
    clavado en el objetivo correcto reprobaba con 12,58 pp de error puramente
    contable.
    """
    _calibracion(tmp_path, monkeypatch,
                 total=0.1799, micro=0.5961, pyme=0.1057, grande=0.0081)
    estado, detalle = candado_g3()
    assert estado is Estado.PASA, detalle
    assert "error=0.00 pp" in detalle
    assert "empleados de firma" in detalle


def test_g3_exige_orden_estricto_micro_pyme_grande(tmp_path, monkeypatch):
    """Acertar el NIVEL y aplanar el desglose no es calibrar.

    Es el caso real de hoy: la corrida sin política queda a 0,92 pp del objetivo
    —dentro del umbral de 2 pp— pero manda pyme y grande a 0%. El agregado se
    salva porque las desviaciones por tamaño se cancelan entre sí, y sin esta
    cláusula el candado no lo vería.
    """
    _calibracion(tmp_path, monkeypatch,
                 total=0.1799, micro=0.67, pyme=0.0, grande=0.0)
    estado, detalle = candado_g3()
    assert estado is Estado.FALLA
    assert "orden micro>pyme>grande=False" in detalle


def test_g3_se_bloquea_sin_corrida_sin_politica(tmp_path, monkeypatch):
    monkeypatch.setattr(validate, "ARTEFACTOS", tmp_path)
    monkeypatch.setattr(validate, "DATA", tmp_path / "data")
    estado, detalle = candado_g3()
    assert estado is Estado.BLOQUEADO
    assert "--aumento 0" in detalle


# --- El código de salida -----------------------------------------------------


def test_solo_las_compuertas_deciden_el_codigo_de_salida(capsys):
    """Una medición BLOQUEADA no puede reprobar la validación.

    Las compuertas se filtraban por `estado in COMPUERTAS`, y `BLOQUEADO` está
    en esa tupla: bastaba que M3 no pudiera correr —o que se pidiera `--dry`—
    para que una MEDICIÓN entrara al código de salida, justo lo que
    `VALIDATION.md` declara imposible.
    """
    validate.main(["--json", "--dry"])
    salida = json.loads(capsys.readouterr().out)
    assert set(salida["compuertas"]) == {
        "G1 reproducibilidad", "G2 no contaminación", "G3 calibración base",
    }
    m3 = next(f for f in salida["filas"] if f["nombre"].startswith("M3"))
    assert m3["estado"] == "BLOQUEADO"
    assert "M3" not in " ".join(salida["compuertas"])


@pytest.mark.parametrize("bandera", ["--dry", "--json"])
def test_las_banderas_existen(bandera):
    """`--dry` estaba citado en el informe del juez científico y no existía.

    `scripts/validate.py` no tenía `argparse`, así que cualquier bandera se
    ignoraba en silencio: el comando del informe corría la validación completa
    mientras su autor creía estar haciendo una pasada seca.
    """
    assert validate.main([bandera, "--json"]) in (0, 1)
