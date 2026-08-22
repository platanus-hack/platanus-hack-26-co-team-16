# Review del PR #5 — Manuel (R2)

> **Qué es este archivo.** La revisión completa del
> [PR #5](https://github.com/platanus-hack/platanus-hack-26-co-team-16/pull/5) de Alejo
> (`rol/datos` → `main`), hecha el 2026-08-22. Existe porque el resumen no cabía en el
> handoff y porque la regla 4 de `AGENTS.md` dice que *"el reporte de un agente de código es
> un reclamo, no evidencia"*: acá queda separado **lo que verifiqué corriendo algo** de **lo
> que solo leí**.
>
> **Es un hallazgo con fecha, no una decisión.** Lo que se confirme se gradúa a un ADR o al
> registro de supuestos de `engine/MODELO.md`, o no pasó. Este archivo es mío (R2) y nadie
> más lo edita.

## Método

Dos pasadas independientes, a propósito:

1. **A mano.** Copié `data/` de `origin/rol/datos` a un directorio limpio y corrí
   `parametros_legales.py` y `construir_empresas.py` yo mismo antes de leer una sola línea
   de opinión ajena.
2. **`/code-review`** sobre el PR. La primera invocación **cayó sobre el target equivocado**
   (`main...rol/backend`, o sea mi propia rama); la relancé con la URL del PR.

Los hallazgos donde las dos pasadas coinciden están marcados **✅✅**.

## Estado del PR al momento de revisar

| | |
|---|---|
| Autor | Alejandro Davila (`alejandrod-24`), R1 |
| Rama | `rol/datos` → `main` |
| Al empezar | 22 archivos, +2436/−10, 10 commits |
| Al terminar | **26 archivos, 12 commits** (llegaron 4 `.codex/agents/*.toml`) |

**El PR se movió mientras se revisaba.** Un PR que cambia bajo revisión invalida la revisión.
Vale decirlo en el grupo, no como reproche sino porque a esta altura del reloj cuesta caro.

## Lo que verifiqué corriendo algo

**Los números del PR se reproducen exactos.** Corrí los dos scripts desde una copia limpia:
368.491 empresas, 3.235.639 trabajadores con empleador, 964.004 cuenta propia (22,9%), factor
1,384–1,583, sobrecosto micro 74,9% contra grande 40,3%. **Nada inventado en el reporte.**

### 1. Las dos tablas de headcount divergen, y el código jura que no ✅✅ · ALTO

`data/construir_empresas.py:46` dice literalmente:

> *"Idéntico al `EMPLEADOS_POR_CODIGO` de behavior/arquetipos.py a propósito: dos tablas
> distintas para el mismo código serían una divergencia silenciosa entre el motor y la capa
> conductual."*

No son idénticas:

| Código | Rango declarado | `data/construir_empresas.py` | `behavior/arquetipos.py` |
|---|---|---|---|
| 2 | 2-3 personas | `2.5` | **`3`** |
| 3 | 4-5 personas | `4.5` | **`5`** |
| resto | — | iguales | iguales |

Es exactamente la divergencia que el comentario dice estar previniendo, y **es la que carga el
peso del titular**: con el `3` de `behavior/`, la celda código 2 tiene 2 empleados, califica
para la exoneración del Art. 114-1, y el sobrecosto cae de **74,9% a 61,4%**.

Detalle aparte: **ninguna de las dos es "el punto medio del rango"** que ambos archivos dicen
ser (2-3 no promedia 3), aunque los dos lo afirman.

### 2. El titular del pitch descansa en un encuestado y en un redondeo ✅✅ · ALTO

Dos problemas encima del mismo número.

**Uno: `n_muestra = 1`.** El 74,9% sale de `emp-agro_mineria-t02`, **una sola persona** de la
GEIH expandida a 408 empresas. La segunda celda, `emp-construccion_utilities-t02`, da 72,5%
con 48 observaciones y aguanta cualquier pregunta del jurado.

**Dos: el umbral legal es discreto y se evalúa sobre un punto medio fraccionario.** El script
hace `empleados = max(1.0, personas - 1) = 1.5` para el código 2, y `1.5 >= 2` es falso, así
que la celda entera pierde el Art. 114-1 y paga los 13,5 puntos. **Nueve de las diez "celdas
sin exoneración" son ese redondeo**, no la norma. La décima (`agro_mineria-t07`) sí la pierde
por la razón legítima: el tope de 10 SMLMV.

Una celda código 2 en la realidad mezcla firmas de 1 y de 2 empleados. Asignarlas todas a la
rama no exonerada es una decisión de modelado que merece un `# SUPUESTO:`, no un efecto
colateral de un redondeo.

### 3. `n_empresas_expandidas` mezcla dos bases ✅✅ · ALTO

El numerador (`trabajadores_exp`) suma los factores de expansión de **todas las personas** de
la celda, dueños incluidos: `3.235.639 + 964.004 = 4.199.643`, la población completa. El
denominador (`empleados`) **excluye** al dueño. Dividir personas entre empleados-por-firma
sobrecuenta.

| | |
|---|---|
| Publicado en el PR y en `data/README.md` | **368.491** |
| Dividiendo por `n_personas` (consistente) | **254.307** |
| Diferencia | **+45%** |

`poblacion.parquet` **no permite resolverlo con datos**: la columna `tipo` es constante
`"trabajador"` y no hay posición ocupacional. Hay que elegir una convención y escribirla.

### 4. La indemnización ignora la rama ≥10 SMLMV que el propio JSON codifica ✅✅ · MEDIO

`construir_empresas.py:154` siempre lee `meses_de_salario_bajo_10_smlmv` (2,33 meses).
`emp-agro_mineria-t07` tiene mediana ponderada de **20.000.000 COP**, por encima de los
17.509.050 que son 10 SMLMV, donde el Art. 64 da 20 + 15×2 = 50 días = **1,67 meses**. Esa
celda queda sobrestimada **~40%**.

`costo_despido_meses()` ya sabe distinguir y recibe el salario como parámetro. Y el dato para
ramificar está en la línea de arriba (`salario_mediano < 10 * smlmv`, el test de exoneración).

### 5. División por cero latente · MEDIO

`poblacion.parquet` tiene **21 filas con `ingreso_mensual_cop == 0`**, repartidas en los
códigos 1, 2, 3, 5, 6 y 9 — no solo en cuenta propia. Si una regeneración futura deja una
celda chica con mediana ponderada 0, `costo_formal / nomina` en `:152` levanta
`ZeroDivisionError` y **el parquet no se escribe**. Hoy no pasa (la mediana mínima es 980.000)
y por eso nadie lo vería venir.

### 6. Los cuatro críticos: la garantía es prosa, no permiso ✅✅ · MEDIO

El PR pide al revisor confirmar que ninguno declara `Edit`. Es cierto, ninguno lo declara.
Pero **los cuatro declaran `Write` y `Bash`**, así que la garantía documentada (*"su única
escritura permitida es su propio informe"*) no la sostiene el grant de herramientas:

- Con `Write` se sobrescribe cualquier archivo, incluido un `contracts/*.json` congelado en H+4.
- Con `Bash` se hace `sed -i`.
- **`.claude/settings.json` tiene `Bash(make:*)` y `Bash(python:*)` en la allow-list**, así que
  la regla *"nunca ejecuta `make run` ni `behavior/demo.py`"* es un consejo: un auditor corre
  `make validate` sin pedirle permiso a nadie y quema el corte duro de $50 que el PR dice
  proteger.

Si el corte de presupuesto es no-negociable, vive en la **deny-list**, no en un párrafo del
prompt.

## Lo que verifiqué leyendo, sin correr nada

### 7. `contracts/README.md` manda a `engine/` a la tabla equivocada · MEDIO

La advertencia nueva (buena en su intención: `tamano_empresa` es un código ordinal, no un
headcount) le dice a `engine/costos.py` que use `EMPLEADOS_POR_CODIGO` de `behavior/` como
traducción de referencia, y la describe como *"punto medio de cada rango"*. Ninguna de las dos
cosas se sostiene: no es el punto medio, y **contradice la tabla que este mismo PR entrega en
`data/construir_empresas.py`**. Seguir esa nota hace que `engine/` calcule headcounts que no
cuadran con `empresas.parquet`.

**Consecuencia para mí:** no uso esa tabla hasta que exista una sola.

### 8. El auxilio de transporte entra incompleto · MEDIO

El docstring de `auxilio_transporte_cop()` dice que el auxilio no entra al IBC de seguridad
social **pero sí a la base de prima y cesantías**. `costo_formal` lo suma plano, sin ese
21,8% encima (prima 8,33 + cesantías 8,33 + intereses 1 + vacaciones 4,17). Son **~54.300 COP
por empleado al mes** en el salario mínimo, casi 3% del salario, subestimado justo en el tramo
bajo del que trata el modelo.

### 9. El Art. 114-1 quedó recortado sin marcarlo · BAJO/MEDIO

El docstring dice bien que el artículo exonera a *"las personas jurídicas **y** las personas
naturales que empleen dos o más trabajadores"*. El código emite `EXONERACION_MIN_TRABAJADORES
= 2` como criterio único, así que **una SAS de un empleado paga 13,5 puntos que no debe**. Con
la regla de "todo supuesto se marca", esto pide un `# SUPUESTO:`.

### 10. Una afirmación falsa dentro del cazador de afirmaciones falsas · BAJO

`docs/agents/peeky/README.md:14` dice que peeky *"es el único que no consulta nada externo: no
tiene `WebSearch` ni `WebFetch` a propósito"*. **`juez-hackathon` tampoco los tiene**
(`tools: Read, Grep, Glob, Bash, Write`). Las dos líneas viven en este mismo PR.

Aparte, y es una pregunta de diseño más que un bug: la vara declarada de `juez-hackathon` es
*"el mercado"* y no tiene con qué mirarlo.

### 11. Verificación del auxilio contra la norma · pendiente

El auxilio sube 24,5% (200.000 → 249.095) mientras el SMLMV sube 23,0%. Puede ser correcto
(no siempre van al mismo ritmo), pero **es la única cifra del archivo cuya fuente es un blog
de abogados y no el decreto**. Vale confirmarla antes del pitch.

## Donde no le creo al `/code-review`

El agente afirma que el parquet commiteado es **reproducible byte a byte**. En mi máquina no
lo es:

- Los **datos** son idénticos: `DataFrame.equals()` contra el commiteado devuelve `True`.
- Los **bytes** no: yo corro pandas 3.0.3 y el layout del parquet cambia.
- Dos corridas **mías** sí dan el mismo sha256, así que el determinismo del script se sostiene.

La causa es que **el repo no tiene `requirements.txt`, ni `pyproject.toml`, ni venv**. Dos
revisores honestos obtienen dos hashes distintos y ninguno miente.

Esto **ya está en mi handoff como pendiente de Juanda (R5)** y en la
[ADR 0009](../adr/0009-frontera-del-determinismo.md), que define el determinismo como *"mismo
seed + misma caché + mismas versiones"*. El PR #5 no lo empeora; solo lo vuelve visible otra
vez. **Si `make validate` va a hashear artefactos, el candado tiene que ser sobre los datos,
no sobre el archivo.**

## Lo que revisé y está limpio

- Las tasas contra fuente: pensión 12%, salud 8,5%, ARL clase I 0,522% y clase V 6,96%,
  prima y cesantías 8,33%, intereses 1%, vacaciones 4,17%, SMLMV +23,0%. **Todas correctas.**
- El factor 1,384 (exonerado, riesgo I) y 1,583 (no exonerado, riesgo V) cuadran sumando el
  desglose a mano.
- La negación de `data/.gitignore` re-incluye `empresas.parquet` correctamente por encima del
  `*.parquet` de la raíz.
- Los dos informes nuevos (`juez-tecnico` y `peeky`) **citan `archivo:línea` reales**:
  verifiqué 4 al azar (`behavior/arquetipos.py:175`, `contrato.py:135`, `higiene.py:128`,
  `cache.py:12`) y las cuatro resuelven a líneas que existen. Los informes son honestos en su
  forma.
- Ningún `contracts/*.json` se toca: el congelamiento de H+4 sigue intacto.

## Recomendación

**Bloquear el merge por dos cosas, no por diez:**

1. **Unificar la tabla de headcount en un solo lugar**, y decidir si el código 2 son 2 o 3
   personas. De ahí sale el titular del pitch.
2. **Corregir el conteo de empresas o el número publicado.** 368.491 contra 254.307.

Lo demás son arreglos de pocas líneas que pueden entrar en el mismo push. Y el bloque de los
cuatro críticos debería ir a su propio PR con las dos afirmaciones de seguridad corregidas:
mezclado con datos, un revisor con 2.436 líneas enfrente revisa bien la mitad que entiende.

**Lo que el PR hace bien y hay que decirlo:** reemplaza supuestos por norma citada con
artículo y URL, que es exactamente lo que pedía `engine/MODELO.md` S1. El hallazgo de que el
factor prestacional **no es un número con incertidumbre sino dos separados por una frontera
legal** es un hallazgo de modelado, no de dato, y mejora el proyecto.

## Qué me cambia a mí (R2)

- ✅ `empresas.parquet` trae `factor_prestacional` **resuelto por celda**: `costos.py` lo lee y
  no promedia nada. **Mata el supuesto S1.**
- ✅ `MARGEN_SOBRE_NOMINA` en un solo lugar con nombre: es el techo duro del veto y R5 lo puede
  barrer.
- 🔴 **Los 964.004 cuenta propia (22,9%) no tienen fila de empresa** y `engine/veto.py` no
  tiene rama para ellos. Es trabajo mío, no un defecto del PR: el código 1 no es una firma y
  está bien excluido.
- 🔴 **No uso `EMPLEADOS_POR_CODIGO`** hasta que haya una sola tabla.

## Nota de proceso: `AGENTS.md` promete una rama imposible

El flujo de trabajo dice que se puede trabajar *"en una rama de feature colgada de ella
(`rol/backend/veto`)"*. **Git no lo permite** mientras exista la rama `rol/backend`: una ref no
puede ser prefijo de otra.

```
fatal: cannot lock ref 'refs/heads/rol/backend/notas-review':
'refs/heads/rol/backend' exists; cannot create 'refs/heads/rol/backend/notas-review'
```

El ejemplo del contrato no funciona para ninguno de los cinco roles. Es de docs raíz, o sea de
Juanda; queda dicho acá y hay que avisarlo. La convención que sí funciona es un prefijo
distinto (`notas/review-pr5`, `feat/veto`).
