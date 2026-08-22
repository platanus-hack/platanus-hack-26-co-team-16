# Prompt para la sesión de Claude Code de MANUEL (pegar completo como primer mensaje)

Estoy en un hackathon de 36 horas (PlatanusHack 26 Bogotá, track Simulations). El equipo construye un simulador de políticas públicas que responde "¿cuánta gente cumple la política y a quién le cae encima?", con población real de la GEIH del DANE, un motor determinista con veto de factibilidad, una capa LLM que descubre estrategias de adaptación, y rondas de mejor respuesta que producen una cascada de evasión. Caso demo: el aumento del salario mínimo del 23% en Bogotá.

**Antes de escribir una línea de código, lee, en este orden:**

1. `docs/agents/handoff-manuel.md` — dónde quedaste.
2. **`docs/IDEA.md`** — la idea completa y las decisiones de modelo. Es la espina dorsal.
3. **`engine/MODELO.md`** — el mapa *teoría → archivo → función → test → supuesto*, con los 10 archivos de `engine/` ya definidos y los 7 supuestos pre-declarados. **Es tu orden de trabajo real.**
4. `docs/adr/0005` a `0009` — las cinco decisiones de motor que ya se tomaron. No se re-litigan.
5. `docs/PLAN.md` (§3, 4, 4.1, 4.2, 5), `docs/ROLES.md` (sección Manuel), `docs/UML.md`, `docs/FLUJO.md`.
6. `docs/investigacion/` — cuando dudes de dónde sale una pieza.

## Mi rol

Soy **R2 · Backend: motor + API**. El motor es lo que el agente del juez va a leer para decidir el 25% técnico: debe poder leerse completo en una tarde.

- **Dueño exclusivo de:** `engine/` y `api/`. NO toques `behavior/` (el LLM es de Nico), `web/`, `data/` ni los docs raíz.
- **Rama:** `rol/backend`. Commits pequeños; **PR a `main` mínimo cada 6 horas** (nadie pushea directo a `main` — ver `AGENTS.md`).
- **Stack fijado:** Python + numpy/pandas + FastAPI. **PROHIBIDO importar Mesa, Concordia o cualquier framework de ABM** — decisión build-vs-buy documentada en `docs/PLAN.md` §4.1: el motor es vectorizado y nuestro.

## Orden de trabajo (estricto)

> **Estado a 2026-08-22:** el bloque de fundamentación ya se hizo (PR #3): la idea está en
> `docs/IDEA.md`, el fundamento en `docs/investigacion/`, y el motor está mapeado archivo por
> archivo en `engine/MODELO.md`. **El paso 1 de abajo es lo que sigue**, y ahora arranca con
> las decisiones ya tomadas en vez de con preguntas abiertas.

1. **AHORA (H+0 a H+4):** primer commit del motor con **seed y determinismo desde el inicio** (misma seed → mismo resultado, siempre; meterlo después es reescribir). Estructura: un concepto por archivo en `engine/`, cada uno con docstring de cabecera (qué modela, entradas, salidas, supuestos).
2. **H+4 (30 min, con Nico):** congelar el contrato del **veto de factibilidad** contra `contracts/decision.json`: Nico me manda `estrategia_propuesta` + `detalle`, yo respondo `{"factible": bool, "razon": str|null}`. Es la interfaz más importante del proyecto.
3. **H+4 a H+10:** el motor punta a punta con datos falsos conformes a `contracts/agente.json` (checkpoint C3): cargar población → aplicar política como cambio de costos → recibir decisiones (stub de Nico o aleatorias) → vetar → aplicar → recalcular fiscalización → agregado por ronda (`contracts/ronda.json`) → 4 rondas.
4. **Piezas del motor, en orden:**
   - Costos: `costo_formal = salario × factor_prestacional` (verificación V3 a H+4: si no hay cifra exacta verificada, usar rango 1,4–1,5 con `# SUPUESTO:` y un barrido de sensibilidad); `costo_informal = salario negociado + riesgo de sanción esperado`.
   - **Fiscalización endógena — el corazón de la cascada:** `prob_sancion(C, E) = 1 - exp(-C / max(E, 1))` — ver [ADR 0007](../adr/0007-forma-funcional-prob-sancion.md), que **supera** la forma abreviada `capacidad / n_evasores` que decía este prompt (no era una probabilidad: no acotada e indefinida en 0). La capacidad NUNCA se ajusta a mano para producir la cascada: `C` sale de la cifra de la OIT (1.300 inspectores) y lo que no tenga fuente va con `# SUPUESTO:` y barrido de sensibilidad. La capacidad **no es campo de `Politica`** ([ADR 0006](../adr/0006-fiscalizacion-es-estado-del-mundo.md)).
   - El veto de factibilidad (flujo de caja, opciones existentes).
   - Scheduler de rondas (ronda 0 ingenua = la proyección del gobierno; rondas 1–3 con el agregado visible). **Una ronda es un trimestre, horizonte 9 meses** ([ADR 0005](../adr/0005-el-reloj-de-la-simulacion.md)).
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
