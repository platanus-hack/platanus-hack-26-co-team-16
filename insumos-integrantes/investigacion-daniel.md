# Investigación — Track Simulaciones
### Daniel · Platanus Hack 26 Bogotá · 22 ago 2026

> **Cómo leer este documento.** Está hecho para compararse con los MDs de Alejo, Manu, Nico y Juanda. Tres temas, cada uno con: el core teórico, lo que ya se hizo, el hueco verificado, y propuestas de proyecto puntuadas contra la rúbrica del jurado.
>
> **Convención de marcado** (importante para comparar): `[V]` verificado contra fuente primaria · `[INF]` inferencia mía o del proceso de investigación, no afirmación de la fuente · `[NV]` no verificado, trátalo como hipótesis.
>
> **Método:** ~50 búsquedas web y ~70 fetches a fuentes primarias (Nature, Science, PNAS, AER, JPE, QJE, NeurIPS, EMNLP, COLM, arXiv, NBER). Todos los números que aparecen tienen fuente. Donde no pude verificar, lo digo.

---

## 0 · TL;DR — lo que traigo a la mesa

**La tesis de fondo:** el track pide *"información que no es directamente accesible, aproximada con un caso teórico"*. Los tres temas que exploré atacan eso desde ángulos distintos, pero **solo uno de ellos tiene un hueco confirmado por búsqueda explícita, datos de validación públicos, y cabe en 36 horas**.

**Mi recomendación:** simular la **emergencia endógena del dinero** con agentes LLM (Kiyotaki-Wright 1989), con un test de contaminación integrado. Puntaje ponderado **8.30/10**, viabilidad **8/10**.

**Por qué:** el origen del dinero es literalmente inaccesible — ocurrió en el neolítico, sin registro. Es el caso perfecto del track. Y busqué explícitamente: **nadie ha corrido Kiyotaki-Wright con agentes LLM.** `[V del hueco]` Hay LLMs en trading, en bonos y hasta en corridas bancarias. Nadie en el origen del medio de cambio.

Y el resultado es interesante **en las dos direcciones**: si el dinero emerge, mostramos que la coordinación monetaria surge del puro razonamiento en lenguaje sin institución previa. Si no emerge, mostramos que el dinero requiere algo que el lenguaje no provee — probablemente conocimiento común à la Chwe — **y ese es el resultado más fuerte de los dos**.

### Tabla maestra — las 16 propuestas puntuadas

Ponderación exacta del jurado: originalidad 15%, ambición 20%, ejecución 20%, técnico 25%, impacto 20%. `Viab` = viabilidad en 36h (mi criterio, no del jurado, pero decide si hay entrega).

| # | Propuesta | Tema | Orig | Amb | Ejec | Téc | Imp | **Total** | Viab |
|---|---|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| **F3** | Interpretabilidad mecanicista sobre un cerebro real | Fly | 10 | 9 | 6 | 10 | 8 | **8.60** | 6 |
| **S2** | Núcleo crítico: la intervención mínima que revierte segregación | Sch | 9 | 8 | 7 | 9 | 9 | **8.40** | 7 |
| **S4** | Tamaño óptimo de la unidad institucional | Sch | 9 | 7 | 8 | 8 | 10 | **8.35** | 8 |
| **F1** | Farmacología in-silico sobre cerebro completo | Fly | 10 | 9 | 6 | 9 | 8 | **8.35** | 6 |
| 🥇 **J1** | **Emergencia endógena del dinero (Kiyotaki-Wright + LLMs)** | **Juegos** | **10** | **8** | **8** | **8** | **8** | **8.30** | **8** |
| **J6** | ¿Son extorsionables los agentes LLM? (determinante cero) | Juegos | 9 | 7 | 8 | 9 | 8 | **8.20** | 8 |
| **J4** | La cascada que no ocurre (Kuran + conocimiento común) | Juegos | 9 | 8 | 7 | 8 | 9 | **8.15** | 7 |
| **F2** | Efectoma: del cableado a la causalidad | Fly | 9 | 9 | 5 | 10 | 7 | **8.05** | 5 |
| **F4** | Lesión y compensación funcional | Fly | 9 | 8 | 7 | 9 | 7 | **8.00** | 7 |
| **S1** | El tipping point del crédito | Sch | 9 | 8 | 6 | 8 | 9 | **7.95** | 6 |
| **S5** | Los estratos de Bogotá como Schelling institucionalizado | Sch | 9 | 7 | 7 | 7 | 10 | **7.90** | 7 |
| **J7** | Ostrom como diseño de mecanismos: ablación de los 8 principios | Juegos | 8 | 8 | 7 | 8 | 8 | **7.80** | 7 |
| 🥈 **J2** | **Índice de contaminación por juego × modelo** | **Juegos** | 7 | 5 | 9 | 9 | 8 | **7.70** | **9** |
| **J3** | ¿Reproducen los LLMs el castigo antisocial transcultural? | Juegos | 8 | 7 | 8 | 8 | 7 | **7.60** | 8 |
| **J5** | Auditoría de contradicción: el factorial que reconcilia la literatura | Juegos | 7 | 6 | 8 | 9 | 7 | **7.50** | 8 |
| **S3** | Longitud de correlación del sorteo partidista | Sch | 8 | 6 | 8 | 9 | 6 | **7.45** | 7 |

**Lectura de la tabla:** los puntajes más altos (F3, F1, S2) tienen viabilidad 6-7. **J1 es el mejor puntaje ajustado por riesgo** — 8.30 con viabilidad 8. Y **J2 es el seguro**: 7.70 con viabilidad 9, y se puede correr *dentro* de J1 como control metodológico. La jugada es **J1 + J2 como un solo proyecto**.

---
---

# TEMA 2 · Dilemas, teoría de juegos y LLMs
### *(Lo pongo primero porque es mi énfasis, aunque en tu lista sea el #2)*

## 2.1 · El canon, en una página

**Axelrod 1980a, *Journal of Conflict Resolution* 24(1).** `[V]` **14 estrategias**, 200 jugadas, **120.000 movimientos**. Ganó **TIT FOR TAT** de Anatol Rapoport con **504.5** puntos (2.52 por jugada). El corte estructural es lo importante: **las 8 mejores estrategias eran todas *nice* (nunca desertan primero); ninguna de las 7 peores lo era.** Las cuatro propiedades: *nice, retaliating, forgiving, clear*. TFT era la estrategia más corta del torneo — ganó por transparente, no por lista.

**Axelrod 1980b, *JCR* 24(3).** `[V]` **62 participantes**, todos sabiendo ya que TFT había ganado. **TFT ganó otra vez.**

> ⚠️ **Matiz que casi nadie menciona** `[V]`: una reproducción de 2025 (arXiv:2510.15438) rescató el Fortran original. Los hallazgos se sostienen, **pero el torneo era especialmente favorable a TFT**. Con ruido y otro pool de estrategias, otras rinden mejor. No lo presentemos como ley de la naturaleza.

**Press & Dyson 2012, *PNAS* 109(26):10409–10413.** ⚠️ `[V]` El resultado que rompió el consenso de Axelrod. Un jugador de memoria-1 puede **imponer unilateralmente** una relación lineal entre su pago y el del rival: `s_X − K = χ(s_Y − K)`, sin importar qué haga el otro. Las **estrategias de determinante cero (ZD)**. Lo que rompen:

1. Un jugador puede **fijar unilateralmente el pago del otro**. La simetría implícita de Axelrod no existe.
2. Contra un oponente que aprende, **la mejor respuesta es cooperar siempre — y eso maximiza el pago del extorsionador**. El que "aprende" está siendo domesticado.
3. **El torneo de Axelrod no era el juego completo.** Nadie había mandado esa región del espacio de estrategias.

Contra-literatura `[V]`: Stewart & Plotkin 2013 y Hilbe, Nowak & Sigmund 2013 (*PNAS*) muestran que en poblaciones grandes se estabilizan las ZD **generosas**, no las extorsivas. El arco completo: *TFT gana (1980) → hay estrategias que dominan a cualquier oponente evolutivo (2012) → solo si la población es pequeña y no evoluciona (2013)*.

**Nowak 2006, *Science* 314(5805):1560–1563 — las cinco reglas.** `[V]`

| Mecanismo | Condición | Variable |
|---|---|---|
| Selección de parentesco | **r > c/b** | r = coeficiente de parentesco (regla de Hamilton) |
| Reciprocidad **directa** | **w > c/b** | w = probabilidad de otro encuentro |
| Reciprocidad **indirecta** | **q > c/b** | q = probabilidad de conocer la reputación |
| Reciprocidad de **red** | **b/c > k** | k = número medio de vecinos |
| Selección de **grupo** | **b/c > 1 + n/m** | n = tamaño máx. de grupo, m = nº de grupos |

> `[INF]` Dos observaciones que importan para nosotros. **La regla 4 es contraintuitiva y barata de simular: redes más escasas (k bajo) sostienen MÁS cooperación.** Y **la regla 3 es la única que requiere lenguaje** — reputación y chisme. Por eso es exactamente donde los LLMs tienen ventaja estructural sobre el ABM clásico.

**Ostrom 1990, *Governing the Commons*, Nobel 2009.** Los 8 principios de diseño `[NV en formulación verbatim]`: límites claros · congruencia local · elección colectiva · monitoreo por los propios apropiadores · **sanciones graduadas** · resolución barata de conflictos · derecho a organizarse · empresas anidadas. Demuele a Hardin: **la tragedia de los comunes no es inevitable, es un fallo de diseño institucional.**

---

## 2.2 · Catálogo de dilemas — "comportamientos tontos con impacto enorme"

Esto es exactamente lo que pediste. Cada fila: el mecanismo, los números duros, y por qué un comportamiento aparentemente idiota sostiene o destruye una sociedad.

| Dilema | Mecanismo | Números duros | Por qué importa |
|---|---|---|---|
| **PD one-shot vs iterado** | Desertar es estrictamente dominante; el futuro compra la cooperación | Axelrod R=3,S=0,T=5,P=1; TFT 504.5/200 jugadas `[V]`. Iterar sostiene cooperación si **w > c/b** | Lo racional individual es lo peor colectivo. Todo contrato no ejecutable es este juego |
| **Bienes públicos** | PD de N jugadores | Fehr & Gächter `[V]`: sin castigo, **58.9% contribuye CERO** en la ronda final. Herrmann `[V]`: medias de **4.9 (Melbourne) a 11.5 (Copenhague)**. Burton-Chellew & West 2021 *Nat.Hum.Behav.* sobre **237 juegos** `[V]`: el declive lo explica **aprendizaje por pagos**, no erosión de la cooperación condicional | La cooperación decae sola salvo que algo la sostenga |
| **Castigo altruista** | Pagar por dañar a un free-rider sin poder cobrar el beneficio | Fehr & Gächter 2002 *Nature* `[V]`: **84.3% castiga al menos una vez**; **74.2%** de los castigos van de arriba-de-la-media a abajo-de-la-media; con castigo, **77.8% aporta ≥15 de 20** en la ronda final; +1.62 unidades tras ser castigado; z=2.803, P=0.005 | **El gasto irracional es la tecnología que hace posible el bien público** |
| **Castigo ANTISOCIAL** ⚠️ | Pagar por dañar a quien contribuyó **igual o más** que tú | Herrmann, Thöni & Gächter 2008 *Science* `[V]`: **1.120 sujetos, 16 ciudades**. Con castigo: **Zúrich 16.2 vs Atenas 5.7** — el castigo AMPLÍA la varianza entre sociedades. Antisocial: **Mascate ~1.2 vs Boston ~0.1 (12x)**. **Spearman r = −0.90** con cooperación. Normas cívicas −1.093, imperio de la ley −0.641 (p<0.01) | **La misma institución que salva el bien público en Zúrich lo destruye en Atenas.** Datos crudos abiertos: `zenodo.org/records/4969858` |
| **Ultimátum / Dictador** | Veto costoso vs donación pura | Henrich et al. 2001 *AER* `[V]`: oferta media **Machiguenga 0.26 → Lamalera 0.58**, industrializados ≈0.44. Hadza rechazan **43%** de ofertas ≤20%. **Los Au/Gnau rechazan ofertas HIPER-JUSTAS (>50%) casi con la misma frecuencia** | La variación cultural iguala a la variación individual. Es el test de estrés de cualquier simulación de humanos |
| **Confianza** | Enviar se triplica; devolver es voluntario; el equilibrio es enviar 0 | Berg, Dickhaut & McCabe 1995 `[V]`: **30 de 32 envían algo**, media **$5.16**, **12/28 devuelven más de lo enviado**, retorno neto **−$0.50**. Con historia social visible: **+$1.10** | Confiar pierde dinero y 30/32 confían igual. **Mostrar la historia invierte el signo** |
| **Caza del ciervo** | Dos equilibrios: eficiente vs seguro. No hay conflicto de intereses, solo de creencias | Van Huyck, Battalio & Beil 1990 *AER* `[NV en cifras]`: con N=14–16 converge al **peor** equilibrio; con N=2 al eficiente | La coordinación eficiente colapsa con el tamaño del grupo. Es el modelo del cambio institucional |
| **Corridas bancarias** — Diamond & Dybvig 1983 *JPE* | Transformación de vencimientos + servicio secuencial = dos equilibrios con **los mismos fundamentales** | Con depositantes LLM (Harvard 2026) `[V]`: retiro global **30%**; **no asegurados 81.3% vs asegurados 34.5%**; First Republic quiebra al **40%** pese a mejores fundamentales que SVB; **transición de fase abrupta en spillover ≈ 0.10** | **La solvencia bancaria es un hecho social, no contable.** El seguro de depósitos elimina el equilibrio malo sin pagarle a nadie: funciona en la medida en que no se usa |
| **Origen del dinero** — Kiyotaki & Wright 1989 *JPE* ⚠️ | 3 agentes, 3 bienes, sin doble coincidencia de necesidades. ¿Acepto un bien que no consumo? | `[V]` Equilibrio **fundamental** S=(0,1,0) si **C₃−C₂ > ⅓[P₃₁−P₂₁]u₁**. Equilibrio **especulativo** S=(1,1,0) si se invierte | `[V]` En el equilibrio especulativo se acepta el bien **MENOS almacenable**, porque se cree que otros lo aceptarán. **El dinero es un equilibrio de coordinación, no una mercancía.** Es el punto focal de Schelling aplicado a la economía entera |
| **Cascadas informacionales** | Cuando la inferencia sobre acciones ajenas abruma tu señal privada, dejas de aportar información al sistema | BHW 1992 *JPE* `[V]`: con p=0.7 la cascada acierta ≈**0.67 — peor que tu señal sola (0.70)**. Anderson & Holt 1997 *AER* `[V]`: cascadas en **73%** de períodos; **31 de 87 fueron INVERSAS**; y aun así **91% de las decisiones eran bayesianamente correctas** | **La racionalidad individual perfecta produce convergencia colectiva al error** |
| **Falsificación de preferencias** — Kuran 1995 | Umbral de revelación privado e inobservable; la distribución está oculta a todos, incluidos los disidentes | `[NV en detalle]` Equilibrio estable "99% odia el régimen, 0% lo dice"; un disidente marginal dispara la cascada. Con LLMs `[V]`: conformidad **64–94%** pero cascadas exitosas **<26%** | **La revolución es impredecible aunque sea inevitable**: la variable predictiva es, por construcción, inobservable |
| **Concurso de belleza / level-k** | Elige p×(media). Nash = 0. Nadie juega 0 | Nagel 1995 `[V]`: estudiantes **36.73**, prensa **23.08**, teóricos de juegos **18.98**. Picos en 0, 22, 33, 50, 100 = niveles ∞/2/1/0. k=1 en **54%** de la ronda 1 | **La sofisticación óptima es exactamente un nivel por encima de la población — ni más.** Quien juega Nash pierde |
| **Subasta del dólar** — Shubik 1971 | Pagan el primer **y el segundo** postor. Subir siempre parece lo menos malo | `[V]` "Un total de pagos de **tres a cinco dólares** no es infrecuente" por un billete de $1 | Escalada de compromiso. Cada paso es racional, la trayectoria es demencial. **La única jugada ganadora es no jugar** |
| **El Farol Bar** — Arthur 1994 *AER* | 100 personas, umbral 60. Cualquier expectativa compartida se auto-refuta | `[INF]` No existe modelo deductivo consistente → racionalidad **inductiva** con hipótesis heterogéneas. Converge a ≈60 con fluctuación persistente | `[INF]` **Convierte el problema de homogeneidad de los LLMs en una señal medible**: agentes idénticos producirían oscilaciones 0↔100, no convergencia a 60 |
| **Puntos focales** — Schelling | Infinitos equilibrios; la cultura selecciona uno | `[V]` Repartir $100: **36 de 40 reclaman $50**. Cara/cruz: 16/22. ABC: 14/16 | **La selección de equilibrio no la hace la teoría de juegos, la hace la cultura compartida.** Es la unidad atómica de una cultura |
| **Conocimiento común** — Chwe 2001 | Conocimiento común ≠ conocimiento mutuo. Los rituales lo fabrican | `[V]` Super Bowl: **$5M por 30s**, **103.39M espectadores = 68% de EE.UU.** Los bienes con problema de coordinación pagan prima publicitaria | `[INF]` **Kuran + Chwe + Diamond-Dybvig son el mismo mecanismo:** un régimen cae, un banco quiebra y un dinero se adopta porque un evento público convierte conocimiento privado disperso en común |

**Dilemas que valdría la pena mirar y no estaban en tu lista** `[INF]`: el **dilema del voluntario** (la probabilidad de que alguien se ofrezca **DECRECE con N** — el efecto espectador formalizado; barato de simular y contraintuitivo); **gallina/chicken** (ganar = comprometerse creíblemente a ser irracional — y el compromiso de un LLM no es costoso ni verificable, lo cual es en sí un experimento); el **mercado de limones** de Akerlof (colapso por información, no por incentivos); el **juego del ciempiés**; el **naming game / señales de Lewis** (sustrato de las convenciones monetarias, ya instrumentado con LLMs).

---

## 2.3 · Qué se sabe hoy de LLMs jugando estos juegos

Esta es la parte que más cambió mi opinión sobre qué construir.

### Los hallazgos duros

**Akata et al. 2025, *Nature Human Behaviour* 9(7):1380–1390.** `[V]` GPT-3/3.5/4 sobre **1.224 juegos 2×2**. **GPT-4 nunca vuelve a cooperar con un agente que deserta una vez y luego coopera siempre → 0% de recuperación.** Es *nice* y *retaliating* pero **NO *forgiving***: es Grim Trigger, no Tit-for-Tat. Falla en coordinación (Battle of the Sexes) contra un humano que alterna. Con "social chain-of-thought" (predecir la jugada del rival antes de decidir) empieza a alternar desde la ronda 6 (60% de rondas finales). Validado con **195 humanos** reales.
> `[INF]` Le falta exactamente la propiedad que Axelrod identificó como decisiva. **En un torneo con ruido, GPT-4 sería masacrado.**

**Mei, Xie, Yuan & Jackson 2024, *PNAS* 121(9).** `[V]` Contra decenas de miles de humanos de +50 países: los rasgos de GPT-4 son "estadísticamente indistinguibles de un humano aleatorio", y cuando divergen lo hacen **hacia el extremo altruista y cooperativo**. Estimación estructural: los chatbots **actúan como si maximizaran el promedio de su propio pago y el de su pareja** (peso ~0.5 sobre el otro).

**Piatti et al., GovSim, NeurIPS 2024.** `[V]` Comunes con horizonte de 12 meses. **"Todos salvo los agentes LLM más potentes fallan; la tasa de supervivencia más alta está por debajo del 54%."**

| Modelo | Fishery | Pasture | Pollution | **Agregado** | Meses (media) |
|---|:--:|:--:|:--:|:--:|:--:|
| GPT-4o | 100% | 20% | 40% | **53.3%** | 9.3 |
| Claude-3 Opus | 60% | 80% | 20% | **46.7%** | 6.9 |
| GPT-4 | 100% | 0% | 20% | **40.0%** | 6.6 |
| Qwen-110B | 40% | 0% | 20% | **20.0%** | 4.5 |
| Llama-3-70B ↓ | 0% | 0% | 0% | **0%** | 1.0 |

> ⚠️ **El hallazgo más importante de toda esta sección** `[V]`: añadir razonamiento de **universalización** ("¿qué pasa si todos hacen esto?") da **+4 meses, +29 unidades de recurso, +24% de eficiencia** (p<0.001). **Llama-3-70B y Mixtral pasan de 0% a 100% de supervivencia.** Y quitar la comunicación **aumenta la sobreexplotación 22%**.
> `[INF]` **Una sola frase de prompt convierte un modelo que colapsa el 100% de las veces en uno que sobrevive el 100%. La cooperación en LLMs es un problema de framing, no de capacidad.**

**Ashery, Aiello & Baronchelli 2025, *Science Advances* 11.** ⚠️ El más elegante de todos. `[V]` Naming game con N=24 (robusto hasta N=200). **Una convención global emerge en ~15 rondas poblacionales**, sin coordinación central y sin que ningún agente vea el estado global. Y el hallazgo clave: **los agentes son individualmente insesgados en su primera interacción (p = 0.068–0.849), pero las poblaciones convergen de forma no-uniforme.** Hay un sesgo poblacional que no existe en el agente. Masa crítica para voltear una convención establecida: **Llama-3-70B 2%, Claude-3.5-Sonnet ~21%, Llama-2 67%.**
> `[INF]` **Auditar un LLM individualmente no te dice nada sobre el sesgo que producirá una población de esos LLMs.** Es el mejor argumento que existe para hacer simulación multi-agente en vez de evaluación individual. Si el jurado pregunta "¿por qué multi-agente?", esta es la respuesta.

**Payne & Alloui-Cros 2025 (arXiv:2507.02618).** `[V]` Siete torneos evolutivos de PD iterado, LLMs vs estrategias canónicas, variando la probabilidad de terminación.

| Condición | Gemini | OpenAI |
|---|:--:|:--:|
| Terminación 10% | 85.2% | 87.6% |
| Terminación 25% | 76.8% | 87.1% |
| **Terminación 75%** | **2.2%** | **95.7%** |

"Huellas estratégicas" distintas y estables: Gemini = *teórico de juegos calculador, extremadamente sensible al horizonte*; OpenAI = *cooperador de principios y testarudo*; Anthropic = *diplomático sofisticado*. Al 75% de terminación Gemini colapsa a 2.2% de cooperación **y prolifera a 16 agentes**; OpenAI se queda en 95.7% **y es eliminado**. Horizonte mencionado en **94%** de las racionalizaciones de Gemini vs **30%** de OpenAI.
> `[V]` Contraintuitivo: **los modelos modelan MENOS al oponente después de ser traicionados** — lo opuesto a la psicología humana.

**Corridas bancarias con depositantes LLM (Harvard 2026, arXiv:2602.15066).** `[V]` Diamond-Dybvig + red social, calibrado a SVB. Retiro global **30%** — frente a **>99%** de Morris-Shin y a los equilibrios binarios (0%/100%) de Diamond-Dybvig. **No asegurados 81.3% vs asegurados 34.5%.** Contagio: First Republic **40%** y quiebra pese a tener mejores fundamentales que SVB.
> `[INF]` **Los agentes LLM producen un *interior* que los modelos analíticos no producen.** Ese es exactamente el valor añadido que hay que vender.

**Mentira emergente (arXiv:2606.28456, jun 2026).** `[V]` **Sin permiso explícito para mentir: 44% de tasa de engaño. Con permiso: 65%.** Bluffing 17%, diversión 34%, **pero romper compromisos de paz solo 0.4–2%**.
> `[INF]` Asimetría fascinante: **mienten sobre hechos pero honran compromisos.** Esa asimetría es exactamente la variable que determina si una institución funciona.

**"Everyone Conforms, No One Believes" (arXiv:2608.02758, ago 2026).** `[V]` 100 escenarios × 10 dominios × 5 niveles de autoridad, 8 modelos. **Conformidad pública 64–94% pese a oponerse en privado.** Pero **cascadas de ruptura de norma exitosas <26% en 7 de 8 modelos** (GPT-4o outlier a 48%, uno con cero). Quitar el framing de falso consenso: conformidad 52–92% → **el comportamiento es emergente, no inducido**.
> `[INF]` Las poblaciones de LLMs replican **la primera mitad de Kuran** (conformidad con disenso privado) pero **fallan la cascada**. Los humanos de 1989 sí cascadearon. **Ese gap es publicable.**

**Otros que valen la pena:**
- **ALIGN / chisme (arXiv:2602.07777)** `[V]`: **sin chisme, los razonadores cooperan ~0%; con chisme, 69–100%.** Los agentes cross-validan chisme falso contra su propia experiencia — nadie codificó eso. **Lenguaje puro, sin tocar los pagos, lleva la cooperación de 0 a 100.**
- **AgentElect (arXiv:2604.11721)** `[V]`: liderazgo electo vs sin líder: **+55.4% de bienestar social** (p<0.001), **+128.6% de supervivencia**. Los agentes **desarrollan espontáneamente cuotas y monitoreo** — reinventan los principios 1, 4 y 5 de Ostrom sin que nadie se los programe.
- **"Spontaneous Giving and Calculated Greed" (EMNLP 2025)** `[V]`: PD **GPT-4o 95/100 → o1 16/100**; bienes públicos **96/100 → 20/100** (p<0.001). Dosis-respuesta del CoT: 96% → 36% (5-6 pasos) → 33% (15 pasos). **Razonar más los hace más egoístas.**
- **CICERO (Meta, *Science* 2022)** `[V]`: Diplomacy a 7 jugadores, **más del doble del score humano promedio, top 10%**. ⚠️ `[INF]` **CICERO NO es un LLM puro** — es un LLM controlado por un planificador de teoría de juegos. El habla sin planificación no bastó. Dato importante para no sobrevender.

---

## 2.4 · La crítica metodológica ⚠️ — esto es lo que nos puede matar en la presentación

### Contaminación: la evidencia dura

**Gao, Lee, Burtch & Fazelpour 2025, *PNAS* 122.** ⚠️ El paper que hay que conocer.

> 🔴 `[V]` **"Los LLMs alcanzaron 75–100% de precisión reproduciendo las instrucciones del concurso de belleza, pero casi 0% para el juego 11-20 isomorfo, sugiriendo que su éxito previo reflejaba regurgitación de datos de entrenamiento en vez de razonamiento genuino."**

GPT-4 y Claude-3-Opus se agrupan en 19–20 (razonamiento estratégico esencialmente nulo). Todos p<0.001 vs humanos. **No lo arreglan** CoT, few-shot, prompts emocionales ni RAG. Sí lo arregla el fine-tuning (p=0.3417) **pero requirió entrenar con las respuestas humanas reales del estudio: no simuló, memorizó.**

**El protocolo de re-skinning estructural (Georgousis et al. 2026, arXiv:2603.19167).** Cópialo:

| Juego | Manipulación |
|---|---|
| **PD → Stag Hunt** | Cambiar pagos a **R > T ≥ P > S**. Elimina la dominancia estricta; el juego *se ve* idéntico pero el equilibrio cambió por completo |
| **RPS por pagos** | ×3 a Piedra-Papel: rompe la simetría, fuerza mixtas sesgadas |
| **RPS por etiquetas** | Permutar (Tijeras vence a Piedra): desacopla memorización de razonamiento estructural |

`[V]` Mistral Large en "PD con pagos de Stag Hunt": cooperación 18.6 → 29.8 con CoT. **Delay de comprensión m > 16 rondas en algunos modelos — más rondas de las que tiene el horizonte del juego: nunca lo entienden.**

> 🔴 **Regla operativa para nuestro proyecto:** nunca reportar un resultado en un juego canónico sin correr su versión re-skinneada. Cuesta media hora y sin eso un jurado informado nos mata con una pregunta.

### Los LLMs replican la media, no la varianza

**Bisbee et al. 2024, *Political Analysis* 32(4).** `[V]` ChatGPT adoptando personas de respondientes reales del ANES; 3.6M respuestas. **48% de los coeficientes son estadísticamente distintos de los reales; entre esos, el signo se invierte el 32% de las veces.** Y el dato que más asusta: **un análisis de potencia con datos sintéticos sugeriría ~16–35 respondientes donde los reales requieren 129–299** — los datos sintéticos mienten sobre cuánta evidencia tienes por un factor de ~8x.

**Wang, Morgenstern & Dickerson 2025, *Nature Machine Intelligence*.** `[V]` 3.200 humanos, 16 identidades demográficas, 4 LLMs. Los LLMs **aplanan** los grupos. **Ajustar la temperatura NO resuelve la planitud — la limitación es estructural, no un hiperparámetro.**

**Revisión de 21 estudios (arXiv:2506.19806).** `[V]` 14/21 comparan contra ground truth, los 14 chequean la media, **solo 9 evalúan la varianza — y cuando lo hacen, los LLMs muestran MENOR varianza en todos los casos**.

**Aher et al., ICML 2023 — "hyper-accuracy distortion".** `[V]` "Los modelos más grandes y más alineados simulan sujetos que dan respuestas inhumanamente precisas". Replicaron ultimátum y Milgram (75/100 vs 26/40 original) pero **fallaron sabiduría de multitudes** porque la mayoría de agentes acertaba perfectamente.
> `[INF]` **El RLHF elimina exactamente la propiedad que necesitas simular:** la sabiduría de multitudes depende de que los errores sean independientes y se cancelen.

### El contrapunto fuerte (para ser honestos)

**Ashokkumar, Hewitt, Ghezae & Willer 2026, *Nature*.** `[V]` **70 experimentos, 469 efectos, 119.330 participantes.** La correlación LLM↔efectos reales es fuerte, iguala a los pronósticos humanos agrupados, **incluso para estudios publicados DESPUÉS del corte de entrenamiento** (argumento fuerte contra contaminación pura). Caveat: **sobreestiman sistemáticamente los tamaños de efecto**.

> `[INF]` **La distinción que casi todo el debate confunde, y que deberíamos poner en una slide:** los LLMs son **buenos PREDICIENDO efectos agregados de tratamiento** (Ashokkumar) y **malos SIMULANDO distribuciones de comportamiento individual** (Bisbee, Wang, Gao). Para nuestro track, la tarea correcta es la primera.

### ⚠️ La paradoja de la cooperación: la literatura se contradice frontalmente

| Paper | Afirmación |
|---|---|
| "Nicer Than Humans" (ICWSM) | Hipercooperativos, ≥ humano típico |
| Mei et al. (PNAS 2024) | En el extremo altruista |
| Akata et al. (Nat.Hum.Behav. 2025) | Permanentemente implacables, 0% de recuperación |
| GovSim (NeurIPS 2024) | Fallan la sostenibilidad, máx. 53.3% |
| "Corrupted by Reasoning" (COLM 2025) | 69.33% de free-riding en o1-mini |
| **CoopEval (2026)** | **Desertan consistentemente, baseline 0.072/1.0** |

`[V]` El propio paper de fronteras pide "auditorías de contradicción" **y nadie las ha hecho.** Cada paper fija cuatro factores y varía uno. Las variables candidatas son identificables: generación del modelo, presencia de razonamiento, horizonte, framing, rotación de co-jugadores.

---

## 2.5 · Qué añaden los LLMs que el ABM clásico no podía

`[INF]` **La tesis en una frase:** el ABM clásico exige que especifiques el espacio de acciones por adelantado. Un LLM tiene por espacio de acciones **el lenguaje natural**. Es una diferencia categorial, no de grado: si no codificaste "hacer una promesa", en un ABM **nadie puede prometer**. En un agente generativo la promesa aparece porque el lenguaje la contiene.

Evidencia concreta de fenómenos que un ABM de reglas no produce:

- **Chisme** lleva la cooperación de ~0% a 69–100% sin tocar pagos, y los agentes **cross-validan chisme falso contra experiencia propia** — nadie codificó eso `[V]`
- **Mentira endógena** al 44% sin permiso, con una taxonomía emergente (bluff / diversión / traición) que el modelador no definió `[V]`
- **Instituciones emergentes**: cuotas y monitoreo espontáneos (AgentElect); convención global en ~15 rondas con N hasta 200 (Ashery) `[V]`
- **Sesgo colectivo inexistente a nivel individual** (Ashery) — `[INF]` emergencia en sentido fuerte, imposible de detectar auditando agentes sueltos
- **Razonamiento moral inyectable**: universalización 0%→100%. No puedes meter el imperativo categórico en un autómata de estados finitos `[V]`
- **Razonamiento inspeccionable**: Payne codificó racionalizaciones con κ=0.75 y descubrió que los modelos modelan MENOS al rival tras ser traicionados — un mecanismo cognitivo **solo observable porque el agente habla** `[V]`

⚠️ **Contrapeso honesto** `[INF]`: CICERO no es un LLM puro; Concordia (DeepMind) admite que **no presenta evidencia de emergencia y que la validación es "debatible"**; el déficit de varianza anula los fenómenos que dependen de heterogeneidad; el **déficit de castigo (ratio humano 1.66 vs LLM 0.00–0.88)** impide reproducir la institución central de Fehr & Gächter; y el costo cierra el régimen de N grande — **GovSim corre 5 agentes × 12 meses y ya es caro. Hay que diseñar para N pequeño.**

---

## 2.6 · Propuestas de proyecto — tema 2

### 🥇 J1 · ¿Emerge el dinero endógenamente en una población de LLMs? — **8.30/10, viabilidad 8**

**El montaje.** Instanciar Kiyotaki-Wright 1989: 3 tipos de agente, 3 bienes, sin doble coincidencia de necesidades, costos de almacenamiento c₃>c₂>c₁, encuentros bilaterales. **No mencionar nunca la palabra "dinero".** Solo: *"tienes X, quieres Y, este agente tiene Z, ¿intercambias?"* 200 rondas. ¿Converge la población a aceptar sistemáticamente un bien que **no consume**?

**Por qué es nuevo** `[V del hueco]`: busqué explícitamente. **No existe ningún trabajo que corra Kiyotaki-Wright con agentes LLM.** Encaje perfecto con el track: **el origen del dinero es literalmente inaccesible** — ocurrió en el neolítico, sin registro; un caso teórico simulado es el único acceso posible.

**Por qué es interesante en las dos direcciones:**
- Si **emerge** → la coordinación monetaria surge del razonamiento en lenguaje sin institución previa.
- Si **no emerge** → el dinero requiere algo que el lenguaje no provee (probablemente conocimiento común à la Chwe), **y ese es el resultado más fuerte de los dos.**

**Validación en tres vías:**
1. **Contra la teoría.** Las dos condiciones de equilibrio están escritas. Barremos el costo de almacenamiento a ambos lados de `C₃−C₂ = ⅓(P₃₁−P₂₁)u₁` y verificamos si el régimen cambia donde la teoría dice. Esto es un backtest matemático exacto, no una opinión.
2. **Contra humanos.** Duffy & Ochs 1999 *AER* corrieron KW en laboratorio `[NV — verificar]`: el resultado reportado es que los humanos convergen al equilibrio **fundamental** pero **fallan el especulativo**. Si se sostiene, tenemos un test de tres vías teoría / humanos / LLMs.
3. **Test de contaminación integrado.** Versión re-skinneada (bienes con nombres inventados, prohibido usar "dinero", "moneda", "intercambio") vs canónica.

**La extensión de lujo:** añadir un cuarto bien **intrínsecamente inútil y sin costo de almacenamiento** — dinero fiduciario — y ver si lo adoptan. Ese es el experimento que responde la pregunta grande.

### 🥈 J2 · Índice de contaminación por juego × modelo — **7.70/10, viabilidad 9**

6 juegos canónicos × 3 versiones: (a) canónica, (b) re-skinneada semánticamente, (c) **estructuralmente contrafactual** (PD→Stag Hunt). En 4–6 modelos, midiendo comportamiento, comprensión de reglas, y **delay de comprensión m**.

**Por qué es nuevo:** Gao et al. lo hicieron para **un** juego; Georgousis et al. para **dos**. Nadie construyó la batería completa. El producto es un **artefacto reutilizable que todo el campo necesita** y que convierte una queja metodológica en un instrumento.

**Predicción falsable ordenada:** la caída debe ser **mayor para juegos más citados en la web** (el PD más que el dilema del voluntario). Si fuera uniforme, la explicación sería "los prompts raros confunden", no memorización. Y en la condición (c) el modelo **debe** cambiar de comportamiento si razona: **jugar igual en PD y en Stag Hunt con la misma historia es memorización pura, sin ambigüedad interpretativa.**

> 💡 **La jugada del equipo:** J2 corre *dentro* de J1 como control metodológico. Es el arnés de validación que discutimos ayer, materializado. Dos entregables, un solo proyecto.

### J4 · La cascada que no ocurre — **8.15/10, viabilidad 7**
Población con **distribución explícita e inducida de umbrales de revelación** (unos hablan si 5% ya habló, otros necesitan 50%). Tres shocks: (a) un disidente extra, (b) un **anuncio público** que crea conocimiento común, (c) la misma información **en privado a cada agente**. ¿Cuál dispara la cascada? El paper de agosto 2026 encontró el fallo pero **no manipuló ni la distribución de umbrales ni la estructura de conocimiento**. La pregunta abierta: ¿la cascada falla porque los LLMs son homogéneos, o porque no distinguen conocimiento mutuo de común? **Son diagnósticos opuestos y nadie los ha separado.** La manipulación (b) vs (c) es un test directo de la teoría de Chwe.

### J6 · ¿Son extorsionables los agentes LLM? — **8.20/10, viabilidad 8**
Agentes LLM contra una estrategia de determinante cero extorsionadora con χ = 2, 3, 5. `[V del hueco]` **Toda la literatura LLM-IPD usa el zoo canónico de Axelrod. Nadie ha puesto LLMs contra estrategias ZD.** La teoría hace una predicción precisa: un agente que sigue cualquier trayectoria de mejora de pago **debe ser exitosamente extorsionado**. Un LLM que reconoce la extorsión y prefiere la deserción mutua exhibiría algo que la teoría no captura. **Cruce elegante con Payne & Alloui-Cros: predicción concreta — Gemini debería resistir, OpenAI debería capitular.** Lectura de seguridad IA directa.

### J3 · Castigo antisocial transcultural — **7.60/10, viabilidad 8**
Reproducir Herrmann et al. 2008 con parámetros exactos, condicionando agentes al contexto de las 16 ciudades. ¿Recuperamos el rango 5.7 (Atenas) – 16.2 (Zúrich) y r = −0.90? **Probablemente no, y por eso importa:** todos los LLMs tienen ratio castigo/recompensa 0.00–0.88 vs 1.66 humano. **Documentar el fallo con 16 puntos de datos reales y una correlación esperada es un resultado limpio.** Mejor validación del documento: **datos crudos por sujeto en `zenodo.org/records/4969858`** — comparamos contra distribuciones completas, no contra medias de un abstract.

### J5 · Auditoría de contradicción — **7.50/10, viabilidad 8**
Factorial completo: razonamiento × horizonte × co-jugador × framing × generación. Convertir siete papers contradictorios en una tabla ANOVA. Resultado esperado y no obvio: **que la varianza explicada por razonamiento y rotación domine sobre la varianza entre modelos** — es decir, *"¿cooperan los LLMs?" es una pregunta mal planteada*.

### J7 · Ostrom como diseño de mecanismos — **7.80/10, viabilidad 7**
Implementar los 8 principios como módulos activables sobre GovSim y ablacionar. **Predicción no obvia** `[INF]`: los principios que dependen de **castigo** (sanciones graduadas) fallarán — los LLMs no castigan — mientras que los que dependen de **comunicación y compromiso** funcionarán desproporcionadamente bien. **Si se confirma: las sociedades de LLMs necesitan un diseño institucional DISTINTO al humano.**

---

## 2.7 · Tres decisiones de método si vamos por aquí `[INF]`

1. **La barra de error debe ser sobre PARÁFRASIS DEL PROMPT, no sobre temperatura.** La evidencia dice que la temperatura mueve poco (r>0.97 entre 0.1 y 1.0) y el framing lo mueve todo (0%→100%). **Reportar semillas de temperatura es teatro estadístico.** N≥5 paráfrasis independientes.
2. **Toda condición canónica lleva su gemela re-skinneada.** Es el estándar de Gao et al. (PNAS) y cuesta media hora.
3. **Reportar la varianza, no solo la media.** Solo 9 de 21 papers lo hacen, y cuando lo hacen los LLMs siempre pierden. **Reportarla y perder es honesto y publicable; omitirla es el error modal del campo.** La ratio "varianza LLM / varianza humana" resume el estado del arte en un número.

---
---

# TEMA 1 · Segregación de Schelling

## 1.1 · El core

**Schelling, T. C. (1969).** "Models of Segregation." *American Economic Review* 59(2):488–493. `[V]`
**Schelling, T. C. (1971).** "Dynamic Models of Segregation." *Journal of Mathematical Sociology* 1(2):143–186. `[V]`
**Nobel de Economía 2005** (compartido con Aumann). `[V]`

`[V]` Dato poco citado: **James M. Sakoda** desarrolló un modelo de tablero equivalente en su tesis de 1949, publicado en 1971 en el mismo volumen del *JMS* (Hegselmann 2017, *JASSS* 20(3)).

**Son dos modelos, no uno** — se confunden todo el tiempo `[V]`:

1. **Modelo espacial de tablero** (el famoso): retícula con dos tipos de agente y celdas vacías. Cada agente mira su vecindario de Moore (8 vecinos), está contento si la fracción de vecinos iguales ≥ *T*, y si no se muda a la vacante más cercana que lo satisfaga.
2. **Modelo de "tipping" / vecindario acotado** (agregado, no espacial): cada individuo tiene un umbral máximo de proporción del otro grupo que tolera; la distribución de umbrales genera curvas cruzadas cuyos **equilibrios interiores son inestables**. De aquí sale formalmente el concepto de *tipping point*.

### Los números — y por qué el "30%" es una cifra de póster

La divulgación dice: por debajo de ~30% de preferencia por vecinos propios el sistema se queda aleatorio, por encima colapsa a segregación. **No es un teorema.** `[V como afirmación de la fuente divulgativa]`

Los números robustos son de **Singh, Vainchtein & Weiss 2009, *Demographic Research* 21(12):341–366** `[V]`:

| Umbral | Comportamiento |
|---|---|
| **T = 3** (≥3 de 8 = 37.5%) | La segregación es **estrictamente un fenómeno de ciudad pequeña**. En N=100 aparecen **22–55 clusters** en vez de 1–2. Escalamiento cúbico con la fracción de vacantes |
| **T = 4** (50%) | Clusters compactos, agregación a mesoescala, escalamiento lineal. Agentes con vecinos exclusivamente iguales: **~40% (vs ~10% con T=3)** |
| **T = 5** (62.5%) | Un solo cluster grande y muchos agentes permanentemente infelices — el algoritmo estándar deja de converger |

⚠️ `[V]` **Dependencia invertida de las vacantes:** con T=3 la agregación **crece** con la razón de vacantes; con T=4 **decrece**. Crítico y contraintuitivo.

> `[INF]` **Lo defendible no es un número, es que existe una transición de fase en el espacio (umbral × densidad de vacantes × tamaño de vecindario).** Un buen demo barre los tres ejes, no solo el umbral.

**La medición empírica definitiva:** **Card, Mas & Rothstein 2008, *QJE* 123(1):177–218.** `[V]` Regresión discontinua sobre tracts censales 1970–2000, **114 áreas metropolitanas**, ~40.000 tracts por década. **Los tipping points reales están entre 5% y 20% de share minoritaria.** Medias por década: **11.87% → 13.53% → 14.46%**. Son **más bajos** donde las actitudes raciales son menos tolerantes (coef. −3.0): la diferencia Memphis–San Diego implica ~7.5 puntos de diferencia en el tipping point.

## 1.2 · La física detrás (lo más fuerte técnicamente)

**Vinković & Kirman 2006, *PNAS* 103(51):19261–19265.** `[V]` Sustituyen **la "utilidad" del agente por la "energía interna" de una partícula**. Bajo esa traducción, la dinámica de clusters queda gobernada por **tensión superficial** — el mismo mecanismo que rige las gotas. **Las poblaciones segregadas se comportan como fluidos inmiscibles** (agua/aceite).

**Dall'Asta, Castellano & Marsili 2008, *J. Stat. Mech.* L07002.** `[V]` Formalización con spines σᵢ ∈ {0, ±1}. Exponente dinámico **z = 2** — coarsening tipo Ising/Allen-Cahn. Umbral de percolación de vacíos en 2D: **0.45 < ρ̂₀ < 0.5**.

> ⚠️ **El hallazgo más citable de esta sección** `[V]`: existen **estados desordenados atrapados**. La segregación falla en **ambos extremos** — cuando los agentes son extremadamente intolerantes *y* cuando aceptan tener solo un vecino igual. **El mapeo umbral→segregación no es monótono.** Los autores conectan esto con **modelos con restricciones cinéticas**, la clase usada para vidrios estructurales.
>
> `[INF]` **En lenguaje de política pública: un barrio puede quedar bloqueado en una configuración que ninguna política de preferencias puede desbloquear, porque el problema es cinético — no hay camino de movimientos individualmente mejorantes hacia el óptimo — no de preferencias.**

## 1.3 · La extensión que más importa

**Pancs & Vriend 2007, *Journal of Public Economics* 91(1–2):1–24.** `[V]` Confirmado textualmente:

> *"even if all individual agents have a strict preference for perfect integration, best-response dynamics may lead to segregation."*

Testean cuatro funciones de utilidad, incluida una con **pico simétrico en 50-50 y sin ningún sesgo hacia los propios**. Simulación grande: tablero 100×100, 4.000 agentes por tipo, 50 millones de períodos.

`[INF]` **Por qué ocurre, sin exagerar la afirmación:** los agentes no *quieren* segregación. Pero bajo dinámica de mejor respuesta cada uno elige la mejor posición **disponible dado el estado actual**, y como el 50-50 exacto en un vecindario de 8 es un blanco estrecho, y el movimiento de uno cambia el vecindario de todos, el sistema no puede coordinarse en el punto que todos prefieren. **La segregación aquí no es un óptimo individual, es un fallo de coordinación.**

**La conclusión de política, textual** `[V]`: la educación que promueve tolerancia **puede empeorar los resultados**; se requieren **mecanismos gubernamentales de coordinación** además de políticas que moldeen preferencias.

**O'Sullivan 2009, *RSUE* 39(4):397–408** `[V]` llega a lo mismo por otro camino (mercado de suelo con puja competitiva) y añade algo infrautilizado: **la segregación es ineficiente en términos de mercado** — reduce la disposición agregada a pagar por el suelo. Es un **argumento de eficiencia, no de equidad**, a favor de la integración.

⚠️ **Debate abierto que hay que mencionar para ser honestos:** Bruch & Mare 2006 (*AJS* 112(3)) argumentan que la segregación alta requiere una **función escalón**, y que con preferencias continuas estimadas de encuestas reales (MCSUI, 4.025 encuestados en LA) la segregación resultante es ≈0.1 vs el 0.6–0.8 real. **Van de Rijt, Siegel & Macy 2009 (*AJS* 114(4)) replican que eso es un artefacto de implementación.** `[V-parcial]` La formulación defendible: *la forma de la función de preferencia es un parámetro de primer orden cuyo efecto es objeto de disputa metodológica activa.*

## 1.4 · Aplicaciones fuera de segregación racial

**Mercado laboral — el mejor resultado y el menos conocido.** **Pan 2015, *Journal of Labor Economics* 33(2).** `[V]` Es literalmente Card-Mas-Rothstein aplicado a ocupaciones. Censo de EE.UU. 1940–1980, ocupación × estado:
- **Cuello blanco: tipping point en 30–60% de participación femenina.**
- **Cuello azul: 12–25%.**
- **Magnitud del salto: caídas de 18 a 50 puntos porcentuales** en el crecimiento neto del empleo masculino.
- **Validación del mecanismo:** los tipping points son más bajos donde los hombres sostienen actitudes más sexistas (GSS 1977–1998).

> `[INF]` **Esto es la mejor evidencia disponible de que la dinámica de Schelling es sustrato-independiente, empíricamente y no solo teóricamente.** Misma estructura identificativa, dominio completamente distinto, mismo mecanismo, misma prueba de placebo.

**Sorteo político.** **Brown & Enos 2021, *Nature Human Behaviour* 5(8):998–1008.** `[V]` **n = 180.660.202 votantes registrados individuales**, con índices de aislamiento espacialmente ponderados para el entorno inmediato de *cada* votante. *"Demócratas y republicanos que viven en la misma ciudad, o incluso el mismo barrio, están segregados por partido."*
> `[INF]` **El debate Bishop vs. Fiorina se resuelve con Schelling:** Fiorina medía a nivel de condado y no encontró el sorteo; Brown & Enos midieron a escala de vecindario y sí. **Schelling predice exactamente eso** — la segregación es local y se promedia hacia cero en agregados grandes. Fiorina miraba a la escala equivocada.

**Escuelas.** **Stoica & Flache 2014, *JASSS* 17(1):5.** `[V]` **La preferencia por distancia SUPRIME la tendencia a la segregación auto-organizada.** Y el insight crítico: **unidades locales más grandes preservan la integración cuando la composición coincide con las preferencias, pero disparan cascadas cuando no coincide.**
> `[INF]` **El tamaño del "vecindario" es una variable de diseño de política, no un dato de la naturaleza.**

**Redes sociales.** **Henry, Prałat & Zhang 2011, *PNAS* 108(21):8605–8610.** `[V]` Más fuerte que Schelling: con una **leve aversión** a mantener lazos disímiles y **ninguna preferencia positiva** por lazos homogéneos, **las redes segregadas emergen SIEMPRE, sin importar el nivel de aversión** — incluso infinitesimal. **La homofilia no es necesaria para la segregación.**

**Cultura.** Gracia-Lázaro et al. 2009, *Phys. Rev. E* 80(4):046123 `[V]` — híbrido Axelrod-Schelling. **Paradoja verificada: aumentar la diversidad cultural inicial paradójicamente aumenta la convergencia hacia una cultura dominante** en ciertos regímenes.

### ⚠️ Mercados financieros y monetarios — HAY UN HUECO REAL

`[V]` Se buscó con **cuatro estrategias distintas** (Schelling + mercados/herding/segmentación; Schelling + crédito/redlining/asignación de capital; tipping point + hipotecas + ABM; segregación + banca + exclusión financiera). **Resultado: NO existe literatura de segregación tipo Schelling en crédito, asignación de capital o mercados financieros.**

Lo más cercano: un Schelling heterogéneo en riqueza (ACM EAAMO 2022), Schelling + mercado de suelo (O'Sullivan 2009), Schelling + ingreso y precios (Sethi & Somanathan 2004, *JPE* 112(6)). Y del lado empírico, econometría descriptiva de redlining sin modelo de agentes.

> **Dado que el redlining es *literalmente* una regla de umbral aplicada a unidades geográficas, la ausencia de esta literatura es notable.** Es el hueco más limpio del tema 1.

## 1.5 · Datos y métricas

**Índices estándar** `[V]`:
- **Disimilitud D** = ½ Σ |xᵢ/X − yᵢ/Y|. Fracción del grupo minoritario que tendría que mudarse para lograr distribución uniforme. Rango [0,1].
- **Aislamiento** ₓP*ₓ = Σ (xᵢ/X)(xᵢ/tᵢ). ⚠️ **Sensible al tamaño relativo del grupo** — peor para comparar entre ciudades.
- **Theil's H** (multigrupo, entropía). **Ventaja decisiva: es descomponible aditivamente** — puedes atribuir la segregación total a componentes geográficos anidados *y* a variables cruzadas (raza × ingreso).

**Datos EE.UU.** `[V]`: ACS/Censo por tract; **Neighborhood Change Database** (tracts armonizados a fronteras constantes 1970–2010 — el único que permite series temporales limpias); **HMDA** (todas las solicitudes hipotecarias georreferenciadas con raza e ingreso — *el* dataset para el hueco financiero); Mapping Inequality (mapas HOLC 1935-40 digitalizados); Opportunity Atlas (20.5M niños).

**Datos Colombia** `[V]`:
- **CNPV 2018 (DANE)** — datos a **escala de manzana censal**, resolución equivalente o mejor que un tract de EE.UU.
- **Encuestas de Movilidad** Bogotá 2019, Medellín 2017, Cali 2015 → permite medir **exposición efectiva**, no solo residencial.
- **Estratificación socioeconómica (1–6)** — datos abiertos de Bogotá.

**Estudio de referencia colombiano** `[V]`: Mayorga Henao 2023, *Territorios* (48). Distribución por calidad de vida: Bogotá 31% bajo / 50% medio / 19% alto. **Probabilidad de interacción entre grupos bajo–alto: 4%–5% en Bogotá, Medellín y Cali.** Nivel de aislamiento extremo.

> ⚠️ `[INF]` **El caso colombiano es único y no lo he visto explotado.** El estrato socioeconómico es una **etiqueta institucional visible y oficial** asignada a cada manzana, que determina tarifas de servicios públicos y acceso a subsidios. Es decir: **Colombia tiene un sistema donde el "tipo" del agente de Schelling está impreso en el mapa por el Estado.** No conozco otro país con este diseño. Eso convierte a Bogotá en un laboratorio natural para separar preferencias endógenas de clasificación institucional — algo imposible con datos de EE.UU.

## 1.6 · Propuestas de proyecto — tema 1

### S2 · El núcleo crítico: la intervención mínima que revierte la segregación — **8.40/10, viab 7**
Pancs & Vriend concluyen que hacen falta "mecanismos de coordinación" **pero no especifican cuáles ni cuantifican nada.** O'Sullivan prueba tres políticas **sin costos ni comparación**. Y **CMTO (Bergman, Chetty et al. 2024, *AER* 114(5))** demuestra empíricamente que una intervención de coordinación funciona — **elevó del 15% al 53%** la proporción de familias que se mudan a barrios de alta movilidad, y **el componente que hizo el trabajo fue la asistencia de búsqueda personalizada, no el dinero** `[V]` — **pero no la modela ni la extrapola a equilibrio.**

**Nadie ha unido las tres piezas.** `[INF]` **El giro que lo hace nuevo:** si el problema es de coordinación y no de preferencias, la política óptima puede ser **temporal y no monetaria** — mover a *k* familias **simultáneamente** en lugar de secuencialmente puede lograr con presupuesto cero lo que millones en subsidios secuenciales no logran. **Nadie ha calculado ese *k*.** En física es trivial de formular: es el tamaño de núcleo crítico de una nucleación heterogénea. En política pública nadie lo ha planteado.

**Validación:** replicar el 15%→53% de CMTO como calibración, y luego extrapolar a equilibrio de largo plazo — algo que el experimento real, por diseño, no puede observar.

### S4 · Tamaño óptimo de la unidad institucional — **8.35/10, viab 8**
`[INF]` **La propuesta más accionable de todo el documento.** Stoica & Flache demuestran que el tamaño de la unidad local es una variable de primer orden pero **solo comparan dos tamaños y no optimizan**. La pregunta: ¿existe un tamaño de unidad *L\** que minimiza la segregación de equilibrio, y es **interior**? Probablemente sí — hay un trade-off documentado (grandes preservan pero disparan cascadas).

**Por qué es la palanca más barata que existe:** el tamaño de la zona escolar, la definición de la Unidad de Planeamiento Zonal, el radio de un distrito electoral **son variables que un gobierno controla directamente con costo cercano a cero.** No requieren cambiar preferencias, ni presupuesto, ni consenso político sobre raza. **Y están completamente sin estudiar.**

### S1 · El tipping point del crédito — **7.95/10, viab 6**
¿Existe una fracción crítica de rechazo hipotecario o de retiro de sucursales por encima de la cual un barrio "voltea" irreversiblemente hacia la exclusión financiera? El redlining **es** una regla de umbral geográfica, con una asimetría que Schelling no tenía: **la retroalimentación es de segundo orden** (menos crédito → menor mantenimiento y valor → peor perfil de riesgo → menos crédito). `[INF]` En lenguaje de Dall'Asta et al., no es un ferromagneto: es uno donde **el acoplamiento J depende del estado local — un vidrio de espín con desorden auto-generado.** Datos: HMDA + FDIC Summary of Deposits + Mapping Inequality, todo público y georreferenciado.

### S5 · Los estratos de Bogotá como Schelling institucionalizado — **7.90/10, viab 7**
El más relevante localmente. Colombia asigna oficialmente un "tipo" a cada manzana. La pregunta: **¿cuánta de la segregación observada en Bogotá es preferencia y cuánta es la clasificación misma?** Contrafactual: correr la ciudad con y sin la etiqueta visible. Validación contra el 4–5% de probabilidad de interacción bajo–alto medido por Mayorga Henao.

### S3 · Longitud de correlación del sorteo partidista — **7.45/10, viab 7**
`[INF]` Calcular D y H a escalas anidadas (manzana → tract → condado → estado) y ajustar la ley de escalamiento. **Un sistema cerca de una transición de fase tiene longitud de correlación divergente.** Si la longitud de correlación del sorteo está creciendo, es una firma **medible y falsable** de que el sistema se acerca a una transición — reemplaza la discusión cualitativa sobre polarización con un número.

---
---

# TEMA 3 · FlyWire — no los sentidos, la perturbación

## 3.1 · El reframe que pediste, y por qué es el correcto

Tu instinto de mover el foco de "recrear los sentidos" a "estimular para explicar cosas" **es exactamente el estado del arte.** El campo llama a esto ir del **conectoma** (quién se conecta con quién) al **efectoma** (quién causa qué en quién).

**Los números base** `[V]`: la reconstrucción completa del cerebro de una mosca adulta — **~139.000 neuronas, ~50 millones de sinapsis** (FlyWire, *Nature*, oct 2024). Público, versionado (v783 en Zenodo), con API en Python (`fafbseg` / `navis`) y navegador web (Codex). **Corre en un portátil.**

Y el dato que casi nadie menciona pero lo cambia todo: **cada sinapsis tiene un neurotransmisor predicho** a partir de las imágenes de microscopía electrónica (Eckstein et al. 2024, *Cell*). No solo sabes quién se conecta con quién — **sabes con qué química.**

## 3.2 · Las cuatro capacidades reales

### (a) Optogenética virtual — activar o silenciar cualquier neurona

**Shiu et al. 2024, *Nature*.** `[V]` Modelo de integración-y-disparo con fugas (LIF) sobre el conectoma completo en Brian2, con neurotransmisores predichos. **Solo un parámetro libre** (Wsyn); todo lo demás sale del conectoma o de literatura previa.

Lo que hicieron y validaron:
- Activaron neuronas gustativas (azúcar, agua, amargo) a 10–200 Hz y predijeron el patrón de disparo de las motoneuronas de la probóscide.
- **Validación experimental: activación optogenética de 106 tipos celulares en la mosca real, con >90% de precisión de predicción a 50 Hz.** `[V]`
- Predijeron que las neuronas Ir94e son inhibitorias; el experimento lo confirmó.
- Silenciamiento individual de las neuronas más activas para identificar cuáles son **necesarias** para el output motor.

> `[INF]` **Esto es el track puro:** silenciar una a una 139.000 neuronas y ver qué se rompe es un experimento **imposible en vivo** — costaría décadas y millones. En silico es un bucle `for`.

### (b) El efectoma — inferencia causal sobre un cerebro completo

**Pospisil, Aragon & Pillow et al. 2024, *Nature*** ("The fly connectome reveals a path to the effectome"). `[V]` La pregunta: el conectoma te da la anatomía, no la fuerza funcional. La solución: **variables instrumentales** — el láser optogenético es un instrumento que empuja neuronas independientemente de confusores no observados — **usando el conectoma como prior**.

Resultados:
- Modelo dinámico: autorregresivo vectorial de primer orden, `r(t+1) = W·r(t)`.
- **El estimador bayesiano informado por conectoma mejora la velocidad de convergencia en al menos un orden de magnitud** frente al IV ingenuo.
- ⚠️ **Los circuitos dominantes involucran poblaciones pequeñas: menos del 10% del cerebro basta para explicar los modos dinámicos principales. Los primeros 10 autovectores involucran ~50 neuronas.**
- Redescubre circuitos conocidos (detección de movimiento oponente) y **propone nuevos** (winner-take-all en el cuerpo elipsoide).

### (c) Farmacología in-silico — lo que más potencial tiene `[INF]`

Como cada sinapsis tiene neurotransmisor predicho, **puedes apagar globalmente un sistema neuroquímico entero y ver qué le pasa al cerebro completo.** Eso es, funcionalmente, **administrar una droga a un cerebro simulado**.

`[V del hueco, según mi búsqueda]` No encontré trabajo que haga esto sistemáticamente sobre el conectoma completo. Es el análogo neurocientífico exacto del hueco de Kiyotaki-Wright: **una pregunta cuya respuesta requiere un experimento que nadie va a correr.**

### (d) Interpretabilidad mecanicista sobre un cerebro real `[INF]`

El argumento que más me gusta y el que puntúa más alto (**8.60**): el conectoma de la mosca es **la única red neuronal biológica cuyo cableado completo conocemos**. Eso la pone, metodológicamente, en la misma categoría que un LLM: una red donde puedes hacer ablaciones, trazado de circuitos, y análisis de activación **con acceso total a los pesos**.

**La pregunta:** ¿funcionan los métodos de interpretabilidad mecanicista de IA sobre un cerebro real? Y al revés: ¿los métodos de neurociencia de sistemas encuentran algo que los de IA no?

`[INF]` Es genuinamente novedoso y encaja con el track por una vía distinta: la información no accesible no es sobre la mosca, **es sobre si nuestras herramientas de entender redes funcionan cuando la red no la diseñamos nosotros.**

## 3.3 · Propuestas de proyecto — tema 3

| # | Propuesta | Total | Viab | Nota |
|---|---|:--:|:--:|---|
| **F3** | **Interpretabilidad mecanicista sobre un cerebro real.** Aplicar ablación, trazado de circuitos y análisis de activación (métodos de IA) al conectoma completo. ¿Encuentran los mismos circuitos que la neurociencia? | **8.60** | 6 | El puntaje técnico más alto del documento (10/10). Encaje conceptual raro y memorable |
| **F1** | **Farmacología in-silico.** Apagar sistemas neurotransmisores completos sobre el cerebro entero y mapear el efecto conductual. Un "atlas de drogas virtuales" | **8.35** | 6 | Hueco aparente. Demo visualmente espectacular |
| **F2** | **Efectoma.** Estimar la matriz causal W con variables instrumentales y buscar los circuitos dominantes. ¿Se sostiene el <10%? | **8.05** | 5 | Máximo técnico pero **el más riesgoso**: requiere reproducir un paper de *Nature* en horas |
| **F4** | **Lesión y compensación.** Barrido sistemático de lesiones: ¿qué neuronas son cuellos de botella? ¿Se reorganiza el cerebro? ¿Hay redundancia? | **8.00** | 7 | El más viable del grupo. Puro bucle de perturbación con métricas de grafo |

## 3.4 · La advertencia honesta ⚠️

`[INF]` Tres cosas que hay que decir en voz alta antes de comprometerse:

1. **El conectoma es el cableado, no el software.** Tienes quién se conecta con quién y con qué neurotransmisor. **No tienes los pesos sinápticos reales ni los neuromoduladores.** El modelo de Shiu et al. tiene un solo parámetro libre porque *asume* que todas las sinapsis pesan igual. Funciona sorprendentemente bien, pero es una aproximación fuerte.
2. **El puntaje de impacto es el más bajo de los tres temas (5–8).** El track premia información nueva sobre **el mundo**. "Así responde un cerebro de mosca simulado" es fascinante y difícil de volver accionable en un pitch de 3 minutos.
3. **La viabilidad es 5–7, la peor del documento.** Si a la hora 30 no corre, no hay demo.

> **Mi propuesta sobre este tema:** no como proyecto principal. Como **segunda mitad de la demo** — *"y este mismo motor de perturbación lo corrimos sobre un cerebro real de 139.000 neuronas"* — es un final de presentación que nadie más va a tener. **Decisión a la hora 24, no a la hora 0.**

---
---

# 4 · Síntesis: qué llevo a la mesa

## 4.1 · Los tres huecos verificados

Esto es lo que aporto de más concreto. Los tres se confirmaron con búsqueda explícita, no son intuición:

| Hueco | Estado | Qué habilita |
|---|---|---|
| **Nadie ha corrido Kiyotaki-Wright con agentes LLM** | `[V]` búsqueda explícita | J1 — la emergencia del dinero |
| **No existe literatura de Schelling en crédito / asignación de capital** | `[V]` cuatro estrategias de búsqueda | S1 — el tipping point del crédito |
| **Nadie ha puesto LLMs contra estrategias de determinante cero** | `[V]` búsqueda explícita | J6 — extorsión de agentes |

## 4.2 · El patrón que conecta los tres temas `[INF]`

Los tres temas son **la misma pregunta a distinta escala**:

**Schelling** → cómo un umbral local produce una estructura global que nadie quería.
**Dilemas** → cómo una regla de decisión individual produce una institución (o su colapso).
**FlyWire** → cómo la conectividad local produce comportamiento.

En los tres, **el objeto de estudio es el salto de la regla micro al fenómeno macro**, y en los tres **el dato que falta es contrafactual**: qué habría pasado con otro umbral, otra norma, otro cableado. Si presentamos el proyecto, ese es el marco.

Y hay un puente concreto entre el tema 1 y el 2 que no vi hecho en ninguna parte `[INF]`: **Pancs & Vriend dicen que la segregación es un fallo de coordinación, no de preferencias. Kiyotaki-Wright dice que el dinero es un equilibrio de coordinación. Chwe dice que el conocimiento común es lo que selecciona el equilibrio.** Son el mismo mecanismo mirado desde tres disciplinas que no se citan entre sí.

## 4.3 · Lo que propongo al equipo

**Proyecto:** J1 (emergencia endógena del dinero con agentes LLM) con J2 (batería de re-skinning) incrustado como control metodológico.

**Puntaje ponderado 8.30, viabilidad 8.** No es el número más alto de la tabla, pero **es el mejor ajustado por riesgo**, está en el hueco más limpio que encontré, y tiene tres vías de validación independientes — incluida una **matemáticamente exacta** contra las condiciones de equilibrio de Kiyotaki-Wright.

**La frase completa:**
> *Nuestra simulación responde **si el dinero puede emerger de puro razonamiento en lenguaje sin ninguna institución previa**, que hoy nadie puede responder porque **el origen del dinero ocurrió en el neolítico y no dejó registro**, y vamos a saber que funciona porque **la transición entre el equilibrio fundamental y el especulativo tiene una condición matemática cerrada que podemos verificar, y porque la versión re-skinneada del juego debe dar el mismo resultado que la canónica**.*

## 4.4 · Preguntas para el mentor (CTO de Platanus)

1. **¿Un resultado negativo bien medido puntúa igual que uno positivo?** Varias de estas propuestas son más fuertes si fallan (J1, J3). Necesito saber si el jurado lo compra antes de comprometernos.
2. **¿Qué separa una simulación que produce información nueva de una demo bonita?** Su criterio específico, no el enunciado público.
3. **¿Cuánto pesa que el resultado sea verificable contra la realidad vs. exploratorio pero ambicioso?** Si dice "exploratorio", FlyWire sube de 6 a primera opción.
4. **Un proyecto de alto riesgo que falla parcialmente, ¿puntúa mejor que uno seguro que funciona completo?** Ambición 20% vs ejecución 20% — necesito saber cómo se rompe ese empate.
5. **¿Cuál es el error más común que ven en este track?** Pregunta barata, respuesta cara.

---

## 5 · Fuentes principales

**Schelling y segregación**
Schelling 1969 *AER* 59(2) · Schelling 1971 *JMS* 1(2):143–186 · Card, Mas & Rothstein 2008 *QJE* 123(1):177–218 · Vinković & Kirman 2006 *PNAS* 103(51) · Dall'Asta, Castellano & Marsili 2008 *J.Stat.Mech.* L07002 · Pancs & Vriend 2007 *J.Pub.Econ.* 91(1–2) · Bruch & Mare 2006 *AJS* 112(3) · Van de Rijt, Siegel & Macy 2009 *AJS* 114(4) · Singh, Vainchtein & Weiss 2009 *Demographic Research* 21(12) · O'Sullivan 2009 *RSUE* 39(4) · Sethi & Somanathan 2004 *JPE* 112(6) · Pan 2015 *JOLE* 33(2) · Brown & Enos 2021 *Nat.Hum.Behav.* 5(8) · Stoica & Flache 2014 *JASSS* 17(1) · Henry, Prałat & Zhang 2011 *PNAS* 108(21) · Gracia-Lázaro et al. 2009 *Phys.Rev.E* 80(4) · Chetty, Hendren & Katz 2016 *AER* 106(4) · Bergman, Chetty et al. 2024 *AER* 114(5) · Mayorga Henao 2023 *Territorios* (48)

**Teoría de juegos y cooperación**
Axelrod 1980a/b *JCR* 24(1),(3) · Axelrod & Hamilton 1981 *Science* 211 · Press & Dyson 2012 *PNAS* 109(26) · Stewart & Plotkin 2013 *PNAS* · Hilbe, Nowak & Sigmund 2013 *PNAS* · Nowak 2006 *Science* 314(5805) · Ostrom 1990 *Governing the Commons* · Fehr & Gächter 2002 *Nature* · Herrmann, Thöni & Gächter 2008 *Science* (datos: zenodo.org/records/4969858) · Henrich et al. 2001 *AER* · Berg, Dickhaut & McCabe 1995 · Diamond & Dybvig 1983 *JPE* 91(3) · Kiyotaki & Wright 1989 *JPE* 97(4) · Bikhchandani, Hirshleifer & Welch 1992 *JPE* · Anderson & Holt 1997 *AER* · Kuran 1995 *Private Truths, Public Lies* · Chwe 2001 *Rational Ritual* · Nagel 1995 · Shubik 1971 *JCR* 15(1) · Arthur 1994 *AER* 84(2) · Burton-Chellew & West 2021 *Nat.Hum.Behav.*

**LLMs como agentes**
Akata et al. 2025 *Nat.Hum.Behav.* 9(7) (arXiv:2305.16867) · Mei, Xie, Yuan & Jackson 2024 *PNAS* 121(9) · Horton 2023 NBER w31122 · Aher, Arriaga & Kalai 2023 ICML (arXiv:2208.10264) · Argyle et al. 2023 *Political Analysis* 31(3) · Piatti et al. 2024 NeurIPS, GovSim (arXiv:2404.16698) · Ashery, Aiello & Baronchelli 2025 *Science Advances* 11 · Payne & Alloui-Cros 2025 (arXiv:2507.02618) · CICERO, Meta 2022 *Science* 378(6624) · Concordia, DeepMind (arXiv:2312.03664) · CoopEval 2026 (arXiv:2604.15267) · AgentElect 2026 (arXiv:2604.11721) · ALIGN 2026 (arXiv:2602.07777) · Bank runs con LLMs 2026 (arXiv:2602.15066) · "Is Lying an Emergent Behaviour?" 2026 (arXiv:2606.28456) · "Everyone Conforms, No One Believes" 2026 (arXiv:2608.02758) · "Spontaneous Giving and Calculated Greed" EMNLP 2025 · "Corrupted by Reasoning" COLM 2025

**Crítica metodológica**
Gao, Lee, Burtch & Fazelpour 2025 *PNAS* 122 (arXiv:2410.19599) · Georgousis et al. 2026 (arXiv:2603.19167) · Bisbee et al. 2024 *Political Analysis* 32(4) · Wang, Morgenstern & Dickerson 2025 *Nat.Mach.Intell.* · Lin 2025 *AMPPS* "Six Fallacies" · Ashokkumar, Hewitt, Ghezae & Willer 2026 *Nature* · "LLM-Based Social Simulations Require a Boundary" (arXiv:2506.19806)

**FlyWire**
Dorkenwald et al. 2024 *Nature*, "Neuronal wiring diagram of an adult brain" · Shiu et al. 2024 *Nature*, "A *Drosophila* computational brain model reveals sensorimotor processing" · Pospisil, Aragon & Pillow et al. 2024 *Nature*, "The fly connectome reveals a path to the effectome" · Eckstein et al. 2024 *Cell*, neurotransmisores desde EM · Lappalainen et al. 2024 *Nature*, red mecanística del sistema visual · Neuromorphic Loihi 2 (arXiv:2508.16792) · Datos: `zenodo.org/records/10676866` (v783) · Herramientas: `fafbseg` / `navis` / `codex.flywire.ai`

---

**⚠️ Pendientes de verificación** (marcados `[NV]` en el texto, por honestidad al comparar con los demás MDs): los 8 principios de Ostrom en formulación verbatim · Duffy & Ochs 1999 *AER* (crítico para J1) · Centola et al. 2018 *Science* (crítico para J4) · Van Huyck et al. 1990 en cifras · Engel 2011 sobre el juego del dictador (una fuente secundaria lo reporta invertido) · desagregados de Mei et al. (PNAS bloquea el fetch) · el porcentaje exacto del experimento de Grand Central de Schelling.
