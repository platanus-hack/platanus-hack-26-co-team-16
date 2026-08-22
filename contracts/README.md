# Contratos de datos — la especificación viva

> **Congelados a partir de H+4.** Después de eso, cambiar cualquiera de estos JSON exige avisar en el grupo **ANTES** de tocar nada (regla de `AGENTS.md`). Todos construyen contra estos **ejemplos concretos**, nunca contra un tipo vacío.

| Contrato | Qué representa | Productor → Consumidor | Lo congela |
|---|---|---|---|
| [`agente.json`](agente.json) | Una fila de la GEIH transformada: un agente-trabajador | Alejo (`data/`) → Manuel (`engine/`), Nico (`behavior/`) | Alejo (con Manuel) |
| [`decision.json`](decision.json) | Propuesta de estrategia de la capa LLM + veredicto del veto | Nico (`behavior/`) ↔ Manuel (`engine/`) | Manuel ↔ Nico |
| [`ronda.json`](ronda.json) | Agregado por ronda hacia el frontend y de vuelta a los agentes | Manuel (`api/`) → Dani (`web/`) | Manuel (con Dani) |

## `agente.json` — procedencia campo a campo (GEIH real, catálogo 900 del DANE)

Verificado contra los microdatos descargados (GEIH 2026, enero–junio, módulos `Ocupados` y
`Características generales, seguridad social en salud y educación`) y contra el diccionario
de datos del ANDA (`microdatos.dane.gov.co/index.php/catalog/900/data-dictionary`).

| Campo | Variable(s) GEIH | Transformación |
|---|---|---|
| `id` | `PERIODO`+`DIRECTORIO`+`SECUENCIA_P`+`ORDEN` | `geih-2026-mMM-NNNNN`: identificador único del registro, no re-identificable |
| `tipo` | — | Constante `"trabajador"`. Las empresas se derivan agrupando trabajadores por sector × tamaño |
| `ciudad` | `AREA == 11` | Filtro: Bogotá D.C. (código de área metropolitana del DANE) |
| `sector` | `RAMA2D_R4` | CIIU Rev. 4 A.C. a 2 dígitos, agrupado en ~9 sectores (tabla en `data/construir_poblacion.py`) |
| `tamano_empresa` | `P3069` | Código 1–10 tal cual viene: 1=trabaja solo · 2=2-3 · 3=4-5 · 4=6-10 · 5=11-19 · 6=20-30 · 7=31-50 · 8=51-100 · 9=101-200 · 10=201+ personas |
| `ingreso_mensual_cop` | `INGLABO` | Ingreso laboral mensual total calculado por el DANE, en COP corrientes |
| `formal` | `P6920` | `true` si cotiza a pensión (`P6920 == 1`); pensionados (`3`) se tratan como formales. Es un proxy de la definición OIT — marcado `# SUPUESTO:` en el script |
| `educacion` | `P3042` | Nivel educativo (1–13, dicc. DANE) agrupado en: `primaria`, `secundaria`, `media`, `tecnica`, `universitaria` |
| `factor_expansion` | `FEX_C18` | Factor de expansión del DANE **÷ número de meses apilados** (6), práctica estándar para pooling mensual de la GEIH |
| `arquetipo` | derivado | sector × tamaño (micro/pyme/grande) × formal/informal × tercil de ingreso. **Preliminar** — la definición final se cierra con Nico (R3) hacia H+14 |

Los valores del ejemplo son ilustrativos del **tipo y formato**; los reales salen de
`data/poblacion.parquet`.

## `decision.json` y `ronda.json`

Copiados tal cual de `docs/PLAN.md` §4 — la interfaz del veto (Manuel↔Nico) y del agregado
(Manuel→Dani) no depende de columnas de la GEIH. Ejemplo de veto negado (mismo esquema):

```json
"veto": { "factible": false, "razon": "flujo de caja insuficiente para pagar indemnizaciones de despido" }
```
