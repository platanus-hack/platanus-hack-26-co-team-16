# PlatanusHack 26 Bogotá — Track: Simulations
## Brainstorm + plan crudo (equipo de 5)

> Fuente: `docs/historia/transcript-kickoff.md` (autotranscripción del kickoff, calidad baja — verificar todo dato duro con los organizadores).

---

## 1. Las reglas del juego (extraídas del kickoff)

**Formato**: 36 horas. Pitch de **3.5 minutos** el domingo en la tarde. Charla de "cómo pitchear" el sábado. Cena con el mentor asignado la primera noche para aterrizar la idea.

**Rúbrica (esto es lo único que decide)**:

| Criterio | Peso | Qué significa textualmente |
|---|---|---|
| Aspecto técnico | **25%** | Que haya ingeniería real detrás. "Que no lo pueda hacer tu primo de 8 años con tres prompts". |
| Ambición | **20%** | Problema grande, mucha gente. Dijeron explícitamente: **no queremos apps de finanzas personales**. Arriésguense a algo que no están seguros de poder hacer. |
| Ejecución | **20%** | Que NO parezca hecho en 36 horas. Sustancia, no cáscara. |
| Impacto | **20%** | Que de verdad resuelva el problema y sea fácil de usar. Una idea buena con UX imposible no tiene impacto. |
| Originalidad | **15%** | Que no exista ya. **Van a googlearlo.** Búsqueda de prior art obligatoria antes de comprometerse. |

**El dato táctico más importante del kickoff**: *"los jueces tienen una copia de sus repositorios en sus computadores y van a estar con agentes haciéndole preguntas al código"*. El repo es parte del pitch. Un agente va a leerlo. → Ver §5.

**Restricciones duras**:
- Repo **público**, licencia **MIT**.
- Debe estar **desplegado y accesible** (nada de localhost en el pitch). Render da créditos.
- Premio extra por **voto público**: publican los proyectos ~10 días después → un extraño con el link tiene que poder usarlo sin nosotros.

**Créditos de sponsors**: Anthropic ($50 API por persona), WhatsApp API de bajo nivel, Render (hosting).

**Premios**: $3.000 USDC. ~$400 por track ganador. Mejor proyecto general **$1.200 + viaje a la final en Chile en noviembre**. $400 al más votado.

**Los 4 tracks** (elegimos el 4):
1. **AI Safety** — medir, controlar y desplegar IA de forma segura; observabilidad de agentes.
2. **Access** — hacer disponible al mundo real como datos para que los agentes puedan actuar sobre él.
3. **Emergencies** — cuando el mundo se rompe (desastre natural o falla técnica), tecnología para volver a funcionar rápido.
4. **Simulations** — *"cómo piensan las personas, cómo funcionan las sociedades, cómo funcionan los mercados"*. Obtener información que no es obvia y hay que aproximarla con un caso hipotético. Ejemplo que dieron: cómo se movió la opinión política ante la publicidad de un candidato.

**Nota del organizador sobre nuestro track**: dijo que Simulations es el que más potencial tiene de generar **presentaciones interesantes**. Eso corta para los dos lados — ver §2.

---

## 2. La trampa del track (leer esto antes de enamorarse de una idea)

**Trampa A — el prior art.** "Agentes LLM con personalidades que interactúan" ya existe y es famoso: *Generative Agents / Smallville* (Stanford, 2023) y los *1000 agentes réplica de personas reales* (2024). Hay startups vivas haciendo focus groups sintéticos y encuestas sintéticas. Si el pitch es "poblamos un mundo con personas LLM y vemos qué pasa", el 15% de originalidad se pierde en 14 letras de Google, que es literalmente lo que advirtieron.

**Trampa B — la simulación es slop con gráficas bonitas.** El organizador dedicó varios minutos del keynote al concepto de *slop*. Una simulación produce un resultado **plausible** siempre, gane o pierda contra la realidad. Un juez técnico va a preguntar, en algún momento de los 3.5 minutos: *"¿y cómo sé que esto no es puro invento?"*. **Ese es el proyecto entero.** El equipo que responda esa pregunta con evidencia gana el track.

**Trampa C — la demo bonita sin motor.** El track invita a lo visual, y lo visual se puede fingir. Pero el 25% es técnico y los jueces leen el repo con agentes. Una visualización preciosa sobre 200 líneas de prompts se cae en el interrogatorio.

**El wedge, entonces**: no competir por "la simulación más llamativa". Competir por **la simulación que se puede equivocar** — que hace una predicción falsable, la contrasta contra algo que ya pasó, y reporta su propio error. Es lo contrario del slop y es defendible ante un juez técnico.

---

## 3. Seis ideas

### A. Backtest de política pública ("¿qué pasa si aprueban esto?")
Simulador donde metes un proyecto de ley / reforma y te dice cómo responde una población sintética de Colombia.
- **Carne técnica**: síntesis de población real (Iterative Proportional Fitting sobre marginales del censo / GEIH del DANE) → agentes con atributos consistentes, no inventados. Capa LLM solo para la respuesta conductual, no para los datos. Motor determinista con seeds.
- **El golpe de pitch**: le corremos una reforma **que ya pasó** (tributaria 2016, salario mínimo de algún año) y mostramos que el simulador predice lo que efectivamente ocurrió. Después le corremos la reforma en discusión hoy.
- **Rúbrica**: ambición ↑↑, impacto ↑↑, técnico ↑↑, originalidad media-alta (existe modelaje econométrico, no existe con esta interfaz + validación abierta).
- **Riesgo**: los datos. Si el DANE no suelta microdatos usables en las primeras 4 horas, se cae. **Verificar disponibilidad ANTES de comprometerse.**

### B. Túnel de viento para agentes
Le describes tu sistema en producción (una API, un flujo de soporte, un marketplace) y genera un mundo simulado hostil: usuarios adversariales, datos de borde, fallas inyectadas. Corre tu agente miles de veces y te devuelve dónde se rompe.
- **Carne técnica**: generación de entornos, fault injection, búsqueda dirigida de fallas (no fuerza bruta), reducción de casos a un mínimo reproducible.
- **Rúbrica**: técnico ↑↑↑, impacto ↑↑ (dolor real y hoy), cruza con el track AI Safety, lo cual es bueno (jueces de dos tracks lo entienden).
- **Riesgo**: originalidad. Hay varias startups de evals de agentes. Y es difícil de explicar en 3.5 min a alguien que no sufre el problema.

### C. Bogotá se rompe (cruza con Emergencies)
Gemelo digital de la ciudad sobre el grafo vial real de OpenStreetMap + población censal. Inyectas un sismo o una inundación, y pruebas decisiones: cerrar este puente, poner los albergues acá, evacuar por allá. Devuelve tiempos de evacuación y población desatendida.
- **Carne técnica**: ruteo sobre grafo real a escala, modelo de congestión, optimización de ubicación de recursos. Poco LLM, mucha computación de verdad.
- **Rúbrica**: impacto ↑↑↑, visualmente demoledor en pitch (un mapa de Bogotá poniéndose rojo), técnico ↑↑.
- **Riesgo**: la simulación de transporte es un campo maduro (SUMO, MATSim). El aporte tiene que ser la capa de decisión, no el motor. Y el rendimiento sobre un grafo de Bogotá completo se puede comer 10 horas.

### D. La sala de negociación
Simular una negociación multi-actor (sindicato-empresa, gobierno-gremio, socios de una compañía) donde cada actor se construye a partir de sus posiciones **documentadas y citables**, no imaginadas. Pruebas estrategias antes de sentarte en la mesa real.
- **Carne técnica**: cada afirmación de un agente anclada a una fuente; solver de teoría de juegos por encima para encontrar la zona de acuerdo; búsqueda sobre árbol de estrategias.
- **Rúbrica**: originalidad ↑↑, presentación ↑↑↑ (se puede demostrar en vivo).
- **Riesgo**: sin la capa de teoría de juegos es "chatbots conversando" y el 25% técnico se evapora.

### E. Gemelo digital de la organización
Simula el reorg antes de hacerlo. A partir de artefactos reales (org chart, tickets, calendarios), modela el flujo de trabajo y responde: ¿qué pasa si se va esta persona? ¿si partimos este equipo en dos? ¿dónde está el cuello de botella que nadie ve?
- **Carne técnica**: simulación de eventos discretos / teoría de colas sobre el grafo organizacional + agentes para la decisión humana. Bus factor calculado, no opinado.
- **Rúbrica**: ambición ↑↑, y **le habla directo a Buk** (el sponsor de RRHH que abrió el evento). Eso no está en la rúbrica pero los jueces son humanos.
- **Riesgo**: sin datos reales de una organización, la demo es de juguete.

### F. El runtime de simulaciones (la infra, no la simulación)
No una simulación: el motor sobre el que corren todas. Mundos deterministas y con seed, snapshot del estado, **bifurcación contrafactual** (forkeas el mundo en el paso N, cambias una variable, corres las dos ramas), caché de llamadas al LLM, N corridas en paralelo para significancia estadística en vez de una anécdota.
- **Carne técnica**: es la opción de mayor puntaje técnico posible. Determinismo con LLMs no es trivial y es un problema real.
- **Riesgo**: una plataforma abstracta muere en un pitch de 3.5 min. Nadie aplaude un runtime.

---

## 4. Recomendación: F como motor + A (o C) como demo insignia

Ninguna de las seis gana sola. **F sin demo es invisible; A sin motor es un notebook.**

La combinación:
- **El motor** (F) da el 25% técnico y hace verdadera la afirmación "esto no se hizo en 36 horas": determinismo, seeds, bifurcación contrafactual, corridas en paralelo, caché.
- **La demo insignia** (A, o C si los datos del DANE no aparecen) da ambición, impacto y los 20 segundos que ganan el pitch: **el backtest**.
- **La barra de error** es la firma del proyecto. Cada predicción sale con su intervalo y con el historial de aciertos del simulador. Es la respuesta anticipada a la única pregunta que importa.

**Frase del pitch a la que hay que llegar**: *"Le pedimos que predijera algo que ya pasó, sin dejarle ver el resultado. Se equivocó por X%. Ahora le preguntamos por lo que viene."*

Si el backtest sale bien: ganamos el track. Si sale mal pero **medido y reportado honestamente**, sigue siendo el proyecto más serio de la sala — porque todos los demás van a estar presentando resultados que nadie puede refutar.

---

## 5. Táctica: el repo es parte del pitch

Dijeron que los jueces cargan el repo y lo interrogan **con agentes**. Eso significa que hay un lector no-humano que se puede optimizar, y casi ningún equipo va a hacerlo:

- `README.md` que responde en los primeros 20 renglones: qué es, cómo se corre, qué es lo no obvio.
- `ARCHITECTURE.md` con el flujo de datos, las decisiones de diseño **y sus alternativas descartadas con el porqué**. Un agente al que le preguntan "¿esto tiene ingeniería real?" encuentra ahí su respuesta.
- `VALIDATION.md`: la metodología del backtest, los números, y **las limitaciones admitidas**. Admitir límites sube la credibilidad técnica, no la baja.
- Commits legibles y repartidos entre los 5 (se nota quién trabajó).
- Tests sobre el núcleo determinista. Es la prueba más barata de que hay ingeniería.

---

## 6. Plan crudo — 36 horas, 5 personas

### Roles (una cabeza por área, nadie sin dueño)

| # | Rol | Responsable de |
|---|---|---|
| 1 | **Motor** | Núcleo de simulación: determinismo, seeds, estado, bifurcación |
| 2 | **Datos** | Ingesta, población sintética, calibración, el backtest |
| 3 | **Agentes** | Capa LLM: prompts, caché, batching, control de costo |
| 4 | **Interfaz** | Visualización y demo pública. Vale más de lo que parece: el 20% de impacto es "fácil de usar" |
| 5 | **Integración + pitch** | Deploy, README/ARCHITECTURE/VALIDATION, guion, ensayos, video de respaldo |

El rol 5 no es "el que no programa" — es el que impide que el proyecto muera a la hora 34. Suele ser el puesto más subestimado de un hackathon.

### Línea de tiempo

**H0–H2 · Cena con el mentor — decidir, no explorar**
- Elegir UNA idea y el backtest concreto (qué evento histórico, qué dato, dónde vive).
- **Búsqueda de prior art de 20 minutos, en serio.** Si existe, pivotear ahora y no a la hora 12.
- Escribir la frase del pitch **antes** de escribir código. Si no se puede escribir, la idea no está lista.

**H2–H4 · Andamiaje**
- Contratos de interfaz entre los 5 módulos, para poder trabajar en paralelo sin bloquearse.
- **Deploy de un "hola mundo" a Render YA.** Regla dura: el pipeline de deploy funciona en la hora 3, no en la hora 34. Lo que más mata proyectos de hackathon no es la idea, es el despliegue de última hora.
- Determinismo y seeds desde el primer commit. Meterlo después es reescribir.

**H4–H10 · Núcleo en paralelo**
- Meta H10: **una simulación fea corre de punta a punta con datos falsos.** Fea está bien. Completa es obligatorio.

**H10–H14 · Turnos de sueño escalonados**
- Nunca los 5 despiertos ni los 5 dormidos. Dos duermen 4h, luego los otros dos. El rol 5 arbitra.

**H12–H20 · Calibración y primer backtest**
- **Checkpoint duro en H20**: si el backtest no da, se cambia **la métrica de validación**, no el proyecto. Cambiar de proyecto en la hora 20 es perder.

**H20–H28 · Interfaz y narrativa**
- La visualización que va a estar en pantalla durante el pitch.
- **Feature freeze en H28.** Sin excepciones. Nada de dependencias nuevas después de esta hora.

**H28–H32 · Cierre**
- Deploy final y probarlo desde el celular de alguien, en datos móviles, sin sesión iniciada (el premio del voto público exige exactamente eso).
- README + ARCHITECTURE + VALIDATION.
- **Grabar un video del demo funcionando.** El wifi de un hackathon se cae siempre. Este video es el seguro de vida del proyecto.

**H32–H36 · Ensayar**
- Mínimo 5 pasadas con cronómetro. 3.5 minutos es brutalmente corto: alcanza para ~6 frases y una demo.
- Estructura sugerida: problema (25s) → por qué las simulaciones no son creíbles (20s) → nuestra respuesta (20s) → **demo del backtest** (90s) → predicción nueva (30s) → escala (15s).

### Reglas del equipo
1. Feature freeze en H28, se respeta aunque duela.
2. El demo grabado existe antes de que alguien pula nada.
3. Nadie toca el repo de otro sin avisar. Ramas por rol.
4. Cada 6 horas, 10 minutos de sincronización de pie. Solo tres preguntas: qué está corriendo, qué está roto, qué necesito de ustedes.
5. Si algo lleva 2 horas trabado, se corta y se hardcodea. Hay 34 horas y ninguna es reemplazable.

---

## 7. Lo que hay que decidir esta noche

1. **¿Idea A, C, o D como insignia?** (El motor F va debajo de cualquiera de las tres.)
2. **¿Cuál es el backtest exacto?** Evento, fuente de datos, métrica de error. Sin esto no hay proyecto.
3. **¿Los datos existen y son descargables hoy?** Verificar antes de comprometerse, no después.
4. **¿Quién toma cuál rol?** Que nadie quede sin dueño de área.
