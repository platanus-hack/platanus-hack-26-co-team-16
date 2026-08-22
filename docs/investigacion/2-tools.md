# Esfera 2 · Tools — el stack real y los estándares

**Dueño: Manuel (R2)** · Reglas de la carpeta: [`README.md`](README.md)

> `docs/PLAN.md` §4.1 ya hizo build-vs-buy sobre **frameworks de ABM** y el veredicto fue
> "motor propio" ([ADR 0001](../adr/0001-motor-vectorizado-propio.md)). Esa decisión no se
> reabre. Este documento cubre lo que aquella tabla no cubría: **qué patrón le robamos a
> cada framework que descartamos**, y sobre todo **con qué herramientas y estándares se
> construye de verdad el motor**.

**Convención de verificación:** ✅ URL abierta en esta sesión o ya verificada en el repo ·
◻️ URL canónica del proyecto oficial, no abierta acá · ⚠️ sin verificar, no usar.

---

## 1. Frameworks de ABM — qué le robamos a cada uno

No entra ninguno como dependencia ([ADR 0001](../adr/0001-motor-vectorizado-propio.md)).
Lo que sí entra es el diseño.

| Framework | Patrón que le robamos | Qué NO le robamos |
|---|---|---|
| **Mesa** ✅ [repo](https://github.com/mesa/mesa) | La separación explícita *modelo · agentes · scheduler · recolector de datos*. Nuestro `engine/` tiene esas cuatro cosas, solo que vectorizadas | El scheduler OOP agente-por-agente. Nuestro bucle son 4 rondas sobre un dataframe |
| **AgentTorch** ✅ (`PLAN.md` §4.1) | **La idea de arquetipo:** llamar al LLM por grupo y que los miles de agentes muestreen de esa distribución. Es [ADR 0002](../adr/0002-llm-por-arquetipo.md) | La dependencia. El muestreo por arquetipo son ~50 líneas |
| **OASIS** ✅ [arXiv 2411.11581](https://arxiv.org/html/2411.11581v4) | El **agregado compartido**: los agentes no se ven entre sí uno a uno, ven un resumen del estado del sistema. Es exactamente nuestra entidad `Agregado` y lo que hace posible la cascada sin O(n²) | El runtime de 1M de agentes. Nuestra escala viene del factor de expansión de la GEIH, no del runtime |
| **AgentSociety** ✅ [arXiv 2502.08691](https://arxiv.org/abs/2502.08691) | Que un entorno de política pública con agentes LLM a escala es viable, y sirve de prior art citado | Todo el entorno urbano. No trae GEIH ni margen formal/informal |
| **Concordia** ✅ [repo](https://github.com/google-deepmind/concordia) | Nada estructural. Prior art | El framework: solo tenemos 3-4 historias narradas |
| **Agents.jl** ✅ [arXiv 2101.10072](https://arxiv.org/pdf/2101.10072) | La tesis de que un ABM completo cabe en poco código si el modelo está bien acotado. Es el argumento de nuestras ~300 líneas | Julia. El equipo escribe Python |
| **NetLogo**, **SUMO/MATSim** ✅ | Nada | No existe modelo NetLogo de informalidad laboral colombiana; el caso no es de movilidad |

---

## 2. Estándares y protocolos — la parte que nadie más va a tener

| Estándar | Qué es | **Qué NO nos da** | Veredicto |
|---|---|---|---|
| **Protocolo ODD** ✅ [JASSS 23(2):7](https://www.jasss.org/23/2/7.html) | El estándar de facto para describir un ABM completo y reimplementable (7 elementos, ver [`1-teorica.md`](1-teorica.md) §1) | **No dice si el modelo es bueno.** Es documentación, no validación ni diseño. Un modelo malo documentado en ODD sigue siendo malo, solo que ahora es refutable | **Sí, como estructura documental.** Cuesta cero y es lo primero que reconoce un revisor que sepa del campo |
| **CoMSES Net / Model Library** ✅ [estándares](https://www.comses.net/resources/standards/) | La comunidad que archiva y revisa modelos computacionales en ciencias sociales y ecológicas. Define qué hace a un modelo archivable y reproducible | **No hay tiempo de publicar ahí** (hay revisión por pares del artefacto), y su checklist asume datos redistribuibles — los microdatos de la GEIH tienen sus propios términos | **Sí, como checklist de reproducibilidad**, no como destino de publicación. Lo que nos llevamos: código + datos + documentación ODD + licencia + instrucciones de corrida, que es exactamente lo que `make reproduce` tiene que satisfacer |
| **Model card** ◻️ | Ficha corta: qué modela, con qué datos, para qué usos sirve y para cuáles no | **El formato viene de ML supervisado**: sus casillas (métricas por subgrupo, datos de entrenamiento) no mapean limpio a un ABM. Se adapta la idea, no la plantilla | **Sí**, en forma de `engine/MODELO.md` + la sección "dónde NO hay que creerle" de `VALIDATION.md` |

---

## 3. Determinismo y vectorización en Python — el corazón operativo

La promesa *"mismo seed, mismo resultado"* está en el pitch. Estas son las herramientas que
la hacen cierta en vez de aspiracional.

| Herramienta | Qué ahorra | Qué construiríamos igual | Veredicto |
|---|---|---|---|
| **`numpy.random.Generator` + `SeedSequence`** ✅ [docs de generación paralela](https://numpy.org/doc/stable/reference/random/parallel.html) | La forma **correcta** de tener aleatoriedad reproducible: `SeedSequence` convierte una semilla cualquiera en un estado inicial de buena calidad, y `.spawn()` deriva sub-streams independientes con muy alta probabilidad. Además la práctica recomendada de **registrar la entropía** de la semilla para poder reproducir | La disciplina de que **toda** aleatoriedad pase por el generador sembrado y nada por `random` global | **Sí, obligatorio.** Un `Generator` raíz por corrida, un sub-stream por ronda vía `spawn()`. Así agregar una ronda no corre los números de las anteriores, que es el error clásico que rompe la reproducibilidad a mitad del hackathon |
| **pandas / numpy vectorizado** ✅ | Todo el motor. 4 rondas sobre un dataframe en vez de un bucle por agente | La lógica del modelo, que es 100% nuestra | **Sí.** Es el entregable técnico ([ADR 0001](../adr/0001-motor-vectorizado-propio.md)) |
| **`PYTHONHASHSEED`** ◻️ | Elimina la variación de orden en iteración de sets/dicts entre procesos | — | **Sí, fijado en el `Makefile`.** Es una línea y evita un no-determinismo invisible |
| Determinismo en punto flotante | — | — | ⚠️ **Límite declarado:** operaciones vectorizadas pueden variar en el último bit entre versiones de BLAS o arquitecturas. La promesa honesta es *misma máquina + mismas versiones + mismo seed*, y así se escribe en [ADR 0009](../adr/0009-frontera-del-determinismo.md), no "bit a bit en cualquier computador" |

---

## 4. Calibración y sensibilidad

| Herramienta | Qué ahorra | Qué construiríamos igual | Veredicto |
|---|---|---|---|
| **SALib** ✅ [repo](https://github.com/SALib/SALib) · [docs](https://salib.readthedocs.io/) | Implementaciones de Sobol, Morris, FAST y muestreo de Saltelli. Hay uso documentado exactamente para nuestro caso: barrer el espacio de parámetros de un ABM y medir qué parámetro mueve el resultado | El bucle de corridas y la agregación de resultados | **Sí, si el tiempo alcanza — con Morris, no con Sobol.** El barrido de sensibilidad de `capacidad_fiscalizacion` y `factor_prestacional` no es opcional: `PLAN.md` §10 lo exige para que la cascada no parezca escogida a conveniencia. Morris (screening) da el ranking de qué importa con órdenes de magnitud menos corridas que Sobol. **Si SALib no entra a tiempo, el barrido se hace a mano con un `for`** — lo que no es negociable es que exista |
| **`sbi`** ✅ [docs](https://sbi-dev.github.io/sbi/) | Calibración bayesiana con verosimilitud intratable | — | **No en 36 horas.** `VALIDATION.md` como camino futuro |
| **scipy.optimize** ◻️ | Ajuste de parámetros contra momentos (el MSM simple del candado 1) | — | **Sí si hace falta.** Con 2-3 parámetros libres, una búsqueda en grilla puede bastar y es más legible para un revisor |

---

## 5. Contratos y datos

| Herramienta | Qué ahorra | Qué construiríamos igual | Veredicto |
|---|---|---|---|
| **pydantic v2** ◻️ [docs](https://docs.pydantic.dev/) | Validación en la frontera de `api/`: los tres `contracts/*.json` se vuelven modelos tipados y un payload malformado falla en el borde con mensaje claro, no tres capas adentro | Los modelos en sí (son los contratos, ya están escritos) | **Sí, solo en `api/`.** FastAPI ya lo trae, así que no es dependencia nueva. **`engine/` no lo usa:** adentro se trabaja con dataframes, y meter validación por fila mataría la vectorización |
| **pyarrow / parquet** ◻️ [docs](https://arrow.apache.org/docs/python/) | Leer `data/poblacion.parquet` de Alejo | — | **Sí.** Es el formato que ya acordó `PLAN.md` §4 |
| **jsonschema** ◻️ | Validar que la salida del motor cumple `contracts/ronda.json` | — | **Sí, pero en `tests/` (Juanda), no en el motor.** Es el test 4 de `tests/README.md`. Validar en caliente cuesta tiempo de corrida y no aporta nada al pitch |

---

## 6. API, streaming y reproducibilidad

| Pieza | Decisión | Por qué |
|---|---|---|
| **FastAPI** ◻️ [docs](https://fastapi.tiangolo.com/) | Sí, ya fijado en `PLAN.md` D7 | El motor es Python; la API vive donde vive el motor |
| **Supabase Realtime vs SSE** | **Supabase**, ya fijado en D7 | El insumo de Manuel §4.4 recomendaba SSE por simplicidad, pero D7 eligió Supabase y Dani (R4) construye contra eso. **No se reabre.** Se anota el trade-off: SSE habría sido menos infraestructura; Supabase da persistencia y streaming en una sola pieza, y el equipo ya lo maneja |
| **Caché en disco por hash del prompt** | Sí, en `behavior/` (Nico), pero **el motor depende de ella para la reproducibilidad** | Es lo que convierte una corrida con LLM en algo repetible. Por eso la caché es un **artefacto versionado**, no un archivo temporal: ver [ADR 0009](../adr/0009-frontera-del-determinismo.md) |
| **Escenarios precomputados** | Sí | `PLAN.md` §8: un run de 4 minutos mata un pitch de 3:30. Los puntos del barrido se precomputan y se sirven de Supabase |

---

## Lo que NO entra, y por qué

| Descartado | Razón |
|---|---|
| Cualquier framework de ABM como dependencia | [ADR 0001](../adr/0001-motor-vectorizado-propio.md). Si una herramienta nos ahorra el 100% del motor, el 25% técnico se va con ella |
| **DoWhy** | La validación es calibración + backtest, no un grafo causal. Importarlo sin usarlo de verdad es decoración que un revisor detecta |
| **Sobol** (a favor de Morris) | Sobol necesita un orden de magnitud más de corridas. Con presupuesto de LLM acotado, el screening de Morris da la respuesta que necesitamos: *qué parámetro importa* |
| Auth, cuentas, multi-tenant | Un extraño con el link tiene que usarlo sin registrarse (`PLAN.md` §9) |
| ORM sobre Supabase | `api/` escribe rondas y decisiones; el cliente de Supabase alcanza. Un ORM son horas que no compran nada |
| **Cualquier dependencia nueva después de H+28** | Feature freeze, `AGENTS.md` |
