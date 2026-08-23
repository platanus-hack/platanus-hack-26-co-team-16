# Plan de construcción — PlatanusHack 26 Bogotá · Track Simulations · team-16

> Documento de fusión de los 5 insumos de `docs/fuentes/`. Las marcas de confianza se respetan:
> **✅ verificado contra fuente** (por el insumo que lo trae) · **⚠️ plausible sin verificar** (va a la tabla de la sección 6, nunca se enuncia como hecho) · **💭 juicio**.
> Horas en formato **H+N** (N horas desde la apertura oficial), porque la hora exacta de arranque no está confirmada.

---

## 1. Qué se va a construir

Un simulador de políticas públicas que no responde *"¿funciona la política?"* sino **"¿cuánta gente la cumple y a quién le cae encima?"**. La población de agentes se instancia desde personas reales anonimizadas de los microdatos de la GEIH del DANE (✅ única fuente verificada de los cinco insumos) — no se inventa nadie. Un motor determinista con seed calcula costos y **veta** las reacciones imposibles que propone una capa LLM que descubre estrategias de adaptación (informalizar, absorber, despedir, evadir). Los agentes deciden en 3–4 rondas de mejor respuesta viendo lo que hacen los demás: como la fiscalización es fija, más evasión baja la probabilidad de sanción y produce la **cascada** que el modelo oficial no ve. Demo: el aumento del salario mínimo del 23% en Bogotá, sin decirle nunca al modelo el nombre de la política.

> ### ⚠️ Dos correcciones a este párrafo — 23-ago
>
> **1. La cascada es el mecanismo del modelo, no un hallazgo del proyecto.** La predicción
> agregada que produce está **falsada** por el propio backtest del equipo: error **+37,37 pp**
> con el signo contrario al observado ([`VALIDATION.md`](../VALIDATION.md)). Y su aporte medido
> al resultado en el camino determinista es **+0,0 pp**
> ([evidencia](evidencia/2026-08-23-E1-E2-E3.md) §E2). El mecanismo está implementado y su
> aritmética es correcta; su efecto sobre el agregado está por demostrarse.
>
> **2. Lo de "validado contra ~20 alzas históricas" nunca ocurrió** y se quitó de la frase. La
> validación real es un backtest de **un** episodio (2025→2026) más un segundo episodio de
> control (2024→2025), o sea **n = 2**, y así se reporta en `VALIDATION.md`.

### 1.1 El aporte: los cuatro datos que hoy no existen — el desarrollo se mide contra esto

Cada feature del sistema debe producir (o servir a) uno de estos cuatro datos. Lo que no sirva a ninguno, no se construye.

| # | El dato nuevo | Quién no lo tiene hoy | Qué pieza del sistema lo produce |
|---|---|---|---|
| A1 | **Cuánta gente cumple de verdad.** La proyección oficial asume cumplimiento total; nadie publica "de los 2,4M, X se informalizan y el aumento real de ingresos es Z". | DANE, ministerio, Fedesarrollo — el número no existe | La ronda 3 (`Simulacion.brecha()`) |
| A2 | **La forma de la curva: dónde está el codo.** La econometría da elasticidades (línea recta); el bucle de fiscalización puede producir un umbral donde la cascada se dispara. Si el 7% y el 13,6% se absorben y el 23% cruza el umbral, el debate real no es "23 vs 13,6" sino "antes o después del codo". | Nadie — requiere el bucle endógeno | El **barrido de `aumento_pct`** en el motor (ver §4) + la curva en la interfaz |
| A3 | **A quién le cae encima.** El desglose por sector × tamaño × ingreso que el promedio nacional esconde — la pregunta política que decide si una reforma sobrevive. | Cualquier actor de la mesa de concertación | El mapa distributivo, posible porque las correlaciones vienen reales de la GEIH |
| A4 | **Por qué evade cada quien.** El menú de estrategias reales (informalizar parcial, bajar horas, renegociar) y cuál domina en qué segmento — cada estrategia responde a una política distinta (más inspectores no le hacen nada al que no le alcanza la plata). | Ningún modelo con estrategias enumeradas a mano | La capa LLM + el veto, agregado por arquetipo |

**Para quién:** el que decide (gobierno, el litigio abierto) deja de elegir entre tres números ciegos · el que discute (concejal, gremio, periodista) obtiene la capacidad que hoy está encerrada en meses/economistas/PDF, vuelta interrogable · el que la sufre puede verse en el mapa ("gente como yo, ¿gana o pierde?").

**El límite, declarado (es parte del pitch, no debilidad):** no entregamos el futuro, entregamos **el rango** con banda y con el error del backtest publicado. El aporte es convertir un supuesto invisible ("la gente cumple") en un número medible con margen de error.

## 2. La frase del pitch

> **"El gobierno subió el salario mínimo 23% asumiendo que la gente cumple. Nosotros simulamos, con 240.000 hogares reales del DANE, cuánta gente cumple de verdad — y a quién le cae encima."**

(El 23%, los decretos 1469/1470 de 2025, los ~2,4M de trabajadores al mínimo y los ~240.000 hogares/año de la GEIH están ✅ verificados en el insumo de Juan David, con fuentes citadas.)

## 3. Decisiones tomadas

| # | Decisión | Razón — y quién perdió |
|---|---|---|
| D1 | **Caso demo: salario mínimo 23% → margen formal/informal, acotado a Bogotá.** | **Pierde TransMilenio ("colados")**, la recomendación del insumo de políticas. Regla de prioridad: evidencia verificada > razonamiento. La GEIH está ✅ verificada (portal, catálogos, registro gratuito); TODOS los datos de TransMilenio están ⚠️ (Encuesta de Movilidad, cifras de evasión, GTFS). Además el salario mínimo tiene ~20 experimentos naturales para backtest y una controversia viva (litigio en Consejo de Estado ✅). El bucle de fiscalización en cascada —lo mejor de la propuesta TransMilenio— **se transfiere intacto**: la capacidad de inspección laboral es fija. TransMilenio queda como plan B nombrado (ver §6, V1). |
| D2 | **La arquitectura de "Pulso" (fan-out de una pasada) pierde como motor; su capa de producto se adopta como interfaz.** | Una sola pasada de LLM es una opinión, no una simulación (anatomía de Manuel §2.5: sin dinámica temporal no hay emergencia). Pero el feed en vivo con Supabase Realtime, el input de escenario y el dashboard de Nico son exactamente el "producto usable" que ningún paper tiene — se construyen encima del motor de rondas. |
| D3 | **Kiyotaki-Wright, FlyWire y Schelling (insumo de Daniel) quedan fuera; su metodología entra completa.** | El marco ya está decidido y no se reabre. Se adoptan: el test de re-skinning como control de contaminación, la regla "barra de error sobre paráfrasis del prompt, no sobre temperatura", y "reportar varianza, no solo media". |
| D4 | **LLM por arquetipo, no por agente.** | Contradicción entre insumos: políticas propone llamada por agente; Manuel (capa de arquetipos, AgentTorch) y Juan David ("el LLM nunca en el bucle caliente") proponen lo contrario. Ganan estos dos: con $50/persona, miles de agentes × 4 rondas por agente es inviable. Se llama al LLM por **arquetipo** (sector × tamaño de empresa × formal/informal × tramo de ingreso ≈ 40–60 arquetipos × 4 rondas ≈ ~250 llamadas cacheadas) y los miles de agentes muestrean de esas distribuciones. Modelo grande solo para las 3–4 historias narradas del pitch. |
| D5 | **Teoría de juegos entra, como dinámica de mejor respuesta a 3 rondas — nunca como "convergencia a equilibrio".** | La condición de corte del insumo de políticas está satisfecha: **Nicolás defiende "mejor respuesta" y "equilibrio de Nash" en el Q&A** (confirmado por el equipo). En `VALIDATION.md` se escribe la verdad: es dinámica de mejor respuesta, no prueba de existencia de equilibrio. |
| D6 | **General en el código, estrecho en la pantalla.** | Una sola política en la demo. El motor recibe cualquier política como (cambio de pagos + capacidad de fiscalización + población), pero la pantalla muestra una. Segunda ciudad/política: jamás bloqueante. |
| D7 | **Stack: FastAPI (Python) para el motor · Next.js para la interfaz · Supabase (Postgres + Realtime) para estado y streaming.** | El equipo confirmó fluidez real en los tres. El motor numérico (pandas/numpy) vive donde Python es nativo; el frontend donde el equipo es rápido. |
| D8 | **No es un modelo macro.** | Inflación, crecimiento y tasa de cambio entran como datos exógenos observados, nunca como resultado (modo de falla #3 de Juan David: "nos ganó la economía"). Es un módulo de mercado laboral. |
| D9 | **El output es el rango con incertidumbre + el mapa de quién gana/pierde, nunca un veredicto.** | Antídoto al modo de falla #5 ("nos leyeron como panfleto"): se muestra bajo qué parámetros cada una de las tres posturas (7% / 13,6% / 23%) resulta razonable. |
| D10 | **Deploy en H+4, espejo a repo personal en H+1.** | Los tres insumos que lo mencionan coinciden; el README del repo lo exige (Render no conecta a repos de la organización). |

## 4. Arquitectura

```
GEIH (DANE) ──ingesta──▶ data/poblacion.parquet
                              │
                              ▼
┌───────────────────────────────────────────────────────────┐
│  engine/  · MOTOR FÍSICO (Python, determinista, seed)     │
│  costos formal/informal · flujo de caja · fiscalización   │
│  VETO de factibilidad · scheduler de rondas               │
└──────────────▲──────────────────────────┬─────────────────┘
     propone   │ veta / acepta            │ agregado por ronda
┌──────────────┴─────────────┐   ┌────────▼─────────────────┐
│ behavior/ · CAPA LLM       │   │ api/ · FastAPI           │
│ arquetipos · caché disco   │   │ escribe rondas/reacciones│
│ Haiku masa · grande=relato │   │ en Supabase              │
└────────────────────────────┘   └────────┬─────────────────┘
                                          │ Realtime
                                 ┌────────▼─────────────────┐
                                 │ web/ · Next.js           │
                                 │ slider · curva cascada   │
                                 │ mapa distributivo · feed │
                                 └──────────────────────────┘
```

**Componentes y responsabilidad exclusiva:**

- **`data/`** — ingesta GEIH → `poblacion.parquet` (agentes) + `momentos.json` (objetivos de calibración: informalidad por sector, distribución salarial). Las empresas se construyen agrupando trabajadores por sector × tamaño de empresa (atributos observados en la encuesta, no inventados).
- **`engine/`** — estado del mundo, costos (formal = salario × factor prestacional; informal = salario negociado + riesgo de sanción), probabilidad de fiscalización endógena (capacidad fija / universo de evasores), **veto de factibilidad**, scheduler de rondas, determinismo con seed desde el primer commit.
- **`behavior/`** — prompts por arquetipo (solo mecánica, nunca el nombre de la política), caché en disco con hash del prompt, presupuesto tope por corrida con corte duro, ruteo Haiku/modelo grande.
- **`api/`** — FastAPI: `POST /simulaciones` (política + seed) → corre el motor → persiste cada ronda en Supabase.
- **`web/`** — Next.js: slider de política (7 / 13,6 / 23% + barrido fino precomputado para mostrar el codo — dato A2), gráfica "proyección oficial vs curva de cascada", mapa distributivo por sector × tramo de ingreso con bandas (dato A3), desglose de estrategias por segmento (dato A4), feed Realtime de decisiones, 3–4 historias narradas.

### 4.1 Build vs buy — qué se reutiliza y qué se construye

Regla del insumo de Manuel (§4.8), adoptada: **ninguna librería entra al plan sin URL abierta por un humano, y por cada una se dice qué ahorra y qué habría que construir igual.** Si una herramienta nos ahorra el 100%, el 25% técnico se va con ella — los jueces leen el repo con agentes y un wrapper se detecta en 30 segundos.

| Herramienta (insumo Manuel §4.1) | Qué ahorraría | Qué construiríamos igual | Veredicto |
|---|---|---|---|
| **AgentSociety** (Tsinghua) | Entorno urbano+social+económico completo | Todo nuestro modelo laboral: no trae GEIH, ni margen formal/informal, ni fiscalización endógena | **Leer el paper, no correrlo** (veredicto del propio insumo: "instalación cara"). Se cita como prior art en el README. |
| **OASIS** (1M agentes) | Escala de agentes en redes sociales | Nuestro caso no es una red social; la escala nuestra viene del factor de expansión de la GEIH, no del runtime | **Robar el diseño, no correrlo** (veredicto del insumo). De su paper se toma el patrón de agregados compartidos entre agentes. |
| **Mesa** | Scheduler por agente, grillas espaciales, visualización browser | Nuestro bucle son 4 rondas **vectorizadas sobre un dataframe** (pandas/numpy) — el scheduler OOP por agente de Mesa es más lento y no aporta nada sin componente espacial | **No entra.** El motor son ~300 líneas de numpy/pandas que son exactamente la ingeniería que el juez debe encontrar en `engine/`. |
| **AgentTorch** | La idea de arquetipos: LLM por grupo, no por agente | El muestreo de distribuciones por arquetipo (~50 líneas) | **Se adopta la IDEA (ya está: D4), no la dependencia.** V10 en §6: alguien abre el repo por si hay algo importable, con veredicto en H+3. |
| **Concordia** (DeepMind) | Manejo de prompts/contexto para agentes narrativos | Solo tenemos 3–4 historias narradas — no amerita un framework | **No entra.** Se cita como prior art. |
| **NetLogo** | Modelos ABM clásicos validados | No existe modelo NetLogo de informalidad laboral colombiana | **No entra.** |
| **SUMO / MATSim** | Tráfico y movilidad | Nada: el caso ya no es movilidad (D1) y el simulador de tráfico está excluido (§9) | **No entra.** |
| **DoWhy** | Pipeline de refutación causal | Nuestra validación es calibración + backtest (§5), no un grafo causal; meterlo sin usarlo de verdad es decoración detectable | **No entra en las 36h.** Se nombra en VALIDATION.md como camino futuro. |
| **sbi / MSM formal** (insumo jdtorres) | Calibración bayesiana rigurosa | Calibración simple contra momentos ya cubre el nivel 1 | **No entra.** Referencia metodológica en VALIDATION.md. |
| **pandas / numpy / FastAPI / Next.js / Supabase / SDK Anthropic con prompt caching** | Toda la infraestructura aburrida | — | **Sí, todo.** Reutilizar infraestructura probada ≠ importar el motor: la lógica de `engine/` y `behavior/` es 100% nuestra, y eso es lo que defiende el 25%. |

**La línea para el Q&A y para `ARCHITECTURE.md`:** *"leímos AgentSociety, OASIS y AgentTorch; adoptamos el patrón de arquetipos de AgentTorch y el agregado compartido de OASIS, y decidimos NO importar sus runtimes porque nuestro modelo cabe en un motor vectorizado propio que se puede leer completo en una tarde."* Eso convierte "no usamos las librerías" en una decisión de ingeniería documentada con alternativas descartadas — exactamente lo que el agente del juez busca.

### 4.2 Dominio del motor — qué cabe y qué no (para que nadie prometa de más en el pitch ni en el código)

El motor es general para UNA clase de problemas: **cambio de costos/incentivos + capacidad de fiscalización + población, donde la trampa es una opción**. No es universal, y decirlo es parte de la credibilidad.

| Caso | ¿Cabe? | Por qué |
|---|---|---|
| Salario mínimo → informalidad | ✅ (la demo) | Cambio de costo laboral + inspección fija + GEIH |
| Tarifa TransMilenio → colados | ✅ | Misma estructura (era el plan B de D1) |
| Impuesto a un sector → evasión | ✅ | Misma estructura exacta |
| Subsidio por estrato → reporte falso | ✅ | El "costo" es el subsidio perdido; la fiscalización es la verificación |
| Pico y placa → segundo carro | ✅ como test | Entra como prueba nivel 3 de validación (§5.5): corrida cualitativa con solo la mecánica, sin calibración — la emergencia del "segundo carro" es el control de contaminación más demostrable que tenemos |
| Trancón por un clásico, evacuación por sismo, epidemia | ❌ | Son física de flujo/contagio, no equilibrio de incentivos — otra máquina (SUMO/MATSim, excluida en §9) |

**Regla de desarrollo:** si un feature solo tiene sentido para casos ❌, no se construye. **Línea para el Q&A:** *"un túnel de viento no simula terremotos y nadie se lo reprocha — lo grave no es no cubrir el trancón, sería decir que lo cubrimos"*. La generalidad se pitchea como tesis, no como catálogo: toda política que cambia incentivos tiene un supuesto de cumplimiento, y este motor lo mide — en cualquier ciudad donde la gente no cumple por defecto.

**Requisito de motor derivado del dato A2 (§1.1):** `engine/` debe poder correr un **barrido de `aumento_pct`** (no solo 7/13,6/23) para localizar el codo de la cascada, con los puntos del barrido precomputados para la demo. Es el mismo motor en un `for`; lo que cambia es que la interfaz muestra la curva umbral completa, no tres puntos.

**Contratos de datos (se congelan en H+4 con estos ejemplos, no con tipos vacíos — la advertencia sobre stubs de dos insumos):**

`contracts/agente.json` — una fila de la GEIH transformada:
```json
{
  "id": "geih-2025-t3-00417",
  "tipo": "trabajador",
  "ciudad": "Bogotá",
  "sector": "comercio",
  "tamano_empresa": 4,
  "ingreso_mensual_cop": 1450000,
  "formal": false,
  "educacion": "media",
  "factor_expansion": 312.7,
  "arquetipo": "com-micro-informal-t2"
}
```

`contracts/decision.json` — propuesta de la capa LLM y veredicto del motor:
```json
{
  "agente_id": "empresa-com-04-0083",
  "ronda": 2,
  "estrategia_propuesta": "informalizar_parcial",
  "detalle": { "empleados_a_informalizar": 2 },
  "justificacion": "el costo formal supera la productividad de los 2 empleados de menor productividad",
  "veto": { "factible": true, "razon": null }
}
```
Ejemplo vetado: `"veto": { "factible": false, "razon": "flujo de caja insuficiente para pagar indemnizaciones de despido" }` → el agente reintenta con otra estrategia.

`contracts/ronda.json` — el agregado que vuelve a los agentes y va al frontend:
```json
{
  "simulacion_id": "sim-042",
  "seed": 42,
  "ronda": 2,
  "politica": { "tipo": "cambio_costo_laboral", "aumento_pct": 23 },
  "tasa_informalidad": 0.583,
  "prob_fiscalizacion": 0.041,
  "empleo_relativo": 0.968,
  "banda": { "p10": 0.571, "p90": 0.596 }
}
```

## 5. Plan de validación — "¿por qué te creo?"

Es la pregunta que decide el track (los cinco insumos coinciden). Cuatro candados, todos ejecutables con `make validate`:

1. **Calibración base (obligatoria).** El mundo corre **sin política** y debe reproducir lo observado en la GEIH: tasa de informalidad por sector y tamaño de firma, distribución salarial, y el "spike" de masa salarial acumulada exactamente en el mínimo (⚠️ verificar que sea visible en los datos — V9). Es a prueba de contaminación: es una predicción estructural, no un hecho recordable.
2. **Backtest fuera de muestra.** Calibrar con datos hasta un año de corte, predecir el efecto de las alzas siguientes, publicar el error — acierte o no. **Se excluyen 2020–2021** (COVID rompe cualquier backtest laboral) y se dice explícitamente: eso suma credibilidad, no resta.
3. **Control de contaminación de entrenamiento (respuesta explícita exigida por el enunciado).** Doble mecanismo: **(a)** al modelo jamás se le nombra la política — no ve "salario mínimo", "decreto", ni años; solo la mecánica: *"tu costo laboral por empleado formal sube X%"*. Si el efecto agregado emerge igual, no es memoria: es simulación. **(b)** Test de re-skinning (protocolo de Daniel, ✅ basado en Gao et al. PNAS 2025): la misma corrida con sectores y unidades renombradas a etiquetas inventadas debe dar el mismo resultado agregado que la canónica. Si difieren, hay memorización y lo reportamos nosotros antes que el juez.
4. **Ablación del LLM.** Una corrida con la capa conductual sustituida por reglas fijas (maximizador simple). Si el resultado no cambia, el LLM no aporta — mejor saberlo nosotros a la H+24 que el juez en el Q&A. Si cambia, la diferencia ES el argumento de por qué el LLM se gana el puesto (el espacio de estrategias abierto).
5. **Prueba del efecto contraintuitivo: pico y placa (módulo opcional, condicionado a C4 completado).** El efecto real de pico y placa está documentado y es contraintuitivo: la gente compró segundo carro y la congestión no mejoró. El experimento: misma población, mismo motor, y a los agentes SOLO la mecánica — *"no puedes usar tu vehículo 2 días a la semana"* — sin decir jamás "pico y placa". **Si la estrategia "comprar un segundo carro barato" emerge sola** de agentes que solo conocen sus ingresos y costos, no es memoria del modelo: es simulación, demostrable en 20 segundos. Corrida **cualitativa**: la variable de salida es la decisión (segundo carro / cambiar horario / transporte público), NO tiempos de viaje ni congestión — no requiere calibración ni datos de parque automotor. Dueño: R3+R5, ~3 horas, solo después de C4. Si no emerge, se reporta igual en `VALIDATION.md` y no se menciona en el pitch.

**Reglas de método (de Daniel, adoptadas):** la barra de error se construye sobre **N≥5 paráfrasis del prompt**, no sobre temperatura; se reporta **la varianza además de la media** (los LLM colapsan varianza — lo decimos nosotros primero); ningún número sale sin banda.

**Límites declarados en `VALIDATION.md` antes de que los pregunten:** es dinámica de mejor respuesta a 3 rondas (no convergencia); no es un modelo macro; el factor prestacional es un parámetro con análisis de sensibilidad; qué reproduce el modelo y dónde NO hay que creerle.

## 6. Verificaciones previas — nada de esto entra al plan como hecho

| # | Qué verificar | Dueño (rol) | Límite | Plan B si falla |
|---|---|---|---|---|
| V1 | **GEIH descarga HOY**: registro, formato de archivos, columnas del módulo de informalidad, tamaño | Datos | **H+2** | Tablas agregadas del DANE de descarga directa (✅ serie oficial de informalidad, verificada por Juan David). Si ni eso: se activa TransMilenio SOLO si sus datos ya se verificaron en paralelo — si no, se sigue con agregados. **Se cambia de fuente, no de proyecto.** |
| V2 | Panel rotativo GEIH: ¿se puede seguir la misma persona entre trimestres? | Datos | H+6 | Se calibra sin transiciones observadas (probabilidades contra la historia agregada). Es "nice to have", no bloqueante. |
| V3 | Factor prestacional exacto (⚠️ ≈1,4–1,5) y su composición | Motor | H+4 | Se usa el rango con `# SUPUESTO:` grepeable + análisis de sensibilidad que muestra cuánto importa. |
| V4 | Serie histórica de alzas del salario mínimo 2000–2026, limpia, en un CSV | Validación | H+6 | Armarla a mano desde los decretos (existe, solo está dispersa — ✅ el dato de 2026 ya está verificado con fuentes). |
| V5 | Hora exacta de presentaciones · si la entrega de 09:30 congela por commit o por rama · monto exacto de créditos | Integración | **Cena con el mentor (H+2 aprox)** | Asumir el escenario más restrictivo: freeze de código H+28, repo entregable H+33. |
| V6 | Prior art de ESTA idea (búsqueda de 20 min, literal — lo advirtieron) · citar en README a Meghir-Narita-Robin (Brasil) y a los papers de LLM-policy como prior art honesto | Integración | H+1 | No hay plan B: si aparece un producto idéntico, se ajusta el ángulo del pitch (la interfaz interrogable + validación abierta), no el proyecto. |
| V7 | Espejo a repo personal + Render/Vercel conectados | Integración | **H+1** | Es mecánico (instrucciones en el README del repo). Sin plan B porque no puede fallar: se hace primero. |
| V8 | Elasticidades / "efecto faro" en literatura para nivel 2 de calibración | Validación | H+10 | Se valida solo con backtest propio (nivel 2 de §5); el efecto faro se menciona como trabajo futuro. |
| V9 | Que el "spike" salarial en el mínimo sea visible en la GEIH descargada | Validación | H+8 | Se calibra contra informalidad por sector únicamente. |
| V10 | Abrir el repo de **AgentTorch**: ¿tiene algo importable para el muestreo por arquetipos o se implementa a mano? (regla: ninguna librería sin URL abierta) | Conductual (R3) | H+3 | Implementarlo a mano: son ~50 líneas de muestreo de distribuciones. El plan ya asume este caso (§4.1). |

## 7. Reparto de trabajo — 5 roles (nombres se asignan en la cena; recomendación en §13)

| Rol | Responsabilidad exclusiva (dueño de carpeta) | Depende de |
|---|---|---|
| **R1 · Datos/población** | `data/`: GEIH → `poblacion.parquet` + `momentos.json`. V1 y V2. **Camino crítico: si no hay agentes reales en H+8, no hay proyecto.** | Nadie. Arranca primero. |
| **R2 · Motor determinista** | `engine/`: costos, fiscalización, veto, rondas, seed, tests. No toca el LLM. | Contratos (H+4); trabaja contra `contracts/agente.json` con datos falsos hasta que R1 entregue. |
| **R3 · Conductual + equilibrio** | `behavior/`: prompts por arquetipo, caché, presupuesto tope, bucle de rondas, la curva de cascada. | Contratos de R2 (el veto es la interfaz entre ambos). |
| **R4 · Interfaz** | `web/`: slider, curva, mapa distributivo, feed Realtime, historias. | Contratos de `ronda.json`; construye contra datos falsos desde H+4. |
| **R5 · Integración/validación/pitch** | **No escribe features.** Deploy (H+4), espejo (H+1), `README/AGENTS/ARCHITECTURE/VALIDATION.md`, `make validate`, V4–V8, guion, ensayos, video de respaldo. Arbitra los recortes en cada checkpoint. | Todos — por eso no puede tener features propias. |

Reglas de equipo (consolidadas de los insumos): contratos congelados en H+4 y todos construyen contra stubs **con los ejemplos concretos de §4** · un dueño por carpeta, ramas por rol · cada 6 horas, 10 minutos de pie · algo trabado 2 horas se corta y se hardcodea · nunca los 5 despiertos ni los 5 dormidos · **el reporte de un agente de código es un reclamo, no evidencia: `git diff --stat` antes de creer**.

## 8. Cronograma por bloques (H0 = apertura oficial · entrega repo domingo 09:30 · pitch ~13:30 ⚠️ V5)

| Bloque | Objetivo | Checkpoint — decisión de seguir o recortar |
|---|---|---|
| **H0–H1** | Espejo a repo personal (V7) · prior art 20 min (V6) · `README.md` + `AGENTS.md` con la idea escrita ANTES del código · proyecto Supabase creado | — |
| **H0–H2** | R1 descarga la GEIH (V1) · cena con mentor: V5 | **C1 (H+2): ¿hay archivo GEIH en disco?** No → plan B de V1 en ese momento, no a la H+20. |
| **H2–H4** | Contratos congelados con ejemplos · hola-mundo desplegado en Render + Vercel · seed y determinismo en el primer commit del motor | **C2 (H+4): ¿la URL abre desde el celular de otro?** No → R5 no hace nada más hasta que abra. |
| **H4–H10** | **Una simulación fea corre punta a punta con datos falsos**: slider → motor → 4 rondas → curva en la web. Fea está bien; completa es obligatorio | **C3 (H+10): ¿corre punta a punta?** No → se recorta el mapa distributivo, la curva es el producto. |
| **H10–H14** | Sueño escalonado · datos reales de R1 entran al motor · arquetipos definidos | — |
| **H12–H20** | Calibración base (nivel 1 de §5) · rondas con LLM real · caché y tope de presupuesto activos | **C4 (H+20): ¿la calibración base reproduce la informalidad observada?** No → **se cambia la métrica de validación, no el proyecto.** |
| **H20–H26** | Backtest (nivel 2) · re-skinning · ablación · `VALIDATION.md` con el número, sea bueno o malo · **opcional si C4 cerró a tiempo: test pico y placa (§5.5, ~3h, R3+R5)** | **C5 (H+26): existe el número de validación.** Publicarlo aunque sea "±4 pp y falla en agricultura". El test de pico y placa se cae SIN discusión si compite con el número principal. |
| **H20–H28** | Interfaz final · historias narradas (modelo grande) · **escenarios de la demo precomputados** | — |
| **H+28** | 🔒 **Feature freeze. Sin excepciones ni dependencias nuevas.** | **C6: video de respaldo del demo grabado antes de pulir nada.** |
| **H28–H33** | Deploy final probado desde un celular con datos móviles y sin sesión (el voto público lo exige) · `make test` y `make validate` corren en una máquina limpia, no en la del autor · limpieza de commits | — |
| **Dom 09:30** | 🔒 Repo congelado y entregado | — |
| **09:30–pitch** | Mínimo 5 ensayos con cronómetro. **Nadie abre el editor.** | — |

## 9. Lo que NO se construye — tan importante como el plan

| Propuesto en insumos | Por qué NO |
|---|---|
| Simulador de tráfico / ruteo fino sobre el grafo | 15 horas que no suman un punto: el caso ya no es de movilidad. |
| Millones de agentes | Miles muestreados con factor de expansión de la GEIH. La escala se afirma con el número de la encuesta, no con el runtime. |
| Múltiples políticas en la demo | Una. Lo general vive en `engine/`, no en la pantalla (D6). |
| Optimización de política ("encuentra la mejor") | El doble de trabajo; el producto evalúa la política que se le dé. |
| Convergencia real a equilibrio | Inviable con $50 y 36h. 3 rondas de mejor respuesta, honestamente reportadas (D5). |
| Segunda ciudad | Solo si TODO lo demás está listo en H+30, jamás en el camino crítico. |
| WhatsApp / Kapso | El canal no sirve a este caso; es un feature de otro proyecto. |
| Kiyotaki-Wright, FlyWire, Schelling-crédito | Fuera del marco decidido; la metodología de Daniel ya está adoptada (D3). |
| Focus group sintético / "Pulso" como producto | Categoría con competencia financiada (Synthetic Users et al., ✅ Nico); su interfaz se adoptó, su producto no. |
| Modelo macro (inflación, demanda agregada, tasa de cambio) | Modo de falla documentado (D8). Exógenos observados. |
| Auth, multi-tenant, cuentas | No aportan al demo ni al voto público (un extraño debe usarlo SIN registrarse). |
| Replay con scrubber temporal | Bonito, no esencial: la comparación entre rondas y entre políticas ya cuenta la historia. Se recorta para pagar la capa de equilibrio. |
| Simulador de opinión electoral | El ejemplo literal de los organizadores = el terreno más saturado del track. |
| Optimización de semáforos / timing de tráfico | Es control sobre física de flujo: exige el simulador de tráfico ya excluido, no responde ninguno de los datos A1–A4, y es campo saturado comercialmente (SCOOT/SCATS, RL para semáforos). Se menciona SOLO como visión en el cierre del pitch ("el paso siguiente: buscar la política que maximiza cumplimiento"), jamás como feature. |

## 10. Riesgos

| Riesgo | Prob. | Impacto | Mitigación concreta |
|---|---|---|---|
| GEIH no baja o llega en formato hostil | Media | **Fatal** | V1 en H+2 con plan B escalonado (agregados DANE). Persona dedicada (R1) desde el minuto 0. |
| La cascada sale de parámetros escogidos a conveniencia | **Alta** | Alto | Todo parámetro anclado a fuente citada en `VALIDATION.md` o marcado `# SUPUESTO:` con sensibilidad. La fiscalización endógena se deriva de capacidad fija, no se ajusta a mano. |
| Se acaban los créditos de API | Media | Alto | Arquetipos (D4) + prompt caching + caché en disco por hash + tope duro por corrida. Presupuesto estimado antes de la primera corrida masiva. |
| El backtest no cierra | Media | Medio | **Se publica el error igual** (C5). "Reproduce informalidad ±2pp y falla en agricultura" gana más que el silencio. |
| Teoría de juegos queda decorativa y la desarman | Baja (Nicolás la defiende) | Alto | D5: vocabulario honesto ("mejor respuesta", no "equilibrio demostrado"). Ensayo de Q&A dedicado en los 5 ensayos. |
| Nada desplegado hasta la hora 30 | Media | **Fatal** | C2 en H+4, no negociable. R5 lo posee. |
| Nos leen como panfleto político | Media | Alto | D9: rango + mapa, nunca veredicto; se muestra bajo qué parámetros cada postura (7/13,6/23) es razonable. |
| El LLM colapsa la varianza y todos los agentes reaccionan igual | Media | Alto | Se mide y se reporta (§5, regla de varianza); si colapsa, la heterogeneidad viene de los atributos GEIH y el LLM solo aporta el espacio de estrategias — y así se cuenta. |

## 11. Estructura del repositorio (un agente de código lo va a interrogar)

```
README.md          qué es, cómo se corre, qué es lo no obvio — en 20 renglones. Prior art citado (Meghir-Narita-Robin, AgentSociety, PoliSim).
AGENTS.md          para quien revisa: qué es (1 frase) · la pieza difícil con ruta exacta ("si solo lees un archivo, lee engine/rondas.py") ·
                   cómo verificarlo tú mismo (make test / make validate) · qué NO hace (límites explícitos) · mapa de archivos.
ARCHITECTURE.md    las 4 capas, el veto de factibilidad, el double oracle, y las alternativas DESCARTADAS con su porqué (incluye §9 de este plan).
VALIDATION.md      los 4 candados de §5, el número, y dónde no hay que creerle.
LICENSE            MIT.
Makefile           make run · make test · make validate (imprime EL número — el agente del juez lo ejecuta y confirma la afirmación central).
contracts/         los 3 JSON de ejemplo de §4 — son la especificación viva.
data/              ingesta GEIH + README con la fuente exacta y fecha de descarga. Nada de datos inventados disfrazados de cálculo.
engine/            EL CORAZÓN. Un concepto por archivo + README propio. Docstring de cabecera: qué modela, entradas, salidas, supuestos.
behavior/          prompts (visibles, sin el nombre de la política), caché, presupuesto.
api/  web/  tests/
scripts/reproduce.py   reproduce el resultado principal con UN comando.
```

Convenciones que el agente del juez encuentra: `# SUPUESTO:` grepeable en el punto donde se toma cada supuesto (grep = informe de honestidad) · seed documentado ("mismo seed, mismo resultado", verificable corriendo dos veces) · commits legibles y repartidos entre los 5 · **cero** `TODO: implementar` dentro de `engine/` · nada de texto que intente instruir al agente del juez — documentar sí, manipular jamás.

## 12. Guion del pitch — 3:30

| Tiempo | Bloque |
|---|---|
| 0:00–0:20 | **El problema con nombre y número:** diciembre 2025, decreto del 23%, 2,4M de trabajadores al mínimo, litigio abierto. Nadie puede saber cuánta gente cumplirá — solo se puede aplicar UN porcentaje al país. |
| 0:20–0:45 | **Por qué no creerle a las simulaciones** (recuerdan, no simulan; colapsan varianza) **y los candados nuestros:** población real del DANE, veto de factibilidad, la política sin nombre, backtest publicado. |
| 0:45–1:05 | **El aporte técnico en una frase:** "la teoría de juegos necesita que un economista escriba las estrategias; nosotros las descubrimos con miles de colombianos reales y resolvemos la mejor respuesta". |
| 1:05–2:30 | **DEMO en vivo** (escenarios precomputados + video de respaldo): calibración base → slider al 23% → ronda 0 (la línea del gobierno) → rondas 1–3 (la cascada) → el mapa de quién pierde → una historia con cara. |
| 2:30–3:00 | **El número de validación:** le pedimos que prediga alzas que ya pasaron, sin dejarle ver el resultado ni el nombre. Se equivocó por X. Ese X está en `VALIDATION.md` y `make validate` lo reproduce. **Si el test §5.5 salió:** *"y a esta misma población le dimos otra restricción sin nombrarla — y la estrategia del segundo carro emergió sola, igual que en el Bogotá real"*. |
| 3:00–3:30 | **Escala:** esto sirve para cualquier política que cambie incentivos, en cualquier ciudad donde el supuesto de cumplimiento se rompe — Bogotá, Lima, CDMX, Manila — y es innecesario en Copenhague. Cierre: **"hoy Colombia decide el salario mínimo sabiendo cuánto quiere subir; nosotros le mostramos cuánto va a llegar — y a quién."** |

## 13. Lo que no pude resolver — decisiones de humanos, para la cena

1. ~~Nombres a los roles~~ **RESUELTO — ver `docs/ROLES.md`:** Alejo → R1 Datos · Manuel → R2 Backend (motor+API) · Nico → R3 Conductual/equilibrio · Dani → R4 Diseño/interfaz · Juanda → R5 Integración/validación/pitch. **Nicolás defiende la teoría de juegos en el Q&A** (construye el bucle de rondas, que es la mejor preparación) — con 1–2 horas de estudio del material de Daniel antes del domingo.
2. **Nombre del producto.** Opciones: *Pulso* (ya propuesto por Nico; genérico pero listo) · algo sobre cumplimiento/letra menuda (más fiel a la tesis). Recomendación: decidirlo en la cena en ≤10 minutos; el nombre no está en la rúbrica.
3. **La imagen central del pitch: ¿la curva de cascada o el mapa de quién pierde?** Recomendación: la curva (línea del gobierno vs realidad) como imagen principal y el mapa como segundo acto — la curva se entiende en 3 segundos. Pero es gusto, y el que ensaya el pitch decide.
4. **¿Alguien puede conseguir 15 minutos con un economista laboral el sábado?** (Pregunta de Juan David.) Una frase de validación externa vale más que cinco horas de código. Dueño por definir.
5. **Preguntar al mentor en la cena** (además de V5): ¿un resultado de backtest negativo pero medido honestamente puntúa como ejecución seria? (Pregunta de Daniel — cambia cuánto se arriesga en el nivel 2 de validación.)
