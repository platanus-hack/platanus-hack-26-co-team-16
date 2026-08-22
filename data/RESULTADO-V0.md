# Resultado V0 — BLOQUEADO

V0 no se pudo ejecutar en esta máquina el 2026-08-22. El entorno niega conexiones de red a
`microdatos.dane.gov.co`, por lo que no fue posible leer el catálogo 853, verificar los IDs de
enero–junio de 2025 ni descargar GEIH 2025. No se sustituyeron por IDs inferidos.

## Valores disponibles antes de V0

- Proxy GEIH 2026 enero–junio, con filtro de ingreso: **30,57%**.
- Proxy GEIH 2026 abril–junio con el mismo filtro de ingreso del constructor: **30,81%**.
- Proxy GEIH 2026 abril–junio sin filtro de ingreso: **31,17%**. Esta cifra no es
  comparable con `momentos.json`; usarla en V0 violaría el requisito proxy-contra-proxy.
- Predicción registrada del modelo: brecha **+33,3 pp**; ronda 3 **63,8%**.
- Rango entre paráfrasis registrado: **47,9%–81,8%**; ancho **33,9 pp**.

## Valores que siguen bloqueados

- Proxy GEIH 2025 enero–junio.
- Proxy GEIH 2025 abril–junio.
- Delta observado 2025→2026.
- Error absoluto y firmado del modelo.
- Error del baseline de persistencia B1 y `skill = 1 − error_modelo/error_baseline`.
- Cobertura de la banda contra V0.

`python scripts/validate.py` computará estas magnitudes proxy contra proxy cuando existan
`data/raw/GEIH_2025_<mes>/CSV/` y `data/momentos_2025.json`.
