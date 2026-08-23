# Decisiones y tracks — sesión del 22-ago, 22:00-22:30

Base: `origin/main` = `c63343f`. Tres auditorías de solo lectura. Hallazgos en `hallazgos.md`.
**Congelamiento: domingo 09:30. Quedan ~11h.**

---

## 1. Decisiones tomadas, con hora

| Hora | # | Decisión | Por qué |
|---|---|---|---|
| 22:05 | C10 | **Juanda arranca el deploy YA**, en paralelo a todo | Es lo único que puede fallar por razones que no controlamos (build, DNS, límites). Descubrirlo a las 06:00 no tiene arreglo |
| 22:20 | C1 | **Se retracta "fuera de muestra de verdad" de `VALIDATION.md`** y se declara qué es realmente. El error de 37,37 pp sigue publicado | El código contradice la frase: la corrida usa `poblacion.parquet` (2026) y arranca en el dato post-política. Retractar cuesta 0,25h; que lo encuentre un juez cuesta el pitch |
| 22:25 | — | **PRE-COMPROMISO, escrito ANTES de correr:** cuando S3-1 se arregle, **el número nuevo reemplaza a EL NÚMERO, salga como salga**, y los dos quedan publicados con su hash | Correr, mirar y quedarse con el que se vea mejor es exactamente lo que el pre-registro existe para impedir. Esto se commitea antes de correr o no vale |
| 22:25 | C3 | **Se fija `temperature=0`** en `behavior/cliente.py:_llamar` | Hoy la temperatura está suelta, así que parte de la dispersión viene de donde AGENTS.md juró que no vendría. Con temp=0 la variación queda siendo puramente la paráfrasis, y la restricción declarada pasa a ser cierta |
| 22:25 | C11 | La rama de Dani (`e4381ed`) **se lleva al grupo** con las dos opciones | Cruza dos dueños (Dani y Juanda). Regla 6 |
| 22:30 | C2 | **Se corrigen los cinco archivos más el oneliner de votación** | Los jueces leen el repo con agentes. Una contradicción entre `VALIDATION.md` y `README.md` se encuentra en 30 segundos |
| 22:30 | C4/C6 | **Suben a pantalla:** `fraccion_fallback` + `sin_salida`, el modo llm/reglas, y un **panel de procedencia** (DATO / NORMA / CALCULADO / SUPUESTO por métrica) | Es la respuesta a "¿de dónde se alimenta esto?" sin que haya que preguntarla |
| 22:30 | C8 | **La lámina de límites entra al repo**, adaptada a lo que el modelo hace hoy | Declarar los límites ANTES del Q&A neutraliza la pregunta difícil (`research/07` §4) |
| 22:30 | C5 | Industrias: **no está roto**, solo el comentario. 0,25h | 9 sectores con prefijos únicos y `desde_empresas` no trunca. El código está bien |
| 22:30 | C9 | Entrenamiento: **se declara que no hay** y que la caché es memoización, no aprendizaje | Confundirlas en el Q&A es regalar el punto |

---

## 2. Todo entra. Se ordena por dependencia, no por horas

El cuello de botella no son las horas: son los **dueños de carpeta** y las **dependencias**. Con dos
agentes por persona, lo que sigue son tres oleadas donde nada de una misma oleada toca el mismo archivo.

### Oleada 1 · arranca ya, cero dependencias, todo simultáneo

| Quién | Agente | Qué | Archivos |
|---|---|---|---|
| **Juanda** | A1 | **Deploy vivo** + `project-description.md` + `deploy-url` | infra, `platanus-hack-project.jsonc` |
| **Juanda** | A2 | **C1**: retractar "fuera de muestra de verdad" + **commitear el pre-compromiso** | `VALIDATION.md` |
| **Nico** | A1 | **S1-1** el `round()` sobre `banda.tipo` + **C3** `temperature=0` | `behavior/rondas.py`, `behavior/cliente.py` |
| **Nico** | A2 | **S3-6** quitar "el dato A1 aguanta" + **S1-10** el comentario de los 4 sectores | `behavior/README.md`, `arquetipos.py` |
| **Dani** | A1 | **S2-1** que la pantalla diga llm vs reglas (el evento ya trae `modo`) | `flujo.ts`, `simulacion.ts`, `BarraTiempo.tsx` |
| **Dani** | A2 | **S2-5** la cola de rondas en `MotorVisual` | `motorVisual.ts` y los paneles |
| **Manuel** | A1 | **S2-9** `rondas_totales` fuente única + **S1-4** el rótulo del seed | `api/serializar.py`, `api/servidor.py` |
| **Alejo** | A1 | **S3-3** la brecha 2,49 vs 2,1 | `data/`, y apoyo a `VALIDATION.md` |

### Oleada 2 · depende de que la 1 esté en `main`

| Quién | Qué | Depende de |
|---|---|---|
| **Dani** | **S2-2** pedir `parafrasis=5` desde el front | S1-1 (hoy revienta con N≥2) |
| **Nico + Alejo** | **S3-1** el backtest fuera de muestra real | **el pre-compromiso commiteado**, no antes |
| **Nico** | S1-2 `_banda` IndexError · S1-3 las 5 paráfrasis vs las 9 que acepta la API · S1-8 planta viva | S1-1 |
| **Juanda** | **C2** los 5 archivos + el oneliner · `AGENTS.md:11` (la mentira de `engine/rondas.py`) | C1 |
| **Manuel** | **S1-7** la banda entre trayectorias en la API · **S2-8** la conversión a COP a `serializar.py` | S1-1 |

### Oleada 3 · pulido y honestidad, todo paralelo

**Juanda:** C8 lámina de límites · S3-9 el segundo episodio (2024→2025, +2,63pp, dirección opuesta) a
`VALIDATION.md` · S3-2 el 35,60% sin fuente · S3-7 el test de clon limpio que pasa por construcción ·
S3-10 G1 que nunca puede dar verde · S3-11 · S3-5 · S3-8 · S3-4 G3 apuntando a `momentos_2025`
**Dani:** panel de procedencia · S2-7 fallback y sin_salida · S2-3 el `+0.15` · S2-4 la onda · S2-6
subtítulo del relato · S2-10 marcar `// SUPUESTO:` en el front · S2-11 · S2-12
**Nico:** S1-11 `desde_poblacion` muerta · S1-13 ronda 0 · S1-14 umbral de fallback · S1-15 `renegociar`
sin efecto · S1-16 vetadas acumuladas entre paráfrasis

### Las tres dependencias duras, que son lo único que puede trabar todo

1. **S1-1 antes que S2-2.** Pedir 5 paráfrasis sin arreglar el `round()` revienta la corrida entera.
2. **El pre-compromiso antes que S3-1.** Commiteado primero o el número nuevo no vale nada.
3. **C1 antes que C2.** Primero se define qué se afirma, después se propaga a los cinco archivos.

---

## 3. Los cinco tracks, con revisor y verificador

**Regla: nadie revisa ni verifica su propia carpeta.**

| Persona | Carpetas | Revisa los PR de | Su verificador |
|---|---|---|---|
| **Juanda** R5 | `tests/` `scripts/` `Makefile` docs raíz deploy | Nico | `juez-cientifico` + **P8 pre-registro** |
| **Dani** R4 | `web/` | Manuel | **P5 juez frío** |
| **Nico** R3 | `behavior/` | Dani | **P7 entrega** + **P6 rúbrica** |
| **Manuel** R2 | `engine/` `api/` | Juanda | Prompt 16 re-apuntado + `juez-hackathon` |
| **Alejo** R1 | `data/` `contracts/` | Dani | `juez-tecnico` + `peeky` + **P9 procedencia** |

**P9 · auditor de procedencia** se lo lleva Alejo: es quien tiene la carga más liviana y el que mejor
conoce la cadena de datos, que es donde P9 empieza.

**Los verificadores se corren al final de cada oleada**, no al final de todo: un hallazgo que llega a las
08:00 ya no se puede arreglar.

## 4. Lo que hay que llevar al grupo, y solo lo decide el equipo

1. **El pre-compromiso sobre el número nuevo.** Se commitea ANTES de correr S3-1 o no vale nada.
2. **La rama de Dani** (`e4381ed`): entra por PR o se borra la referencia de `DEFECTOS.md:27`.
3. **La línea de corte P0/P1/P2.** Si alguien no está de acuerdo con qué es P0, ahora, no a las 04:00.
4. **Que el pre-registro no fue ciego.** `2d4aa7e` ya traía "lo que ya se sabe apunta a la rama B".
   **Se dice en el pitch, de frente.** Dicho por nosotros es rigor; encontrado por un juez es fraude.
