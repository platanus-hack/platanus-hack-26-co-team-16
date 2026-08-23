# Handoff — Dani · R4 · Diseño e interfaz

> **Tu memoria entre sesiones.** Léelo al abrir tu sesión de agente, actualízalo antes de cerrarla.
> Este archivo es solo tuyo: nadie más lo edita, así nunca da conflicto de merge.
> Tus carpetas: `web/` · Tu rama: `rol/interfaz`
> Tu misión, entregables y prompt de arranque: [`docs/ROLES.md`](../ROLES.md)

## Dónde quedé

_Lo más reciente arriba. Qué existe, qué acabas de hacer, qué necesita saber tu próxima sesión para no arrancar de cero. Corto: enlaza a commits y ADRs en vez de copiarlos._

### 2026-08-23 08:52 — **Realismo del empleador: los prompts dejan de congelar el mundo.** ⚠️ fuera de `web/`

Está en `main`, dentro del commit **`3f5d3d9 final`**. Archivo nuevo: **`behavior/contexto.py`** (445
líneas). Tocados: `behavior/prompts/{sistema,arquetipo}.md`, `parafrasis/p3.md`, `p5.md`,
`behavior/{capa,rondas}.py`, `api/{servidor,trayectorias}.py`.

> **⚠️ ESTO NO ES MI CARPETA.** `behavior/` es de Nico (R3) y `api/` de Manuel (R2). Lo hice porque
> se me pidió de frente, no por descuido, y lo declaro acá para que nadie lo descubra por un
> conflicto de merge. **Si Nico o Manuel abren sesión, este es el primer párrafo que tienen que
> leer.** Sale de mi propio hallazgo de la sesión anterior
> ([`hallazgos-dani-cache-decisiones.md`](hallazgos-dani-cache-decisiones.md)) y del encargo de
> [`docs/ultimo-momento/revision-prompts-empleadores.md`](../ultimo-momento/revision-prompts-empleadores.md)
> — que, ojo, decía **«NO APLICAS NINGÚN CAMBIO»**. Se aplicaron igual, por decisión de Dani.

**El problema, medido en la sesión anterior:** 1 despido en 518 decisiones ante un alza del 23%.
No era criterio del modelo, era aritmética: *«Nada más cambia: tus ingresos, tus clientes y tu
capacidad de producción son los mismos»* congelaba la demanda, y con ingreso fijo **no existía
estado del mundo en el que despedir fuera la mejor respuesta**. Y `subir_precios` era *«trasladas
el costo a tus clientes»* en un mundo donde los clientes no se pueden ir: 27% salió por ahí.

**La restricción que mandó en todo el diseño.** `engine/veto.py` costea `despedir`/`cumplir`/
`absorber`/`bajar_horas` contra `flujo_caja × 3` y **nunca costea `subir_precios`**. El repo ya se
quemó con esto una vez (defecto A3: el agente calculaba con caja mensual y el veto con trimestral —
*«estaban mirando billeteras distintas»*). Por eso la regla que seguí: **nada de lo que agregué es
un número que el motor también calcule.** Todo es cualitativo — ordena preferencias, no entra a la
aritmética. Caja, indemnización y sanción siguen siendo las únicas cifras del prompt y siguen
siendo exactamente las del motor.

**Los cinco mecanismos, cada uno con su porqué:**

1. **La demanda se descongela, y la justificación es específica del choque.** El alza del piso
   laboral mueve los DOS lados del mostrador: quien le vende a hogares que viven de ese piso puede
   ver la venta sostenerse o subir; quien vende contra un precio cerrado antes del alza tiene el
   valor de su venta congelado y solo le subió el costo. Mismo choque, signo contrario, por sector.
   **Eso es lo que vuelve el despido una opción viva sin tocar un solo número del motor.**
2. **El traslado a precios tiene techo, y el techo es la tasa de informalidad.** Tu competidor de
   precio está fuera de regla con probabilidad ≈ la proporción de unidades fuera de regla, que el
   agente ya ve en el prompt. **Es un segundo canal de la cascada** y empuja en la misma dirección
   que el primero: más evasión no solo baja p(inspección), también le quita capacidad de traslado a
   quien se quedó adentro. Verificado: 0% de informalidad → 0 firmas con rival fuera de regla;
   100% → 86 de 101.
3. **Estar fuera de regla cuesta sin inspector**: el trabajador que se va molesto reclama, los
   compradores grandes piden soporte de aportes, el trabajador entrenado se va con quien se los
   pague. Ataca el hallazgo §3.3 (los que veían 0,3% informalizaban con limpieza mecánica) **sin
   tocar p**, así que la cascada sigue intacta.
4. **El margen tiene piso porque es el ingreso del hogar del dueño.** En la caché había
   `reduccion_margen_pct: 100` — el dueño trabajando gratis. Nadie hace eso, cierra antes.
5. **Aleatoriedad como heterogeneidad, no como ruido.** Los **rasgos** (quién te compra, competidor,
   planta, margen, experiencia de inspección, compromisos) se sortean SIN la ronda: la firma es la
   misma en el periodo 1 y en el 3. Los **choques** (cómo viene la venta, cliente perdido, pagador
   tarde) se sortean CON la ronda. Todo determinista en el seed.

**Efecto colateral que importa: la perilla `seed` de la API por fin hace algo.** Estaba rotulada
`SEED_EFECTO = "etiqueta"` justamente porque `capa.renderizar()` no recibía seed, así que dos
semillas hasheaban el mismo prompt y pegaban en la misma entrada del caché. Ahora el seed elige el
contexto de cada firma → **`SEED_EFECTO = "trayectoria"`** (`api/servidor.py:85`). Actualicé esa
línea y los otros tres sitios que afirmaban lo contrario (`api/servidor.py` `description` del
Query, `api/trayectorias.py:19`). **En el camino de reglas fijas sigue siendo una etiqueta y está
bien así: la ablación no lee el prompt, y esa es justo la comparación que la hace útil.**

**Verificado, no afirmado:**

| Qué | Resultado |
|---|---|
| 1.818 prompts renderizados (3 seeds × 101 arquetipos × 3 rondas × re-skin on/off) | **0 contaminados** |
| `python3 -m behavior.higiene` | `7/7 prompts limpios` |
| `make test` · `pytest tests/` · `python3 -m behavior.pruebas` | 88 · 11 · todas pasan |
| `python3 -m behavior.demo` (ablación, $0) | corre de punta a punta |
| Determinismo, persistencia de rasgos, varianza de choques | verificados uno por uno |

**LO QUE NO SE MIDIÓ, Y HAY QUE DECIRLO:** no hay `ANTHROPIC_API_KEY` en el entorno, así que
**ninguna decisión nueva se ha visto**. No sé si los despidos subieron. El mecanismo está puesto y
el razonamiento está escrito, pero el reparto 40,7 / 27,0 / 23,9 **sigue sin probarse contra estos
prompts**. Cualquiera que diga lo contrario está afirmando sin evidencia.

**Costo si se vuelve a correr:** el prompt pasó de ~943 a ~2.026 tokens de entrada (+1.083 por
llamada). Sobre 518 llamadas son **~$1,68 encima de los ~$7,87** de recomprar el caché que este
cambio invalidó (`cache.clave()` hashea el prompt). Y mientras no se pague, `scripts/reproduce.py`
cae al nivel 2 de la [ADR 0009](../adr/0009-reproducibilidad.md) (ablación de reglas fijas).

**Lo que deliberadamente NO hice.** La vía real por la que una PYME reduce planta sin indemnizar es
**no renovar un contrato a término fijo**. No se la conté al agente: el veto cobra `costo_despido`
por cualquier `empleados_a_despedir`, así que habría recreado el defecto A3 exacto. Hacerlo bien
exige una fracción de planta a término fijo en `engine/` — carpeta de Manuel, y es la opción cara.

### 2026-08-23 07:30 — **PR #25 mergeado (`357c5e2`). El frontend entero está en `main`.**

37 archivos, **+3.055 / −304** en `web/`, 14 commits míos entre las 00:59 y las 01:48.
Es la iteración 2 y 3 completas del frontend. `rol/interfaz` **no tiene nada por delante de
`main`** (`git rev-list --count main..rol/interfaz` = 0): si abres sesión, arrancas de `main`.

**Lo que existe hoy en `web/enjambre/` (Next.js 15.5 · React 19 · TS estricto · zustand · three.js):**

| Capa | Archivos | Qué hace |
|---|---|---|
| Estado | `estado/simulacion.ts`, `estado/flujo.ts` | almacén zustand + cliente SSE contra `/api/simulaciones/flujo` |
| Escena | `componentes/enjambre/{Escena,Empresas,Personas,Onda,motorVisual}.tsx` | el enjambre: hexágonos-empresa, abejas-persona, onda de informalización |
| Paneles | `componentes/Paneles/*` + `Noticias`, `Relato`, `Globo`, `Simulacion` | lo que se ve encima del lienzo |
| Reporte | `app/reporte/page.tsx` + `componentes/reporte/Graficas.tsx` | 6 gráficas SVG a mano + hallazgos calculados + `window.print()` |
| Laboratorio | `app/laboratorio/*`, `componentes/laboratorio/Graficas.tsx`, `web/scripts/graficas_laboratorio.py` | histórico de corridas en JSONL |
| Librería | `lib/{disposicion,narrativa,corrida,formato}.ts` | disposición determinista, titulares, registro de corrida |

**Cero dependencias nuevas** (feature freeze, `AGENTS.md` §restricciones): las gráficas son SVG
escrito a mano, el PDF es `window.print()` + `@media print`, y el script de Python es **solo
biblioteca estándar**. No hay chart lib, no hay lib de PDF, no hay matplotlib.

**Lo que se construyó, por bloque:**

- **P0 · ruido y solapamientos.** Los tres solapamientos verificados (Estrategias×Leyenda,
  Noticias×Metricas, botón×Hero) se cerraron fusionando la columna izquierda en
  `Paneles/ColumnaIzquierda.tsx`.
- **S2-5 · el split-brain.** El almacén distingue `rondas` (lo que **llegó** por el cable) de
  `rondaMostrada` (lo que se **está viendo**), y todo lo que narra o grafica lee de
  `rondasVisibles()` (`estado/simulacion.ts:240`). Antes, con caché caliente, media pantalla
  contaba una ronda y la otra media contaba otra. Se migraron los 5 consumidores; el quinto
  (`Globo.tsx`) se me pasó en la fase 1 y se cazó en la fase 4.
- **P1 · pausa por ronda.** La API **no sabe pausar** (`api/servidor.py`: hilo daemon que empuja a
  una cola sin backpressure), así que la pausa es del cliente: el buffer ya tiene la corrida
  entera y `motorVisual.ts` decide a qué ritmo se reproduce. Botón `Paneles/Continuar.tsx`.
- **P2 · intro.** ~10,25 s de nacimiento escalonado (`DURACION_INTRO` en `motorVisual.ts:35`).
- **P4 · vida.** Deriva continua por celda (dos senos desfasados por índice), cola de decisiones
  repartida en 4 s por ronda, viaje intra-empresa órbita formal → órbita informal.
- **P5 · rebrand HIVE.** Logo en `public/hive-logo.png`, con fallback tipográfico.
- **P6 · hover.** El globo distingue `hoverTipo: "empresa" | "personas"`, porque el disco y la
  nube que lo orbita responden preguntas distintas.
- **Iteración 3.** El mapa se queda con el 85% de la pantalla (`4691cb9`); las noticias pasaron a
  burbujas cuadradas flotantes arriba (`Noticias.tsx`, `@keyframes burbuja-entra`); el Hero
  muestra **cifras mudas** (solo el número, la etiqueta aparece al pasar el mouse o al fijarla); y
  el reporte se reconstruyó alrededor de gráficas (`6729ceb`).

### 2026-08-23 — Alejo tocó `web/` tres veces, y esos commits ya están en `main`

Rompe la regla de un dueño por carpeta, pero está mergeado y es correcto. **No lo re-hagas:**

- `024340b` — *«reporte: la procedencia vuelve, y la cascada deja de ser un hallazgo»*
- `e4ff8a2` — *«paneles: el rótulo de modo deja de quedar debajo de las burbujas»*
- `c6aa889` — *«huérfanos y laboratorio: que cada archivo diga si se monta»*

De ahí salió que **`Paneles/Metricas.tsx` y `Paneles/CurvaBrecha.tsx` NO se montan** y lo dicen en
su propio encabezado. `Simulacion.tsx` monta hoy: `Globo`, `BarraTiempo`, `ColumnaIzquierda`,
`Continuar`, `Hero`, `Titulo`, `Noticias`. Los dos huérfanos se conservan a propósito (son el
único sitio donde la masa salarial y bajo-el-mínimo están cableadas a pantalla); **no se borran**
—decisión de `10-fusion.md` §3: *«Borrar código a las 5am con cinco ramas vivas produce
conflictos, no claridad»*.

### 2026-08-22 → 23 — Lo anterior (historia)

- El prototipo `web/prototipo/mapa.html` se **superó**: el motor visual se portó a `web/enjambre/`
  cambiando solo la fuente de datos. Se conserva por trazabilidad. Las decisiones de diseño y su
  porqué siguen en [`web/DISENO.md`](../../web/DISENO.md) — **léelo antes de tocar la escena**.
- Se descartó Claude Design: la pieza es movimiento y densidad, y un artboard estático no puede
  juzgar ninguna de las dos.

## En qué estoy trabajando

**Los cinco arreglos que la revisión a tres ejes me asignó** ([`docs/vet/revision-3ejes/10-fusion.md`](../vet/revision-3ejes/10-fusion.md) §1).
Son **95 minutos**, el segundo dueño más cargado después de Juanda. Ninguno está hecho: los greps
de verificación siguen fallando todos. El informe completo del que salen C1/C2/C3 es
[`docs/agents/juez-hackathon/2026-08-23-eje-C-pantalla.md`](juez-hackathon/2026-08-23-eje-C-pantalla.md).

- [ ] **C1 · Rebautizar la brecha** (20 min). «proyección oficial» → «escenario sin adaptación ·
      ronda 0 del modelo». La ronda 0 **no es** cumplimiento total: es la reacción ingenua sin LLM
      y arranca de la informalidad observada post-política.
      Sitios: `Paneles/Hero.tsx:70`, `app/reporte/page.tsx:182`, `reporte/Graficas.tsx:84,115`,
      `lib/narrativa.ts:99`, `lib/corrida.ts:112`, `motorVisual.ts:25`, `Relato.tsx:86`,
      `Paneles/CurvaBrecha.tsx:9,16,73`.
      **Verificación:** `grep -rn "proyección oficial\|cumplimiento total" web/enjambre` = 0.
      Hoy devuelve **12**.
- [ ] **C2 · Que la espera diga la verdad y la banda diga qué es** (25 min). Las rondas no se
      transmiten mientras se calculan: salen todas al final, así que `rondaMostrada` queda `null` y
      `Titulo.tsx` muestra `RONDA 0 DECIDIENDO · x/81 CELDAS` durante toda la corrida, con el
      contador dando ~15 vueltas. Los eventos de decisión **sí traen `trayectoria`**
      (`api/servidor.py:342`) y el almacén nunca lo lee (`estado/simulacion.ts:199-203`).
      Leerlo y mostrar «trayectoria 2 de 5 · ronda 1». Y `Paneles/Procedencia.tsx:44` dice que la
      banda son «paráfrasis del mismo prompt, N≥2» cuando el backend dice
      `PARAFRASIS_EFECTO = "ninguno"`: cambiar a *«dispersión entre 5 trayectorias (una paráfrasis
      cada una), sin calibrar — NO es un intervalo de confianza»*.
      **Verificación:** grep de «intervalo» y «confianza» en 0.
      **Estado medido 08:52:** la mitad de texto **ya está hecha** — el grep de «intervalo\|confianza»
      da 2 y las dos son `Procedencia.tsx:46-47`, o sea el comentario que explica la retractación y
      una frase que **niega** correctamente (*«NO es un intervalo de confianza ni un p10/p90
      calibrado»*). Lo que queda de C2 es el contador de trayectoria en `Titulo.tsx`.
      ⚠️ **Y la premisa cambió:** `PARAFRASIS_EFECTO` sigue en `"ninguno"`, pero `SEED_EFECTO` pasó
      a `"trayectoria"` (entrada del 08:52). Si algún texto de `web/` dice que el seed no cambia
      nada, ahora es falso.
- [ ] **C3 · Subir el error del backtest a la primera pantalla** (15 min). Los 37,37 pp viven en la
      **última viñeta** de `/reporte`, después de seis gráficas. Una línea fija bajo el logo en
      `Carga.tsx:80` y en `Menu.tsx:25`. **Verificación:** se lee en `/` sin un solo clic.
- [ ] **B1 · Rebautizar el mapa** (20 min, con Juanda). Decir de qué está hecho: «carga legal por
      celda (sobrecosto prestacional + costo de despido del CST)».
      **Verificación:** `grep -rn "no puede pagar\|quién aprieta" web/` = 0 *(ya da 0 — confirmar
      que el rótulo nuevo existe, no solo que el viejo se fue)*.
- [ ] **B3 · Quitar «cobertura» del número** (15 min, con Juanda). Vive en `scripts/validate.py:206`,
      que **no es mi carpeta**: lo mío es que ningún texto de `web/` lo repita.
- [ ] **D1 · El seed está clavado en 42 en el cliente** (10 min). **Esto lo creé yo hoy.**
      `estado/flujo.ts:38` arma el query con `seed: "42"` literal. Mientras el seed era una etiqueta
      daba igual; desde la entrada del 08:52 el seed **elige el contexto de cada firma**, así que
      con el 42 clavado la pantalla nunca puede mostrar otra población sobre los mismos arquetipos.
      Es la perilla más barata que tenemos para enseñar variabilidad en vivo.
      **Verificación:** `grep -n 'seed: "42"' web/enjambre/estado/flujo.ts` = 0.
      *(Revisado también: ningún texto de `web/` afirma que el seed no cambia nada, así que no hay
      nada que retractar — solo que cablear.)*

## Bloqueado / esperando a alguien

- **NADIE HA ABIERTO LA INTERFAZ EN UN NAVEGADOR.** Todo el trabajo se verificó con
  `npx tsc --noEmit` y con corridas SSE por `curl`. La intro, los hexágonos, las abejas, las
  burbujas y el botón de continuar **no los ha visto un ojo humano**. Está declarado en el PR #25.
  Es lo primero que hay que hacer en la próxima sesión.
- **Juanda (R5) · el deploy no es `main`.** La rama desplegada es un ancestro estricto: le faltan
  15 commits, **incluido `024340b`**. Cualquier cosa que yo mergee antes de que él arregle eso, el
  juez no la va a ver. Es el arreglo que desbloquea a otros cinco.
- **NO HAY `ANTHROPIC_API_KEY` EN EL ENTORNO.** Es lo que bloquea la única pregunta abierta del
  cambio de prompts del 08:52: **¿los despidos subieron?** Sin key no se ha visto ni una decisión
  nueva. Una sonda de ~30 llamadas cuesta **~$0,50** y contestaría; una corrida completa de 518
  cuesta **~$9,55** (los ~$7,87 del caché quemado + ~$1,68 del prompt más largo) y además devuelve
  `scripts/reproduce.py` al nivel 1. **Es una decisión de plata, no técnica.**
- **Nico (R3) · el modo reglas está saturado.** Medido con llamadas directas a la API a 5 / 13,5 /
  23 / 40%: informalidad **31,010% en los cuatro**, empleo 94,890% en los tres primeros. La causa
  está en `behavior/ablacion.py`: `costo_informal = ingreso + p·multa ≈ 1,20·ingreso` contra
  `costo_formal = ingreso·factor·(1+alza)`, que ya lo supera al 5%. **Consecuencia para mí: el
  camino de demo de $0 (`?modo=reglas`) es insensible al slider.** No es mío arreglarlo.
  ⚠️ **El cambio de prompts del 08:52 NO arregla esto, y no podía**: la ablación no lee el prompt
  —esa es justamente su razón de ser como contrafactual—, así que `?modo=reglas` sigue igual de
  saturado. Verificado: `python3 -m behavior.demo` da el mismo 50,0% de siempre. Si alguien asume
  que los prompts nuevos destaparon el slider de la demo de $0, **se va a llevar la sorpresa en
  vivo**.
- **Manuel (R2) + Alejo (R1) · datos que se calculan y se tiran** (`docs/VARIABLES-PENDIENTES.md`):
  `fraccion_firmas_fuera_de_regla` se calcula en `behavior/rondas.py:295-310` y se descarta;
  `vetadas` se publica por arquetipo y nunca se suma por ronda (lo sumo yo en
  `lib/corrida.ts:vetadasDeRonda`); y la **exposición al mínimo es derivable** — `empresa_id` mapea
  1:1 a `(sector, tamano)` en `poblacion.parquet`, el join da **81/81 celdas**, y la exposición
  ponderada al mínimo anterior es **10,02%**. Faltan 3 columnas en
  `data/construir_empresas.py:134-157`.

## Supuestos que tomé

_Todo lo que decidiste sin dato duro. Además del `# SUPUESTO:` en el código, anótalo acá para que R5 lo recoja en `VALIDATION.md`._

### Los 10 de `behavior/contexto.py` (nuevos, 23-ago 08:52) — **para `VALIDATION.md`**

`grep -n "SUPUESTO:" behavior/contexto.py` = **10**. Son repartos de probabilidad, y **ninguno
entra a la aritmética del motor**: solo ordenan preferencias del agente (esa fue la regla de diseño,
ver la entrada del 08:52). Aun así son supuestos y R5 tiene que recogerlos:

| Dónde | Qué se supone | Cómo defenderlo |
|---|---|---|
| `:115` | El reparto sector → régimen de precio (mostrador / pactado / tomador) | No sale de una fuente: sale de **cómo se cobra en cada actividad**. Quien vende al menudeo mueve el precio mañana; quien firmó por término o cotizó una obra a precio cerrado no. **La dirección es el modelo; los decimales son andamio.** |
| `:140` | Reparto de respaldo para un sector fuera de la tabla | Mitad y mitad — el reparto que menos supone |
| `:177` | Los tres repartos de perspectiva de venta | La **dirección** está justificada (el alza mueve los dos lados del mostrador); las magnitudes van al barrido |
| `:203` | El choque idiosincrático del periodo, con 55% de «nada fuera de lo normal» | La mayoría de los periodos no pasa nada. Es la heterogeneidad que la celda de la encuesta promedia y borra |
| `:235` | 15% sin competencia cercana | Una unidad de barrio cuyos clientes no tienen a quién más comprarle sí tiene traslado que las demás no |
| `:265`, `:336` | Cortes de tamaño para composición de planta y tope de margen | Dirección: entre más chica la unidad, más atada su planta y menos margen puede ceder, **porque el margen es lo que come su casa** |
| `:309` | Reparto de experiencia de inspección | La mayoría de los pequeños empleadores nunca ha visto una visita, y por eso la cifra del papel les dice poco |
| `:374` | Que la mayoría de unidades pequeñas tenga arriendo y una cuota corriendo | Redactado **al revés a propósito**: declara que la caja del prompt ya viene neta, para no crear una segunda billetera (defecto A3) |

**Todos son de dirección conocida y todos van al barrido de sensibilidad de R5.**

### Los 11 de `web/enjambre/`

**11 marcadores `SUPUESTO:` en `web/enjambre/`**, todos grepeables con
`grep -rn "SUPUESTO:" web/enjambre`. Ninguno afecta al motor: son escala visual y pisos de
visibilidad. Los que importan:

- **El LOD** (`lib/disposicion.ts:36`): 3.000 / 1.500 / **1.000** personas por punto.
  **El piso de 1.000 no se toca**, y la razón es de honestidad, no de legibilidad: la GEIH expande
  ~630 personas por fila encuestada, así que bajar de ahí es dibujar una resolución que la encuesta
  no tiene. Yo mismo lo bajé a 500 en un momento de la iteración 2 y me contradije con el
  comentario del propio archivo; está retractado en el mensaje de commit.
  Los dos niveles de arriba sí bajaron (de 8.000/3.000): con 8.000 por punto muchas celdas quedaban
  en 1-3 puntos y los despidos moderados eran **literalmente invisibles** por redondeo.
- **La disposición es una elipse** (`A=46, B=29`), no geografía. Se probaron barrios por sector con
  dispersión gaussiana y **se revirtió**: la elipse deja el enjambre como UN cuerpo; los barrios lo
  volvían un diagrama de sectores. Determinista por seed `20260322`.
- **El mapeo brecha→radio de la onda** (`Onda.tsx:60`): `4 + 55·√brecha`, tope 30, piso 0,04 pp.
  Escala visual arbitraria para que quepa en pantalla.
- **Los tres tamaños de punto** (1,30 / 0,88 / 0,62) y sus cortes de LOD (`Personas.tsx`).
- **Los pisos de «vale la pena mostrarlo»**: 0,05 pp en `Hero`, 0,1% y 0,5% en `Metricas`,
  ±3 pp de ventana mínima en `CurvaBrecha`.
- **El top-25 de celdas por peso** como corte de «lo que mueve el agregado» en `Relato.tsx`.

## Reglas de operación que aprendí a la mala

- **Nunca correr `npm run build` con `npm run dev` vivo.** Comparten `.next`, el mapa de chunks
  queda rancio y el servidor responde 500 (`Cannot find module './843.js'`). Para verificar tipos:
  **`npx tsc --noEmit`**, que no toca `.next`.
- **`app/laboratorio/registro/route.ts` está fuera de `/api` a propósito.** `next.config.mjs`
  reescribe `/api/:path*` hacia el backend de Python y el proxy se lo tragaría.
- **`/laboratorio` se queda fuera de la demo.** Decisión de `10-fusion.md` §3: 5 líneas de
  `historico.jsonl` sobre disco efímero en Render no sostienen el título «Lo que sabemos después de
  5 corridas». No se borra, no se muestra.
