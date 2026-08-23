# Arquitectura

> **Qué es este archivo.** La síntesis de cómo está construido el sistema y por qué. El detalle
> de cada decisión vive en [`docs/adr/`](docs/adr/) y se enlaza, no se copia.
>
> Cada afirmación de acá es verificable en el repo con el comando o la línea que la acompaña.
> Si una no lo es, es un defecto y se corrige.

## Qué es este sistema

Un simulador que responde **"¿cuánta gente cumple una política y a quién le cae encima?"**, no
"¿la política funciona?". Toda proyección oficial de una política laboral asume cumplimiento; este
sistema simula la decisión de cumplir o no, empleador por empleador, y agrega el resultado.

Es un modelo basado en agentes con tres piezas que normalmente no van juntas: **población real de
una encuesta nacional** (GEIH-DANE, no agentes sintéticos), **una capa LLM que propone estrategias**
en vez de escogerlas de un menú, y **un motor determinista que veta** lo que es materialmente
imposible. El caso demo es el alza del salario mínimo colombiano del 23% sobre Bogotá.

## Las capas

```
data/      GEIH cruda ──> poblacion.parquet, empresas.parquet, momentos.json
              │           (6.692 personas -> 4,2M expandidos; 81 celdas de empleador)
              v
behavior/  la capa conductual: arma arquetipos, renderiza el prompt, llama al LLM,
              │               corre las rondas de mejor respuesta y agrega
              v
engine/    el motor determinista: veto de factibilidad + fiscalización endógena + seed
              │
              v
api/       FastAPI: corre 5 trayectorias en paralelo y transmite cada ronda por SSE
              │
              v
web/       Next.js: el enjambre en three.js, el slider de política y el reporte
```

| Capa | Responsabilidad | Lo que NO le corresponde |
|---|---|---|
| `data/` | Convertir microdatos de encuesta en población y momentos observados, con fuente por artículo del CST | Decidir nada del comportamiento |
| `engine/` | Aritmética: qué es factible, cuál es la probabilidad de sanción, el estado vivo de la firma | Proponer estrategias, hablar con el LLM |
| `behavior/` | Descubrir el espacio de estrategias y correr la dinámica de rondas | Juzgar si una propuesta es viable — eso lo hace el veto |
| `api/` | Orquestar trayectorias, presupuesto y transmisión | Calcular cifras nuevas |
| `web/` | Mostrar lo que llega por el flujo | Calcular nada: *"si un número no está en el flujo, no está acá"* (`web/enjambre/lib/corrida.ts:4-6`) |

**El bucle está en `behavior/rondas.py:206 correr()`** y el veto en `engine/veto.py:323 vetar()`.
Entre los dos vive la tesis: el modelo propone y la aritmética manda.

## El veto de factibilidad

En casi toda simulación con agentes LLM, el modelo también juzga si su propia decisión es viable.
Acá no. El LLM **solo propone**; quien acepta o rechaza es aritmética determinista sobre el flujo de
caja de la firma. Una empresa sin caja para pagar indemnizaciones **no puede despedir**, por
convincente que suene la justificación.

Una propuesta rechazada no aborta la corrida: cae por `ORDEN_FALLBACK` (`behavior/contrato.py:59`)
hasta la primera opción factible, y si no hay ninguna se cuenta como `fraccion_sin_salida`, que se
publica. Ver [ADR 0003](docs/adr/0003-veto-de-factibilidad.md) y [ADR 0010](docs/adr/0010-fallback-factible.md).

**Por qué importa para la validez:** es la frontera entre lo que el modelo *imagina* y lo que la
contabilidad *permite*. Sin ella, un LLM convincente puede producir cualquier agregado.

## La cascada: fiscalización endógena

La capacidad de inspección laboral es **fija** —derivada de los 1.300 inspectores que reporta la
OIT para Colombia (`engine/fiscalizacion.py:80`)— así que la probabilidad de que la sanción caiga
sobre una firma concreta se diluye con cada evasor adicional:

```
p(E) = 1 − exp(−C/E)        engine/fiscalizacion.py:124
```

donde `C` son las inspecciones disponibles por trimestre y `E` el peso que está fuera de regla. Más
evasión ⇒ menos riesgo individual ⇒ más incentivo a evadir. Eso convierte decisiones individuales en
una **cascada**, que es el mecanismo que una proyección con cumplimiento total no puede ver.
Ver [ADR 0006](docs/adr/0006-fiscalizacion-es-estado-del-mundo.md) y [ADR 0007](docs/adr/0007-forma-funcional-prob-sancion.md).

> ### ⚠️ La cascada es el mecanismo, no un resultado del proyecto
>
> Dos cosas medidas, las dos publicadas:
>
> 1. **La predicción agregada que produjo está falsada** por el propio backtest del equipo:
>    error +37,37 pp con el signo contrario al observado ([`VALIDATION.md`](VALIDATION.md)).
> 2. **Su aporte al resultado en el camino determinista es +0,0 pp**
>    ([evidencia](docs/evidencia/2026-08-23-E1-E2-E3.md) §E2). p(sanción) sí se mueve —de 67,8% a
>    62,0% según cuánta gente evade— pero ese movimiento todavía no cambia el agregado, porque las
>    reglas fijas de la ablación no son sensibles a p(sanción) en ese rango.
>
> El mecanismo está implementado y su aritmética es correcta y verificable. Su efecto sobre el
> agregado **está por demostrarse**, y hasta que se demuestre no se afirma.

## Determinismo y reproducibilidad

Tres niveles, según la [ADR 0009](docs/adr/0009-frontera-del-determinismo.md):

| Nivel | Qué garantiza | Cómo se comprueba |
|---|---|---|
| **3 · ablación** | El camino sin LLM es determinista por construcción | `make run` (modo `reglas` por defecto) |
| **2 · caché** | Mismo seed + misma caché + mismas versiones = mismo resultado | `make run MODO=llm`, comparando el par `(seed, manifiesto)` |
| **1 · LLM en vivo** | No se garantiza, y se dice | — |

**Qué garantiza exactamente.** `make run` emite un **artefacto canónico** en `scripts/salidas/` que
**no lleva fecha**, a propósito: dos corridas con la misma identidad producen el archivo byte a
byte igual, y un timestamp haría imposible compararlo. El candado **G1** de `VALIDATION.md` corre la
simulación dos veces y compara los bytes; hoy **PASA**.

```bash
make run && make run     # el segundo imprime "DETERMINISMO: IDÉNTICO al anterior"
```

**Qué NO garantiza, y hay que decirlo:** hoy **el `seed` es una etiqueta, no una perilla**
(`api/servidor.py:80`). Medido: `--seed 42` y `--seed 99` dan rondas idénticas, y solo cambia el
rótulo. La reproducibilidad de hoy viene de la caché y de la ablación, no de la semilla. Cambiará el
día que el seed elija las paráfrasis de la banda, y es una sola línea.

## Alternativas descartadas y por qué

La sección que responde *"¿hay ingeniería real acá?"*. Cada una con su ADR:

| Decisión | Se descartó | Por qué |
|---|---|---|
| [ADR 0001](docs/adr/0001-motor-vectorizado-propio.md) · Motor propio en numpy | Mesa, AgentSociety, OASIS, AgentTorch | ~300 líneas vectorizadas caben en una tarde de lectura de un revisor; un framework de agentes mete su propio scheduler entre la tesis y el resultado |
| [ADR 0002](docs/adr/0002-llm-por-arquetipo.md) · LLM por arquetipo, no por agente | Una llamada por agente | 4,2M de agentes son inviables; la heterogeneidad la pone la GEIH, el LLM solo aporta el espacio de estrategias |
| [ADR 0003](docs/adr/0003-veto-de-factibilidad.md) · Veto determinista | Menú fijo de estrategias · Juez LLM | El menú fijo mete la conclusión en el diseño; el juez LLM valida sus propios sesgos |
| [ADR 0004](docs/adr/0004-geih-y-salario-minimo.md) · GEIH + salario mínimo | TransMilenio | La política ya ocurrió y la encuesta posterior existe, así que el modelo se puede puntuar sin esperar nada |
| [ADR 0005](docs/adr/0005-el-reloj-de-la-simulacion.md) · 3 rondas de mejor respuesta | Iterar a convergencia | No se puede probar equilibrio en el alcance; se reporta como dinámica y con la etiqueta de si se estabilizó |
| [ADR 0008](docs/adr/0008-asimetria-firma-trabajador.md) · Asimetría firma/trabajador | Agentes simétricos | Quien decide el registro laboral es el empleador |

Lo que **no se construyó** y por qué está en [`docs/PLAN.md`](docs/PLAN.md) §9 y en la tabla
*"Dónde NO hay que creerle"* de [`VALIDATION.md`](VALIDATION.md).

## Dominio del motor: qué cabe y qué no

Declarar los límites es parte de la credibilidad, no una debilidad.

**Sirve para:** cambio de costos o incentivos + capacidad de fiscalización finita + población real,
donde **incumplir es una opción**. Impuestos, subsidios condicionados, regulación laboral, cuotas.

**No sirve para:** física de flujo (tráfico, evacuación, contagio), ni nada donde la decisión no sea
cumplir/no cumplir.

**No modela, y el sesgo va declarado:** productividad, demanda, capital y precios endógenos (⇒ la
informalidad es cota superior y el empleo cota inferior); tasa de desempleo (no hay denominador);
trabajadores por cuenta propia, el 23% de los ocupados (⇒ el agregado cubre 3.235.639 personas con
empleador, no 4,2 millones); efecto faro sobre salarios informales.

**Hoy el motor tiene una sola política.** `aumento_pct: float` recorre las cinco capas hasta el
prompt, y el campo `politica.tipo` de `contracts/ronda.json` existe pero **no lo lee nadie**.
Generalizarlo a una abstracción `Politica` es la fase 2 de [`ROADMAP.md`](ROADMAP.md), y es lo que
separa este demo de una plataforma.

## Costo y presupuesto de LLM

| | |
|---|---|
| Escala | 81 celdas de empleador × 3 rondas con LLM × 5 trayectorias |
| Corrida en frío, 1 trayectoria, cobertura 0,80 | **94 llamadas, USD 1,26, 2 min 46 s** |
| Corrida completa, 5 trayectorias | **~5 min** (en paralelo desde `a4e1429`; antes ~23 min) |
| Corrida más cara que tiene sentido pedir | cobertura 1,00 × 5 trayectorias = 1.215 llamadas = **USD 16,29** |

**Tres frenos, y el del medio es el que importa:**

1. **Caché en disco** por hash de `(modelo, sistema, usuario, esquema)` — `behavior/cache.py:33`.
   El escenario demo va versionado en `behavior/cache-demo.json` (518 respuestas ya pagadas).
2. **Tope derivado por request** (`api/servidor.py:152 tope_derivado()`): se calcula con la cuenta
   **exacta** de llamadas que esa corrida va a hacer, usando la misma `particionar_por_peso()` del
   motor. Un tope fijo o corta una corrida legítima —y entonces publica una banda sobre 2
   trayectorias donde el contrato promete 5— o deja pasar una desbocada.
3. **Corte duro de presupuesto** (`behavior/presupuesto.py`), con precio de lista y no promocional,
   para sobreestimar a propósito.

**Límite conocido:** el corte no es atómico (`behavior/cliente.py:135`) — `comprobar()` y
`registrar()` están en bloques separados, así que con `paralelismo=8` hay ventana de sobregiro. Es
un detector, no un freno, y así se declara.
