# Insumo — Simulación de políticas públicas con agentes + teoría de juegos
### PlatanusHack 26 Bogotá · Track: Simulations · Equipo de 5

---

## 0. Cómo usar este documento

**Qué es:** uno de varios insumos que se van a fusionar para producir el plan definitivo. No es el plan. Está escrito para que un modelo de síntesis pueda arbitrar entre este documento y los de los demás participantes sin perder el *porqué* de cada decisión.

**Qué NO es:** no es una investigación primaria. No se verificó ninguna fuente de datos externa mientras se escribió. Todo lo marcado ⚠️ tiene que confirmarlo un humano antes de que el plan final lo dé por hecho.

**Convención de confianza — respétenla en la fusión:**

| Marca | Significado |
|---|---|
| ✅ | Extraído del transcript del kickoff. Confiable salvo error de transcripción (la autotranscripción es de baja calidad). |
| ⚠️ | Plausible pero **no verificado**. Si el plan final depende de esto, alguien tiene que confirmarlo primero. |
| 💭 | Juicio / opinión. Discutible por diseño. Si otro insumo lo contradice con evidencia, gana el otro. |

**Nota para el modelo de síntesis:** cuando este documento choque con otro insumo, prioriza el que traiga **evidencia verificada** sobre el que traiga razonamiento. Este documento es mayormente razonamiento. Y si algo aquí está marcado ⚠️ y otro participante ya lo verificó, su versión reemplaza la mía sin discusión.

---

## 1. Restricciones del evento

### Rúbrica ✅ — es lo único que decide

| Criterio | Peso | Textual |
|---|---|---|
| Aspecto técnico | **25%** | Ingeniería real. *"Que no lo pueda hacer tu primo de 8 años con tres prompts"* |
| Ambición | **20%** | Problema grande, mucha gente. Dijeron explícitamente: **no apps de finanzas personales** |
| Ejecución | **20%** | Que **no** parezca hecho en 36 horas |
| Impacto | **20%** | Que resuelva de verdad y sea fácil de usar |
| Originalidad | **15%** | Que no exista ya. **Van a googlearlo** |

### Restricciones duras ✅

- Repo **público**, licencia **MIT**
- **Desplegado y accesible** — nada de localhost en el pitch. Render da créditos
- Pitch de **3.5 minutos**, domingo en la tarde ⚠️ (hora exacta por confirmar)
- Charla de cómo pitchear el sábado; cena con mentor la primera noche
- Premio por **voto público** ~10 días después → un extraño con el link tiene que poder usarlo sin nosotros

### Dato táctico crítico ✅

> *"Los jueces tienen una copia de sus repositorios en sus computadores y van a estar con agentes haciéndole preguntas al código."*

**El repo es parte del pitch y hay un lector no-humano al que se le puede escribir.** Ver §11.

### Premios y créditos ⚠️ (montos del transcript, confirmar con organizadores)

$3.000 USDC total · ~$400 por track · **$1.200 + viaje a la final en Chile (noviembre)** al mejor general · $400 al más votado.
Créditos: Anthropic ~$50 API por persona · WhatsApp API de bajo nivel · Render.

### El track ✅

> *"Cómo piensan las personas, cómo funcionan las sociedades, cómo funcionan los mercados. Obtener información que no es obvia y hay que aproximarla con algún caso hipotético."*

El organizador dijo que Simulations es el track con más potencial de generar presentaciones interesantes. **Eso implica que va a estar concurrido.**

---

## 2. La decisión del equipo

Ya está tomada y este documento la asume:

1. **Simulación de políticas públicas y su efecto sobre agentes.**
2. **Motor general, demo sobre una ciudad concreta.**
3. **Incorporar teoría de juegos.**
4. **Explorar Colombia como nicho.**

Las secciones siguientes son la versión más fuerte de esa decisión, no una alternativa a ella.

---

## 3. Diagnóstico crudo de la decisión 💭

**Escogieron la idea más concurrida del track.** Modelación de política pública con agentes es un campo con 30 años (agent-based modeling, MATSim, UrbanSim, NetLogo) y ya hay literatura de agentes LLM aplicados a política.

**Consecuencia práctica:** en originalidad (15%) arrancan abajo y no hay nada que hacer al respecto. Acéptenlo y jueguen a ganar los otros 85%, donde técnico + ejecución + impacto suman 65% y se ganan con oficio.

**Lo que compra de vuelta parte de la originalidad** no es la idea sino tres detalles de craft, descritos abajo: el veto de factibilidad (§6), el control de contaminación (§8) y el descubrimiento de estrategias con LLM (§7).

### La palabra peligrosa: "general" 💭

Generalidad ≠ ambición. En 36 horas, generalidad = superficialidad repartida en más superficie, y el criterio de ejecución es literalmente *"que no parezca hecho en 36 horas"*.

**Regla propuesta:** general en el adaptador de datos, estrecho en la pantalla. Cargar una segunda ciudad es **meta de la hora 30**, nunca bloqueante. Si entra en el camino crítico, no se entrega ninguna de las dos.

---

## 4. La tesis del producto

No pitchear *"simulamos políticas públicas"*. Eso lo hace la econometría desde hace décadas, mejor.

**Dos reencuadres, y ambos deben sobrevivir la fusión:**

### 4.1 De agregado a distribución

Un modelo econométrico estima el efecto **promedio**. Lo que solo una simulación con agentes heterogéneos puede dar es la **distribución**: quién específicamente gana y quién pierde. Y esa es la pregunta política que hunde reformas.

> No es *"¿funciona la política?"*. Es **"¿a quién le cae encima?"**

### 4.2 El supuesto de cumplimiento

> **Toda política pública tiene un supuesto de cumplimiento que nadie modela.** La econometría estima el efecto *si la gente cumple*. Nosotros estimamos **cuánta gente cumple en equilibrio**, que casi nunca es lo que el diseñador supuso.

Esto convierte el producto en: **"tu política no falla por mala, falla porque asumiste un cumplimiento que no existe."**

Es información no obvia que hay que aproximar con un caso hipotético — la definición literal del track.

---

## 5. Las trampas del track (crítico — no perder en la fusión)

### 5.1 Contaminación de entrenamiento ⚠️→💭 **el punto más importante de todo el documento**

**Cualquier validación contra un evento anterior al corte de entrenamiento del modelo es teatro.** Si le piden a una población sintética que "reaccione" a la reforma tributaria de 2016, no está simulando — está recordando y disfrazándolo. Un juez técnico lo tumba con una pregunta: *"¿cómo controlaron contaminación de entrenamiento?"*

Esto invalidó una versión anterior de esta propuesta y **cualquier plan que salga de la fusión tiene que responderlo explícitamente.** Ver §8 para la solución.

### 5.2 Simulaciones no falsables

Una simulación produce un resultado plausible **siempre**, acierte o no. Si el output no puede estar equivocado, no es información: es contenido. El organizador dedicó parte del keynote al concepto de *slop* — no es casualidad que este track sea donde más fácil se produce.

### 5.3 Predicción disfrazada de simulación

Si el sistema solo escupe un número y no permite preguntar *"¿y si cambio esto?"*, es un clasificador con pasos extra. **El contrafactual es lo que distingue simulación de predicción, y es el producto.**

### 5.4 La visualización preciosa sobre 200 líneas de prompts

Los jueces leen el repo con agentes. Se nota en 30 segundos.

---

## 6. Arquitectura propuesta 💭

Tres capas. **La relación entre ellas es el aporte, no las capas.**

```
┌─────────────────────────────────────────────────────┐
│ CAPA 3 · EQUILIBRIO (teoría de juegos)              │
│ Resuelve el nivel de cumplimiento en equilibrio     │
│ sobre las estrategias descubiertas por la capa 2    │
└──────────────┬──────────────────────────────────────┘
               │ devuelve el agregado a los agentes
               ▼
┌─────────────────────────────────────────────────────┐
│ CAPA 2 · CONDUCTUAL (LLM)                           │
│ Dado el cambio de costos, ¿cómo se adapta ESTA      │
│ persona? Espacio de adaptación abierto              │
└──────────────┬──────────────────────────────────────┘
               │ propone adaptación
               ▼ ◄──── VETO DE FACTIBILIDAD ────┐
┌─────────────────────────────────────────────────────┐
│ CAPA 1 · FÍSICA (determinista, sin LLM)             │
│ Agentes con datos reales sobre la red real.         │
│ Costos, tiempos, restricciones presupuestales.      │
│ Con seed. Testeada.                                 │
└─────────────────────────────────────────────────────┘
```

**Capa 1 — física, determinista, sin LLM.** Agentes construidos desde datos reales (§10), no inventados. Con seed y tests. Es lo que hace que esto sea ingeniería y no prompting.

**Capa 2 — conductual, con LLM.** El espacio de adaptación es abierto y ningún modelo econométrico lo enumera: comprar un segundo carro, mudarse, informalizarse, mototaxi, cambiar de horario, pedirle el carro a un primo. Aquí el LLM se gana el puesto.

**El pegamento: la capa física VETA a la capa LLM.** El agente propone una adaptación; el motor verifica si es factible (¿le alcanza la plata? ¿esa ruta existe? ¿ese horario tiene servicio?). Si no, se rechaza y reintenta.

> Ese bucle es la respuesta a la única pregunta que un juez técnico va a hacer: **"¿cómo evitan que el LLM alucine comportamiento?"** Va explícito en `ARCHITECTURE.md`.

**Capa 3 — equilibrio.** Ver §7.

---

## 7. Teoría de juegos: la única versión que no es decoración 💭

### El riesgo

*"Además usamos teoría de juegos"* como adorno se detecta en el Q&A y **cuesta credibilidad en vez de sumarla**. Teoría de juegos y simulación con agentes son dos respuestas distintas a la misma pregunta; pegarlas por sonar sofisticado se nota.

### Por qué aquí sí es obligatoria

En un diseño sin teoría de juegos, la política **le cae encima** a los agentes y ellos reaccionan. Eso es un problema de decisión, no un juego. Ninguna política real funciona así: la política **cambia el juego** y los actores anticipan.

- Pico y placa → segundo carro
- Subsidio por estrato → reporte falso de dirección
- Impuesto → informalización
- Multa → cálculo de si vale la pena pagarla

### La división de labores que es el aporte técnico real

**Debilidad de la teoría de juegos clásica:** alguien tiene que escribir las estrategias a mano. El economista enumera `{cumplir, evadir}`. La gente real inventa estrategias que el modelador nunca imaginó.

**Debilidad de los agentes LLM:** no tienen concepto de equilibrio. Corren hacia adelante y producen anécdotas.

**Juntos:**

1. Los agentes LLM, con perfiles de personas reales, **descubren el espacio de estrategias**. Nadie lo escribió.
2. Se construyen los pagos sobre las estrategias descubiertas.
3. Se resuelve el equilibrio.
4. **El equilibrio vuelve a los agentes** para que respondan a lo que todos los demás están haciendo, no al mundo vacío.
5. Iterar.

Estructuralmente es un *double oracle* con el LLM como generador de estrategias. Ningún juez puede llamar eso un prompt wrapper.

> **Frase de pitch:** *"La teoría de juegos necesita que un economista escriba las estrategias. Nosotros las descubrimos con miles de bogotanos reales, y después resolvemos el equilibrio."*

### El mecanismo que hace el demo dramático 💭

Un solo bucle de retroalimentación, barato de implementar, con resultado contraintuitivo:

> **La capacidad de fiscalización es fija.** Si más gente evade, la probabilidad de que te agarren baja. Si baja, evadir se vuelve más atractivo. **Cascada.**

El gobierno proyecta con una línea recta. La realidad es una curva que se dispara. **Esa gráfica —la línea plana del modelo oficial contra la curva que trepa— probablemente es mejor imagen de pitch que el mapa.**

### El costo honesto, y la versión mínima viable 💭

Iterar a equilibrio = correr la simulación N veces = N× costo de API y N× tiempo. Con ~$50 de créditos y 36 horas, **no van a converger a un equilibrio real.** No lo pretendan.

**Lo que sí es construible:**

- **Ronda 0:** agentes responden ingenuamente. *Este es el número que el gobierno usaría.*
- **Rondas 1–3:** cada agente ve el agregado (*"el 30% está evadiendo, la probabilidad de multa bajó a 4%"*) y vuelve a decidir.
- Se muestran las 4 rondas. **La brecha entre ronda 0 y ronda 3 es el producto entero.**

Y en `VALIDATION.md` se escribe la verdad: *"esto es dinámica de mejor respuesta a 3 rondas, no una prueba de existencia de equilibrio."* Un juez técnico respeta esa honestidad mucho más que una afirmación falsa de convergencia, que se tumba en 20 segundos.

### ⛔ Condición de corte

**Si nadie en el equipo puede explicar *mejor respuesta* y *equilibrio de Nash* en frío durante el Q&A, no metan teoría de juegos.** Es peor tenerla y que los desarmen que no tenerla. Esta decisión se toma mirándose a la cara, no por orgullo.

---

## 8. Validación sin contaminación 💭 — el diferenciador

Tres niveles, de más honesto a más espectacular. **Hacer al menos el 1.**

**Nivel 1 · Calibración base.** Correr la simulación **sin política** y verificar que reproduce lo observado (repartición modal, tiempos promedio, tasa base de evasión). Es a prueba de contaminación porque es una predicción física, no un hecho recordado. Es el piso mínimo y casi nadie lo va a hacer.

**Nivel 2 · Elasticidad contra literatura.** Si suben la tarifa 10% y la elasticidad simulada cae dentro del rango publicado para ciudades latinoamericanas, están calibrados. ⚠️ Requiere encontrar la referencia.

**Nivel 3 · La prueba del efecto contraintuitivo — mejor momento de pitch.** Correr una política cuyo efecto real se conoce, **sin decirle nunca al agente cómo se llama**. El agente solo ve la mecánica (*"no puedes usar tu vehículo los martes"*), jamás la etiqueta *"pico y placa"*. Si el efecto agregado emerge de todas formas, eso no es memoria del modelo: es simulación. Y se puede demostrar.

> Ese control de contaminación es un párrafo de 20 segundos que **ningún otro equipo va a tener**. Es la pieza de mayor retorno de todo el documento.

---

## 9. ¿Existe esto en Colombia? ¿Colombia como nicho?

### 9.1 Lo que existe ⚠️ (nombres de memoria, verificar antes de citarlos en el pitch)

Colombia tiene capacidad seria de modelación de política pública: **Fedesarrollo**, **DNP** (con Sinergia para evaluación), **Banco de la República**, **CEDE de los Andes**, y la **Secretaría Distrital de Movilidad** con sus modelos de transporte. Hay modelos de equilibrio general computable y microsimulación corriendo hoy.

> ⛔ **Nunca pitchear "nadie hace esto en Colombia".** Es falso y es la forma más rápida de perder credibilidad si un juez viene de ese mundo.

### 9.2 El hueco real 💭

> Esa capacidad existe pero está **encerrada**. Un modelo CGE toma meses, cuesta un equipo de economistas, produce un PDF, y **no se le puede preguntar nada**. Un concejal, un periodista, una ONG o un ciudadano no tienen forma de interrogarlo.

El producto no es modelar. Es **hacer interrogable lo que hoy solo se puede leer**. Meses → minutos. PDF → contrafactual. Economista → cualquiera.

### 9.3 Colombia como nicho: demo sí, posicionamiento no 💭

*"Nuestro nicho es Colombia"* le baja puntos al 20% de ambición, ante un jurado que pidió impacto en la mayor cantidad de personas posible — y que además es chileno, con final regional en Chile.

**El reencuadre que convierte la limitación en tesis:**

> **Los modelos de política pública se diseñaron en países donde la gente cumple.** Aquí la informalidad ronda el 55–60% ⚠️ y la fiscalización es débil. Nuestra simulación trata la evasión como **estrategia racional, no como ruido** — y por eso sirve en Bogotá, Lima, Ciudad de México y Manila, y es innecesaria en Copenhague.

Eso no es un nicho: es una tesis sobre por qué el producto existe.

**Formulación final:** el foso es el método, la demo es Colombia, el mercado es cualquier ciudad donde el supuesto de cumplimiento se rompe — que es la mayoría del mundo.

---

## 10. Caso de demo recomendado 💭

### Recomendación: evasión de pago en TransMilenio ("los colados")

Encaja en todas las casillas:

- **Es literalmente un juego de inspección**, el caso de libro de texto. La estructura formal ya existe, no hay que inventarla.
- **El bucle de fiscalización es el mecanismo real:** subir la tarifa para tapar el déficit aumenta la evasión, que aumenta el déficit. Espiral de muerte. Fenómeno documentado; simularlo es un demo espectacular.
- **Hay datos públicos** ⚠️ de pasajeros y estimaciones de evasión que TransMilenio publica. **Verificar cifras exactas en la primera hora.**
- **El LLM aporta lo que la econometría no puede:** *por qué* evade cada quien — no me alcanza / es injusto / todo el mundo lo hace / la multa no es nada — y cada motivación responde distinto a cada política. Poner más inspectores no le hace nada al que evade por injusticia percibida.
- **Los jueces son chilenos.** La evasión en el transporte público de Santiago es uno de los problemas de política más conocidos de Chile ⚠️. Van a entender el problema en tres segundos y van a saber que es difícil. Eso vale muchísimo en 3.5 minutos.

### Alternativas

| Caso | A favor | En contra |
|---|---|---|
| **Pico y placa** | Permite la prueba del nivel 3 (§8) — el efecto de segundo carro está documentado | Menos estructura de juego de inspección; datos de parque automotor más difíciles ⚠️ |
| **Cobro por congestión** | Nadie sabe la respuesta, debate vivo en Bogotá, efecto distributivo brutal, alto valor de "información no obvia" | Sin política vigente = sin datos observados = **imposible validar** |
| **Subsidios por estrato** | Muy colombiano, distributivo puro, datos de estratificación disponibles ⚠️ | Menos visual; el juego de misreporting es más difícil de demostrar |

**Combinación óptima si alcanza el tiempo:** TransMilenio para vender + pico y placa para validar (nivel 3). La segunda valida, la primera vende.

### El motor sigue siendo general

Cualquier política = un cambio de pagos + una capacidad de fiscalización + una población. TransMilenio es la demo, no el producto.

---

## 11. Datos a verificar en la primera hora ⚠️

**Nada de esto está verificado. Es la tarea #1 del equipo, antes de escribir una línea de código.**

| Fuente | Para qué | Riesgo |
|---|---|---|
| **Encuesta de Movilidad de Bogotá** (Secretaría de Movilidad) | Agentes con viajes reales: origen, destino, modo, hora, demografía | **Camino crítico.** ¿Hay microdatos descargables o solo el informe en PDF? |
| **OSM / OSMnx** | Grafo vial de Bogotá | Bajo. Esto sí es seguro y se resuelve en minutos |
| **GTFS TransMilenio / SITP** | Red y horarios de transporte público | ¿Existe y está actualizado? |
| **Estratificación por manzana** | Ingreso proxy, efecto distributivo | Portal de datos abiertos de Bogotá |
| **Cifras de evasión de TransMilenio** | Calibración del nivel 1 | Puede estar solo en informes de gestión |

> **Regla:** si a la hora 2 no hay un archivo de datos en disco, **se cambia de política, no de proyecto.** Hay versiones que corren solo con OSM + estratificación.

**La pieza que hace o rompe el proyecto** es la que da agentes que **no inventaron**. Es la diferencia entre un proyecto serio y slop con mapa.

---

## 12. Recortes explícitos de alcance 💭

Decidir ahora, no a la hora 20. Lo que **NO** se va a construir:

- ⛔ **Un simulador de tráfico.** Tiempos de viaje aproximados o precalculados. Un modelo de congestión real se come 15 horas y no suma un punto.
- ⛔ **Millones de agentes.** Miles, muestreados representativamente. Y solo los que la política toca llaman al LLM.
- ⛔ **Múltiples políticas en el demo.** Una. Lo general vive en el código, no en la pantalla.
- ⛔ **Optimización de política.** No buscar la mejor política; evaluar la que se le dé. Eso es el doble de trabajo.
- ⛔ **Convergencia real a equilibrio.** 3 rondas de mejor respuesta, honestamente reportadas.

**Si entra teoría de juegos, algo tiene que salir.** Recomendación: el ruteo fino sobre el grafo.

---

## 13. Costos y ruteo de modelos 💭

Con ~$50 por persona ⚠️, esto es una decisión de ingeniería real y además queda bien en el repo:

- **Haiku** para la población completa (miles de agentes × 4 rondas).
- **Un modelo grande** solo para el puñado de agentes que se muestran en narrativa durante el pitch.
- **Prompt caching:** el estado del mundo es idéntico entre miles de agentes → cachear el prefijo compartido baja el costo un orden de magnitud. Es la diferencia entre correr el demo cinco veces y correrlo una.
- **Caché de respuestas en disco** con hash del prompt. En un hackathon se corre la misma simulación decenas de veces; pagar dos veces por lo mismo es regalar presupuesto.
- **Presupuesto tope por corrida**, con corte duro. Nadie quiere descubrir a la hora 30 que se acabaron los créditos.

---

## 14. Equipo y tiempos 💭

### La verdad sobre 5 personas

**No es 1/5 cada uno. Nunca lo es.** El paralelismo en hackathones no se rompe por capacidad sino por integración. Cinco personas sobre una base de código de 36 horas es una de más — **a menos que la quinta no escriba features.**

| # | Rol | Dueño de |
|---|---|---|
| 1 | **Datos / población** | Encuesta → agentes con viajes reales. **Camino crítico.** Si no está a la hora 8, no hay proyecto |
| 2 | **Motor físico** | Grafo, ruteo, costos, tiempos, veto de factibilidad. Determinista, con tests. No toca el LLM |
| 3 | **Capa conductual + equilibrio** | Prompts, bucle de rondas, caché, control de costo, la curva de cascada |
| 4 | **Interfaz** | El mapa y la gráfica de rondas. Antes/después. Slider de política. Es el 20% de impacto |
| 5 | **Integración + validación + pitch** | Deploy desde la hora 3, `VALIDATION.md`, números de calibración, guion, ensayos, video de respaldo |

**Riesgo de dependencias:** 3 necesita 1 y 2. 4 necesita todo. → **A la hora 2 se congelan los contratos entre módulos y todos construyen contra stubs con datos falsos.** El que espere a que otro termine, perdió su turno.

⚠️ **Advertencia sobre stubs:** un stub no es neutral — contesta en silencio preguntas de diseño que nadie tomó, y toda la cadena se ve sana mientras produce el artefacto equivocado. Definan el contrato **con un ejemplo concreto del dato real**, no con un tipo vacío.

### Línea de tiempo

| Ventana | Objetivo |
|---|---|
| **H0–H2** (cena con mentor) | Decidir, no explorar. Una política con nombre. Búsqueda de prior art de 20 min. Escribir la frase del pitch **antes** del código |
| **H2–H4** | Contratos entre módulos. **Deploy de un hola-mundo a Render YA** (hora 3, no hora 34). Seeds y determinismo desde el primer commit |
| **H4–H10** | Meta: **una simulación fea corre punta a punta con datos falsos.** Fea está bien; completa es obligatorio |
| **H10–H14** | Sueño escalonado. Nunca los 5 despiertos ni los 5 dormidos. El rol 5 arbitra |
| **H12–H20** | Calibración base (§8 nivel 1) + primeras rondas de equilibrio. **Checkpoint duro H20:** si no calibra, se cambia la métrica de validación, **no** el proyecto |
| **H20–H28** | Interfaz y narrativa. **Feature freeze H28**, sin excepciones ni dependencias nuevas |
| **H28–H32** | Deploy final probado desde un celular en datos móviles sin sesión iniciada (el voto público lo exige). Docs. **Video de respaldo del demo** — el wifi de un hackathon se cae siempre |
| **H32–H36** | Mínimo 5 ensayos con cronómetro |

### Reglas de equipo

1. Feature freeze en H28, aunque duela.
2. El demo grabado existe **antes** de que alguien pula nada.
3. Ramas por rol. Nadie toca el módulo de otro sin avisar.
4. Cada 6 horas, 10 minutos de pie: qué corre, qué está roto, qué necesito de ustedes.
5. Si algo lleva 2 horas trabado, se corta y se hardcodea.
6. **El reporte de un agente de código es un reclamo, no evidencia.** Verifiquen con `git diff --stat` antes de creer que algo se hizo.

---

## 15. El repo es parte del pitch 💭

Los jueces cargan el repo y lo interrogan con agentes ✅. Hay un lector no-humano optimizable y casi ningún equipo lo va a hacer:

- **`README.md`** — en los primeros 20 renglones: qué es, cómo se corre, qué es lo no obvio.
- **`ARCHITECTURE.md`** — flujo de datos, decisiones de diseño **y las alternativas descartadas con su porqué**. Aquí va el veto de factibilidad (§6) y el double oracle (§7). Es donde el agente-juez encuentra la respuesta a *"¿esto tiene ingeniería real?"*.
- **`VALIDATION.md`** — metodología, números, el control de contaminación (§8), y **las limitaciones admitidas**. Admitir límites sube la credibilidad técnica.
- **Tests sobre el núcleo determinista.** Es la prueba más barata de que hay ingeniería.
- **Commits legibles y repartidos entre los 5.** Se nota quién trabajó.

---

## 16. Estructura del pitch (3.5 min) 💭

| Tiempo | Contenido |
|---|---|
| 0:00–0:25 | El problema. Una política real, un número real, una pregunta que hoy nadie puede responder |
| 0:25–0:45 | Por qué las simulaciones no son creíbles — y por qué la nuestra sí (contaminación, falsabilidad) |
| 0:45–1:05 | El aporte: el LLM descubre las estrategias, la teoría de juegos resuelve el equilibrio |
| 1:05–2:35 | **Demo.** Calibración base → política → la curva de cascada → el mapa de quién pierde |
| 2:35–3:05 | El contrafactual: cambiamos un parámetro, cambia quién paga |
| 3:05–3:20 | Escala: cualquier ciudad donde el supuesto de cumplimiento se rompe |

**Regla:** 3.5 minutos alcanza para ~6 frases y una demo. Todo lo demás sobra.

---

## 17. Registro de riesgos

| Riesgo | Prob. | Impacto | Mitigación |
|---|---|---|---|
| Los microdatos de movilidad no existen o no se descargan | Media | **Fatal** | Verificar en H0–H2. Plan B: versión con solo OSM + estratificación |
| Teoría de juegos queda decorativa y la desarman en Q&A | Media | Alto | Condición de corte §7. Si nadie la defiende, se elimina |
| La cascada se produce por parámetros escogidos a conveniencia | **Alta** | Alto | Anclar parámetros a fuentes publicadas y **citarlas en `VALIDATION.md`** |
| Se acaban los créditos de API | Media | Alto | Haiku + prompt caching + caché en disco + tope por corrida (§13) |
| Nada desplegado hasta la hora 34 | Media | **Fatal** | Deploy en hora 3, no negociable |
| Alcance: 3 capas en 36 horas | **Alta** | Alto | Recortes de §12 decididos antes de codear |
| Un juez conoce Fedesarrollo/DNP y detecta una afirmación falsa | Baja | Alto | Nunca decir "no existe en Colombia" (§9.1) |

---

## 18. ⚠️ Afirmaciones NO verificadas — no las laven en la síntesis

**Esta sección existe para que el plan final no convierta suposiciones en hechos.** Todo lo siguiente salió de razonamiento o memoria, sin verificar contra ninguna fuente:

1. Que la **Encuesta de Movilidad de Bogotá** tiene microdatos públicos descargables con diarios de viaje individuales.
2. Que **TransMilenio publica** estimaciones de evasión con granularidad usable. **No se citó ninguna cifra concreta a propósito.**
3. Que existe **GTFS público y actualizado** de TransMilenio/SITP.
4. Que la informalidad laboral en Colombia ronda **55–60%**.
5. Que la evasión en el transporte de Santiago es un problema de política notorio en Chile — base del argumento de que los jueces lo reconocerán.
6. Los **montos de premios y créditos** (§1) salen de una autotranscripción de baja calidad.
7. La **hora exacta** de las presentaciones del domingo.
8. Que las instituciones nombradas en §9.1 hacen hoy el tipo específico de modelación descrita.
9. Que existen **elasticidades tarifarias publicadas** para ciudades latinoamericanas utilizables como referencia de calibración.

> Cada punto necesita un humano con un navegador. Varios se resuelven en 10 minutos. **Ninguno debe entrar al plan final sin verificar.**

---

## 19. Decisiones abiertas — que las resuelva la fusión

1. **¿Qué política concreta va en el demo?** Una, con nombre. (Recomendación: TransMilenio para vender + pico y placa para validar.)
2. **¿Entra teoría de juegos?** Depende exclusivamente de si alguien la puede defender en el Q&A.
3. **¿Qué se cae del alcance para que quepa la tercera capa?** (Recomendación: el modelo de congestión fino.)
4. **¿De dónde salen los parámetros de la cascada?** Sin respuesta a esto, el mecanismo es un truco elegante.
5. **¿Cuál es la métrica de calibración base** — repartición modal, tiempo promedio, tasa de evasión, todas?
6. **¿Quién toma cada rol, y quién es el 5 que no escribe features?**
7. **¿Segunda ciudad: sí o no?** (Recomendación: meta de H30, jamás bloqueante.)

---

## 20. Resumen en cinco líneas

1. Simulador de política pública que responde **"¿a quién le cae encima?"**, no *"¿funciona?"*.
2. Su diferenciador es que modela el **cumplimiento en equilibrio**, que es el supuesto que toda política tiene y nadie modela.
3. Técnicamente: capa física determinista que **vetea** a una capa LLM que **descubre estrategias**, sobre las cuales la teoría de juegos resuelve el equilibrio.
4. Se valida contra lo observado **sin decirle nunca al modelo el nombre de la política** — control de contaminación que ningún otro equipo va a tener.
5. Demo en Bogotá con gente real; tesis para cualquier ciudad donde el supuesto de cumplimiento se rompe.
