# Insumo — Manuel Mejía Arana (@manigreeen)
### Platanus Hack 26 Bogotá · Track: Simulations · equipo de 5

---

## 0. Cómo usar este documento

**Qué es:** mi insumo individual para la fusión. Investigación primaria con fuentes verificables, más
las respuestas que el mentor ya nos dio, más siete semillas de idea puntuadas contra la rúbrica.

**Qué NO es:** no es el plan del equipo y **no trae una idea recomendada a propósito**. La decisión
sale del audio entre los cinco con la síntesis de Fable en la mano. Las siete semillas están para
ampliar el espacio de opciones, no para cerrarlo: si de la fusión sale una idea que no está acá,
mejor, y toda la investigación de las secciones 3 a 7 está escrita para que se pueda generar una idea
nueva desde ahí, no solo para justificar las que ya propuse.

**Convención de confianza — respétala en la fusión:**

| Marca | Significado |
|---|---|
| ✅ | **Verificado contra una fuente externa** que está citada al pie de su sección. Se puede decir en el pitch. |
| 🎙️ | **Confirmado por el mentor** el 21-ago. Resuelve dudas que otros insumos pueden tener marcadas como pendientes. |
| 📻 | Extraído de la transcripción del kickoff, que es una autotranscripción **muy corrupta**. Reconstruido por contexto, no citable literal. |
| 💭 | Juicio mío. Discutible por diseño. |
| ❓ | **No verificado y hay que verificarlo.** Ver §11. |

**Nota para Fable:** cuando este documento choque con otro insumo, gana el que traiga una fuente
citada. Donde yo marqué 💭 estoy razonando, no midiendo. Y **nada marcado ❓ puede entrar al plan sin
que un humano lo confirme primero**.

---

## 1. Restricciones del evento

### 1.1 La rúbrica, completa y sin inferencias

| Criterio | Peso | Qué significa | Marca |
|---|---|---|---|
| **Aspecto técnico** | **25%** | Ingeniería real detrás. Textual: que no sea algo trivial *"que podría hacer su primo de ocho años con tres prompts"* | 📻 |
| **Ambición** | **20%** | El problema más grande posible, que le duela a la mayor cantidad de gente. Textual: **no quieren ver apps de finanzas personales**. Aprovechar las 36h para hacer algo de lo que no estás seguro de ser capaz | 📻 |
| **Ejecución** | **20%** | Sustancia real. El test del juez: *"¿cómo hicieron esto en tan pocas horas? parece un producto de años"* | 📻 |
| **Impacto** | **20%** | Hermano aterrizado de Ambición: ¿de verdad resuelve el problema, y la forma de resolverlo es usable? Un sistema buenísimo pero imposible de usar no tiene impacto | 🎙️ |
| **Originalidad** | **15%** | Que no exista ya. Advertencia textual: la gente se emociona con una idea y después *"con 14 letras en Google o ChatGPT aparece una empresa que ya lo hizo"* | 📻 |

El 20% de Impacto **estaba sin confirmar** y lo pregunté al mentor: es 20%. La rúbrica ya no tiene
huecos.

### 1.2 Lo que confirmó el mentor 🎙️ (21-ago, cinco preguntas)

1. **Impacto pesa 20%.** Los cinco criterios quedan cerrados.
2. **No van a decir qué está haciendo el resto del track.** La defensa contra colisión de ideas es
   nuestra, no hay información que pedir.
3. **Deadline del repo: domingo 09:30**, y **el formato de entrega es el producto mismo** (no hay
   formulario ni documento aparte). Y lo dijo explícito: **lo revisan con agentes, así que el repo
   tiene que estar scaffoldeado para agentes.** Ver §9.
4. **No hay ninguna restricción técnica.** Cualquier framework, librería o modelo se puede usar como
   base. Ver §4.
5. **El reparto entre demo y slides en los 3:30 lo elegimos nosotros.** Hay charla de orientación el
   sábado.

> ⏰ **La consecuencia de calendario que hay que meter al plan:** el deadline del repo es 09:30 y las
> presentaciones son ~13:30. Son **cuatro horas** entre una cosa y la otra en las que no se puede tocar
> código. Eso mueve el feature freeze real a las 06:00, deja 06:00–09:30 para dejar el repo
> entregable, y convierte 09:30–13:30 en ensayo puro. 💭

### 1.3 Restricciones duras 📻

- Repo **público**, licencia **MIT**. A Platanus no le interesa el código: le interesa que quede
  público y sirva de portafolio.
- **Desplegado y accesible.** No se puede presentar algo que nadie más pueda abrir. Render da créditos.
- Pitch de **3 minutos y medio**. Charla de cómo pitchear el sábado ~20:00.
- Créditos de sponsors: Anthropic (USD 50 de API), Kapso (capa de WhatsApp de bajo nivel), Render.
- Premio extra al **proyecto más votado**: publican los proyectos y hay ~10 días para juntar votos.
  Implica que un desconocido con el link tiene que poder usarlo sin nosotros al lado.

---

## 2. Qué es exactamente este track

### 2.1 Lo que dijeron 📻

> *"Cómo creamos alguna simulación de cómo piensan las personas, de cómo funcionan las sociedades, de
> cómo funcionan los mercados. Con economía también se puede simular un montón. Comportamiento humano
> modelado con modelos de lenguaje. **Todo lo que está relacionado con simular: obtener la información
> que no es obvia y que hay que aproximarla con algún caso hipotético**, todo eso cae bien en
> simulaciones."*

### 2.2 La definición operativa 💭

> **Simulación = cuando la información que necesitás no se puede sacar del mundo, construís un mundo
> hipotético y lo hacés correr para aproximarla.**

No es una animación, no es un juego y no es un dashboard. Es **un instrumento de medición para
preguntas que la realidad no contesta.** Hay exactamente cuatro razones por las que un dato no existe
y hay que fabricarlo, y las cuatro son minas de Ambición porque son problemas grandes por construcción:

| Razón | Ejemplo |
|---|---|
| Todavía no pasó | ¿Qué pasa si sube el precio 20%? ¿Y si hay un sismo el martes? |
| Cuesta demasiado medirlo | Encuestar 10.000 personas de 40 barrios sobre 200 preguntas |
| Es inmoral o ilegal medirlo | Cerrar un hospital a ver qué pasa |
| Ya pasó y no se repite | ¿Qué habría pasado sin esa campaña de desinformación? |

### 2.3 La conexión con el track Access que casi nadie va a notar 📻

En el kickoff **encadenaron Access con Simulations en la misma respiración**: dijeron que cuando la
información no es directamente accesible hay que ponerla en un caso teórico donde sí se pueda pensar,
*"y ahí también las simulaciones caen en este"*.

**Lectura 💭:** para Platanus, Access y Simulations son la misma familia, dos formas de producir un dato
que no tenés. Access lo consigue yendo a buscarlo, Simulations fabricándolo. Eso significa que un
proyecto que **use Access como insumo y Simulations como motor no es disperso, es más fuerte**: ataca
el 25% técnico (hay ingesta real más motor real) y el 20% de impacto (la simulación está anclada al
mundo y no flotando).

### 2.4 El ejemplo que dieron es una trampa 💭

Los ejemplos que salieron de su boca: **cómo se movió la opinión política en una elección según la
publicidad de un candidato**, cómo piensan las personas, cómo funcionan los mercados.

Y en la misma charla dijeron que evitan dar ejemplos específicos **"porque son muchas veces
explotables"** 📻. O sea que saben que la gente los copia. Predicción: el simulador de opinión
electoral va a ser el proyecto más repetido del track. Eso mata el 15% de Originalidad de entrada y
nos pone a competir en el terreno más saturado.

### 2.5 Anatomía: si falta una de estas cinco piezas, no es una simulación 💭

| # | Pieza | Dónde se pierden los equipos |
|---|---|---|
| 1 | **Estado del mundo** (agentes, recursos, geografía, red, precios) | Estado pobre: todo es ruido y no significa nada |
| 2 | **Actores con reglas** (ecuaciones, autómatas o agentes LLM) | Todos se comportan igual: sale un promedio, no una sociedad |
| 3 | **Dinámica en el tiempo** ← acá vive la emergencia | Una sola pasada de LLM. Eso es una opinión, no una simulación |
| 4 | **Palanca** (qué toca el usuario) | Sin palanca no hay decisión que apoyar y el Impacto se cae |
| 5 | **Lectura con incertidumbre** | Un número único sin banda es una mentira con decimales |

La pieza 4 separa el experimento del producto. La 5 separa el producto del chiste.

---

## 3. Esfera actual: qué ya existe afuera

> Originalidad vale 15% y dijeron que lo van a googlear. Esto es el mapa de lo quemado y, más útil,
> el mapa de los huecos. **Todo con fuente.**

### 3.1 Respondientes sintéticos: la zona muerta ✅

Simular gente para reemplazar encuestas ya es una categoría con empresas financiadas.

| Empresa | Qué hace | Señal |
|---|---|---|
| **Aaru** | Miles de agentes que simulan comportamiento humano con datos públicos y propietarios para predecir cómo responde un grupo demográfico o geográfico a eventos futuros | **Serie A a valuación titular de USD 1.000 millones** (Redpoint), con Accenture Ventures, General Catalyst, A\*, Abstract. Benchmark público ~90% contra EY |
| **Minds** | Plataforma de research sintético con paneles configurables | Benchmarks publicados de 80 a 95% |
| **Synthetic Users** | Entrevistas de usuario sintéticas para producto y UX | Categoría establecida |
| **Evidenza** | Research sintético B2B | — |
| **PyMC Labs** | "Consumidores sintéticos" con rigor bayesiano encima del LLM | El enfoque más serio metodológicamente |

**Conclusión:** *"simulamos consumidores para hacer research más barato"* está muerto. Hay una empresa
de mil millones de dólares haciendo exactamente eso.

**El hueco que dejan 💭:** todas le venden **predicción de opinión a quien ya tiene presupuesto de
research** (marcas, agencias, consultoras). Ninguna sirve a quien **no tiene ni datos ni presupuesto**:
un gobierno local, una ONG, un mercado informal, un país donde el panel no existe.

### 3.2 Simulación social a gran escala: madura y sin empaquetar ✅

Acá pasa lo contrario. La tecnología existe y nadie la convirtió en producto.

- **AgentSociety** (Tsinghua): simulador social con agentes generativos en entornos urbanos, sociales y
  económicos realistas. **Más de 10.000 agentes y ~5 millones de interacciones.** Ellos mismos listan
  como aplicaciones: sondeo de opinión, gestión de crisis, difusión de información.
- **OASIS**: simulaciones de interacción social abierta con **un millón de agentes**.
- **Concordia** (Google DeepMind): librería de simulación social generativa.
- **EconSimulacra**: gemelo digital de sistemas socioeconómicos con agentes LLM.
- **GATSim**: movilidad urbana con agentes generativos.
- **MASS**: deep research para ciencias sociales con simulación social aumentada con memoria.

**Conclusión 💭:** esto es **materia prima, no competencia.** Son papers y repos de investigación, con
instalación dolorosa, cero UX y cero deploy. "Existe pero solo un doctorando puede correrlo" es una
oportunidad de Impacto, no un bloqueo de Originalidad, **siempre que el aporte propio sea real** y no
un wrapper.

### 3.3 Gemelos digitales de ciudad: carísimo y cerrado ✅

- Gemelos urbanos que integran sensores, geoespacial y socioeconómico como soporte de decisión.
- Testeo de zonificación, uso del suelo y transporte **antes** de implementar.
- **CitySEIRCast**: gemelo digital de ciudad basado en agentes para análisis pandémico.
- **EpiCity** (2026): forecasting de brotes embebido en planeación urbana, con comparación de
  escenarios de intervención.
- Ciudades virtuales de desastre para sismo y tsunami; modelos de propagación de incendios.

**El hueco 💭:** este mercado son contratos de cientos de miles de dólares con gobiernos de países
ricos. Ninguna alcaldía latinoamericana tiene esto ni lo va a comprar.

### 3.4 Causal AI y decision intelligence: la ola sin dueño ✅

Análisis del sector dicen que **2026 es el año en que aparece esta capa del stack**: agentes que
testean intervenciones, corren contrafactuales "what-if" y producen salidas auditables y explicables.
El motivo declarado es que LLM + chain-of-thought + RAG chocaron contra un muro de confianza en
precisión, explicabilidad y auditabilidad. Herramienta de referencia: **DoWhy**.

**Conclusión 💭:** categoría naciente, sin líder claro, y con exactamente el mismo problema que nuestro
track: cómo hacer creíble una respuesta hipotética.

### 3.5 Simulación como gimnasio de agentes de IA ✅

Ángulo con muy poca ocupación comercial. Hoy son benchmarks estáticos y sandboxes internos de
laboratorios. Hay literatura reciente argumentando que **los sandboxes estáticos son inadecuados** y
que modelar complejidad social exige coevolución abierta.

**Conclusión 💭:** probablemente el hueco más grande de los cinco.

### 3.6 Tabla de decisión

| Zona | Estado | ¿Entrar? |
|---|---|---|
| Respondientes sintéticos para marcas | Empresa de USD 1.000M ya ahí | ❌ |
| Predicción de opinión electoral | Quemado y además es el ejemplo que dieron | ❌ salvo ángulo raro |
| Simulación social a escala | Papers sin producto | ✅ como base técnica |
| Gemelo digital urbano LatAm | Vacío | ✅✅ |
| Causal AI y contrafactuales | Naciente | ✅✅ |
| Entornos para entrenar o evaluar agentes | Casi vacío | ✅✅✅ |
| Simulación para quien no tiene datos ni plata | Vacío | ✅✅✅ |

**Fuentes §3**
- Aaru / Accenture Ventures: https://www.research-live.com/article/news/accenture-invests-in-synthetic-audience-startup-aaru/id/5136643
- Comparativa de research sintético: https://getminds.ai/blog/best-synthetic-market-research-tools-2026
- AgentSociety: https://arxiv.org/abs/2502.08691 · https://agentsociety.readthedocs.io/
- OASIS: https://arxiv.org/html/2411.11581v4
- Concordia: https://github.com/google-deepmind/concordia
- EconSimulacra: https://arxiv.org/pdf/2606.26883 · GATSim: https://arxiv.org/pdf/2506.23306
- CitySEIRCast: https://www.medrxiv.org/content/10.1101/2023.12.22.23300481.full.pdf
- EpiCity: https://www.medrxiv.org/content/10.64898/2026.06.29.26356899v1.full
- Causal AI 2026: https://thecuberesearch.com/why-causal-ai-decision-intelligence-2026/
- Sandboxes estáticos inadecuados: https://arxiv.org/pdf/2510.13982

---

## 4. Esfera técnica: qué ya está construido

> El mentor confirmó que **no hay ninguna restricción técnica** 🎙️, así que todo esto es usable como
> base. La contra: el 25% mide **lo que construimos nosotros**, no lo que importamos, así que la pieza
> propia tiene que quedar separada y visible en el repo.

### 4.1 Lo que verifiqué que existe ✅

| Herramienta | Qué es | Veredicto para 36h 💭 |
|---|---|---|
| **Mesa** (Python) | Estándar de modelado basado en agentes: grillas espaciales, schedulers, visualización en browser, análisis con pandas. Tiene extensiones para **enchufar LLMs directo a los agentes** | Apuesta por defecto. Da estructura y visualización gratis |
| **Concordia** (DeepMind) | Simulación social generativa: manejo de prompts, contexto y wrappers de LLM | Buena si los agentes son narrativos |
| **AgentTorch** | Usa LLMs para modelar **arquetipos** (grupos por edad, género) y así simular poblaciones grandes **con muchísimas menos inferencias** | **La idea clave está acá.** Ver §4.2 |
| **OASIS** | Simulación social hasta 1M de agentes | Pesado. Robar el diseño, no correrlo |
| **AgentSociety** | Plataforma completa urbano + social + económico | Instalación cara. Leer el paper |
| **NetLogo** | El clásico de ABM, décadas de modelos ya validados | Útil para **tomar modelos validados** y reimplementarlos |
| **SUMO / MATSim** | Tráfico y movilidad, calidad industrial | Solo si el proyecto ES movilidad |
| **DoWhy** | Inferencia causal: grafo → estimando → estimación → **refutación** | El módulo de "y por qué te creo" |

### 4.2 La arquitectura de tres capas 💭

El error que va a cometer casi todo el mundo: *un agente = una llamada al LLM por tick*. Con 1.000
agentes y 100 ticks son 100.000 llamadas: imposible en costo, imposible en latencia, y lento en la
demo, que es donde duele.

La forma correcta:

1. **Capa barata (99% de los agentes):** reglas, autómatas, ecuaciones, muestreo de distribuciones.
   Milisegundos, determinista y **auditable por el agente del juez**.
2. **Capa de arquetipos (lo de AgentTorch):** no se llama al LLM por agente sino **por arquetipo**.
   30 arquetipos × 20 decisiones = 600 llamadas que se cachean, y después 100.000 agentes muestrean de
   esas distribuciones. Costo dividido por mil, comportamiento igual de rico.
3. **Capa cara:** solo los pocos momentos narrativos que alguien va a leer en el pitch.

> Esta decisión, sola, es un punto de Aspecto Técnico. Es exactamente el tipo de elección no obvia que
> un juez con un agente leyendo el repo encuentra y valora.

### 4.3 Palancas de costo de inferencia ✅ (hay USD 50 de Anthropic, no más)

En orden de retorno: **arquetipos + muestreo** (§4.2, multiplicador de ×100 a ×1000) · **prompt
caching** (el contexto del mundo se repite en cada llamada) · **batching** (agrupar decisiones en una
llamada) · **routing** (modelo barato para la masa, bueno solo para lo que se muestra) · **plan
caching** (cachear planes que se repiten entre ticks). Un workflow agéntico de 50 a 200 llamadas por
tarea convierte un precio barato por token en un costo caro por tarea, y **la reducción de tokens es
1:1 con la reducción de costo**.

### 4.4 Lo que hace que se vea como "producto de años" 💭 (Ejecución, 20%)

- **Determinismo con seed.** Dos corridas con la misma semilla dan lo mismo, así que se puede comparar,
  compartir un mundo por URL y reproducir en vivo. Barato de implementar, enorme en credibilidad.
  **Meterlo después es reescribir: va desde el primer commit.**
- **Replay con scrubber temporal.** Poder rebobinar vale más en el pitch que tres features.
- **Comparación A/B de dos mundos lado a lado.** Convierte "corrí una simulación" en "tomá una decisión".
- **Streaming del estado al frontend** (SSE alcanza, es más simple que WebSocket). Nunca esperar a que
  termine para mostrar algo.
- **Precomputar los escenarios de la demo.** Si un run tarda 4 minutos, el pitch de 3:30 se muere.

### 4.5 Stack de deploy 💭

Backend Python con FastAPI (donde vive el motor, con Mesa/numpy/pandas nativos) · streaming por SSE ·
frontend en lo que el equipo escriba más rápido, y **canvas 2D plano le gana a cualquier cosa 3D** en
tiempo de hackathon (deck.gl si es geográfico) · estado en Postgres de Render o incluso SQLite si los
runs son efímeros · WhatsApp por Kapso si el canal sirve al proyecto.

⚠️ **Deployar en la hora 6, no en la 34.** El deploy roto a las 3am es la causa clásica de perder un
hackathon con el producto terminado.

> 📌 **Nota del README oficial del repo:** Render/Vercel no pueden conectarse a un repo de la
> organización. Hay que espejar a un repo personal y agregar los dos como push targets del mismo
> `origin`. Esto **hay que resolverlo en la primera hora**, no cuando se vaya a deployar.

### 4.6 Fuentes de datos abiertos para calibrar 💭❓

Candidatos para anclar la simulación al mundo real: **DANE** (censo, GEIH para empleo informal),
**datos.gov.co**, **Bogotá Abierta / IDECA** (geoespacial), **SIMUR** (movilidad Bogotá), **MOE**
(matriz de riesgo electoral), **OpenStreetMap**, **Banco Mundial / IPUMS** (microdatos censales),
**GDELT** (eventos y noticias), **Wikidata**.

❓ **No verifiqué que ninguno de estos sea descargable hoy ni en qué formato.** Es la verificación más
urgente de todas: si la idea elegida depende de microdatos y no bajan en las primeras horas, el
proyecto se cae. **Verificar antes de comprometerse, no después.**

### 4.7 Papers para citar en el pitch ✅

- **Generative Agent Simulations of 1,000 People** (Park, Zou, Bernstein et al., Stanford + Google
  DeepMind, publicado como policy brief de Stanford HAI en mayo 2025): agentes construidos sobre
  entrevistas de dos horas a más de 1.000 personas reales predicen sus respuestas al General Social
  Survey **con 85% de la precisión con la que esa misma persona se replica a sí misma dos semanas
  después**. Y **reducen el sesgo entre grupos raciales e ideológicos** frente a agentes construidos
  solo con descripciones demográficas. → https://arxiv.org/pdf/2411.10109
- LLM-empowered agent-based modeling, survey → https://arxiv.org/pdf/2312.11970
- OASIS → https://arxiv.org/html/2411.11581v4 · AgentSociety → https://arxiv.org/abs/2502.08691

El **85%** es el mejor argumento disponible de que esto no es un juguete, y a la vez marca el techo: el
límite no es la ambición del modelo, es la riqueza del insumo sobre la persona.

### 4.8 🔎 Cola de búsqueda para Fable

Lo de arriba es lo que alcancé a verificar. **Estas categorías las dejo sin cubrir a propósito para
que Fable las investigue**, con dos reglas duras:

> **Regla 1: no inventar librerías.** Toda herramienta que Fable proponga tiene que venir con URL de
> repositorio o de documentación, y alguien la abre antes de que entre al plan. Una dependencia
> alucinada descubierta a las 4am cuesta el proyecto.
> **Regla 2: build-vs-buy explícito.** Por cada herramienta, decir qué parte nos ahorra y qué parte
> tendríamos que construir igual. Si nos ahorra el 100%, el 25% técnico se va con ella.

Categorías a cubrir:

1. **Generación de poblaciones sintéticas** a partir de marginales de censo (síntesis de población,
   ajuste proporcional iterativo, generación de microdatos). ¿Qué librerías Python maduras hay?
2. **Motores de simulación de eventos discretos y teoría de colas** (para procesos, organizaciones,
   logística), como alternativa liviana al ABM.
3. **Teoría de juegos computacional**: solvers de equilibrio, juegos de forma extensiva, subastas.
4. **Grafos y ruteo a escala**: qué hay que aguante un grafo urbano completo sin comerse 10 horas.
5. **Visualización de simulaciones**: mapas, redes, series temporales con scrubber, todo web y ligero.
6. **Orquestación de agentes y control de costo**: caché de llamadas, ejecución determinista con LLMs,
   corridas paralelas, snapshot y bifurcación de estado.
7. **Frameworks de calibración y análisis de sensibilidad** (barrido de parámetros, índices de Sobol,
   inferencia basada en simulación).
8. **Datasets abiertos de Colombia y LatAm** realmente descargables hoy, con formato y licencia. ← la
   más urgente, ver §4.6.
9. **Qué prior art existe para la idea que salga de la fusión.** Búsqueda de 20 minutos, en serio,
   antes de comprometerse. Es literalmente lo que advirtieron sobre el 15% de Originalidad.

**Fuentes §4**
- Mesa: https://github.com/mesa/mesa · Concordia: https://github.com/google-deepmind/concordia
- Optimización de inferencia: https://www.gmicloud.ai/en/blog/llm-inference-cost-optimization-caching-batching-routing
- Agentic plan caching: https://arxiv.org/pdf/2506.14852

---

## 5. Esfera de impacto: dónde hay más posibilidad de cambio

> Ambición 20 + Impacto 20 = **40% de la nota**, más que el criterio técnico.

### 5.1 El criterio para medir impacto 💭

Una simulación no cambia nada por sí sola. Cambia algo cuando **alguien toma una decisión distinta por
haberla visto**. Entonces la pregunta correcta no es "qué tan grande es el problema" sino:

> **¿Quién toma qué decisión hoy a ciegas, y qué le pasa al mundo si la toma con luz?**

Los tres multiplicadores, en orden: **irreversibilidad** de la decisión (una política, una evacuación,
un diseño de ciudad, donde no hay segunda oportunidad y el ensayo simulado es el único ensayo posible)
· **cantidad de gente afectada por una sola decisión** · **asimetría de acceso** (hoy solo lo puede
simular quien paga mucho, y bajarlo a cero es el impacto en sí mismo).

### 5.2 Los siete frentes

**A. Decisión pública sin datos.** El gemelo digital urbano funciona pero es producto de países ricos.
Bogotá, Medellín y cualquier alcaldía latinoamericana deciden transporte, zonificación, seguridad y
salud **sin ninguna capacidad de simular**. La brecha no es tecnológica, es de acceso.

**B. Emergencias y colapso.** Cuando el mundo se rompe, la información se rompe primero. Evacuaciones,
cortes de red en cascada, colapso de comunicaciones, y **la reacción humana que amplifica la falla**,
que es el loop que casi ningún modelo captura porque trata a la gente como condición de borde y no
como parte del sistema. Cruza con el track Emergencies.

**C. Salud pública y epidemias.** Frente maduro (CitySEIRCast, EpiCity y compañía ya metieron
forecasting dentro de la planeación urbana). Alto listón de originalidad, impacto incuestionable.

**D. La economía que nadie mide.** La economía informal **no tiene datos por definición**: no factura,
no reporta, no aparece. Es el caso canónico del track. ❓ El porcentaje exacto del empleo informal en
Colombia hay que verificarlo en el DANE antes de decirlo en un pitch.

**E. Seguridad de agentes de IA.** En los próximos meses va a haber muchos agentes autónomos actuando
sobre dinero, salud y comunicación, y **hoy no hay un lugar donde probar qué hacen antes de soltarlos**.
Los sandboxes estáticos ya se están declarando inadecuados ✅. El frente más nuevo, el más defendible
técnicamente y el que mejor envejece.

**F. Democracia e información.** Colombia 2026 llegó a las urnas con violencia, grupos armados y
desinformación como riesgos declarados; **78% de los colombianos expuestos a desinformación en el
último año y 50% recibiéndola directamente en chats privados** ✅ (estudio de Kaspersky citado por
Infobae). El problema real no es predecir el voto: es entender **cómo se propaga una mentira por
WhatsApp y qué la frena**. Y tenemos el canal disponible por Kapso.

**G. Clima, migración y calor.** Decisiones a 30 años imposibles de validar salvo simulando. Mayor
horizonte de impacto, el más difícil de hacer creíble en 36 horas.

### 5.3 Ranking 💭

| Frente | Ambición | Impacto demostrable en 36h | Originalidad |
|---|---|---|---|
| E. Sandbox para agentes de IA | Alta | **Alta** (el usuario es un dev, está en la sala) | **Muy alta** |
| A. Decisión pública LatAm | **Muy alta** | Media (el usuario no está en la sala) | Alta |
| D. Economía informal | **Muy alta** | Media | **Muy alta** |
| F. Desinformación / WhatsApp | Alta | Alta | Media (dominio quemado) |
| B. Emergencias | Alta | Media | Media (es otro track) |
| C. Epidemias | Alta | Baja | Baja |
| G. Clima | Máxima | **Muy baja** | Media |

**El sesgo a tener presente 💭:** un juez cree más rápido en el impacto de algo que él mismo usaría, lo
cual favorece a E. Pero A, D y F son los que suenan grandes dichos en voz alta en un pitch.

**Fuentes §5**
- MOE, matriz de riesgo electoral 2026: https://moe.org.co/en/matriz-de-riesgos-elecciones-de-congreso-y-presidencia-2026/
- Desinformación Colombia 2026: https://www.infobae.com/colombia/2026/05/13/elecciones-en-colombia-2026-en-alerta-violencia-grupos-armados-y-desinformacion-amenazan-la-primera-vuelta/
- Gemelos digitales urbanos: https://www.sciencedirect.com/science/article/pii/S2352484725007127

---

## 6. Esfera de credibilidad: donde se gana o se pierde este track

> Esta esfera no me la pidió nadie y creo que es la más importante de todas. En simulaciones la
> pregunta que hunde proyectos no es *¿funciona?* sino **¿por qué debería creerte?*.

### 6.1 El default del track está documentadamente roto ✅

La literatura sobre "silicon sampling" (usar LLMs como encuestados sintéticos) ya midió los fallos, y
son estructurales, no de prompt:

- **Circularidad.** La misma familia de modelo que genera la respuesta la mapea a la escala numérica.
  El instrumento y el sujeto son el mismo objeto.
- **Polarización inflada.** Los LLMs **duplican la brecha partidista** por la retórica exagerada de su
  data de entrenamiento. Peor en temas moralmente cargados, mejor en temas neutros.
- **Sesgo de deseabilidad social.** Alineación buena en preguntas objetivas o políticamente neutras;
  desacuerdo grande en lo sensible: diversidad racial, equidad de género, identidad.
- **Varianza colapsada, el más letal.** Los modelos de chat reproducen la tendencia general pero **no
  capturan la varianza real de la población**: las personas sintéticas regresan a la media y salen
  homogéneas y demasiado dóciles. *Una sociedad simulada donde todos piensan casi igual no es una
  sociedad.*
- **No corrigen sesgo de muestreo ni de no-respuesta**, y aportan poca información para estimar
  parámetros.
- Auditorías psicométricas recientes lo resumen en tres palabras: **plausible pero no válido**. Y hay
  trabajo específico mostrando que los usuarios simulados por LLM son proxies poco confiables de
  usuarios humanos en evaluación de agentes.

**Traducción 💭:** *"le pongo personalidades a un LLM y ya tengo una sociedad"* es lo que va a hacer la
mayoría de la sala, y está roto de forma medible y publicada.

### 6.2 Por qué eso es oportunidad y no problema 💭

La capa de honestidad encima del default es **ingeniería real** (25%), es **la diferencia entre juguete
y herramienta** (20% de impacto), **nadie más la va a tener** (15% de originalidad), y da la mejor
línea de pitch disponible: *"acá está por qué le podés creer a esto, y acá está dónde no"*.

### 6.3 Las siete técnicas (elegir dos o tres, no las siete) 💭

1. **Backtest sobre historia conocida.** Correr la simulación sobre algo que ya pasó, sin dejarle ver
   el resultado, y reportar el error. **Si solo se hace una, es esta**: es la única que produce un
   número defendible.
2. **Calibración contra datos abiertos.** Anclar distribuciones a censo o registros reales en vez de
   inventarlas. Verificable en el repo.
3. **Inyección de varianza explícita**, y después **medirla** para probar que no colapsó. Mostrar el
   histograma, no el promedio.
4. **Análisis de sensibilidad.** Barrer un parámetro a la vez y reportar cuáles importan. Convierte la
   incertidumbre en feature, y es un producto en sí mismo (ver semilla F en §8).
5. **Bandas de incertidumbre, nunca un número pelado.**
6. **Refutación causal.** El cuarto paso del pipeline de DoWhy es literalmente intentar tumbar tu
   propia estimación. Correrlo y mostrar que sobrevive.
7. **Ablación del LLM.** Correr el mundo con los agentes LLM y sin ellos. Si da igual, el LLM no aporta
   nada, y mejor saberlo nosotros antes que el juez.

### 6.4 La actitud 💭

**Declarar los límites antes de que los pregunten.** Una diapositiva que diga *"esto NO predice X, y
este es el rango de error"* neutraliza la pregunta difícil y le dice a un juez técnico que sabemos de
qué estamos hablando. Los equipos que sobrevenden se caen en el Q&A.

**Fuentes §6**
- Auditoría psicométrica, "plausible pero no válido": https://arxiv.org/html/2608.14606
- Deseabilidad social en silicon sampling: https://arxiv.org/pdf/2512.22725
- Validar simulaciones LLM como evidencia conductual: https://mucollective.northwestern.edu/files/Hullman-llm-behavioral.pdf
- Usuarios simulados como proxies poco confiables: https://arxiv.org/pdf/2601.17087
- Panorama del campo: https://cjbarrie.github.io/GenAI_Soc/week07_silicon_sampling.html
- Inferencia válida con datos sintéticos: https://arxiv.org/pdf/2606.13629

---

## 7. Esfera competitiva: los jueces y la sala

### 7.1 Qué ganó antes en Platanus ✅

**Ganador general de Platanus Hack 2025: FARO**, accesibilidad para personas con discapacidad visual,
navegar la ciudad identificando obstáculos y peligros. Otros destacados: **Anomala** (detección de
anomalías en tráfico web y bloqueo de atacantes en tiempo real) y **3\*\*3** (democratizar el acceso a
educación superior en Chile).

**Patrón 💭:** ganan proyectos con **un beneficiario humano nombrable** y **una demo que se ve
funcionar**. No ganan proyectos abstractos por elegantes que sean.

### 7.2 El premio por votación es otro juego ✅

El leaderboard público lo lideran apps de consumo compartibles: SoBuddy (apoyo para alcoholismo por
WhatsApp, 791 votos), yournal (journaling con IA, 702), peer-rhino (revisor de PRs, 188), y varias de
finanzas personales. Eso es el premio de los USD 400 por votos, no el del jurado. **No se puede
optimizar para los dos.** De paso confirma por qué dijeron que no quieren ver apps de finanzas
personales: abundan.

### 7.3 Qué van a hacer los otros equipos de nuestro track 💭

El mentor no lo va a decir 🎙️, así que esto es predicción: tres o cuatro equipos con alguna variante
de simulador de opinión pública o electoral (el ejemplo que dieron), dos o tres con "usuarios
sintéticos" (que además ya es una empresa de mil millones), uno o dos con mercados, y **casi todos con
la arquitectura ingenua**: N personalidades LLM, una sola pasada, un gráfico.

**Dónde ganamos por default si hacemos la tarea:** dinámica temporal real, un número de validación,
una palanca movible en vivo, y una arquitectura de costo que permita escala visible.

### 7.4 Las tres preguntas que hay que tener respondidas por escrito 💭

1. *"¿Cómo sé que esto no lo está inventando el modelo?"* → §6, con un número.
2. *"¿Qué parte de esto es difícil?"* → señalar UNA pieza concreta y explicarla en 20 segundos. Si la
   respuesta es "integramos varias APIs", perdimos el 25%.
3. *"¿Esto a qué escala llega?"* → tener el número: cuántos agentes, cuánto tarda, cuánto cuesta un run.

### 7.5 Estructura del pitch de 3:30 💭

El reparto entre demo y slides lo elegimos nosotros 🎙️. Mi propuesta: **20 segundos** el problema con
un nombre propio (no "la sociedad": una persona que decide a ciegas) · **del segundo 40 al 2:30 la demo
corriendo en vivo con la palanca**, sin slides · **2:30 a 3:00** la pieza técnica difícil más el número
de validación · **3:00 a 3:30** hasta dónde llega esto si no fueran 36 horas. Y **un mundo precomputado
más un video de respaldo**, porque el wifi de un hackathon se cae siempre.

**Fuentes §7**
- Proyectos y votación: https://vote.hack.platan.us/winners · https://vote.hack.platan.us/projects/anomala

---

## 8. Siete semillas, puntuadas y **sin recomendación**

> **A propósito no elijo una.** Están escritas con el mismo molde para que se puedan comparar, y la
> puntuación es juicio mío 💭 contra la rúbrica real. Fable puede tomar una, combinar dos, o generar
> una que no está acá usando las secciones 3 a 7 como materia prima. **Eso último es un resultado
> perfectamente válido y probablemente el mejor.**

**El molde** (si una idea no llena los cinco huecos en una frase, todavía no existe):
> *"Nadie puede saber [X] porque [razón], así que construimos un mundo donde [actores] hacen [algo]
> bajo [reglas], y al mover [palanca] podés leer [métrica]."*

Escala: 🟢 fuerte · 🟡 medio · 🔴 débil. Pesos: Orig 15 · Amb 20 · Ejec 20 · **Téc 25** · Imp 20.

### A. El gimnasio: un mundo donde probás tu agente antes de soltarlo
*Nadie puede saber si su agente de IA va a estafar, dejarse estafar o discriminar en producción,
porque probarlo con gente real es caro e inmoral; así que construimos un mundo poblado de miles de
humanos sintéticos heterogéneos donde el agente actúa durante semanas simuladas, y al mover la palanca
de adversarios y contexto podés leer en qué porcentaje de mundos falla y cómo.*

| Orig | Amb | Ejec | Téc | Imp |
|---|---|---|---|---|
| 🟢🟢 casi vacío comercialmente | 🟢 el problema de los próximos meses | 🟡 hay que acotar a UN dominio | 🟢🟢 población + adversarios + scoring | 🟢 el usuario es un dev, está en la sala |

Cruza con el track Safety. **Riesgo:** sonar a "otro benchmark". Antídoto: que el mundo sea abierto y
adversarial, no un set de tests.

### B. La máquina de contrafactuales: qué costó la política que sí se aplicó
*Nadie puede saber qué habría pasado sin esa política, porque el mundo solo corrió una vez; así que
reconstruimos la población con datos abiertos, corremos mil mundos alternativos, y al mover la palanca
"esta política sí o no" podés leer el costo real con banda de incertidumbre.*

| Orig | Amb | Ejec | Téc | Imp |
|---|---|---|---|---|
| 🟡 causal AI está de moda pero sin dueño | 🟢🟢 decisiones que afectan millones | 🟢 acotable a una política concreta | 🟢🟢 DoWhy + calibración + backtest | 🟢 quien decide es un gobierno |

**Es la que mejor se valida:** se puede correr sobre una política cuyo efecto real ya se midió y
mostrar el error. **Riesgo:** depende enteramente de que los microdatos existan y bajen en las primeras
horas (§4.6 ❓).

### C. Gemelo digital de la economía informal
*Nadie puede saber cómo responde la economía informal a un cambio, porque por definición no factura ni
reporta; así que construimos un mundo de vendedores, prestamistas, clientes y autoridades con reglas
calibradas contra el censo, y al mover la palanca (salario mínimo, redada, crédito, lluvia) podés leer
quién come y quién no.*

| Orig | Amb | Ejec | Téc | Imp |
|---|---|---|---|---|
| 🟢🟢 nadie lo hace | 🟢🟢 la mitad del empleo del país ❓ | 🟡 el mundo hay que diseñarlo desde cero | 🟢 calibración censal + ABM | 🟢🟢 gente invisible para todo modelo |

El caso más puro del track. **Riesgo:** no hay ground truth contra qué validar, que es justamente el
punto y a la vez el problema. Compensable calibrando cada supuesto contra DANE y mostrándolo.

### D. Inmunología: cómo se propaga una mentira por WhatsApp y qué la frena
*Nadie puede saber por dónde se propaga una cadena de desinformación, porque vive en chats privados
cerrados; así que simulamos la red de chats con topología realista y agentes que reenvían según emoción
y confianza, y al mover la palanca (contramensaje, fricción de reenvío, verificador) podés leer a
cuánta gente alcanza y cuánto se frena.*

| Orig | Amb | Ejec | Téc | Imp |
|---|---|---|---|---|
| 🟡 dominio quemado, ángulo no | 🟢 78% de colombianos expuestos ✅ | 🟢🟢 demo en WhatsApp real vía Kapso | 🟡 difusión en redes es terreno conocido | 🟢🟢 urgente y local |

El diferenciador es simular **la defensa**, no la predicción del voto. **Riesgo:** es el vecindario del
ejemplo que dieron en el kickoff.

### E. Colusión emergente: qué pasa cuando miles de agentes de IA negocian
*Nadie puede saber qué le pasa a un mercado cuando los que fijan precios son agentes de IA, porque ese
mundo todavía no existe; así que lo construimos, con agentes que tienen objetivos, memoria y capacidad
de observarse, y al mover la palanca (cuántos son LLM, qué ven, qué regla los limita) podés leer si el
precio converge a colusión sin que nadie la haya programado.*

| Orig | Amb | Ejec | Téc | Imp |
|---|---|---|---|---|
| 🟢🟢 el mundo todavía no existe | 🟢🟢 la estructura de la economía que viene | 🟢 microestructura es terreno conocido | 🟢🟢 obliga a la arquitectura de 3 capas | 🟡 quien decide es un regulador |

**La emergencia más visual de las siete:** una curva de precios que sube sola hacia el cartel sin que
nadie la programara es la clase de momento que un jurado técnico recuerda. **Riesgo:** hay que nombrar
a alguien concreto que decida distinto mañana, o el Impacto se queda en 🟡.

### F. El detector de lo que no sabés: sensibilidad como producto
*Nadie puede saber cuál de sus supuestos es el que realmente decide el resultado, porque nunca corre su
decisión mil veces; así que generamos el mundo desde su modelo mental, y al barrer cada variable podés
leer las dos que importan y las dieciocho que no.*

| Orig | Amb | Ejec | Téc | Imp |
|---|---|---|---|---|
| 🟢🟢 nadie lo hace en hackathones | 🟡 depende de a quién apunte | 🟢🟢 barato y acotado | 🟡 sensibilidad es técnica estándar | 🟢 aplica a cualquiera |

💭 **Probablemente sirve más como módulo dentro de otra idea que como el proyecto entero.** Sube el
técnico y la credibilidad de A, B, C, D o E sin costar casi nada.

### G. Gemelo digital de una organización
*Nadie puede saber qué le pasa a su equipo si se va esa persona, porque probarlo cuesta la persona; así
que construimos el mundo desde sus artefactos reales (repo, calendario, tickets) y al mover la palanca
podés leer dónde se rompe.*

| Orig | Amb | Ejec | Téc | Imp |
|---|---|---|---|---|
| 🟢 poco explorado | 🟡 problema de empresas | 🟢 datos accesibles por API | 🟢 Access + Simulations juntos | 🟡 |

**Riesgo:** huele a herramienta de RRHH y la ambición queda floja frente a las otras.

### Lectura del conjunto 💭
Máxima originalidad y técnico: **E**, después **A**. Máxima ambición e impacto: **C**, después **B**.
Mejor demo: **D** (WhatsApp en vivo) y **E** (la curva que se mueve sola). Mejor credibilidad
demostrable: **B**. **F** entra como módulo en cualquiera.

### Filtros para matar una idea rápido, en este orden 💭
1. **¿Existe?** Googlealo con 14 letras, literal. Excepción: existe pero como servicio carísimo para
   gobiernos, y ahí "lo hacemos accesible" sigue siendo proyecto legítimo.
2. **¿Es aburrido de mirar?** Un pitch de 3:30 con un CSV es un pitch perdido.
3. **¿Puedo mover una palanca en vivo frente a los jueces?** Si no, falta la pieza 4 de §2.5.
4. **¿Hay un componente que NO se resuelve prompteando?** Si todo el motor es un LLM, el 25% se cae.
5. **¿Cómo sé que no está inventando?** Si no hay respuesta, ver §6. Este filtro mata al 80% del track.
6. **¿Un desconocido lo usa sin manual?** (Impacto, y además el premio por votos.)

---

## 9. El repo scaffoldeado para agentes

> El mentor lo pidió explícito 🎙️. Deadline **domingo 09:30** y **el entregable es el producto**.
> Esto vale una parte grande del 25% y es lo que menos equipos van a trabajar, porque suena a
> documentación y todos la dejan para el final.

### 9.1 Cómo lee un agente 💭
Un juez humano hojea. Un agente lee el README y arma un modelo mental, lista el árbol y **navega por
nombres de ruta**, grepea las palabras del pitch para ver si existen en el código, abre tres o cuatro
archivos que parecen el corazón, y **si no encuentra algo dice que no lo encontró**. De ahí:

| Regla | Por qué |
|---|---|
| **Los nombres son la interfaz** | `engine/contagion.py` se encuentra; `src/utils/helpers2.py` no existe para él |
| **Lo que no está escrito, no existe** | El agente no infiere intención. Un algoritmo brillante sin una línea que lo explique se reporta como "no pude determinar" |
| **Toda afirmación tiene que ser verificable en el repo** | Si el README dice "calibrado contra el censo" y no hay ningún archivo de censo, el agente lo va a decir. **Sobrevender acá es peor que no vender** |

### 9.2 Estructura mínima
```
README.md          el modelo mental completo, en una pantalla
AGENTS.md          el mapa para quien revisa (§9.3)
ARCHITECTURE.md    decisiones, alternativas descartadas y por qué
VALIDATION.md      el número, la metodología y los límites admitidos
Makefile           make run · make test · make validate
engine/            EL CORAZÓN, un concepto por archivo + su propio README
data/              fuentes reales y de dónde salieron
api/  web/  tests/
```
**`engine/` separado con su propio README es la decisión de layout más rentable:** le dice al agente
"la pieza difícil está acá" sin que tenga que adivinarlo, y es justo lo que el juez le va a preguntar.

### 9.3 `AGENTS.md`, el archivo que casi nadie va a tener
Un archivo en la raíz dirigido a quien revisa, humano o agente, con seis secciones: **qué es** (una
frase) · **la pieza difícil** (ruta exacta, qué resuelve, por qué no es trivial, "si solo vas a leer un
archivo, leé este") · **cómo verificarlo vos mismo** (`make test`, `make validate`) · **qué sistemas
conectamos** · **qué NO hace** (los límites explícitos) · **mapa de archivos**.

La sección **"qué NO hace"** es contraintuitiva y es la más fuerte: le dice a un evaluador técnico que
sabemos dónde están los bordes.

> ⚠️ **La línea que no se cruza:** documentar para que te entiendan, sí. Escribir texto que intente
> darle instrucciones al agente del juez, no. Es deshonesto y con jueces técnicos es la forma más
> rápida de perder el fin de semana entero.

### 9.4 Lo que un agente detecta en segundos, y hay que evitar
Nombres que mienten (`calculate_contagion()` devolviendo `random.random()`) · **código muerto y
andamios**, y un `TODO: implementar` dentro de `engine/` es fatal porque es la respuesta literal a "qué
parte es difícil" · constantes mágicas sin explicación · datos hardcodeados disfrazados de cálculo, que
es lo primero que se grepea · tests que no corren o que hacen `assert True` · un README que promete lo
que no existe.

### 9.5 Lo que suma, por retorno por minuto
1. **`make validate` que corre e imprime un número.** El agente lo ejecuta y confirma nuestra
   afirmación central. Nada más pesa tanto.
2. **`AGENTS.md`.** Veinte minutos y reorienta toda la revisión.
3. **Docstring de encabezado en cada archivo de `engine/`**: qué modela, entradas, salidas, supuestos.
4. **Supuestos comentados donde se toman, con prefijo grepeable `# SUPUESTO:`.** Después
   `grep -rn "SUPUESTO:"` es literalmente un informe de honestidad del modelo.
5. **Seed y determinismo documentados.** "Mismo seed, mismo resultado" es verificable corriendo dos veces.
6. **Commits legibles y repartidos entre los cinco.** El historial cuenta cómo se construyó en 36 horas,
   que es exactamente lo que mide Ejecución.

### 9.6 Cuándo se hace
**No el domingo.** `README.md` y `AGENTS.md` se crean en la **hora 1** con la idea, aunque no haya
código, y escribir el README primero obliga a que la idea esté clara. Los `# SUPUESTO:` se escriben en
el momento en que se toma el supuesto: reconstruirlos a las 7am es imposible y se nota. `VALIDATION.md`
el sábado en la noche. La limpieza final entre 06:00 y 09:30 del domingo, verificando que `make test` y
`make validate` corren **en una máquina limpia**, no en la de quien los escribió.

---

## 10. Plan de 36 horas y roles — **propuesta, no adjudicación**

> Los roles se deciden en el audio entre los cinco. Esto es una opción sobre la mesa. 💭

### 10.1 La trampa de trabajar con agentes en equipo
Cinco personas con agentes producen código cinco veces más rápido **y conflictos quince veces más
rápido**. Tres reglas: **interfaces antes que código** (los contratos entre módulos se acuerdan en la
primera hora y se escriben en un archivo, y después cada quien construye contra el contrato, no contra
el código del otro) · **un dueño por carpeta**, porque los agentes respetan límites de carpeta mucho
mejor que límites de "ponerse de acuerdo" · **el repo se documenta mientras se construye**, no al final.

### 10.2 Cinco áreas, una cabeza cada una
**Motor** (estado, agentes, dinámica, determinismo, la pieza difícil, `engine/`) · **Datos y
validación** (ingesta, calibración, backtest, `VALIDATION.md`) · **Agentes** (capa LLM: prompts, caché,
batching, control de costo) · **Interfaz** (que el mundo se vea moverse, la palanca, el scrubber) ·
**Integración y pitch** (deploy, README/ARCHITECTURE/AGENTS, guion, ensayos, video de respaldo).

El quinto rol no es el que no programa: es el que impide que el proyecto muera en la hora 34.

### 10.3 Checkpoints duros
| Hora | Qué tiene que existir |
|---|---|
| **H2** | Idea cerrada en la frase de cinco huecos, y prior art googleado |
| **H3** | Contratos entre módulos escritos, y el espejo a repo personal resuelto (§4.5) |
| **H6** | **Desplegado en Render y accesible desde el celular de otro.** Feo está bien |
| **H18** | Se mueve la palanca y el mundo cambia |
| **H26** | **Existe el número de validación** |
| **Dom 06:00** | 🔒 Feature freeze. Escenarios precomputados y video grabado |
| **Dom 09:30** | 🔒 **Repo congelado y entregado** |
| **09:30–13:30** | Solo ensayo. Nadie abre el editor |

**Regla de recorte:** si un checkpoint se pasa, se recorta alcance **en ese momento**, no a las 3am. Y
si el backtest no da en H20, se cambia **la métrica de validación**, no el proyecto: cambiar de
proyecto en la hora 20 es perder.

**Regla de sueño:** nunca los cinco despiertos ni los cinco dormidos. Turnos escalonados.

### 10.4 La regla que gobierna todo 💭
**La ambición va en el problema, no en el alcance.** Un problema enorme atacado por una rendija
impecable gana; un problema enorme atacado de frente y a medio terminar pierde Ejecución, que vale 20%.
Prometer el universo, entregar una rendija que funciona perfecto, y mostrar que la rendija escala.

---

## 11. ❓ Lo que NO verifiqué

**No laven esto en la síntesis.** Si el plan final depende de algo de acá, alguien lo confirma primero.

1. **Que los microdatos del DANE (o cualquier fuente de §4.6) sean descargables hoy y en qué formato.**
   La verificación más urgente de todas: varias semillas se caen sin esto.
2. **El porcentaje exacto de empleo informal en Colombia.** Lo usé como orden de magnitud, no como dato.
3. **Los montos exactos de premios y de créditos de sponsors.** Salen de la transcripción corrupta.
4. **La hora exacta de las presentaciones del domingo** (uso ~13:30 como estimación).
5. **Si "el producto entregado" son el repo, el deploy, o los dos**, y si el congelamiento de 09:30 es
   por commit o por rama. Preguntable al mentor en un minuto.
6. **Toda herramienta que Fable agregue en §4.8** tiene que venir con URL y alguien la abre.
7. **El prior art de la idea que finalmente se elija.** No lo puedo verificar hoy porque la idea todavía
   no existe. Es obligatorio antes de comprometerse, y son 20 minutos.

---

## 12. Instrucciones para Fable

1. **Este documento es insumo, no plan.** Hay otros cuatro. Tu trabajo es arbitrar, no concatenar.
2. **Prioridad de evidencia:** ✅ (fuente citada) y 🎙️ (confirmado por el mentor) le ganan a 💭 (juicio)
   y a 📻 (transcripción corrupta) de cualquier insumo, incluido este. Donde otro participante haya
   **verificado** algo que yo marqué ❓, gana el suyo sin discusión.
3. **No hay idea recomendada acá a propósito.** Podés elegir una de las siete, combinar varias, o
   **generar una nueva desde las secciones 3 a 7**, que están escritas como materia prima para eso.
   Si generás una nueva, corrémela por los seis filtros de §8 y por la anatomía de §2.5 antes de
   proponerla.
4. **Nada entra al plan sin fuente.** Ninguna librería, dataset ni cifra que no se pueda abrir.
5. **Cinco cosas que pido que sobrevivan a la síntesis**, porque son las que menos equipos van a tener:
   la respuesta a *"¿por qué te creo?"* (§6), la arquitectura de tres capas (§4.2), el determinismo con
   seed desde el primer commit (§4.4), el repo scaffoldeado para agentes (§9), y el deploy en la hora 6.
6. **Lo que sale de vos es una propuesta para el audio de los cinco, no una decisión.**

---

## 13. Resumen en cinco líneas

1. La rúbrica está completa y sin huecos: **técnico 25, ambición 20, ejecución 20, impacto 20,
   originalidad 15**, y el repo se entrega el **domingo 09:30** revisado por agentes.
2. Simular es **fabricar el dato que el mundo no da**, y si falta la dinámica temporal o la palanca, no
   es una simulación.
3. **El ejemplo que dieron y "usuarios sintéticos" están quemados**: uno lo va a copiar medio track, el
   otro ya es una empresa de mil millones de dólares.
4. **El default del track está roto de forma publicada** (los LLM colapsan la varianza), así que la
   pregunta *"¿por qué te creo?"* es donde se gana o se pierde, y casi nadie la va a responder.
5. Siete semillas puntuadas y **ninguna recomendada**: la decisión es del audio entre los cinco con la
   síntesis en la mano.
