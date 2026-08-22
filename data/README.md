# `data/` — de la GEIH del DANE a la población de agentes

**Dueño: Alejo (R1).** Aquí no se inventa nadie: cada agente es una persona real anonimizada
de la Gran Encuesta Integrada de Hogares (GEIH) del DANE. Todo lo que hay en esta carpeta
se reproduce con dos comandos.

## Fuente exacta

| | |
|---|---|
| Fuente | DANE — GEIH, **microdatos anonimizados de uso público** (gratuitos, sin registro para descarga directa) |
| Catálogo | <https://microdatos.dane.gov.co/index.php/catalog/900> (GEIH 2026) |
| Archivos | `Enero 2026.zip` … `Junio 2026.zip` — los 6 meses publicados a la fecha de descarga |
| Fecha de descarga | **2026-08-22** |
| Trazabilidad | `raw/DESCARGA.json`: URL exacta y **sha256** de cada zip (lo genera el script de descarga) |
| Módulos usados | `Ocupados` + `Características generales, seguridad social en salud y educación` |
| Diccionario | <https://microdatos.dane.gov.co/index.php/catalog/900/data-dictionary> |

Los crudos (~65 MB/mes) no van al repo (`data/.gitignore`); cualquiera los reproduce con el
script y verifica el sha256 contra `raw/DESCARGA.json`.

## Reproducir

```bash
python data/descargar_geih.py       # baja y descomprime los 6 zips + DESCARGA.json
python data/construir_poblacion.py  # crudo -> poblacion.parquet + momentos.json
```

Determinista sin seed: no hay muestreo, solo transformación; dos corridas producen
archivos idénticos byte a byte (verificado por sha256).

## Transformaciones aplicadas (todas en `construir_poblacion.py`)

1. **Filtro Bogotá:** `AREA == 11` en el módulo Ocupados.
2. **Pooling de 6 meses** (enero–junio 2026) para densidad muestral por arquetipo;
   el factor de expansión mensual `FEX_C18` se divide entre 6 (práctica estándar para
   promedios de período). Verificado: ningún `DIRECTORIO` se repite entre meses en los
   microdatos públicos, así que nadie queda contado dos veces.
3. **Ingreso:** `INGLABO` (ingreso laboral mensual total calculado por el DANE).
   Los registros sin `INGLABO` se **descartan, no se imputan** (el conteo exacto queda en
   `momentos.json → n_descartados_sin_ingreso`).
4. **Formalidad:** proxy por cotización a pensión (`P6920`). Los supuestos exactos están
   marcados `# SUPUESTO:` en el script (greppables); el sesgo del proxy se evalúa contra la
   serie oficial de informalidad en el candado 1 de validación.
5. **Sector:** `RAMA2D_R4` (CIIU Rev. 4 A.C. a 2 dígitos) agrupada en 9 sectores; la tabla
   de rangos está en el script.
6. **Educación:** `P3042` (13 niveles del diccionario DANE) agrupada en 5 niveles.
7. **Arquetipo (preliminar):** sector × tamaño (micro/pyme/grande, de `P3069`) ×
   formal/informal × tercil de ingreso ponderado, con colapso determinista de celdas con
   <60 observaciones muestrales. Resultado: **67 arquetipos**. La definición final se
   cierra con Nico (R3); es una sola función en el script.

## Salidas y números de control (corrida del 2026-08-22)

| Archivo | Qué es | Control |
|---|---|---|
| `poblacion.parquet` | 6.692 agentes-trabajadores de Bogotá, esquema = `contracts/agente.json` | Suma de `factor_expansion` = **4.199.644 ocupados** — comparable con la serie oficial de ocupados de Bogotá del DANE |
| `momentos.json` | Objetivos de calibración: informalidad total (**30,6%** con el proxy), por sector y por tamaño (micro 66,7% / pyme 10,6% / grande 0,8%), percentiles salariales, terciles | Contrastar contra la [serie oficial de empleo informal del DANE](https://www.dane.gov.co/index.php/estadisticas-por-tema/mercado-laboral/empleo-informal-y-seguridad-social) — candado 1 de `VALIDATION.md` |

**Hallazgo V9 (para R5):** el "spike" de masa salarial existe y es visible — **12,1% de toda
la masa salarial de Bogotá está exactamente en 1.750.000 COP** (la moda observada; confirmar
contra el SMLMV 2026 con la serie de decretos, V4).

## Verificación V2 — panel rotativo: **NO en los microdatos públicos**

Chequeo empírico (no de documentación): entre enero y febrero 2026 hay **0** valores de
`DIRECTORIO` repetidos en Bogotá (y 0 entre enero y junio). En los archivos anonimizados de
uso público los identificadores no enlazan entre meses, así que **no se pueden observar
transiciones de la misma persona**. Se calibra contra la historia agregada, como preveía el
plan B de V2 (`docs/PLAN.md` §6). No bloqueante.
