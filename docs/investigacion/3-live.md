# Esfera 3 · Live — quién está vivo, cómo lo vende y cómo lo resuelve

**Dueño: Manuel (R2)** · Reglas de la carpeta: [`README.md`](README.md)

> Las otras dos esferas responden *"¿está bien construido?"*. Esta responde *"¿esto ya
> existe y cómo se gana la confianza de alguien que paga?"*. Importa para el backend por
> una razón concreta: **la pregunta que hunde a los productos vivos de esta categoría es la
> misma que hunde a los proyectos del track**, y la respuesta se construye en el motor, no
> en la interfaz.

---

## 1. Research sintético — la categoría con dinero

### Aaru — el caso que hay que conocer

| | |
|---|---|
| **Qué es** | Plataforma de simulación de poblaciones con agentes múltiples para predecir comportamiento humano en marketing, política y decisiones de negocio. Fundada en marzo de 2024. |
| **Cómo lo resuelve** | Usa **datos de censo para replicar distritos electorales**, y crea agentes programados para pensar como los votantes que copian. Cada agente carga etiquetas (edad, ingreso) **y además** patrones de conducta y motivos de decisión. Hace pasar a los agentes por varios pasos de razonamiento antes de la respuesta final. |
| **Cómo lo vende** | Con dos claims de precisión: una primaria demócrata en Nueva York predicha **con margen de 371 votos**, y un estudio de EY (*2025 Global Wealth Study*, 3.600 inversionistas en 30+ mercados) recreado **a ciegas** en un día, con **correlación de Spearman mediana de 0,90**. |
| **Señal de mercado** | Serie A de más de USD 50M liderada por Redpoint, a valuación *headline* de ~USD 1.000M (diciembre 2025). Accenture Ventures entre los inversionistas. |
| **Fuentes** | [TechCrunch](https://techcrunch.com/2025/12/05/ai-synthetic-research-startup-aaru-raised-a-series-a-at-a-1b-headline-valuation/) · [Research Live / Accenture](https://www.research-live.com/article/news/accenture-invests-in-synthetic-audience-startup-aaru/id/5136643) · [Semafor](https://www.semafor.com/article/09/20/2024/ai-startup-aaru-uses-chatbots-instead-of-humans-for-political-polls) · [aaru.com](https://aaru.com/simulation) |

**La grieta, y es la nuestra.** Una reseña de 2026 lo dice sin rodeos: para un producto cuya
promesa entera es predecir, **la vara que importa es la validación independiente, y esa es
más difícil de encontrar desde afuera que los titulares de financiación**
([FishDog, 2026](https://fish.dog/news/aaru-ai-review-2026-the-prediction-startup-and-where-it-fits)).

> Traducción para nosotros: la empresa de mil millones de dólares de esta categoría valida
> **hacia adentro y por invitación** (un estudio de EY que ellos recrearon). Nosotros
> validamos **hacia afuera y con un comando**: `make validate` imprime el error del backtest
> fuera de muestra, salga como salga, y cualquiera lo puede correr. Eso no es un detalle de
> ingeniería, es el único terreno donde un equipo de hackathon puede ganarle a un unicornio.

### El resto de la categoría

| Empresa | Qué vende | A quién | Fuente |
|---|---|---|---|
| **Minds** | Plataforma de research sintético con paneles configurables; benchmarks publicados de 80-95% | Marcas y agencias | [comparativa 2026](https://getminds.ai/blog/best-synthetic-market-research-tools-2026) |
| **Synthetic Users** | Entrevistas de usuario sintéticas para producto y UX | Equipos de producto | [syntheticusers.com](https://www.syntheticusers.com/) |
| **Evidenza** | Research sintético B2B | Marketing B2B | `docs/fuentes/manuel.md` §3.1 |
| **PyMC Labs** | "Consumidores sintéticos" con rigor bayesiano encima del LLM | El más serio metodológicamente | `docs/fuentes/manuel.md` §3.1 |

**Patrón del segmento:** todas le venden **predicción de opinión a quien ya tiene
presupuesto de research**. Todas usan benchmark contra un estudio propio o de un cliente.
Ninguna publica un backtest fuera de muestra reproducible por un tercero.

**Dónde NO competimos:** no vamos a hacer research sintético para marcas. La categoría tiene
un unicornio y nuestra ventaja (datos públicos de una encuesta nacional) ahí no vale nada.

---

## 2. Simulación de política pública — dónde sí estamos

| Trabajo | Qué es | Producto o paper |
|---|---|---|
| **Gemelos digitales de política** ✅ [arXiv 2607.13766](https://arxiv.org/html/2607.13766) | Prototipos que operacionalizan ABMs multinivel como motores de escenarios para usuarios de política. Una instancia en Newcastle usa **~97.300 agentes-hogar derivados de datos reales de stock de vivienda (EPC)**, calibrados contra estadísticas de consumo 2021-2023 | **El análogo más cercano a lo nuestro.** Mismo patrón: microdatos reales → agentes → motor de escenarios. Sigue siendo investigación, no producto abierto |
| **PolicySim** (ACM Web Conf 2026) | Sandbox de agentes LLM para **optimización** de política pública | Paper. Y optimiza la política; nosotros evaluamos la que se nos dé |
| **PoliSim @ CHI 2026** | La comunidad del campo tiene nombre desde abril de 2026 | No estamos inventando la categoría, y decirlo primero nos protege |
| **Gemelos digitales urbanos comerciales** | Integran sensores, geoespacial y socioeconómico como soporte de decisión. Se venden como *"réplica exacta"* y márgenes premium por algoritmos propietarios | Contratos de cientos de miles de dólares con gobiernos de países ricos. **Ninguna alcaldía latinoamericana tiene esto ni lo va a comprar** |
| **Causal AI / decision intelligence** ✅ [análisis 2026](https://thecuberesearch.com/why-causal-ai-decision-intelligence-2026/) | La capa que testea intervenciones y corre contrafactuales con salidas auditables | Categoría naciente, sin líder. Mismo problema que nosotros: cómo hacer creíble una respuesta hipotética |

---

## 3. Cómo responden ellos a *"¿por qué te creo?"* — y cómo respondemos nosotros

Esta tabla es el insumo directo del guion del pitch.

| Estrategia | Quién la usa | Qué tan fuerte es |
|---|---|---|
| **Benchmark contra un estudio propio o de cliente** | Aaru (EY), Minds | Fuerte comercialmente, débil científicamente: el que elige el benchmark es el vendedor, y no es reproducible desde afuera |
| **Un acierto famoso** (los 371 votos) | Aaru | Memorable en prensa, pero es un punto, no una distribución de error |
| **Rigor metodológico del método** | PyMC Labs (bayesiano) | Sólido, pero le habla a estadísticos, no a quien decide |
| **Calibración contra datos oficiales** | Gemelos digitales de política | Sólido. Es nuestro candado 1 |
| **Backtest fuera de muestra publicado, con el error, acierte o no** | **Casi nadie** | Es la más costosa de fingir y la única que un tercero puede rehacer. **Es nuestro candado 2 y el centro del pitch** |
| **Declarar dónde NO hay que creerle** | Casi nadie | Contraintuitivo: leído por un evaluador técnico, la honestidad calibrada es madurez, no debilidad |

---

## 4. De la idea a producción — cómo se empaquetan

La pregunta de Mani: *¿cómo llegan de la idea a producción y cómo entregan el valor?* Hay un
**espectro**, y la posición en él no es estilo: la decide **cuánta calibración necesita cada
cliente nuevo**.

```
  self-serve                                                 servicio gestionado
  ◄──────────────────────────────────────────────────────────────────────────────►
  Synthetic Users            Minds                Evidenza              Aaru
  entras y corres       panel configurable   engine + interpretación   6-7 cifras de ACV
  tú mismo                                    experta                  semanas/meses de
                                                                       calibración
```

| | Synthetic Users | Evidenza | Aaru |
|---|---|---|---|
| **Quién lo usa** | Equipos de producto y UX, solos | Organizaciones grandes, acompañadas | Fortune 500, consultoras, agencias de research |
| **Cómo se entra** | Te registras y corres | Onboarding gestionado | **Semanas a meses** de calibración e integración, normalmente con soporte de Aaru |
| **Qué recibes** | Insights direccionales rápidos y baratos | Resultados **más interpretación estratégica experta**; exportable como plan de go-to-market para C-suite | Un pronóstico cuantitativo, no un resultado de encuesta: **distribución de reacciones, estimaciones agregadas y, en encargos profundos, dinámica intertemporal** (cómo se propagan las actitudes, cómo decae la atención, cómo se influyen los segmentos) |
| **Precio** | Autoservicio | Enterprise gestionado | **Seis a siete cifras de ACV** |
| **Fuentes** | [reseña](https://ai-cmo.net/tools/synthetic-users) · [sitio](https://www.syntheticusers.com/) | [evidenza.ai](https://www.evidenza.ai/) · [análisis](https://getminds.ai/blog/best-synthetic-research-tools-2026) | [Minds sobre Aaru](https://getminds.ai/blog/minds-ai-vs-aaru) · [Aaru × EY](https://getminds.ai/blog/aaru-ey-partnership-explained) |

**El flujo de trabajo es el mismo en todas, y es el nuestro:** anclar en datos reales →
construir las personas → armar el panel → aplicar un estímulo → leer la respuesta
poblacional. Que la categoría entera converja a ese pipeline es una señal de que nuestra
arquitectura no es rara, aunque nuestro anclaje (una encuesta nacional pública) sí lo sea.

### Las tres lecciones que sí cambian lo que hacemos

**1. La generalidad te empuja a servicios.** Aaru necesita semanas o meses de calibración por
cliente, y por eso cobra seis o siete cifras y **solo puede venderle a quien puede pagar
eso**. No es codicia: es que un motor general no sabe nada de tu problema hasta que alguien
lo calibra. **Nosotros no podemos pagar ese costo y por eso elegimos un solo caso calibrado.**
Esto le da respaldo comercial a la decisión D6 del plan (*"general en el código, estrecho en
la pantalla"*): la pantalla estrecha es lo que nos permite ser autoservicio y gratis. Si en
el pitch prometemos generalidad de pantalla, nos estamos metiendo, sin quererlo, en el
negocio de Aaru, donde perdemos.

**2. El entregable correcto es una distribución, no una respuesta.** Aaru vende explícitamente
"distribución de reacciones + estimaciones agregadas + dinámica intertemporal" y lo distingue
de un resultado de encuesta. Eso es **exactamente** nuestra banda de incertidumbre más las
rondas. Confirma que nuestro formato de salida no es una concesión de hackathon: es el
estándar de lo que la gente paga.

**3. El costo de entrada es el terreno donde ganamos.** Aaru: semanas o meses. Evidenza:
onboarding gestionado. **Nosotros: cero.** Un extraño abre un link y mueve un slider. Eso no
es un detalle de UX, es la traducción de nuestra única ventaja estructural — los datos son
públicos y ya están calibrados a un solo caso — y es lo que hace que el cliente que el equipo
eligió (gobierno y periodismo) exista como cliente.

## 5. El posicionamiento que hay que robar

De los cuatro, el movimiento más inteligente no es de Aaru: es de **Synthetic Users**, que
**invierte el flujo de research**. No se venden como reemplazo de la investigación real. Se
venden como el **primer paso barato**: corres sintético primero para explorar el espacio del
problema y afinar la pregunta, y después gastas una porción menor del presupuesto en
entrevistas reales para validar.

Traducido a nuestro caso, y es la frase de posicionamiento que faltaba:

> **No reemplazamos al DANE, ni a Fedesarrollo, ni a la mesa de concertación. Somos el primer
> paso barato: mostramos cuál de las preguntas merece el estudio caro.**

Es más defendible que *"simulamos la política"*, desactiva la objeción obvia (*"¿y por qué le
creería a esto en vez de a un economista?"*) sin pelearla, y es honesto con lo que un backtest
con banda de error puede sostener de verdad.

## Lo que nos llevamos

**Qué copiamos (de producto, no de motor):**
- **Instanciar desde datos oficiales, no inventar la población.** Aaru lo hace con censo y
  calibración con datos de panel; el gemelo de Newcastle con stock de vivienda; nosotros con
  GEIH. Es el patrón que le da credibilidad instantánea a la demo.
- **La palanca visible.** Todos los productos vivos tienen una perilla que el usuario mueve;
  ningún paper la tiene. Es la pieza 4 de la anatomía y la diferencia entre experimento y producto.
- **El entregable es una distribución con dinámica**, no un número. Es lo que Aaru cobra en
  siete cifras y es lo que nuestras rondas con banda ya producen.
- **La inversión del flujo de Synthetic Users** como posicionamiento (§5). El primer paso
  barato, no el reemplazo.
- **Precomputar y responder rápido.** Nuestro equivalente al "estudio de EY en un día" es que
  el slider responda en segundos.

**Dónde no competimos:** research sintético para marcas (unicornio ocupando el espacio) ·
optimización de política (PolicySim) · gemelos urbanos con sensores (contratos de gobiernos
ricos) · cualquier cosa que exija calibración por cliente.

**El hueco, que es exactamente el que el equipo identificó en el audio:**

1. **Nadie sirve a quien no tiene ni datos propios ni presupuesto.** Con ACV de seis y siete
   cifras y onboarding de meses, un concejal, un periodista o un gremio colombiano no es
   cliente de ninguno de estos productos, ni podría serlo.
2. **Lo que sí existe para política pública se queda en Python.** Hay literatura capaz de
   decir qué pasa si sube la tarifa de transporte en Nueva York, y alguien que no programa no
   puede verlo. La brecha es de acceso, no tecnológica.
3. **Nadie publica un backtest fuera de muestra que un extraño pueda rehacer.** La empresa de
   USD 1.000M de esta categoría valida con estudios propios, por invitación. Nosotros
   validamos con un comando que cualquiera corre. Es la vara más alta de la categoría y la
   única que se puede montar en 36 horas, porque no exige escala: exige honestidad y un `Makefile`.

**Cómo aterriza en el backend:** los tres puntos justifican decisiones de motor, no de
interfaz. (1) obliga a que la población salga de datos públicos gratuitos y que la corrida
sea barata, y a que **la calibración venga hecha, no por cliente**. (2) obliga a que el motor
corra detrás de una API pública sin auth y en segundos, con escenarios precomputados. (3)
obliga a que `engine/` sea determinista y auditable, porque un backtest que no se puede
repetir no vale nada.
