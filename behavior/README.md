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
| `python3 -m behavior.demo` | Corrida completa con reglas fijas — sin API key, $0 |
| `python3 -m behavior.demo --real --cobertura 0.8` | Población real de la GEIH en modo top-K |
| `python3 -m behavior.cache` | Tamaño del caché y su **hash de manifiesto** (ADR 0009) |
| `python3 -m behavior.demo --barrido` | Barre 7 / 13,6 / 23 / 30% para buscar el codo |
| `python3 -m behavior.demo --llm` | La capa LLM real (necesita credenciales) |
| `python3 -m behavior.cache` | Estado del caché en disco |

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
capa.py          propuesta -> veto -> reintento (máx 3) -> fallback 'absorber'
rondas.py        el bucle: ronda 0 ingenua + 3 de mejor respuesta (ADR 0005)
ablacion.py      la misma corrida con reglas fijas (candado 4 de validación)
demo.py          corrida punta a punta sin motor y sin API key
```

El ciclo, que es la tesis del proyecto:

```
propuesta del LLM  ->  veto del motor  ->  ¿factible?
                                           sí -> entra al agregado de la ronda
                                           no -> reintento CON LA RAZÓN encima
                                                 (máximo 3, luego 'absorber')
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

### 4. Con reglas fijas no hay cascada — y ahora la diferencia es enorme

Con los mismos parámetros de andamio, la ablación **formaliza a todo el mundo**
(informalidad 0%) mientras el LLM llega a 75,6%. El umbral de una regla fija
("sobrecosto > sanción esperada") escala con el ingreso en los dos lados, así
que es idéntico para todos los arquetipos: cruzan todos o ninguno.

Ojo con la lectura: esa diferencia es **a parámetros de andamio no calibrados**,
así que todavía no es el número del candado 4. Pero la dirección es la que
esperábamos, y la razón estructural (el umbral homogéneo) va a sobrevivir a la
calibración.

### 5. Notas sueltas para el equipo

- **`contracts/decision.json` todavía no existe en disco.** `contrato.py` valida
  contra el ejemplo de `docs/PLAN.md` §4 y prefiere el archivo apenas aparezca.
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
