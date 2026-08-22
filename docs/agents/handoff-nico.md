# Handoff — Nico · R3 · Conductual + equilibrio

> **Tu memoria entre sesiones.** Léelo al abrir tu sesión de agente, actualízalo antes de cerrarla.
> Este archivo es solo tuyo: nadie más lo edita, así nunca da conflicto de merge.
> Tus carpetas: `behavior/` · Tu rama: `rol/conductual`
> Tu misión, entregables y prompt de arranque: [`docs/ROLES.md`](../ROLES.md)

## Dónde quedé

_Lo más reciente arriba._

- **2026-08-22 (mañana) — `main` mergeado (PR #1 y #2). Un bug serio que solo
  apareció al enchufar el parquet real de Alejo.**
  - **`tamano_empresa` es un CÓDIGO ORDINAL 1-10 de la GEIH (P3069), no un
    número de empleados.** Está documentado en `contracts/README.md` y yo lo
    estaba leyendo como headcount. Dos efectos, los dos silenciosos: la
    categoría `mediana` quedaba **vacía** (el corte `bins=[0,4,19,inf]` espera
    headcounts y los códigos topan en 10), y una firma de "201+ personas"
    entraba con **10 trabajadores** — de ahí a `flujo_caja` y por lo tanto al
    **techo duro que usa el veto**. Corregido en `EMPLEADOS_POR_CODIGO`
    (commit `d28d371`). Verificado: 36 micro / 34 pequeña / 31 mediana, `n` de
    1 a 300.
  - **La grilla real son 101 arquetipos**, no 48: recuperar `mediana` más los
    **9 sectores reales** de Alejo (mi constante `SECTORES` decía 4, quedó
    obsoleta para el camino real). Consecuencia de plata: la corrida en frío
    pasa de $0,51 a **~$1,06**, y el barrido de 7 puntos con N≥5 paráfrasis a
    **~$37** contra un techo de $50. Ya no cabe con margen.
  - **La salida está en el mismo dato:** 51 de los 101 arquetipos pesan <0,5%
    cada uno. top-10 = 46,8% · top-20 = 67,4% · **top-30 = 79,5%** · top-40 =
    87,6% de la población expandida. Con top-30 al LLM y la cola de 71 a
    reglas fijas ponderadas, el barrido con banda baja a ~$11. **Sin
    implementar todavía.**
  - `contrato.py` ya lee el `contracts/decision.json` real de Alejo y coincide
    campo a campo con `EJEMPLO`. `make estado` marca el parquet en verde.
  - Higiene 7/7 y `python3 -m behavior.demo` siguen corriendo a $0.

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

- [ ] **Modo top-K** (30 arquetipos al LLM, cola a reglas fijas ponderadas).
      Es lo que vuelve a hacer viable el barrido con banda dentro del
      presupuesto. Va con `# SUPUESTO:` y reportando qué fracción de la
      población fue decidida por LLM.
- [ ] **Barrido con N≥5 paráfrasis por punto**, para poder afirmar o descartar
      el codo. Es el número que el pitch quiere y hoy no tenemos. **Depende del
      top-K**: sin él son ~$37 y no caben. **Sigue siendo la tarea más
      importante.**
- [ ] **ADR 0010** — reabrir el H10 de Manuel (input en lenguaje natural).
      Concede la ADR 0006 (la fiscalización no va en la política) y trae el
      mecanismo contra la fuga que el H10 no nombra: un parser LLM puede emitir
      la magnitud **de memoria** del decreto en vez de leerla del texto. Test:
      re-skinning aplicado al parser.
- [ ] Cerrar la definición de arquetipo con Alejo: **mi agrupación da 101 y la
      suya 67.** `contracts/README.md` dice que la cierro yo hacia H+14.
- [ ] Enchufar el veto real de Manuel en lugar de `demo.veto_doble_prueba`.
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
- ~~Alejo — `contracts/decision.json`~~ — **resuelto** (PR #2). En disco y
  coincide campo a campo con `EJEMPLO`.
- ~~Alejo — `data/poblacion.parquet`~~ — **resuelto** (PR #2). 6.692 filas,
  esquema exacto. Ver el bug de `tamano_empresa` arriba.
- **Manuel — ADR 0008 espera MI aval** (y el de Alejo). Ya lo di con una
  precisión que es de mi capa: si el trabajador rechaza la oferta, eso **no
  puede volver por el mismo canal que el veto**. Hoy `capa.py` reintenta ante
  un veto pasándole la razón al agente; si el rechazo del trabajador entra por
  ahí, el agente reintenta contra algo que no es una restricción física suya, y
  el dato A4 mezcla "no pudo pagarlo" con "no se lo aceptaron". Propuse que
  `decision.json` gane un campo hermano de `veto`
  (`realizacion: {ocurre, razon}`) que **no** dispare reintento. Aditivo.

## Lo que hay que contarle al equipo

1. **⚠️ Alejo — `tamano_empresa` es un código ordinal, no un headcount.** Yo caí
   en ese error y me corrompía el flujo de caja que usa el veto. **Manuel va a
   escribir `engine/costos.py` contra el mismo campo y tiene el mismo pie para
   tropezar** — y en su caso cae directo sobre el veto. Vale una línea de
   advertencia en `contracts/README.md`.
2. **Alejo — dos definiciones de arquetipo circulando:** mi agrupación da 101 y
   la del parquet trae 67. Hay que cerrar una hoy.
3. **Juanda — el presupuesto cambió.** Con la grilla real (101 arquetipos), el
   barrido con banda cuesta ~$37 de $50. Con top-30 baja a ~$11. El techo sigue
   siendo real, pero el margen se estrechó.
4. **⚠️ Lo más importante: no prometer el codo, y hay un choque con `IDEA.md`.**
   `IDEA.md` §6 promete "muestra dónde está el codo (dato A2)" y `MODELO.md`
   le pone a `barrido.py` un test de "monótono donde debe serlo". **Yo medí que
   no es monótono**, y que la banda de 5 paráfrasis (20 pp de ancho a 18%) es
   más ancha que la diferencia entre políticas vecinas (8,7 pp). Con 1
   paráfrasis, el codo es ruido. No es opinión contra opinión: hay una
   medición, y el guion se está construyendo encima. El dato A2 queda en duda
   hasta que corra el barrido con banda; **la curva de la brecha (A1) sí se
   sostiene.**
5. **Con reglas fijas no hay cascada.** La ablación formaliza a todos (0%)
   mientras el LLM llega a 75,6%: el umbral de una regla fija escala con el
   ingreso en los dos lados, así que es idéntico para todos los arquetipos.
   La dirección del candado 4 es la que esperábamos, pero es a parámetros de
   andamio sin calibrar — todavía no es EL número.
6. **Dani: agrega por `familia`, no por `estrategia_propuesta`.** El modelo
   inventa sinónimos (cinco nombres para "seguir informal" en 193 llamadas).
   Cada decisión trae las dos: la cruda para el feed, la familia para agregar.
7. **Los prompts no nombran país, ciudad, moneda ni año** — más estricto de lo
   que pide el plan. Los montos van en "unidades (u)". Eso deja el test de
   re-skinning (candado 3b) casi hecho. El motor convierte a COP; el agente
   nunca ve pesos.
8. **Prompt caching de la API: medido, no aplica** (0 tokens cacheados en 193
   llamadas). La palanca real es el caché en disco: la repetición cuesta $0 y
   tarda 0,5 s. Eso además hace viable el demo en vivo.

## Supuestos que tomé

_Además del `# SUPUESTO:` en el código, para que R5 los recoja en `VALIDATION.md`._

- **Código 10 de `tamano_empresa` = 300 empleados.** El rango es "201 o más",
  abierto, sin punto medio. Los otros nueve códigos sí son el punto medio de su
  rango. **Es el primer parámetro de esta capa que R5 debe someter a análisis
  de sensibilidad**: entra en `flujo_caja` y por lo tanto en el veto.
- **Arquetipos (andamio, superado por el parquet real):** 4 sectores × 3 tramos de tamaño (micro 3 / pequeña 10 /
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
