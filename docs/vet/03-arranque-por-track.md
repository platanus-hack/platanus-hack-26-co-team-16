# Prompts de arranque, uno por track

> **Para qué existe.** Que cinco personas abran diez agentes en paralelo sin pisarse. Cada bloque es
> autocontenido: se copia, se pega en una sesión nueva, y el agente arranca sin haber leído nada más.
>
> **Antes de pegar cualquiera de estos:** `git fetch origin && git checkout main && git pull --ff-only`.

## Lo que va en TODOS los prompts

Estas cinco reglas se cumplen sin excepción y el agente las tiene que tener adentro:

1. **No toques carpetas ajenas.** Si tu arreglo necesita un archivo de otro dueño, **para y avísale**.
   No lo edites "de una" porque son las 3am.
2. **Nadie pushea a `main`.** Rama propia → PR → lo revisa **otra persona** (ver la tabla de revisores).
3. **Cero datos inventados.** Todo supuesto se marca donde se toma, con `# SUPUESTO:` en Python y
   `// SUPUESTO:` en TypeScript. `grep -rn "SUPUESTO:"` es el informe de honestidad del proyecto.
4. **Al LLM jamás se le nombra la política.** Solo la mecánica ("tu costo laboral por empleado formal
   sube X%"). Nunca "salario mínimo", ni "decreto", ni un año.
5. **`git diff --stat` antes de decir que algo se hizo.** El reporte de un agente es un reclamo, no evidencia.

## Las tres dependencias duras

Romperlas traba a todo el mundo:

- **S1-1 antes que S2-2.** Pedir 5 paráfrasis sin arreglar el `round()` revienta la corrida entera.
- **El pre-compromiso commiteado antes que S3-1.** O el número nuevo no vale nada.
- **C1 antes que C2.** Primero se define qué se afirma, después se propaga.

---

## Track NICO · `behavior/` · rama `rol/conductual`

```
Trabajas en `behavior/` y SOLO en `behavior/`. Rama: rol/conductual. Tu PR lo revisa Dani.
Lee primero: docs/vet/01-decisiones-y-tracks.md y docs/vet/00-hallazgos.md.

PRIMERO, y desbloquea a Dani, así que va antes que todo lo tuyo:
- S1-1: `behavior/rondas.py:120` hace `round(v, 4)` sobre todos los valores de `banda` salvo booleanos,
  y `banda.tipo` es un string. Cualquier corrida con n_parafrasis>=2 revienta con TypeError al
  serializar la primera ronda. Arréglalo y escribe el test que lo hubiera cazado.
- C3: `behavior/cliente.py:_llamar` (~línea 197) no fija `temperature`. Fíjala en 0. Razón: AGENTS.md
  declara que la banda sale de N>=5 paráfrasis y NUNCA de temperatura; hoy la temperatura está suelta,
  así que parte de la dispersión viene de donde el proyecto juró que no vendría.
- V-1: alguien cambió MODELO_MASA a claude-sonnet-5 y la clave de caché incluye el modelo, así que la
  caché quedó FRÍA. Mide cuánto cuesta y cuánto tarda UNA corrida ahora, con parafrasis=1 y con
  parafrasis=5. Reporta las dos cifras antes de que Dani cablee el front. Avísale a Manuel si `tope_usd`
  (api/servidor.py:89, hoy 3.0) se queda corto.

DESPUÉS:
- S3-6: `behavior/README.md:86-90` y `:309-316` afirman "el dato A1 aguanta, +28 a +45 pp".
  VALIDATION.md ya declaró eso falsado. Quítalo o reescríbelo contra el dato observado.
- S1-2: `_banda` (rondas.py:551-563) indexa `decisiones[i]` hasta el máximo, así que
  `parafrasis_por_peso=True` da IndexError seguro. La bandera está muerta.
- S1-3: solo existen 5 archivos en `prompts/parafrasis/` pero la API acepta hasta 9 y
  N_PARAFRASIS_MAX=9. Pedir 6 mata la corrida. Cuadra los dos números.
- S1-8: `capa.py:188` le pasa al agente `arquetipo.n_trabajadores`, la planta ORIGINAL, mientras el veto
  usa `planta_viva()`. En la ronda 2 el agente propone despedir sobre gente que ya despidió y el veto lo
  rechaza, empujándolo al fallback.
- S3-1 (con Alejo): la corrida usa `poblacion.parquet` (2026) y arranca la ronda 0 del dato POST-política.
  `poblacion_2025.parquet` existe y nadie lo lee. NO CORRAS ESTO hasta que Juanda haya commiteado el
  pre-compromiso: el número nuevo reemplaza al viejo salga como salga.

SI SOBRA: S1-11 (`desde_poblacion` muerta), S1-13 (ronda 0 estabilizada), S1-14 (el umbral de fallback
del 5% vive solo en el CLI, y la corrida de reglas ya lo supera con 7,4%), S1-15 (`renegociar` está en el
menú del agente y no mueve ningún agregado), S1-16, S1-10 (el comentario de los 4 sectores es falso:
son 9 en data/empresas.parquet).
```

---

## Track DANI · `web/` · rama `rol/interfaz`

```
Trabajas en `web/` y SOLO en `web/`. Rama: rol/interfaz. Tu PR lo revisa Manuel.
Lee primero: docs/vet/01-decisiones-y-tracks.md y docs/vet/00-hallazgos.md.

ARRANCA YA, no dependen de nadie:
- S2-1 🔴: la demo se ve IDÉNTICA con LLM y con `?modo=reglas` (la ablación determinista sin ningún
  LLM), con citas entre comillas incluidas. El evento `inicio` YA trae `modo` (api/servidor.py:213) y
  `flujo.ts:44` solo lo manda a console.info. Guárdalo en el almacén y muéstralo en pantalla. Un juez
  tiene que poder ver con qué corrió.
- S2-5 🟠: la pantalla salta de "preparando" a "Ronda 3/3". Causa raíz: `motorVisual.ts:79-81` toma
  `rondas[length-1]` y DESCARTA las intermedias, y todos los paneles leen `ultimaRonda()`. Con caché
  caliente las 3 rondas llegan en la misma ráfaga. Arreglo: una cola de rondas pendientes en MotorVisual
  que se consuma una cada DURACION_TRANSICION, y los paneles leyendo la ronda mostrada.
  OJO: la caché acaba de quedar fría por el cambio de modelo, así que el síntoma puede no aparecer hoy.
  El bug sigue ahí igual y vuelve en cuanto la caché se caliente. No lo cierres por observación.

DESPUÉS DE QUE NICO MERGEE S1-1 (hoy n_parafrasis>=2 revienta):
- S2-2 🔴: `flujo.ts:35` arma el query solo con `aumento_pct` y `seed`, así que nunca se pide
  parafrasis>1 y la banda SIEMPRE sale degenerada y la curva tiene área cero. Pásale parafrasis=5.
  Pídele a Nico el costo y el tiempo medidos antes de fijar el número: la caché está fría y el modelo
  cambió a Sonnet 5.

DESPUÉS:
- S2-7: `fraccion_fallback` y `sin_salida` viajan en el contrato (serializar.py:184-191) y NINGÚN panel
  los lee. Es la primera cifra que pide un juez técnico y hoy solo vive en la terminal.
- Panel de procedencia: por cada métrica de la pantalla, si es DATO GEIH, NORMA citada, CALCULADO o
  SUPUESTO. Es la respuesta a "¿de dónde se alimenta esto?" sin que la tengan que preguntar.
- S2-3: `Personas.tsx:194` tiene un `+0.15` inventado que infla los puntos ámbar de "jornada recortada",
  y la cifra real está justo al lado en Metricas.tsx. Los dos números no cuadran.
- S2-4: `Onda.tsx:57` salta de radio 0 a ~5 con una brecha de 0,05pp. Es el elemento más grande de la
  pantalla y ninguna leyenda dice qué mide.
- S2-6: el panel "relato de la corrida" muestra un subconjunto filtrado (top-25 por peso) y podado, sin
  decirlo. Ponle subtítulo.
- S2-10: `grep SUPUESTO` sobre web/ devuelve UNA línea. Hay al menos 8 constantes de decisión sin marcar.
- S2-11 (barra de carga falsa hasta 82%), S2-12 (el "+23,0%" está hardcodeado mientras
  `piso_salarial_anterior` viaja por el cable y se descarta).

TUYO Y NADIE MÁS LO TOCA: la línea de tiempo explícita.
```

---

## Track JUANDA · `tests/` `scripts/` `Makefile` docs raíz deploy · rama `rol/integracion`

```
Trabajas en tests/, scripts/, Makefile, documentos raíz y el deploy. Rama: rol/integracion.
Tu PR lo revisa Manuel. Lee docs/vet/01-decisiones-y-tracks.md y docs/vet/00-hallazgos.md.

ESTO ES LO PRIMERO Y NO ESPERA A NADIE:
- El DEPLOY. `platanus-hack-project.jsonc:22` sigue en "deploy-url": "<FILL THIS>" y
  `project-description.md` sigue siendo el placeholder de la plantilla. SIN URL DESPLEGADA LA ENTREGA NO
  CUENTA. Es lo único que puede fallar por razones que no controlamos (build, DNS, límites) y
  descubrirlo a las 06:00 no tiene arreglo.
- C1 + el pre-compromiso, en el MISMO commit y ANTES de que Nico corra S3-1:
  (a) `VALIDATION.md:159-163` afirma "es fuera de muestra de verdad: la población se instancia con 2025
      y el modelo nunca ve 2026". El código lo contradice y el propio documento lo admite cuatro
      párrafos más abajo. Retracta la frase y declara qué es realmente.
  (b) Escribe y commitea: cuando S3-1 se arregle, el número nuevo REEMPLAZA a EL NÚMERO, salga como
      salga, y los dos quedan publicados con su hash. Esto va antes de correr o no vale nada.
  NO REESCRIBAS el bloque de las dos ramas del pre-registro: cópialo. Ya pasó una vez y quedó un falso
  positivo.

DESPUÉS (C2, la coherencia; behavior/README.md lo hace Nico, no tú):
- README.md:23, AGENTS.md:3, docs/PLAN.md §1.1, docs/IDEA.md:145,154 y el oneliner de
  platanus-hack-project.jsonc siguen vendiendo la cascada como HALLAZGO. VALIDATION.md la declara
  falsada. Los jueces leen el repo con agentes y esto se encuentra en 30 segundos.
- AGENTS.md:11 dice "si solo lees un archivo: engine/rondas.py, es donde vive la tesis". ESE ARCHIVO NO
  EXISTE. `engine/MODELO.md` cita otros cinco módulos inexistentes. Apunta a algo real.

DESPUÉS:
- S3-9: hay un SEGUNDO episodio de backtest (2024→2025: +2,63pp con alza de 9,5%, dirección OPUESTA al
  de 2026) medido, versionado e impreso por validate.py, pero AUSENTE de VALIDATION.md. Es el dato que
  convierte "el modelo erró un año" en "el modelo erra sistemáticamente". Va en los dos sentidos y hay
  que ponerlo.
- S3-2: el 35,60% (mitad del argumento de robustez) no tiene fuente en ninguna parte del repo.
- S3-7: `tests/test_reproducible_en_clon_limpio.py:74-88` pasa POR CONSTRUCCIÓN: en un clon limpio los
  dos lados que compara recorren la misma rama. Solo prueba algo en tu máquina, que es donde el bug
  original se escondió.
- S3-10: `scripts/validate.py:66-76` agrega la tercera razón de bloqueo de G1 INCONDICIONALMENTE, así
  que G1 nunca puede dar verde aunque el determinismo se cierre.
- S3-4: G3 compara la corrida sin política contra `momentos.json` (2026, POST-política) en vez de
  `momentos_2025.json` (34,64%, que está versionado y no se usa).
- La lámina de límites: qué NO modela (productividad, demanda, capital, contrataciones), que la tasa de
  desempleo no es computable, que los cuenta propia están fuera de la grilla, y la DIRECCIÓN DEL SESGO.
  Va ADENTRO del pitch, no en el Q&A.
- S3-5, S3-8, S3-11.
```

---

## Track MANUEL · `engine/` `api/` · rama `rol/backend`

```
Trabajas en `engine/` y `api/`. Rama: rol/backend. Tu PR lo revisa Juanda.
Lee docs/vet/01-decisiones-y-tracks.md y docs/vet/00-hallazgos.md.

ARRANCA YA:
- S2-9: `api/serializar.py:74` sirve `rondas_totales: 4` como literal y `behavior/rondas.py:181` tiene
  otro default de 4, y la API nunca se lo pasa. Cuadran hoy por casualidad. El día que cambie uno, la
  barra de tiempo del front miente en silencio. Fuente única.
- S1-4: `api/servidor.py:86` expone `seed` como perilla de usuario y el seed de behavior es DECORATIVO
  (medido: seed 42 y seed 99 dan trayectorias idénticas). O la quitas o la rotulas diciendo qué hace hoy
  y por qué. Una perilla que no hace nada es peor que no tenerla si un juez la mueve.
- V-1: la caché quedó fría por el cambio a Sonnet 5. Habla con Nico: si una corrida con parafrasis=5 no
  cabe en `tope_usd=3.0` (servidor.py:89), súbelo con criterio, no a ojo.

DESPUÉS:
- S1-7: `banda_entre_trayectorias()` (rondas.py:590) es la banda HONESTA (el propio código dice que la
  intra da 0,0pp contra 22,5pp de la real) y NO existe en el camino del producto: la API corre una sola
  trayectoria. La pantalla recibe la intra-ronda.
- S2-8: `Metricas.tsx:27,45` calcula "$X billones/mes · proxy de PIB laboral" EN EL NAVEGADOR, fuera de
  la capa que declara "cero números inventados". Es la única cifra en pesos absolutos de la pantalla y
  la más citable en un pitch. Muévela a serializar.py con su `# SUPUESTO:`. Coordina con Dani.

TU VERIFICADOR, y córrelo cuando cierres la primera oleada: el prompt 16 re-apuntado (está en
platanus-hack-26-simulations/reencuadre/16-prompt-de-cuestionamiento.md, con las tres preguntas
re-apuntadas en docs/vet/01-decisiones-y-tracks.md) y `juez-hackathon`.
```

---

## Track ALEJO · `data/` `contracts/` · rama `rol/datos`

```
Trabajas en `data/` y `contracts/`. Rama: rol/datos. Tu PR lo revisa Dani.
Lee docs/vet/01-decisiones-y-tracks.md y docs/vet/00-hallazgos.md.

Tienes la carga más liviana a propósito, porque te toca el verificador que cruza tres carpetas.

- S3-3: `VALIDATION.md:133` dice 30,81% y `:135` dice que la brecha proxy-oficial es ≈2,1pp.
  33,3 − 30,81 = 2,49. El 2,1 venía del 31,17% del pre-registro, que cambió sin recalcular la brecha ni
  explicar por qué se movió el proxy. La limitación declarada está subestimada. Coordina con Juanda: el
  archivo es suyo.
- S3-1 (con Nico): la corrida arranca del dato POST-política. `poblacion_2025.parquet` existe y ningún
  ejecutable lo lee (`git grep poblacion_2025` solo pega en validate.py). NO SE CORRE hasta que Juanda
  haya commiteado el pre-compromiso.
- Apoyo a C2 en lo que toque data/ y contracts/.

TU VERIFICADOR PRINCIPAL, y es el que más valor tiene de todos: P9 · auditor de procedencia.
  "Traza cada número que la pantalla le muestra a un humano hasta su fuente última, y etiquétalo:
   DATO GEIH · NORMA citada · CALCULADO (¿por qué script?) · SUPUESTO (¿marcado o no?).
   Señala TODO número afirmado en voz alta cuya procedencia no puedas establecer: esos son los que
   matan en el Q&A. Devuelve una tabla con archivo:línea en cada fila, y una sección obligatoria de
   lo que el equipo hizo mejor de lo que esperabas."
Y después `juez-tecnico` y `peeky`.
```

---

## Quién revisa a quién, y quién verifica qué

**Nadie revisa ni verifica su propia carpeta.** No es burocracia: un modelo que revisa su propio trabajo
valida sus propios sesgos.

| Persona | Carpetas | Revisa los PR de | Su verificador |
|---|---|---|---|
| **Juanda** | `tests/` `scripts/` `Makefile` docs raíz deploy | Nico | `juez-cientifico` + P8 pre-registro |
| **Dani** | `web/` | Manuel | P5 juez frío |
| **Nico** | `behavior/` | Dani | P7 entrega + P6 rúbrica |
| **Manuel** | `engine/` `api/` | Juanda | prompt 16 re-apuntado + `juez-hackathon` |
| **Alejo** | `data/` `contracts/` | Dani | P9 procedencia + `juez-tecnico` + `peeky` |

**Los verificadores se corren al cerrar cada oleada, no al final de todo.** Un hallazgo que llega a las
08:00 ya no se puede arreglar.

### Los cinco prompts nuevos, en una línea cada uno

- **P5 · juez frío:** llega sin contexto, solo el repo clonado, y contesta *¿cómo sé que no lo inventa el
  modelo? ¿qué parte es difícil? ¿esto escala?* Se registra lo que responde, no lo que quisiéramos.
- **P6 · rúbrica:** puntúa contra Originalidad 15 · Ambición 20 · Ejecución 20 · Técnico 25 · Impacto 20.
- **P7 · entrega:** ¿un extraño con el link lo usa sin registrarse? ¿MIT? ¿repo público? ¿hay respaldo si
  el deploy se cae en vivo?
- **P8 · pre-registro:** verificar con `git log --date=iso` que el criterio es anterior a los datos. Ya se
  verificó una vez y se sostiene; se re-corre después de que C1 toque `VALIDATION.md`.
- **P9 · procedencia:** el de Alejo, arriba.
