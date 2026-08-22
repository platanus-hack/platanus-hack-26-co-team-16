# Investigación — Juan David Torres

> Documento de investigación individual para fusionar con el de los demás integrantes.
> **No contiene decisiones de implementación**: es material crudo verificado para que el plan se arme después con el aporte de los cinco.
>
> Convención usada en todo el documento:
> ✅ **Verificado** en esta sesión · ⚠️ **Por verificar** antes de construir encima · 💭 Análisis / opinión

---

## 1. Hallazgo central — los microdatos del DANE

### Qué son ✅

La **Gran Encuesta Integrada de Hogares (GEIH)** del DANE publica **microdatos anonimizados de acceso público**:

| Atributo | Valor |
|---|---|
| Portal | `microdatos.dane.gov.co` |
| Cobertura temporal | Desde el primer trimestre de **2013**, catálogos hasta **2026** |
| Tamaño de muestra | **~240.000 hogares al año** |
| Nivel | Persona y hogar (no agregado) |
| Módulos | Mercado laboral, ingresos, **empleo informal y seguridad social** |
| Acceso | Público, requiere **registro gratuito** |
| Costo | $0 |

Catálogos directos: [2022](https://microdatos.dane.gov.co/index.php/catalog/771) · [2023](https://microdatos.dane.gov.co/index.php/catalog/782) · [2024](https://microdatos.dane.gov.co/index.php/catalog/819) · [2025](https://microdatos.dane.gov.co/index.php/catalog/853) · [2026](https://microdatos.dane.gov.co/index.php/catalog/900)

### Por qué esto cambia la arquitectura 💭

**No necesitamos un LLM para generar la población de agentes.** Cada agente se instancia desde una persona real anonimizada, con sus atributos observados: salario, sector económico, región, nivel educativo, tamaño de la empresa donde trabaja, y estado de formalidad.

Esto tiene tres consecuencias grandes:

1. **La heterogeneidad se hereda, no se inventa.** El problema clásico de los modelos basados en agentes es que las distribuciones de atributos son supuestos del modelador. Aquí no: vienen de una encuesta de 240k hogares con diseño muestral probabilístico. Además la **correlación entre atributos** viene gratis y correcta — no hay que asumir cómo se relacionan educación, sector e informalidad, porque están juntos en la misma fila.

2. **Neutraliza el ataque más peligroso en el Q&A.** *"Ustedes sacaron lo que metieron"* es la pregunta que mata un proyecto de simulación. La respuesta se vuelve: *"no metimos supuestos sobre la población, metimos la población"*.

3. **Libera el presupuesto de Anthropic.** Los $50 de créditos no se gastan generando agentes sintéticos. Quedan para lo que sí aporta: interpretar resultados y elicitar reglas de comportamiento que la encuesta no captura.

### ⚠️ Lo que los microdatos NO resuelven — importante

Hay que ser preciso aquí, porque si el equipo asume que el microdato lo resuelve todo, se estrella más adelante:

| Los microdatos SÍ dan | Los microdatos NO dan |
|---|---|
| El **estado inicial** de cada agente | La **regla de decisión** del agente |
| La distribución conjunta real de atributos | Cómo reacciona esa persona ante un cambio de política |
| Los **momentos objetivo** para calibrar | Los parámetros de comportamiento |
| El ground truth para validar | El mecanismo causal |

Es decir: la GEIH nos dice **quién es cada agente**, pero no **qué hace cuando el salario mínimo sube 23%**. Esa regla hay que calibrarla contra la historia (ver §6) o elicitarla y destilarla.

### ⚠️ Verificación de alto valor — el panel rotativo

La GEIH tiene **estructura de panel rotativo**: los mismos hogares se encuestan durante varios meses consecutivos.

**Si eso permite seguir a la misma persona a través del tiempo, es lo más valioso de todo este documento**, porque se podrían observar **transiciones reales** — la misma persona pasando de formal a informal, o a desempleada, en meses donde ocurrió un cambio de salario mínimo. Eso convierte la regla de comportamiento de "supuesto calibrado" a **"transición observada en datos"**, que es un salto enorme de credibilidad.

**Acción concreta:** alguien debe verificar en la documentación técnica de la GEIH si los identificadores permiten enlazar la misma persona entre trimestres, y cuántos meses dura la ventana. Es la primera cosa que yo revisaría.

---

## 2. El problema, documentado (no deducido)

### El hecho ✅

Cada diciembre, la Comisión Permanente de Concertación (gobierno + gremios + centrales obreras) negocia el aumento del salario mínimo. Para 2026:

| Postura | Porcentaje |
|---|---|
| Propuesta de los empresarios | **7%** |
| Fórmula técnica (inflación + productividad 0,91% + crecimiento 2,9%) | **13,6%** |
| **Lo que el gobierno decretó** | **23%** |

- **Decretos 1469 y 1470 de 2025**, expedidos el **29 de diciembre de 2025**.
- SMMLV 2026 = **$1.750.905**. Auxilio de transporte: +24,5%.
- **~2,4 millones de trabajadores** devengan el salario mínimo.
- **Hay un pulso jurídico abierto en el Consejo de Estado** sobre el decreto.
- Analistas advirtieron que un incremento tan alto aumentaría la informalidad y probablemente el desempleo.
- Colombia tiene **~55% de informalidad laboral** (2025) y desempleo ~8,6%.

Fuentes: [elempleo](https://www.elempleo.com/co/noticias/tendencias-laborales/salario-minimo-2026-el-gobierno-ratifica-el-aumento-del-23-mediante-decreto-transitorio-8757) · [Holland & Knight](https://www.hklaw.com/en/insights/publications/2025/12/colombia-decreta-aumento-del-salario-minimo-y-auxilio-de-transporte) · [ConsultorSalud](https://consultorsalud.com/decreto-transitorio-aumento-del-salario-minimo/) · [El País](https://www.elpais.com.co/economia/aumento-del-salario-minimo-en-colombia-para-el-2026-seria-superior-al-20-segun-un-borrador-de-decreto-2920.html)

### Por qué esto tiene forma de simulación 💭

Un problema justifica una simulación solo si pasa estas cuatro. Este las pasa las cuatro:

1. **¿La decisión se toma antes de poder observar el resultado?**
   Sí. Se decreta en diciembre; los efectos aparecen durante el año siguiente.

2. **¿Hay interacción, retroalimentación o umbrales?**
   Sí, y es el punto clave. Una empresa que no puede pagar el nuevo mínimo **no necesariamente despide: informaliza.** Y esa decisión depende de qué hagan las demás empresas del sector.

3. **¿Probar en la realidad es imposible?**
   Sí, de forma absoluta. Solo se puede aplicar **un** porcentaje al país entero. Los otros dos mundos nunca existen. Ese es literalmente el hueco que una simulación llena.

4. **¿Hay caso pasado contra el cual validar?**
   Sí, y es la mejor parte: **Colombia sube el mínimo todos los años, con porcentajes distintos**, y el DANE mide informalidad y empleo todos los años. Son ~20 experimentos naturales con datos públicos.

### ⚠️ Nota de terminología

El salario mínimo es **política laboral / fiscal**, no monetaria (la monetaria es la tasa de interés del Banco de la República). Decir "política monetaria" frente a un juez con background económico cuesta credibilidad gratis. Usar **"política salarial"** o **"política laboral"**.

---

## 3. Fuentes de datos verificadas

### Directamente relevantes

| Fuente | Acceso | Qué tiene | Estado |
|---|---|---|---|
| [**GEIH — microdatos DANE**](https://microdatos.dane.gov.co/) | Registro gratuito | Microdatos persona/hogar, 240k hogares/año, 2013→2026, módulo de informalidad | ✅ |
| [**DANE — empleo informal y seguridad social**](https://www.dane.gov.co/index.php/estadisticas-por-tema/mercado-laboral/empleo-informal-y-seguridad-social) | Directo | Serie oficial de informalidad — el objetivo de calibración | ✅ |
| [**datos.gov.co**](https://datos.gov.co/) | Directo | Portal nacional de datos abiertos | ✅ |
| [**Datos Abiertos Bogotá**](https://datosabiertos.bogota.gov.co/) | Directo | Datos distritales | ✅ |

### De respaldo (si el proyecto pivotara)

| Fuente | Acceso | Qué tiene | Estado |
|---|---|---|---|
| [**XM / SIMEM — `pydataxm`**](https://github.com/EquipoAnaliticaXM/API_XM) | **Sin usuario ni clave** | Sistema eléctrico colombiano: demanda, generación por planta, disponibilidad, hidrología, precios. Granularidad horaria/diaria/mensual | ✅ |
| [**USGS FDSN**](https://earthquake.usgs.gov/fdsnws/event/1/) | Sin API key | Catálogo sísmico global en tiempo real, GeoJSON | ✅ |
| [**SDM / SIMUR Bogotá**](https://datos.movilidadbogota.gov.co/) | Directo | Movilidad: CSV, GeoJSON, WMS/WFS | ✅ |
| OpenStreetMap | Directo | Edificaciones, vías | ✅ |

### ⚠️ Por verificar

- **Factor prestacional colombiano.** Costo total de un empleado formal ≈ salario × 1,4–1,5 (parafiscales + prestaciones + seguridad social). El número exacto y su composición hay que confirmarlo — es un parámetro central del modelo.
- **Panel rotativo de la GEIH** (ver §1) — la verificación de mayor valor de toda la lista.
- **Serie histórica de aumentos del salario mínimo** 2000→2026 en un solo lugar limpio. Existe pero hay que armarla.

---

## 4. Prior art — qué ya existe

> **Esto importa para el 15% de originalidad.** El organizador les dijo explícitamente a los jueces que verifiquen si la idea ya existe, y los jueces evalúan con agentes. Conviene que el README nombre el prior art antes de que lo encuentren ellos.

### Economía del salario mínimo e informalidad (literatura madura)

| Trabajo | Qué hace |
|---|---|
| [Harris-Todaro ABM](https://arxiv.org/pdf/physics/0510248) | Modelo basado en agentes de migración rural-urbana con aprendizaje social por imitación; analiza el efecto del salario mínimo en equilibrio de largo plazo |
| [IMF WP 2024/159 — *Minimum Wages, Inequality, and the Informal Sector*](https://www.elibrary.imf.org/view/journals/001/2024/159/article-A001-en.xml) | Firmas heterogéneas que **eligen** informalidad; cuándo subir el mínimo aumenta la desigualdad |
| [Meghir, Narita & Robin — *Wages and Informality in Developing Countries* (AER)](https://www.aeaweb.org/articles?id=10.1257%2Faer.20121110) | Modelo de equilibrio con wage-posting y firmas que eligen sector formal/informal, **estimado sobre microdatos de la encuesta laboral de Brasil** |
| [CEMLA — *Macroeconomic Effects of the Minimum Wage in an Emerging Economy with Labor Informality*](https://www.cemla.org/actividades/2025/2025-11-xxx-meeting-central-bank-researchers/papers/Macroeconomic%20Effects%20of%20the%20Minimum%20Wage%20in%20an%20Emerging%20Economy%20with%20Labor%20Informality.pdf) | Modelo neokeynesiano de dos agentes con trabajo formal e informal |
| [arXiv 2509.20465](https://arxiv.org/html/2509.20465v1) | Síntesis de meta-análisis: informalidad, salario mínimo y poder de monopsonio |
| [CEPR / VoxEU](https://cepr.org/voxeu/columns/informality-and-effects-minimum-wage-policy-developing-countries) | Resumen del estado del debate |

**Lectura de esto** 💭: el modelo de Meghir-Narita-Robin es el precedente más cercano — estructura equivalente, estimado sobre microdatos, pero de **Brasil** y como paper académico. Es una referencia metodológica excelente y, al mismo tiempo, el prior art más incómodo. Hay que citarlo.

### Simulación de políticas con agentes LLM (categoría saturada en 2025–2026)

| Trabajo | Qué hace |
|---|---|
| [AgentSociety](https://arxiv.org/abs/2502.08691) | 10.000+ agentes LLM, 5 millones de interacciones, entorno societal realista |
| [GenWorld](https://arxiv.org/pdf/2606.27650) | Simulación urbana a escala de ciudad; destila LLMs en modelos estudiantes baratos |
| [LLM-Powered Social Digital Twins](https://arxiv.org/abs/2601.06111) | Réplicas de población **calibradas a censo** para respuesta a intervenciones de política |
| [PoliSim @ CHI 2026](https://dl.acm.org/doi/10.1145/3772363.3778738) | Workshop entero dedicado a simulación con agentes LLM para política pública |
| [Integrating LLM in Agent-Based Social Simulation](https://arxiv.org/pdf/2507.19364) | Revisión de oportunidades y límites |
| [Static Sandboxes Are Inadequate](https://arxiv.org/pdf/2510.13982) | Crítica: los sandboxes estáticos no capturan complejidad societal real |

**Lectura de esto** 💭: **si el proyecto se presenta como "agentes LLM simulando una sociedad", la originalidad arranca en cero.** Esa categoría está ocupada por trabajos con más escala y más recursos.

La diferenciación honesta que sí queda en pie:

- La población **no es sintética generada por un LLM** — son personas reales anonimizadas de la GEIH.
- **Colombia específicamente**, con su margen de informalidad del 55%, que es donde vive el fenómeno y que los modelos genéricos no capturan.
- **Es una herramienta usable**, no un paper. Ninguno de los trabajos de arriba le sirve a alguien que esté dentro de la discusión de diciembre.
- **Un contrafactual concreto y vivo**: 7% vs 13,6% vs 23%, con litigio abierto.

### El paper que define el estándar de rigor

[**We Need Strong Preconditions For Using Simulations In Policy**](https://arxiv.org/html/2604.07838v1) (2026) argumenta que el gap real no es construir simuladores, sino **saber cuándo creerles**. Nombra los modos de falla: modelos que exhiben estereotipos en vez de comportamiento realista, y la ausencia de mecanismos para distinguir *"una herramienta de decisión de una bola mágica 8"*.

💭 Vale la pena leerlo: es esencialmente el guion de las preguntas difíciles que nos van a hacer.

---

## 5. Riesgo de diseño #1 — el resultado no puede estar en el supuesto

> **Si todos los agentes maximizan ganancia, la conclusión ya está escrita en el supuesto.**
> Sube el costo del trabajo → el maximizador despide → sube el desempleo. Habríamos demostrado nuestra propia premisa.
> El juez pregunta *"¿qué aprendí?"* y no hay respuesta. **Este es el modo de falla más probable del proyecto.**

### El mecanismo correcto para Colombia: el margen de informalidad 💭

Con ~55% de informalidad, la empresa que no puede pagar el nuevo mínimo tiene **tres salidas, no una**:

1. **Despedir**
2. **Informalizar** — mantener al trabajador sin contrato ni prestaciones
3. **Absorber** — reducir su margen

Y el trabajador también decide: un empleo formal al mínimo deja **menos plata en el bolsillo hoy** (descuentos de ley) pero da protección; uno informal paga más neto y no protege nada.

Esa frontera es donde vive el fenómeno colombiano. **Modelar el margen formal/informal —y no el despido— es lo que separa esto de un ejercicio de libro de texto.**

La decisión de la firma compara productividad marginal contra:

- **costo formal** = salario mínimo × factor prestacional (⚠️ ≈1,4–1,5, por verificar)
- **costo informal** = salario negociado, sin cargas, penalizado por riesgo de sanción y por pérdida de acceso a crédito, contratos públicos y clientes formales

Y las probabilidades de cada salida deben ser **calibradas contra la historia, no supuestas**. Esa es toda la diferencia.

---

## 6. Qué hace creíble una simulación ante jueces técnicos

> Aplica a cualquier proyecto de este track, no solo al nuestro. Peso: **aspecto técnico = 25%**, el criterio más pesado.

### Las cuatro capas de credibilidad

1. **Población real, no supuesta.** Ya la tenemos (§1).

2. **Calibración.** Ajustar los parámetros de comportamiento para que el modelo reproduzca momentos observados: tasa de informalidad por sector y por tamaño de firma, distribución salarial, tasa de desempleo. El método estándar es **Method of Simulated Moments (MSM)**.

3. **Backtest fuera de muestra.** Ajustar con datos hasta un año de corte, **predecir** los años siguientes, medir el error contra lo que realmente pasó. **Sin esto, el proyecto es opinión con gráficas.**
   - ⚠️ **Cuidado con COVID:** 2020–2021 rompe cualquier backtest de mercado laboral. Validar sobre 2013–2019 y 2022–2025, tratando el shock como exógeno. Decirlo explícitamente **suma**, no resta.

4. **Falsación y límites declarados.** Un `VALIDATION.md` que diga qué reproduce el modelo, qué no, y **dónde no hay que creerle**. La honestidad calibrada se lee como madurez de ingeniería, no como debilidad.

### ⚠️ Hechos estilizados como objetivo de validación

Dos fenómenos documentados del mercado laboral latinoamericano que, si el modelo los reproduce **sin que se los digamos**, son un argumento demoledor:

- **La masa salarial acumulada exactamente en el mínimo** (el "spike"). Debería ser visible directamente en la GEIH.
- **El "efecto faro"** — que el salario mínimo arrastra también los salarios del sector *informal*, aunque legalmente no lo cubra. ⚠️ Por verificar en la literatura y en los datos.

Ambos se pueden comprobar contra la GEIH en las primeras horas de trabajo.

### Referencias metodológicas

- [`sbi` — simulation-based inference toolkit](https://sbi-dev.github.io/sbi/) — inferencia bayesiana cuando la verosimilitud es intratable pero se puede simular
- [Automatic Calibration Framework of ABMs for Dynamic and Heterogeneous Parameters](https://arxiv.org/pdf/2203.03147)
- [Evaluating the Validity of Agent-Based Models: Challenges and Methodological Approaches](https://link.springer.com/chapter/10.1007/978-3-032-13869-9_3)

---

## 7. Restricciones del evento (extraídas del transcript de la charla)

### Rúbrica de evaluación

| Criterio | Peso | Qué significa según el organizador |
|---|---|---|
| Originalidad | 15% | *"Crear algo que aún no existe."* Recomendó explícitamente buscar en Google/ChatGPT si ya existe |
| Ambición | 20% | Resolver un problema lo más grande posible; *"hagan algo que ni siquiera están seguros de ser capaces de hacer"* |
| Ejecución | 20% | *"Que no parezca hecho en 36 horas"* |
| **Aspecto técnico** | **25%** | *"Que no lo pueda hacer tu primo de 8 años con tres prompts"* |
| Impacto | 20% | Que la forma de resolverlo tenga potencial real. Un sistema difícil de usar no tiene impacto aunque la idea sea buena |

### Reglas operativas

- **Los jueces tienen una copia del repositorio en sus computadores y usan agentes para interrogar el código.** Todos los jueces son técnicos. → **El repo es parte del pitch.**
- Repo público, licencia **MIT**.
- **Debe estar desplegado.** ⚠️ Según el README de este repo, Vercel/Render/Netlify **no pueden conectarse al repo de la organización** — hay que espejar a un repo personal y desplegar desde ahí.
- **Créditos:** $50 de API de Anthropic · Render · WhatsApp API (Bird) · otros sponsors.
- **Pitch: 3 minutos y medio.** Hay una charla del sábado sobre cómo presentar.
- Premios: $400 USDC por track · $1.200 al mejor equipo general + viaje a la final en Chile en noviembre · $400 al proyecto más votado (votación abierta ~10 días después).

### 💭 Implicaciones de diseño que se derivan de lo anterior

1. **El LLM nunca en el bucle caliente.** $50 no aguantan un loop de LLM sobre miles de agentes, y además cae en el modo de falla "wrapper de prompt" que castiga el 25% técnico. El LLM sirve para elicitar reglas una vez, destilarlas en políticas paramétricas, e interpretar resultados.
2. **El repo debe leerse como ingeniería.** `README` con prior art honesto · `VALIDATION.md` · tests del núcleo numérico · un `scripts/reproduce.py` que reproduzca el resultado principal con **un** comando. Cuesta pocas horas y pesa sobre el criterio más grande.
3. **Un solo número y una sola imagen.** En 3,5 minutos solo sobrevive un mensaje.
4. **Mirror a repo personal desde temprano**, no a la hora 34.

---

## 8. Modos de falla observados (pre-mortem)

Los cinco escenarios en que este tipo de proyecto pierde, con su antídoto:

| # | Modo de falla | Antídoto |
|---|---|---|
| 1 | **El resultado estaba en el supuesto.** Todos maximizan ganancia, sube el costo, se destruye empleo — demostramos nuestra premisa | §5: el margen formal/informal con probabilidades calibradas, no supuestas |
| 2 | **No conseguimos los microdatos a tiempo.** El registro del DANE y el tamaño de los archivos se comieron la mañana | Empezar por ahí, con una persona dedicada. Fallback: tablas agregadas del DANE, de descarga directa |
| 3 | **Nos ganó la economía.** Intentamos un modelo macro completo (inflación, demanda agregada, tasa de cambio) y no cerró nada | **No es un modelo macro.** Es un módulo de mercado laboral. Inflación y crecimiento entran como datos exógenos observados, no como resultado |
| 4 | **El backtest no cerró** y escondimos la validación para mostrar solo el contrafactual bonito | Publicar el error igual. *"Reproduce informalidad con ±2pp y falla en agricultura"* es infinitamente más fuerte que el silencio |
| 5 | **Nos leyeron como panfleto político.** El modelo "demostró" que el gobierno se equivocó y la sala se dividió por ideología en vez de por técnica | El producto es el **rango con incertidumbre** y el **mapa de quién gana y quién pierde**, no un veredicto. Mostrar bajo qué parámetros cada una de las tres posturas resulta razonable |

---

## 9. Preguntas abiertas para el equipo

1. **¿El panel rotativo de la GEIH permite seguir a la misma persona entre trimestres?** (§1) — la verificación de mayor valor de todo el documento.
2. **¿Cuál es el output final: un número, un rango, un mapa distributivo o un umbral?** Mi lectura 💭 es que el agregado esconde la historia y que lo valioso es **quién** gana y **quién** pierde, más el umbral donde el efecto se acelera. Pero es decisión del equipo.
3. **¿Hasta dónde llega el alcance del modelo?** Solo mercado laboral, o también consumo, precios, recaudo. Cada extensión multiplica el riesgo de no cerrar.
4. **¿Cómo se presenta sin volverse político?** (modo de falla #5)
5. **¿Quién se encarga del deploy espejado a repo personal, y desde cuándo?**
6. **¿Alguien puede conseguir 15 minutos con un economista laboral?** Una revisión de un experto vale más que cinco horas de código y da una frase de validación externa para el pitch.

---

## 10. Contexto adicional que puede ser útil

Material verificado que no aplica directamente al proyecto actual, pero que quedó de rondas anteriores de investigación y podría servirle a alguien:

- **Terremoto del 10 de agosto de 2026** ✅ — M7.4, epicentro cerca de San José del Palmar (Chocó), 103 km de profundidad, 07:34 hora local. Desastre nacional declarado (decreto 1261 de 2026). Entre 132 y 285 fallecidos según la fuente, 570+ heridos, 1.000+ edificios colapsados. Pereira, Cali, Manizales, Armenia y Quibdó afectados.
- **El Sistema Interconectado Nacional perdió el 18% de la demanda del país en segundos** durante el sismo y estuvo muy cerca de un apagón total; lo confirmó el gerente general de XM. La demanda se recuperó al ~99% del nivel previo. Publicado el 20 de agosto de 2026.
- **Contexto energético 2026** — déficit proyectado de -2% al cierre del año, crisis financiera del sector (~$9,2 billones), riesgo de El Niño.
- **Riesgo hídrico de Bogotá** — el Concejo alertó riesgo alto de racionamiento en 2026; el sistema Chingaza surte ~70% del agua potable de la ciudad. El racionamiento de abril de 2024 es un experimento natural con datos públicos.
- **Crisis del sistema de salud** — déficit patrimonial de -$15,8 billones a inicios de 2026; pérdidas operacionales superiores a $7,3 billones a noviembre de 2025.

💭 Ninguno de estos es un problema atacable tal como está enunciado — son macro-diagnósticos. Los incluyo por si a alguien le sirven de contexto o los cruza con su propia investigación.

---

## Anexo — Nota de método

💭 Una lección de este proceso que vale para todo el equipo:

**Buscar problemas en Google no funciona.** Lo intenté y solo devuelve macro-diagnósticos sin decisor concreto, sin decisión concreta y sin forma de saber si acertaste. Los problemas buenos vienen de tres fuentes, en orden de rendimiento:

1. **Dolor propio** — algo que te pasó, con fecha.
2. **Dolor ajeno observado de cerca** — con nombre propio de quien lo sufre.
3. **Preguntarle a alguien que lo vive.** Estamos 36 horas en un edificio lleno de fundadores, mentores y sponsors. La pregunta que rinde es: ***"¿qué decisión tomas en tu trabajo donde básicamente estás adivinando?"***

Y el filtro que separa un problema de simulación de uno que no lo es: **si el dato se puede medir, no hace falta simular — hace falta un dashboard, y eso pierde en este track.**
