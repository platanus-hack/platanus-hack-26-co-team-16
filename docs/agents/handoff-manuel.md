# Handoff — Manuel · R2 · Backend

> **Tu memoria entre sesiones.** Léelo al abrir tu sesión de agente, actualízalo antes de cerrarla.
> Este archivo es solo tuyo: nadie más lo edita, así nunca da conflicto de merge.
> Tus carpetas: `engine/`, `api/` · Tu rama: `rol/backend`
> Tu misión, entregables y prompt de arranque: [`docs/ROLES.md`](../ROLES.md)

## Cómo retomar (actualizado 2026-08-23 06:45, sesión 4 — la del corte final)

> **Pega esto en una sesión nueva y arranca sin leer nada más.** El detalle está más abajo,
> en la sección **Sesión 4**.

```
Trabajas en engine/ y api/, y SOLO ahí. Rama: rol/backend.
Lee docs/agents/handoff-manuel.md, seccion "Sesion 4". Congelamiento: domingo 09:30.

TODO LO DE ABAJO ESTA MEDIDO A MANO ENTRE LAS 04:45 Y LAS 06:45. No confies en los
informes del vet a tres ejes: los tres miden arboles viejos.

ESTADO DEL DEPLOY, y es lo primero que hay que arreglar:
- enjambre-web YA esta en main. Probado: /reporte paso de 404 a 200.
- enjambre-api NO se redesplego. La prueba: el candado `_ocupado` (api/servidor.py:167)
  sigue trabado desde las 04:49, y un redeploy reinicia el proceso y lo liberaria. Son
  DOS servicios en render.yaml (:32 api, :52 web) y se cambio solo uno.
- Consecuencia: la URL publica NO puede correr una sola simulacion. Seis corridas de
  `make humo` entre 04:49 y 06:40 devuelven "ya hay una corrida en curso".
- ARREGLALO PRIMERO: cambiar la rama de enjambre-api a main en el dashboard, o reiniciar
  el servicio. Verifica con `make humo URL=https://enjambre-web.onrender.com` (ablacion,
  cuesta $0): tiene que llegar el evento `fin` con 4 rondas.

LO QUE MIDE EL REPO HOY (corrido, no leido):
  make test       88 passed en 0.48s + regresiones de behavior/ ok
  make reproduce  corre y es determinista SIN cache-demo.json; CON el revienta
  make run        PENDIENTE - scripts/run_simulacion.py NO EXISTE
  make validate   imprime EL numero pero SALE CON EXIT CODE 1 (G1, G2, G3 BLOQUEADO)
  make humo prod  FALLO por el candado trabado

DOS DEFECTOS QUE NADIE HABIA MEDIDO Y NO SON DEL DEPLOY:
1. `make humo` sobre la corrida real falla con "la ronda 0 arranca en 0.1799 y la GEIH
   dice 0.3057". Es sobre main, sin Render de por medio. El motor arranca en ~18% y
   /poblacion declara 30,57%. Es una pregunta de juez sin respuesta ensayada, y NO esta
   en ninguno de los 9 arreglos de la fusion.
2. scripts/humo_deploy.py:53 se traga la excepcion y reporta "ni /api/poblacion ni
   /poblacion respondieron 200". Con el CA bundle roto el error real es SSL y el mensaje
   manda a perseguir Render en vez del portatil. Son 3 lineas.

LOS 9 ARREGLOS DE LA FUSION: al cierre solo A1 (a medias) y A2 estaban tocados.
   Verificados uno por uno con grep; la tabla esta en la seccion "Sesion 4".

LO TUYO (engine/ y api/), en orden:
   1. A3 - cap de gasto acumulado en el evento `fin` y exponer fraccion_fallback (69,1%)
      y fraccion_sin_salida (63,0%). Los campos ya viajan en el contrato y ningun panel
      los lee. Es la mitad de motor del defecto estructural E2.
   2. El candado `_ocupado` no tiene timeout ni forma de resetearse sin reiniciar el
      proceso. Hoy costo ~2 horas de URL muerta. Un timeout, o un endpoint de estado que
      diga si esta ocupado, es tuyo.
   3. El 18% vs 30,57%: si sale de engine/, es tuyo.
```

## Sesión 4 — 2026-08-23 04:45-06:45 — la corrida pagada y el vet de ejecución

Sesión de verificación y de A2. **Nada de lo de acá viene de un informe de agente: todo se
corrió.** El disparador fue leer `docs/vet/revision-3ejes/10-fusion.md` y preguntarse qué falta
para que el deploy esté vivo de verdad.

### Lo que se entregó

- **PR #36** (`a2/cache-demo-versionada`): `behavior/cache-demo.json` con **518 respuestas
  Sonnet ya pagadas**. Cierra la deuda que la **ADR 0009** le dejó abierta a `behavior/`
  (`:32-34`) y que nunca se cumplió.
- Este handoff.

### La corrida pagada, con sus números

Contra `api/servidor.py` local, sobre el código de `main`, con los **mismos parámetros que
manda el frontend** (`web/enjambre/estado/flujo.ts:37` manda `aumento_pct=23` y `seed=42`; el
resto son defaults del servidor: `cobertura=0.8`, `trayectorias=5`, `parafrasis=1`):

```
518 llamadas a claude-sonnet-5 · USD 7,8731 · 1547,9 s (25,8 min)
1028 decisiones · 4 rondas · cache 0 aciertos / 648 fallos (corrida en frío)
final: informalidad 31,22% · empleo 99,64%
banda entre_trayectorias [27,21%, 50,84%] · estabilizada=True
```

**El costo real fue 2,5× la primera estimación.** Se estimó "<$3" leyendo
`behavior/presupuesto.py:30` (`TOPE_POR_DEFECTO_USD = 3.00`). El número correcto sale de
`api/servidor.py`: el front no fija `trayectorias`, así que toma `N_TRAYECTORIAS = 5`, y eso
son 465 llamadas previstas (~$6,23), no 93 (~$1,25). Terminó en 518 llamadas y $7,87 por
reintentos. **Para la próxima: el costo de una corrida se calcula con
`llamadas_de_la_corrida(cobertura, trayectorias)` y `tope_derivado(...)`, que ya existen y no
mienten. La constante de `presupuesto.py` es de cuando una corrida era UNA trayectoria.**

### Por qué el `cache-demo.json` no se pudo hacer gratis

El primer intento fue exportar la caché que ya había en disco (503 entradas). **No sirve, y
falla de la peor forma:** son todas `claude-haiku-4-5`, anteriores al commit `13c5a5b` ("la
masa pasa de Haiku 4.5 a Sonnet 5"), y `cache.clave()` hashea el modelo como **primer campo**.
Acierto estructural: **cero**. Commitear ese archivo convierte un `make reproduce` que cae
limpio a la ablación en un stack trace para cualquiera sin API key. Se probó y se descartó.

`Cache.exportar()` (`behavior/cache.py:94`) **ya existía y nadie lo había llamado nunca.**

### El límite conocido que el PR #36 deja abierto

`make reproduce` **no** queda arreglado, y cambia su modo de fallar: con el archivo presente,
`scripts/reproduce.py:58-66` construye `ClienteConductual` (que sin key **no** falla al
construirse, falla al pedir) y revienta en vez de caer a la ablación.

Causa: `reproduce.py` llama a `correr()` **sin `cobertura_llm`**, o sea manda las **81** celdas
al LLM; la API manda **31**. Medido: con `cobertura_llm=0.8` sube a **43 aciertos / 5 fallos**,
así que tampoco alcanza solo con eso. Los 5 que faltan son de la **paráfrasis**, que
`reproduce.py` no fija y `api/trayectorias.py` sí. El arreglo es de R5 y son dos cosas: pasar la
cobertura, y capturar `SinCredenciales`.

### Los 9 arreglos de la fusión, verificados uno por uno

| # | Estado al cierre | Evidencia |
|---|---|---|
| A1 | **a medias** | web en main (`/reporte` 200); api no (candado sigue trabado) |
| A2 | **PR #36** | `cache-demo.json` con 518 entradas Sonnet |
| A3 | sin tocar | `fraccion_fallback` 69,1% y `fraccion_sin_salida` 63,0% siguen sin panel |
| B1 | parcial | "no puede pagar"/"quién aprieta" ya no están en `web/`; falta la nota al pie |
| B2 | sin tocar | `VALIDATION.md`: 0 ocurrencias de "2,63" y 0 de "ciego" |
| B3 | sin tocar | `scripts/validate.py:206` sigue diciendo `Cobertura del rango:` |
| C1 | sin tocar | "proyección oficial" vivo en `Hero.tsx:70`, `CurvaBrecha.tsx`, `Relato.tsx:86`, `reporte/page.tsx:182` **y en el stdout de `make reproduce`** |
| C2 | sin tocar | no verificable con la API trabada |
| C3 | sin tocar | el 37,37 solo vive en `/reporte` y `narrativa.ts`, no en `/` |

**Dos cosas que la fusión no vio:** C1 **también está en la CLI**, no solo en `web/` (`make
reproduce` termina con "brecha contra la proyección oficial"); y `web/prototipo/mapa.html`
narra la cascada como hallazgo en 4 líneas.

**Y un número que la fusión subestimó:** al deploy le faltaban **71** commits de `main`, no 15.

## Cómo retomar (sesión 3, histórico)

> **Pega esto en una sesión nueva y arranca sin leer nada más.** Lo de abajo es el detalle.

```
Trabajas en engine/ y api/, y SOLO ahí. Rama: rol/backend, con 13 commits empujados.
Lee primero docs/agents/handoff-manuel.md: la entrada del 2026-08-23 (sesión 3).

ESTADO: PR #19 abierto, mergeable=CLEAN y BLOQUEADO por S1-1 de Nico. El arreglo existe en
conductual/banda-s1-1, commit ed99d79, pero al cierre NO tiene PR y main sigue en 9f5d71e con
el round() sobre banda.tipo. Los 5 puntos del track están CERRADOS: S2-9, S1-4, S1-7, S2-8
y V-1. La primitiva opcional A3, engine/arquetipos.py::muestrear(), también está hecha en
43d5664 y auditada por juez-cientifico. 89 tests verdes (python3 -m pytest api/ engine/ -q).

LO PRIMERO, y solo cuando S1-1 esté en main:
- Traer main a rol/backend, correr la suite completa y el smoke SSE en modo=reglas con
  trayectorias=5. Hoy main todavía muere con "TypeError: type str doesn't define __round__".
  Cuando termine en evento fin, quitar el prefijo BLOQUEADO del PR #19 y pedir review a Juanda.

LO QUE ESTÁ ESPERANDO A MANI (no arranques sin su OK, cuesta plata):
- El warmeo de auditoría: UNA trayectoria a 23% = USD 1,26. Audita la cadena entera
  (credencial -> llamada real -> caché -> exportar -> preload al arrancar) antes de gastar
  los ~$31 de las 5 posiciones. Requiere que Mani exporte ANTHROPIC_API_KEY: el .env del
  repo dice ANTHROPIC_KEY y nada hace load_dotenv, así que hoy no llega al proceso.
  NUNCA le pidas la key por chat.
- Warmear en un DIRECTORIO APARTE (Cache(directorio=...)), no en behavior/.cache/: así el
  cache-demo.json sale limpio y no se toca la caché de Nico.

FRONTERA DE A3:
- muestrear(arq, n, rng) ya existe y acepta el ResultadoArquetipo real. Falta cablearlo al
  bucle/API y pintarlo; no decir que el mapa está entregado. Ese cableado NO bloquea PR #19.

REGLAS: no tocar carpetas ajenas (si el arreglo las necesita, se avisa en Vibe Coders); todo
supuesto marcado con # SUPUESTO: donde se toma; al LLM jamás se le nombra la política, solo la
mecánica; git diff --stat antes de decir que algo se hizo; nadie pushea a main.
```

**Ya comunicado al equipo** (Vibe Coders, 2026-08-23): los 6 hallazgos de otras carpetas, el
"Dani, no hagas S2-2" y el dato de p10/p90 para el pitch. No hay que repetirlo.

## Dónde quedé

_Lo más reciente arriba._

- **2026-08-23 07:00 — revisé y mergeé el PR #21 (el deploy de R5) a `main`. Merge commit `9665a08`.**
  - **Por qué me tocó a mí:** la tabla de revisores de [`docs/vet/03-arranque-por-track.md`](../vet/03-arranque-por-track.md)
    asigna el track de R5 a R2, y el punto 3 del flujo de `AGENTS.md` exige que revise alguien
    distinto de quien escribió, en sesión distinta.
  - **Merge commit y no squash, a propósito:** los cuatro mensajes de Juanda traen tres hallazgos
    medidos (Vercel corta los rewrites externos a 120 s y una corrida LLM tarda 166 s ·
    `ENJAMBRE_API` se congela en `.next/routes-manifest.json` durante el **build**, no al arrancar ·
    Render define `NODE_ENV=production` y `npm ci` a secas se salta `typescript`). Squashearlos
    perdía justo lo que sirve dentro de seis meses.
  - **Lo que verifiqué antes de mergear** (no lo que el PR decía): cero solapamiento de archivos
    con lo que `main` avanzó desde el merge-base — los PR #20 y #23 tocaron `behavior/`, `engine/`
    y `data/`, este toca docs raíz, `Makefile`, `scripts/` y `render.yaml` · `make test` sobre el
    árbol **ya mergeado**: **70 pasando** (no 66; los 4 extra vienen del #23) · el deploy responde
    en vivo, incluido **el proxy `/api/poblacion` del front en 200**, que es la prueba de que
    `ENJAMBRE_API` quedó bien horneado · el bloque pre-registrado de `VALIDATION.md` intacto con su
    propio comparador: `idéntico: True | 1056 vs 1056`.
  - **Qué gana el repo:** la URL de la entrega existe (`https://enjambre-web.onrender.com`),
    `platanus-hack-project.jsonc` dejó de tener `<FILL THIS>`, y `VALIDATION.md` **retracta** la
    frase *"es fuera de muestra de verdad"* y **pre-compromete** qué se hace con el número nuevo
    cuando se arregle S3-1. Eso desbloquea a Nico y Alejo: pueden correr S3-1 sabiendo que el
    criterio ya está escrito y no depende del resultado.
  - 🔴 **Cabo suelto que dejé vivo a propósito — no es mío y no lo toqué.** `render.yaml` declara
    `branch: rol/integracion-deploy` en los dos servicios. **Por eso NO borré la rama al mergear:
    borrarla tumba el autodeploy de la URL de la entrega.** Consecuencia contraintuitiva mientras
    siga así: **un commit a `main` NO redespliega, y uno a `rol/integracion-deploy` SÍ.** El cambio
    a `branch: main` (o cambiar la rama en el dashboard, que es equivalente) es de R5; se lo dejé
    escrito en el comentario del PR #21. `docs/DEPLOY.md:69` también quedó desactualizado por lo
    mismo.
  - **Lo que este PR NO cerró y sigue abierto:** el resto de C2 — la cascada todavía figura como
    *hallazgo* en `README.md:23`, `AGENTS.md:3`, `docs/PLAN.md` §1.1 y `docs/IDEA.md:145,154`. En
    los dos archivos que Juanda sí publicó ya está escrita como **mecanismo**. Y `$50` de crédito
    de Render ≈ 30 días: los servicios se suspenden cuando pase la votación.

- **2026-08-23 (sesión 3) — `arquetipos.py` cerrado, PR #19 re-auditado y bloqueo S1-1
  localizado en una rama concreta. Commit `43d5664`, empujado a `rol/backend`.**

  **Estado remoto medido al cierre:** `origin/main = 9f5d71e`; PR #19 abierto,
  `mergeStateStatus=CLEAN`, sin review ni checks publicados. S1-1 es de **Nico (R3)**. Su arreglo
  está en `origin/conductual/banda-s1-1`, commit `ed99d79`, pero GitHub no reporta ningún PR para
  esa rama. No se trajo ese commit directamente: el acuerdo dice esperar a que entre a `main`.

  **El cuarto archivo de engine entró.** `engine/arquetipos.py::muestrear(arq, n, rng)` reparte
  estrategias individuales desde la distribución de `behavior.capa.ResultadoArquetipo`, con
  stream externo derivable por `stream_nombrado()`, orden estable y normalización resistente a
  pesos extremos. `engine/test_arquetipos.py` agrega 18 pruebas. La suite completa queda en
  **89 verdes** (`python3 -m pytest api/ engine/ -q`).

  **La auditoría científica sí cambió el código.** El primer pase detectó que el protocolo decía
  `id` mientras el productor real expone `arquetipo_id`; también detectó que el reporte decía
  “A3 entregado” sin ningún consumidor. Se corrigió el contrato y se añadió una prueba contra el
  `ResultadoArquetipo` real. El segundo pase exigió declarar dos supuestos más fuertes que
  “intercambiabilidad”: (1) frecuencias de decisiones aceptadas → probabilidades conductuales y
  (2) sorteos iid condicionales. Quedaron marcados con `# SUPUESTO:` y en S6 de `MODELO.md`.
  Veredicto final: sin bloqueantes de código ni tests.

  **Frontera honesta de A3:** la primitiva de muestreo está lista; nadie la llama todavía. Falta
  cablearla al bucle, exponer los agentes por la API y pintarlos. No bloquea este PR y no se toca
  `behavior/` ni `web/` desde este track.

  **Lo único que falta para entregar PR #19 a Juanda:**
  1. Nico abre y fusiona S1-1 desde `conductual/banda-s1-1` hacia `main`.
  2. Manuel trae `main` a `rol/backend` sin resolver por encima de carpetas ajenas.
  3. Corre `python3 -m pytest api/ engine/ -q` y el smoke SSE `modo=reglas`,
     `trayectorias=5`; tiene que cerrar con evento `fin`, no `error`.
  4. Quita `🔴 BLOQUEADO` del título del PR #19 y pide review a Juanda.

  **No ejecutado:** ninguna llamada paga, ninguna credencial solicitada, ninguna caché tocada.
  El warmeo de auditoría de USD 1,26 sigue esperando OK explícito de Mani y no es prerrequisito
  para que Juanda revise PR #19.

- **2026-08-23 (sesión 2) — el track del vet queda CERRADO: S2-8 y V-1 hechos, los dos
  verificadores corridos, y un bug propio encontrado por ellos. Commits `5bdc2b6` … `def0db7`.**

  **S2-8 · los pesos absolutos salen del servidor.** `Metricas.tsx:27,45` rearmaba la masa
  salarial base desde `poblacion.arquetipos` y la multiplicaba por el índice relativo para
  mostrar "$ 8,15 billones/mes · proxy de PIB laboral": la única cifra en pesos de la pantalla,
  la más citable en un pitch, nacía **en el navegador**, fuera de la capa que declara "cero
  números inventados" y sin `# SUPUESTO:`. Ahora viaja como `masa_salarial_cop` en el evento
  `ronda`. Las dos cifras salen de UNA pasada (`_masa_salarial()`) para no reabrir el hueco de
  S2-9. *Medido:* es el mismo número, diferencia **1,6e-05 relativo** (todo el `round(rel, 4)`
  del alambre) y en pantalla el mismo texto a dos decimales de billón. 4 tests en
  `api/test_serializar.py`. **El borrado en `web/` es de Dani y no está hecho:** hasta que
  borre, la cifra tiene dos fuentes, que es literalmente el defecto S2-9.

  **V-1 · el tope de gasto se deriva de la corrida que se pidió.** Primero lo derivé de la
  medición ($1,26 × N × 1,25 = $7,88 fijo) y **eso estaba mal**: el costo no es constante,
  depende de `cobertura`. Ahora `tope_derivado(cobertura, trayectorias)` cuenta las llamadas
  exactas con `particionar_por_peso()`, la misma función que usa el motor. No es estimación.

  | `cobertura` | Celdas | Llamadas (×5 tray.) | En frío | Tope |
  |---|---|---|---|---|
  | 0,50 | 9 | 135 | $1,81 | $2,26 |
  | **0,80** (default) | **31** | **465** | **$6,23** | **$7,79** |
  | 1,00 | 81 | 1.215 | $16,29 | $20,36 |

  `TOPE_USD_MAXIMO = 25,00` es el techo y la única cifra que es juicio y no cuenta: deja pasar
  la corrida de calidad máxima sin clipar y es el 11% de los ~$230 vivos del equipo. Si lo
  pedido no cabe, **la corrida se rechaza antes de gastar un peso**, diciendo cuánto cuesta y
  qué bajar. La tabla quedó en `api/README.md`, que es la respuesta a la pregunta de Q&A
  "¿cuánto les cuesta mover el slider?".

  **El bug que era MÍO y lo encontró el verificador.** `_parafrasis_fijada()` reemplaza
  `behavior.capa.parafrasis` por una lambda que **ignora su `n`**, así que `behavior/capa.py:250`
  da una sola vuelta pase lo que pase: **`parafrasis` quedó inerte en el camino de trayectorias**,
  y lo rompí yo en el PR anterior. O sea que arreglé una perilla muerta (el seed) y creé otra en
  el mismo PR, esta documentada como "multiplica el costo por su valor". No se arregla, se
  declara (`PARAFRASIS_EFECTO = "ninguno"`, mismo patrón que `SEED_EFECTO`): una trayectoria
  **está definida** por su paráfrasis, así que pedir N paráfrasis adentro de una no significa
  nada. Y salió del cálculo del tope: con `parafrasis=9` autorizaba 9× lo que se iba a gastar.

  **`engine/MODELO.md`**, carpeta propia: decía *"si solo lees un archivo, lee `rondas.py`"*
  catorce líneas después de declarar ese archivo como uno de los siete que NO se escriben.
  Mismo defecto que `AGENTS.md` ya se había corregido el 22-ago.

  **La caché versionada.** `api/servidor.py` ahora levanta `behavior/cache-demo.json` al
  arrancar, si existe. Es el eslabón que faltaba: la caché en disco vive en la MÁQUINA que corre
  el motor, así que warmear un portátil **no calienta el deploy**. Hasta hoy solo la importaba
  `scripts/reproduce.py`. El archivo no existe todavía (`DEFECTOS.md` 3.6, abierto).

  **Lo verificado, en las dos direcciones, sobre esta rama:**

  ```
  trayectorias=1 -> el flujo cierra limpio (evento fin, banda_tipo "degenerada")
  trayectorias=5 -> event: error · TypeError: type str doesn't define __round__ method
  con S1-1 parchado EN MEMORIA -> 5 trayectorias efectivas · banda_tipo entre_trayectorias · fin limpio
  ```

  La frontera exacta es **trayectorias >= 2**, no `n_parafrasis >= 2`: con una sola trayectoria
  válida `consolidar_trayectorias()` devuelve la corrida intacta y la banda nunca lleva `tipo`.
  O sea que el bloqueo cae sobre **la configuración por defecto del endpoint**. Comunicado a
  Nico en Vibe Coders el 23-ago junto con el cambio del tope.

## Lo que quedó abierto y de quién es

  **Mío, y bloqueado por plata (necesita el OK de Mani):**
  - El warmeo de auditoría: **1 trayectoria a 23% = USD 1,26**. Audita credencial → llamada →
    caché → `exportar()` → preload, antes de comprometer los ~$31 de las 5 posiciones
    (23%, 0%, 10%, 17%, 30%). Decisión de Mani: precalentar en vez de bajar la calidad.
  - Warmear en un **directorio aparte** (`Cache(directorio=...)`), no en `behavior/.cache/`:
    deja el `cache-demo.json` limpio y no toca la caché de Nico (505 entradas de Haiku, ya
    invisibles para Sonnet porque la clave incluye el modelo; **no las borres**).

  **Mío, si sobra:** `engine/arquetipos.py` con `muestrear(arq, n, rng)`. Sin eso Dani no
  dibuja el mapa distributivo (dato A3).

  **La credencial, que es de Mani y NO se pide por chat:** el `.env` del repo tiene
  `ANTHROPIC_KEY` y el SDK lee `ANTHROPIC_API_KEY` (`.env.example:36`), y **no hay `load_dotenv`
  en ningún módulo de Python**. Hoy ese `.env` no llega al proceso. Se arranca con
  `set -a && source .env && set +a && uvicorn api.servidor:app --port 8000`.

  **De otros, comunicado y sin tocar:**
  - **Nico (S1-1):** el `round()` de `behavior/rondas.py:119`. Bloquea PR #19 y a Dani.
  - **Nico:** `behavior/cache-demo.json` hay que exportarlo y commitearlo; el archivo vive en
    su carpeta. Sin eso el deploy arranca frío siempre.
  - **Dani:** borrar `Metricas.tsx:24-31,45` cuando entre PR #19. Mientras tanto la cifra en
    pesos tiene dos fuentes.
  - **Juanda:** `VALIDATION.md:164` sigue diciendo "fuera de muestra de verdad" cuando la
    decisión C1 fue retractarlo. `juez-hackathon` lo marca como lo primero que un juez encuentra.

  **Riesgo de demo, decidido pero no resuelto:** el front manda solo `aumento_pct` y `seed`, así
  que recibe `trayectorias=5`. Las 5 corren EN SERIE (un global de módulo lo obliga,
  `api/trayectorias.py`) a 2m46s cada una: **~14 minutos en frío** y las rondas salen todas al
  final por diseño. Un juez que mueve el slider a una posición nueva mira el enjambre 14 minutos
  sin una sola ronda. La decisión de Mani fue **precalentar**, no bajar la calidad.


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

---

# Sesión 23-ago · último momento (rama `backend/ultimo-momento`)

Se ejecutó `docs/ultimo-momento/manu-backend.md` completo Y el barrido de todo lo que
quedaba abierto de backend en los informes (auditoría final, juez técnico eje A, juez
científico eje B, peeky, p9-procedencia, `DEFECTOS.md`, `10-fusion.md`).

**9 pendientes cerrados**, cada uno con su verificación. La tabla completa y el reparto de
lo que queda están en [`../ultimo-momento/backend-reparto.md`](../ultimo-momento/backend-reparto.md).

## Los dos hallazgos que cambian una creencia del equipo

**1. El costo por llamada NO es constante entre configuraciones.** La corrida paga de
verificación gastó USD 0,9742 en 50 llamadas (USD 0,0195) contra los USD 0,0152 de la
corrida completa. `cobertura` no elige *cuántas* celdas, elige **cuáles**: con 0,50 el
top-K se queda con las 9 más grandes, cuyos prompts son más largos y se vetan más. Bajar
la cobertura **encarece** cada llamada. El tope se recalibró sobre el peor caso medido.

**2. La maqueta NO cabe en 60 segundos.** Medido: **111,6 s en frío**, 41,1 s con la
caché caliente. La fórmula del documento (`olas × 23,3 s`) subestima porque los reintentos
del veto son **secuenciales dentro de una decisión**: una ola cuesta hasta 3 llamadas de
tiempo, no 1. La maqueta baja la corrida de ~5 min a ~1 min 52, que sigue siendo la mejora,
pero el número que hay que decir en voz alta es 112 s y no 47.

## Lo que se decidió y no estaba en el guion

- **`TOPE_USD_MAXIMO` subió de $25 a $35** para no romper el invariante que el equipo ya
  había escrito en `test_el_tope_paga_la_corrida_que_promete`. Subir el techo no gasta: la
  corrida que se corre es cobertura 0,80 × 5, que costó USD 7,87 reales.
- **Se cambió ese mismo test**, y es lo único que toca un invariante del equipo. Ya no
  promete que la corrida de cobertura 1,00 cabe bajo el techo (deriva $48,13), porque la
  calibración está hecha sobre el camino caro y aplicarla a las 81 celdas es una
  sobreestimación conocida. El porqué quedó escrito en el propio test.
- **Gasto de la sesión: USD 1,03** en tres corridas (la primera se cortó sola con el tope
  viejo, que fue justamente lo que destapó el hallazgo #1).

## Lo que sigue

Dos carriles, sin un solo archivo compartido, en
[`../ultimo-momento/backend-reparto.md`](../ultimo-momento/backend-reparto.md):
**A** = reproducibilidad (`make run`, `make validate`, `scripts/`),
**B** = el modelo (α circular, `tasa_informalidad` ponderada, unidades de `ablacion.py`).
Los 6 pendientes cuestan **$0**.
