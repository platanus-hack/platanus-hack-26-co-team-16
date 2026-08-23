# Variables GEIH que entran al modelo

> **Qué es este archivo.** El inventario reproducible de atributos de la GEIH 2026 que
> entran, podrían entrar o quedan fuera del modelo. Aplica el criterio de Pattern-Oriented
> Modeling de [`docs/investigacion/1-teorica.md`](../docs/investigacion/1-teorica.md) §1 a
> 6.692 ocupados de Bogotá con `AREA == 11` e `INGLABO` observado, apilados entre enero y
> junio de 2026. Documenta el estado medido el **2026-08-22**; no cambia contratos ni es una
> decisión normativa.

## Método y límite de las etiquetas

Las coberturas son `no nulos / 6.692` y los conteos son muestrales, salvo donde se indica
ponderación por `FEX_C18`. Se releyeron los CSV de `data/raw/GEIH_2026_*/CSV/`; no se
regeneró ningún Parquet.

Los DTA de enero no permiten recuperar las etiquetas de valor. En
`data/raw/GEIH_2026_enero/DAT/`, `StataReader.value_labels()` devuelve `{}` y el bloque
binario de cada archivo termina en `<value_labels></value_labels>`. La lectura con
`convert_categoricals=True` conserva números. Por eso este archivo no inventa equivalencias:

| Variable | Códigos observados en enero | Etiquetas oficiales |
|---|---:|---|
| `P6430` | 1, 2, 3, 4, 5, 6, 7, 8 | ⚠️ Pendientes de verificar contra el diccionario ANDA |
| `P6880` | 1–11 | ⚠️ Pendientes de verificar contra el diccionario ANDA |
| `P6440` | 1, 2 | ⚠️ Pendientes de verificar contra el diccionario ANDA |
| `P6450` | 1, 2, 9 | ⚠️ Pendientes de verificar contra el diccionario ANDA |
| `P6460` | 1, 2, 9 | ⚠️ Pendientes de verificar contra el diccionario ANDA |
| `P7240` | 1–10 | ⚠️ Pendientes de verificar contra el diccionario ANDA |
| `P6990` · `P9450` | 1, 2, 9 | ⚠️ Pendientes de verificar contra el diccionario ANDA |
| `P1879` | 1–11 | ⚠️ Pendientes de verificar contra el diccionario ANDA |
| `P6100` | 1, 2, 3, 9 | ⚠️ Pendientes de verificar contra el diccionario ANDA |

Los nombres cortos usados abajo describen la pregunta, no asignan significado a un código.
`P6870` y `P6210`, citadas en literatura y tutoriales de versiones anteriores, **no existen**
en estos archivos de la GEIH 2026. Sus reemplazos presentes son `P3069` y `P3042`.

## El criterio: cuatro puertas

Una variable entra solo si pasa al menos una puerta. Existir en la encuesta no basta.

| Puerta | Pregunta operativa |
|---|---|
| **A · Pago** | ¿Cambia un número de la comparación formal frente a informal? |
| **B · Factibilidad** | ¿Cambia lo que el veto puede rechazar? |
| **C · Corte** | ¿Es dimensión del mapa distributivo (dato A3) o del arquetipo? |
| **D · Dispersión** | ¿Hace que dos agentes iguales en los atributos actuales decidan distinto? |

## Qué hay hoy

`data/poblacion.parquet` tiene 6.692 filas y estas **10 columnas**:

| Columna | Origen |
|---|---|
| `id` · `tipo` · `ciudad` · `arquetipo` | Derivadas por `data/construir_poblacion.py` |
| `sector` | `RAMA2D_R4` |
| `tamano_empresa` | `P3069` |
| `ingreso_mensual_cop` | `INGLABO` |
| `formal` | Proxy `P6920 ∈ {1, 3}` |
| `educacion` | `P3042` |
| `factor_expansion` | `FEX_C18 / 6` |

`tamano_empresa` es el **código ordinal 1–10 de `P3069`, no un headcount**. La equivalencia
está declarada en `contracts/README.md:23`; confundirlos ya produjo el bug documentado en el
PR #4 y en `behavior/arquetipos.py:100-106`.

Enero trae 208 columnas en `Ocupados`, 55 en Características generales, 112 en Otras formas
de trabajo, 60 en Otros ingresos e impuestos, 49 en Datos del hogar y la vivienda, 43 en
Migración, 42 en Fuerza de trabajo y 36 en No ocupados. Aunque el lector carga las 208
columnas de `Ocupados`, la transformación referencia **10 variables de entrada** de ese
módulo —las cuatro llaves más `AREA`, `INGLABO`, `P6920`, `RAMA2D_R4`, `P3069` y `FEX_C18`—
y una variable no llave de Características generales, `P3042`. No son 11 variables de
`Ocupados`.

## Tier 1 — corrigen una rotura o un supuesto activo

| Variable | Módulo | Cobertura | Puerta | Qué arregla |
|---|---|---:|---|---|
| `P6430` posición ocupacional | Ocupados | 100,0% | A · B · C | Separa asalariados, cuenta propia, patrones y empleo público antes de construir firmas. |
| `P6426` antigüedad, meses | Ocupados | 100,0% | B · D | Reemplaza los 3 años fijos del costo de despido. |
| `P6800` / `P6850` horas | Ocupados | 100,0% | A · B | Hace aplicable y medible `bajar_horas`. |
| `P6440` / `P6450` / `P6460` contrato | Ocupados | 100,0% / 74,5% / 61,0% | B | Decide si existe contrato y qué terminación genera indemnización. |
| `P6880` lugar de trabajo | Ocupados | 100,0% | A · C · D | Permite distribuir inspecciones por observabilidad sin cambiar la capacidad fija. |
| `P6040` edad · `P3271` sexo | Características generales | 100,0% / 100,0% | C | Habilita el corte edad × sexo × educación del contraste externo. |
| `P6100` régimen de salud | Características generales | 94,7% | A · C · D | Permite distinguir el costo de perder protección según régimen. |

### P6430 — la unidad que decide

`data/construir_empresas.py:98-102` excluye `tamano_empresa == 1`: son **1.570** filas. El
corte por posición ocupacional identifica **2.086** cuenta propia y **187** patrones; también
separa **290** empleados públicos. Las interpretaciones de los códigos 4, 5 y 2 usadas en
esta comparación quedan ⚠️ pendientes de cotejar con la etiqueta oficial ANDA.

| Código `P6430` | n | Participación ponderada por `FEX_C18` |
|---:|---:|---:|
| 1 | 3.930 | 58,9% |
| 2 | 290 | 4,5% |
| 3 | 193 | 2,8% |
| 4 | 2.086 | 30,9% |
| 5 | 187 | 2,9% |
| 7 | 4 | 0,1% |
| 8 | 2 | 0,0% |

Mientras el corte sea `P3069 == 1`, 516 cuenta propia quedan tratadas como si tuvieran un
empleador y parte de los asalariados que trabajan solos pueden quedar excluidos. Una persona
cuenta propia no debe decidir con la lógica de una firma que puede informalizar a su
empleador; el empleo público tampoco es informalizable por la misma vía del demo.

### P6426 — el veto está en las colas

`data/parametros_legales.py:108-113` fija tres años. El supuesto acierta exactamente a la
mediana —36 meses— y no representa las colas: p10 es 3 meses, p90 es 204 meses y la media es
72,2 meses. `data/construir_empresas.py:154-155` aplica a las 81 celdas un costo fijo de
2,3333 salarios mensuales.

Para el tramo menor a 10 SMLMV, `data/parametros_legales.py:101-105` materializa el Art. 64
CST como 30 días el primer año y 20 días por año adicional. Aplicando proporcionalidad a la
fracción de año adicional, el costo implícito por decil es:

| Percentil | Antigüedad (meses) | Días de indemnización | Meses de salario |
|---:|---:|---:|---:|
| p10 | 3 | 30 | 1,00 |
| p20 | 7 | 30 | 1,00 |
| p30 | 12 | 30 | 1,00 |
| p40 | 24 | 50 | 1,67 |
| p50 | 36 | 70 | 2,33 |
| p60 | 48 | 90 | 3,00 |
| p70 | 72 | 130 | 4,33 |
| p80 | 120 | 210 | 7,00 |
| p90 | 204 | 350 | 11,67 |

El supuesto es insesgado en la mediana, donde el veto tiene menos información marginal, y
equivocado en las colas, donde el costo acumulado puede cruzar el techo de caja. El resultado
de 350 días, equivalente a 11,7 salarios mensuales para 17 años, contrasta con los 2,3333
meses aplicados hoy.

### Horas y contrato — estrategias que hoy no aterrizan

`bajar_horas` está en `behavior/prompts/sistema.md` y el veto reconoce
`reduccion_horas_pct` en `engine/veto.py:197`, pero `poblacion.parquet` no contiene horas.
`P6800` y `P6850` tienen cobertura completa y 79 y 85 valores distintos: sin ellas la
estrategia se acepta como porcentaje, pero no se aplica a una jornada observada ni se mide.

`P6440` cuenta 4.983 personas con código 1 y 1.709 con código 2; la lectura
“con contrato/sin contrato” queda ⚠️ pendiente de la etiqueta ANDA. `P6450` y `P6460` tienen
4.983 y 4.080 respuestas. Sus coberturas de 74,5% y 61,0% no son imputables como faltantes:
son saltos estructurales de preguntas condicionadas. El salto informa si hay contrato y si
procede la terminación que el veto pretende costear. La regla jurídica exacta por tipo de
contrato requiere validación normativa de R2; este archivo solo identifica el dato.

### P6880 — selección de inspecciones

El código 7 concentra 4.024 de 6.692 personas (60,1%); siguen 1 (992), 2 (558), 4 (443),
6 (264), 5 (257), 9 (118), 8 (24), 11 (6), 3 (4) y 10 (2). Sin etiquetas oficiales no se
asigna aquí cuáles códigos son local fijo, calle o vivienda. Una vez verificados, `P6880`
permite que `p_i` dependa de inspeccionabilidad. La capacidad agregada continúa fija: aparece
selección, no una segunda perilla, en línea con `docs/adr/0006-fiscalizacion-es-estado-del-mundo.md`.

### Edad y sexo — candado de validación

El contraste de Banco de la República indicado para esta tarea reporta un efecto por
edad × sexo × educación y un rango de **+0,35 a +0,99 pp** de probabilidad de informalidad
ante +1 pp del MW ratio: <https://repositorio.banrep.gov.co/items/d9c8d84d-cd38-45a6-a2be-c9c4f2c1d438>.
⚠️ El contenido del documento externo no está reproducido en el repo y debe verificarse
contra la fuente antes de graduarlo a objetivo de calibración.

`docs/IDEA.md:211` y `docs/investigacion/1-teorica.md:143` citan **+0,21 pp** del WP 1104.
No es el mismo documento ni necesariamente la misma medida. El objetivo debe registrarse
como rango con fuente y definición, no mezclarse en un punto único. Sin `P6040` y `P3271` no
se puede puntuar el patrón por edad y sexo; `P3042` ya está en la población.

### P6100 — régimen de salud cruzado con formalidad

Distribución ponderada dentro de cada estado del proxy `formal`:

| `formal` | Código `P6100` | n | Participación dentro del estado |
|---|---:|---:|---:|
| No | 1 | 788 | 37,8% |
| No | 2 | 16 | 0,7% |
| No | 3 | 927 | 43,2% |
| No | 9 | 6 | 0,4% |
| No | salto estructural / no respuesta | 358 | 18,0% |
| Sí | 1 | 4.439 | 96,6% |
| Sí | 2 | 152 | 3,3% |
| Sí | 3 | 6 | 0,1% |

La hipótesis de uso es que estar en régimen subsidiado reduce la protección perdida al pasar
a informalidad y cambia el pago del trabajador. ⚠️ No se asigna “subsidiado” a un código
hasta verificar la etiqueta oficial de `P6100`.

## Tier 2 — contenido empírico para ADR 0008

`docs/adr/0008-asimetria-firma-trabajador.md` propone una prima de protección; el supuesto S3
vive en `engine/MODELO.md:64`. Estas variables permiten reemplazar un número global por
atributos observados. La propuesta sigue pendiente de implementación fuera de `data/`.

| Variables | Cobertura | Puerta | Uso |
|---|---:|---|---|
| `P1805` · `P1879` | 34,0% · 34,0% | A · C · D | Distinguen escape y exclusión entre quienes reciben el bloque condicionado de independencia. Marco: Perry et al., Banco Mundial (2007), <https://documents1.worldbank.org/curated/en/889371468313790669/pdf/400080PUB0SPAN101OFFICIAL0USE0ONLY1.pdf>. |
| `P7240` | 100,0% | A · D | Colchón declarado ante desempleo. |
| `P6050` + `DIRECTORIO` | 100,0% · 100,0% | A · C · D | Parentesco y hogar; permite identificar perceptores múltiples sin inventar convivencia. |
| `P7040` / `P7045` / `P7070` | 100,0% / 2,7% / 2,5% | A · D | Pluriempleo; los dos últimos son saltos condicionados. |
| `P6920` + `P6990` + `P9450` | 100,0% cada una | A · C | Pensión, ARL y caja convierten el proxy binario en una escalera de protección. |
| `P6090` | 100,0% | A · C | Afiliación a salud antes de distinguir el régimen con `P6100`. |
| `P3045S1` | 66,0% | A · C · D | Registro de la unidad para dirigir `p_i`; la cobertura refleja el bloque condicionado. |

`P1805`, `P1879` y `P6750` tienen 2.275 respuestas, no 2.273. El bloque equivale al 34,0%
de la muestra y es estructural: se pregunta a la población independiente. Dentro de él hay
2.086 cuenta propia + 187 patrones y dos observaciones con otro código de `P6430`; por eso
“2.273 propietarios” y “2.275 respuestas al bloque” no son el mismo conteo.

## Lo que no entra

| Variable o módulo | Razón de exclusión |
|---|---|
| `OFICIO_C8` · `RAMA4D_R4` | No abren una puerta adicional que justifique la fragmentación. En la muestra hay 343 oficios y 364 ramas a 4 dígitos, con mediana de 6 observaciones por código; `RAMA2D_R4` tiene 84 códigos y mediana 36. Se conserva el corte a 2 dígitos. |
| `P7170S*` satisfacción | No cambia pago, veto, corte declarado ni dispersión identificada. |
| `P550` cosecha | Cobertura 0,0% en Bogotá; cero observaciones. |
| `P6775` contabilidad | Cobertura 5,7% (384 observaciones); no sostiene un corte general. |
| Migración | No abre una puerta del mecanismo actual. |
| No ocupados | El modelo no tiene transición de entrada desde desempleo. |
| `P1881` / `P1882` transporte | No cambia un pago implementado ni el veto actual. |

## Dos defectos de datos

### 1. El proxy de informalidad no es la definición DANE

`data/momentos.json` publica **0,3057** para Bogotá 2026 enero–junio usando solo la regla
`P6920 ∈ {1, 3}` de `data/construir_poblacion.py:110-114`. La definición oficial requiere
cruzar posición ocupacional, tamaño y cotización; `data/README.md:38-40` ya declara que
`P6920` es un proxy.

⚠️ Cifras de prensa atribuyen al DANE entre **33,8% y 35,3%** en ventanas cercanas. No se
enuncian aquí como serie oficial hasta cotejarlas con el boletín y su ventana exacta. Si se
confirman, el hueco sería del orden de 3,2–4,7 pp frente a 30,57%, no un error que el candado
1 pueda ignorar.

### 2. El spike está etiquetado como masa salarial y no lo es

`data/construir_poblacion.py:185-190` redondea ingresos a 10.000 COP y calcula la participación
del **factor de expansión de trabajadores** en la moda. El resultado confirmado es 0,1207.
La participación de esos trabajadores en `Σ(FEX_C18 × INGLABO)` es **0,0617**.

| Medida sobre la moda redondeada a 1.750.000 COP | Participación |
|---|---:|
| Trabajadores expandidos | 12,07% |
| Masa salarial ponderada | 6,17% |

Corrección propuesta para `data/README.md:62-64`, sin editarlo en este informe:
“**12,1% de los trabajadores expandidos de Bogotá reporta un ingreso que redondea a
1.750.000 COP; representa 6,2% de la masa salarial ponderada**”. El valor observado no es el
SMLMV 2026 exacto de 1.750.905 COP registrado en `data/parametros_legales.py:43`; es el
redondeo del encuestado. Eso conserva el patrón P3 como amontonamiento alrededor del mínimo.

## Lo que la GEIH no entrega para el veto de caja

El parámetro más débil sigue siendo `flujo_caja = nómina × 0,18`, declarado como
`# SUPUESTO:` en `data/construir_empresas.py:65-71` y heredado por
`behavior/arquetipos.py:157-160`. Es el techo duro del veto. `engine/MODELO.md:111` reporta
que usar un mes produjo 96 vetos, usar tres meses produjo 0, y el empleo de la ronda 3 pasó
de 100% a 85,7%. Es una medición con fecha del modelo, no una relación normativa.

Los caminos de datos, en orden, son:

1. **GEIH inmediata.** `P6750` observa ganancia neta para 2.275 respuestas al bloque
   condicionado. Los 187 patrones tienen valor observado, declaran `P3069 >= 2` y presentan
   p25/p50/p75 de **2.000.000 / 3.000.000 / 5.000.000 COP mensuales**. Cuenta propia +
   patrones suman 2.273 personas y 33,84% del empleo ponderado. La frase de
   `data/README.md:110-115` debe precisarse: la GEIH sí observa ganancia de la unidad que la
   persona posee, pero no la firma que emplea al otro 66,16%. Los 187 patrones son una base
   delgada para imputar firmas empleadoras.
2. **EMICRON (DANE).** ⚠️ Los catálogos suministrados describen la Encuesta de
   Micronegocios, hasta nueve ocupados y muestreada desde la GEIH, con ventas/ingresos,
   costos y gastos, ganancia, RUT, cámara de comercio, contabilidad, protección social y
   CIIU Rev. 4. Debe verificarse el diccionario antes de integrar: catálogo
   [2024](https://microdatos.dane.gov.co/index.php/catalog/875) y
   [2023](https://microdatos.dane.gov.co/index.php/catalog/832). Ataca el segmento micro,
   cuya informalidad proxy es 0,6672 en `data/momentos.json`.
3. **Fuera del alcance actual.** Márgenes de firmas grandes (EAM/EAS y Supersociedades),
   entrada y salida de firmas (RUES/Confecámaras) y elasticidad sectorial de traslado a
   precios.
