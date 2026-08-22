"""Descarga reproducible de la GEIH (DANE) — enero a junio 2026, modulo de informalidad.

Fuente: Archivo Nacional de Datos (ANDA) del DANE.
  Catalogo GEIH 2026: https://microdatos.dane.gov.co/index.php/catalog/900
  Meses publicados al 2026-08-22: enero a junio. Descarga directa verificada
  sin login (microdatos anonimizados de uso publico, gratuitos).
  Se apilan 6 meses para densidad muestral por arquetipo en Bogota
  (~1.100 ocupados/mes en la muestra de Bogota; con 6 meses ~6.500).

Uso:  python data/descargar_geih.py
Deja: data/raw/GEIH_2026_<mes>.zip + carpeta descomprimida por mes
      data/raw/DESCARGA.json (URLs exactas, fecha, sha256 — trazabilidad)
"""

from __future__ import annotations

import datetime
import hashlib
import json
import sys
import zipfile
from pathlib import Path

import requests

CATALOGO = 900  # GEIH 2026 en el ANDA del DANE
# id de descarga por mes, tomado de la pagina get-microdata del catalogo 900
MESES = {
    "enero": 24530,
    "febrero": 24594,
    "marzo": 24674,
    "abril": 24703,
    "mayo": 24731,
    "junio": 24760,
}

RAW = Path(__file__).parent / "raw"


def sha256_de(ruta: Path) -> str:
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()


def main() -> None:
    RAW.mkdir(exist_ok=True)
    registro = {
        "fuente": "DANE - Gran Encuesta Integrada de Hogares (GEIH), microdatos anonimizados de uso publico",
        "catalogo": f"https://microdatos.dane.gov.co/index.php/catalog/{CATALOGO}",
        "fecha_descarga": datetime.date.today().isoformat(),
        "archivos": [],
    }

    for mes, archivo_id in MESES.items():
        url = f"https://microdatos.dane.gov.co/index.php/catalog/{CATALOGO}/download/{archivo_id}"
        zip_path = RAW / f"GEIH_2026_{mes}.zip"

        if not zip_path.exists():
            print(f"Descargando {mes} 2026: {url} ...")
            with requests.get(url, stream=True, timeout=180) as r:
                r.raise_for_status()
                with open(zip_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=1 << 20):
                        f.write(chunk)
            print(f"  OK ({zip_path.stat().st_size / 1e6:.1f} MB)")
        else:
            print(f"Ya existe {zip_path.name}, no se vuelve a descargar.")

        destino = RAW / f"GEIH_2026_{mes}"
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
    sys.exit(main())
