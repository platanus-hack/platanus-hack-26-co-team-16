# Decisiones de la corrida — alza 23%, seed 42

> Generado por `scripts/informe_decisiones.py` sobre la cache ya pagada.
> **Costo de este informe: USD 0.00 · 0 llamadas nuevas.**
> 81 celdas · 4 rondas · 243 decisiones con nombre y apellido.

## 0 · De donde sale cada decision

Tres origenes distintos, y confundirlos cambia todas las cifras de abajo:

- **81 decisiones del modelo**, resueltas con una respuesta ya pagada de
  `behavior/cache-demo.json`. Son las unicas que un LLM escribio.
- **150 decisiones de la cola**, que van a la **regla fija** de
  `behavior/ablacion.py` **por diseno**: el ruteo top-K manda al modelo solo la
  cabeza que concentra el 80% del peso (31 de 81 celdas). Esto no es un defecto.
- **12 decisiones que SI debian ir al modelo y cayeron a la regla** porque su
  respuesta no estaba en la cache. Esto **si** es un defecto, y es de esta corrida.

La cache se pago antes de un cambio que movio la probabilidad de inspeccion por
celda, y esa probabilidad va dentro del texto del prompt, o sea dentro de la clave
de cache. Es el mismo defecto que AGENTS.md ya declara para
`data/prediccion_modelo.json`. Consecuencia medida: `scripts/reproduce.py` no
reproduce sobre `main` hoy — se cae en la primera celda sin cachear.

**Lee las secciones 1 a 6 sabiendo eso.** La seccion 7 cita solo justificaciones
de origen `llm-cache`, que son las unicas escritas por el modelo.

## 1 · Que se decidio, en los tres denominadores

La misma decision pesa distinto segun que se cuente. `decisiones` es una fila por
voto; `personas` usa el factor de expansion de la GEIH; `firmas` cuenta unidades
productivas. Son universos distintos y enfrentarlos es un error, por eso van los tres.

| familia | n | % decisiones | % personas | % firmas | que mueve |
|---|---|---|---|---|---|
| `absorber` | 149 | 61.3% | 43.0% | 30.4% | NADA en el agregado |
| `subir_precios` | 41 | 16.9% | 35.8% | 3.8% | NADA en el agregado |
| `informalizar` | 40 | 16.5% | 19.6% | 64.7% | informalidad ↑ |
| `bajar_horas` | 13 | 5.3% | 1.6% | 1.1% | jornada ↓ |

**Y solo las 81 que decidio el modelo** — la tabla de arriba las
mezcla con las que resolvio la regla fija, y las dos poblaciones no se parecen:

| familia | n | % decisiones | % personas | que mueve |
|---|---|---|---|---|
| `subir_precios` | 41 | 50.6% | 62.3% | NADA en el agregado |
| `informalizar` | 33 | 40.7% | 32.3% | informalidad ↑ |
| `absorber` | 6 | 7.4% | 4.5% | NADA en el agregado |
| `bajar_horas` | 1 | 1.2% | 0.9% | jornada ↓ |


**Decisiones que no mueven ninguna cifra de portada:** 190 de 243 (78.2% de las decisiones, 78.8% de las personas).
Son `subir_precios`, `absorber` y `renegociar`: la planta queda donde estaba y el
empleo tambien. La pantalla las lee como adaptacion; el motor las lee como nada.

## 2 · Quien decidio que — reparto por sector

| sector | n | `absorber` | `subir_precios` | `informalizar` | `bajar_horas` |
|---|---|---|---|---|---|
| adm_publica_edu_salud | 27 | 89% | 0% | 11% | 0% |
| agro_mineria | 27 | 89% | 0% | 0% | 11% |
| alojamiento_comida | 27 | 70% | 11% | 7% | 11% |
| comercio | 27 | 30% | 37% | 33% | 0% |
| construccion_utilities | 27 | 85% | 11% | 4% | 0% |
| industria | 27 | 37% | 15% | 48% | 0% |
| otros_servicios | 27 | 63% | 11% | 15% | 11% |
| servicios_empresariales | 27 | 7% | 63% | 26% | 4% |
| transporte | 27 | 81% | 4% | 4% | 11% |

## 3 · Reparto por tamano

| tamano | n | `absorber` | `subir_precios` | `informalizar` | `bajar_horas` |
|---|---|---|---|---|---|
| grande | 54 | 57% | 43% | 0% | 0% |
| micro | 81 | 52% | 0% | 44% | 4% |
| pyme | 108 | 70% | 17% | 4% | 9% |

## 4 · La restriccion que decide: la caja

Cuantas indemnizaciones alcanza a pagar cada celda con su flujo de caja libre.
Es la variable que las justificaciones invocan mas que ninguna otra.

- Decisiones tomadas por una celda que **alcanza a indemnizar al menos a un trabajador**: 162 de 243 (66.7%).
- Decisiones que efectivamente fueron `despedir`: **0**.

## 5 · Magnitudes declaradas

Lo que el agente DIJO que haria, cuando el campo trae numero. `aumento_precios_pct`
es traslado declarado, no inflacion: no hay respuesta de demanda en este modelo
(`behavior/rondas.py:779`).

| campo | n con valor | min | mediana | max |
|---|---|---|---|---|
| `empleados_a_informalizar` | 26 | 0.0 | 2.0 | 7.0 |
| `empleados_a_despedir` | 7 | 0.0 | 0.0 | 0.0 |
| `reduccion_horas_pct` | 13 | 20.0 | 20.0 | 41.0 |
| `reduccion_margen_pct` | 6 | 5.0 | 8.0 | 15.0 |
| `aumento_precios_pct` | 41 | 6.0 | 15.0 | 96.8 |

## 6 · Salud de la capa

- **Fallback** (el veto tumbo todo lo que propuso y cayo a la opcion terminal): 118 de 243 decisiones (48.6%), que son 36.3% de las personas.
- **Sin ninguna opcion factible** (ni siquiera la terminal era pagable): 106 (43.6%).
- De esos fallbacks, **13** son de celdas que van al modelo; el resto son de la cola resuelta por regla fija.

Los dos denominadores no coinciden y esa diferencia importa: la pantalla publica el
de decisiones, y el que describe a cuanta gente le paso es el de personas.

## 7 · Por que — en palabras del agente

Textual, sin editar. Es la materia prima de todo lo anterior.

### `absorber` · 6 decisiones — NADA en el agregado

- **alojamiento_comida · micro · ronda 1** (2 trab., representa 45,450 personas) — «Ya opero con ambos trabajadores fuera de regla, no tengo caja para indemnizar ni margen para formalizar, así que mantengo la planta informal y absorbo cualquier presión de costo con un leve recorte de margen, dado que la probabilidad de inspección (0.3%) hace que seguir informal sea la opción más racional.»
- **alojamiento_comida · micro · ronda 2** (2 trab., representa 45,450 personas) — «Con ambos trabajadores ya fuera de regla y sin caja suficiente para pagar la indemnización de un despido ni para asumir el 23% extra de formalizar, la única salida viable es mantener el esquema informal y absorber el ajuste reduciendo mi propio margen.»
- **alojamiento_comida · micro · ronda 3** (2 trab., representa 45,450 personas) — «Como ya casi todos mis trabajadores están fuera de regla y el riesgo de inspección es mínimo (0.2%), me conviene mantener el esquema informal y absorber el pequeño resto de costo formal reduciendo mi margen, en lugar de despedir (indemnización inviable con mi caja) o formalizar (costo 23% más alto).»
- **adm_publica_edu_salud · pyme · ronda 1** (74 trab., representa 42,149 personas) — «sin ninguna opción factible tras 3 propuestas vetadas: el sobrecosto del periodo es 202.567.949 u y la caja del periodo es 119.480.400 u: no se puede pagar con el margen; el sobrecosto del periodo es 119.515.090 u y la caja del periodo es 119.480.400 u: no se puede pagar con el margen; el sobrecosto del periodo es 172.182.757 u y la caja del periodo es 119.480.400 u: no se puede pagar con el margen»
- **industria · pyme · ronda 3** (24 trab., representa 37,493 personas) — «El costo esperado de informalizar más trabajadores (22% de probabilidad de inspección x 21.000.000 u de sanción) supera con creces el ahorro marginal del 23% en costo formal, y mi caja de 22.680.000 u alcanza para cubrir el incremento de costo de los 13 trabajadores que sigo manteniendo formales sin necesidad de despedir ni reducir horas.»
- **alojamiento_comida · micro · ronda 3** (4 trab., representa 37,052 personas) — «Ya opero totalmente informal por lo que el alza del costo formal no me afecta directamente, así que mantengo mi planta y absorbo cualquier presión residual sobre márgenes en lugar de arriesgar despidos costosos, dado que la probabilidad de inspección (0,9%) hace que el riesgo esperado de sanción sea mínimo frente a la caja disponible.»

### `subir_precios` · 41 decisiones — NADA en el agregado

- **servicios_empresariales · grande · ronda 1** (299 trab., representa 428,937 personas) — «Con probabilidad de inspección del 100% y una sanción de 36.000.000 u por trabajador, informalizar o despedir es económicamente inviable, así que trasladar el alza del 23% en el costo formal vía precios preserva la planta y evita riesgo legal.»
- **servicios_empresariales · grande · ronda 2** (299 trab., representa 428,937 personas) — «Con inspección al 100% y sanción de 36M por trabajador, informalizar es ruinoso, así que mantengo la estrategia de trasladar el aumento del 23% en costos formales a precios, como ya hice el periodo anterior, preservando mi plantilla formal y mi caja.»
- **servicios_empresariales · grande · ronda 3** (299 trab., representa 428,937 personas) — «Con probabilidad de inspección del 100% y una sanción de 36.000.000 u por trabajador, informalizar es ruinoso frente al ahorro marginal del 23% en costo formal, por lo que la mejor respuesta es trasladar el aumento de costo a precios, como ya vengo haciendo con éxito.»
- **industria · grande · ronda 2** (299 trab., representa 144,627 personas) — «Con la caja insuficiente para absorber el sobrecosto y una probabilidad de inspección del 100% que hace inviable informalizar, trasladar el aumento de costo laboral a los precios evita un desembolso de caja inmediato y la sanción segura por informalidad.»
- **comercio · grande · ronda 1** (299 trab., representa 142,914 personas) — «Con probabilidad de inspección del 100% y una sanción que multiplica varias veces el ahorro por informalizar, la única salida racional es trasladar el aumento del 23% en el costo formal a los precios de venta, manteniendo la planta formal intacta y evitando riesgo legal y de caja.»
- **comercio · grande · ronda 2** (299 trab., representa 142,914 personas) — «Con probabilidad de inspección del 100% y una sanción de 27,6M por trabajador, informalizar es demasiado riesgoso, así que traslado el aumento del 23% en costos formales directamente a precios, manteniendo mi plantilla y evitando exponerme a la sanción.»

### `informalizar` · 33 decisiones — informalidad ↑

- **comercio · micro · ronda 1** (2 trab., representa 132,468 personas) — «Con 0 trabajadores en regla no puedo informalizar más ni pagar una indemnización con la caja disponible, así que mantener la informalidad total es la única opción viable y de menor riesgo dado el bajo riesgo de inspección.»
- **comercio · micro · ronda 2** (2 trab., representa 132,468 personas) — «Con los dos trabajadores ya informales y sin caja suficiente para indemnizar (1.377.000 u frente a 3.966.610 u por despido), la mejor respuesta es sostener la informalidad dado el bajo riesgo de inspección observado.»
- **comercio · micro · ronda 3** (2 trab., representa 132,468 personas) — «Con caja de 1.377.000 u insuficiente para indemnizar (3.966.610 u) y sin trabajadores formales que informalizar o hacer cumplir, la mejor respuesta es sostener la informalidad total ya lograda, minimizando costos ante un riesgo de inspección casi nulo.»
- **comercio · micro · ronda 1** (7 trab., representa 61,130 personas) — «El costo esperado de sanción (3.2%×21.000.000≈672.000 u por trabajador) es muy inferior al ahorro que genera evitar el alza del 23% en el costo formal, y mi caja no alcanza para indemnizar despidos, por lo que conviene informalizar a la mayoría de los trabajadores formales restantes manteniendo solo uno registrado.»
- **comercio · micro · ronda 2** (7 trab., representa 61,130 personas) — «Con solo 1 trabajador aún formal, pasarlo a informal minimiza el nuevo costo del 23% mientras el riesgo esperado de sanción (2.7%×21M ≈ 567k) sigue siendo muy inferior al ahorro, y es la única opción compatible con mi caja disponible.»
- **comercio · micro · ronda 3** (7 trab., representa 61,130 personas) — «Con 0 trabajadores en regla no puedo informalizar más y el riesgo esperado de sanción sigue siendo mucho menor que el costo formal, por lo que la mejor respuesta es sostener la informalidad total ya alcanzada.»

### `bajar_horas` · 1 decisiones — jornada ↓

- **servicios_empresariales · pyme · ronda 1** (39 trab., representa 49,001 personas) — «Con la sanción esperada (56.2% x 36.000.000 u) muy por encima del ahorro de informalizar, y sin caja para indemnizar despidos ni para absorber el sobrecosto completo, reducir horas contratadas en 41% es la única vía que recorta el costo formal lo suficiente para caber en los 63.180.000 u disponibles sin exponerme a sanción ni gastar en indemnizaciones.»

---

## Como se reproduce

```bash
python3 scripts/informe_decisiones.py
```

Lee `behavior/cache-demo.json` y no toca la red. Si alguna llamada saliera a la API,
el script aborta con codigo distinto de cero antes de escribir nada.

