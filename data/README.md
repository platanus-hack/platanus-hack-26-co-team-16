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
python data/parametros_legales.py   # normativa -> parametros_legales.json
python data/construir_empresas.py   # poblacion + normativa -> empresas.parquet
```

Determinista sin seed: no hay muestreo, solo transformación; dos corridas producen
archivos idénticos byte a byte (verificado por sha256).

### Corte abril–junio para el contraste oficial

La ventana del proyecto apila enero–junio para construir la población. El DANE publica
la cifra comparable como trimestre **abril–junio**, así que ese corte se conserva aparte.
No se genera otro parquet: el corte solo sirve para el contraste y duplicaría microdatos
sin aportar otro entregable.

```bash
python data/construir_poblacion.py --anio 2026 --meses abril,mayo,junio
python data/construir_poblacion.py --anio 2025 --meses abril,mayo,junio
```

| Artefacto | Informalidad total (proxy de pensión) |
|---|---|
| `momentos_abr_jun.json` (2026) | **30,81%** |
| `momentos_abr_jun_2025.json` (2025) | **33,25%** |

**Por qué esto existe como artefacto y no como una nota a mano.** La brecha contra el DANE
(33,3% oficial abr–jun 2026 − 30,81% nuestro = **2,49 pp**) estuvo publicada como *≈2,1 pp*
durante casi seis horas: el número era correcto cuando se escribió, el proxy se movió 18
minutos después y nadie recalculó la resta. Un número sin script que lo produzca se queda
viejo en silencio, y este además subestimaba **a nuestro favor** la limitación declarada.
Cada archivo lleva dentro la ventana que usó (clave `meses`), así que la cifra no depende
de que alguien recuerde de qué corte salió.

**Lo que el corte deja comparar, y antes no se podía:** el delta abr–jun del proxy entre
2025 y 2026 es **−2,44 pp** (33,25 → 30,81), contra el **−2,30 pp** de la serie oficial en
esa misma ventana. Antes solo se podía contrastar ene–jun (−4,07 pp) contra abr–jun
(−2,30 pp), que son ventanas distintas. Misma ventana, dos definiciones, y la dirección y
la magnitud coinciden.

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

**Hallazgo V9 — cerrado, y V4 con él.** El "spike" de masa salarial existe y es visible:
**12,1% de toda la masa salarial de Bogotá está exactamente en 1.750.000 COP**. El SMLMV 2026
verificado es **1.750.905 COP** (Decreto 1469 de 2025), o sea la moda observada **es** el
salario mínimo, redondeado por el encuestado. La población reproduce el spike sin que nadie
se lo haya impuesto: es el primer indicio de que los microdatos y la política se tocan donde
deben. El aumento del 23% del caso demo también queda verificado contra el decreto
(1.423.500 → 1.750.905 = +23,0%), no supuesto.

## El lado empleador: `parametros_legales.json` y `empresas.parquet`

La GEIH es una encuesta de **hogares**: cada fila es una persona. Pero el veto del motor
([ADR 0003](../docs/adr/0003-veto-de-factibilidad.md)) decide sobre una **firma**. Estos dos
archivos construyen ese lado sin inventarlo.

**`parametros_legales.json`** — el costo legal de la formalidad, tasa por tasa, cada una con
su norma y su URL (Ley 100, Ley 21/1982, Decreto 1772/1994, Arts. 186/249/306/64 del CST,
Art. 114-1 del ET). Reemplaza el supuesto S1 de `engine/MODELO.md` ("factor prestacional
≈1,4–1,5, sin cifra exacta verificada") y el coeficiente `ingreso * 1.5` que `behavior/`
usaba como andamio para el despido.

Dos hallazgos que cambian el modelo, no solo el número:

1. **El factor prestacional no es un número con incertidumbre: son dos, y el tamaño del
   empleador decide cuál.** El Art. 114-1 del Estatuto Tributario exonera de salud patronal
   (8,5%), SENA (2%) e ICBF (3%) a quien emplee **2 o más** trabajadores que ganen menos de
   10 SMLMV. Un empleador de **un solo** trabajador paga esos 13,5 puntos. El rango completo
   va de **1,384 a 1,583**, y el motor debe **asignar** el factor que corresponde a cada
   firma, no promediar el rango.
2. **El auxilio de transporte (249.095 COP) es un costo fijo, no un porcentaje.** Sobre el
   salario mínimo pesa **14,2%**; sobre un salario de 4 millones no se paga. Encarece la
   formalidad justo en el tramo bajo, que es donde vive la informalidad.

**`empresas.parquet`** — 81 celdas de empleador (sector × código de tamaño `P3069`), con
headcount, nómina, mezcla formal/informal, costo de la formalidad y a cuántas empresas reales
representa cada celda.

| Control | Valor |
|---|---|
| Empresas expandidas de Bogotá | **368.491** |
| Trabajadores con empleador | 3.235.639 |
| Cuenta propia (código 1, sin nómina) | 964.004 — **22,9%** de los ocupados |
| Celdas que pierden la exoneración del Art. 114-1 | 10 de 81 |

El resultado que importa para el pitch: **formalizar a un trabajador cuesta hasta 74,9% sobre
su salario en una micro, contra 40,3% en una grande.** Esa regresividad no es un parámetro
que hayamos elegido — sale de la frontera de la exoneración, del auxilio fijo y de la clase
de riesgo, las tres verificables contra la norma.

**Lo que estos archivos NO resuelven.** La GEIH no observa ingresos, activos ni márgenes de
las empresas, así que **el flujo de caja no se puede derivar de ella**. Se emite como un
supuesto explícito y parametrizado (`MARGEN_SOBRE_NOMINA = 0.18`, rango de barrido
0,05–0,40) para que viva en **un solo lugar con nombre**, en vez de aparecer como un `0.18`
suelto dentro de otra carpeta. Es el parámetro número uno que R5 debe barrer: el veto lo usa
como techo duro.

## Verificación V2 — panel rotativo: **NO en los microdatos públicos**

Chequeo empírico (no de documentación): entre enero y febrero 2026 hay **0** valores de
`DIRECTORIO` repetidos en Bogotá (y 0 entre enero y junio). En los archivos anonimizados de
uso público los identificadores no enlazan entre meses, así que **no se pueden observar
transiciones de la misma persona**. Se calibra contra la historia agregada, como preveía el
plan B de V2 (`docs/PLAN.md` §6). No bloqueante.
