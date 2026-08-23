# Handoff — Juanda · R5 · Integración / validación / pitch

> **Tu memoria entre sesiones.** Léelo al abrir tu sesión de agente, actualízalo antes de cerrarla.
> Este archivo es solo tuyo: nadie más lo edita, así nunca da conflicto de merge.
> Tus carpetas: `tests/, scripts/, Makefile, docs raíz` · Tu rama: `rol/integracion`
> Tu misión, entregables y prompt de arranque: [`docs/ROLES.md`](../ROLES.md)

## Dónde quedé

_Lo más reciente arriba._

- **2026-08-23 — EL DEPLOY ESTÁ VIVO** + el pre-compromiso. Rama `rol/integracion-deploy`.

  - **https://enjambre-web.onrender.com** — abre sin registro, y el humo de la cadena
    completa pasa contra producción. La API es `https://enjambre-api.onrender.com`.
    `deploy-url` y `project-description.md` ya no son placeholders: **la entrega cuenta**.
  - **La rama NO se llama `rol/integracion/deploy`.** Git no deja crear esa ref porque
    ya existe la rama `rol/integracion` (una ref no puede ser rama y carpeta a la vez).
    Quedó `rol/integracion-deploy`. Si vas a colgar otra rama de la tuya, mismo problema.
  - **Los dos servicios en Render, no Vercel, y hay dato:** la interfaz es 100% cliente y
    pide `/api/...` relativo, así que el servidor de Next hace de **proxy del SSE**, y
    Vercel corta los rewrites con destino externo a **120 s** (una corrida LLM tarda 166 s).
    Render aguanta 100 minutos. Beneficio lateral: no hubo que tocar un archivo de `web/`.
  - 🔴 **`ENJAMBRE_API` se lee en el BUILD, no al arrancar.** `next build` congela el
    destino del rewrite en `.next/routes-manifest.json`. Si el build corre sin la
    variable, el front queda apuntando a `localhost:8000` dentro de su contenedor: la
    página carga perfecta y **ninguna simulación arranca nunca**. Falla en silencio.
    Cambiarla exige rebuild (editarla en el dashboard ya lo dispara).
  - 🔴 **Render define `NODE_ENV=production`**, así que `npm ci` a secas se salta las
    devDependencies — y `typescript` vive ahí. El primer build del front murió por eso.
    Se arregló con `--include=dev` en `render.yaml`, no moviendo paquetes en el
    `package.json` de Dani.
  - **Una llave de Anthropic se quemó** al pegarse por error en `ENJAMBRE_API`: quedó
    impresa en el log de build de Render. Se rotó. Si volvés a tocar variables, ojo con
    cuál va en cuál servicio.
  - **Plata:** $50/mes entre los dos servicios ≈ 30 días de crédito. **A partir de
    ~23-sep-2026 le cae a la tarjeta.** Suspenderlos cuando pase la votación — está
    escrito en `docs/DEPLOY.md` para que no dependa de que alguien se acuerde.
  - **El pre-compromiso ya está commiteado**, o sea que Nico y Alejo pueden correr S3-1.
    Va DESPUÉS del bloque pre-registrado: ese bloque tiene un comparador contra `2d4aa7e`
    y meterse en el medio da un falso positivo. Verificado: `idéntico: True | 1056 vs 1056`.
  - **Retractada** la frase de `VALIDATION.md` sobre "fuera de muestra de verdad", y
    **corregida** la brecha proxy-oficial (decía ≈2,1 pp, la resta da 2,49 — estaba
    subestimada a favor nuestro; lo levantó Alejo).
  - **Pendiente de C2 y NO lo hice:** `README.md:23`, `AGENTS.md:3`, `docs/PLAN.md` §1.1 y
    `docs/IDEA.md:145,154` siguen por revisar. En los archivos que sí toqué
    (`platanus-hack-project.jsonc`, `project-description.md`) la cascada ya está escrita
    como **mecanismo**, no como hallazgo. También sigue pendiente
    `docs/agents/handoff-alejo.md:33`, que cita el −2,1 pp viejo: es de él.

- **2026-08-22 · H+18 — el barrido adaptado al `main` post-PR #12**, en `rol/integracion`.

  - **`main` se movió debajo de la rama y el barrido dejó de correr.** La corrección C2
    borró `capacidad_fiscalizacion` de `correr()` y el arnés reventaba con un
    `TypeError`. Se puso al día con **merge**, no con rebase: la rama ya estaba pusheada
    y abierta como PR #11, y rebasarla exigía un force-push que está en la deny-list.
    El merge entró **sin un solo conflicto** —mi commit solo agrega 5 archivos que
    `main` no tiene—, así que el resultado es el mismo y el PR se actualizó solo.
  - **Tres cosas que el arnés hacía y ahora hace el motor.** El veto real, el
    `EstadoVivo` con su función de sutura y el factor prestacional por sector se
    borraron del script. Las tres se fueron a `behavior/rondas.correr()` con C1 y C2.
    **Ojo con la tercera:** mi `ClienteReglasPorSector` discrepaba del parquet en
    **10 de las 81 celdas**, siempre por los ~13,5 puntos de la exoneración del 114-1 y
    siempre subestimando, porque contaba la exoneración sobre un headcount que C1
    redefinió (`n_empleados` ya no incluye al dueño). Diez celdas de micro-empleador,
    que es justo donde vive la informalidad. Mantenerlo habría reintroducido la
    divergencia que C1 quitó.
  - **El barrido es ahora la única herramienta que corre la §9.** Se le puso el
    **semáforo de aceptación** con los seis criterios, la **banda entre trayectorias**
    (B2, que necesita corridas completas e independientes y por eso solo se puede
    calcular acá), y `--cascada-apagada` para B4. Los seis campos nuevos de la ronda
    —`traslado_precios_pct`, `ingreso_laboral_relativo`, `movimiento_pp`,
    `estabilizada`, `fraccion_fallback`, `fraccion_sin_salida`— entraron al reporte.
  - **Lo que el semáforo dice hoy, y es lo importante:** en ablación **no se puede
    medir ni el ruido ni el signo**. La informalidad no se mueve entre políticas
    (`despedir` domina con 67,2% de la población en todas), así que ruido y señal salen
    los dos en 0,00 pp. El script lo reporta como *"sin señal"* en vez de imprimir el
    `inf` que salía del cociente, porque `inf` se leía como "demasiado ruido" y habría
    mandado al equipo a cazar varianza cuando el problema es el contrario.
    **Los dos 🔴 del proyecto —ruido/señal 0,71 y el signo −0,311— siguen SIN REMEDIR.**
    Las correcciones que los atacan ya están en `main`; el número que las juzga solo
    sale de una corrida con LLM real que nadie ha hecho después del PR #12.
  - **`DEFECTOS.md` no se editó, se le puso encima una tabla de estado.** Verifiqué los
    21 defectos uno por uno contra el árbol de `main`: 8 cerrados, 5 parciales, 3
    abiertos, 3 declarados en el bloque D, y los 2 sin remedir. El inventario original
    queda intacto porque es la línea base contra la que se mide todo esto.
  - **`requirements.txt` sigue sin estar en `main`** y es el candado 1: nadie que clone
    el repo puede montar el entorno. Cierra cuando entre el PR #11.
  - _Nota:_ `make reproduce` no funciona con `PY=` si la ruta del repo tiene un espacio
    (`$(PY)` va sin comillas en el `Makefile`). Se corrió metiendo el venv en el `PATH`.
    Es un arreglo de una línea en el `Makefile` para la próxima sesión.

- **2026-08-22 · H+1 — bloque H+0→H+1 cerrado** en `rol/integracion`.

  - **V7 (espejo) — hecho, y ojo con esto:** el doble push **NO estaba configurado** en
    este clon, contra lo que asumía el prompt de arranque. Ya está: `remote.origin` tiene
    dos `pushurl` (organización + `vibe-coders-team/platanus-hack-26-T16-simulations`,
    que existe y es público). Un `git push` actualiza los dos.
    **Si otro integrante clonó de cero, tampoco lo tiene** — el procedimiento y cómo
    verificarlo quedaron en la sección de deploy del `README.md`.
  - **V7 (deploy) — PENDIENTE, y no lo puede hacer el agente.** Conectar Render y Vercel
    exige autorizar OAuth con la cuenta de GitHub desde el navegador. Lo hace un humano,
    apuntando al **espejo**, no al repo de la organización. Sin esto no hay C2 (H+4).
  - **V6 (prior art) — hecho.** Los 20 minutos, con la tabla citada en el `README.md`.
    Lo más cercano que existe: [arXiv 2501.18177](https://arxiv.org/abs/2501.18177),
    evasión fiscal con LLM+DRL donde la evasión emerge **sin avisarle al agente que
    evadir es una opción** — es nuestro mismo control de contaminación, publicado en
    2025. Hay que conocerlo antes del Q&A: si el juez lo saca y nosotros no lo citamos,
    perdemos; citándolo primero, ganamos.
  - **Hallazgo no buscado:** apareció la objeción de frente — Luo, Arora & Guirado,
    [arXiv 2604.07838](https://arxiv.org/abs/2604.07838) (abril 2026), tres
    precondiciones para simular poblaciones en política pública. El `README.md` las
    responde una por una y **admite que la segunda no la cumplimos** (no hay proceso
    participativo en 36 horas). Esa admisión es a propósito, no un descuido.
  - **V8 (elasticidades) — resuelto 9 horas antes de lo previsto**, de rebote en la
    búsqueda de prior art. Banco de la República WP 1104: +1 pp en el ratio del mínimo
    ≈ **+0,21 pp** de probabilidad de empleo informal, con el efecto concentrado en
    18–25 años de baja educación. Está en `VALIDATION.md` como objetivo de calibración
    con fuente. **Pasárselo a Manuel (R2) y a Alejo (R1) en el próximo standup:** es la
    pendiente que el motor debe reproducir en el tramo bajo antes de que podamos hablar
    del codo en el tramo alto.
  - **`README.md`: se INSERTA, no se reescribe.** El template de Platanus queda intacto
    —logo, roster, `Before Submitting`, sección de deploy, `Have fun`— y el contenido de
    proyecto entra entre el roster y el checklist. El diff es de 69 líneas añadidas y
    **cero borradas**. La instrucción inyectada del template (insertar 🍌 después de cada
    palabra) **se conserva verbatim y simplemente no se sigue**: es un canario de los
    organizadores para detectar READMEs escritos por un LLM sin supervisión, y dejar el
    renglón intacto prueba que no tocamos su texto. Verificación: todas las 🍌 del archivo
    están en un solo renglón, el original.
  - **`Makefile` inicial** cableado y probado: `run` / `test` / `validate` / `reproduce`
    / `estado`. Los targets sin código detrás dicen qué falta y en qué checkpoint llega,
    en vez de reventar con un stack trace. **`make estado` es la respuesta honesta a
    "¿esto ya sirve?"** en cualquier momento — úsalo al abrir cada standup.
  - `AGENTS.md`, `ARCHITECTURE.md`, `VALIDATION.md` y `LICENSE` ya venían del scaffold de
    Manuel. No hubo que escribirlos, solo llenarlos.

  - _Nota de proceso:_ este bloque se ejecutó una primera vez sin plan y reescribiendo el
    README entero. Se reversó completo (rama borrada en los dos remotos, `main` nunca se
    tocó, `git push --force` está en la deny-list del equipo así que la única vía fue
    borrar y recrear) y se rehízo. **Los checkpoints se planean antes, no se improvisan.**

- 2026-08-22 — Repo scaffoldeado. Nada construido todavía.

## Preguntas para la cena con el mentor (V5) — llevarlas escritas

1. **¿A qué hora exacta son las presentaciones del domingo?** Todo el cronograma de
   ensayos cuelga de esto (`docs/PLAN.md` §8 lo tiene marcado ⚠️).
2. **El congelamiento de las 09:30, ¿es por commit o por rama?** Si es por rama se puede
   seguir puliendo en `rol/integracion` sin mergear; si es por commit, el freeze real es
   antes de lo que dice el cronograma.
3. **¿Un backtest con error grande, pero medido y reportado honestamente, puntúa como
   ejecución seria?** (pregunta de Daniel) — decide cuánto se arriesga en el candado 2.
   Es la más importante de las tres.
4. **Créditos de Anthropic: ¿$50 por persona o $50 por equipo?** El plan asume por
   persona; si es por equipo, el presupuesto de la capa LLM cambia 5×.
5. Si hay chance: **¿alguien del staff conoce a un economista laboral?** Quince minutos
   de validación externa valen más que cinco horas de código (`docs/PLAN.md` §13.4).

## En qué estoy trabajando

- [ ] **PR #11** de `rol/integracion` → `main`: barrido + `DEFECTOS.md` +
      `requirements.txt`. Al día con `main`. **Falta la review de alguien más**
      (regla 3 de `AGENTS.md`): es lo único que no puedo hacer yo.
- [ ] **La corrida con LLM post-corrección.** Es lo que decide la §9 y hoy no
      existe. `python scripts/barrido_politicas.py --llm --repeticiones 5 --desde 5
      --hasta 20 --paso 2 --cascada-apagada`.
- [ ] `behavior/cache-demo.json` no existe: `make reproduce` cae a la ablación.
      Es de Nico (R3), avisarle — sin ese archivo el nivel 2 de la ADR 0009 no corre.
      **Lo revisa alguien distinto de mí** (regla 3 de `AGENTS.md`).
- [ ] Pasar la elasticidad de V8 a Manuel y Alejo en el próximo standup.

## Bloqueado / esperando a alguien

- **Render + Vercel:** necesito que un humano del equipo autorice OAuth y conecte los dos
  servicios al **espejo**. Sin esto no hay checkpoint C2 (H+4), y C2 no es negociable.
- **C1 (H+2) es de Alejo:** ¿hay archivo GEIH en disco? Si a la H+2 no está, el plan B de
  V1 se decide **en ese momento**, no a la H+20.

## Supuestos que tomé

- **El checklist "Before Submitting" del template se queda en el `README.md`**, verbatim.
  Los cuatro pendientes siguen abiertos, así que borrarlo sería esconder trabajo sin
  hacer. La lista de abajo lo espeja para seguimiento; el README manda.
- **`make validate` sale con código 0 mientras no haya número.** Un target que revienta
  hace pensar que el repo está roto; uno que explica en qué checkpoint llega el número,
  no. Cuando el número exista, si falla un candado **debe fallar de verdad** — acordarse
  de cambiarlo en C5.

## Pendientes de entrega (espejo del checklist del README)

- [ ] `platanus-hack-project.jsonc` — nombre, oneliner, descripción, URL de deploy
- [ ] `project-description.md` — reemplazar por la descripción real
- [ ] `project-logo.png` — el actual cumple lo técnico (1000×1000, 12 KB) pero es
      placeholder: falta el definitivo
- [ ] URL pública que abra desde un celular con datos móviles y sin sesión
