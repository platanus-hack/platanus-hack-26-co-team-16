# Esfera 1 · Teórica — qué ya está probado

**Dueño: Manuel (R2)** · Reglas de la carpeta: [`README.md`](README.md)

> El motor no inventa una teoría del cumplimiento. Toma una que tiene cincuenta años de
> literatura, le cambia **una** cosa, y esa cosa es la tesis del proyecto.
>
> Las cuatro casillas de cada entrada: *qué prueba · qué nos sirve · **qué NO** · dónde aterriza*.

---

## 1. Método — cómo se describe y se valida un modelo basado en agentes

Este frente no es sobre economía: es sobre **cómo se escribe un modelo para que otro lo
pueda reimplementar y refutar**. Es la parte que casi ningún equipo del track va a tener,
y es barata.

### Protocolo ODD
[Grimm et al. (2020), *JASSS* 23(2):7](https://www.jasss.org/23/2/7.html) — segunda
actualización del protocolo original de 2006.

| | |
|---|---|
| **Qué prueba** | Existe un estándar internacional para describir un ABM de forma completa y reimplementable. Siete elementos: **1)** propósito y patrones · **2)** entidades, variables de estado y escalas · **3)** procesos y scheduling · **4)** conceptos de diseño (11 sub-conceptos: emergencia, adaptación, objetivos, aprendizaje, predicción, sensing, colectivos, entre otros) · **5)** inicialización · **6)** datos de entrada · **7)** submodelos. |
| **Qué nos sirve** | Es el esqueleto de [`docs/IDEA.md`](../IDEA.md) y de [`engine/MODELO.md`](../../engine/MODELO.md). Un revisor que sepa de ABM lo reconoce de inmediato; uno que no, igual obtiene un documento completo. Elemento 1 ("propósito **y patrones**") nos obliga a declarar contra qué patrones observados se juzga el modelo antes de escribirlo. |
| **Qué NO nos sirve** | Es un protocolo de **documentación**, no de diseño ni de validación: no dice si el modelo es bueno. Y ODD completo es largo; usamos la estructura, no el formato de paper académico. |
| **Dónde aterriza** | Estructura de `docs/IDEA.md` (§ anatomía) y de los docstrings de cabecera de cada archivo de `engine/`. |

### Pattern-Oriented Modeling (POM)
[Grimm et al. (2005), *Science* 310(5750):987-991](https://www.science.org/doi/10.1126/science.1116681) · [espejo de acceso abierto (KNAW)](https://pure.knaw.nl/portal/en/publications/pattern-oriented-modeling-of-agent-based-complex-systems-lessons-/).

| | |
|---|---|
| **Qué prueba** | Que la pregunta *"¿cuánto detalle meto?"* tiene respuesta metodológica: se incluye el detalle mínimo necesario para reproducir **varios patrones observados a la vez**, a distintas escalas (individual y de sistema). Un modelo que reproduce un solo patrón está sobreajustado; uno que reproduce tres con los mismos parámetros tiene estructura. |
| **Qué nos sirve** | Es la respuesta literal a la pregunta que el equipo se hizo en el audio (*"cómo definen qué componentes son valiosos"*). Da el criterio para podar la GEIH: una columna entra si sirve a un patrón declarado, no porque exista. Nuestros patrones: informalidad por sector · informalidad por tamaño de firma · distribución salarial con el spike en el mínimo. Tres patrones, un solo juego de parámetros. |
| **Qué NO nos sirve** | POM asume que tienes varios patrones independientes bien medidos. El nuestro más valioso (el spike salarial) está ⚠️ sin verificar en la GEIH descargada (V9 del plan). Si no aparece, quedamos con dos patrones y hay que decirlo. |
| **Dónde aterriza** | El criterio de selección de columnas que se le pasa a Alejo (R1), y el candado 1 de validación (calibración base). |

### Epstein, "Why Model?"
[Epstein (2008), *JASSS* 11(4):12](https://www.jasss.org/11/4/12.html).

| | |
|---|---|
| **Qué prueba** | Dieciséis razones legítimas para construir un modelo que **no son predecir**: explicar, delimitar el rango de resultados posibles, descubrir qué datos harían falta, iluminar incertidumbres centrales, entrenar intuición, disciplinar el diálogo político. |
| **Qué nos sirve** | Convierte *"no entregamos el futuro, entregamos el rango"* (`PLAN.md` §1.1) de excusa defensiva en **postura reconocida y citable**. Es la respuesta de una frase a *"¿pero esto predice o no?"* en el Q&A. |
| **Qué NO nos sirve** | No exime del backtest. Epstein justifica no-predecir; no justifica no-medirse. Nuestro candado 2 sigue siendo obligatorio. |
| **Dónde aterriza** | `VALIDATION.md` (dueño Juanda) y el guion del pitch. No toca código. |

---

## 2. Teoría del cumplimiento — de dónde sale la decisión de evadir

### Allingham & Sandmo (1972) — el modelo canónico
[*Journal of Public Economics* 1(3-4):323-338](https://eml.berkeley.edu/~saez/course/Allingham&SandmoJPubE(1972).pdf) (PDF abierto, Berkeley) · [ficha RePEc](https://ideas.repec.org/a/eee/pubeco/v1y1972i3-4p323-338.html). Casi 5.000 citas.

| | |
|---|---|
| **Qué prueba** | Que la decisión de evadir se modela como una apuesta bajo incertidumbre: el agente compara el pago de cumplir contra el valor esperado de evadir, que depende de **la probabilidad de detección `p`** y **la multa `F`**. Es el esqueleto formal de toda la literatura posterior. |
| **Qué nos sirve** | La forma de la decisión, tal cual. Nuestro agente hace exactamente esta comparación: costo formal cierto contra costo informal esperado (= salario negociado + `p` × sanción). |
| **Qué NO nos sirve** | **En A-S, `p` es exógeno y fijo.** Ese es precisamente el supuesto que rompemos, y romperlo es la tesis del proyecto (ver §3). Además A-S es un agente representativo con utilidad esperada; nosotros no imponemos una función de utilidad, la conducta la propone la capa LLM y la filtra el veto. |
| **Dónde aterriza** | `engine/costos.py` (comparación formal vs informal) y `engine/fiscalizacion.py`. |

### Becker (1968) — disuasión
[*Journal of Political Economy* 76(2):169-217](https://www.journals.uchicago.edu/doi/10.1086/259394) · [PDF abierto (NBER)](https://www.nber.org/system/files/chapters/c3625/c3625.pdf) · [ficha RePEc](https://ideas.repec.org/a/ucp/jpolec/v76y1968p169.html).

| | |
|---|---|
| **Qué prueba** | El marco de disuasión: el castigo esperado es `p × F`, y el infractor responde a ese producto. Es el ancestro de A-S. |
| **Qué nos sirve** | Justifica que solo necesitemos modelar el producto, no la psicología del infractor. |
| **Qué NO nos sirve** | Becker es indiferente entre subir `p` o subir `F` (solo importa el producto). **La evidencia empírica dice que no son intercambiables** (ver PNAS 2021 abajo), y nuestro diseño toma partido. |
| **Dónde aterriza** | Se cita en `engine/README.md` como linaje. No genera código propio. |

---

## 3. Fiscalización endógena — el único cambio que hacemos, y de dónde sale

**Aquí vive la tesis.** Todo lo anterior asume `p` dado. Nosotros lo hacemos función del
número de evasores, porque la capacidad de inspección es fija.

### Interacción social y equilibrios múltiples
[*Tax evasion and social interactions*, JPubE (2007)](https://www.sciencedirect.com/science/article/abs/pii/S0047272707000497).

| | |
|---|---|
| **Qué prueba** | Que extender A-S con interacción entre contribuyentes produce **equilibrios múltiples** y soluciones de esquina (todos cumplen / nadie cumple). O sea: el umbral y la cascada no son una invención nuestra, son un resultado conocido de esta familia de modelos. |
| **Qué nos sirve** | Legitima que busquemos **el codo** (dato A2 del plan). Si un revisor pregunta "¿por qué habría un umbral?", la respuesta es que esta clase de modelos los produce y está publicado. |
| **Qué NO nos sirve** | **Su canal es conformidad social** (la gente evade porque otros evaden, por norma). El nuestro **no**: nuestro único canal es aritmético, la capacidad de inspección se diluye. Es un mecanismo más restrictivo y más defendible, y hay que decir la diferencia en voz alta, no dejar que se confundan. |
| **Dónde aterriza** | `engine/fiscalizacion.py` y el barrido de `aumento_pct`. |

### ABMs de evasión con auditoría endógena
[Springer (2013), *Tax Enforcement in an Agent-Based Model with Endogenous Audits*](https://link.springer.com/chapter/10.1007/978-3-319-00912-4_4) · [modelo cinético de tres estados, arXiv 1407.5220](https://arxiv.org/pdf/1407.5220) · [dinámica de evasión, arXiv 1112.0233](https://arxiv.org/pdf/1112.0233).

| | |
|---|---|
| **Qué prueba** | Que ya existen ABMs de evasión con probabilidad de auditoría endógena, con agentes heterogéneos y moral fiscal distinta, y que producen **transiciones de fase**: por debajo de un punto crítico el cumplimiento es alto y la sanción casi no importa; por encima, la fiscalización sí mueve la aguja. |
| **Qué nos sirve** | Es prior art directo del mecanismo. Nos dice qué esperar cualitativamente y nos ahorra descubrirlo a las 4am. También nos da vocabulario: "punto crítico" en vez de "codo" cuando hablemos con alguien técnico. |
| **Qué NO nos sirve** | Son **poblaciones sintéticas de econofísica** (agentes tipo Ising, sin atributos reales) y su dominio es impuesto a la renta, no contratación laboral. No traen microdatos, ni margen formal/informal, ni backtest fuera de muestra. Ahí está nuestro aporte. |
| **Dónde aterriza** | Diseño de `engine/fiscalizacion.py` y expectativa cualitativa del barrido. |

### Frecuencia sobre severidad
[*Frequency of enforcement is more important than the severity of punishment in reducing violation behaviors*, PNAS 118 (2021)](https://www.pnas.org/doi/10.1073/pnas.2108507118).

| | |
|---|---|
| **Qué prueba** | Empíricamente, subir la **frecuencia** de fiscalización reduce infracciones más que subir la **severidad** de la sanción. Contradice la indiferencia de Becker. |
| **Qué nos sirve** | Es la justificación publicada de nuestra decisión de diseño más importante: **la variable de estado del sistema es la capacidad de inspección (`p`), no el monto de la multa (`F`)**. Sin esta cita, esa decisión parecería arbitraria. |
| **Qué NO nos sirve** | El estudio es sobre infracciones de tránsito, no laborales. Extrapolamos el principio, no la magnitud, y se marca así. |
| **Dónde aterriza** | [ADR 0006](../adr/0006-fiscalizacion-es-estado-del-mundo.md) y [ADR 0007](../adr/0007-forma-funcional-prob-sancion.md). |

### El número que ancla `capacidad_fija`

**Para qué se necesita.** La cascada sale de `p(E) = 1 − exp(−C/E)`. `C` es el numerador: el
número esperado de inspecciones en el trimestre. **Si `C` es inventado, la cascada es una
perilla que giramos, no un hallazgo.** La pregunta del Q&A es *"¿por qué el codo aparece en
23% y no en 30%?"*, y la respuesta tiene que ser *"porque Colombia tiene N inspectores"*, no
*"porque escogimos un número"*. Es la diferencia entre medir y decorar.

| Dato | Fuente | Estado |
|---|---|---|
| **1.300 inspectores del trabajo** en Colombia, en **36 direcciones territoriales** | [OIT, *Mayor capacidad de la inspección del trabajo en Colombia*](https://www.ilo.org/es/projects-and-partnerships/projects/mayor-capacidad-de-la-inspeccion-del-trabajo-en-colombia), proyecto ago-2023 a ago-2024 | ✅ **Es la cifra que se usa.** Fuente institucional y reciente |
| Planta de **904 cargos**, **813 provistos** (89%); pasó de 424 a 904 en cuatro años | [MinTrabajo, *Inspección del trabajo en Colombia*](https://www.mintrabajo.gov.co/documents/20147/51963/Inspeccion+trabajo+en+Colombia_web.pdf/686c8c7b-9eb7-990d-e4ab-7b18d9d9a6d1) (cifras ~2014-2015) | ✅ fuente primaria, **superada** por la de la OIT. Se conserva porque muestra la trayectoria de crecimiento |
| Estándar **OIT/OCDE: 1 inspector por cada 10.000 trabajadores**, invocado por MinTrabajo como justificación de ampliar la planta | [Presidencia, ene-2026](https://www.presidencia.gov.co/prensa/Paginas/MinTrabajo-hace-precisiones-sobre-planta-temporal-de-inspectores-260125.aspx) | ✅ |
| Planta **temporal** creada por Decreto 0052 del 22-ene-2026, vinculación por fases | [Decreto 0052 de 2026](https://dapre.presidencia.gov.co/normativa/normativa/DECRETO%20No.%200052%20DEL%2022%20DE%20ENERO%20DE%202026.pdf) | ⚠️ **las cifras que circulan se contradicen** (500 vs 1.141 empleos; 460 vs 1.000 inspectores). No se usa ninguna hasta abrir el decreto. Es posterior a nuestra ventana de simulación, así que **no afecta el caso demo** |
| La capacidad **no escala con el problema**: pese a triplicar el presupuesto de inspección en 2018, el número de investigaciones y de procesos sancionatorios **cayó** en siete años, y casi la mitad de las investigaciones exceden el plazo legal | [OECD Reviews of Labour Market and Social Policies: Colombia](https://www.oecd.org/en/publications/oecd-reviews-of-labour-market-and-social-policies-colombia-2024_6ed40726-en.html) | ✅ |

**Orden de magnitud** (💭 cálculo nuestro, va con `# SUPUESTO:` porque el denominador es
aproximado): con **1.300 inspectores** para una población ocupada nacional del orden de 23
millones, Colombia está alrededor de **1 inspector por cada 18.000 trabajadores**, casi el
doble de lo que fija el estándar OIT/OCDE que el propio ministerio invoca.

> **Por qué esto importa más que cualquier otra cifra del proyecto:** el hallazgo de la OCDE
> —presupuesto triplicado, investigaciones a la baja— es evidencia externa de que la
> capacidad de fiscalización **no responde al tamaño de la evasión**. Ese es exactamente el
> supuesto que hace correr la cascada, y no lo pusimos nosotros: está publicado.

---

## 4. Informalidad y salario mínimo — el dominio

| Fuente | Qué prueba | Qué nos sirve / qué NO | Dónde aterriza |
|---|---|---|---|
| Meghir, Narita & Robin, [*AER* 105(4), 2015](https://www.aeaweb.org/articles?id=10.1257%2Faer.20121110) | Modelo de equilibrio donde firmas de igual productividad eligen sector formal o informal, estimado con datos de Brasil | **Sirve:** la economía de la informalidad no es novedad nuestra y así se cita. **NO sirve:** es un modelo estimado en equilibrio, no un instrumento interrogable; no dice "quién concretamente" ni corre detrás de un slider | `engine/costos.py`, linaje |
| Banco de la República, WP 1104 | Para Colombia: +1 pp en el ratio del mínimo ≈ **+0,21 pp** de probabilidad de empleo informal, concentrado en 18-25 años de baja educación | **Sirve:** es el objetivo de calibración del tramo bajo. **NO sirve:** es una elasticidad, o sea una recta — no dice nada sobre umbrales. Usarla como resultado sería circular | Candado 1, calibración |
| [AEA 2025, *Incentives to Comply with the Minimum Wage in the US*](https://www.aeaweb.org/conference/2025/program/paper/k7ETG828) | En EE.UU. una firma infractora tiene ~**1,4%** de probabilidad de ser investigada al año; con las multas típicas, haría falta ~**88%** de probabilidad esperada de detección para que cumplir fuera la mejor opción | **Sirve:** ancla del **orden de magnitud** de `p` en el dominio exacto (cumplimiento del salario mínimo), y evidencia de que `p` real es de un dígito. **NO sirve:** es EE.UU. Entra como `# SUPUESTO:` con rango y sensibilidad, jamás como dato colombiano | `engine/fiscalizacion.py`, calibración de `C` |

---

## 5. Agentes LLM en simulación social — qué pueden y qué no

Consolidado de `docs/fuentes/dani.md` y `docs/fuentes/manuel.md` §6. Lo que hay que
retener para el motor:

| Hallazgo | Consecuencia de diseño |
|---|---|
| **Contaminación medida.** Gao et al., *PNAS* 122 (2025): 75-100% de precisión reproduciendo el concurso de belleza, ~0% en el juego 11-20 isomorfo. No lo arreglan CoT, few-shot ni RAG | Justifica el doble control: jamás nombrar la política + test de re-skinning. `Politica.como_mecanica()` es esto hecho código |
| **Colapso de varianza.** Bisbee et al., *Political Analysis* 32(4); Wang et al., *Nature Machine Intelligence* — y ajustar temperatura **no** lo arregla, es estructural | La heterogeneidad **no puede venir del LLM**: viene de los atributos de la GEIH. El LLM aporta el espacio de estrategias, no la dispersión. Es la razón por la que ADR 0002 (LLM por arquetipo) no pierde casi nada |
| **El contrapunto honesto.** Ashokkumar et al., *Nature* (2026): 70 experimentos, 119.330 participantes — los LLM correlacionan bien con **efectos agregados de tratamiento**, incluso post-cutoff; pero **sobreestiman los tamaños de efecto** | La tarea correcta para nosotros es la primera (efecto agregado), no simular distribuciones individuales. Y hay que esperar sobreestimación: es una dirección de sesgo conocida que se declara |
| **Los LLM son Grim Trigger, no Tit-for-Tat.** Akata et al., *Nature Human Behaviour* 9(7), 2025: GPT-4 nunca vuelve a cooperar tras una deserción — **0% de recuperación** | ⚠️ **Cruce que el equipo necesita para el Q&A.** El canon que se discutió en el audio (torneo iterado de Axelrod, gana el bondadoso = Tit-for-Tat) **no describe a los LLM**. Si Nico defiende teoría de juegos con el canon de Axelrod y el juez conoce Akata, se cae. Nuestra defensa es más simple y más segura: son **3 rondas de mejor respuesta**, no un torneo iterado, y no dependemos de perdón ni de reciprocidad |
| **Auditar un LLM solo no predice el sesgo de una población de LLMs.** Ashery et al., *Science Advances* 11 (2025): agentes individualmente insesgados, poblaciones que convergen de forma no uniforme | Es la mejor respuesta publicada a *"¿por qué multi-agente y no un prompt?"* |

---

## 6. Calibración

| Herramienta / método | Qué es | Veredicto |
|---|---|---|
| **Method of Simulated Moments (MSM)** | El estándar para ajustar parámetros de conducta a momentos observados | **Sí, en versión simple.** Es el candado 1: el mundo sin política reproduce informalidad por sector y tamaño |
| [`sbi`](https://sbi-dev.github.io/sbi/) | Inferencia bayesiana basada en simulación cuando la verosimilitud es intratable | **No en 36 horas.** Se nombra en `VALIDATION.md` como camino futuro. Meterlo sin usarlo de verdad es decoración detectable |
| [Calibración automática de ABMs, arXiv 2203.03147](https://arxiv.org/pdf/2203.03147) | Framework para parámetros dinámicos y heterogéneos | **No.** Referencia metodológica |

---

## La genealogía, en una tabla

Lo que un revisor quiere ver: qué tomamos prestado y **qué cambiamos**.

| Pieza del motor | Ancestro | Qué cambiamos |
|---|---|---|
| Decisión de evadir | Allingham-Sandmo 1972; Becker 1968 | Nada en la forma. La conducta no la impone una función de utilidad: la propone el LLM y la filtra el veto |
| `prob_sancion` | Allingham-Sandmo 1972 | **`p` deja de ser exógeno.** Se vuelve función decreciente del número de evasores. **Este es el cambio, y es la tesis** |
| La cascada y el codo | JPubE 2007; ABMs de auditoría endógena | El canal no es conformidad social sino dilución aritmética de capacidad fija. Más restrictivo, más defendible |
| Que la palanca sea `p` y no `F` | PNAS 2021 | Decisión de diseño con respaldo empírico, no gusto |
| Margen formal/informal | Meghir-Narita-Robin 2015 | Ellos estiman un equilibrio; nosotros corremos mejor respuesta sobre población observada de una encuesta nacional |
| Cuánto detalle meter | Pattern-Oriented Modeling 2005 | Criterio explícito para podar la GEIH: tres patrones, un juego de parámetros |
| Cómo se describe | Protocolo ODD 2020 | La estructura de `IDEA.md` y de los docstrings |
| Espacio de acciones abierto | [Survey LLM-ABM, arXiv 2312.11970](https://arxiv.org/pdf/2312.11970); [evasión fiscal LLM+DRL, arXiv 2501.18177](https://arxiv.org/abs/2501.18177) | Le ponemos encima un veto determinista sobre flujo de caja |

**Ninguna pieza es inédita por separado. La composición sí:** población real de una encuesta
nacional + `p` endógena por capacidad fija + veto determinista + la política jamás nombrada
al modelo + backtest fuera de muestra publicado. Ver [`3-live.md`](3-live.md) para por qué
nadie vivo hoy junta esas cinco.
