# Prompt para la sesión de Claude Code de NICO (pegar completo como primer mensaje)

Estoy en un hackathon de 36 horas (PlatanusHack 26 Bogotá, track Simulations). El equipo construye un simulador de políticas públicas que responde "¿cuánta gente cumple la política y a quién le cae encima?", con población real de la GEIH del DANE, un motor determinista con veto de factibilidad, una capa LLM que descubre estrategias de adaptación, y rondas de mejor respuesta que producen una cascada de evasión. Caso demo: el aumento del salario mínimo del 23% en Bogotá.

**Antes de escribir una línea de código, lee:** `docs/PLAN.md` (secciones 3 [decisión D4], 4, 5 y 6 [V10]), `docs/ROLES.md` (sección Nico) y `docs/FLUJO.md`.

## Mi rol

Soy **R3 · Capa conductual + equilibrio**: la capa LLM que descubre estrategias y el bucle de rondas de mejor respuesta. Además soy quien defiende "mejor respuesta" y "equilibrio de Nash" en el Q&A del domingo.

- **Dueño exclusivo de:** `behavior/`. NO toques `engine/` (yo PROPONGO decisiones, Manuel las veta y aplica), `web/`, `data/` ni los docs raíz.
- **Rama:** `rol/conductual`. Commits pequeños; merge a `main` mínimo cada 6 horas.

## Las 3 reglas de oro de mi capa (no negociables, están en el plan §5)

1. **Al LLM SOLO la mecánica, JAMÁS el nombre de la política.** El prompt dice "tu costo laboral por empleado formal sube X%" — nunca "salario mínimo", "decreto", "reforma", ni años. Es nuestro control de contaminación de entrenamiento y la respuesta a la pregunta que mata proyectos en este track.
2. **LLM por arquetipo, no por agente** (decisión D4): ~40–60 arquetipos × 4 rondas ≈ ~250 llamadas cacheadas; los miles de agentes muestrean de esas distribuciones. Haiku para la masa; modelo grande SOLO para las 3–4 historias narradas del pitch.
3. **Control de costo brutal:** prompt caching de Anthropic (el contexto del mundo se repite), caché en disco por hash del prompt (una simulación se corre decenas de veces — no pagamos dos veces lo mismo), y presupuesto tope por corrida con corte duro. El presupuesto total del equipo es ~$50/persona.

## Orden de trabajo (estricto)

1. **AHORA (H+0 a H+3):** verificación V10: abrir el repo de AgentTorch (github, buscar "agenttorch") y decidir en 30 min si su muestreo por arquetipos es importable o si lo escribo a mano (~50 líneas — el plan ya asume este caso). Documentar el veredicto en `behavior/README.md`.
2. **H+3 a H+4 (30 min, con Manuel):** congelar el contrato del veto contra `contracts/decision.json`: yo produzco `{agente_id, ronda, estrategia_propuesta, detalle, justificacion}`, Manuel responde el veto. Si vetado → reintento con otra estrategia (máximo 3 reintentos, luego fallback "absorber").
3. **H+4 a H+10:** prompts por arquetipo funcionando contra el motor de Manuel con datos falsos. Estructura del prompt: perfil del arquetipo (ingresos, sector, tamaño) + la mecánica del cambio + el agregado de la ronda anterior ("el 30% ya evade, la probabilidad de sanción bajó a 4%") → salida JSON estructurada con la estrategia. Espacio de estrategias ABIERTO: cumplir, informalizar (total/parcial), despedir, absorber, renegociar, bajar horas — y lo que el modelo proponga, que el veto filtrará.
4. **H+8 a H+14 (con Alejo):** definir los arquetipos reales sobre `poblacion.parquet` y reemplazar los falsos.
5. **H+14 a H+20:** el bucle completo de 4 rondas con presupuesto medido. Registrar en `behavior/README.md` el costo real por corrida.
6. **H+20 a H+26 (SOLO si el checkpoint C4 cerró, con Juanda):** el test de pico y placa (`docs/PLAN.md` §5.5): misma población, prompt con solo la mecánica "no puedes usar tu vehículo 2 días a la semana" — ¿emerge la estrategia del segundo carro sola? Corrida cualitativa, ~3 horas. Si compite con el número principal de validación, se cae sin discusión.
7. **Antes del domingo (fuera del código, 1–2 h):** estudiar del insumo de Daniel (`insumos-integrantes/investigacion-daniel.md` §2.1) y del insumo de políticas (§7): qué es mejor respuesta, qué es equilibrio de Nash, y por qué lo nuestro es "dinámica de mejor respuesta a 3 rondas, no una prueba de convergencia". Esa honestidad es la defensa.

## Reglas duras

- N≥5 paráfrasis del prompt para la barra de error (no seeds de temperatura — regla del plan §5).
- Los prompts son visibles en el repo (`behavior/prompts/`): el juez debe poder verificar que no nombramos la política.
- El reporte de cualquier agente es un reclamo: verifica con `git diff --stat` y revisando el caché.

## Definición de listo

Una corrida de 4 rondas completa cuesta menos del tope, usa el caché en repeticiones (segunda corrida ≈ $0), produce `contracts/decision.json` válidos que el veto de Manuel acepta/rechaza, y el desglose de estrategias por arquetipo llega a Supabase para la pantalla de Dani.
