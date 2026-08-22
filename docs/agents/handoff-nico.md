# Handoff — Nico · R3 · Conductual + equilibrio

> **Tu memoria entre sesiones.** Léelo al abrir tu sesión de agente, actualízalo antes de cerrarla.
> Este archivo es solo tuyo: nadie más lo edita, así nunca da conflicto de merge.
> Tus carpetas: `behavior/` · Tu rama: `rol/conductual-top-k` (la de trabajo; `rol/conductual` ya se mergeó en el PR #4)
> Tu misión, entregables y prompt de arranque: [`docs/ROLES.md`](../ROLES.md)

## Dónde quedé

_Lo más reciente arriba._

- **2026-08-22 (noche) — PR #6 listo para review. A1 re-medido post-fix, y una
  afirmación del README resultó falsa.**
  - **[PR #6](https://github.com/platanus-hack/platanus-hack-26-co-team-16/pull/6)**
    abierto contra `main`, MERGEABLE/CLEAN, cuerpo completo escrito. Es
    **fix-forward**, no reemplazo del #4: `main` ya carga el bug.
  - **Nada de código nuevo en esta sesión.** Los 11 puntos ya estaban cerrados en
    `0f9fccf`. Lo de esta sesión fue: verificar corriendo, re-medir A1, escribir
    la especificación para R2, y corregir un error del README.
  - **Verificación (regla 4: el reporte de un agente es un reclamo).**
    `pruebas` en verde · `higiene` 7/7 exit 0 · `demo` 4 rondas sin excepciones ·
    `ablacion --barrido-factor` reproduce F=1,4309 · dos corridas mismo seed,
    byte a byte idénticas.
  - **El dato A1 post-fix: SOBREVIVE.** Se re-pagó una de las siete políticas
    (23%, población real, N=5, top-K 0,80): 503 llamadas, **$1,38**.
    Brecha **+37,4 → +33,3 pp**, dentro del rango que ya se reportaba.
    Trayectoria 30,6% → 59,0% → 87,5% → 63,8%, sanción 6,3% → 2,3%.
  - **⚠️ La banda se TRIPLICA: 10,3 → 33,9 pp.** No debilita el proyecto, endurece
    el hallazgo del A2: las bandas se solapan todavía más. La frase para el pitch
    es *"+33 pp con intervalo de +17 a +51; el signo y el mecanismo son robustos,
    la magnitud no está clavada"*.
  - **⚠️ Corrección: el reflujo de la ronda 3 NO era el bug.** El README decía que
    "plausiblemente" lo era. Se midió con el estado arreglado y **sigue ahí**
    (87,5% → 63,8%). Mecanismo legítimo: `cumplir` devuelve la planta entera a
    regla, así que la informalidad puede bajar sin que nada esté roto. Corregido
    en el README en vez de borrado.
  - **Las otras seis políticas del barrido siguen siendo pre-fix.** Están marcadas.
    No citarlas como si no lo fueran. Re-medirlas cuesta ~$9.
  - **Presupuesto de la capa: $10,06** de $50 ($8,68 barrido + $1,38 esta sesión).

  **Lo que queda abierto al cerrar:**
  1. **Crítico #2 — bloqueado por R2.** La especificación de lo que `behavior/`
     necesita de `engine/` está escrita (punto 10 de este handoff) y el punto de
     sutura marcado en `rondas.py` (`grep "PUNTO DE SUTURA"`). No construir motor
     dentro de `behavior/`.
  2. **#10 — avisarle a @DanRin9** del campo `degenerada` en `banda`. Es
     comunicación, no código. **Sigue pendiente.**
  3. **El PR #6 necesita review de alguien distinto** (regla 3 del flujo).
  4. **Para R5:** no hay `requirements.txt` (faltaban `anthropic` y `pyarrow` en
     la máquina) y el caché está gitignoreado, así que hoy un extraño no puede
     reproducir esto. Si queremos demo sin API key, hay que commitear un caché.

- **2026-08-22 (tarde) — los 11 puntos del review del PR #4, cerrados. Y el
  candado 4 no discrimina: el hallazgo de la sesión.**
  - **Rama `rol/conductual-top-k`.** ⚠️ **El #4 se mergeó igual** (35b8dbd,
    15:21, trece minutos después del APPROVED de Alejo), así que el plan de
    "reemplazarlo sin mergear" ya no aplica: **`main` HOY carga el bug del caché
    envenenado y el `FALLBACK = "absorber"` divergente.** Verificado contra
    `origin/main`, no supuesto. Este PR pasa de reemplazo a corrección de algo
    que ya está en producción. Mismo contenido, más urgencia.
  - **Los 3 críticos, reproducidos antes de arreglarlos** y convertidos en
    regresión ejecutable: `python3 -m behavior.pruebas` (34 checks, $0, sin API).
    - **#1** el caché envenenado: con `estrategia_propuesta: ""` la corrida moría
      con UNA llamada y la respuesta mala quedaba **grabada**; la re-corrida sin
      API reventaba idéntico. Doble candado: `cliente.py` valida antes de
      escribir, `capa.py` mete `construir()/validar()` dentro del `try`.
    - **#2** el estado muerto: un arquetipo que informalizó su planta en R1 leía
      *"tu planta: toda formal"* en R2, encima de su historial que decía
      "informalizar". Y los despedidos resucitaban. Estado vivo por arquetipo
      (dos dicts en `correr()`), `fraccion_fuera_de_regla()` acumulativa,
      `empleo_relativo` arrastrado.
    - **#3** el costo de formalizarse. Ver abajo, es lo importante.
  - **⚠️ EL CANDADO 4 NO DISCRIMINA — y eso es el resultado.** Con el costo bien
    especificado y el factor prestacional en 1,40 la ablación **todavía**
    formaliza a todos... por **0,31 pp**: `p*` = 6,02% contra `p(ronda 0)` =
    6,33%. Y el signo **se voltea en F = 1,4309**, dentro del rango 1,4-1,5 que
    el supuesto **S1** de `engine/MODELO.md` ya declaraba incierto. El
    entregable es el barrido, no el número:
    `python3 -m behavior.ablacion --barrido-factor` ($0).
  - **Los puntos #3 y #11 casi se cancelan, y nadie lo notó.** Corregir la tasa
    inicial (0,42 → 30,57%) sube `p(E)` de 4,65% a 6,33%, y ese salto es justo lo
    que cruza el umbral. Por separado dan resultados opuestos.
  - **La spec del costo se eligió por fundamento ANTES de correr**, y sesga a
    favor nuestro: suponer que el salario bruto no cambia al formalizarse
    subestima el costo, o sea que empuja hacia "la ablación formaliza". Está
    dicho así en el README y en el PR, no escondido.
  - **Baratos cerrados:** `FALLBACK = "cumplir"` · tasa inicial sin default de
    andamio · `fallos_tecnicos` fuera del `if` · caché antes del presupuesto ·
    `muestrear()` → `_muestrear_local` · `cargar_contrato()` borrado · `assert`
    de unicidad de ids. El **hash de manifiesto ya existía** (`Cache.manifiesto()`).
  - **Dos huecos que encontré yo, no el review:** la property
    `Arquetipo.situacion_planta` quedó huérfana al mover la situación al estado
    vivo (borrada — era justo la que hacía mentir al prompt), y **el
    `Protocol Veto` no ve el estado vivo**: `arquetipo.formal` es el estado
    INICIAL, así que hay dos estados (el mío y el del motor) que pueden divergir.
    Documentado en el docstring de `capa.Veto`; **hay que cerrarlo con Manuel.**
  - **De acuerdo con las 4 decisiones de Manuel**, sin objeción: razones del veto
    limpias de higiene, fallback `cumplir`, `muestrear()` en `engine/` con firma
    `(arq, n, rng)`, y `C`/`0.18`/`1.5` suyos.

- **2026-08-22 (mediodía) — top-K construido y EL BARRIDO CORRIDO. El dato A2
  se cae, con evidencia. El A1 aguanta.**
  - **Rama `rol/conductual-top-k`** (pusheada, PR sin abrir todavía a propósito:
    cuelga de `rol/conductual`, que aún espera el merge del PR #4).
  - **Cinco cambios juntos, una sola corrida en frío:** ronda 0 ingenua sin LLM
    (ADR 0005) · `p(E)` exponencial (ADR 0007) · `Cache.manifiesto()` (ADR 0009)
    · grilla real de 101 arquetipos · modo top-K.
  - **La ronda 0 parte de la informalidad OBSERVADA (30,57%)**, leída de
    `data/momentos.json`, no del 0,42 de andamio que había. Doce puntos de
    diferencia en la base del número principal.
  - **Verificación buena:** el peso de los arquetipos informales sobre el total
    da **0,3057** — la reconstrucción por arquetipo reproduce el momento
    observado de Alejo exactamente. Es medio candado 1 ya cerrado.
  - **Determinismo nivel 2 (ADR 0009) verificado:** repetí la corrida sin key y
    dio números idénticos, $0,00, 93/93 aciertos. El par `(seed 42, manifiesto
    08d94cb3980bf4b1)` es lo que hace comparables dos corridas.
  - **Bug encontrado corriendo: el dato A4 se agregaba por CONTEO de arquetipos.**
    La tabla imprimía "estrategia dominante: cumplir" en la misma fila donde la
    informalidad subía a 64,6%. Ponderado por factor de expansión domina
    `informalizar` con 51,0% y `cumplir` cae a 18,1%. Corregido; ver el punto de
    Dani abajo.
  - **⚠️ EL BARRIDO CON N=5: el codo no existe.** 7 políticas × 3 rondas × 5
    paráfrasis × 31 arquetipos = **3.235 llamadas, $8,68**. La serie **no es
    monótona** y en **5 de 6** pares vecinos las bandas se solapan. Banda mediana
    15,3 pp contra un rango total entre políticas de 16,7 pp. **No distinguimos
    el 7% del 26%, ni el 23% del 13,6%.** Tabla completa en `behavior/README.md`,
    log crudo en `behavior/barrido-2026-08-22.log`.
  - **El A1 sí aguanta:** brecha de **+28 a +45 pp** sobre la proyección oficial
    en las siete políticas, y la cascada aparece en todas (p. de sanción cae de
    6,3% a 2,6–3,4%). La frase defendible: *"la brecha está entre 28 y 45 puntos
    y no depende de qué alza elijas"*.
  - **Gasto:** $8,68 (barrido) + $0,25 (corrida de verificación) hoy, ~$4,3
    anoche. **~$13,2 de los $50.**

- **2026-08-22 (mañana, 2) — PR #3 de Manuel mergeado. Avales dados y TRES
  divergencias de mi código contra las ADR que ahora son canon.**
  - **Aval dado a la ADR 0008** (asimetría firma/trabajador), con una precisión
    de mi capa: el rechazo del trabajador **no puede volver por el canal del
    veto**. Ver "Bloqueado" abajo.
  - **Aval dado a la ADR 0009**, que me crea una obligación concreta: la caché
    deja de ser temporal y pasa a ser **artefacto versionado con hash de
    manifiesto que la corrida imprime**. `Cache.exportar()` existe; el hash de
    manifiesto **no**. Sin eso el nivel 2 de determinismo no existe para nadie
    fuera del equipo.
  - **⚠️ Divergencia 1 — la ronda 0 (ADR 0005). Es la más grave.** El canon dice
    que la ronda 0 es *"la reacción ingenua: la proyección oficial, que asume
    cumplimiento total"*. Mi `rondas.py` corre las 4 rondas como decisión de
    LLM, incluida la 0. Dos consecuencias: (a) gasto 4 rondas de LLM donde el
    diseño quiere 3 + una línea base calculada — **25% del presupuesto**; y
    (b) `brecha = ronda 3 − ronda 0` es el producto entero según `MODELO.md`,
    y hoy mi ronda 0 no es lo que esa resta supone. **El número principal (A1)
    está midiendo otra cosa.**
  - **Divergencia 2 — `prob_sancion` (ADR 0007).** Yo uso `p ≈ C/E` (la forma
    abreviada del plan) con `min(1.0, ...)`. El canon es
    `p(E) = 1 − exp(−C/max(E,1))`. En el régimen real coinciden (a 63,2% de
    informalidad: 3,16% vs 3,12%), pero en el borde la mía **se rompe**: con 2%
    de evasores da 100% y la exponencial da 63,2%. Mi docstring ya decía "el
    motor de Manuel tiene la versión que manda"; ahora esa versión existe y hay
    que adoptarla.
  - **Divergencia 3 — ninguna.** La ADR 0006 (fiscalización fuera de `Politica`)
    ya la cumplo: `capacidad_fiscalizacion` es parámetro de `correr()`, no un
    campo del dict de política. Nada que cambiar.
  - **Decisión de secuencia:** las tres divergencias, más el top-K y los 101
    arquetipos, **cambian el texto del prompt y por lo tanto invalidan la caché
    en disco**. Arregladas por separado son tres corridas en frío; juntas, una.
    Van todas en el PR siguiente, no en este.

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

- [ ] **Abrir el PR de `rol/conductual-top-k` contra `main`.** El #4 ya está
      mergeado, así que este PR corrige `main` en vez de reemplazar al #4.
- [ ] **Correr la corrida en frío con LLM.** No se hizo en esta sesión (sin
      credenciales a mano). Dos cambios tocan el texto del prompt —la situación
      de planta viva y la tasa inicial en modo andamio—, así que el caché quedó
      parcialmente invalidado. Medido: la ronda 1 en `--real` conserva el caché
      completo (31/31), así que cuesta bastante menos que el techo de $0,61. Los
      números del LLM del README son PRE-fix y están marcados como tales.
- [x] ~~Modo top-K~~ — hecho. 31 arquetipos cubren el 80,5% de la población.
- [x] ~~Barrido con N≥5 paráfrasis~~ — hecho. **El codo no existe** (ver arriba).
- [ ] **Exportar la caché consolidada y versionarla.** Ahora es obligación de la
      ADR 0009, no un "nice to have": sin ella el nivel 2 de determinismo no
      existe para nadie fuera del equipo. La caché tiene ~5.100 entradas y el
      demo del domingo tiene que correr sin key y sin red.
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
- **Manuel — ADR 0008: aval DADO** (falta el de Alejo). Con una precisión que
  es de mi capa: si el trabajador rechaza la oferta, eso **no
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
4. **Manuel — mi ronda 0 no es tu ronda 0 (ADR 0005).** Tú la defines como la
   proyección oficial que asume cumplimiento total; yo la corro como una ronda
   de LLM más. Como `brecha = ronda 3 − ronda 0` es "el producto entero" según
   `MODELO.md`, hoy esa resta mide otra cosa. Lo arreglo yo en `behavior/`,
   pero conviene que quede claro entre los dos **antes** de que `engine/rondas.py`
   se escriba, para no terminar con dos calendarios.
5. **⚠️ LO MÁS IMPORTANTE: el dato A2 (el codo) está muerto, con evidencia.**
   Barrido de 7 políticas con N=5 paráfrasis, $8,68: la serie **no es monótona**
   y en **5 de 6** pares vecinos las bandas se solapan. Banda mediana 15,3 pp
   contra 16,7 pp de rango total entre políticas. No distinguimos el 7% del 26%.
   **Juanda:** el codo sale del guion. Lo que queda en su lugar es más
   defendible: *"medimos si había un umbral, publicamos que la incertidumbre lo
   tapa, y por eso reportamos rango y no punto"*. **Manuel:** el test "el
   barrido es monótono donde debe serlo" de `MODELO.md` va a fallar, y no por un
   bug — el fenómeno no es monótono. **El A1 sí aguanta:** brecha de +28 a
   +45 pp en las siete políticas, con la cascada presente en todas.
6. **⚠️ SUPERADO — el candado 4 no discrimina.** Lo que decía este punto ("con
   reglas fijas no hay cascada") salía de una ablación mal especificada: la regla
   comparaba el sobrecosto del aumento contra la sanción, o sea un delta contra
   un nivel. Corregido, el resultado **no se voltea: queda en el filo**. Con
   F = 1,40 la ablación todavía formaliza a todos, por 0,31 pp, y el signo cambia
   en **F = 1,4309** — dentro del rango 1,4-1,5 que S1 de `MODELO.md` ya
   declaraba incierto. **Juanda:** el candado 4 va a `VALIDATION.md` como barrido
   con punto de quiebre publicado, no como número. **Manuel:** `p(E) → 1.0`
   cuando E→0 crea un **estado absorbente** que ayuda a clavar la ablación en 0%;
   conviene saberlo antes de cablear `fiscalizacion.py`. Lo que SÍ sobrevive es
   el argumento estructural: el umbral de una regla fija escala con el ingreso en
   los dos lados, así que es idéntico para todos los arquetipos y cruzan todos o
   ninguno — verificado, la tabla es igual con 48 arquetipos de andamio y con los
   101 reales. Esa homogeneidad es lo que el LLM no tiene.
6b. **El A1 se re-midió post-fix y sobrevive; la banda se triplica.** De las
   siete políticas del barrido solo se volvió a pagar la del caso demo (23%,
   503 llamadas, $1,38, población real). Brecha **+37,4 → +33,3 pp**: dentro del
   rango que ya se reportaba, o sea que el fix del estado vivo **no tumba el dato
   titular**. Pero la banda pasa de 10,3 a **33,9 pp**. **Juanda:** eso no
   debilita el guion, lo endurece — la conclusión "no podemos afirmar el codo"
   queda más firme, y la frase defendible es *"la brecha es de +33 pp con un
   intervalo de +17 a +51; el signo es robusto, la magnitud no"*. **Y una
   corrección incómoda:** el README decía que el reflujo de la ronda 3 era
   "plausiblemente el bug". Se midió y **sigue ahí** (87,5% → 63,8%), porque
   `cumplir` devuelve la planta a regla y la informalidad puede bajar sin que
   nada esté roto. Ya está corregido en el README. Las otras seis políticas
   siguen siendo pre-fix y no hay que citarlas como si no lo fueran.

7. **Dani — el dato A4 se agrega de dos maneras y las dos importan.**
   **(a) Por `familia`, no por `estrategia_propuesta`:** el modelo inventa
   sinónimos (cinco nombres para "seguir informal" en 193 llamadas). Cada
   decisión trae las dos, la cruda para el feed y la familia para agregar.
   **(b) Ponderado por factor de expansión, NUNCA por conteo de arquetipos.**
   Las dos versiones dicen lo contrario: en la corrida del 23%, por conteo
   domina `cumplir` (44 de 101 arquetipos) y ponderado domina `informalizar`
   (51,0% de la población), con `cumplir` en 18,1%. Un arquetipo de microempresa
   informal representa a muchísima más gente que uno de mediana formal. Ya está
   arreglado en `Ronda.desglose_estrategias()`, que devuelve fracciones de
   población; `desglose_estrategias_conteo()` conserva el crudo para el feed.
8. **Los prompts no nombran país, ciudad, moneda ni año** — más estricto de lo
   que pide el plan. Los montos van en "unidades (u)". Eso deja el test de
   re-skinning (candado 3b) casi hecho. El motor convierte a COP; el agente
   nunca ve pesos.
9. **Prompt caching de la API: medido, no aplica** (0 tokens cacheados en 193
   llamadas). La palanca real es el caché en disco: la repetición cuesta $0 y
   tarda 0,5 s. Eso además hace viable el demo en vivo.

10. **Manuel — el `Protocol Veto` no ve el estado vivo.** Es consecuencia del
   crítico #2 y no lo nombró ninguno de los dos reviews: `arquetipo.formal` es el
   estado INICIAL, así que en la ronda 2 el veto no puede saber por ese campo si
   la unidad ya está fuera de regla. Hoy `behavior/` lleva su propio estado vivo
   y el motor llevará el suyo: **son dos estados que pueden divergir.** O el
   motor es la única fuente y yo leo de él, o la firma lleva el estado. Hay que
   decidirlo antes de que `engine/rondas.py` se cierre.

   **La especificación, para que Manuel la implemente sin preguntar.** Esto es
   lo único que `behavior/` necesita de `engine/` para cerrar el crítico #2; no
   pido el estado del mundo completo, solo el pedazo que entra al prompt.

   | | |
   |---|---|
   | **Qué** | La fracción de la planta del arquetipo que está fuera de regla al EMPEZAR la ronda |
   | **Nombre** | `fraccion_informal_previa` — el que ya consumen `capa.decidir_arquetipo()` y el `contexto` de la ablación |
   | **Tipo** | `float` en `[0,1]`. `0.0` = toda la planta en regla, `1.0` = toda fuera |
   | **Clave** | Por `arquetipo_id` (el `id` de `behavior/arquetipos.py`) |
   | **Quién manda** | `engine/`. Es la ÚNICA fuente; `behavior/` deja de calcularlo |
   | **Cuándo** | Al empezar cada ronda `n ≥ 1`, ANTES de renderizar el prompt |
   | **Análogo** | Lo mismo para el empleo: fracción de la planta ORIGINAL que sigue empleada, acumulativa contra la línea base sin política |

   **El punto de sutura, exacto.** En `behavior/rondas.py`, dentro de `correr()`,
   están los dos diccionarios que hoy hacen de andamio:

   ```python
   frac_informal: dict[str, float] = {a.id: (0.0 if a.formal else 1.0) for a in arquetipos}
   empleo:        dict[str, float] = {a.id: 1.0 for a in arquetipos}
   ```

   Cuando `engine/` exponga el estado, esos dos dicts dejan de escribirse y pasan
   a LEERSE del motor; el resto del bucle no cambia una línea, porque
   `fraccion_informal_previa` ya viaja hasta el prompt y hasta el `contexto`.
   El bloque de actualización que hoy los pisa (después de resolver la ronda) es
   lo que se borra.

   **Mientras tanto** el andamio se queda, porque sin él la ronda n+1 contradice
   a la ronda n y las dos métricas del pitch mienten. Está marcado como andamio
   en el comentario del código, no escondido. **Este punto queda ABIERTO y
   bloqueado por R2.**

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
- **Máximo 3 reintentos** tras veto, luego fallback a `cumplir` — canon de
  `docs/IDEA.md` §5.3 y §5.7 y de `engine/MODELO.md`, cambiado en este PR
  (antes decía `absorber`, y la divergencia no era inocua: para una unidad
  informal `absorber` puntúa 1.0 fuera de regla y `cumplir` puntúa 0.0). El
  fallback queda marcado con `fue_fallback: True` para que se pueda contar.
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
