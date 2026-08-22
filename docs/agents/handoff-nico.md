# Handoff — Nico · R3 · Conductual + equilibrio

> **Tu memoria entre sesiones.** Léelo al abrir tu sesión de agente, actualízalo antes de cerrarla.
> Este archivo es solo tuyo: nadie más lo edita, así nunca da conflicto de merge.
> Tus carpetas: `behavior/` · Tu rama: `rol/conductual`
> Tu misión, entregables y prompt de arranque: [`docs/ROLES.md`](../ROLES.md)

## Dónde quedé

_Lo más reciente arriba._

- **2026-08-22 — `behavior/` construido punta a punta y corriendo sin API key.**
  - **V10 cerrada.** Veredicto en `behavior/README.md`: se adopta la idea de
    AgentTorch, no la dependencia. El bloqueo duro es la **licencia AGPL-3.0**
    contra nuestro MIT; además su muestreo es escalar (float) y el nuestro es
    categórico con veto. Muestreo propio en `behavior/arquetipos.py`.
  - Módulos: `higiene`, `arquetipos`, `contrato`, `cache`, `presupuesto`,
    `cliente`, `capa`, `rondas`, `ablacion`, `demo`. 48 arquetipos falsos
    (4 sectores × 3 tamaños × formal/informal × 2 tramos).
  - `python3 -m behavior.demo` corre 4 rondas completas con reglas fijas, sin
    key y a $0. El veto se ejercita (96 propuestas rechazadas en la corrida).
  - `python3 -m behavior.higiene` escanea los prompts: 7/7 limpios.
- 2026-08-22 — Repo scaffoldeado. Nada construido todavía.

## En qué estoy trabajando

- [ ] **Primero al abrir la próxima sesión:** una llamada real a la API. Todo el
      camino LLM está escrito pero **jamás se ejecutó** (no había credenciales).
      `python3 -m behavior.demo --llm` es la prueba. Hasta que eso pase, el
      costo por corrida es un estimado ($0,29 normal / $1,44 con 5 paráfrasis).
- [ ] Congelar `contracts/decision.json` con Manuel y enchufar el veto real en
      lugar de `demo.veto_doble_prueba`.

## Bloqueado / esperando a alguien

- **Credenciales de la API de Anthropic.** No hay `ANTHROPIC_API_KEY` ni CLI
  `ant` en la máquina. Es lo único que separa a `behavior/` de estar terminado.
- **Manuel — el veto real.** Yo consumo `Veto` (`behavior/capa.py`):
  `veto(decision, arquetipo) -> {"factible": bool, "razon": str|None}`. Mientras
  tanto uso un doble de prueba en `behavior/demo.py`, claramente marcado como
  tal. **Un veto sin `razon` no sirve:** el reintento le pasa la razón al agente,
  y esa es justamente la información que un economista no le daría.
- **Alejo — `contracts/decision.json` no existe en disco.** `contrato.py` valida
  contra el ejemplo de `docs/PLAN.md` §4 y prefiere el archivo apenas aparezca.
- **Alejo — `data/poblacion.parquet`.** `arquetipos.desde_poblacion()` ya está
  escrito contra el esquema de `contracts/agente.json`; es un cambio de una línea.

## Lo que hay que contarle al equipo

1. **Con reglas fijas no hay cascada, hay un escalón.** El umbral de evadir
   ("sobrecosto > sanción esperada") escala con el ingreso en los dos lados, así
   que es idéntico para todos los arquetipos: cruzan todos o ninguno. La
   retroalimentación sí funciona (50% → 100% con la probabilidad de sanción
   cayendo 4,8% → 2,0%), pero **el codo (dato A2) no puede salir de una regla
   fija.** Necesita heterogeneidad en el umbral: población real (Alejo) o el
   espacio de estrategias abierto del LLM. Si el codo aparece con LLM y no con
   reglas, esa diferencia ES el candado 4.
2. **Los prompts no nombran país, ciudad, moneda ni año** — más estricto de lo
   que pide el plan. Los montos van en "unidades (u)". Eso deja el test de
   re-skinning (candado 3b) casi hecho. El motor convierte a COP; el agente
   nunca ve pesos.
3. **Prompt caching de la API probablemente no aplica.** El mínimo cacheable de
   Haiku 4.5 son 4096 tokens y nuestro prefijo es más corto. Está cableado y
   medido, pero la palanca real de costo es el caché en disco. Está dicho en
   `behavior/README.md` para que no lo descubra el juez.

## Supuestos que tomé

_Además del `# SUPUESTO:` en el código, para que R5 los recoja en `VALIDATION.md`._

- **Arquetipos:** 4 sectores × 3 tramos de tamaño (micro 3 / pequeña 10 /
  mediana 45) × formal/informal × 2 tramos de ingreso = 48. Los cortes los
  confirma o corrige Alejo contra el parquet real.
- **Números de andamio** (`arquetipos_falsos`, se van con los datos reales):
  t1 = 1,0× el piso y t2 = 1,6×; el informal paga 0,85× del formal; el flujo de
  caja libre es 0,18× la nómina; la indemnización es 1,5× el ingreso mensual.
- **Sanción = 12 meses de ingreso por trabajador** (`multa_factor`). Es el
  parámetro que decide si evadir paga: **el primero que R5 debe someter a
  análisis de sensibilidad.** El valor que manda es el del motor.
- **Capacidad de fiscalización = 2%** del universo por periodo, FIJA — no se
  ajusta entre rondas. Ese compromiso es lo que hace la cascada un resultado y
  no un supuesto.
- **Mejor respuesta simultánea:** el agregado que ve un arquetipo es el de la
  ronda anterior completa, no el que se va formando dentro de la ronda.
- **Máximo 3 reintentos** tras veto, luego fallback a `absorber`; el fallback
  queda marcado con `fue_fallback: True` para que se pueda contar.
- **El determinismo del proyecto en esta capa lo da el caché en disco**, no el
  modelo: con el caché poblado la corrida relee exactamente las mismas
  respuestas. Es un hecho del diseño y así hay que reportarlo.

## Para el Q&A del domingo (mi parte)

- Es **dinámica de mejor respuesta a 3-4 rondas**, no una prueba de existencia ni
  de convergencia a Nash. `rondas.converge()` solo mira si la última ronda movió
  la informalidad menos que un umbral, y se reporta como observación de *esa*
  corrida. Está escrito así en el docstring de `behavior/rondas.py`.
- Pendiente (1–2 h, fuera del código): `docs/fuentes/dani.md` §2.1 y el insumo de
  políticas §7.
