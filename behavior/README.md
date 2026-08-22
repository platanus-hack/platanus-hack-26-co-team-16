# `behavior/` — Capa conductual (LLM)

**Dueño: Nico (R3)** · rama `rol/conductual`

Descubre estrategias de adaptación que un economista no habría enumerado.
Propone; no aplica nada.

## Alineación con las ADR del motor

Las ADR 0005-0009 (PR #3, Manuel) son canon. Qué hace esta capa con cada una:

| ADR | Qué exige | Estado acá |
|---|---|---|
| **0005** · el reloj | La ronda 0 es la reacción ingenua —la proyección oficial, cumplimiento total— y solo 1-3 son mejor respuesta | ✅ La ronda 0 no llama al LLM. Parte de la informalidad **observada** que publica `data/momentos.json` (30,6%), no de un número de andamio. Ahorra 25% del presupuesto y hace que `brecha = ronda 3 − ronda 0` sea la resta que define `engine/MODELO.md` |
| **0006** · fiscalización | La capacidad es estado del mundo, no un campo de la política ni una perilla del usuario | ✅ Ya se cumplía: `capacidad_fiscalizacion` es parámetro de `correr()`, nunca entra al dict de política |
| **0007** · `p(E)` | `p(E) = 1 − exp(−C/max(E,1))`, con micro-fundamento Poisson | ✅ Adoptada. Reemplaza a la forma abreviada `p ≈ C/E`, que coincidía en el régimen real (3,12% vs 3,16% a 63,2% de informalidad) pero saturaba en 100% en el borde donde la exponencial da 63,2% |
| **0008** · asimetría | La firma propone vía LLM, el trabajador calcula por regla determinista | 🔶 Avalada. Falta que el motor exponga `realizacion` como campo hermano de `veto`: el rechazo del trabajador **no puede** volver por el canal del veto, o el reintento le entrega al agente una razón que no es una restricción suya y el dato A4 mezcla "no pudo pagarlo" con "no se lo aceptaron" |
| **0009** · determinismo | La caché es artefacto versionado con hash de manifiesto que la corrida imprime | ✅ `Cache.manifiesto()`. Cubre claves **y contenido**: editar una entrada a mano cambia el hash, así que no se puede "arreglar" un resultado tocando el caché sin que se note |

## Los 3 críticos del review del PR #4 — cerrados, con prueba

`python3 -m behavior.pruebas` los ejecuta como regresión ($0, sin API). Cada uno
reproduce el bug tal como lo reportaron @alejandrod-24 y @Manigreeen y verifica
que hoy no ocurre.

| # | Qué pasaba | Qué se hizo |
|---|---|---|
| **1** | Una `estrategia_propuesta` vacía —que el esquema JSON permite— mataba la corrida con **una sola llamada**, y como `proponer()` cacheaba antes de que nadie validara, la respuesta mala quedaba **grabada en disco**: la re-corrida sin API reventaba idéntico. Se disparaba justo en la re-corrida barata delante de un juez | Doble candado: `cliente.py` valida con `contrato.construir()` **antes** de escribir el caché, y `capa.py` mete `construir()`/`validar()` **dentro** del `try`. Una respuesta inválida ya no llega al disco ni tumba la corrida — es un intento perdido, como un veto |
| **2** | `ya_informal = not a.formal` era estático las 4 rondas. Una unidad que informalizó su planta en R1 leía *"tu planta: toda formal"* en R2, encima de su propio historial que decía *"informalizar"*; si respondía "mantener", la tasa **bajaba** por una razón espuria. Y los despedidos **resucitaban** en cuanto la ronda siguiente no despedía | Estado vivo por arquetipo entre rondas (dos diccionarios en `rondas.correr()`, nada de estado del mundo — eso es de `engine/`). `fraccion_fuera_de_regla()` se vuelve acumulativa y `empleo_relativo` se arrastra contra la línea base sin política, que es como lo define `engine/MODELO.md` |
| **3** | La regla fija comparaba el **sobrecosto** contra la sanción esperada, o sea un delta contra un nivel. El candado 4 salía de esa comparación | El costo formal completo. **Y el resultado cambió** — ver la sección del candado 4 abajo, que es lo más importante de este PR |

Y los menores: `FALLBACK = "cumplir"` (canon `IDEA.md` §5.3/§5.7 — no era
cosmético: para una unidad informal `absorber` puntúa 1.0 fuera de regla y
`cumplir` 0.0, así que las dos capas habrían reportado tasas distintas con las
mismas decisiones) · `tasa_informalidad_inicial` sin default de andamio, leída de
`momentos.json` · `fallos_tecnicos` contado también cuando el reintento funciona ·
caché escrito **antes** de registrar el gasto, para no re-pagar lo ya pagado ·
`muestrear()` renombrado a `_muestrear_local` (el canónico es de `engine/`) ·
`cargar_contrato()` borrado · `assert` de unicidad de ids en `desde_poblacion()`.

## El barrido con banda — el dato A2 NO se sostiene

> ⚠️ **Medido ANTES del fix del estado vivo entre rondas** (crítico #2 del review
> del PR #4). Con el bug, un arquetipo que informalizaba su planta volvía a
> contar como formal la ronda siguiente, así que **los niveles de esta tabla se
> van a mover**. No se re-mide en este PR: repetir el barrido cuesta ~$9 de un
> techo de $50 y la conclusión que importa —que las bandas se solapan— no depende
> del nivel sino del ancho. Se marca en vez de borrarse porque el hallazgo
> negativo sigue en pie; el número exacto queda pendiente.

Corrida del 2026-08-22: 7 políticas × 3 rondas × **5 paráfrasis** × 31 arquetipos
(top-K 0,80) = **3.235 llamadas, $8,68**. Log crudo en
[`barrido-2026-08-22.log`](barrido-2026-08-22.log). Reproducible con:

```bash
python3 -m behavior.demo --llm --real --cobertura 0.8 --parafrasis 5 \
        --puntos 7,10,13.6,18,23,26,30 --tope 12
```

| política | brecha (dato A1) | p10 | p90 | ancho | ¿solapa con el vecino? |
|---|---|---|---|---|---|
| 7,0% | +33,4 pp | 55,7% | 69,0% | 13,3 pp | — |
| 10,0% | +28,4 pp | 32,4% | 78,4% | 46,1 pp | **sí** (salto 5,0 vs banda 46,1) |
| 13,6% | +41,8 pp | 62,5% | 77,8% | 15,3 pp | **sí** (salto 13,4 vs banda 15,3) |
| 18,0% | +34,3 pp | 54,7% | 76,2% | 21,5 pp | **sí** (salto 7,4 vs banda 21,5) |
| 23,0% | +37,4 pp | 61,7% | 72,0% | 10,3 pp | **sí** (salto 3,0 vs banda 10,3) |
| 26,0% | +32,7 pp | 49,9% | 71,5% | 21,6 pp | **sí** (salto 4,6 vs banda 21,6) |
| 30,0% | +45,0 pp | 72,7% | 78,8% | 6,1 pp | no (salto 12,3 vs banda 6,1) |

**Conclusión: el dato A2 (el codo) no se puede afirmar y no va al pitch.** La serie
**no es monótona** y en **5 de 6** pares vecinos las bandas se solapan. La banda
mediana es de 15,3 pp y el rango completo entre las siete políticas es de
16,7 pp: la incertidumbre de una política es casi tan grande como toda la
variación entre políticas. No podemos distinguir el efecto del 7% del efecto del
26%, ni el del 23% del 13,6% — que es justamente el debate público.

Se mide con N=5 paráfrasis, que es la regla del plan §5 (la banda se construye
sobre paráfrasis del prompt, no sobre temperatura). Con N=1 el mismo barrido
parecía tener estructura; no la tenía.

**Lo que SÍ sobrevive, y es el hallazgo del proyecto:**

- **El dato A1 aguanta.** Las siete políticas dan una brecha de **+28 a +45 pp**
  sobre la proyección oficial. El signo, el mecanismo y el orden de magnitud son
  robustos aunque el nivel exacto no lo sea. La afirmación defendible es *"la
  brecha está entre 28 y 45 puntos y no depende de qué alza elijas"*.
- **La cascada aparece en los 7 puntos:** la probabilidad de sanción cae de 6,3%
  a 2,6–3,4% en todos. El mecanismo es consistente aunque el nivel sea ruidoso.

**Consecuencia para el motor:** el test *"el barrido es monótono donde debe
serlo"* de [`engine/MODELO.md`](../engine/MODELO.md) va a fallar, y no por un bug
— el fenómeno medido no es monótono. R2 necesita saberlo antes de escribir
`barrido.py`.

## El modo top-K — por qué existe

Con la grilla real (101 arquetipos) una corrida en frío son ~404 llamadas y el
barrido con banda se sale del presupuesto. La distribución de peso lo hace
evitable:

```
top 10 ->  46,8%      top 30 ->  79,5%       51 de los 101 arquetipos
top 20 ->  67,4%      top 40 ->  87,6%       pesan <0,5% cada uno
```

`particionar_por_peso(arquetipos, 0.80)` manda **31 arquetipos** al LLM (80,5% de
la población expandida) y los **70** restantes a las reglas fijas de
`ablacion.ClienteReglas`.

**Es un compromiso de costo, no de modelo**, y se reporta como tal: cada ronda
publica `fraccion_poblacion_llm`. El sesgo tiene dirección **conocida**: la regla
fija no descubre estrategias, así que la cola subestima la evasión y la cascada
con top-K es una **cota inferior** por este canal.

`fraccion_poblacion_llm` **no** va en `a_contrato()`: `contracts/ronda.json` está
congelado desde H+4 y agregarle un campo exige avisar en el grupo antes.

## Cómo verificarlo tú mismo

| Comando | Qué hace |
|---|---|
| `python3 -m behavior.higiene` | Escanea los prompts y falla si alguno nombra la política |
| `python3 -m behavior.pruebas` | Las regresiones de los 3 críticos del review — sin API, $0 |
| `python3 -m behavior.ablacion --barrido-factor` | La sensibilidad del candado 4 al supuesto S1 — $0 |
| `python3 -m behavior.demo` | Corrida completa con reglas fijas — sin API key, $0 |
| `python3 -m behavior.demo --real --cobertura 0.8` | Población real de la GEIH en modo top-K |
| `python3 -m behavior.cache` | Tamaño del caché y su **hash de manifiesto** (ADR 0009) |
| `python3 -m behavior.demo --barrido` | Barre 7 / 13,6 / 23 / 30% para buscar el codo |
| `python3 -m behavior.demo --llm` | La capa LLM real (necesita credenciales) |

## La regla de oro

**Al LLM jamás se le nombra la política.** Ni "salario mínimo", ni "decreto", ni
años. Solo la mecánica: *"tu costo laboral por empleado formal sube X%"*. Es el
control de contaminación de entrenamiento y sostiene la mitad del argumento de
validación. Un prompt que la viole invalida la corrida.

Eso no es una promesa, es un candado: `behavior/higiene.py` tiene la lista negra
y **todo prompt pasa por `verificar()` antes de salir hacia la API**, sin bandera
para desactivarlo. Si algo se filtra, la corrida revienta en vez de producir un
número contaminado.

Fuimos más lejos de lo que pide el plan: los prompts tampoco nombran el país, la
ciudad, la moneda ni el año. Los montos van en **unidades (u)** abstractas. Eso
hace que el test de re-skinning (candado 3b) sea casi gratis: ya no hay etiqueta
real que renombrar.

Los prompts son legibles en [`behavior/prompts/`](prompts/) — `sistema.md` es el
contexto del mundo, `arquetipo.md` la plantilla por grupo, y `parafrasis/` las 5
variantes con las que se construye la barra de error.

## Verificación V10 — AgentTorch (`docs/PLAN.md` §6)

**Veredicto: se adopta la idea, no la dependencia.** El muestreo por arquetipos
está implementado a mano en [`arquetipos.py`](arquetipos.py) (~50 líneas), como
el plan ya anticipaba en §4.1.

Qué se abrió: [`AgentTorch/AgentTorch`](https://github.com/AgentTorch/AgentTorch),
`agent_torch/core/llm/archetype.py` y `behavior.py`.

**Sí tiene lo que buscábamos.** `Archetype`, `LLMArchetype` y `Behavior.sample()`
hacen exactamente el patrón de D4: se prompta a arquetipos representativos y los
agentes individuales muestrean de la distribución resultante. Nuestra decisión
D4 no era original, y eso es bueno: hay prior art y lo citamos.

**Aun así no entra, por cuatro razones concretas:**

1. **Licencia — es el bloqueo duro.** AgentTorch es **AGPL-3.0**. Nuestro repo es
   MIT y tiene que serlo (repo público, entregable del hackathon). Importar
   código AGPL a un proyecto MIT es un conflicto de licencia, no una molestia de
   ingeniería. Esto solo ya cierra la discusión.
2. **Forma equivocada de la salida.** Su `Behavior.sample()` promedia salidas
   **float** entre arquetipos: está hecho para una variable conductual escalar
   (p. ej. "número de viajes"). Lo nuestro es una **estrategia categórica** con
   veto de factibilidad y reintento. No es el mismo objeto.
3. **Acoplamiento.** Arrastra PyTorch más su `PromptManager`, su
   `LoadPopulation` y su sistema de `registry`/`substep`. Para usar 50 líneas
   habría que adoptar su runtime completo.
4. **No trae lo que de verdad nos cuesta.** No tiene veto de factibilidad, ni
   caché por hash de prompt, ni tope de presupuesto. Esas tres son el trabajo
   real de esta carpeta y las escribimos igual.

**Lo que sí tomamos:** la idea y la cita. Va al README como prior art, junto al
paper de *Large Population Models*, y es la línea para el Q&A: *"leímos
AgentTorch, adoptamos su patrón de arquetipos y decidimos no importar su runtime
— la licencia es incompatible con MIT y su muestreo es escalar, no categórico"*.

## Arquitectura

```
prompts/         los prompts, visibles y auditables
higiene.py       la lista negra + el candado que revienta la corrida
arquetipos.py    definición de arquetipos + muestreo determinista (reemplaza AgentTorch)
contrato.py      contracts/decision.json: construir, validar, fallback
cliente.py       API: ruteo de modelo, prompt caching, caché en disco, presupuesto
cache.py         caché en disco por hash del prompt
presupuesto.py   tope duro por corrida
capa.py          propuesta -> veto -> reintento (máx 3) -> fallback 'cumplir'
rondas.py        el bucle: ronda 0 ingenua + 3 de mejor respuesta (ADR 0005)
ablacion.py      la misma corrida con reglas fijas (candado 4 de validación)
demo.py          corrida punta a punta sin motor y sin API key
pruebas.py       las regresiones de los 3 críticos del review del PR #4
```

El ciclo, que es la tesis del proyecto:

```
propuesta del LLM  ->  veto del motor  ->  ¿factible?
                                           sí -> entra al agregado de la ronda
                                           no -> reintento CON LA RAZÓN encima
                                                 (máximo 3, luego 'cumplir')
```

`ablacion.py` es un reemplazo directo de `cliente.py`: misma firma de
`proponer()`, así que la corrida con LLM y la corrida con reglas fijas comparten
`capa.py` y `rondas.py` sin cambiar una línea. La diferencia entre las dos ES el
candado 4.

## Costo — medido, no estimado

48 arquetipos × 4 rondas = **193 llamadas** por corrida. Medido contra la API
real el 22-08-2026 con `claude-haiku-4-5`:

| Corrida | Llamadas | Costo | Tiempo |
|---|---|---|---|
| En frío, secuencial | 193 | **$0,5080** | 10 min 12 s |
| En frío, `--paralelismo 8` | 193 | $0,5080 | **~1,5 min** |
| Repetición con caché caliente | 0 | **$0,0000** | **0,5 s** |

Promedio real por llamada: 1.622 tokens de entrada / 192 de salida ≈ $0,0026.
(Mi estimado previo de 900 tokens de entrada se quedó corto en un 80%.)

Tope duro por corrida: **$3,00** (`--tope` para subirlo). Barrer 7 políticas ×
4 rondas costó $3,04 y el corte se disparó como debía.

**El caché en disco es lo que hace usable el demo en vivo:** la segunda corrida
es 1.200× más rápida y gratis. También es lo que sostiene el determinismo — con
el caché poblado, la corrida relee exactamente las mismas respuestas. Verificado:
dos corridas seguidas dan contratos byte a byte idénticos, en paralelo y en serie.

**Prompt caching de la API: confirmado que NO aplica.** Medido
`cache_read_input_tokens = 0` y `cache_creation_input_tokens = 0` en las 193
llamadas. El mínimo cacheable de Haiku 4.5 son 4.096 tokens y nuestro prefijo
estable es más corto. Lo sospechábamos; ahora está medido. La palanca real de
costo es el caché en disco.

**Tasa de fallo del modelo: ~0,1%.** En 1.160 llamadas, una respuesta no parseó
como JSON. Antes eso tumbaba la corrida entera; ahora cuenta como intento
perdido y se reintenta (`RespuestaInvalida` en `cliente.py`).

## Hallazgos que afectan a otros roles

### 1. La cascada existe con LLM, y se ve

> ⚠️ **Medida ANTES del fix del estado vivo entre rondas.** El "se devuelve" de la
> ronda 3 (93,8% → 75,6%) es plausiblemente el bug y no el fenómeno: con el
> estado muerto, una unidad que ya se había informalizado volvía a contar como
> formal si respondía "mantener". Ver la corrida nueva más abajo.

Corrida real, aumento 23%, 48 arquetipos:

| ronda | informalidad | prob. de sanción |
|---|---|---|
| 0 | 63,2% | 4,8% |
| 1 | 70,1% | 3,2% |
| 2 | 93,8% | 2,9% |
| 3 | 75,6% | 2,1% |

El mecanismo se comporta como dice la tesis: más agentes fuera de regla → la
capacidad fija se reparte entre más → la probabilidad de sanción cae → más
evaden. **No converge**, y así hay que reportarlo (decisión D5): la ronda 2 se
pasa y la 3 se devuelve. Eso es dinámica de mejor respuesta, no equilibrio.

### 2. ⚠️ El codo (dato A2) NO se puede afirmar todavía

*(También pre-fix. Superado por el barrido con N=5 de arriba, que es el que manda.)*

Barrido real de 7 niveles de política (1.160 llamadas, $3,04):

| aumento | 0% | 7% | 13,6% | 18% | 23% | 30% | 40% |
|---|---|---|---|---|---|---|---|
| informalidad final | 0,0% | 58,3% | 73,6% | 84,3% | 75,6% | 91,0% | 80,0% |

Dos lecturas, y la segunda es la que importa:

- **Bueno:** con aumento 0% la informalidad se queda en 0%. El mecanismo no
  dispara solo; necesita el choque. Es una buena señal para el candado 1.
- **Malo:** la curva **no es monótona** y el salto de 0% a 7% (0 → 58 pp) es
  desproporcionado. Peor: midiendo la banda de 5 paráfrasis en la ronda 0 con
  aumento 18%, el ancho fue de **20 puntos** (59,6% – 79,6%) — **más ancho que
  las diferencias entre políticas vecinas** (75,6% vs 84,3% = 8,7 pp).

**Conclusión: con 1 paráfrasis, lo que parece un codo es ruido.** Cualquier
afirmación sobre el umbral necesita N≥5 paráfrasis por punto del barrido, y hoy
no la tenemos. Esto es exactamente para lo que existe la regla de "todo número
sale con banda" del plan §5. **No lo llevemos al pitch como codo hasta medirlo.**

### 3. El LLM sí inventa estrategias fuera del menú — y eso rompe la agregación

En 193 llamadas propuso cinco nombres distintos para la misma conducta:
`mantener_informal` (41), `mantener_informalidad` (14), `mantener_status_quo` (4),
`mantener_operacion_informal` (3), `mantener_informalidad_total` (2). Más
`formalizarse_mantener_escala`, que no estaba en el menú.

Es la evidencia de que el espacio abierto funciona, y a la vez fragmentaba el
dato A4 en sinónimos. La solución **no** fue cerrar el menú con un enum — eso
mata lo que aporta el LLM. Se guardan las dos: `estrategia_propuesta` (cruda,
como la inventó) y `familia` (canónica, para agregar). Dani: agrega por
`familia`; el nombre crudo sirve para el feed y para mostrar que el modelo
inventa.

### 4. ⚠️ El candado 4 no discrimina — y el hallazgo es ese, no un número

**Esto reemplaza al *"con reglas fijas no hay cascada"* que decía este README
antes.** Aquel número salía de una ablación mal especificada, y corregirla no lo
volteó: lo dejó **en el filo**.

**Qué estaba mal.** La regla fija comparaba el **sobrecosto** del aumento
(`0,23 × ingreso`) contra la sanción esperada. Eso es comparar un delta contra un
nivel: para una unidad informal, formalizarse cuesta el costo formal **completo**,
no solo lo que el aumento agrega. El umbral quedaba en `p > 1,92%`, así que
cualquier probabilidad de fiscalización realista formalizaba a **todas** las
unidades informales en la ronda 1 → informalidad 0% → `p(E)` salta a 100% → el
sistema se clava ahí para siempre. El 0% no era un resultado, era un artefacto.

**Cómo quedó** (`behavior/ablacion.py`, con `# SUPUESTO:` en el punto donde se toma):

```
costo de formalizarse   = ingreso × factor_prestacional × (1 + aumento)
costo de seguir informal = ingreso + p × multa
```

**Y acá está el problema.** Con el factor prestacional en 1,40 —el extremo bajo
del supuesto **S1** de [`engine/MODELO.md`](../engine/MODELO.md), declarado
literalmente como *"≈1,4-1,5, sin cifra exacta verificada"*— la ablación
**todavía** formaliza a todos. Pero por muy poco:

| | valor |
|---|---|
| Punto de indiferencia de la regla fija, `p* = (F(1+a) − 1)/12` | **6,02%** |
| `p(E)` en la ronda 0 con la informalidad observada (30,57%) | **6,33%** |
| **Margen** | **0,31 pp** |

Y el barrido sobre el rango que el propio modelo declaró incierto
(`python3 -m behavior.ablacion --barrido-factor`, cuesta **$0**):

| factor prestacional | informalidad final | p. sanción | conclusión |
|---|---|---|---|
| 1,4000 | 0,0% | 100,0% | sin cascada |
| 1,4250 | 0,0% | 100,0% | sin cascada |
| 1,4300 | 0,0% | 100,0% | sin cascada |
| **1,4309** | — | — | **← aquí se voltea el candado 4** |
| 1,4375 | 100,0% | 2,0% | **cascada con reglas fijas** |
| 1,4500 | 100,0% | 2,0% | **cascada con reglas fijas** |
| 1,5000 | 100,0% | 2,0% | **cascada con reglas fijas** |

El punto de quiebre medido por bisección es **F = 1,4309**, idéntico al analítico
`F* = (1 + 12·p)/(1 + a)`. Cae en el **31% inferior** del rango declarado de S1.

**Conclusión, y es la que va al pitch:** con los parámetros actuales el candado 4
**no discrimina**. No decimos "con reglas fijas no hay cascada" ni decimos "sí la
hay": decimos que el signo del candado 4 **depende de un supuesto que el proyecto
ya había declarado incierto antes de medirlo**, y publicamos el punto exacto
donde se voltea. La afirmación defendible es:

> *"La ablación separa al LLM de la regla fija solo si el factor prestacional
> está por debajo de 1,43. Ese parámetro no lo tenemos verificado y lo dijimos
> antes de medir. Aquí está el barrido completo."*

**Tres cosas que hay que decir junto con esto:**

1. **Los puntos #3 y #11 del review casi se cancelan.** Corregir la tasa inicial
   de 0,42 al 30,57% observado sube `p(E)` de 4,65% a 6,33%, y ese salto es
   justo lo que cruza el umbral. Aplicados por separado dan resultados opuestos;
   juntos dejan el resultado en el filo. Ninguno de los dos reviews lo notó, y
   es la razón por la que el número no se cayó limpiamente.
2. **El resultado es idéntico con población real y con andamio** (verificado: 101
   arquetipos y 48 dan la misma tabla). No es coincidencia — el umbral de una
   regla fija escala con el ingreso **en los dos lados**, así que es el mismo
   para todos los arquetipos y cruzan todos o ninguno. Esa homogeneidad es
   precisamente lo que el LLM no tiene, y sigue siendo el argumento estructural
   a favor de la capa conductual; lo que ya no se sostiene es el *número* que lo
   respaldaba.
3. **`p(E) → 1.0` cuando E → 0 crea un estado absorbente.** Es la
   [ADR 0007](../docs/adr/0007-forma-funcional-prob-sancion.md) y es de R2, así
   que no se toca desde acá; pero en la ablación **sí** muerde: en cuanto la
   informalidad llega a 0, la probabilidad de sanción salta a 100% y nadie vuelve
   a evadir nunca. El "0% para siempre" es en parte esa esquina de la fórmula, no
   solo la conducta. **@Manigreeen** debería saberlo antes de cablear
   `fiscalizacion.py`.

**La especificación se eligió por fundamento, antes de correr, y hay que decir en
qué dirección sesga.** Se supone que el salario bruto no cambia al formalizarse
—solo se agregan las cargas— porque es la única alternativa que no exige inventar
una brecha salarial informal/formal (el `0,85×` del andamio no es un dato). Esa
elección **subestima** el costo de formalizarse, o sea que sesga a favor de que
la ablación formalice, o sea **a favor de nuestro propio candado 4**. Con la
especificación alternativa (formalizarse obliga a pagar el salario formal
comparable) el costo sube a `2,03×` y la ablación produce cascada en todo el
rango. Está dicho acá para que nadie tenga que descubrirlo leyendo el código.

### 5. Notas sueltas para el equipo

- **`contracts/decision.json` ya está congelado en `main`** y `contrato.py`
  coincide con él campo a campo. La función `cargar_contrato()`, que existía para
  el caso "todavía no existe", se borró.
- **Los prompts no usan pesos.** Adentro todo es "unidades (u)"; la conversión
  es del motor.
- **`informalizar_parcial` cuenta parcial.** Mueve solo la fracción de la planta
  que informaliza, no la unidad entera. Contarlo entero era lo que saturaba la
  tasa en 100% desde la ronda 0.

## Lo que falta

- [x] ~~Primera llamada real a la API~~ — hecho: 1.880 respuestas en caché.
- [ ] **Barrido con N≥5 paráfrasis por punto** para poder afirmar (o descartar)
      el codo. Es el número que hoy no tenemos y que el pitch quiere. ~$18 a
      precio de lista; se puede acotar a 3 puntos por ~$8.
- [ ] Congelar `contracts/decision.json` con Manuel (H+4) y enchufar el veto real.
- [ ] Reemplazar `arquetipos_falsos()` por `desde_poblacion()` cuando Alejo
      entregue `data/poblacion.parquet` (H+8–14). El código ya está escrito.
- [ ] Test de pico y placa (§5.5), solo si el checkpoint C4 cerró.

## Qué NO va aquí

- Aplicar decisiones al estado del mundo (eso lo hace `engine/`).
- Nada de `web/`, `data/` ni `engine/`.
