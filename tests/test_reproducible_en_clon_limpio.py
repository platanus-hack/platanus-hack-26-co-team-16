"""EL NÚMERO tiene que salir en un clon recién clonado, sin crudos.

Por qué existe: `README.md` y `AGENTS.md` prometen que un extraño reproduce el
número con un comando, y `VALIDATION.md` lo repite. Una auditoría post-merge
encontró que era falso: `medicion_v0()` exigía los seis directorios de
`data/raw/GEIH_2025_*`, que pesan ~370 MB y están gitignorados. En la máquina
del autor funcionaba porque tenía los crudos de haberlos descargado; en un clon
limpio, M1/M2 y EL NÚMERO quedaban BLOQUEADOS.

La promesa se sostiene porque los dos momentos que V0 necesita —el proxy de 2025
y el de 2026— viven en `data/momentos_2025.json` y `data/momentos.json`, que sí
están versionados. Los crudos solo hacen falta para el corte abr–jun, que es un
extra para contrastar contra el trimestre que publica el DANE.

Este test simula el clon limpio: un `data/` con solo los tres JSON versionados y
sin `raw/`. Si alguien vuelve a meter una dependencia de los crudos en el camino
principal, esto se pone rojo.
"""

import importlib.util
import shutil
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]

# Lo único que un clon limpio tiene de `data/` para computar V0.
VERSIONADOS = ("momentos.json", "momentos_2025.json", "prediccion_modelo.json")


def _validador_con_data(data_dir: Path):
    spec = importlib.util.spec_from_file_location("validate_aislado", RAIZ / "scripts" / "validate.py")
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    modulo.DATA = data_dir
    return modulo


def _data_de_clon_limpio(destino: Path) -> Path:
    data = destino / "data"
    data.mkdir()
    for nombre in VERSIONADOS:
        shutil.copy(RAIZ / "data" / nombre, data / nombre)
    assert not (data / "raw").exists(), "el clon limpio no puede traer crudos"
    return data


def test_el_numero_sale_sin_crudos(tmp_path):
    """Sin `data/raw/`, V0 igual entrega error, skill y el rango entre parafrasis."""
    v = _validador_con_data(_data_de_clon_limpio(tmp_path))
    estado, detalle, numeros = v.medicion_v0()

    assert estado is v.Estado.MEDIDO, f"V0 quedó {estado.value} en un clon limpio: {detalle}"
    assert numeros is not None
    # B3: la clave se llamaba "cobertura"; hoy es "observado_en_rango", porque
    # con N=5 el rango es un min-max entre parafrasis y no una cobertura de
    # ningun nivel. Ver scripts/validate.py.
    for clave in ("error_absoluto_pp", "error_firmado_pp", "skill_b1", "observado_en_rango"):
        assert numeros[clave] is not None, f"falta {clave} sin crudos"

    # El corte abr-jun es el ÚNICO que puede faltar, y falta en silencio.
    assert numeros["delta_abr_jun_pp"] is None
    assert "opcional" in detalle


def test_el_numero_no_cambia_por_tener_crudos_o_no(tmp_path):
    """Con crudos y sin crudos, el número principal es el mismo.

    Si difiriera, la ventana ene-jun estaría contaminada por el camino de los
    crudos y el backtest dejaría de ser proxy contra proxy.
    """
    limpio = _validador_con_data(_data_de_clon_limpio(tmp_path))
    _, _, sin_crudos = limpio.medicion_v0()

    completo = _validador_con_data(RAIZ / "data")
    _, _, con_crudos = completo.medicion_v0()

    for clave in ("pre_ene_jun_pct", "post_ene_jun_pct", "delta_ene_jun_pp",
                  "error_absoluto_pp", "skill_b1"):
        assert sin_crudos[clave] == con_crudos[clave], f"{clave} cambia según haya crudos"


def test_la_prediccion_del_modelo_es_un_artefacto_y_no_una_constante():
    """El delta del modelo tiene que venir de un archivo rastreable.

    Estaba como `DELTA_MODELO_PP = 33.3` dentro del validador: un número mágico
    que nadie podía rastrear ni notar si quedaba viejo.
    """
    artefacto = RAIZ / "data" / "prediccion_modelo.json"
    assert artefacto.exists(), "falta data/prediccion_modelo.json"

    v = _validador_con_data(RAIZ / "data")
    pred = v._prediccion()
    assert pred["brecha_pp"] == 33.3
    assert pred["rango_entre_parafrasis_pct"] == [47.9, 81.8]

    fuente = artefacto.read_text(encoding="utf-8")
    assert "behavior/README.md" in fuente, "el artefacto debe decir de qué corrida salió"
