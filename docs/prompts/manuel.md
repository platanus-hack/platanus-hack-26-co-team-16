# Prompt para la sesión de Claude Code de MANUEL (pegar completo como primer mensaje)

Estoy en un hackathon de 36 horas (PlatanusHack 26 Bogotá, track Simulations). El equipo construye un simulador de políticas públicas que responde "¿cuánta gente cumple la política y a quién le cae encima?", con población real de la GEIH del DANE, un motor determinista con veto de factibilidad, una capa LLM que descubre estrategias de adaptación, y rondas de mejor respuesta que producen una cascada de evasión. Caso demo: el aumento del salario mínimo del 23% en Bogotá.

**Antes de escribir una línea de código, lee:** `docs/PLAN.md` (secciones 3, 4, 4.1, 4.2 y 5), `docs/ROLES.md` (sección Manuel), `docs/UML.md` y `docs/FLUJO.md`.

## Mi rol

Soy **R2 · Backend: motor + API**. El motor es lo que el agente del juez va a leer para decidir el 25% técnico: debe poder leerse completo en una tarde.

- **Dueño exclusivo de:** `engine/` y `api/`. NO toques `behavior/` (el LLM es de Nico), `web/`, `data/` ni los docs raíz.
- **Rama:** `rol/backend`. Commits pequeños; merge a `main` mínimo cada 6 horas.
- **Stack fijado:** Python + numpy/pandas + FastAPI. **PROHIBIDO importar Mesa, Concordia o cualquier framework de ABM** — decisión build-vs-buy documentada en `docs/PLAN.md` §4.1: el motor es vectorizado y nuestro.

## Orden de trabajo (estricto)

1. **AHORA (H+0 a H+4):** primer commit del motor con **seed y determinismo desde el inicio** (misma seed → mismo resultado, siempre; meterlo después es reescribir). Estructura: un concepto por archivo en `engine/`, cada uno con docstring de cabecera (qué modela, entradas, salidas, supuestos).
2. **H+4 (30 min, con Nico):** congelar el contrato del **veto de factibilidad** contra `contracts/decision.json`: Nico me manda `estrategia_propuesta` + `detalle`, yo respondo `{"factible": bool, "razon": str|null}`. Es la interfaz más importante del proyecto.
3. **H+4 a H+10:** el motor punta a punta con datos falsos conformes a `contracts/agente.json` (checkpoint C3): cargar población → aplicar política como cambio de costos → recibir decisiones (stub de Nico o aleatorias) → vetar → aplicar → recalcular fiscalización → agregado por ronda (`contracts/ronda.json`) → 4 rondas.
4. **Piezas del motor, en orden:**
   - Costos: `costo_formal = salario × factor_prestacional` (verificación V3 a H+4: si no hay cifra exacta verificada, usar rango 1,4–1,5 con `# SUPUESTO:` y un barrido de sensibilidad); `costo_informal = salario negociado + riesgo de sanción esperado`.
   - **Fiscalización endógena — el corazón de la cascada:** `prob_sancion = capacidad_fija / n_evasores`. La capacidad NUNCA se ajusta a mano para producir la cascada: sale de una fuente o de un `# SUPUESTO:` con sensibilidad.
   - El veto de factibilidad (flujo de caja, opciones existentes).
   - Scheduler de rondas (ronda 0 ingenua = la proyección del gobierno; rondas 1–3 con el agregado visible).
   - **Barrido de `aumento_pct`** (no solo 7/13,6/23): un `for` sobre el motor para localizar el codo de la cascada (dato A2 del plan). Resultados precomputables para la demo.
5. **H+10 a H+16:** `api/`: FastAPI con `POST /simulaciones` (política + seed) que corre el motor y persiste cada ronda y cada decisión en Supabase (esquema acordado con Dani). Cuando Alejo entregue `poblacion.parquet` real (H+8), reemplazar los datos falsos.
6. **Siempre:** tests del núcleo determinista junto a Juanda (dos corridas con la misma seed dan bit a bit lo mismo; el veto rechaza lo imposible; la cascada es monótona respecto a capacidad).

## Reglas duras

- Determinismo: toda aleatoriedad pasa por UN `numpy.random.Generator` sembrado. Nada de `random` global.
- Cero `TODO: implementar` en `engine/` — es la respuesta literal a "¿qué parte es difícil?" y un agente lo encuentra en segundos.
- Constantes con nombre y fuente o `# SUPUESTO:`. Nada de números mágicos.
- El reporte de cualquier agente es un reclamo: verifica con `git diff --stat` y corriendo los tests.

## Definición de listo

`make run` (o `uvicorn`) levanta la API; un `POST /simulaciones` con seed=42 produce 4 rondas en Supabase; correrlo dos veces da resultados idénticos; los tests pasan; `engine/README.md` explica el modelo en una pantalla.
