# ADR 0001 — Motor vectorizado propio, no un framework de ABM

**Estado:** aceptado · **Fecha:** 2026-08-22 · **Fuente:** `docs/PLAN.md` §4.1

## Contexto

Existen frameworks maduros de simulación basada en agentes (Mesa, NetLogo) y plataformas recientes de agentes LLM a escala (AgentSociety, OASIS, AgentTorch, Concordia). La tentación obvia en un hackathon es importar uno y ahorrar horas.

Regla adoptada del insumo de Manuel §4.8: **ninguna librería entra al plan sin que un humano haya abierto su URL**, y por cada una se declara qué ahorra y qué habría que construir igual.

## Decisión

El motor se construye: ~300 líneas de numpy/pandas, con el bucle de rondas **vectorizado sobre un dataframe**. Se reutiliza infraestructura aburrida y probada (pandas, numpy, FastAPI, Next.js, Supabase, SDK de Anthropic con prompt caching), nunca el motor de simulación.

## Alternativas descartadas

| Alternativa | Qué ahorraba | Por qué no |
|---|---|---|
| **Mesa** | Scheduler por agente, grillas espaciales, visualización | Nuestro bucle son 4 rondas vectorizadas sobre un dataframe. El scheduler OOP agente-por-agente es más lento y no aporta nada sin componente espacial. |
| **AgentSociety** (Tsinghua) | Entorno urbano, social y económico completo | No trae GEIH, ni margen formal/informal, ni fiscalización endógena: habría que construir todo el modelo laboral igual. Instalación cara. Se lee el paper, se cita como prior art. |
| **OASIS** (1M agentes) | Escala de agentes en redes | El caso no es una red social. Nuestra escala viene del factor de expansión de la GEIH, no del runtime. Se roba el patrón de agregado compartido entre agentes, no el código. |
| **AgentTorch** | La idea de LLM por arquetipo | Se adopta la **idea** (ver ADR 0002), no la dependencia. El muestreo por arquetipos son ~50 líneas. |
| **Concordia** (DeepMind) | Manejo de prompts para agentes narrativos | Solo hay 3-4 historias narradas: no amerita un framework. |
| **NetLogo** | Modelos ABM clásicos validados | No existe modelo NetLogo de informalidad laboral colombiana. |
| **DoWhy**, **sbi / MSM formal** | Refutación causal, calibración bayesiana | La validación es calibración contra momentos + backtest, no un grafo causal. Meterlos sin usarlos de verdad es decoración detectable. Se nombran en `VALIDATION.md` como camino futuro. |

## Consecuencias

Si una herramienta nos ahorrara el 100% del motor, el mérito técnico se iría con ella y un revisor detecta un wrapper en 30 segundos. `engine/` es el archivo que debe poder leerse completo en una tarde: esa legibilidad **es** el entregable técnico.

La línea para el Q&A y para `ARCHITECTURE.md`: *"leímos AgentSociety, OASIS y AgentTorch; adoptamos el patrón de arquetipos de AgentTorch y el agregado compartido de OASIS, y decidimos no importar sus runtimes porque nuestro modelo cabe en un motor vectorizado propio."*
