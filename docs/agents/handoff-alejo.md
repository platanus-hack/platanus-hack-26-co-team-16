# Handoff — Alejo · R1 · Datos / población

> **Tu memoria entre sesiones.** Léelo al abrir tu sesión de agente, actualízalo antes de cerrarla.
> Este archivo es solo tuyo: nadie más lo edita, así nunca da conflicto de merge.
> Tus carpetas: `data/, contracts/` · Tu rama: `rol/datos`
> Tu misión, entregables y prompt de arranque: [`docs/ROLES.md`](../ROLES.md)

## Dónde quedé

_Lo más reciente arriba. Qué existe, qué acabas de hacer, qué necesita saber tu próxima sesión para no arrancar de cero._

- 2026-08-22 (6ª sesión) — **Los 4 críticos quedaron integrados y pusheados en 2 PR.**
  - **El problema no era el contenido de los agentes, era el cableado.** Cuatro agentes
    escritos en cuatro sesiones distintas: `juez-hackathon`, `juez-tecnico`, `juez-cientifico`
    y `peeky`. Solo `juez-tecnico` estaba versionado (76aa4cf); los otros tres estaban en
    disco sin commitear y **el repo no sabía que existían**. Ninguno se reescribió: la
    personalidad, el filtro, los modos y el contrato de salida de cada uno quedaron intactos.
  - **`rol/datos` (pusheada, 3 commits nuevos hasta `adeb31a`):**
    - `8a19c51` — los 3 agentes que faltaban + sus 3 comandos + sus 3 carpetas de informes
      en `docs/agents/`. 935 líneas.
    - `adeb31a` — **la frontera cerrada.** Las referencias cruzadas eran una cadena de una
      sola dirección: cada agente nuevo nombraba a los viejos y ningún viejo sabía del nuevo;
      `juez-hackathon` no nombraba a nadie. Un juez que no conoce la jurisdicción de su
      hermano invade la ajena y produce el informe redundante. Ahora `juez-tecnico` le cede
      explícitamente la derivación y las unidades a `juez-cientifico` y se queda el
      determinismo como problema de ingeniería, y las 3 tablas de `docs/agents/*/README.md`
      tienen las mismas 4 columnas y las mismas filas (pregunta · vara · sobre la demo · salida).
  - **`docs/contrato-agentes` (rama nueva, pusheada, `c8ea869`):** `AGENTS.md` pasa de "tres
    críticos" a los cuatro, con tabla de 5 columnas y la nota de que **`peeky` no es un cuarto
    juez** — los jueces miden contra una vara externa (mercado, industria, matemática), él
    reconcilia el repo contra sí mismo. `docs/README.md` indexa también `docs/agents/peeky/`.
    **Va aparte a propósito:** docs raíz es de Juanda (`docs/ROLES.md:15`) y la regla 5 parte
    los PR que cruzan dos dueños. **Revisor: jdtorres59.**
  - **⚠️ La trampa que casi se cuela, para no repetirla:** colgué esa rama de `main` **local**,
    que estaba 8 commits detrás de `origin/main`. El PR no habría mostrado "+15 líneas" sino
    **"−2.138", borrando todo `behavior/` de Nico**. Se detectó con `git diff --stat
    origin/main..<rama>` ANTES de pushear y se rebasó con cherry-pick limpio.
    **Regla para la próxima: `git fetch` y colgar de `origin/main`, nunca de `main` local, y
    mirar el `--stat` contra el remoto antes de abrir cualquier PR.**
  - **Verificación, no reclamo:** un script recorrió los 4 comandos → 4 `subagent_type` → 4
    agentes → 4 carpetas de informes, confirmó que **ninguno tiene `Edit`** y resolvió los 40
    enlaces relativos. Todo verde.
  - **Los 4 agentes viven en DOS formatos y hay que mantener la paridad a mano.**
    `.claude/agents/<n>.md` lo lee Claude Code; `.codex/agents/<n>.toml` lo lee Codex.
    Los `.toml` estaban en disco sin versionar (103 KB) y entraron en `0d2a952`. Verifiqué
    la paridad parseando el TOML y haciendo diff línea por línea contra el `.md`: **0
    diferencias en los cuatro**. De paso apareció un bug real — `juez-tecnico.toml`
    apuntaba a `.Codex/settings.json`, que no existe (sustitución automática de más al
    portar); corregido a `.claude/settings.json`.
    **Regla: si editas un `.md`, regeneras su `.toml` en el mismo commit.** Nada sincroniza
    los dos puertos automáticamente, y dos versiones del mismo agente diciendo cosas
    distintas es exactamente el hallazgo tipo de peeky.
  - **Sigue abierto el bug de `AGENTS.md` que marcó la 5ª sesión:** dice que los agentes van
    en `.claude/agents/<nombre>/` (carpeta) y Claude Code lee archivos planos
    `.claude/agents/<nombre>.md`. **No se arregló** — está en la misma sección que edita
    `docs/contrato-agentes`, así que es una línea que se le puede pedir a Juanda en ese PR.

- 2026-08-22 (5ª sesión) — **Agente `juez-hackathon`: crítico adversarial del pitch y del repo.**
  - Nuevo: `.claude/agents/juez-hackathon.md` (el agente), `.claude/commands/juez.md` (el
    slash command `/juez`) y `docs/agents/juez-hackathon/` (donde caen los informes, con su
    README). Único cambio fuera de `data/` y `contracts/`; `.claude/` no tiene dueño en
    `ROLES.md` y `AGENTS.md` autoriza alojar agentes ahí. **Va en un PR aparte** del trabajo
    de datos.
  - **Cada corrida deja un informe en disco** (`docs/agents/juez-hackathon/AAAA-MM-DD-HHMM-<modo>.md`,
    nunca se sobrescribe) y cada informe nuevo arranca comparándose con el anterior: qué se
    cerró y qué sigue abierto. Es la única escritura que el agente tiene permitida.
  - **Para qué sirve:** entra como entraría el jurado — asume que la demo funciona y juzga si
    alguien usaría y pagaría esto. Tres modos: `/juez` (pitch, default, sobre `PLAN.md` §12),
    `/juez repo` (auditoría promesa↔disco) y `/juez qa` (simulacro interactivo, una pregunta
    por turno). Solo lee: no tiene Write ni Edit, y **tiene prohibido correr `make run` o
    `make validate`** para no quemar el presupuesto de $50.
  - **Cómo se construyó:** draft escrito con Claude, atacado por Codex (modelo distinto →
    regla 3 de `AGENTS.md`) y fusionado. Lo que Codex encontró y quedó incorporado: la regla
    de citar permitía "rigor de utilería" (ahora la cita debe *sostener* la afirmación y se
    clasifica `[disco] / [dicho] / [pendiente]`); la lista de munición conocida lo volvía un
    secretario (ahora máximo 1 de las 3 trampas puede salir de ella); y faltaba lo obvio de
    negocio (ahora tres preguntas obligatorias: comprador con nombre y cargo, qué decisión
    concreta cambia y cuándo, y si esto es producto o consultoría disfrazada).
  - **Ojo para quien lea `AGENTS.md`:** ahí dice que los agentes van en `.claude/agents/<nombre>/`
    (carpeta) pero Claude Code lee archivos planos `.claude/agents/<nombre>.md`. **Es de Juanda
    — se le avisa en el grupo, no se edita desde `rol/datos`.**

- 2026-08-22 (4ª sesión) — **El lado empleador construido: `parametros_legales.json` + `empresas.parquet`.**
  - **Diagnóstico del repo que hay que llevar al grupo YA:** `engine/` tiene **cero líneas de
    código** en `main` (solo README + MODELO.md). Lo mismo `api/`, `web/`, `tests/` y
    `scripts/`. Las únicas carpetas con código son `data/` (mía) y `behavior/` (Nico, 1.634
    líneas). **El checkpoint C3 (H+10, "corre punta a punta") no puede cerrarse**: falta el
    centro del proyecto. Ver "Bloqueado" abajo.
  - **`data/parametros_legales.json`** (nuevo, con `data/parametros_legales.py`): el costo
    legal de la formalidad tasa por tasa, cada una con norma y URL. **Mata el supuesto S1
    de `engine/MODELO.md`** ("factor prestacional ≈1,4–1,5, sin cifra exacta verificada") y
    el `ingreso * 1.5` de andamio que `behavior/arquetipos.py` usaba para el despido.
    Dos hallazgos que cambian el modelo, no solo el número:
    (a) **el factor prestacional no es un número con incertidumbre, son dos y los separa el
    tamaño del empleador** — el Art. 114-1 del ET exonera de salud patronal (8,5%), SENA (2%)
    e ICBF (3%) a quien emplee 2+ trabajadores con salario <10 SMLMV; el de UN trabajador
    paga esos 13,5 puntos. Rango real **1,384–1,583**, y el motor debe **asignarlo por firma,
    no promediarlo**. (b) **el auxilio de transporte (249.095) es costo FIJO**, 14,2% del
    salario mínimo y 0% arriba de 2 SMLMV: encarece la formalidad justo en el tramo bajo.
  - **`data/empresas.parquet`** (nuevo, con `data/construir_empresas.py`): 81 celdas de
    empleador (sector × código `P3069`). **368.491 empresas expandidas** de Bogotá,
    3.235.639 trabajadores con empleador, **964.004 cuenta propia (22,9%, código 1 = sin
    nómina, no son firmas)**. 10 de 81 celdas pierden la exoneración. Determinista byte a
    byte (verificado con sha256 en dos corridas), igual que el parquet de población.
  - **El número para el pitch:** formalizar a un trabajador cuesta **hasta 74,9% sobre su
    salario en una micro contra 40,3% en una grande**. Esa regresividad no es un parámetro
    que elegimos: sale de la frontera de la exoneración + el auxilio fijo + la clase de
    riesgo, las tres verificables contra la norma.
  - **V4 y V9 cerradas de una vez:** SMLMV 2026 = **1.750.905** (Decreto 1469 de 2025, cuya
    suspensión revocó el Consejo de Estado en julio de 2026). La moda observada en la GEIH
    era 1.750.000 → **la moda ES el mínimo**, redondeado por el encuestado. Y el aumento del
    caso demo queda verificado: 1.423.500 → 1.750.905 = **+23,0%**, no supuesto.
  - **Lo que estos archivos NO resuelven, dicho aquí para que nadie lo asuma:** la GEIH no
    observa ingresos ni márgenes de empresas, así que **el flujo de caja no se deriva de
    ella**. Queda como `MARGEN_SOBRE_NOMINA = 0.18` (rango de barrido 0,05–0,40) en UN solo
    lugar con nombre, en vez de suelto en `behavior/`. Es el supuesto #1 a barrer por R5:
    el veto lo usa como techo duro.
- 2026-08-22 (3ª sesión) — **PR #4 APROBADO Y MERGEADO a `main`. Advertencia `tamano_empresa` en `contracts/README.md`.**
  - **Segunda review del PR #4 (APPROVE, 15:08 UTC), con evidencia reproducida, no creída:**
    higiene 7/7 · demo 4 rondas / 96 vetos / $0 · dos corridas byte a byte idénticas ·
    `desde_poblacion()` contra el parquet real → 101 arquetipos, 36/34/31 por tamaño,
    `n` 1–300, 0 ids duplicados, peso total 4.199.644 (= los ocupados expandidos exactos) ·
    `EMPLEADOS_POR_CODIGO` cuadra código a código con los rangos P3069 del README.
  - **⚠️ Conflicto de reviews a resolver con cabeza fría:** la review de la 2ª sesión
    (CHANGES_REQUESTED, 14:27 UTC, "3 críticos") fue sobre el MISMO tip (`afee16d`, 13:12 UTC)
    que yo aprobé. Releyendo los críticos de esa review con su detalle completo (Memory de la
    sesión 2), **los tres siguen vigentes en el código mergeado** y van al PR top-K de Nico
    como issues (el merge ya está, no se re-litiga; ninguno rompe el demo, los tres tocan la
    calidad del número): (a) **caché envenenable** — si el modelo devuelve JSON válido al
    esquema pero con `estrategia_propuesta` vacía, `cliente.py` lo cachea ANTES de que
    `contrato.construir()` reviente con ValueError, y el reintento usa el mismo prompt →
    mismo hash → mismo veneno; los 3 intentos queman contra la entrada cacheada.
    (b) **estado congelado entre rondas** — `Arquetipo` es frozen y nunca se actualiza: una
    firma que se informalizó en R1 vuelve a la R2 con `situacion_planta: "toda formal"`; el
    historial en el prompt lo mitiga a medias pero el prompt queda contradictorio y
    `empleo_relativo` no acumula despidos entre rondas. (c) **la regla nula de la ablación
    es demasiado blanda** — formaliza a todos por construcción (con aumento 0: sobrecosto
    0 < sanción → `cumplir`), así que el "0% vs 75,6%" del candado 4 es en parte artefacto;
    endurecerla antes de presentar el candado 4.
  - **`contracts/README.md`:** bloque de advertencia (código ordinal 1–10, no headcount, con
    puntero a `EMPLEADOS_POR_CODIGO`) commiteado y pusheado en `rol/datos` (llegó a los dos
    remotos: el doble pushurl del espejo SÍ está en este clon). **PR #5 retitulado** para
    cubrir handoff + advertencia; sigue abierto **sin revisor** — no auto-mergear, pedirlo.
  - **Borrador del mensaje al grupo listo** (quedó en el chat de la sesión): aval ADR 0008
    con la precisión de Nico + aviso de contratos congelados para `realizacion` en
    `decision.json` y `trimestre`/`n_vetos`/`n_fallback` en `ronda.json`. **FALTA ENVIARLO.**
- 2026-08-22 (2ª sesión) — **PR #2 MERGEADO. Review de PR #4 (Nico) publicada: CHANGES_REQUESTED.**
  - Revisé `behavior/` completo + pasada profunda verificada. 3 críticos (caché envenenado
    por respuestas vacías `capa.py:179`, estado estático entre rondas `rondas.py:189`,
    ablación sesgada `ablacion.py:60`), 3 de integración con `engine/` y 5 menores.
    El detalle está en la review del PR #4.
  - **Me están esperando para el aval del ADR 0008** (rama del trabajador que acepta/rechaza
    informalizarse) — pendiente de Alejo y Nico; FLUJO/UML ya lo dan por hecho. Leerlo y decidir.
  - Inconsistencias detectadas en los docs mergeados del PR #3 (de Manuel), avisadas a Alejo
    para pasar al grupo: `docs/UML.md` usa `arquetipo_id` contra los contratos congelados
    (`agente_id`/`arquetipo`); cifra de inspectores contradictoria (ADR 0006 dice pendiente/904,
    handoff-manuel dice resuelta/1.300 OIT); `docs/README.md` con edición a medio merge.
- 2026-08-22 — **Pipeline completo entregado en `rol/datos` (PR #2 a `main`):**
  - **C1 ✅** GEIH 2026 enero–junio descargada del catálogo 900 del ANDA (descarga directa,
    sin login). Trazabilidad con URL + sha256 en `data/raw/DESCARGA.json`.
  - **Contratos ✅** `contracts/agente.json|decision.json|ronda.json` + README con la
    procedencia campo→variable GEIH verificada contra el diccionario del ANDA.
  - **`data/poblacion.parquet` ✅** 6.692 agentes de Bogotá (AREA=11), 4.199.644 ocupados
    expandidos, 67 arquetipos preliminares. Esquema = contrato. Incluido en el repo
    (107 KB; excepción en `data/.gitignore` al `*.parquet` del raíz — **avisado en el PR
    para que Juanda lo valide**).
  - **`data/momentos.json` ✅** informalidad total 30,6% (proxy pensión), por sector y por
    tamaño (micro 66,7% / pyme 10,6% / grande 0,8%), percentiles salariales, terciles.
  - **V9 (hallazgo para Juanda):** el spike salarial EXISTE — 12,1% de la masa salarial de
    Bogotá exactamente en 1.750.000 COP (moda observada; confirmar = SMLMV 2026 con V4).
  - **V2 ✅ resuelta: NO.** 0 `DIRECTORIO` repetidos entre meses en microdatos públicos →
    no hay transiciones observables de la misma persona. Se calibra contra historia
    agregada (plan B previsto). Bonus: el pooling de 6 meses no duplica personas.

## En qué estoy trabajando

- [x] Descarga GEIH (C1) · contratos (H+4) · parquet + momentos (H+8) · README · V2
- [x] Review cruzada del PR #4 de Nico — cerrada: APPROVE con evidencia reproducida, mergeado
- [x] Advertencia `tamano_empresa` en `contracts/README.md` (en PR #5, abierto)
- [ ] **Enviar el mensaje al grupo** (borrador listo): aval ADR 0008 + aviso de cambio
      aditivo en contratos (`realizacion` en `decision.json`; `trimestre`/`n_vetos`/
      `n_fallback` en `ronda.json`). Tras el ok del grupo: hacer los dos cambios en un PR.
- [ ] Llevar los tres hallazgos latentes del PR #4 (caché envenenable por estrategia vacía,
      estado congelado entre rondas, regla nula de la ablación demasiado blanda) al PR
      top-K de Nico como comentarios.
- [ ] Definir con Nico los arquetipos FINALES (~H+14). Hoy: 67 celdas
      sector×tamaño×formal×tercil con colapso <60 obs. Mi propuesta (dejada en la review
      del PR #4): que `behavior/desde_poblacion()` agrupe por MI columna `arquetipo` en
      vez de re-derivar cortes propios. Cambiar del lado mío = una función en
      `data/construir_poblacion.py` y regenerar.
- [x] Empresas explícitas para el veto de Manuel → `data/empresas.parquet` (4ª sesión).
- [x] Costo legal de la formalidad con fuente → `data/parametros_legales.json` (4ª sesión).
- [x] Los 4 críticos internos versionados, con frontera cerrada y declarados en `AGENTS.md`
      (6ª sesión, 2 PR: `rol/datos` y `docs/contrato-agentes`).
- [ ] **Pedirle a Juanda que `AGENTS.md` mencione los dos puertos de agentes** (`.claude/agents/*.md` y `.codex/agents/*.toml`) y la regla de regenerarlos juntos.
- [ ] **Pedirle a Juanda en el PR `docs/contrato-agentes`** que corrija la línea de
      `.claude/agents/<nombre>/` → `.claude/agents/<nombre>.md`. Es suya; no se toca desde
      `rol/datos`.
- [ ] **Proponer al grupo un 4º contrato `contracts/empresa.json`** para `empresas.parquet`.
      NO lo agregué unilateralmente: los contratos están congelados desde H+4 y aunque esto
      es un archivo nuevo (no un cambio a los tres existentes), la regla dice avisar antes.
      El esquema ya está documentado en `data/README.md`.

## Bloqueado / esperando a alguien

- 🔴 **Manuel / `engine/`: cero líneas de código en `main`.** Es el camino crítico de todo lo
  que sigue y el archivo que AGENTS.md manda leer primero (`engine/rondas.py`). El spec
  (`engine/MODELO.md`) está excelente y completo — archivo, función, test y supuesto por
  concepto — pero no hay implementación. **C3 (H+10, "corre punta a punta") no se puede
  cerrar.** Ya no me bloquea a mí: `poblacion.parquet`, `empresas.parquet` y
  `parametros_legales.json` están listos y son todo lo que el motor necesita de datos.
- 🔴 **Dani / `web/`: cero líneas.** Sin interfaz no hay demo, y C3 la incluye.
- **PR #5 espera un revisor distinto de mí** (regla 3). Es docs-only (mi handoff + la
  advertencia en `contracts/README.md`); cualquiera del equipo puede mergearlo en 2 min.
- Nico: la conversación de arquetipos (mi 67 vs su 101) sigue pendiente — para el standup.
  Ahora hay un motivo más para cerrarla: `behavior/arquetipos.py` calcula `flujo_caja` y
  `costo_despido` con coeficientes de andamio que ya tienen reemplazo con fuente en
  `empresas.parquet`. Que los lea de ahí en vez de recalcularlos.

## Supuestos que tomé

_Todo greppable con `# SUPUESTO:` en `data/construir_poblacion.py`; R5 los recoge en VALIDATION.md._

- **`formal` = cotiza a pensión (`P6920==1`; pensionados `==3` cuentan como formales).**
  Proxy de la definición OIT del DANE (la oficial cruza más módulos). El sesgo se mide en
  el candado 1: nuestro 30,6% vs la serie oficial de informalidad de Bogotá.
- **`P3069` faltante (independientes) → tamaño 1 ("trabaja solo")**, el caso modal.
- **Registros sin `INGLABO` se descartan, no se imputan** (conteo en `momentos.json`).
- **Pooling 6 meses con `FEX_C18/6`** — práctica estándar GEIH para promedios de período;
  verificado que ningún hogar aparece en dos meses.
- ~~**La moda salarial (1.750.000 COP) se reporta como observada**~~ — **resuelto en la 4ª
  sesión:** el SMLMV 2026 verificado es 1.750.905 (Decreto 1469 de 2025). La moda observada
  es el mínimo redondeado por el encuestado.

_Nuevos en `data/parametros_legales.py` y `data/construir_empresas.py`:_

- **Clase de riesgo ARL por sector** — el Decreto 1607 clasifica a 4 dígitos de CIIU y
  nuestros sectores son agregados a 2; se asigna la clase modal. Es el parámetro más flojo
  de los legales y el de menor impacto (mueve el factor entre 0,5 y 7 puntos).
- **Uno de los ocupados del establecimiento es el dueño**, así que empleados = personas − 1.
  Importa en el código 2 (2–3 personas): ahí la firma emplea a 1 o 2 y con 1 pierde la
  exoneración del Art. 114-1.
- **Antigüedad promedio de 3 años** para convertir el Art. 64 CST en un costo por trabajador
  (la GEIH pública no trae antigüedad en el módulo que usamos): 70 días = 2,33 meses.
- **Punto medio 300 para el código 10 ("201+")** — el rango es abierto y no tiene punto medio.
- **`MARGEN_SOBRE_NOMINA = 0.18`** — la GEIH no observa caja de empresas. Heredado del
  andamio de `behavior/` para no mover el demo al introducir la tabla. **Es el supuesto #1
  a barrer**: el veto lo usa como techo duro. Rango sugerido 0,05–0,40.
