# Handoff — Dani · R4 · Diseño e interfaz

> **Tu memoria entre sesiones.** Léelo al abrir tu sesión de agente, actualízalo antes de cerrarla.
> Este archivo es solo tuyo: nadie más lo edita, así nunca da conflicto de merge.
> Tus carpetas: `web/` · Tu rama: `rol/interfaz`
> Tu misión, entregables y prompt de arranque: [`docs/ROLES.md`](../ROLES.md)

## Dónde quedé

_Lo más reciente arriba. Qué existe, qué acabas de hacer, qué necesita saber tu próxima sesión para no arrancar de cero. Corto: enlaza a commits y ADRs en vez de copiarlos._

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
- [ ] **C3 · Subir el error del backtest a la primera pantalla** (15 min). Los 37,37 pp viven en la
      **última viñeta** de `/reporte`, después de seis gráficas. Una línea fija bajo el logo en
      `Carga.tsx:80` y en `Menu.tsx:25`. **Verificación:** se lee en `/` sin un solo clic.
- [ ] **B1 · Rebautizar el mapa** (20 min, con Juanda). Decir de qué está hecho: «carga legal por
      celda (sobrecosto prestacional + costo de despido del CST)».
      **Verificación:** `grep -rn "no puede pagar\|quién aprieta" web/` = 0 *(ya da 0 — confirmar
      que el rótulo nuevo existe, no solo que el viejo se fue)*.
- [ ] **B3 · Quitar «cobertura» del número** (15 min, con Juanda). Vive en `scripts/validate.py:206`,
      que **no es mi carpeta**: lo mío es que ningún texto de `web/` lo repita.

## Bloqueado / esperando a alguien

- **NADIE HA ABIERTO LA INTERFAZ EN UN NAVEGADOR.** Todo el trabajo se verificó con
  `npx tsc --noEmit` y con corridas SSE por `curl`. La intro, los hexágonos, las abejas, las
  burbujas y el botón de continuar **no los ha visto un ojo humano**. Está declarado en el PR #25.
  Es lo primero que hay que hacer en la próxima sesión.
- **Juanda (R5) · el deploy no es `main`.** La rama desplegada es un ancestro estricto: le faltan
  15 commits, **incluido `024340b`**. Cualquier cosa que yo mergee antes de que él arregle eso, el
  juez no la va a ver. Es el arreglo que desbloquea a otros cinco.
- **Nico (R3) · el modo reglas está saturado.** Medido con llamadas directas a la API a 5 / 13,5 /
  23 / 40%: informalidad **31,010% en los cuatro**, empleo 94,890% en los tres primeros. La causa
  está en `behavior/ablacion.py`: `costo_informal = ingreso + p·multa ≈ 1,20·ingreso` contra
  `costo_formal = ingreso·factor·(1+alza)`, que ya lo supera al 5%. **Consecuencia para mí: el
  camino de demo de $0 (`?modo=reglas`) es insensible al slider.** No es mío arreglarlo.
- **Manuel (R2) + Alejo (R1) · datos que se calculan y se tiran** (`docs/VARIABLES-PENDIENTES.md`):
  `fraccion_firmas_fuera_de_regla` se calcula en `behavior/rondas.py:295-310` y se descarta;
  `vetadas` se publica por arquetipo y nunca se suma por ronda (lo sumo yo en
  `lib/corrida.ts:vetadasDeRonda`); y la **exposición al mínimo es derivable** — `empresa_id` mapea
  1:1 a `(sector, tamano)` en `poblacion.parquet`, el join da **81/81 celdas**, y la exposición
  ponderada al mínimo anterior es **10,02%**. Faltan 3 columnas en
  `data/construir_empresas.py:134-157`.

## Supuestos que tomé

_Todo lo que decidiste sin dato duro. Además del `# SUPUESTO:` en el código, anótalo acá para que R5 lo recoja en `VALIDATION.md`._

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
