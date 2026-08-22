# Investigación Nico — Platanus Hack 26 Bogotá (Track: Simulaciones)

> Documento de trabajo para cruzar con la investigación del resto del equipo antes de meter todo a Fable y empezar desarrollo. Fecha: 22 agosto 2026.

---

## 1. Qué dijeron los organizadores (transcripción de la charla inicial)

### Definición oficial del track "Simulaciones"
Va junto con el track "Access": se trata de **obtener información que no es directamente accesible u observable, aproximándola con un caso hipotético / modelo**. Ejemplos que dieron textualmente:

- Simular cómo piensan las personas, cómo funcionan las sociedades, cómo funcionan los mercados.
- Simular economía, interacción entre agentes, comportamiento humano usando modelos de lenguaje como los "agentes".
- **Único ejemplo concreto que dieron**: simular cómo se mueve la opinión pública en una elección en base a la publicidad de un candidato.

Advertencia de los propios organizadores: evitan dar ejemplos muy específicos porque la gente se ancla en ellos y termina copiándolos — el ejemplo de elecciones es inspiración, no plantilla.

Hay 4 tracks en total (todos nuevos esta edición). El otro relevante para nosotros es **Emergencias**: "cuando el mundo deja de funcionar, ¿qué tecnología debería existir para que los daños sean lo menor posible?" — solapa conceptualmente con Simulaciones (info no accesible / hay que reconstruirla o simularla).

### Criterios de evaluación (rúbrica explícita)
| Criterio | % | Qué significa |
|---|---|---|
| Originalidad | 15% | Que no exista ya — buscarlo antes en Google/ChatGPT. |
| Ambición | 20% | Resolver un problema grande. Dijeron explícitamente que **no quieren ver apps de finanzas personales**. |
| Ejecución | 20% | Que el proyecto se sienta terminado y funcional en 36h, no una idea sin sustancia. |
| Aspecto técnico | 25% (el que más pesa) | Jueces **todos técnicos**, van a tener copia de los repos y usar agentes de IA para interrogar el código e implementación. |
| Impacto | ~20% (inferido por descarte, no dicho explícito en el audio) | Que resuelva un problema real a la mayor cantidad de gente posible. |

### Reglas duras
- Proyecto debe quedar **deployado y público** (no sirve localhost).
- Código **open source, licencia MIT**.
- No se mencionó explícitamente ninguna restricción sobre usar boilerplates/código previo — no asumir esa regla, no salió en la charla.

### Sponsors y herramientas
- **Anthropic**: $50 USD en créditos de API por equipo (vía consola/dashboard).
- **Render**: hosting, con créditos (monto no queda claro en el audio, no confiar en cifra exacta).
- Mentores técnicos y de producto acompañan a cada equipo todo el fin de semana.

### Premios
- $3,000 USD (USDC) a repartir entre los ganadores de los 4 tracks.
- Mejor equipo del hackathon: $1,200 USD (en vez de ~$400 de un track normal), destinado a viajar a la final regional en **Santiago de Chile, noviembre** (compitiendo contra Buenos Aires, CDMX, Caracas — Bogotá es la 3ra parada de la gira 2026).
- Posible viaje adicional a Brasil a fin de año para el mejor equipo del año (dato con baja claridad en el audio).
- Premio aparte por **votación pública**: $400 USD al proyecto más votado, ~10 días después del evento vía plataforma pública.

### Deadlines / hitos
- Sábado ~8pm: charla de cómo hacer un buen pitch.
- **El pitch en vivo dura 3 minutos y medio (3:30)** — no 3-5 min genérico.
- Domingo: presentaciones → premiación → cierre.
- No mencionaron freeze de idea/scope explícito.

### Señales indirectas de qué buscan los jueces
- Insistieron en **alejarse del modelo de negocio** — foco 100% en la solución tecnológica.
- Aspecto técnico pesa más que nada (25%) y lo van a auditar con IA sobre el código real.
- Dijeron textualmente que **no quieren otra app de finanzas personales**.
- Quieren que el resultado **"no parezca hecho en 36 horas"**.
- Este año definieron % explícitos en la rúbrica como respuesta a que en ediciones pasadas "no era claro" — señal de que la van a aplicar al pie de la letra.

---

## 2. Candidatas evaluadas en el brainstorm

Marco de evaluación usado por candidata: qué simula/para quién, wow factor, factibilidad en ~30h (Next.js + Supabase + IA), diferenciación, gancho narrativo.

1. **Motor de simulación social genérico** (escenario libre, en vivo) — alta ambición + aspecto técnico + diferenciación (framework, no un solo caso de uso).
2. **Simulador de opinión pública en elecciones** — calca el ejemplo textual de los organizadores → riesgo alto en originalidad.
3. **Focus group sintético para founders** ("prueba tu pitch contra 50 clientes falsos") — rápido de construir, conecta con la audiencia de Platanus, pero impacto/ambición más débiles (herramienta de nicho B2B).
4. **Simulador de respuesta a emergencias** (cruce Simulaciones + Emergencias) — alto impacto y narrativa, pero más costoso en tiempo (mapa + geolocalización).
5. **Simulador de propagación de "slop"/desinformación en redes** — buen callback a la charla (mencionaron "slop" como palabra del año 2025), pero género ya conocido.

### Deep dive — Opción 1: Motor social genérico (caso Transmilenio)

**Cómo funciona:**
1. Población fija de ~100-150 "bogotanos sintéticos" generada una sola vez con Claude (localidad, ingreso, ocupación, modo de transporte, tolerancia a gasto, tendencia política) → tabla `personas` en Supabase.
2. Input de escenario en texto libre (ej. "Suben el pasaje de Transmilenio de $2.950 a $3.500").
3. Fan-out: una llamada a Claude (Haiku, por costo/velocidad) por persona, con salida estructurada JSON (sentimiento, cambio de comportamiento, cita textual). 100-150 calls en paralelo = segundos, costo de centavos.
4. Guardado incremental en Supabase + **Realtime** empujando cada respuesta al frontend apenas llega.
5. Dashboard: feed tipo timeline llenándose en vivo + agregados (% que cambia comportamiento, sentimiento por localidad) + resumen ejecutivo generado al final.
6. El mismo motor sirve para cualquier escenario que un juez escriba en vivo (~15-20 seg de respuesta).

**Estimado de horas (30h, equipo de 3-5):**
- Personas + schema: 2-3h
- Motor de simulación (fan-out + structured output + reintentos): 4-6h
- Supabase Realtime: 3-4h
- Dashboard (feed + charts + input libre): 8-10h
- Polish + guion demo: 4-6h

**Riesgos:** que se vea "genérico" si la población no está bien anclada en datos reales de Bogotá (localidades/estratos reales); ser honestos en el pitch de que esto aproxima reacciones cualitativas, no predice el futuro; cuidar rate limits/costo usando Haiku para las reacciones individuales.

### Deep dive — Opción 3: Founders / focus group sintético

**Cómo funciona:** mismo motor base, pero la población es dinámica (definida por el founder describiendo su cliente ideal) en vez de fija; el estímulo es el pitch/copy/precio del producto en vez de una política pública.

**Comparación técnica con Transmilenio:** prácticamente el mismo código base (fan-out + structured output + Realtime), incluso más rápido de construir porque no requiere validar datos demográficos reales.

**Dónde pierde en la rúbrica:** impacto más débil (ayuda a founders individuales, no a una sociedad), se siente menos "wow" que ver reaccionar a una ciudad entera, y (ver sección de investigación de mercado abajo) es la que tiene más competencia directa ya en producción.

### Opción híbrida (tercera opción explorada): Motor multi-propósito

Un solo backend con capa de configuración: `poblaciones` (fija tipo ciudad o dinámica tipo cliente), `personas` con atributos en **JSONB** (para que ciudadanos y clientes convivan en la misma tabla sin schema rígido), `escenarios` + `reacciones` iguales para ambos casos. El demo abre con Transmilenio (gancho cívico) y gira en vivo hacia un caso de producto — muestra generalidad sin duplicar trabajo de construcción.

**Riesgo a vigilar:** scope creep — preparar de antemano solo 2 escenarios completos con fallback cacheado (nunca depender 100% de una generación en vivo sin red de seguridad frente a los jueces); no construir features de "producto real" (auth, multi-tenant) que no aportan al demo.

---

## 3. Investigación de mercado — ¿ya existe esto?

### Rama "founders / producto" — categoría de mercado YA consolidada
- **[Synthetic Users](https://www.syntheticusers.com/)**: SaaS en producción. Personas con modelo de personalidad OCEAN, $2-60 por entrevista, claim de 85-92% de paridad con research real. Esto no es un prototipo, es un producto vendiéndose.
- Ecosistema completo de competidores: **[Delve.ai](https://www.delve.ai/blog/synthetic-focus-groups)**, **[Perspective AI](https://getperspective.ai/blog/synthetic-focus-groups-why-fake-respondents-can-t-replace-real-customer-research)**, **[SYMAR](https://www.symar.ai/synthetic-focus-groups/)**, **[Minds](https://getminds.ai/blog/best-synthetic-market-research-tools-2026)** — existe incluso un **["market map" 2026 de research sintético](https://fish.dog/news/synthetic-research-platforms-the-2026-market-map)**.
- PwC ya escribió sobre esto: **["Retail's invisible focus group"](https://www.pwc.com/us/en/industries/consumer-markets/library/retail-invisible-focus-group.html)**.
- Paper académico **["Synthetic Founders"](https://arxiv.org/html/2509.02605v1)**: literalmente simula founders e inversionistas reaccionando a validación de startups, usando la plataforma Synthetic Users.

→ **Conclusión: la opción 3 (founders) queda débil en originalidad — es una réplica en miniatura de un producto ya financiado y en producción.**

### Rama "ciudad / política pública" — más académica, también existe
- **[AgentSociety](https://arxiv.org/html/2502.08691v1)**: framework de investigación, +10.000 agentes LLM simulando una sociedad completa (economía, movilidad, redes sociales). Ya probaron: impacto de renta básica universal, respuesta a crisis (huracanes), polarización política, propagación de desinformación. Es casi nuestro "motor genérico", pero como paper, sin interfaz usable.
- **["Simulating Public Transit Fare Policies in NYC"](https://arxiv.org/html/2606.21897v1)**: paper que simula casi exactamente el caso Transmilenio.
- Varios papers más sobre LLMs prediciendo opinión pública/elecciones: **[arxiv 2504.00241](https://arxiv.org/pdf/2504.00241)**, **[favorability elecciones 2024](https://arxiv.org/html/2602.06302)**, **[simulación a escala poblacional](https://arxiv.org/html/2603.27056)**.
- Origen del concepto: **[Generative Agents / Stanford "Smallville"](https://www.emergentmind.com/topics/generative-agents-smallville)** (2023) — ya hay un ecosistema completo de seguidores.

→ **Conclusión: el concepto de "agentes simulando sociedad" ya existe y es conocido, pero NADA de lo encontrado es un producto web en vivo, interactivo, pulido, en español, hiperlocal a una ciudad — ese es el espacio libre real.**

### Implicación estratégica
No vender el pitch como "inventamos la simulación con IA" (un juez técnico lo puede tumbar en la Q&A buscando 30 segundos). Vender el ángulo de **producto interactivo hiperlocal en tiempo real, en español, gratuito** — la interfaz que le faltaba a una idea que ya es conocida en papers y SaaS caros en inglés.

---

## 4. Recomendación final — "Pulso"

**Una línea:** el pulso de la ciudad, en vivo — le preguntas algo a Bogotá (una política, una noticia, un escenario) y una población sintética hiperlocal te contesta en segundos, con feed en vivo y agregados por localidad.

**Por qué esta y no las otras:**
- Se queda con el framing cívico de alto impacto (Transmilenio como historia de apertura).
- Se despega del ejemplo literal de los organizadores al generalizar más allá de elecciones.
- Arquitectura reusable (población abstracta en JSONB, un solo motor, dos demos) = historia de ingeniería real para el 25% de aspecto técnico.
- Diferenciación defendible: nadie encontrado hace esto como producto vivo, interactivo, en español, hiperlocal — el hueco de mercado real está ahí, no en "inventar el concepto".

**Demo en 3:30:**
1. Abre con Transmilenio — feed llenándose en vivo, agregados por localidad, resumen ejecutivo.
2. Giro: un juez escribe su propio escenario en vivo → mismo dashboard se repuebla desde cero.
3. Cierre: mención de un tercer uso posible (ej. mensaje de emergencia) sin construirlo, para mostrar generalidad.

**Riesgo abierto a resolver con el equipo:** validar localidades/estratos reales de Bogotá para que la población sintética se sienta creíble desde el día uno (no placeholder genérico).

---

## 5. Para cruzar con el equipo antes de Fable

Preguntas abiertas que faltan responder con la investigación de los otros 4:
- ¿Alguno encontró un track/ejemplo distinto o data adicional de la charla que no capturé acá (partes del audio muy garbled)?
- ¿Alguien tiene fuente de datos reales de localidades/estratos de Bogotá lista para usar (DANE, Secretaría de Movilidad, etc.)?
- ¿Confirmar nombre final del producto y si el ángulo "Pulso" convence al resto o prefieren otro framing?
- ¿División de roles: quién arma el motor (fan-out + Supabase), quién el dashboard/dataviz, quién los datos demográficos/prompt engineering de personas?
