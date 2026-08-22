# Handoff — Nico · R3 · Conductual + equilibrio

> **Tu memoria entre sesiones.** Léelo al abrir tu sesión de agente, actualízalo antes de cerrarla.
> Este archivo es solo tuyo: nadie más lo edita, así nunca da conflicto de merge.
> Tus carpetas: `behavior/` · Tu rama: `rol/conductual`
> Tu misión, entregables y prompt de arranque: [`docs/ROLES.md`](../ROLES.md)

## Dónde quedé

_Lo más reciente arriba._

- **2026-08-22 (tarde) — la capa corre contra la API real. 1.880 respuestas en caché.**
  - **Costo medido:** $0,5080 la corrida en frío (193 llamadas), **$0,0000 y
    0,5 s** la repetición con caché. Paralelizado (`--paralelismo 8`) baja el
    frío de 10 min a ~1,5 min. Gasto total de la sesión: **~$4,3**.
  - **Prompt caching de la API: confirmado que NO aplica** (0 tokens cacheados;
    Haiku 4.5 pide 4.096 de prefijo mínimo y el nuestro es más corto). La
    palanca real es el caché en disco. Estaba sospechado, ahora está medido.
  - **La cascada existe con LLM:** 63,2% → 75,6% con la probabilidad de sanción
    cayendo 4,8% → 2,1%. No converge (la ronda 2 se pasa y la 3 se devuelve), y
    así hay que reportarlo.
  - **⚠️ El codo NO se puede afirmar.** El barrido de 7 políticas no es monótono,
    y la banda de 5 paráfrasis (20 pp de ancho a 18%) es MÁS ancha que las
    diferencias entre políticas vecinas (8,7 pp). Con 1 paráfrasis, el codo es
    ruido. **No llevarlo al pitch hasta medirlo con N≥5 por punto.**
  - Tres bugs reales que solo aparecieron corriendo de verdad: sinónimos de
    estrategia fragmentando el dato A4 (→ `contrato.familia()`),
    `informalizar_parcial` contando como total (→ `fraccion_fuera_de_regla()`),
    y una respuesta sin JSON válido en 1.160 que tumbaba la corrida entera
    (→ `RespuestaInvalida`, ahora es reintento).

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

- [ ] **Barrido con N≥5 paráfrasis por punto**, para poder afirmar o descartar
      el codo. Es el número que el pitch quiere y hoy no tenemos. ~$18 completo,
      ~$8 acotado a 3 puntos. **Es mi siguiente tarea y la más importante.**
- [ ] Congelar `contracts/decision.json` con Manuel y enchufar el veto real en
      lugar de `demo.veto_doble_prueba`.
- [ ] Exportar un caché consolidado (`Cache().exportar()`) y versionarlo, para
      que el demo del domingo corra sin API key y sin red.

## Bloqueado / esperando a alguien

- ~~Credenciales de la API~~ — resueltas. **La key está en el historial del chat
  de la sesión, no en el repo. Hay que rotarla al terminar el hackathon.**
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

1. **⚠️ Lo más importante: no prometer el codo todavía.** El barrido con LLM no
   es monótono y la banda de paráfrasis es más ancha que las diferencias entre
   políticas. Con 1 paráfrasis no distinguimos señal de ruido. Juanda: esto
   afecta el guion del pitch — el dato A2 está en duda hasta que corra el
   barrido con banda. La curva de la brecha (A1) sí se sostiene.
2. **Con reglas fijas no hay cascada.** La ablación formaliza a todos (0%)
   mientras el LLM llega a 75,6%: el umbral de una regla fija escala con el
   ingreso en los dos lados, así que es idéntico para todos los arquetipos.
   La dirección del candado 4 es la que esperábamos, pero es a parámetros de
   andamio sin calibrar — todavía no es EL número.
3. **Dani: agrega por `familia`, no por `estrategia_propuesta`.** El modelo
   inventa sinónimos (cinco nombres para "seguir informal" en 193 llamadas).
   Cada decisión trae las dos: la cruda para el feed, la familia para agregar.
4. **Los prompts no nombran país, ciudad, moneda ni año** — más estricto de lo
   que pide el plan. Los montos van en "unidades (u)". Eso deja el test de
   re-skinning (candado 3b) casi hecho. El motor convierte a COP; el agente
   nunca ve pesos.
5. **Prompt caching de la API: medido, no aplica** (0 tokens cacheados en 193
   llamadas). La palanca real es el caché en disco: la repetición cuesta $0 y
   tarda 0,5 s. Eso además hace viable el demo en vivo.

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
