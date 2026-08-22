# Defectos del modelo — inventario medido

> **Dueño: Juanda (R5 · integración/validación).** Fecha de corte: **2026-08-22 15:50** (H+15).
> Todo lo de acá está **medido o verificado en disco**, no inferido. Cada afirmación
> trae su evidencia: un `archivo:línea`, una cifra de corrida, o un comando.
> Un defecto listado acá **no es una decisión**: es un hallazgo con fecha. Lo que se
> confirme y cambie el modelo se gradúa a un ADR o al registro de `engine/MODELO.md`.

## Cómo se midió

Barrido completo con la capa LLM real, cerrado a las 15:50:

```bash
python3 scripts/barrido_politicas.py --llm --repeticiones 3 --desde 5 --hasta 20 --paso 2 --tope 12
```

9 políticas (5 a 20% en pasos de 2) × 3 repeticiones = **27 trayectorias completas e
independientes**, cada una con una paráfrasis distinta del prompt. 101 arquetipos de la
GEIH Bogotá, veto real de `engine/`, top-K 0,80. **$6,63 · 18,3 min.**
Datos crudos: `scripts/salidas/barrido-llm-20260822-1550.json`.

---

## Veredicto en un párrafo

**La máquina funciona; el modelo todavía no.** El pipeline es determinista, la cascada de
fiscalización aparece en 9 de 9 políticas y el efecto sobre el empleo es limpio
(correlación −0,909). Pero la señal que da nombre al proyecto —la informalidad— está
**ahogada en ruido de reformulación** (ruido/señal = 0,71) y además **apunta en la
dirección contraria** a la literatura que el propio `VALIDATION.md` usa como objetivo de
calibración. De las 8 estrategias que el agente puede elegir, **solo 3 mueven un número**.

---

## 1 · Defectos del modelo: lo que no puede representar

### 1.1 · Cinco de las ocho estrategias no mueven ningún número 🔴

`behavior/contrato.py:fraccion_fuera_de_regla` lo declara explícitamente:

> *"ninguna otra estrategia cambia el estatus de regla de la planta. `absorber`,
> `despedir`, `bajar_horas`, `renegociar`, `subir_precios` y lo que el modelo invente
> mueven márgenes, headcount o precios, no el registro laboral."*

Solo `cumplir` e `informalizar` mueven la informalidad, y solo `despedir` mueve el empleo
(vía `empleados_a_despedir`, `behavior/rondas.py:333`). El resto se registra como etiqueta
y se descarta como número.

Reparto medido en el barrido completo:

| estrategia | % población | efecto numérico |
|---|---|---|
| `absorber` | 47,4% | ninguno — legítimo, es "no cambio" |
| `cumplir` | 23,8% | informalidad → 0 |
| `informalizar` | 22,8% | informalidad + |
| `despedir` | 4,7% | empleo − |
| **`subir_precios`** | **1,4%** | **ninguno — se descarta** |

### 1.2 · No hay canal de inflación, y no por decisión de diseño 🔴

`subir_precios` es el único canal por el que un alza salarial se traslada a precios, los
agentes **lo eligen**, y el agregado lo bota. `VALIDATION.md:70` declara que la inflación
es "exógena observada", pero eso describe una decisión de alcance — lo que pasa en el
código es distinto: **la decisión se toma y se pierde.**

Sin cablear esto, la pregunta *"¿cuánta inflación genera este alza?"* no tiene respuesta
posible, ni siquiera aproximada.

### 1.3 · La tasa de desempleo no es computable 🟠

`data/momentos.json` contiene **solo ocupados**: `ocupados_expandidos = 4.199.644`. No hay
fuerza laboral, no hay desocupados, no hay inactivos.

Lo único que el modelo produce es `empleo_relativo`: empleo contra la línea base sin
política. Se puede decir *"se pierde 8,3% del empleo base"*; **no** se puede decir *"la
tasa de desempleo sube a X%"*. Cualquier lámina del pitch que diga "desempleo" está
sobrevendiendo el dato.

### 1.4 · No existe productividad, ni demanda, ni capital 🟠

Conteo en todo el código (`engine/`, `behavior/`, `data/*.py`):

| concepto | menciones |
|---|---|
| productividad | 2 — una en un JSON de ejemplo, otra como texto ambiental del prompt |
| rotación, demanda, elasticidad, capital, automatización, salario de eficiencia | **0** |

Consecuencia directa: el canal *"sube el mínimo → sube la productividad → baja el
desempleo"* **no puede emerger**, porque no está cableado. Si un resultado se pareciera a
eso, sería coincidencia, no mecanismo. Lo mismo para sustitución capital-trabajo y para
cualquier efecto de demanda.

### 1.5 · El costo de despido es restricción, no decisión 🟡

`costo_despido` existe por arquetipo y `engine/veto.py` **bloquea** despedir cuando no hay
caja para la indemnización. Pero el agente **nunca compara** "despedir vs. mantener" por
costo: propone, y el motor veta. El mecanismo real —*"me sale más caro indemnizar que
seguir pagando, así que no despido"*— existe como muro, no como cálculo.

### 1.6 · La simulación no tiene punto de corte definido 🟠

7 de 9 políticas **se devuelven** en la ronda 3: la informalidad sube hasta la ronda 2 y
baja en la 3.

| alza | r0 | r1 | r2 | r3 |
|---|---|---|---|---|
| 13% | 30,6% | 60,2% | 66,6% | **53,4%** |
| 17% | 30,6% | 57,4% | 74,7% | **54,2%** |
| 20% | 30,6% | 51,0% | 85,7% | **84,4%** |

No es un bug —`cumplir` devuelve la planta entera a regla, y está declarado (decisión D5:
mejor respuesta, no equilibrio)—. Pero significa que **el número final depende de dónde
cortemos**, y hoy el corte en la ronda 3 no tiene justificación medida. Cortar en la
ronda 2 daría un resultado sistemáticamente peor.

---

## 2 · Defectos de medición: el ruido se come la señal

### 2.1 · Reformular el prompt mueve casi tanto como cambiar la política 🔴

**El defecto más grave del inventario.**

| | |
|---|---|
| Rango entre las medianas de las 9 políticas | **31,9 pp** |
| Dispersión promedio *dentro de una misma política* | **22,5 pp** |
| **ruido / señal** | **0,71** |

Las tres repeticiones de una misma política difieren solo en **cómo se formula la
pregunta**, no en qué se pregunta. Caso peor, política del 9%:

| repetición | paráfrasis | informalidad final |
|---|---|---|
| r1 | p1 | 60,9% |
| r2 | p2 | 56,4% |
| r3 | p3 | **85,2%** |

**28,8 pp** de diferencia. Con esta dispersión, **ningún número del barrido es defendible
punto por punto**, y ninguna no-monotonía observada se puede atribuir a un mecanismo:
es indistinguible del ruido.

### 2.2 · La informalidad apunta al revés 🔴

Correlación alza → informalidad: **−0,311**. El modelo dice, débilmente, que subir más el
mínimo produce *menos* informalidad.

Eso contradice el objetivo de calibración que el propio `VALIDATION.md:30` cita: Banco de
la República [WP 1104](https://ideas.repec.org/p/bdr/borrec/1104.html), +1 pp en el ratio
del mínimo ≈ **+0,21 pp** de probabilidad de empleo informal — signo **positivo**.

**Es la señal central del proyecto y es la que peor está.**

### 2.3 · La banda subestima la incertidumbre 🟡

`behavior/rondas.py:_banda` lo declara: las N paráfrasis *"parten todas del MISMO estado
previo, no de N trayectorias separadas"*. La banda mide dispersión de la decisión de
**esa** ronda, no de la historia completa.

Medido: la banda intra-corrida da 0,0 pp con `n_parafrasis=1`, mientras la dispersión
entre trayectorias independientes de la misma política da **22,5 pp**. El arnés de
`scripts/barrido_politicas.py` corre trayectorias separadas justamente por esto.

---

## 3 · Huecos de integración: piezas que no se hablan

### 3.1 · `demo.py` no usa el veto real 🔴

`behavior/demo.py:179` sigue pasando `veto_doble_prueba` — el doble de prueba que Nico
escribió cuando `engine/` no existía. Manuel dejó `veto_del_motor(estado)` hecho
**explícitamente para enchufarse** (`engine/veto.py`, docstring: *"Es lo que se le pasa al
parámetro `veto=` en lugar de los dobles de prueba"*).

Los PR #6 y #7 se mergearon con 5 minutos de diferencia y **nadie corrió el uno contra el
otro**. Toda corrida hecha con `demo.py` hasta hoy usó el doble de prueba.

### 3.2 · `behavior/` no importa `engine/` en ninguna parte 🔴

```bash
grep -rn "from engine\|import engine" behavior/    # -> vacío
```

Consecuencia: **`engine/seed.py` no se usa.** El `seed` de la capa conductual sigue siendo
decorativo, tal como Manuel lo describió antes de escribirlo. La reproducibilidad de hoy
viene de la caché, no de la semilla.

### 3.3 · El factor prestacional se promedia, y el dato dice que no se promedie 🟠

`behavior/ablacion.py:39` toma **un solo** `factor_prestacional` para toda la población.
`data/parametros_legales.json` dice literalmente:

> *"El rango NO es incertidumbre: es estructura. El extremo bajo es un empleador exonerado
> en un sector de riesgo I; el alto, un empleador de un solo trabajador en riesgo V. El
> motor debe asignar el factor que corresponde a cada firma, no promediar."*

Rango real calculado por Alejo: **1,3835 – 1,5829** según sector × exoneración del 114-1.
El punto donde se voltea el candado 4, medido por Nico, es **F\* = 1,4309** — **cae dentro
del rango**. 8 de 20 combinaciones quedan por debajo y 12 por encima, y **los 10 casos no
exonerados están todos por encima**. Como el no exonerado es el empleador de un solo
trabajador, y ahí vive el **66,7%** de la informalidad de Bogotá (`momentos.json`), el
signo del candado 4 depende de un parámetro que hoy se promedia.

### 3.4 · Dos particiones incompatibles de la misma población 🟠

`data/poblacion.parquet` trae una columna `arquetipo` con **67** valores distintos (los de
Alejo). `behavior/arquetipos.desde_poblacion()` **ignora esa columna** y re-deriva su
propio esquema: **101** arquetipos.

El peso total coincide exacto (4.199.644 en ambos), así que **no se pierde población** —
son dos particiones distintas de la misma gente. Pero `contracts/agente.json` declara un
campo `arquetipo` que nadie consume, y cualquier comparación contra las tasas por sector
de `momentos.json` (calculadas sobre los 67) cruza dos agrupaciones. **Eso muerde justo en
el candado 1.**

### 3.5 · Divergencia latente en `p(E)` entre el motor y la capa 🟡

Las dos implementan la misma ADR 0007 y **coinciden al bit en todo el régimen del
proyecto** (divergencia máxima medida en el barrido: 4·10⁻¹⁷).

Pero difieren en el borde: `behavior/rondas.py:139` corta con `if peso_fuera_de_regla <= 0:
return 1.0`, y `engine/fiscalizacion.py` aplica `max(E, 1)` argumentando contra ese 1.0
(*"el fondo nunca está vacío: contiene, como mínimo, a quien hace la pregunta"*).

Medido con E = 0, variando la capacidad absoluta:

| C (inspecciones) | capa | motor | diferencia |
|---|---|---|---|
| 1 | 100% | 63,2% | **36,8 pp** |
| 5 | 100% | 99,3% | 0,7 pp |
| ≥ 36 | 100% | 100% | 0 |

Hoy no muerde porque C ≈ 84.000. **Muerde en cuanto la capacidad sea una perilla de la
interfaz**, que es justo lo que la demo quiere ofrecer.

### 3.6 · La caché no está versionada 🟠

```bash
git ls-files | grep "\.cache/"    # -> 0 archivos
```

El [ADR 0009](docs/adr/0009-frontera-del-determinismo.md) obliga a versionarla: sin eso,
**el nivel 2 (corrida completa reproducible) no existe para nadie fuera del equipo**. Un
jurado que clone sin `ANTHROPIC_API_KEY` recibe `SinCredenciales` y no puede correr nada
con LLM.

Agravante: `.gitignore:23` ignora `behavior/cache/`, ruta que **no existe** — la caché real
vive en `behavior/.cache` (`cache.py:30`). La línea es inerte, y quien intente versionar la
caché va a editar la línea equivocada.

### 3.7 · El corte de presupuesto no es atómico 🟡

`behavior/cliente.py:135` llama a `comprobar()` bajo lock, **suelta el lock**, llama a la
API, y `registrar()` (línea 180) detecta el exceso *después* de que el proveedor ya cobró.
Con `paralelismo=8` pueden pasar 8 llamadas juntas por `comprobar()`. El tope es un
detector, no un freno.

---

## 4 · El repo contra sí mismo

### 4.1 · `README.md:41` cita una función que no existe 🟠

El README afirma **en presente** que el control de contaminación *"vive en
`Politica.como_mecanica()`"*.

```bash
grep -rn "def como_mecanica" engine/ behavior/    # -> no existe
```

Estaba planeada en `engine/mundo.py`, uno de los 7 archivos que Manuel declaró fuera de
alcance. La guardia real es `behavior/higiene.py` —que sí es fail-closed en cada
llamada— y **el README no la nombra**. Defecto mío, y viola la regla dura de R5: cada
afirmación del README debe ser verificable en el repo.

### 4.2 · `VALIDATION.md` se contradice con `momentos.json` 🟠

`VALIDATION.md:32` pone la informalidad de referencia en **~55–60%** (definición DANE/OIT,
nacional). `data/momentos.json` mide **30,57%** para Bogotá con proxy de cotización a
pensión (`construir_poblacion.py:110`).

No es que uno esté mal: son definiciones y universos distintos. Pero **el documento no lo
dice**, así que el candado 1 arranca comparando contra un objetivo que está al doble.
Defecto mío.

### 4.3 · El "informe de honestidad" da tres números distintos 🟡

| fuente | comando | resultado |
|---|---|---|
| `Makefile:82` | `grep -rn "SUPUESTO:" engine behavior data api web scripts tests` | **54** |
| `VALIDATION.md:80` | `grep -rn "SUPUESTO:" .` | **94** |

El documento publica un comando que da un número distinto del que imprime el `Makefile`.
Hay que fijar **uno**. Defecto mío.

### 4.4 · El contrato congelado emite un campo que no declara 🟡

`contracts/ronda.json` declara `banda: {p10, p90}`. El código emite un tercer campo:
`banda.degenerada` (`behavior/rondas.py:251`). El contrato está congelado desde H+4 y esto
entró después.

### 4.5 · Faltan los 4 campos de la página de votación 🟠

`platanus-hack-project.jsonc` tiene **4 `<FILL THIS>`** (nombre, one-liner, descripción,
deploy-url) y `project-description.md` sigue siendo la plantilla literal. Sin eso la
tarjeta de votación sale vacía. Defecto mío.

### 4.6 · No hay `requirements.txt` en `main` 🟠

Ninguna rama lo tiene. "Reproducible en máquina limpia" —requisito de entrega y nivel 3 del
ADR 0009— es **falso por construcción** hoy. Hay uno escrito y verificado en venv limpio,
sin commitear.

### 4.7 · Candado 3(b) — re-skinning — no tiene código 🟠

```bash
grep -rln "reskin" behavior/ engine/    # -> nada
```

`VALIDATION.md:47` lo promete. La higiene actual (`behavior/higiene.py`) filtra **términos**,
no **magnitudes**: los montos viajan en COP reales y la moda del parquet es 1.750.000, que
es exactamente el SMLMV 2026 (1.750.905). Un modelo puede reconocer el escenario por los
números aunque nunca vea el nombre.

---

## 5 · Lo que NO está mal

Para que la lista sea creíble hay que decir también qué aguanta:

- **La cascada existe y es robusta.** 9 de 9 políticas: p(sanción) cae de 6,33% a
  2,3–3,5%. Es el mecanismo que da nombre al proyecto y funciona.
- **El pipeline es determinista.** Repetir exacto la misma corrida (política, paráfrasis,
  semilla) da resultado **idéntico**. No hay estocasticidad escondida.
- **El efecto sobre el empleo es limpio.** Correlación −0,909 con dispersión de ±0,1 a
  1,8 pp. Hay un umbral visible: hasta el 11% no pasa nada, del 13% en adelante cae.
- **La población es real y trazable.** 6.692 personas de la GEIH, 4.199.644 expandidos, con
  sha256 y script de descarga reproducible.
- **Los parámetros legales tienen fuente por artículo del CST.** El trabajo de `data/` es
  el más sólido del repo.
- **La higiene es fail-closed de verdad**, en cada llamada, sin bandera para desactivarla.
- **`engine/` trae 44 tests** y sus tres archivos están bien argumentados.

---

## 6 · Prioridad

| # | Defecto | Sev | Dueño | Por qué primero |
|---|---|---|---|---|
| 1 | Ruido/señal 0,71 (§2.1) | 🔴 | R3 + R5 | Sin esto **ningún** número es defendible |
| 2 | Informalidad con signo invertido (§2.2) | 🔴 | R3 + R2 | Es la señal central del proyecto |
| 3 | `demo.py` no usa el veto real (§3.1) | 🔴 | R3 | Una línea. Invalida todo lo corrido antes |
| 4 | `subir_precios` inerte (§1.1, §1.2) | 🔴 | R3 | Es el canal de inflación y ya lo eligen |
| 5 | Caché sin versionar (§3.6) | 🟠 | R3 + R5 | Sin esto el jurado no puede correr nada |
| 6 | `requirements.txt` (§4.6) | 🟠 | R5 | Escrito y verificado, falta commitear |
| 7 | Factor prestacional promediado (§3.3) | 🟠 | R3 + R1 | Decide el signo del candado 4 |
| 8 | 67 vs 101 arquetipos (§3.4) | 🟠 | R1 + R3 | Muerde en el candado 1 |
| 9 | Campos de votación vacíos (§4.5) | 🟠 | R5 | Bloqueante de entrega |
| 10 | README y VALIDATION contradictorios (§4.1, §4.2, §4.3) | 🟠 | R5 | Regla dura de R5 incumplida |

**Lo que NO se va a arreglar y hay que declarar**: productividad, demanda, capital y tasa
de desempleo (§1.3, §1.4) son piezas nuevas, no campos apagados. Entran en
`VALIDATION.md` §"Dónde NO hay que creerle", no en el backlog.
