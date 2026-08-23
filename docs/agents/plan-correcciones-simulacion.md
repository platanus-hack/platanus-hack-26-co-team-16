# Plan de correcciones a la simulación

> **Escrito por Dani (R4) el 2026-08-22, ~H+16**, leyendo `DEFECTOS.md` (Juanda, corte H+15)
> contra el código en disco. **No es una decisión ni una orden**: es una propuesta con
> evidencia. Lo que el equipo confirme se gradúa a ADR o al registro de `engine/MODELO.md`.
> Cada corrección toca la carpeta de alguien más: **nadie edita fuera de la suya**.
>
> **Este documento es también un pre-registro.** Dice qué esperamos ver ANTES de correrlo.
> Si la corrida no lo confirma, se reporta que no lo confirmó. Eso es la mitad del valor.

---

## 0 · El resumen, de pie y en seis líneas

1. El simulador **le pita las faltas a un solo equipo**: castiga a quien intenta escapar
   (despedir, informalizar) y deja pasar gratis a quien dice "me aguanto" o "cumplo",
   que son justo las dos opciones que cuestan plata. Por eso, **entre más dura la
   política, menos incumplimiento mide**: al revés de la realidad y al revés de la
   literatura. Es un error de arbitraje, no de la IA.
2. El número **tiembla casi tanto como se mueve**: reformular la misma pregunta cambia el
   resultado 22,5 pp y cambiar la política solo lo cambia 31,9 pp. Hoy ningún número es
   defendible punto por punto.
3. La capa que decide **no está enchufada al motor**: usa un veto de juguete, una
   capacidad de fiscalización inventada (0,02) y una empresa inventada (0,18 de la
   nómina), cuando el motor y `data/` ya tienen las tres cosas con fuente.
4. Hay **13 correcciones**. Cuatro arreglan el signo, tres arreglan el temblor, cinco
   arreglan la trazabilidad, una es el experimento que le da el número al pitch.
5. Cuesta **~4 h de trabajo repartido en 4 personas y ~US$10 de LLM**, dentro del techo.
6. Y hay **cuatro cosas que NO se arreglan y se declaran**, con la dirección del sesgo.

---

## 1 · El diagnóstico, sin jerga: el árbitro pita para un solo lado

La simulación tiene dos piezas. Una **IA** que hace de empresario y propone qué hacer.
Un **árbitro de calculadora** que revisa si eso se puede pagar. La IA propone, el árbitro
manda. Ese reparto es lo mejor que tiene el proyecto.

El problema es **qué revisa el árbitro**. Hoy revisa exactamente dos jugadas:

| Jugada | ¿El árbitro la revisa? | ¿Cuesta plata? |
|---|---|---|
| Despedir gente | ✅ sí — "¿tienes para la indemnización?" | sí |
| Sacar gente de contrato | ✅ sí — "¿tienes tanta gente en regla?" | **no, ahorra** |
| **Cumplir** (pagar todo el costo formal) | ❌ **no la revisa** | **sí, es la más cara** |
| **Absorber** (aguantar el golpe con mi margen) | ❌ **no la revisa** | **sí** |

Léelo otra vez: **las dos jugadas que cuestan plata son las dos que nadie revisa.**

La consecuencia es mecánica y no tiene nada que ver con la IA:

> Cuando la política aprieta más, más empresarios intentan escapar (despedir,
> informalizar). El árbitro les pita más seguido. Y el reintento los empuja hacia la
> única salida que nadie les revisa: **"me aguanto"** — que es precisamente la que
> acaban de demostrar que no pueden pagar.

Está medido en nuestra propia corrida (`behavior/barrido-2026-08-22.log`):

| alza | propuestas vetadas | `absorber` (conteo) | `cumplir` (ponderado) |
|---|---|---|---|
| 7% | 0 | 33 | 31,4% |
| 10% | 1 | 49 | 34,7% |
| ~20% | **95** | **182** | 22,7% |
| ~23% | **93** | **196** | **9,7%** |

Entre más dura la política, más vetos, más gente parqueada en "me aguanto", **menos
informalidad medida**. Ese es el signo invertido del defecto §2.2. No es un misterio
estadístico: es una regla del juego mal escrita.

Y hay un número que lo cierra. Con los parámetros de hoy, la caja libre de una empresa es
el **18% de su nómina** y el sobrecosto de la formalidad es **~40% de la nómina**:

- **Aguantar** un alza es pagable solo hasta ~**12,9%** de alza. Por encima, ninguna
  empresa de la población puede — y hoy todas pueden, porque nadie las revisa.
- **Formalizarse** cuesta 40-58% de la nómina contra un 18% de caja: **ninguna unidad
  informal de Bogotá puede pagarlo**, nunca. Y hoy entre el 10% y el 31% de la población
  "se formaliza" gratis cada ronda.

Ese "gratis" es el defecto §2.2, el §1.6 (la informalidad que se devuelve en la ronda 3)
y buena parte del §2.1 (el temblor), todos con la misma raíz.

---

## 2 · Las correcciones

Formato de cada una: **qué pasa hoy · qué se cambia · cómo lo vas a ver · dueño · costo**.

### Bloque A — Que el número deje de mentir *(el signo)*

#### A1 · El árbitro pita para los dos lados 🔴 *la corrección más importante del plan*

- **Hoy:** `cumplir` y `absorber` pasan sin revisión, aunque sean las jugadas caras.
- **Se cambia:** el veto revisa las cuatro jugadas con la **misma regla que ya usa para
  despedir**: *"¿esto cabe en la caja del trimestre?"*. Formalizar la planta cuesta el
  costo formal completo; absorber cuesta el sobrecosto del alza. Si no cabe, el árbitro
  dice que no y explica por qué, igual que hoy explica lo de la indemnización.
- **No es afinar el modelo hasta que dé lo que queremos.** Es aplicar el principio que el
  propio prompt del sistema ya le declara al agente —*"no puedes gastar plata que no
  tienes"*— a las dos estrategias que se lo estaban saltando.
- **Cómo lo vas a ver:** la columna `informalidad` **deja de devolverse en la ronda 3** y
  el barrido de 5% a 20% **deja de bajar y empieza a subir**. En el desglose final,
  `cumplir` cae fuerte en las políticas duras (hoy 9,7-31%) porque deja de ser gratis, y
  el `absorber` de las políticas duras (182-196 conteos) se reparte hacia `informalizar`,
  `bajar_horas` y `despedir`.
- **Dueño:** Manuel (R2, `engine/veto.py`) · **Costo:** ~40 min + re-correr el barrido.

#### A2 · Quien no puede pagar nada, se queda como está

- **Hoy:** si a un agente le vetan 3 propuestas seguidas, la jugada terminal es `cumplir`
  — o sea, **formalizarse gratis justo después de demostrar que no tiene plata**.
- **Se cambia:** la jugada terminal pasa a ser *"la primera opción que sí sea factible"*, y
  si ninguna lo es, **quedarse exactamente como estaba** (sin cambiar su estatus de regla).
- **Ojo con la honestidad:** en la corrida medida los fallbacks son **0**, así que esto
  **no es hoy la causa del signo invertido** — es el seguro que hace falta *después* de A1,
  porque A1 va a multiplicar los vetos y sin esto el fallback se vuelve la nueva fuga.
- **Requiere ADR:** `docs/IDEA.md` §5.3 y §5.7 fijan `cumplir` como terminal. Se propone
  **ADR 0010** antes de tocar una línea.
- **Cómo lo vas a ver:** la línea `fallbacks a 'cumplir': N` del terminal se queda cerca de
  0 aun con A1 puesto. Si sube por encima del 5% de las decisiones, la corrida lo dice y
  eso es un hallazgo publicable, no algo que se esconde.
- **Dueño:** Nico (R3, `behavior/contrato.py`) + ADR con Manuel · **Costo:** ~20 min.

#### A3 · El jugador y el árbitro miran la misma billetera

- **Hoy:** al agente se le dice *"margen **mensual** disponible: X u"*, el árbitro juzga
  con **3 meses** de ese margen (`caja_de_la_ronda = flujo_caja × 3`) y la regla fija de
  la ablación compara contra **1 mes**. Tres lugares, dos unidades.
- **Se cambia:** una sola unidad, la del reloj del proyecto (una ronda = un trimestre).
  El prompt dice *"caja disponible en este periodo"* y es la misma cifra que usa el veto.
- **Cómo lo vas a ver:** menos vetos absurdos por indemnización, y las justificaciones que
  escribe la IA dejan de contradecir al árbitro. En el feed de decisiones, las frases del
  tipo *"no me alcanza para indemnizar"* van a coincidir con lo que el árbitro respondió.
- **Dueño:** Nico (R3, `behavior/prompts/arquetipo.md` + `capa.py` + `ablacion.py`).
  **Costo:** ~15 min. **Invalida la caché** (cambia el prompt).

#### A4 · Bajar horas deja de ser una etiqueta y mueve un número

- **Hoy:** de las 8 estrategias, solo 3 mueven algo. `bajar_horas` se registra y se bota.
- **Se cambia:** `reduccion_horas_pct` baja proporcionalmente el costo formal de la planta
  **y el ingreso del trabajador**. Es la válvula de escape intermedia entre "cumplo" e
  "informalizo".
- **Por qué importa justo ahora:** con A1 puesto, "me aguanto" deja de ser gratis y todos
  los agentes necesitan a dónde ir. Sin esta válvula, el modelo se va a saturar hacia
  informalidad 100% y va a mentir por el otro lado.
- **Cómo lo vas a ver:** aparece una **cuarta cifra** en la salida, además de informalidad,
  empleo y sanción: *"trabajadores que conservan el empleo pero pierden X% de ingreso"*.
  Es material nuevo para el mapa distributivo (dato A3) y es un resultado que el modelo
  oficial tampoco ve.
- **Dueño:** Nico (R3, `behavior/contrato.py` + `rondas.py`) · **Costo:** ~30 min.

#### A5 · La regla de corte se declara antes de correr

- **Hoy:** se reporta la ronda 3, y 7 de 9 políticas se devuelven ahí. El número final
  depende de dónde cortemos y ese corte no tiene justificación medida.
- **Se cambia:** regla escrita **antes** de ver el resultado: *se reporta la ronda 3, y si
  el movimiento de la última ronda supera 2 pp, la corrida se marca **"no estabilizada"** y
  el número sale con esa etiqueta pegada, en el terminal y en la pantalla.*
- **Cómo lo vas a ver:** una línea nueva al final: `movimiento de la última ronda: +0,4 pp
  · estabilizada`. En la interfaz, un sello visible cuando no lo esté.
- **Dueño:** Juanda (R5) declara la regla · Nico la imprime · Dani la dibuja.
  **Costo:** ~15 min.

### Bloque B — Que el número deje de temblar *(el ruido)*

#### B1 · Se le pregunta más veces a quien más pesa 🔴

- **Hoy:** cada corrida del barrido usa **una sola** forma de la pregunta. Con la
  población concentrada como está (unos pocos arquetipos cargan casi todo el peso), el
  número final termina decidido por un puñado de lanzamientos de moneda. De ahí el
  22,5 pp de dispersión entre repeticiones de la **misma** política.
- **Se cambia:** dos cosas.
  1. El número que se publica sale de **≥5 paráfrasis promediadas dentro de cada ronda**
     (el código ya sabe hacerlo: `n_parafrasis`). Promediar 5 sorteos en vez de 1 baja el
     temblor por un factor de ~√5.
  2. **El presupuesto de preguntas se reparte por peso**: al arquetipo que representa al
     8% de Bogotá se le pregunta 9 veces; al que representa al 0,3%, 3 veces. Misma plata,
     mucho menos temblor, porque se gasta donde de verdad mueve el agregado.
- **Cómo lo vas a ver:** corres la misma política dos veces y **el número final se repite
  dentro de ±5 pp** en vez de saltar 28,8 pp como hoy (60,9% / 56,4% / 85,2% en la
  política del 9%). Es la diferencia entre un resultado y una anécdota.
- **Dueño:** Nico (R3, `behavior/rondas.py` + `cliente.parafrasis`) · **Costo:** ~40 min y
  ~US$7 de LLM.

#### B2 · La banda deja de mentir hacia abajo

- **Hoy:** la banda `p10/p90` mide la dispersión de **una ronda** partiendo todas del mismo
  estado. El propio código lo declara. Da 0,0 pp cuando hay una sola paráfrasis, mientras
  la dispersión real entre trayectorias independientes es de 22,5 pp.
- **Se cambia:** la banda que se publica es la de **N trayectorias completas e
  independientes** (lo que ya hace el arnés del barrido). La banda intra-ronda se conserva
  con otro nombre, como diagnóstico interno.
- **Cómo lo vas a ver:** la banda de la pantalla **se ensancha** — y eso es la corrección,
  no un empeoramiento. Hoy publicaríamos una banda falsamente angosta, que es la forma más
  rápida de perder credibilidad en el Q&A.
- **Dueño:** Nico (R3) + Juanda (R5) · **Costo:** ~30 min, $0 extra (usa las corridas de B1).

#### B3 · El barrido entra al repo

- **Hoy:** `scripts/barrido_politicas.py` **no existe en `main`** — solo su log y su JSON de
  salida. La medición que sostiene todo `DEFECTOS.md` no es reproducible por nadie más.
- **Se cambia:** el script entra a `scripts/`, con su salida versionada, y `make validate`
  lo consume.
- **Cómo lo vas a ver:** `make validate` deja de imprimir "PENDIENTE" y empieza a imprimir
  EL número, con su banda y con el ruido/señal medido al lado.
- **Dueño:** Juanda (R5) · **Costo:** ~20 min.

#### B4 · El experimento que le da el número al pitch: apagar la cascada

- **Hoy:** decimos *"la cascada existe"* (p(sanción) cae de 6,33% a 2,3-3,5% en 9 de 9
  políticas). Cierto, pero no está cuantificado: no sabemos **cuánto de la brecha es la
  cascada** y cuánto es el efecto directo del alza.
- **Se agrega:** la misma corrida con **p(sanción) congelada** en su valor de la ronda 0.
  La diferencia entre las dos curvas **es** la cascada, en puntos porcentuales.
- **Cómo lo vas a ver:** una segunda línea en la gráfica y una frase para el pitch del
  tipo *"de los +33 pp de brecha, +X pp los pone el alza y +Y pp los pone el hecho de que
  la fiscalización no crece"*. Ese Y es el aporte del proyecto, medido, no afirmado.
- **Dueño:** Nico (R3) + Juanda (R5) · **Costo:** ~20 min y ~US$2.

### Bloque C — Que el número sea trazable

#### C1 · La empresa deja de inventarse 🔴

- **Hoy:** `behavior/arquetipos.py` se fabrica el empleador: caja = 18% de la nómina,
  indemnización = 1,5 salarios, factor prestacional **promediado** en 1,40 para toda la
  población. Mientras tanto **`data/empresas.parquet` ya existe** y trae, celda por celda:
  el factor prestacional real (1,3835-1,5829 según sector × exoneración del Art. 114-1),
  el costo formal con auxilio de transporte, la indemnización según el CST, cuántas
  empresas reales representa y qué fracción de su planta es formal.
- **Se cambia:** `behavior/` **consume esa tabla** en vez de re-derivar la suya.
- **Qué defectos mata de un golpe:** §3.3 (el factor promediado, que decide el signo del
  candado 4), §3.4 (las dos particiones incompatibles, 67 vs 101), y dos números mágicos.
- **Y un hallazgo que no estaba en la lista:** un tercio de los ocupados de Bogotá son
  **cuenta propia y no tienen empleados**. Hoy el simulador les pregunta a cuántos
  empleados despiden. `empresas.parquet` ya los separa.
- **Cómo lo vas a ver:** el mapa distributivo deja de ser plano. Hoy toda Bogotá tiene el
  mismo costo de formalidad; después, el micro-empleador de un solo trabajador —que no
  está exonerado y paga 13,5 puntos más, y donde vive el **66,7%** de la informalidad—
  aparece separado del que sí está exonerado. **La celda que más duele se vuelve visible.**
- **Dueño:** Nico (R3) con Alejo (R1) · **Costo:** ~1 h. **Invalida la caché.**

#### C2 · La fiscalización sale de la fuente, no de un 0,02 🔴

- **Hoy:** `behavior/rondas.py` tiene su propia copia de la fórmula de sanción y una
  capacidad de **0,02** sin fuente, que equivale a **83.993 inspecciones por trimestre**.
  `engine/fiscalizacion.py` deriva la suya de la cifra de la OIT —1.300 inspectores— y da
  **3.900**. Además la capa cuenta *personas* y el motor cuenta *empresas*.
  Y `behavior/demo.py` sigue usando el **veto de juguete**, no el veto real (§3.1); toda
  corrida hecha hasta hoy usó el doble de prueba.
- **Se cambia:** `behavior/` importa `engine/` — el veto real, la fórmula real y la
  semilla real — y el universo sale del conteo de empresas de `data/empresas.parquet`.
- **Qué defectos mata:** §3.1, §3.2, §3.5 y el número mágico, todos con el mismo import.
- **Cómo lo vas a ver:** la columna `p.sanción` **baja de golpe** (arrancaba en 6,3%). Y eso
  hace la informalidad **más atractiva**, o sea que empuja el resultado en la dirección
  correcta por una razón con fuente, no por un ajuste. La cascada se ve más pronunciada
  y cada número de esa columna es defendible con una cita de la OIT.
- **Dueño:** Nico (R3) con Manuel (R2) · **Costo:** ~40 min. **Invalida la caché.**

#### C3 · La decisión de subir precios deja de botarse

- **Hoy:** `subir_precios` es el único canal por el que un alza salarial llega a los
  precios. Los agentes **lo eligen** (1,4% de la población) y el agregado **lo bota**.
  `VALIDATION.md` dice que la inflación es "exógena observada" — pero eso describe una
  decisión de alcance, y lo que pasa en el código es otra cosa: la decisión se toma y se
  pierde.
- **Se cambia:** se agrega al agregado de la ronda un `traslado_precios_pct` = el promedio
  ponderado del alza de precios que las firmas **declararon**. Se publica con su nombre
  honesto: *traslado declarado por las firmas*, **no** un pronóstico de inflación (no hay
  respuesta de demanda; ver Bloque D).
- **Cómo lo vas a ver:** una cifra nueva por ronda. A la pregunta *"¿y esto cuánta
  inflación genera?"* hoy no se puede responder ni de lejos; después se responde *"las
  firmas que representan al Z% de Bogotá declaran trasladar en promedio W%, y eso es lo
  que dijeron, no lo que va a pasar"*. Esa respuesta gana el Q&A; "no lo modelamos" no.
- **Ojo con el contrato:** `contracts/ronda.json` está congelado desde H+4. Este campo
  **se avisa en el grupo antes**, junto con el `banda.degenerada` que ya se coló (§4.4).
- **Dueño:** Nico (R3) con Manuel (R2) y Dani (R4) · **Costo:** ~30 min.

#### C4 · Que un extraño pueda correrlo

- **Hoy:** la caché **no está versionada** (`git ls-files | grep .cache/` → 0 archivos), y
  la línea del `.gitignore` que pretende ignorarla (`behavior/cache/`) **apunta a una ruta
  que no existe**: la caché real vive en `behavior/.cache` y la ignora otro archivo,
  `behavior/.gitignore`. Y **no hay `requirements.txt` en ninguna rama**. Un jurado que
  clone el repo sin API key recibe `SinCredenciales` y no puede correr nada.
- **Se cambia:** se exporta la caché del escenario demo a un archivo versionado
  (`Cache().exportar(...)` ya existe), `make reproduce` la importa, se corrige la línea
  muerta del `.gitignore`, y entra el `requirements.txt` que ya está escrito y verificado.
- **Cómo lo vas a ver:** `make reproduce` en una máquina limpia, **sin API key**, imprime
  exactamente los mismos números que en la tuya. Eso es la promesa de determinismo del
  proyecto pasando de afirmación a hecho verificable.
- **Dueño:** Nico (R3) la caché, Juanda (R5) el `requirements.txt` · **Costo:** ~30 min.

#### C5 · El repo deja de contradecirse

Cinco arreglos de texto, todos con su línea:

| Qué | Dónde | Arreglo |
|---|---|---|
| El README cita una función que no existe (`Politica.como_mecanica()`) | `README.md:41` | nombrar la guardia real: `behavior/higiene.py`, que sí es fail-closed en cada llamada |
| La informalidad de referencia se contradice: ~55-60% vs 30,57% | `VALIDATION.md:32` vs `momentos.json` | decir que son universos y definiciones distintas (DANE/OIT nacional vs Bogotá con proxy de cotización) y fijar **30,57% de Bogotá** como objetivo del candado 1 |
| El "informe de honestidad" da 54 o 94 según quién lo corra | `Makefile:82` vs `VALIDATION.md:80` | un solo comando, publicado en los dos lados |
| El contrato congelado emite un campo que no declara (`banda.degenerada`) | `contracts/ronda.json` | declararlo, en el mismo aviso al grupo que C3 |
| Los 4 campos de la página de votación están vacíos | `platanus-hack-project.jsonc` | llenarlos — **es bloqueante de entrega, no es cosmético** |

- **Dueño:** Juanda (R5) · **Costo:** ~30 min · **Cómo lo vas a ver:** nada en la corrida.
  Se ve cuando un juez abre el repo y **todo lo que dice se puede verificar**. Es la regla
  dura de R5 y hoy está incumplida en cinco puntos.

#### C6 · Candado 3(b): el test de re-skinning *(si alcanza el tiempo)*

- **Hoy:** `VALIDATION.md:47` lo promete y **no hay una línea de código**. La higiene filtra
  *términos*, no *magnitudes*: los montos viajan en pesos reales y la moda del parquet es
  1.750.000, que es el mínimo de 2026. Un modelo puede reconocer el escenario por los
  números aunque nunca vea el nombre.
- **Se cambia:** una bandera `--reskin` que renombra los sectores a etiquetas inventadas y
  **reescala todos los montos** por un factor arbitrario. Como el modelo solo ve "u", el
  agregado debería no moverse.
- **Cómo lo vas a ver:** dos corridas, dos números. Si coinciden, el candado 3 cierra
  completo y es un argumento fuerte del pitch. Si no coinciden, **hubo memorización y lo
  reportamos nosotros antes de que lo pregunten**.
- **Dueño:** Nico (R3) · **Costo:** ~40 min y ~US$2.

---

## 3 · Los criterios de éxito de una buena simulación

La vara. Cada corrección existe para mover una de estas filas, y ninguna otra razón.

| # | Criterio | Cómo se mide | Hoy | Meta | Lo cubre |
|---|---|---|---|---|---|
| 1 | **Reproducible por un extraño** | `make reproduce` en máquina limpia sin API key | imposible | idéntico al bit | C4, B3 |
| 2 | **Señal > ruido** | ruido/señal = dispersión dentro de una política ÷ rango entre políticas | **0,71** | **≤ 0,25** | B1, B2 |
| 3 | **Signo correcto donde hay literatura** | correlación alza → informalidad en el tramo 5-11% | **−0,311** | **positiva** | A1, A2, C2 |
| 4 | **Magnitud del mismo orden que la literatura** | Banrep WP 1104: +1 pp de Kaitz ≈ +0,21 pp de informalidad. Con Kaitz ≈ 87,5% (1.750.905 / 2.000.000), un alza del 10% ≈ +8,8 pp de Kaitz ≈ **+1,8 pp esperados** | +28 a +33 pp (≈15×) | dentro de un factor ~3 **en el tramo bajo**; el exceso del tramo alto debe explicarse por la cascada, no por el nivel | A1, C1, C2, B4 |
| 5 | **Dosis-respuesta monótona** | ¿alza mayor produce alguna vez menos incumplimiento? | 7 de 9 se devuelven en r3 | monótona, salvo mecanismo declarado | A1, A2, A4 |
| 6 | **Un solo estado del mundo** | ¿el árbitro y el jugador usan los mismos números, unidades y reglas? | 3 divergencias (veto de juguete, p(E) duplicada, caja mensual vs trimestral) | 0 | A3, C1, C2 |
| 7 | **Bandas honestas** | ¿la banda cubre la dispersión entre trayectorias independientes? | 0,0 pp publicada vs 22,5 pp real | cobertura real | B2 |
| 8 | **Trazabilidad de cada número** | ¿cada parámetro tiene fuente, o `# SUPUESTO:` **con barrido**? | 0,02 y 0,18 y 1,5 sin fuente ni barrido | todos con fuente o con barrido publicado | C1, C2, C5 |
| 9 | **Límites declarados con dirección del sesgo** | no basta decir "no lo modelamos": hay que decir **hacia dónde** empuja la omisión | parcial | completo | Bloque D |
| 10 | **Corte declarado antes de correr** | ¿la regla de reporte se fijó antes de ver el número? | no | sí, en este documento | A5 |

El criterio 4 es el que más duele y el que más vale. Es literalmente lo que ya dice
`VALIDATION.md:35`: *"reproducir la recta en el tramo bajo es lo que nos da derecho a
hablar del codo en el tramo alto"*. Hoy no reproducimos ni el signo de la recta.

---

## 4 · Cómo lo vas a ver reflejado

### 4.1 · En el terminal, corriendo la simulación

Esto es lo que imprime hoy la política del 20% (medido, `DEFECTOS.md` §1.6):

```
ronda  informalidad  p.sanción   empleo   estrategia dominante
    0        30.6%      6.3%     100.0%   -
    1        51.0%      6.3%     100.0%   informalizar
    2        85.7%      3.8%      98.2%   informalizar
    3        84.4%      3.1%      91.7%   informalizar     <- se devolvió
```
…y la misma política corrida otra vez puede dar **56,4%** o **85,2%**.

Esto es lo que **debe** imprimir si el plan funciona (y si no lo hace, se reporta que no):

```
ronda  informalidad  p.sanción   empleo   horas-  precios  estrategia dominante
    0        30.6%      2.1%     100.0%    0.0%     0.0%   -
    1        4X.X%      1.X%      9X.X%    X.X%     X.X%   informalizar
    2        5X.X%      1.X%      9X.X%    X.X%     X.X%   informalizar
    3        5X.X%      1.X%      9X.X%    X.X%     X.X%   informalizar

movimiento de la última ronda: +0.X pp · ESTABILIZADA
banda entre 5 trayectorias independientes: p10 5X.X% / p90 5X.X%
de la brecha total, la cascada aporta +X.X pp  (contra la corrida con p congelada)
fallbacks: 0.X% de las decisiones · propuestas vetadas: N
```

Las cinco diferencias que vas a poder señalar con el dedo:

1. **La curva no se devuelve.** Sube y se queda. (A1, A2)
2. **Correr dos veces da casi lo mismo.** ±5 pp en vez de ±29 pp. (B1)
3. **Subir la política sube el incumplimiento.** El barrido de 5% a 20% deja de ir al
   revés. (A1)
4. **Hay columnas nuevas** que hoy no existen: horas perdidas y traslado a precios.
   Decisiones que los agentes ya tomaban y que el agregado botaba. (A4, C3)
5. **Cada número trae su etiqueta**: estabilizada o no, banda real, cuánto puso la cascada.

### 4.2 · En la pantalla — lo que te toca a ti, Dani (`web/`)

Ninguna corrección del Bloque A, B o C toca tu carpeta. Lo tuyo es que la pantalla **no
prometa más de lo que el motor entrega**:

- **Nunca decir "desempleo".** El modelo **no puede** calcularlo: `momentos.json` solo trae
  ocupados, no hay fuerza laboral ni desocupados (§1.3). Lo que existe es *empleo relativo
  a la línea base*: "se pierde el 8,3% del empleo base" es verdad; "el desempleo sube a
  X%" es sobreventa. Una lámina con esa palabra es un regalo para el juez que quiera
  hundirnos.
- **La banda se dibuja siempre**, y ahora es más ancha (B2). Ningún número sin banda.
- **El sello "no estabilizada"** cuando el movimiento de la última ronda supere 2 pp (A5).
- **La celda que más duele, visible**: con C1 el micro-empleador no exonerado —13,5 puntos
  más de carga, 66,7% de la informalidad de Bogotá— se puede pintar aparte. Es la mejor
  historia que va a tener el mapa distributivo.
- **La cascada como la pieza principal**: con B4 puedes dibujar las dos curvas, con y sin
  cascada. El área entre ellas es literalmente lo que el modelo oficial no ve. Es la
  imagen del pitch.
- **El traslado a precios** (C3) como cifra secundaria, con su nombre honesto.

---

## 5 · El orden y el reloj

Estamos en ~H+16. Feature freeze en H+28. **Regla de costo que no se negocia:** todo cambio
que toque el prompt invalida la caché entera, así que **A3 + B1 + C1 + C2 se agrupan en un
solo PR y el barrido se corre UNA vez**. Correrlo por partes multiplica la plata por cuatro.

| Bloque | Qué | Dueño | Tiempo | LLM |
|---|---|---|---|---|
| 1 | ADR 0010 (fallback) + A1 + A2 | Manuel + Nico | 1 h | $0 |
| 2 | A3 + A4 + C1 + C2 — **un solo PR**, sin correr todavía | Nico + Alejo | 2 h | $0 |
| 3 | B1 + B2 + A5 y **el barrido único** | Nico + Juanda | 1 h | ~$8 |
| 4 | B4 (cascada apagada) + C3 | Nico | 40 min | ~$2 |
| 5 | C4 + C5 + B3 — entrega y reproducibilidad | Juanda | 1 h | $0 |
| 6 | C6 re-skinning, **si sobra tiempo** | Nico | 40 min | ~$2 |

**Si solo alcanza para tres horas**, en este orden y sin discusión:

1. **A1** — sin esto el número central del proyecto tiene el signo al revés.
2. **C2** — una línea de import mata cuatro defectos y quita el número mágico.
3. **B1** — sin esto ningún número es defendible, ni siquiera el correcto.
4. **C4 + los 4 campos de votación de C5** — son **bloqueantes de entrega**, no mejoras.

Todo lo demás puede quedar declarado en `VALIDATION.md` sin que nadie pierda credibilidad.
Lo que **no** se puede hacer es presentar el número con el signo invertido y sin banda real.

---

## 6 · Anexo técnico — los cambios exactos

### A1 · `engine/veto.py`

```python
# 1. El Protocol `Firma` necesita el ingreso para poder costear cumplir/absorber.
class Firma(Protocol):
    id: str
    n_trabajadores: int
    flujo_caja: float
    costo_despido: float
    formal: bool
    ingreso_por_trabajador: float   # NUEVO — `Arquetipo` ya lo tiene

# 2. Dos razones nuevas en `_RAZONES`, con el mismo formato que `despido_sin_caja`
#    (montos por `_plata()`, o sea con puntos de miles: la higiene rechaza 4 dígitos
#    seguidos y `razon` viaja hacia el modelo en el reintento).
"formalizacion_sin_caja": (
    "no alcanza para poner en regla a {pedidos}: cuesta {costo} en el periodo "
    "y la caja del periodo es {caja}"
),
"absorcion_sin_caja": (
    "el sobrecosto del periodo es {costo} y la caja del periodo es {caja}: "
    "no se puede pagar con el margen"
),

# 3. En `vetar()`, después del bloque 3 (informalización), un bloque 4 nuevo.
#    Requiere el aumento de la política: `vetar(decision, firma, estado, aumento_pct)`
#    — o, más limpio, que `veto_del_motor(estado, aumento_pct)` lo cierre adentro,
#    que es como ya se le pasa el estado.
fam = familia(decision["estrategia_propuesta"])          # de behavior/contrato.py,
                                                          # o se duplica la tabla en engine/
caja = caja_de_la_ronda(firma)                            # flujo_caja * 3
if fam == "cumplir":
    fuera_de_regla = empleados - en_regla
    costo = fuera_de_regla * firma.ingreso_por_trabajador * factor * MESES_POR_RONDA
    if costo > caja: return _infactible("formalizacion_sin_caja", ...)
if fam in ("cumplir", "absorber"):
    sobrecosto = en_regla * firma.ingreso_por_trabajador * factor * (aumento_pct/100) * MESES_POR_RONDA
    if sobrecosto > caja: return _infactible("absorcion_sin_caja", ...)
```

`factor` es el factor prestacional **de la firma**, que llega con C1. Antes de C1, usar el
1,40 de `ablacion.FACTOR_PRESTACIONAL` y marcarlo `# SUPUESTO:`.

**Tests obligatorios**, en `engine/test_veto.py` (parte de los 44 tests de `engine/`):
factible justo debajo del umbral, infactible justo encima, y **que las dos razones nuevas
pasen `higiene.verificar()`** — el test ya existe para las razones viejas
(`test_todas_las_razones_declaradas_pasan_la_higiene:64`), solo hay que extender
`razones_posibles()` con las dos nuevas y se cubre solo.

**Aritmética que este cambio implica** (dejarla escrita para poder falsarla):
con `flujo_caja = 0,18 × nómina` y `factor ≈ 1,40`, absorber deja de ser factible por
encima de **aumento ≈ 0,18 / 1,40 ≈ 12,9%**, y formalizarse **nunca** es factible para una
unidad informal (cuesta 0,40-0,58 × nómina contra 0,18 de caja). Por eso el codo debería
aparecer cerca del 13% — **y por eso mismo su posición depende de un parámetro sin fuente
(el 0,18)**. Ver Bloque D.

### A2 · `behavior/contrato.py` + ADR 0010

```python
# `FALLBACK = "cumplir"` deja de ser una constante y pasa a ser una función del veto:
def decision_fallback(agente_id, ronda, razones, *, veto, arquetipo, fraccion_previa):
    """Primera opción factible del orden canónico; si ninguna, quedarse igual."""
    for candidata in ("cumplir", "bajar_horas", "absorber"):
        if veto({... candidata ...}, arquetipo)["factible"]:
            return _decision(candidata, fue_fallback=True)
    return _decision("absorber", fue_fallback=True, sin_salida=True)
```

`sin_salida=True` se cuenta y se imprime: *"N% de las decisiones no tuvo ninguna opción
factible"* es un resultado del modelo, no un error.

### A3 · la caja, en un solo lenguaje

- `behavior/prompts/arquetipo.md`: `Margen mensual disponible (flujo de caja libre)` →
  `Caja disponible en este periodo`.
- `behavior/capa.py:renderizar()`: pasar `arquetipo.flujo_caja * MESES_POR_RONDA`.
- `behavior/ablacion.py:96,112`: comparar contra la caja del **periodo**, no la mensual.
- Importar `MESES_POR_RONDA` de `engine/veto.py`, no redefinirlo.

### A4 · `bajar_horas` con efecto

- `behavior/contrato.py`: `reduccion_horas_pct` reduce el costo formal de la planta y el
  ingreso del trabajador en la misma proporción; **no** cambia el estatus de regla.
- `behavior/rondas.py`: estado vivo nuevo `horas[a.id]` (arranca en 1,0, acumulativo, como
  `empleo`), y una métrica agregada `ingreso_laboral_relativo`.
- El veto ya acota `reduccion_horas_pct` a [0,100]: no hay que tocarlo.

### C1 · `behavior/arquetipos.py` → `data/empresas.parquet`

`desde_poblacion()` se reemplaza por `desde_empresas("data/empresas.parquet")`. Mapeo:

| Campo del `Arquetipo` | Hoy (inventado) | Después (columna de `empresas.parquet`) |
|---|---|---|
| `n_trabajadores` | `EMPLEADOS_POR_CODIGO` (incluye al dueño) | `n_empleados` (lo excluye) |
| `ingreso_por_trabajador` | mediana simple | `salario_mediano_cop` (mediana **ponderada**) |
| `flujo_caja` | `ingreso × n × 0,18` | `flujo_caja_mensual_cop` |
| `costo_despido` | `ingreso × 1,5` | `costo_despido_por_empleado_cop` (CST) |
| `formal` (booleano) | binario del corte | `share_formal` → **fracción inicial continua**, que es lo que `rondas.frac_informal` ya maneja |
| `factor_prestacional` | 1,40 promedio | `factor_prestacional` (1,3835-1,5829) — **campo nuevo del dataclass** |
| `peso` | suma de expansión | `trabajadores_expandidos` |
| universo de firmas | no existe | `n_empresas_expandidas` → alimenta C2 |

Cuenta propia (código 1, sin nómina) queda **fuera** de la grilla de empleadores, como ya
lo hace `construir_empresas.py`, y se reporta aparte con su peso.

Que este mapeo es el que `data/` esperaba no es interpretación mía: `parametros_legales.json`
lo dice en su propia nota sobre la indemnización — *"reemplaza el coeficiente de andamio
`ingreso * 1.5` de `behavior/arquetipos.py`, que no tenía fuente"*. El dato ya está en el
repo esperando que alguien lo consuma.

### C2 · `behavior/` importa `engine/`

```python
# behavior/rondas.py — se BORRA `_prob_fiscalizacion` y se usa el motor:
from engine.fiscalizacion import EstadoFiscalizacion
from engine.veto import EstadoVivo, veto_del_motor
from engine.seed import stream_nombrado

fisc = EstadoFiscalizacion(universo=n_empresas_expandidas)   # de C1
prob = fisc.prob(tasa)                                        # p(E) = 1 − exp(−C/max(E,1))
```

- Se elimina el parámetro `capacidad_fiscalizacion=0.02` de `correr()`.
- Se elimina la divergencia del borde de §3.5 (`return 1.0` vs `max(E,1)`): queda una sola
  implementación, la del motor, que es la que ya tiene el argumento escrito.
- `behavior/demo.py:179`: `veto=veto_doble_prueba` → `veto=veto_del_motor(estado)`.
  **`veto_doble_prueba` se borra**, no se deja de adorno: mientras exista, alguien la va a
  volver a pasar.
- `engine/seed.py` deja de ser decorativo: la semilla del muestreo sale de ahí.

### C3 · traslado a precios

- `behavior/rondas.py`: `traslado_precios = Σ pesoᵢ × aumento_precios_pctᵢ / Σ pesoᵢ`,
  sobre las decisiones de familia `subir_precios` (0 para el resto).
- Campo nuevo en `Ronda.a_contrato()` **y** en `contracts/ronda.json`, junto con
  `banda.degenerada` (§4.4). **Aviso al grupo antes de tocar el contrato.**

### C4 · caché y entorno

```bash
python3 -c "from behavior.cache import Cache; print(Cache().exportar('behavior/cache-demo.json'))"
git add -f behavior/cache-demo.json
```
- `.gitignore:23`: `behavior/cache/` → `behavior/.cache/` (la ruta real; hoy la línea es
  inerte y quien intente versionar la caché va a editar la línea equivocada).
- `make reproduce` hace `Cache().importar('behavior/cache-demo.json')` antes de correr.
- `requirements.txt` a la raíz (ya escrito y verificado en venv limpio, sin commitear).

### C5 · los cinco arreglos de texto

Están en la tabla de la sección 2, cada uno con archivo y línea. No hay nada que diseñar.

### C6 · re-skinning

`behavior/capa.py:renderizar()` acepta `reskin: Reskin | None`; `Reskin` mapea sectores a
etiquetas inventadas y multiplica **todos** los montos por un factor arbitrario. Como todo
va en "u", el agregado no debería moverse. La comparación se publica en `VALIDATION.md`
candado 3(b) salga como salga.

---

## 7 · Riesgos de estas correcciones

Escritos antes de correr, para que no parezcan excusas después.

1. **A1 puede pasarse de largo y saturar la informalidad en ~100%.** Si absorber y cumplir
   se vuelven infactibles para todos, el único camino que mueve el número es informalizar.
   **Mitigación:** A4 (bajar horas) abre la válvula intermedia. **Cómo lo sabremos:** si el
   desglose final queda con `informalizar` por encima del 90% de la población en el tramo
   alto, nos pasamos, y hay que revisar el 0,18 antes que el veto.
2. **La posición del codo la fija un parámetro sin fuente.** El 12,9% sale del 0,18 de
   margen sobre nómina, que `construir_empresas.py` declara explícitamente como supuesto
   heredado del andamio, con rango de barrido 0,05-0,40. **Entonces se reporta así: lo que
   el modelo dice es que existe un codo donde el margen libre se agota; DÓNDE cae depende
   de un parámetro que no observamos, y por eso va con barrido, no con una cifra.**
3. **"Ustedes tocaron el veto hasta que el signo se volteó."** Es la pregunta que va a
   hacer un juez, y es justa. La defensa tiene que ser estructural, no retórica: el cambio
   **aplica a las cuatro estrategias el criterio que el modelo ya le declara al agente en
   el prompt del sistema** (*"no puedes gastar plata que no tienes"*), y estaba escrito
   —con la aritmética y el número esperado— **antes** de correrlo, en este documento
   fechado. Por eso existe la sección 4.1 con el "debe imprimir".
4. **Presupuesto.** Cada cambio de prompt tira la caché. El plan agrupa todo en una sola
   corrida (~US$10 de los US$50 por persona); ejecutarlo por partes cuesta cuatro veces
   más y no hay tiempo para dos barridos.
5. **C1 cambia la grilla de arquetipos**, así que cambia el número de llamadas y el costo
   de la corrida. Se estima con la grilla nueva antes de lanzar, no después.

---

## 8 · Bloque D — Lo que NO se arregla, y se declara

Va a `VALIDATION.md` § *"Dónde NO hay que creerle"*. **No basta con decir "no lo
modelamos": hay que decir hacia dónde empuja la omisión.** Eso convierte una debilidad en
un dato sobre nuestro propio resultado.

| Lo que falta | Por qué no se agrega | **Hacia dónde sesga el resultado** |
|---|---|---|
| Productividad, demanda, capital, salario de eficiencia (§1.4) | Son piezas nuevas, no campos apagados. Cero menciones en todo el código: el canal *"sube el mínimo → sube la productividad → baja el desempleo"* **no puede emerger** | Sin canales positivos, nuestra informalidad es una **cota superior** y nuestro empleo una **cota inferior** |
| Tasa de desempleo (§1.3) | `momentos.json` solo trae ocupados: no hay fuerza laboral ni desocupados | No se reporta en ninguna forma. Solo *empleo relativo a la línea base* |
| Efecto faro sobre salarios informales | El alza solo encarece el lado formal; los salarios informales cercanos al piso no suben | **Sobreestima la informalización**: en la realidad el costo informal también sube |
| Convergencia a equilibrio | Son 3 rondas de mejor respuesta, decisión D5 | Se reporta como dinámica, nunca como Nash. Con A5, además con la etiqueta de si se estabilizó |
| El despido como cálculo y no como muro (§1.5) | El agente propone y el motor veta; nunca compara "despedir vs. mantener" por costo | Con A3 al menos ve la caja correcta. El mecanismo sigue siendo restricción, y así se dice |
| El costo de la fiscalización sobre el Estado | Fuera de alcance | Ninguno sobre las cifras publicadas |

---

## 9 · La corrida de aceptación

Un solo comando decide si el plan funcionó. Se corre **una vez**, con todo puesto, y su
salida se publica salga como salga:

```bash
make validate     # barrido 5-20%, 5 trayectorias, banda entre trayectorias, cascada apagada
```

Se acepta si, y solo si:

- [ ] **ruido/señal ≤ 0,25** (hoy 0,71) — criterio 2
- [ ] **correlación alza → informalidad positiva** en el tramo 5-11% (hoy −0,311) — criterio 3
- [ ] **ninguna política se devuelve** más de 2 pp en la ronda 3, o sale etiquetada — criterio 5
- [ ] **`make reproduce` en máquina limpia sin API key** da el mismo número — criterio 1
- [ ] **el aporte de la cascada está cuantificado en pp**, no afirmado — B4
- [ ] **la tabla del Bloque D está escrita** con la dirección del sesgo de cada omisión — criterio 9

Si alguna casilla queda sin marcar, **se publica sin marcar**. Un candado que no cerró y se
reporta vale más que un número que nadie puede refutar. Esa regla ya está escrita en
`VALIDATION.md:4` y este plan no la cambia.
