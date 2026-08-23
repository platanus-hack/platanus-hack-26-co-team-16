# Handoff — Manuel · R2 · Backend

> **Tu memoria entre sesiones.** Léelo al abrir tu sesión de agente, actualízalo antes de cerrarla.
> Este archivo es solo tuyo: nadie más lo edita, así nunca da conflicto de merge.
> Tus carpetas: `engine/`, `api/` · Tu rama: `rol/backend`
> Tu misión, entregables y prompt de arranque: [`docs/ROLES.md`](../ROLES.md)

## Dónde quedé

_Lo más reciente arriba._

- **2026-08-23 (sesión del track de backend) — los 3 puntos del track cerrados: `rondas_totales`,
  la perilla del seed y la banda entre trayectorias. Rama `rol/backend`, commits `9167811` y `8b39b4d`.**

  **S2-9 · `rondas_totales` con fuente única.** Había dos fuentes que cuadraban por casualidad
  (el literal `4` de `serializar.evento_poblacion` y el default de `behavior.rondas.correr`, al que
  la API nunca le pasaba nada) más un tercer default en el front (`?? 4`). Ahora `RONDAS_TOTALES`
  se declara una vez en `api/servidor.py`, donde ya viven los demás parámetros de la corrida, y
  alimenta los dos lados. `evento_poblacion` lo recibe **keyword-only**: el literal ya no puede
  volver por construcción, no por disciplina.
  *Verificado moviendo la constante y contando las rondas que el motor emite:* `=4` → el evento
  dice 4 y el motor corre `[0,1,2,3]`; `=3` → dice 3 y corre `[0,1,2]`. Antes el evento decía 4
  pasara lo que pasara. No le escribí test: un test que compara dos números que ahora salen del
  mismo lugar no puede fallar nunca.

  **S1-4 · la perilla del seed, rotulada y no quitada.** Medido antes de afirmar nada:
  `modo=reglas`, seed 42 contra 99, las 4 rondas comparadas campo por campo quitando la etiqueta →
  **trayectorias idénticas, 31,01% en las dos**. Y en el camino del LLM es estructural, más fuerte
  que la medición: `capa.renderizar()` **no recibe seed** en su firma, así que el prompt no lo lleva,
  y `cache.clave()` hashea el prompt, así que dos semillas son dos aciertos de caché iguales.
  Hallazgo de paso: **`engine/seed.py` no lo importa nadie** fuera de su propio test — el módulo con
  los streams derivados por clave existe y el producto no lo usa; el propio archivo lo confiesa en su
  encabezado y nadie lo había cruzado con la perilla que la API expone.
  No se quitó porque el front ya la manda y `web/` no es de este rol. Quedó rotulada en los tres
  sitios donde alguien la mira: `SEED_EFECTO` en el servidor, el `description` del Query (sale en
  `/openapi.json`, que sí está servido aunque la UI de docs esté apagada) y `seed_efecto` en el
  evento `inicio`. **Mandé el enum, no la copia:** si la API manda prosa, la prosa y el hecho quedan
  en dos lados que se desincronizan, que es justo el bug de S2-9. El día que el seed elija las N
  paráfrasis, `SEED_EFECTO` pasa a `"trayectoria"` y es la única línea que cambia.

  **S1-7 · la banda honesta, con un marco más fuerte que el del vet.** No es que a la API "le
  faltara" la banda: **`contracts/ronda.json` YA declara `banda.tipo = "entre_trayectorias"`**, así
  que la API estaba **fuera de su propio contrato**, publicando la intra-ronda (0,0 pp) donde el
  contrato promete la de entre trayectorias (22,5 pp). `api/trayectorias.py` corre N trayectorias
  completas, cada una casada con una paráfrasis distinta desde la ronda 1, y las consolida con
  `behavior.rondas.consolidar_trayectorias()` — que ya existía y **no la llamaba nadie desde el
  producto**. Sale la MEDIANA, no la media: la mediana es una trayectoria que de verdad ocurrió.
  Por eso las rondas salen todas al final (cuál es la mediana no se sabe hasta que las N cierran).
  Decisión de Mani entre tres formas de transmitir; quedó "mediana al final".
  *Cuesta lo mismo que la alternativa mala:* 31 celdas × 3 rondas = 93 llamadas por trayectoria,
  **465 con N=5, exactamente lo que costaría `n_parafrasis=5`** en una sola trayectoria para comprar
  la banda angosta. El tope de gasto es UNO para toda la corrida; si corta, `trayectorias_efectivas`
  lo declara en el evento `fin`.

  **Lo que aprendí probando, que valió más que el código.** Dos fixtures fallaron antes de que uno
  funcionara, y los dos fallos son hallazgos:
  1. Forzar `informalizar_total` no abre la banda: el veto lo tumba y todas caen al mismo fallback.
  2. Entrar por el factor prestacional tampoco: **entre 1,30 y 1,70 cambian 0 de 81 decisiones** de
     la ablación (con p(sanción)=1,6% y multa=1e6). `costo_formal` y `costo_informal` están tan
     separados que el factor nunca voltea la comparación.
  El que funcionó es un cliente falso que decide según la redacción: 5 trayectorias distintas,
  **banda de 8,99 pp**, mediana publicada = la trayectoria 2, una de las 5 que ocurrieron. Ese 8,99
  **no es un resultado del proyecto** y así está declarado en el encabezado del test.
  Quedó en `api/test_trayectorias.py`, 5 tests, $0 y sin red. El que importa es el de la paráfrasis:
  **si el parche dejara de llegar hasta la decisión, nada reventaría** — las N darían el mismo
  número, la banda saldría de ancho 0, y eso en pantalla se lee como "el modelo es muy preciso",
  que es la conclusión contraria a la verdadera.

- **2026-08-22 23:00 (sesión del vet) — el vet completo de `main`, y el reparto en 5 tracks. Mergeado en PR #17.**
  - **Lo que hice:** tres auditorías de solo lectura sobre `c63343f` (conductual, pantalla, datos+validación),
    reverificadas contra `b180d51`. Once componentes decididos uno por uno. Todo quedó en
    [`docs/vet/`](../vet/), que es ahora **lo más reciente del repo** y está enlazado desde `AGENTS.md` y
    `docs/README.md`.
  - **Lo tuyo (R2), en orden:** `rondas_totales` con fuente única (`api/serializar.py:74` literal vs el
    default de `behavior/rondas.py:181`, cuadran hoy por casualidad) · la perilla del `seed`, que es
    **decorativa** y está medida (seed 42 y 99 dan trayectorias idénticas): se quita o se rotula ·
    después S1-7, la banda entre trayectorias, que es la honesta y **no existe en el camino del
    producto** porque la API corre una sola · y S2-8, mover la conversión a pesos fuera del navegador.
    El detalle está en [`docs/vet/03-arranque-por-track.md`](../vet/03-arranque-por-track.md).
  - **Tu revisor es Juanda. Tú revisas a Juanda.** Tu verificador: el prompt 16 re-apuntado + `juez-hackathon`.
  - **🔴 Lo que NO puede pasar desapercibido:**
    (1) `behavior/rondas.py:120` hace `round()` sobre `banda.tipo`, que es un string: **cualquier corrida
        con `n_parafrasis>=2` revienta.** Es de Nico y desbloquea a Dani.
    (2) `VALIDATION.md:159` afirma "fuera de muestra de verdad" y el código lo contradice.
    (3) **El pre-registro se sostiene pero NO fue ciego** (`2d4aa7e` ya traía "apunta a la rama B").
        Se dice en el pitch de frente.
    (4) **V-1, el cambio silencioso de la noche:** `13c5a5b` pasó el modelo a Sonnet 5 y la clave de
        caché incluye el modelo, así que **toda la caché quedó fría**. Cada corrida vuelve a costar y a
        tardar. Con `parafrasis=5` puede no caber en `tope_usd=3.0` (`api/servidor.py:89`), **que es tuyo**.
        Espera la medición de Nico antes de subirlo.
  - **Lo que corregí de mi propia lectura:** las industrias **no** están rotas (9 sectores con prefijos
    únicos y `desde_empresas` no trunca; los 4 hardcodeados son andamio), y la clave de caché **sí**
    incluye la política, o sea que mover la perilla sí mueve la corrida.
  - **Pendiente que no alcancé:** los tickets de `docs/tasks/`. `03-arranque-por-track.md` cubre casi todo
    para lo que servían.

- **2026-08-22 — `engine/` existe. Los tres archivos, escritos y verdes.**

  `engine/` pasó de 0 líneas de código a **3 de 3 archivos**, en el orden que
  dejó la sesión anterior: `veto.py` → `fiscalizacion.py` → `seed.py`.
  **44 tests verdes** (`python3 -m pytest engine/ -q`), **7 supuestos
  grepeables**, **cero `TODO`** en código.

  Cada archivo se puede correr solo y se explica a sí mismo:

  ```bash
  python3 -m engine.veto           # el catálogo de razones y su higiene: 6/6 limpias
  python3 -m engine.fiscalizacion  # C, la curva p(E), la cordura y el barrido de S2
  python3 -m engine.seed           # el manifiesto y la prueba de independencia de orden
  ```

  **Las tres decisiones que hay que revisar, porque son las que se pueden discutir:**

  1. **El veto juzga el DETALLE, no el nombre de la estrategia.** El modelo
     inventa nombres —cinco para la misma conducta en la primera corrida real—
     así que `estrategia == "despedir"` deja pasar `reducir_planta` con la misma
     gente adentro. Ese era el bug del doble de prueba. La canonicalización de
     nombres sigue siendo de `behavior/contrato.familia()`: no se duplicó.
  2. **El borde `E → 0` se declara, no se parcha.** El `max(E,1)` de la ADR 0007
     no es un guardia contra la división por cero: el `1` es **quien hace la
     pregunta** — `p` es lo que enfrenta el que está considerando salirse, y al
     salirse él es una unidad fuera de regla. El estado absorbente es el espejo
     de la cascada (equilibrios múltiples, JPubE 2007), no un artefacto. Lo que
     sí era problema es que fuera **silencioso**: para eso está `es_degenerado()`.
     Arreglar la física para tapar el crítico #3 de la ablación habría sido
     fabricar el resultado.
  3. **El determinismo se deriva por clave, no con `spawn()`.** `spawn()` es
     stateful y con 8 hilos el stream de una ronda dependería del orden de
     terminación. Se usa `SeedSequence(seed, spawn_key=(ronda, ...))`, y nunca
     `hash()` de Python (salado por proceso: rompería el determinismo sin que
     ningún test de una sola corrida fallara). Hay un test en subprocesos con
     `PYTHONHASHSEED` distinto.

  **Tres cosas que aparecieron al medir y que no estaban previstas:**

  - 🔴 **S8 mueve el número y hay que decirlo en el standup.** La caja de la ronda
    son 3 meses de `flujo_caja` (ADR 0005), no 1 como el doble de prueba. En la
    corrida de ablación eso mueve los vetos de **96 a 0** y el empleo de la ronda
    3 de **100% a 85,7%**. Está en `MODELO.md` con la medición al lado. **A R5 le
    cambia `n_vetos`/`n_fallback`, que son métricas de diagnóstico del pitch.**
  - **`satura()`**: con `C/E` por encima de ~36 el exponencial cae debajo del
    epsilon del double y `p` sale 1,0 exacto — hay una meseta donde deja de ser
    estrictamente decreciente. Con la `C` del caso demo cubre el 0,027% del
    universo. Se detecta y se reporta; un tope artificial metería un codo falso
    justo donde el proyecto dice descubrir **el codo**.
  - **`-expm1(-x)` en vez de `1 - exp(-x)`**: en el régimen real el exponente es
    ~0,02 y la forma ingenua pierde media docena de dígitos justo donde vive la
    cascada.

  **Lo que esto desbloquea, y para quién:**

  - **Nico (R3):** `EstadoVivo` es el `fraccion_informal_previa` que pide el
    `PUNTO DE SUTURA` de `behavior/rondas.py` (float [0,1], por `arquetipo_id`).
    El motor es la fuente única: los dos dicts de andamio se borran. Se enchufa
    con `veto=veto_del_motor(estado)` en lugar de `veto_permisivo` /
    `veto_doble_prueba`. Y `ESTRATEGIA_TERMINAL = "cumplir"` vive en
    `engine/veto.py` para que `behavior/contrato.FALLBACK` lo importe en vez de
    duplicarlo (compromiso #2, cumplido de mi lado).
  - **Juanda (R5):** `make test` ya tiene qué correr (`pytest engine/`, 44 casos).
    Para `VALIDATION.md`: S8, S9 y S10 son nuevos; el barrido obligatorio de S2 lo
    imprime `python3 -m engine.fiscalizacion`; y `manifiesto()` da la mitad del
    contrato de determinismo de la ADR 0009 que le toca al motor.
  - **Dani (R4):** el mapa distributivo (dato A3) **sigue bloqueado**: necesita
    `muestrear()`, que es de `arquetipos.py` y no entró. `seed.py` ya tiene la
    plomería (`stream_nombrado`), falta el archivo.

  **Lo que NO se escribió, a propósito:** los otros siete archivos de
  `MODELO.md` (`mundo.py`, `costos.py`, `trabajador.py`, `arquetipos.py`,
  `agregado.py`, `rondas.py`, `barrido.py`). Siguen declarados como límite, no
  como `TODO`. Y dos tests que necesitan `rondas.py` quedan nombrados en los
  docstrings en vez de ausentes en silencio: la **corrida de control con `p`
  fijo** (sin cascada) y los niveles 2 y 3 de la ADR 0009.

  **Excepción que me tomé:** `EstadoFiscalizacion` vive en `fiscalizacion.py` y
  no en `mundo.py` como decía el mapa. Sin `mundo.py` escrito, la clase va donde
  vive su fórmula. Está anotado en `MODELO.md`.

- **2026-08-22 (noche) — la rama quedó lista para escribir el motor. No se
  escribió código de `engine/`.**
  - **Tu WIP estaba SIN COMMITEAR** desde la sesión de las 09:52 (`docs/IDEA.md`,
    este handoff, `engine/MODELO.md`) y venía arrastrándose entre checkouts. Ya
    está commiteado y pusheado (`f94ac4a`).
  - **`rol/backend` al día con `main`** (merge `5089f36`): ahora la rama tiene
    todo `behavior/` del PR #4, así que el motor se puede escribir importando
    contra la capa real en vez de contra un doble.
  - ⚠️ **`rol/backend` NO tiene PR abierto.** Va +2 sobre main y todo entra por
    PR según `AGENTS.md`. Abrirlo o dejarlo acumulando hasta tener los tres
    archivos del motor es decisión tuya, pero no se puede olvidar.
  - **Lo que sigue, en orden:** `veto.py` primero (es lo que desbloquea a R3 y
    hoy corre contra dos dobles de prueba), después `fiscalizacion.py`, después
    `seed.py`.
  - **Dato para `fiscalizacion.py`:** `p(E) → 1.0` cuando E→0 crea un **estado
    absorbente** que clava la ablación en 0% para siempre. Está medido en el
    barrido del candado 4 de `behavior/`. Conviene decidir el borde antes de
    cablear.
  - **Dato para `seed.py`:** confirmado que el seed de `behavior/` es decorativo.
    Hoy el determinismo lo da el caché en disco (503 respuestas, verificado byte
    a byte), no una semilla.
  - **De R3, ya cerrado y esperando tu review:** el [PR #6](https://github.com/platanus-hack/platanus-hack-26-co-team-16/pull/6)
    trae la especificación exacta de lo que `behavior/` te pide para el crítico
    #2 (`fraccion_informal_previa`, float [0,1], por `arquetipo_id`, al empezar
    cada ronda). El punto de sutura está marcado en `behavior/rondas.py`
    (`grep "PUNTO DE SUTURA"`). Las 4 decisiones de interfaz que cerraste **no
    tienen fricción** con el código de R3: verificado leyéndolo.

- **2026-08-22 09:52 — Sesión de auditoría y review. Cero código, y esta vez sí fue el costo correcto.**

  Dos entregables: una auditoría del estado real del repo y el review del
  [PR #4](https://github.com/platanus-hack/platanus-hack-26-co-team-16/pull/4) de Nico
  ([comentario posteado](https://github.com/platanus-hack/platanus-hack-26-co-team-16/pull/4#issuecomment-5381006515)).

  **La auditoría, medida y no opinada (a H+12):**

  | | |
  |---|---|
  | Documentación | 6.268 líneas en 57 archivos `.md` |
  | Código en `main` | **321 líneas**, todas en `data/` |
  | Código en `engine/`, `api/`, `web/`, `tests/`, `scripts/` | **0** |
  | Ratio docs:código | **2,55 a 1** |

  **C2 (deploy, H+4) y C3 (punta a punta, H+10) están vencidos.** `platanus-hack-project.jsonc`
  tiene los 4 campos en `<FILL THIS>`, incluido `deploy-url`, que es el archivo de entrega.
  No existe `requirements.txt` ni `pyproject.toml` en todo el repo. Las ramas de Dani
  (`rol/interfaz`, `interfaz-front`) están **detrás** de `main`, sin trabajo nuevo.

  **El hallazgo que cambia mi plan: la tesis del proyecto ya corrió, y no en `engine/`.**
  El PR #4 produce informalidad 63,2% → 75,6% con la probabilidad de sanción cayendo
  4,8% → 2,1%, medido contra la API real por $0,51. O sea que el camino corto **no** es
  escribir los 10 archivos de `MODELO.md`: es escribir los 3 que vuelven real ese número.

  **El review del PR #4.** Verifiqué corriendo, no leyendo: higiene 7/7 limpio, demo
  reproducido exacto, determinismo con paralelismo 8 confirmado byte a byte, y la
  comparación `p ≈ C/E` vs exponencial reproducida (3,16% vs 3,12%, y el borde en E=2%:
  100% vs 63,2%).

  Alejo había dejado `CHANGES_REQUESTED` con 11 puntos. **Verifiqué los 11 contra el código
  y los 11 son válidos.** El crítico #1 lo **reproduje**: una respuesta con
  `estrategia_propuesta: ""` escapa del `try` (porque `construir()` está fuera), mata la
  corrida sin reintentar, y **queda escrita en el caché**, así que la re-corrida determinista
  revienta en el mismo punto para siempre. Es una bomba que se dispara en la demo barata
  delante de un juez.

  **Tres cosas que agregué yo y él no vio:**
  1. **El `seed` no siembra nada.** Seed 42 contra seed 99: salida idéntica salvo la etiqueta.
     Nada en el bucle de rondas es estocástico y `muestrear()` no lo llama nadie.
  2. **El caché está en `.gitignore`** y no hay manifiesto de dependencias: hoy un extraño no
     puede reproducir nada, ni con API key ni sin ella. Contradice ADR 0009 y `make reproduce`.
  3. **El mapa distributivo (dato A3) no se puede dibujar** con lo que corre: el pipeline para
     en los arquetipos y los 6.692 agentes nunca reciben estrategia individual.

  🔴 **La consecuencia más cara, y es decisión de equipo, no de Nico.** Arreglar el crítico #3
  (la ablación compara mal el costo de formalizarse) son 2 horas, pero con el costo bien
  especificado una unidad informal compara formalizarse (≈1,72× ingreso) contra seguir
  informal (≈1,58×): **seguir informal es más barato**, o sea que una ablación correcta
  probablemente **también produce cascada**. Si eso pasa, el candado 4 deja de decir que la
  diferencia es el argumento del LLM. Hay que correrlo y reportar lo que dé.

## Decisión de alcance: tres archivos, no diez

`engine/MODELO.md` define 10 archivos. **A H+12 se escriben tres**, y los otros siete se
documentan como trabajo futuro con honestidad:

| Archivo | Por qué este |
|---|---|
| `seed.py` | Determinismo desde el primer commit, y hoy el `seed` de `behavior/` es decorativo |
| `fiscalizacion.py` | `p(E) = 1 − exp(−C/max(E,1))` con `C` anclado en la cifra de la OIT. Es la cascada |
| `veto.py` | Reemplaza los **dos** dobles de prueba que hay hoy (`veto_permisivo` y `veto_doble_prueba`) |

- **2026-08-22 — Sesión de fundamentación. Cero código, a propósito.** → [PR #3](https://github.com/platanus-hack/platanus-hack-26-co-team-16/pull/3), abierto y esperando revisión de alguien distinto de mí.

  El repo estaba **escrito, no decidido**: documentación densa y buena, pero con huecos
  tapados por buena prosa. Se encontraron **10, todos de backend**, y se cerraron 9. La
  sesión produjo el fundamento para que el motor se escriba rápido y sin devolverse.

  **Lo que existe ahora:**
  - [`docs/IDEA.md`](../IDEA.md) — **la espina dorsal.** La idea completa contra una rúbrica
    de viabilidad (protocolo ODD + Pattern-Oriented Modeling + Epstein + la anatomía y los
    filtros que ya eran nuestros). Sin un campo en blanco. Es la respuesta al problema del
    audio: *"nadie puede explicar la idea completa"*.
  - [`docs/investigacion/`](../investigacion/) — el fundamento del backend en tres esferas:
    **teórica** (qué está probado), **tools** (stack y estándares), **live** (empresas vivas).
    Cada entrada dice qué sirve, **qué no**, y dónde aterriza en `engine/`.
  - [`engine/MODELO.md`](../../engine/MODELO.md) — el mapa *teoría → archivo → función →
    test → supuesto*, con los 10 archivos de `engine/` definidos antes de escribirlos, las
    métricas sin ambigüedad, y **7 supuestos pre-declarados** (S1-S7).
  - **ADR 0005 a 0009**, `docs/UML.md` y `docs/FLUJO.md` actualizados, glosario extendido.

  **Los tres hallazgos que más cambian el motor:**
  1. **No existía el tiempo.** "Ronda" nunca se mapeó a calendario, y sin eso el backtest no
     se puede puntuar. Ahora: **una ronda = un trimestre, horizonte de 9 meses**
     ([ADR 0005](../adr/0005-el-reloj-de-la-simulacion.md)).
  2. **`prob_sancion = capacidad / n_evasores` no era una probabilidad** (no acotada,
     indefinida en 0, sin unidades). Ahora `p(E) = 1 − exp(−C/max(E,1))`, que **sale de
     repartir C inspecciones al azar entre E evasores** (Poisson) y **coincide con la
     fórmula del plan en el régimen relevante**. No cambia el modelo, lo define
     ([ADR 0007](../adr/0007-forma-funcional-prob-sancion.md)).
  3. **La capacidad de fiscalización estaba dentro de `Politica`**, o sea era una perilla
     del usuario — justo lo que el pitch promete que no es
     ([ADR 0006](../adr/0006-fiscalizacion-es-estado-del-mundo.md)).

## En qué estoy trabajando

- [x] [PR #3](https://github.com/platanus-hack/platanus-hack-26-co-team-16/pull/3) mergeado.
- [x] Review del [PR #4](https://github.com/platanus-hack/platanus-hack-26-co-team-16/pull/4)
      de Nico, consolidado con el de Alejo y posteado.
- [x] **`engine/` escrito**: `veto.py`, `fiscalizacion.py`, `seed.py`. 44 tests verdes.
- [ ] **Avisar S8 en el standup.** Cambia `n_vetos`/`n_fallback` y el empleo de la ronda 3.
- [ ] Tras el merge del PR de Nico: quitar los dos dobles de prueba del veto
      (`capa.veto_permisivo` y `demo.veto_doble_prueba`) y enchufar `veto_del_motor`.
- [ ] Si sobra tiempo, el cuarto archivo es `arquetipos.py`: sin `muestrear()` Dani no
      puede dibujar el mapa distributivo. La plomería de seed ya está.
- [x] **Track del vet, los 3 puntos** (`rondas_totales`, seed, banda). Commits `9167811`, `8b39b4d`.
- [ ] **PR de `rol/backend` a `main`, marcado BLOQUEADO por S1-1.** No se mergea antes que Nico.
- [ ] **S2-8** — el "$X billones/mes · proxy de PIB laboral" se calcula en el navegador
      (`Metricas.tsx:27,45`), fuera de la capa que declara "cero números inventados". Es la única
      cifra en pesos absolutos de la pantalla y la más citable en un pitch. Va a `serializar.py`
      con su `# SUPUESTO:`. Coordinar con Dani.
- [ ] **V-1** — cuando Nico mida el costo real con caché fría, decidir si `tope_usd` (hoy 3.0,
      `servidor.py`) alcanza para 465 llamadas. Con criterio, no a ojo.
- [ ] Correr el verificador del track: prompt 16 re-apuntado + `juez-hackathon`.

## Cuatro compromisos que ya tomé por escrito, en público

Están en el comentario del PR #4, así que **Nico está construyendo contra ellos**. Si el motor
los contradice, el que está mal es el motor.

| # | Compromiso | Dónde aterriza |
|---|---|---|
| 1 | **`engine/veto.py` produce razones que pasan `higiene.revisar()` limpias**, con test. Las razones del veto viajan dentro del prompt de reintento, así que un `$`, un año de 4 dígitos o la palabra "gobierno" en una razón mata la corrida con `ContaminacionError` | `veto.py` + un test |
| 2 | **El fallback terminal es `cumplir`**, no `absorber`. Es el canon de `IDEA.md` §5.3 y §5.7. `behavior/contrato.py` tenía `absorber` y lo cambia Nico | `veto.py`, y `contracts/` no cambia |
| 3 | **El muestreo vive en `engine/`** con la firma de `MODELO.md`: `muestrear(arq, n, rng)`. El de `behavior/arquetipos.py` se borra o se renombra, para que no haya dos con el mismo nombre y semillas distintas | `arquetipos.py` (mío) |
| 4 | **`C`, `0.18` y `1.5` son míos.** `C` sale de la OIT (1.300 inspectores) vía el supuesto S2; los otros dos de V3. En `behavior/` quedan con `# SUPUESTO:` hasta que el motor los provea | `mundo.py`, `costos.py` |

## Hallazgos de esta sesión que son de OTRA carpeta

**Ninguno lo toqué.** Están medidos, con archivo y línea, listos para que su dueño decida.

| # | Hallazgo | De quién | Por qué importa |
|---|---|---|---|
| 1 | 🔴 **S1-1 bloquea DOS tracks, no uno.** `Ronda.a_contrato()` (`behavior/rondas.py:119`) redondea todo lo no-booleano y la banda honesta lleva `tipo`, que es string. Hoy no revienta solo porque la banda degenerada omite `tipo` | Nico | Es **la única línea** entre el producto y su propio contrato. Verificado en los dos sentidos: con `trayectorias=5` la corrida muere con `TypeError: type str doesn't define __round__`; con el fix simulado en memoria el flujo cierra limpio (`inicio · 5 trayectoria · 1215 decision · 4 ronda · fin`) |
| 2 | 🔴 **La banda solo cubre UNA de las cinco métricas publicadas.** `banda_entre_trayectorias()` calcula percentiles solo sobre `tasa_informalidad`. Medido entre 5 trayectorias: `ingreso_laboral_relativo` se mueve **10,23 pp** y sale a pantalla como número pelado — más que la banda que sí publicamos (8,99 pp) | Nico | Publicar banda sobre una métrica y las otras cuatro peladas es **peor que no publicar ninguna**: le enseña al lector que las que no la llevan son ciertas |
| 3 | 🟠 **`p10`/`p90` son el mínimo y el máximo hasta N=8.** Verificado corriendo `_percentiles` con N=3,5,9,11,21: solo desde **N=9** se vuelven percentiles interiores | Juanda (pitch) y Dani (copy) | Con N=5 una sola trayectoria rara define todo el borde. Decir "p10-p90" en pantalla es mentir levemente; decir "rango entre las 5 corridas" es exacto |
| 4 | 🟠 **`degenerada: False` en una banda de ancho cero.** `_percentiles` la marca no-degenerada en cuanto hay 2+ valores, aunque sean todos iguales | Nico | `degenerada` es justo la bandera con la que el front decidiría si dibujar la banda. En `modo=reglas` publica un ancho cero rotulado como real |
| 5 | 🟠 **La ablación es insensible al factor prestacional.** Entre 1,30 y 1,70 cambian **0 de 81** decisiones (p(sanción)=1,6%, multa=1e6): `costo_formal` y `costo_informal` están tan separados que el factor nunca voltea la comparación | Nico / Juanda | `barrer_factor()` (`behavior/ablacion.py:153`) dice medir *"la sensibilidad del candado 4"*. **Pregunta abierta, no defecto afirmado:** no verifiqué con qué multa corre ese barrido. Si corre con estos parámetros, no está midiendo nada |
| 6 | 🟢 **`engine/seed.py` no lo importa nadie** fuera de su propio test | mío, declarado | El módulo de determinismo existe y el producto no lo usa. Es coherente con que la perilla sea decorativa, pero conviene decirlo antes de que lo encuentre un juez |

**Para Dani, tres cosas que le cambian el trabajo:**
1. 🔴 **Que NO haga S2-2 (`parafrasis=5`).** Cuesta las mismas 465 llamadas y compra la banda
   **angosta**. Con `trayectorias=5` compra la honesta. Mismo dinero, distinta verdad.
2. Las rondas **ya no llegan en vivo**: llegan las 4 juntas al final, y son las de la mediana.
   Mientras se calcula llegan `decision` (con campo `trayectoria`) y un evento nuevo `trayectoria`
   `{indice, de}`. Su cola de rondas pendientes (S2-5) encaja perfecto con esto.
3. `inicio` trae `seed_efecto`. Con `"etiqueta"` la frase en pantalla es *"la semilla rotula la
   corrida; hoy no cambia ninguna decisión"*. Va en el mismo panel que `modo` (su S2-1).

**Y una recomendación de diseño que le paso, no le impongo:** con N=5 no hay estadística que
agregar, hay puntos que mostrar. Una desviación estándar o un IQR sobre 5 datos tiene más error que
la cosa que describe. Lo correcto es **dibujar las 5 trayectorias** y resaltar la mediana. Es un
dot plot, no un box plot.

## Bloqueado / esperando a alguien

> 🔴 **2026-08-23 — el PR de `rol/backend` está BLOQUEADO por S1-1 de Nico.** Es una línea en
> `behavior/rondas.py:119` (redondear solo lo que es número). Sin eso, `trayectorias=5` revienta la
> corrida entera. Mergear en orden: primero el suyo, después el mío.


**Nada me bloquea para escribir el motor.** El contrato ya está congelado en `main`
(`contracts/decision.json` + la forma del `Protocol Veto`), y los cuatro puntos de arriba los
respondí yo. La relación se invirtió: **Nico depende de mis decisiones, no yo de su código.**

Lo que sigue abierto y es de otros:

1. **Nico (R3)** — los 3 críticos del PR #4, sobre `rol/conductual-top-k` (que ya trae
   arregladas las dos divergencias de ADR 0005 y 0007). Acordado: **un solo PR que reemplaza
   al #4**, para que `main` nunca cargue el bug del caché.
2. **Alejo (R1)** — aval de [ADR 0008](../adr/0008-asimetria-firma-trabajador.md).
   **Nico ya la avaló** en el PR #4; falta él. Y congelar el campo `realizacion:
   {ocurre, razon}` que Nico propuso y yo avalé: es lo que evita que el dato A4 mezcle
   *"no pude pagarlo"* con *"no me lo aceptaron"*.
3. **Juanda (R5)** — tres cosas, y las tres son más urgentes que las mías:
   - 🔴 **`platanus-hack-project.jsonc` con los 4 campos en `<FILL THIS>`** y nada desplegado.
     C2 lleva vencido desde H+4.
   - 🔴 **No existe `requirements.txt`** y el caché está en `.gitignore`: `make reproduce` no
     puede funcionar para un juez. ADR 0009 define el determinismo como *"mismo seed + misma
     caché + mismas versiones"* y hoy no publicamos ni la caché ni las versiones.
   - La frase de determinismo en `README.md` y `AGENTS.md` ([ADR 0009](../adr/0009-frontera-del-determinismo.md)).
   - Avisarle que **el candado 4 puede colapsar** cuando Nico arregle la ablación. Va en
     `VALIDATION.md`, que es suyo.
4. **Dani (R4)** — `web/` sigue en 0 líneas. Y necesita saber que **el mapa distributivo no se
   puede llenar** hasta que yo cablee el muestreo, y que `banda` gana un campo `degenerada`
   que no está en el `contracts/ronda.json` congelado (aditivo).

## Supuestos que tomé

Los 7 del motor están pre-declarados con impacto y mitigación en
[`engine/MODELO.md`](../../engine/MODELO.md). Los que R5 tiene que recoger en `VALIDATION.md`:

- **S2 · inspecciones por inspector por trimestre** — sin fuente. **Es el supuesto más
  importante del proyecto**: es el numerador de `p(E)`. Barrido de sensibilidad obligatorio.
- **S1 · factor prestacional ≈ 1,4-1,5** — ya estaba previsto (V3 del plan), sigue sin cifra exacta.
- **S3 · prima de protección del trabajador** — sin fuente. Con prima 0 es el caso extremo y se reporta.
- **S7 · el costo informal ignora la pérdida de crédito y de clientes formales** — sesgo de
  dirección **conocida**: subestima el costo de informalizar, luego **nuestra cascada es una
  cota superior por ese canal**. Conviene decirlo antes de que lo pregunten.
- **Reloj:** el backtest se mide **a 9 meses del decreto**. Escrito antes de conocer el
  resultado, a propósito.
