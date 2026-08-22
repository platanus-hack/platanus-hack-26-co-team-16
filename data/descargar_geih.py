"""Descarga reproducible de la GEIH (DANE) — enero a junio del año solicitado.

Fuente: Archivo Nacional de Datos (ANDA) del DANE.
  Catalogo GEIH 2026: https://microdatos.dane.gov.co/index.php/catalog/900
  Meses publicados al 2026-08-22: enero a junio. Descarga directa verificada
  sin login (microdatos anonimizados de uso publico, gratuitos).
  Se apilan 6 meses para densidad muestral por arquetipo en Bogota
  (~1.100 ocupados/mes en la muestra de Bogota; con 6 meses ~6.500).

Uso:  python data/descargar_geih.py [--anio 2026]
Deja: data/raw/GEIH_<anio>_<mes>.zip + carpeta descomprimida por mes
      data/raw/DESCARGA.json (URLs exactas, fecha, sha256 — trazabilidad)
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import html
import json
import re
import sys
import zipfile
from pathlib import Path

import requests

CATALOGOS = {2024: 819, 2025: 853, 2026: 900}

# IDs verificados en la página get-microdata del catálogo 900. Para los demás
# años se leen de la página del catálogo en tiempo de ejecución: nunca se
# infieren por proximidad numérica.
IDS_2026 = {
    "enero": 24530,
    "febrero": 24594,
    "marzo": 24674,
    "abril": 24703,
    "mayo": 24731,
    "junio": 24760,
}

RAW = Path(__file__).parent / "raw"

MESES = ("enero", "febrero", "marzo", "abril", "mayo", "junio")


def ids_desde_catalogo(catalogo: int) -> dict[str, int]:
    """Extrae mes -> id de las filas de recursos publicadas por ANDA."""
    paginas = (
        f"https://microdatos.dane.gov.co/index.php/catalog/{catalogo}",
        # SUPUESTO: ANDA publica la tabla de recursos en get_microdata (guion
        # bajo). La variante con guion medio responde 200 pero SIN la tabla, asi
        # que el descubrimiento salia vacio. Se consultan las dos por si cambia.
        f"https://microdatos.dane.gov.co/index.php/catalog/{catalogo}/get_microdata",
        f"https://microdatos.dane.gov.co/index.php/catalog/{catalogo}/get-microdata",
    )
    encontrados: dict[str, set[int]] = {mes: set() for mes in MESES}
    patron_id = re.compile(rf"catalog/{catalogo}/download/(\d+)", re.IGNORECASE)

    for pagina in paginas:
        try:
            respuesta = requests.get(pagina, timeout=60)
        except requests.RequestException as exc:
            raise RuntimeError(
                f"no se pudo consultar {pagina}; no se usarán IDs no verificados: {exc}"
            ) from exc
        respuesta.raise_for_status()
        contenido = respuesta.text
        # Un bloque de recurso contiene a la vez el nombre del mes y la URL de
        # descarga. Asociarlos solo dentro de ese bloque evita asignar un ID por
        # orden o cercanía, que sería adivinar.
        # ANDA lista cada archivo en un <div class="resource">, no en un <tr>.
        # Se parte por ese div y además se aceptan filas de tabla, por si el
        # portal cambia de plantilla.
        filas = re.split(r'(?i)(?=<div[^>]*class="[^"]*\bresource\b)', contenido)
        filas += re.findall(r"<tr\b[^>]*>.*?</tr>", contenido, flags=re.IGNORECASE | re.DOTALL)
        for fila in filas:
            texto = html.unescape(re.sub(r"<[^>]+>", " ", fila)).lower()
            ids = {int(x) for x in patron_id.findall(html.unescape(fila))}
            for mes in MESES:
                if mes in texto:
                    encontrados[mes].update(ids)

    ambiguos = {mes: sorted(ids) for mes, ids in encontrados.items() if len(ids) != 1}
    if ambiguos:
        raise RuntimeError(
            "ANDA no publicó un ID único por mes; no se descargará nada. "
            f"Catálogo {catalogo}, hallazgos: {ambiguos}"
        )
    return {mes: next(iter(encontrados[mes])) for mes in MESES}


def sha256_de(ruta: Path) -> str:
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description="Descarga GEIH enero-junio desde ANDA.")
    parser.add_argument("--anio", type=int, choices=tuple(CATALOGOS), default=2026)
    args = parser.parse_args()
    anio = args.anio
    catalogo = CATALOGOS[anio]
    ids = IDS_2026 if anio == 2026 else ids_desde_catalogo(catalogo)

    RAW.mkdir(exist_ok=True)
    registro = {
        "fuente": "DANE - Gran Encuesta Integrada de Hogares (GEIH), microdatos anonimizados de uso publico",
        "catalogo": f"https://microdatos.dane.gov.co/index.php/catalog/{catalogo}",
        "fecha_descarga": datetime.date.today().isoformat(),
        "archivos": [],
    }

    for mes in MESES:
        archivo_id = ids[mes]
        url = f"https://microdatos.dane.gov.co/index.php/catalog/{catalogo}/download/{archivo_id}"
        zip_path = RAW / f"GEIH_{anio}_{mes}.zip"

        if not zip_path.exists():
            print(f"Descargando {mes} {anio}: {url} ...")
            with requests.get(url, stream=True, timeout=180) as r:
                r.raise_for_status()
                with open(zip_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=1 << 20):
                        f.write(chunk)
            print(f"  OK ({zip_path.stat().st_size / 1e6:.1f} MB)")
        else:
            print(f"Ya existe {zip_path.name}, no se vuelve a descargar.")

        destino = RAW / f"GEIH_{anio}_{mes}"
        if not destino.exists():
            with zipfile.ZipFile(zip_path) as z:
                z.extractall(destino)

        registro["archivos"].append(
            {"mes": mes, "url_descarga": url, "archivo": zip_path.name, "sha256": sha256_de(zip_path)}
        )

    with open(RAW / "DESCARGA.json", "w", encoding="utf-8") as f:
        json.dump(registro, f, ensure_ascii=False, indent=2)
    print("Registro de trazabilidad: data/raw/DESCARGA.json")


if __name__ == "__main__":
    try:
        sys.exit(main())
    except RuntimeError as exc:
        print(f"BLOQUEADO: {exc}", file=sys.stderr)
        sys.exit(2)
