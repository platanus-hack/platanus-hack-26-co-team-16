# IDEA — la espina dorsal

> **Para qué existe este archivo.** El equipo llegó a un punto en el que la idea estaba
> escrita en muchos lugares y nadie la podía explicar completa en voz alta. Esto lo arregla:
> **leyendo solo este archivo, cualquiera del equipo puede explicar la idea entera sin abrir
> otro.** Si algo acá está vacío o vago, es un defecto, no un pendiente.
>
> **Autoridad:** `docs/PLAN.md` sigue siendo la fuente de verdad del **alcance del producto**.
> Este archivo es la **estructura** de la idea y las decisiones de modelo que el plan dejó
> abiertas. Donde llene un vacío, manda. Donde contradiga, gana `PLAN.md` hasta que el equipo
> decida otra cosa.
>
> **Dueño:** Manuel (R2). Lo marcado 🔶 espera aval del equipo.
>
> **¿Llegaste de cero?** Empieza por [`EXPLICACION-SIMPLE.md`](EXPLICACION-SIMPLE.md), que cuenta lo mismo sin jerga.

---

## 1. La rúbrica: qué hace viable a una idea de simulación

No es nuestra. Se compone de cuatro piezas, tres externas y una propia, y **la idea de abajo
se llena contra ella**:

| Pieza | De dónde sale | Qué exige |
|---|---|---|
| **El molde de cinco huecos** | `docs/fuentes/manuel.md` §8 | Si la idea no cabe en una frase con cinco huecos llenos, todavía no existe |
| **La anatomía de cinco piezas** | `docs/fuentes/manuel.md` §2.5 | Estado del mundo · actores con reglas · **dinámica temporal** · palanca · lectura con incertidumbre. Si falta una, no es una simulación |
| **Protocolo ODD** | [Grimm et al. (2020), *JASSS* 23(2):7](https://www.jasss.org/23/2/7.html) | Siete elementos que hacen que un tercero pueda **reimplementar y refutar** el modelo. Es el estándar del campo |
| **Pattern-Oriented Modeling** | [Grimm et al. (2005), *Science* 310:987](https://www.science.org/doi/10.1126/science.1116681) ([espejo abierto](https://pure.knaw.nl/portal/en/publications/pattern-oriented-modeling-of-agent-based-complex-systems-lessons-/)) | El detalle que entra al modelo es el mínimo que reproduce **varios patrones observados a la vez**. Es el criterio para decidir qué datos importan |

Y una advertencia que también es rúbrica: [Epstein, *Why Model?* (2008)](https://www.jasss.org/11/4/12.html)
enumera dieciséis razones legítimas para modelar que no son predecir. **Nosotros no
predecimos el futuro: acotamos el rango y medimos el error.** Eso es una postura del campo,
no una excusa.

Detalle y fuentes de las cuatro: [`docs/investigacion/1-teorica.md`](investigacion/1-teorica.md).

---

## 2. La idea, en una frase

> **Nadie puede saber cuánta gente va a cumplir un aumento del salario mínimo del 23%**,
> porque el mundo solo corre una vez y el cumplimiento no se observa hasta mucho después;
> **así que construimos un mundo** donde **hogares reales de la GEIH y las firmas que los
> emplean** **eligen entre cumplir, informalizar, despedir, absorber o renegociar**, bajo
> **costos laborales reales y una capacidad de inspección fija que se diluye con cada evasor
> nuevo**, y **al mover el porcentaje de aumento** se puede leer **cuánta gente cumple de
> verdad, con banda de incertidumbre, y a quién le cae encima**.

Los cinco huecos están llenos. Es la prueba de que la idea existe.

---

## 3. Las 5 W y la H

| | |
|---|---|
| **QUÉ** | Un simulador de **cumplimiento** de política pública. No responde *"¿funciona la política?"* sino **"¿cuánta gente la cumple y a quién le cae encima?"** |
| **POR QUÉ** | Porque toda proyección oficial asume cumplimiento total, y ese supuesto nunca se mide. En un país con informalidad alta, es el supuesto que decide si la política funciona o no |
| **PARA QUÉ** | Para que quien decide deje de elegir entre tres números ciegos, y quien discute pueda interrogar el supuesto en vez de creerlo |
| **QUIÉN** | **Gobierno y periodismo**, en ese orden — decisión del equipo. Secundarios: academia y gremios. El afectado no es usuario, pero **se ve en el mapa**: *"gente como yo, ¿gana o pierde?"* |
| **DÓNDE** | Bogotá. El motor no es geográfico; la restricción es que los datos y la controversia son de allí |
| **CUÁNDO** | Ventana de **nueve meses desde el decreto** ([ADR 0005](adr/0005-el-reloj-de-la-simulacion.md)). Caso demo: decretos 1469 y 1470 de 2025, aumento del 23%, ~2,4M de trabajadores al mínimo, litigio abierto |
| **CÓMO** | Población real de la GEIH → una capa LLM propone estrategias de adaptación por arquetipo → un motor determinista **veta** lo que la plata no permite → se recalcula la probabilidad de sanción con capacidad fija → tres rondas de mejor respuesta → **la brecha entre la ronda 0 y la ronda 3 es el producto** |

---

## 4. Propuesta de valor

**El criterio de valor, tal como lo fijó el equipo:** *"las personas que tienen la capacidad
de tomar decisiones hoy las toman sin información; el valor es que puedan cambiar esas
decisiones."* No es "democratizar el acceso" en abstracto: es que **una decisión concreta
salga distinta**.

**Los cuatro datos que hoy no existen** (de `PLAN.md` §1.1, que es la vara de desarrollo:
lo que no sirve a uno de estos, no se construye):

| | El dato | Quién no lo tiene |
|---|---|---|
| **A1** | Cuánta gente cumple de verdad | DANE, ministerio, Fedesarrollo: el número no existe |
| **A2** | La forma de la curva: **dónde está el codo** | Nadie. La econometría da elasticidades, o sea rectas |
| **A3** | A quién le cae encima, por sector × tamaño × ingreso | Cualquier actor de la mesa de concertación |
| **A4** | Por qué evade cada quien, y qué estrategia domina en qué segmento | Ningún modelo con estrategias enumeradas a mano |

**Por qué no lo hace nadie hoy** (de [`docs/investigacion/3-live.md`](investigacion/3-live.md)):

1. Los productos vivos de simulación de poblaciones **le venden a quien ya tiene presupuesto
   de research**. Un concejal, un periodista o un gremio colombiano no es cliente de ninguno.
2. Lo que sí existe para política pública **se queda en Python**. Hay literatura capaz de
   decir qué pasa si sube la tarifa de transporte en Nueva York, y alguien que no programa no
   puede verlo. La brecha es de acceso, no tecnológica.
3. **Nadie publica un backtest fuera de muestra que un extraño pueda rehacer.** La empresa de
   USD 1.000M de esta categoría valida con estudios propios, por invitación. Nosotros
   validamos con un comando que cualquiera corre.

### El posicionamiento

Robado del movimiento más inteligente de la categoría (Synthetic Users invierte el flujo de
research: sintético barato primero para afinar la pregunta, investigación real después para
validar). Traducido a nuestro caso:

> **No reemplazamos al DANE, ni a Fedesarrollo, ni a la mesa de concertación. Somos el primer
> paso barato: mostramos cuál de las preguntas merece el estudio caro.**

Es más defendible que *"simulamos la política"*, desactiva la objeción obvia (*"¿por qué le
creería a esto en vez de a un economista?"*) sin pelearla, y es honesto con lo que un backtest
con banda de error puede sostener.

**Y una restricción comercial que es decisión de motor:** los productos vivos de esta
categoría cobran seis y siete cifras porque necesitan **semanas o meses de calibración por
cliente**. Un motor general no sabe nada de tu problema hasta que alguien lo calibra. Nosotros
no podemos pagar ese costo, y por eso **la calibración viene hecha para un solo caso**. Eso es
lo que nos permite ser gratis y sin registro, y es el respaldo comercial de la decisión D6 del
plan (*general en el código, estrecho en la pantalla*). Si el pitch promete generalidad **de
pantalla**, nos metemos sin querer en el negocio de Aaru, donde perdemos.
Detalle en [`docs/investigacion/3-live.md`](investigacion/3-live.md) §4.

**El límite, declarado como parte de la oferta:** no entregamos el futuro, entregamos **el
rango** con banda y con el error del backtest publicado. Convertimos un supuesto invisible
("la gente cumple") en un número medible con margen de error.

---

## 5. Anatomía de la simulación

Estructurada sobre los siete elementos de ODD. Las cinco piezas de la anatomía propia están
mapeadas: **estado del mundo** → §5.2 · **actores con reglas** → §5.2 y §5.7 · **dinámica
temporal** → §5.3 · **palanca** → §6 · **lectura con incertidumbre** → §7.

### 5.1 Propósito y patrones

**Propósito:** medir la brecha entre el cumplimiento que una política asume y el que
produce, y su distribución entre segmentos de la población.

**Patrones contra los que se juzga el modelo** (criterio POM: varios a la vez, con un solo
juego de parámetros). Sin política, el mundo tiene que reproducir:

| # | Patrón | Estado |
|---|---|---|
| P1 | Tasa de informalidad **por sector** | Observable en la GEIH |
| P2 | Tasa de informalidad **por tamaño de firma** | Observable en la GEIH |
| P3 | **Spike** de masa salarial acumulada exactamente en el mínimo | ⚠️ sin verificar que sea visible en los datos descargados. Si no aparece, el modelo se juzga con P1 y P2, y se dice |

Un modelo que reproduce uno solo está sobreajustado. Reproducir dos o tres con los mismos
parámetros es lo que da derecho a hablar del cuarto (la cascada), que no se observa.

### 5.2 Entidades, variables de estado y escalas

| Entidad | Qué es | Variables de estado |
|---|---|---|
| **Trabajador** | Una persona real anonimizada de la GEIH. **No se inventa ninguno** | sector, tamaño de empresa, ingreso mensual, formal/informal, educación, **factor de expansión** |
| **Firma** | Construida agrupando trabajadores por sector × tamaño (atributos observados en la encuesta) | número de empleados, flujo de caja, productividad marginal, cuántos empleados tiene formales |
| **Arquetipo** | sector × tamaño × formal/informal × tramo de ingreso. ~40-60. **Es la unidad a la que se le llama al LLM**, la unidad de caché y la de presupuesto | estrategia propuesta en la ronda, distribución de respuestas |
| **Agregado** | El resumen del estado del sistema que los arquetipos ven. **Es el mecanismo de la cascada**: nadie ve a nadie individualmente | tasa de evasión, probabilidad de sanción vigente |
| **EstadoFiscalizacion** | La capacidad de inspección del período. **No es parte de la política** ([ADR 0006](adr/0006-fiscalizacion-es-estado-del-mundo.md)) | inspectores efectivos, inspecciones por inspector por trimestre, fracción dirigida al universo |
| **Politica** | Lo único que el usuario mueve. Solo cambia pagos | tipo, porcentaje de aumento |

**Escalas.** Espacial: Bogotá, sin geografía interna (no hay grilla ni red; el caso no es
espacial). Temporal: **el trimestre** ([ADR 0005](adr/0005-el-reloj-de-la-simulacion.md)).
Poblacional: miles de agentes muestreados, **escalados por el factor de expansión de la
GEIH** — la escala se afirma con el número de la encuesta, no con el runtime.

### 5.3 Procesos y scheduling — la dinámica temporal

**Una ronda es un trimestre.** El horizonte de una corrida es de nueve meses desde el decreto.

| Ronda | Momento | Qué pasa |
|---|---|---|
| **0** | El decreto | Reacción ingenua: todos cumplen. **Es la proyección oficial**, la línea recta del gobierno |
| **1** | Trimestre 1 | Cada arquetipo ve el agregado de la ronda 0 → la capa LLM propone estrategia → el motor **veta** lo infactible → aplica lo que sobrevive → **recalcula la probabilidad de sanción** |
| **2** | Trimestre 2 | Igual, viendo el agregado de la ronda 1 |
| **3** | Trimestre 3 | Igual. **Es la ronda que se reporta** |

**El orden dentro de una ronda importa y es fijo:** ver agregado → proponer → vetar →
(reintentar hasta 3 veces, si no, cumplir) → aplicar → recalcular fiscalización → publicar
agregado. Los arquetipos deciden **contra el agregado de la ronda anterior**, no contra el de
la actual: es mejor respuesta con rezago, no un punto fijo simultáneo, y decirlo así evita
prometer un equilibrio que no calculamos.

### 5.4 Conceptos de diseño

Los que aplican, y **los que no**, que es la mitad honesta de esta sección:

| Concepto | Cómo aparece |
|---|---|
| **Emergencia** | 🟡 **La cascada, como mecanismo.** No está programada: sale de que la probabilidad de sanción decrece con el número de evasores, y nadie escribió "si muchos evaden, evade más". **Pero no es un hallazgo del proyecto**: la predicción agregada que produce está falsada por el backtest (+37,37 pp, signo contrario) y su aporte medido al resultado es **+0,0 pp** en el camino determinista ([evidencia](evidencia/2026-08-23-E1-E2-E3.md) §E2) |
| **Adaptación** | ✅ La firma elige estrategia dada la mecánica del cambio de costos y el agregado observado |
| **Objetivos** | ✅ parcial. **No le imponemos función de utilidad a la firma** — la conducta la propone el LLM y la filtra el veto. El trabajador **sí** tiene objetivo explícito: neto ajustado por protección ([ADR 0008](adr/0008-asimetria-firma-trabajador.md)) |
| **Aprendizaje** | ❌ **No hay.** Los agentes no acumulan memoria entre rondas más allá del agregado que ven. Un modelo con aprendizaje sería otra cosa y no cabe en el horizonte |
| **Predicción** | ❌ **No hay.** Los agentes **no anticipan rondas futuras**: responden a lo que ya pasó. Es miope a propósito, y es exactamente por qué esto **no** se llama equilibrio |
| **Sensing** | ✅ Los arquetipos ven **solo el Agregado**: tasa de evasión y probabilidad de sanción. No ven agentes individuales ni el estado completo |
| **Interacción** | ✅ **Indirecta**, vía el agregado y vía la dilución de la capacidad. No hay red social ni contacto uno a uno |
| **Estocasticidad** | ✅ Un `numpy.random.Generator` sembrado, un sub-stream por ronda. Entra en el muestreo de agentes desde las distribuciones por arquetipo ([ADR 0009](adr/0009-frontera-del-determinismo.md)) |
| **Colectivos** | ✅ **El Arquetipo es el colectivo**, y es entidad de primera clase, no un agrupamiento incidental |
| **Observación** | ✅ Un registro por ronda con las métricas de §7, más el feed de decisiones y el desglose por segmento |

### 5.5 Inicialización

El mundo arranca **sin política**, cargando la población desde `data/poblacion.parquet` y la
capacidad desde `EstadoFiscalizacion`. Antes de aplicar nada, el mundo tiene que reproducir
P1, P2 y (si existe) P3. **Ese es el candado 1 de validación y es la condición para que la
corrida con política signifique algo.**

### 5.6 Datos de entrada

| Dato | Origen | Estado |
|---|---|---|
| Población de agentes | Microdatos GEIH (DANE) | Única fuente verificada del proyecto |
| Momentos de calibración | GEIH: informalidad por sector y tamaño, distribución salarial | Los objetivos de P1-P3 |
| Capacidad de inspección | [OIT, 2023-24](https://www.ilo.org/es/projects-and-partnerships/projects/mayor-capacidad-de-la-inspeccion-del-trabajo-en-colombia) | **1.300 inspectores** en 36 direcciones territoriales. Con ~23M de ocupados es ≈1 por cada 18.000 trabajadores, casi el doble del estándar OIT/OCDE de 1 por 10.000. **De acá sale `C`, y de `C` sale la cascada** |
| Elasticidad de contraste | Banco de la República WP 1104: +1 pp en el ratio del mínimo ≈ +0,21 pp de informalidad | Objetivo de calibración del tramo bajo, **nunca resultado** |
| Inflación, crecimiento, tasa de cambio | Observados | **Exógenos siempre.** No es un modelo macro |

### 5.7 Submodelos

| Submodelo | Qué hace | Fundamento |
|---|---|---|
| **Costos** | `costo_formal = salario × factor prestacional`; `costo_informal = salario negociado + sanción esperada` | Allingham-Sandmo 1972. El factor prestacional (≈1,4-1,5) es supuesto con sensibilidad |
| **Fiscalización endógena** | `p(E) = 1 − exp(−C / max(E,1))`, con `C` = inspecciones esperadas en el trimestre y `E` = evasores de la ronda anterior | [ADR 0007](adr/0007-forma-funcional-prob-sancion.md). Deriva de repartir `C` inspecciones al azar entre `E` evasores. **Aquí nace la cascada** |
| **Veto de factibilidad** | Rechaza propuestas que la caja no permite, con razón. Hasta 3 reintentos; al agotarlos, la estrategia terminal es cumplir | [ADR 0003](adr/0003-veto-de-factibilidad.md) |
| **Decisión del trabajador** | Acepta la oferta informal si su neto informal supera al formal por encima de la prima que le asigna a la protección | 🔶 [ADR 0008](adr/0008-asimetria-firma-trabajador.md) |
| **Propuesta de estrategia** | La capa LLM, por arquetipo, viendo **solo mecánica** | [ADR 0002](adr/0002-llm-por-arquetipo.md). Es de `behavior/` (Nico) |

---

## 6. La palanca — qué toca el usuario

**Una sola perilla: el porcentaje de aumento.** Tres valores marcados (7 / 13,6 / 23%, las
tres posturas reales del debate) sobre un barrido fino precomputado que dibuja la curva
completa y muestra **dónde está el codo** (dato A2).

**Lo que el usuario NO puede mover, a propósito:** la capacidad de fiscalización. Si fuera
perilla, cualquier resultado sería alcanzable y la cascada perdería su valor probatorio
([ADR 0006](adr/0006-fiscalizacion-es-estado-del-mundo.md)). Queda como trabajo futuro
nombrado, no como feature escondido.

**Sin registro, sin cuentas.** Un extraño con el link tiene que poder usarlo.

---

## 7. Las métricas — la lectura con incertidumbre

Definidas operativamente, porque cuatro números sin definición son cuatro discusiones a la
hora 30:

| Métrica | Definición exacta |
|---|---|
| **`tasa_informalidad`** | Suma de factores de expansión de los informales sobre suma total de factores de expansión. **Siempre ponderada** — sin el factor no es la informalidad de la GEIH, es la de la muestra |
| **`prob_fiscalizacion`** | `p(E)` evaluada con el `E` de la ronda anterior. Se reporta por trimestre |
| **`empleo_relativo`** | Empleo ponderado de la ronda `k` dividido por el de la **línea base sin política**. La base **no es la ronda 0**: la ronda 0 ya tiene el efecto ingenuo de la política |
| **`banda` (p10/p90)** | Sobre **N≥5 paráfrasis del prompt × M seeds**. Se reportan las dos dimensiones por separado: cuánta variación viene del lenguaje y cuánta del muestreo |
| **`brecha`** | Ronda 3 menos ronda 0. **Es el producto entero** |
| **`n_vetos` / `n_fallback`** | Diagnóstico por ronda. Si muchos arquetipos caen en la estrategia terminal, el veto está demasiado apretado y el resultado no dice lo que creemos |

**Ningún número sale sin banda.** Se reporta **varianza además de media**, porque los LLM
colapsan varianza y preferimos decirlo nosotros primero.

---

## 8. El flujo del producto, punta a punta

```
PREPARACIÓN (una vez)
  GEIH (DANE) → ingesta → poblacion.parquet + momentos.json
  Fuentes de inspección → EstadoFiscalizacion

CALIBRACIÓN (candado 1)
  Mundo SIN política → ¿reproduce P1, P2, P3?
  Si no reproduce, nada de lo que sigue significa algo.

CORRIDA (lo que ve el usuario)
  Usuario mueve el slider
    → Politica se traduce a MECÁNICA SIN NOMBRE
      ("tu costo laboral por empleado formal sube X%")
    → RONDA 0: reacción ingenua = la proyección oficial
    → RONDAS 1-3, cada una un trimestre:
         Arquetipo ve el Agregado anterior
         → capa LLM propone estrategia
         → motor VETA lo infactible (hasta 3 intentos, luego cumplir)
         → trabajador acepta o rechaza (regla determinista)
         → motor aplica
         → recalcula p(E): capacidad FIJA / más evasores ⇒ CASCADA
         → publica Agregado
    → persiste en Supabase → la interfaz lo dibuja en vivo

LECTURA
  Curva de la brecha (oficial vs cascada) · el codo · mapa distributivo
  con bandas · desglose de estrategias · 3-4 historias con cara

VALIDACIÓN (make validate)
  1 calibración base · 2 backtest fuera de muestra (excluye 2020-21)
  3 contaminación: sin nombre + re-skinning · 4 ablación sin LLM
  → imprime EL número, acierte o no
```

---

## 9. Lo que NO es

| No es | Por qué |
|---|---|
| **Un modelo macro** | Inflación, crecimiento y tasa de cambio son exógenos observados, nunca resultado |
| **Una prueba de equilibrio** | Son tres rondas de mejor respuesta con rezago. No calculamos ni demostramos un punto fijo, y no lo llamamos así en ningún texto |
| **Un optimizador de políticas** | Evalúa la que se le dé; no busca la mejor |
| **Física de flujo** | Trancón, evacuación, contagio son otra máquina. El motor sirve a **una** clase: cambio de costos/incentivos + capacidad de fiscalización + población, donde incumplir es una opción |
| **Un predictor** | Entrega el rango con banda y el error del backtest publicado |
| **Research sintético para marcas** | Categoría con un unicornio dentro. No competimos ahí |

### Dos cosas que se decidieron acá y hay que dejar cerradas

**La regla de dominio.** El audio propuso *"población + beneficio fiscal + cambio de
política"*. **Gana la regla escrita en `PLAN.md` §4.2:** *cambio de costos/incentivos +
capacidad de fiscalización + población, donde incumplir es una opción*. El *"beneficio
fiscal"* del audio es un **subconjunto**: toda política con consecuencia fiscal que cambia
incentivos cabe en la regla escrita, pero la regla escrita además exige lo que de verdad
delimita el motor — que exista una **opción de incumplimiento con costo esperado calculable**.
Sin eso no hay nada que simular. La tabla de qué cabe y qué no está en `PLAN.md` §4.2 y no se toca.

**Input en lenguaje natural.** El audio propuso un campo de texto tipo chat (*"qué pasa si
suben los subsidios"*). **Queda fuera**, y la razón es de motor, no de tiempo: traducir texto
libre a mecánica exige que **algo interprete el nombre de la política**, que es exactamente
lo que el control de contaminación prohíbe. Un traductor determinista con vocabulario cerrado
sería posible, pero da la ilusión de generalidad que la regla de dominio niega. El slider es
más honesto y se entiende en tres segundos.

---

## 10. Los seis filtros de muerte, corridos

De `docs/fuentes/manuel.md` §8. Se corren en voz alta, no se asumen:

| Filtro | Respuesta |
|---|---|
| **¿Existe ya?** | Las piezas sí, la composición no. Prior art citado en el `README.md` y en [`3-live.md`](investigacion/3-live.md). Lo más cercano ([arXiv 2501.18177](https://arxiv.org/abs/2501.18177)) usa población sintética y no publica backtest fuera de muestra |
| **¿Es aburrido de mirar?** | No. La imagen es una línea recta oficial contra una curva que se despega, y un mapa de quién pierde |
| **¿Puedo mover una palanca en vivo?** | Sí: el slider, con escenarios precomputados para que responda en segundos |
| **¿Hay algo que no se resuelve prompteando?** | Sí: la fiscalización endógena y el veto de factibilidad. El LLM propone, la aritmética decide |
| **¿Cómo sé que no está inventando?** | Cuatro candados, y el número se publica salga como salga. Es el filtro que mata al 80% del track |
| **¿Un desconocido lo usa sin manual?** | Un slider, una curva, un mapa. Sin registro |

---

## 11. Estado de las decisiones

Los diez huecos que este trabajo encontró, y dónde quedó cada uno:

| # | Hueco | Estado |
|---|---|---|
| H1 | El reloj de la simulación | ✅ [ADR 0005](adr/0005-el-reloj-de-la-simulacion.md) — una ronda es un trimestre |
| H2 | Capacidad de fiscalización dentro de `Politica` | ✅ [ADR 0006](adr/0006-fiscalizacion-es-estado-del-mundo.md) — sale a estado del mundo |
| H3 | `prob_sancion` mal formada | ✅ [ADR 0007](adr/0007-forma-funcional-prob-sancion.md) — forma Poisson acotada |
| H4 | Trabajador y firma mal abstraídos | 🔶 [ADR 0008](adr/0008-asimetria-firma-trabajador.md) — **Nico avaló** en el PR #4 (2026-08-22). **Falta Alejo** |
| H5 | `Arquetipo` y `Agregado` sin nombre | ✅ Entidades de primera clase, §5.2 |
| H6 | Sin salida cuando el veto rechaza todo | ✅ 3 reintentos, luego cumplir. Se reporta `n_fallback`, §7 |
| H7 | Frontera del determinismo | ✅ [ADR 0009](adr/0009-frontera-del-determinismo.md) — **hay una frase que corregir en `README.md` y `AGENTS.md`** |
| H8 | Métricas sin definición operativa | ✅ §7 |
| H9 | Regla de dominio: verbal vs escrita | ✅ Gana la escrita, §9 |
| H10 | Input en lenguaje natural | ✅ Fuera, con razón de motor, §9 |

**Lo que R2 necesita del equipo** *(actualizado 2026-08-22 09:52, tras el review del PR #4)*:

1. ~~**Alejo y Nico** — aval de ADR 0008~~ → **Nico avaló** en el PR #4. **Falta Alejo**, y de
   paso congelar el campo `realizacion: {ocurre, razon}` que Nico propuso y R2 avaló: es
   hermano de `veto`, lo llena el motor **después** del veto y **no dispara reintento**. Sin
   él, el dato A4 mezcla *"no pude pagarlo"* con *"no me lo aceptaron"*.
2. **Juanda** — precisar la frase de determinismo en `README.md` y `AGENTS.md`
   ([ADR 0009](adr/0009-frontera-del-determinismo.md)). Sigue abierto.
3. **Dani y Alejo** — `contracts/ronda.json` gana un campo de tiempo
   ([ADR 0005](adr/0005-el-reloj-de-la-simulacion.md)) y `banda` gana `degenerada`, que
   `behavior/` ya emite. Los dos son aditivos.
4. ~~**Quien pueda** — la cifra vigente de inspectores~~ → **RESUELTO:** la OIT publica 1.300
   inspectores en 36 direcciones territoriales. `C` ya tiene fuente.

🔴 **Lo nuevo, y es lo más urgente de todo lo de arriba:**

5. **Juanda** — `platanus-hack-project.jsonc` tiene los 4 campos en `<FILL THIS>`, incluido
   `deploy-url`, y **no hay `requirements.txt` en el repo** ni caché commiteado. Hoy un
   extraño no puede correr ni reproducir nada, lo cual contradice de frente la restricción
   no-negociable de *"repo público, desplegado y accesible sin registro"* y vacía
   `make reproduce`.
6. **Todo el equipo** — **el candado 4 puede colapsar.** Cuando Nico arregle la ablación (hoy
   compara mal el costo de formalizarse), una regla fija bien especificada probablemente
   **también produce cascada**: formalizarse cuesta ≈1,72× ingreso contra ≈1,58× de seguir
   informal. Si eso pasa, la ablación deja de ser el argumento de por qué el LLM se gana el
   puesto. Se corre, se reporta lo que dé, y se decide con el número en la mano.
