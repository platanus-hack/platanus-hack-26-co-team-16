# Validación — ¿por qué creerle a esta simulación?

> **Qué es este archivo.** El criterio de éxito de la simulación, **escrito antes de correrla**.
> Dueño formal: Juanda (R5). Esta versión la escribió Alejo (R1) en la 8ª sesión y **necesita aviso
> en el grupo**: toca un documento raíz.
>
> **Por qué el orden importa.** Un umbral escrito después de ver el resultado no es un umbral, es
> una racionalización. El timestamp de git de este archivo es la prueba de que el criterio es
> anterior al número: `git log --format="%h %ad %s" --date=iso -- VALIDATION.md`.
>
> **Regla del proyecto, ya escrita:** el número se publica salga como salga.
> Metodología completa: `docs/PLAN.md` §5.

## EL número

**Corrido el 2026-08-22, después del pre-registro `2d4aa7e`. Ningún umbral se movió para llegar aquí.**

```
Error del backtest:            37,37 pp   (firmado modelo − observado: +37,37 pp)
Skill vs persistencia (B1):    -8,182
Cobertura de la banda:         NO
Ancho de la banda:             33,9 pp
Corridas:                      BLOQUEADO — el repo no registra N>=5 trayectorias comparables

Proxy Bogotá, GEIH 2025 ene-jun:   34,64 %
Proxy Bogotá, GEIH 2026 ene-jun:   30,57 %
Delta observado:                   -4,07 pp
Delta predicho por el modelo:     +33,3  pp
```

Reproducible con: `make validate` · sale con código **1** mientras haya compuertas bloqueadas.

### Veredicto: **rama B — la cascada agregada está falsada**

El modelo predice que la informalidad **sube 33 puntos**; bajó **4**. El signo es contrario, la
magnitud está a un orden de magnitud, el observado cae **fuera de la banda del propio modelo**, y
**la persistencia le gana ocho veces**: predecir "2026 = 2025" erra por 4,07 pp y el modelo por 37,37.

**El contraste vale doble porque hay dos escalas independientes y coinciden:**

| Escala | 2025 → 2026 | Cambio |
|---|---|---|
| Proxy propio, mismo código en los dos extremos, ene–jun | 34,64% → 30,57% | **−4,07 pp** |
| Oficial DANE, abr–jun | 35,60% → 33,30% | **−2,30 pp** |

Distinta definición, distinto trimestre, misma dirección y mismo orden de magnitud. **El resultado
no es un artefacto del proxy.**

Un chequeo independiente de que el pipeline lee bien la realidad: el pico salarial se movió solo, de
**1.420.000** en 2025 a **1.750.000** en 2026 — sigue al mínimo legal de cada año (1.423.500 y
1.750.905) sin que nadie se lo dijera. El patrón P3 se sostiene en los dos años.

Lo que sigue en la sección "Las dos ramas" **estaba escrito antes de conocer estos números** y se
aplica tal cual, sin ampliarlo.

---

## Cómo se decide si pasó: compuertas y mediciones

La distinción que hace utilizable este documento.

- **Compuerta.** Si falla, lo que viene después no significa nada. Es binaria.
- **Medición.** Se publica el número que salga. No tiene pasa/falla.

Convertir en medición algo que era compuerta es exactamente cómo se fabrica un "todo salió bien".

| # | Candado | Tipo | Umbral, fijado ANTES de correr | Estado |
|---|---|---|---|---|
| **G1** | Reproducibilidad | Compuerta | Dos corridas con el mismo `(seed, manifiesto de caché, versiones)` dan salida idéntica | 🔴 no corre: sin `requirements.txt` y sin `scripts/validate.py` |
| **G2** | No contaminación | Compuerta | `python -m behavior.higiene` sale 0 **y** el re-skinning mueve el agregado ≤ el ancho del rango entre paráfrasis | 🟡 la higiene existe; **el re-skinning no está implementado** |
| **G3** | Calibración base | Compuerta | Informalidad total dentro de **±2 pp** del proxy medido, **y** se respeta el orden micro > pyme > grande | 🔴 sin corrida formal de calibración |
| **M1** | Backtest | Medición | Se publica. Sin umbral | 🔴 bloqueado: falta la población pre-política |
| **M2** | Habilidad | Medición | Se publica, incluso negativo | 🔴 bloqueado por M1 |
| **M3** | Ablación | Medición | Se publica **con** su sensibilidad al factor prestacional | ✅ medido, y **no discrimina** (ver abajo) |
| **M4** | Banda | Medición | Cobertura **y** agudeza, siempre juntas | 🟡 medida, pero mal nombrada (ver abajo) |

**Por qué G3 con ±2 pp.** El candado 1 es la condición de que todo lo demás signifique algo
(`docs/IDEA.md` §5.5). Laxo lo vuelve decorativo; apretado invita a ajustar parámetros hasta
pegarle, que es el riesgo que `docs/PLAN.md` §10 ya nombró. ±2 pp es holgado frente al ruido
muestral de la GEIH y estrecho frente a la brecha de 33 pp que está en disputa.

---

## Candado 1 · Calibración base

El mundo corre **sin política** y debe reproducir lo observado: informalidad por sector (P1) y por
tamaño de firma (P2), y el pico salarial en el mínimo (P3).

### 🔴 Corrección: el objetivo de calibración estaba mal puesto

La versión anterior de este archivo fijaba como referencia **"informalidad ~55–60%"** citando la
serie DANE. Ese número es **nacional**, y este modelo es de Bogotá.

Verificado contra el boletín oficial [*Ocupación informal, trimestre abril–junio 2026*](https://www.dane.gov.co/files/operaciones/GEIH/bol-GEIHEISS-abr-jun2026.pdf)
(DANE, 13-ago-2026):

| Ámbito | abr–jun 2026 |
|---|---|
| Total nacional | **54,5%** ← de aquí salía el 55–60% |
| 13 ciudades y A.M. | 40,7% |
| **Bogotá D.C.** | **33,3%** ← la más baja de las 23 ciudades |

Con el objetivo equivocado, el candado 1 falla aunque el modelo esté bien, o "pasa" cuando alguien
ajuste hacia un número que no le corresponde. **El objetivo correcto es Bogotá.**

### El proxy del repo no es la definición del DANE, y hay que decir cuánto se parece

`data/construir_poblacion.py` marca informal a quien no cotiza pensión (`P6920`). El DANE define
otra cosa, textual del boletín:

> *"se considera como ocupados informales a todos los asalariados o empleados domésticos que no
> cuentan con cotizaciones a salud ni a pensión por concepto de su vínculo laboral con el empleador
> que los contrató. De igual forma, se consideran como ocupados informales, por definición, a todos
> los Trabajadores sin remuneración, los Otro ¿Cuál?, así como los Trabajadores por cuenta propia y
> Patrones o empleadores que hayan quedado clasificados en el sector Informal."*

Medido sobre nuestros propios microdatos (GEIH 2026, `AREA==11`):

| Medida | Valor |
|---|---|
| Proxy del repo, ene–jun, con filtro de ingreso | **30,57%** (es el de `momentos.json`) |
| Proxy del repo, abr–jun, con filtro de ingreso | **30,81%** |
| **Oficial DANE, Bogotá, abr–jun** | **33,3%** |
| Brecha proxy − oficial | **≈ −2,1 pp** |

**No podemos reproducir hoy la definición oficial**, y la razón es concreta: clasificar a un
independiente en sector formal o informal exige saber si su unidad está registrada, y `P3045S1`
**solo se le pregunta a los asalariados** — los 2.315 independientes de la muestra la tienen vacía,
verificado. Reconstruirla exige variables del módulo de independientes que hoy no se extraen.

**Consecuencia para el benchmark, y es la decisión de diseño central:** el backtest se puntúa
**proxy contra proxy, con el mismo código en los dos extremos**. Si el predicho saliera del proxy y
el observado de un boletín, no se mediría error del modelo sino deriva de definición. La brecha de
2,1 pp contra el DANE queda como **limitación declarada**, no como fallo de validación.

### Los objetivos, con su fuente

| Objetivo | Valor | Fuente | Uso |
|---|---|---|---|
| Informalidad de referencia | **33,3%** Bogotá (oficial) · **30,6%** proxy propio | [Boletín DANE abr–jun 2026](https://www.dane.gov.co/files/operaciones/GEIH/bol-GEIHEISS-abr-jun2026.pdf) · `data/momentos.json` | G3. **Se calibra contra el proxy**, se reporta la brecha contra el oficial |
| Informalidad por sector y tamaño | `data/momentos.json` | GEIH, cálculo propio | P1 y P2. Se exige el **orden**, no el valor exacto |
| Elasticidad mínimo → informalidad | **rango +0,21 a +0,99 pp** por +1 pp del ratio | BanRep [WP 1104](https://ideas.repec.org/p/bdr/borrec/1104.html) (+0,21) y [WP informalidad por grupos demográficos](https://repositorio.banrep.gov.co/items/d9c8d84d-cd38-45a6-a2be-c9c4f2c1d438) (+0,35 a +0,99) | Baseline B2. ⚠️ **Es un rango, no un punto**: son documentos y medidas distintas |
| Heterogeneidad demográfica | Efecto concentrado en 18–25 de baja educación y mujeres 51–65 | Misma fuente | Chequeo del mapa (A3). ⚠️ **Requiere edad y sexo, que hoy no están en el parquet** |

---

## Candado 2 · Backtest fuera de muestra — el diseño V0

### El hecho que lo hace posible hoy

**La política del caso demo ya ocurrió.** El decreto 1469/2025 rige desde el 1-ene-2026 y
`data/raw/` tiene GEIH 2026 ene–jun, que es **posterior**. El modelo no necesita esperar a nada
para ser puntuado.

```
GEIH 2025 (catálogo 853) ──construir_poblacion.py, mismo código──▶ proxy PRE-política
GEIH 2026 (ya en disco)  ──el mismo script, sin cambios──────────▶ proxy POST = 30,57 %
                                                                     │
                        Δ observado ◀────────────────────────────────┘
                        contra Δ predicho por el modelo
```

Verificado: GEIH 2025 tiene la misma estructura de variables que 2026 (`P3069`, `P6920`, `P6430`,
`P6426`, `P6800`, `INGLABO`, `FEX_C18`, `RAMA2D_R4` están todas en el catálogo 853). No hay que
armonizar nada. Es fuera de muestra de verdad: el modelo se instancia con 2025 y nunca ve 2026, y
el control de contaminación se sostiene porque al LLM jamás se le nombra la política.

Se excluyen **2020–2021** de cualquier backtest (COVID). Un segundo punto (GEIH 2024 → +9,5% de
2025 → puntuar contra 2025) da n=2, que sigue siendo delgado y se dice.

### 🔴 Defecto que V0 destapa: la ronda 0 está mal etiquetada

El modelo llama a su ronda 0 *"la proyección oficial, todos cumplen"* y la inicializa con **30,57%**.
Pero ese 30,57% se midió en GEIH 2026 ene–jun, o sea **seis meses después del decreto**: ya contiene
la adaptación que hubo. No es el contrafactual de cumplimiento total, es el resultado observado.

El modelo está partiendo del final y prediciendo que a partir de ahí la informalidad sube. Por eso
V0 exige la población de 2025: **sin ella, el punto de partida y el objetivo son el mismo dato.**

---

## Los baselines — el "¿mejor que qué?"

Un número de error sin baseline no dice nada.

| | Baseline | Qué predice | Para qué sirve |
|---|---|---|---|
| **B0** | Proyección oficial | Informalidad sin cambio | El hombre de paja. Ganarle no prueba nada |
| **B1** | **Persistencia** | Informalidad del período = la del anterior | **El baseline duro.** La informalidad se mueve despacio. Un modelo que no le gana a esto no es un modelo |
| **B2** | Elasticidad econométrica | +0,21 a +0,99 pp por +1 pp del ratio | El competidor real. Es una recta; el aporte declarado (A2) es que hay un codo |

`skill = 1 − (error_modelo / error_baseline)`. Negativo es peor que el baseline, y se publica igual.

**Cómo se puntúa:** error absoluto en pp, **y el signo reportado aparte** — acertar la magnitud con
el signo cambiado no es acertar. La banda se juzga por cobertura **y** agudeza a la vez: la
cobertura sola se gana siendo vago.

---

## Candado 3 · Control de contaminación

**(a) La política jamás se nombra.** Ni "salario mínimo", ni "decreto", ni años, ni país, ni moneda.
Solo la mecánica. `behavior/higiene.py` lo hace cumplir con 31 patrones y mata la corrida si algo se
filtra, sin bandera para desactivarlo. ✅ implementado.

**(b) Test de re-skinning.** 🔴 **No está implementado.** Se declara como hueco, no como hecho.

---

## Candado 4 · Ablación del LLM

✅ Medido, y el resultado es negativo: **la ablación no discrimina.**

El punto de quiebre está en el factor prestacional **F = 1,4309**: por debajo no hay cascada con
reglas fijas, por encima sí. Ese parámetro está declarado como incierto en el rango **1,4–1,5**
(supuesto S1 de `engine/MODELO.md`), o sea que **el signo del candado 4 depende de un número que el
proyecto ya había declarado que no tiene verificado.**

No se puede afirmar que el LLM se gana el puesto por esta vía. Se reporta así.

---

## Candado 5 · Pico y placa (opcional)

_PENDIENTE y condicionado a que C4 cierre. Si compite con el número principal, se cae sin discusión._

---

## Método — y una corrección obligatoria a la banda

- La barra de error se construye sobre **N≥5 paráfrasis del prompt**, no sobre temperatura.
- Se reporta **varianza además de media**.
- **Ningún número sale sin banda.**

🔴 **La banda actual está mal nombrada.** Con N=5, el `p10`/`p90` que emite `behavior/rondas.py:390`
es literalmente **el mínimo y el máximo** de las cinco (`k10 = int(0.10×4) = 0`, `k90 = round(0.90×4) = 4`).
En esperanza son los percentiles **16,7 y 83,3**, no 10 y 90. Y promediar sobre paráfrasis y seeds a
la vez es pseudorreplicación: son dos fuentes de variación distintas.

**Lo correcto y barato:** llamarlo **"rango entre paráfrasis"**, mostrar las cinco curvas, y
reportar la dispersión entre seeds por separado. Mientras eso no se arregle, ningún número sale con
banda válida — que es una de las restricciones no-negociables del repo.

---

## Las dos ramas, decididas antes de ver el número

**Rama A — la cascada agregada sobrevive.** `|error| ≤ 5 pp` **y** `skill > 0` contra B1. Se reporta
el número y el pitch se mantiene. El codo (A2) sigue sin afirmarse hasta que el barrido lo soporte.

**Rama B — falsada.** Cualquier otro resultado. Tres movimientos, ninguno improvisado:

1. **Se publica el error**, con signo y magnitud.
2. **Se acota el claim, y el acotamiento es este y no otro:** el modelo simula el margen
   **formal → informal dentro de los ocupados que ya tienen empleador**. No simula la tasa agregada
   de informalidad que publica el DANE, que además se mueve por composición, por entradas y salidas
   del empleo y por ciclo. Está escrito ahora justamente para que no se pueda estirar después.
3. **Se nombran los confusores que el modelo ya declara no cubrir** — la reforma laboral (Ley 2466
   de 2025), la jornada de 42 horas desde el 15-jul-2026, el ciclo — **como límite declarado (D8),
   nunca como excusa.** La diferencia entre las dos cosas es si se dicen antes o después de conocer
   el resultado. Por eso van aquí.

### La rama que se activó: **B**

V0 corrió el 2026-08-22 y dio `error = 37,37 pp`, `skill = −8,182`, cobertura `NO`. Ninguna de las
dos condiciones de la rama A se cumple, ni de cerca. Los tres movimientos de la rama B son los que
están escritos arriba, sin agregar ninguno.

**Lo que sobrevive, y no es poco:** la población es real y verificable, la política nunca se le
nombra al modelo, el veto es aritmética determinista, y el error está publicado con su signo y
reproducible con un comando. El aparato de medición funciona — fue él quien encontró que el modelo
está mal, seis horas antes de la entrega y no en el Q&A.

**Lo que NO se puede seguir diciendo:** que la cascada agregada de informalidad es un hallazgo del
proyecto. Está falsada contra el dato observado. Los cuatro datos A1–A4 de `docs/PLAN.md` §1.1
dependían de ella y hay que revisarlos uno por uno con el equipo.

### La evidencia previa, que ya apuntaba aquí

**El comparador oficial, año contra año, mismo trimestre y misma fuente.** Los dos boletines del
DANE, publicados con un año de diferencia:

| Bogotá D.C., proporción de ocupados informales | abr–jun |
|---|---|
| [Boletín 13-ago-2025](https://www.dane.gov.co/files/operaciones/GEIH/bol-GEIHEISS-abr-jun2025.pdf) — **2025** (pre-política) | **35,6%** |
| [Boletín 13-ago-2026](https://www.dane.gov.co/files/operaciones/GEIH/bol-GEIHEISS-abr-jun2026.pdf) — **2026** (segundo trimestre bajo el decreto) | **33,3%** |
| **Cambio observado** | **−2,3 pp** |

Contra eso, lo que el modelo predice:

| | Informalidad Bogotá |
|---|---|
| Modelo con +23%, post-fix: ronda 0 → ronda 3 | 30,6% → **63,8%** (brecha **+33,3 pp**) |
| Banda del modelo en la ronda 3 | **47,9% – 81,8%** |
| **Observado**, proxy propio abr–jun 2026 | **30,8%** |
| **Observado**, oficial DANE abr–jun 2026 | **33,3%** |

Tres cosas, y ninguna es el resultado de V0:

1. **El observado cae fuera de la banda del propio modelo**, unos 15 pp bajo su límite inferior. La
   cobertura de M4 es **0**.
2. **El signo no coincide.** El modelo predice que la informalidad sube 33 pp; bajó 2,3.
3. **La persistencia (B1) le gana por mucho.** Predecir "2026 = 2025" da un error de **2,3 pp**. Para
   que el modelo tuviera `skill > 0` tendría que errar por menos que eso, y erra por decenas.

*Los números del modelo son la corrida post-fix del 23% (`behavior/README.md`). **Las otras seis
políticas del barrido son pre-fix y no deben citarse como vigentes.***

---

## Dónde NO hay que creerle

- Es **dinámica de mejor respuesta a 3 rondas**, no convergencia a equilibrio ni prueba de Nash. El
  modelo no converge: en la corrida del 23% la informalidad hace 59,0 → 87,5 → 63,8, y así se reporta.
- **No es un modelo macro.** Inflación, crecimiento y tasa de cambio son exógenos observados.
- El **factor prestacional** (1,4–1,5) es un parámetro, no un dato, **y el candado 4 cambia de signo
  dentro de ese rango.**
- Los agentes de un mismo arquetipo se suponen **intercambiables en su conducta** ([ADR 0002](docs/adr/0002-llm-por-arquetipo.md)).
- La informalidad del modelo es un **proxy de cotización a pensión**, ≈2,1 pp por debajo de la
  definición oficial del DANE, que hoy no podemos reproducir.
- El determinismo es **relativo a la caché**: mismo seed + misma caché + mismas versiones
  ([ADR 0009](docs/adr/0009-frontera-del-determinismo.md)). Sin caché, la capa LLM no es determinista.

## Supuestos tomados

Los diez del motor están en el registro S1–S10 de `engine/MODELO.md`. Los dos que más mueven el
número: **S2** (inspecciones por inspector, que fija `C` y con ella la cascada) y **S8** (la caja de
la ronda: con 1 mes daba 96 vetos, con 3 meses da 0, y el empleo de la ronda 3 pasa de 100% a 85,7%).

```bash
grep -rn "SUPUESTO:" engine behavior data scripts
```

## Trabajo futuro (nombrado, no fingido)

- Reproducir la definición oficial del DANE (exige el módulo de independientes).
- Refutación causal formal (DoWhy) y calibración bayesiana / MSM (`sbi`) — fuera de las 36 horas.
- Efecto faro y elasticidades de literatura como nivel 2 de calibración.
