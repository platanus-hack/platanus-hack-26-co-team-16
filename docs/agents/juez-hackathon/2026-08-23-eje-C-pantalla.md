# Juicio — 2026-08-23 04:17 · modo repo · EJE C · PANTALLA

> Informe del agente `juez-hackathon`. Autocrítica interna del equipo, no una evaluación externa.
> **Material juzgado:** `web/` (código, sin navegador). El deploy vivo lo cronometra otro; lo que dependía de él va marcado [SOSPECHA].
> **Commit:** `f9e705c` · **Rama:** `worktree-revision-eje-C`
> **Pregunta:** un juez que solo mira la pantalla, ¿entiende el problema de la espina y lo que ve es cierto?

**Delta contra `2026-08-23-0009-repo.md`:** cerrado el `<FILL THIS>` (`platanus-hack-project.jsonc:22` ya tiene la URL). Sigue abierto: la cifra de masa salarial calculada en el navegador (`Metricas.tsx:35`, ahora además muerta), y la banda que cubre un solo número.

**Respuesta corta a los 20 segundos:** un juez que abre la URL lee «HIVE · quién cumple una política, y a quién le cae encima» (`componentes/Carga.tsx:81`) y después «¿Qué política quieres estresar?» (`componentes/Menu.tsx:27`). Concluye: *un simulador bonito de salario mínimo con un slider*. No hay una sola palabra sobre que la proyección oficial supone cumplimiento, ni sobre que la informalidad se sabe un año tarde, ni sobre el error publicado. La espina y la pantalla cuentan historias distintas.

---

## 1. MENTIRAS

**M1 · «la proyección oficial» no existe en ninguna parte del código.** [VERIFICADO]
- En cristiano: la pantalla dice que compara contra el pronóstico del gobierno. Está comparando el modelo consigo mismo.
- La cifra secundaria del lienzo se llama «brecha contra la proyección oficial» (`web/enjambre/componentes/Paneles/Hero.tsx:69`) y se calcula como `ronda_última − ronda_0` (`Hero.tsx:56`, `lib/corrida.ts:112-113`).
- El reporte repite el rótulo como cifra de portada (`app/reporte/page.tsx:182`) y la gráfica A1 lo afirma en prosa: *«La línea punteada es lo que el modelo oficial asume: que todo el mundo cumple, para siempre»* (`componentes/reporte/Graficas.tsx:115-117`).
- La ronda 0 **no** es cumplimiento total: es «la reacción ingenua, sin LLM» (`api/servidor.py:62`) y arranca en la informalidad observada post-política (`api/servidor.py:401`; `docs/vet/00-hallazgos.md:10`, S3-1: 30,57%).
- Mismo error en dos sitios más: `lib/narrativa.ts:99` («el escenario de cumplimiento total») y `componentes/enjambre/motorVisual.ts:25` («la ronda 0 … es la proyección oficial»).
- Un juez con un agente lo encuentra en un grep. Es la primera cifra de la pantalla y es la más fácil de tumbar.

**M2 · La pantalla dice «RONDA 0 DECIDIENDO» durante toda la corrida, y el contador da ~15 vueltas.** [VERIFICADO]
- En cristiano: el enjambre repite cinco veces lo mismo, el rótulo nunca avanza, y parece un bucle roto.
- Las rondas **no** se transmiten mientras se calculan: salen todas juntas al final, y solo las de la trayectoria mediana (`api/servidor.py:369-373` y `:414-419`).
- `rondaMostrada` queda `null` hasta ese momento, así que `Titulo.tsx:35` fija `enCurso = 0` y muestra `RONDA 0 DECIDIENDO · x/81 CELDAS` de principio a fin. `Hero` no dibuja nada (`Hero.tsx:50`).
- Los eventos de decisión sí traen `trayectoria` (`api/servidor.py:342`), pero el almacén **nunca lo lee** (`estado/simulacion.ts:199-203`): las 5 pasadas × 4 rondas se ven como un solo contador que reinicia sin explicación.
- La barra de tiempo tampoco avanza: solo el segmento R0 se llena, y con un reloj local de 10 s (`Paneles/BarraTiempo.tsx:64`, `motorVisual.ts:35`).

**M3 · La procedencia se equivoca justo en el número que carga la incertidumbre.** [VERIFICADO]
- En cristiano: el panel que existe para decir de dónde sale cada cifra, en la banda dice una fuente que no es.
- `Paneles/Procedencia.tsx:44`: «Banda de incertidumbre (p10–p90) · CALCULADO · paráfrasis del mismo prompt, N≥2».
- El backend dice lo contrario: `PARAFRASIS_EFECTO = "ninguno"` (`api/servidor.py:96`), el parámetro «HOY NO HACE NADA» (`api/servidor.py:246-253`), y la banda publicada es la dispersión **entre trayectorias** (`api/trayectorias.py:113-118`).
- Y el rótulo «Banda de incertidumbre · p10–p90» se lee como intervalo de confianza. Es dispersión entre 5 paráfrasis, sin calibrar. Ningún texto de pantalla lo dice.

**M4 · «seed 42» impreso como si gobernara algo.** [VERIFICADO]
- En cristiano: mostramos la semilla como sello de rigor, y la semilla no cambia ningún resultado.
- `app/reporte/page.tsx:161` imprime `seed {registro.seed}`; `api/servidor.py:80` declara `SEED_EFECTO = "etiqueta"` con la medición al lado (seed 42 vs 99, trayectorias idénticas).

---

## 2. HUÉRFANOS — candidatos a salir de la DEMO (no del repo)

- **`/laboratorio`** — 5 líneas en `web/laboratorio/historico.jsonl` y un título que dice «Lo que sabemos después de 5 corridas» (`app/laboratorio/page.tsx:44`). No sirve a ningún paso de la espina y en Render el disco es efímero, así que no crece. Fuera de la demo.
- **`Metricas.tsx` + `CurvaBrecha.tsx`** — código muerto, declarado muerto por su propio encabezado (`Paneles/Metricas.tsx:3-9`). Ya no se ve; sigue siendo el archivo donde un agente encuentra la masa salarial calculada en el navegador (`Metricas.tsx:35`).
- **Botón «Simular política personalizada · bloqueado»** (`componentes/Menu.tsx:43-48`) — en 3 minutos, un botón deshabilitado solo genera la pregunta «¿y eso qué hace?». Respuesta: nada.
- **La intro de ~10,25 s** (`motorVisual.ts:35`) — 10 de los 180 segundos del pitch en una animación de nacimiento.
- **`Noticias` / «El Centinela · medio ficticio»** (`lib/narrativa.ts:109`) — titulares inventados en el producto cuyo argumento es «publicamos nuestro error». Riesgo alto, aporte cero a la espina.

## 3. FALTANTES — lo que la espina promete y la pantalla no entrega

- **El error del backtest no está en la pantalla.** Los 37,37 pp viven en `/reporte`, en la **última viñeta** de «dónde no hay que creerle», después de seis gráficas (`app/reporte/page.tsx:272-279`). La espina dice que es la mitad del producto; la interfaz lo trata como letra chica. En `/` no aparece nunca.
- **El veto no tiene rótulo.** «Sin caja para indemnizar no puedes despedir» es lo más defendible que hay, y en el lienzo es un destello rojo de 0,35 de pulso sin leyenda (`componentes/enjambre/Empresas.tsx:128`; `Paneles/Leyenda.tsx:36-40` tiene 4 fichas y ninguna es el veto). Solo se explica al pasar el mouse (`Globo.tsx:153`) o en el reporte.
- **Ningún número de la pantalla principal sale con banda**, contra `AGENTS.md` §restricciones. La banda solo existe en `/reporte` (`reporte/Graficas.tsx:105`).
- **Fallback y sin-salida no se distinguen en el mapa.** Existen como cifras agregadas y mudas (`Hero.tsx:86-101`), pero una celda que cayó al fallback se dibuja igual que una que decidió de verdad: `motorVisual.ts` no conoce esos campos.
- **Cero copy del problema** en las tres primeras pantallas (`Carga.tsx:81`, `Menu.tsx:27`, `ControlPolitica.tsx:36`).
- **La corrida no cabe en la demo.** Una corrida LLM medida son **166 s con una paráfrasis** (`docs/DEPLOY.md:31`), el default son **5 trayectorias** (`api/trayectorias.py:53`) corridas **en serie** (`api/trayectorias.py:132`), y el caché no se versiona (`behavior/.gitignore` → `.cache/`), así que en Render arranca frío. Del orden de 10-14 minutos sin que se mueva un número. [SOSPECHA hasta que llegue el cronómetro; el código no ofrece otra lectura]

## 4. LOS 3 ARREGLOS

**A1 · Rebautizar la brecha.** `web/` (Dani) · 20 min.
- Cambiar «proyección oficial» por «escenario sin adaptación · ronda 0 del modelo» en `Hero.tsx:69`, `app/reporte/page.tsx:182`, `reporte/Graficas.tsx:115-117`, `lib/narrativa.ts:99`, `motorVisual.ts:25`, `lib/corrida.ts:112`.
- Verificación: `grep -rn "proyección oficial\|cumplimiento total" web/enjambre` devuelve 0.
- **SI NO LO ARREGLAMOS:** el juez pregunta «muéstrenme esa proyección oficial» y no existe ninguna. La cifra grande de la pantalla pasa a ser inventada, y ahí se cae todo lo demás.

**A2 · Que la espera diga la verdad, y que la banda diga qué es.** `web/` (Dani) · 25 min.
- Leer `d.trayectoria` en `estado/simulacion.ts:199` y mostrar «trayectoria 2 de 5 · ronda 1» en `Titulo.tsx:71` en vez de `RONDA 0` fijo.
- Cambiar `Procedencia.tsx:44` a «dispersión entre 5 trayectorias (una paráfrasis cada una), sin calibrar — NO es un intervalo de confianza», y poner esa misma línea bajo la gráfica de brecha.
- Verificación: correr con `?modo=reglas` y `trayectorias=2` y ver el rótulo cambiar; grep de «intervalo» y «confianza» en 0.
- **SI NO LO ARREGLAMOS:** la pantalla parece colgada varios minutos y el juez lee el rango como un intervalo de confianza que no calculamos. Las dos cosas juntas son la definición de humo.

**A3 · Subir el error a la primera pantalla.** `web/` (Dani) · 15 min.
- Una línea fija bajo el logo en `Carga.tsx:80` y en `Menu.tsx:25`: «Este simulador publica su propio error: 37,37 pp, con el signo al revés. Perdió ocho veces contra "el año que viene igual que este".»
- Verificación: se lee sin hacer un solo clic, en `/`.
- **SI NO LO ARREGLAMOS:** lo único que ningún otro simulador entrega queda enterrado en el pie de una página secundaria, y en pantalla somos un simulador más que promete el futuro.

## 5. LA PREGUNTA QUE NOS HUNDE

> **«Esa banda azul y ese número de brecha: enséñenme en la pantalla contra qué proyección se están comparando y qué me garantiza el rango.»**

Hoy no se puede contestar. La comparación es contra la ronda 0 del propio modelo, que además ya trae la reacción ingenua adentro y arranca del dato post-política; y el rango es la dispersión entre cinco paráfrasis sin calibrar, rotulado en pantalla como «banda de incertidumbre» y atribuido a una fuente equivocada. Las dos afirmaciones están en la pantalla y ninguna se sostiene sin abrir `api/servidor.py`.
