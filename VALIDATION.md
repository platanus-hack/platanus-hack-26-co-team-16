# Validación — ¿por qué creerle a esta simulación?

> **Qué es este archivo.** El criterio de éxito de la simulación, **escrito antes de correrla**, y el
> número que salió al correrla. Dueño formal: Juanda (R5); esta versión la armó Alejo (R1) en la 8ª
> sesión **sobre** el trabajo de `rol/correcciones-simulacion-limpia`, que no se pisó. Necesita aviso
> en el grupo: toca un documento raíz.
>
> **Por qué el orden importa.** Un umbral escrito después de ver el resultado no es un umbral, es una
> racionalización. El criterio se commiteó en `2d4aa7e` con los datos de 2025 todavía sin descargar;
> el número llegó después. Verificable con `git log --date=iso -- VALIDATION.md`.
> **Regla del proyecto: el número se publica salga como salga.** Un backtest negativo pero medido y reportado con honestidad sigue siendo el resultado más serio de la sala, porque el resto va a presentar cifras que nadie puede refutar.
> Metodología completa: `docs/PLAN.md` §5.

## EL número

**Corrido el 2026-08-22, después del pre-registro. Ningún umbral se movió para llegar aquí.**

```
Error del backtest:            37,37 pp   (firmado modelo - observado: +37,37 pp)
Skill vs persistencia (B1):    -8,182
Cobertura del rango:           NO
Ancho del rango:               33,9 pp  (entre parafrasis, NO calibrado)
Corridas:                      BLOQUEADO - el repo no registra N>=5 trayectorias comparables

Proxy Bogota, GEIH 2025 ene-jun:   34,64 %
Proxy Bogota, GEIH 2026 ene-jun:   30,57 %
Delta observado:                   -4,07 pp
Delta predicho por el modelo:     +33,3  pp
```

Reproducible con: `make validate` · sale con código **1** mientras haya compuertas bloqueadas.

### Veredicto: **rama B — la cascada agregada está falsada**

El modelo predice que la informalidad de Bogotá **sube 33 puntos** con el alza del 23%; **bajó 4**.
Signo contrario, un orden de magnitud, el observado **fuera del propio rango del modelo**, y **la
persistencia le gana ocho veces**: predecir "2026 = 2025" erra por 4,07 pp y el modelo por 37,37.

**Dos escalas independientes coinciden, así que no es artefacto del proxy:**

| Escala | 2025 → 2026 | Cambio |
|---|---|---|
| Proxy propio, mismo código en los dos extremos, ene–jun | 34,64% → 30,57% | **−4,07 pp** |
| Oficial DANE, abr–jun | 35,60% → 33,30% | **−2,30 pp** |

Distinta definición, distinto trimestre, misma dirección y mismo orden de magnitud.

Un chequeo independiente de que el pipeline lee bien la realidad: el pico salarial se movió solo, de
**1.420.000** en 2025 a **1.750.000** en 2026 — sigue al mínimo legal de cada año (1.423.500 y
1.750.905) sin que nadie se lo dijera. El patrón P3 se sostiene en los dos años.

**Qué NO se puede seguir diciendo:** que la cascada agregada es un hallazgo del proyecto.
`behavior/README.md` todavía afirma que *"el dato A1 aguanta: las siete políticas dan una brecha de
+28 a +45 pp"*. Contra el dato observado esa afirmación está falsada, y los datos A1–A4 de
`docs/PLAN.md` §1.1 dependían de ella. **Hay que revisarlos con el equipo.**

**Qué sobrevive, y no es poco:** población real y verificable, la política jamás nombrada al modelo,
el veto como aritmética determinista, y un error publicado con su signo que se reproduce con un
comando. El aparato de medición funciona — fue él quien encontró que el modelo está mal, antes del
Q&A y no durante.

---

## Cómo se decide si pasó: compuertas y mediciones

**Compuerta:** si falla, lo que viene después no significa nada. Es binaria.
**Medición:** se publica el número que salga, sin pasa/falla.

Convertir en medición algo que era compuerta es exactamente cómo se fabrica un "todo salió bien".

| # | Candado | Tipo | Umbral, fijado ANTES de correr | Estado |
|---|---|---|---|---|
| **G1** | Reproducibilidad | Compuerta | Dos corridas con el mismo `(seed, manifiesto de caché, versiones)` dan salida idéntica | 🔴 **tres bloqueos**, no uno: `anthropic` sin fijar · falta `scripts/run_simulacion.py` · falta el artefacto canónico y el manifiesto de caché |
| **G2** | No contaminación | Compuerta | `python -m behavior.higiene` sale 0 **y** el re-skinning mueve el agregado ≤ el ancho del rango entre paráfrasis | 🟡 higiene ✅; `Reskin` implementado (`behavior/capa.py`, `demo.py --reskin`) pero **falta correr y registrar el par canónica/re-skinneada** |
| **G3** | Calibración base | Compuerta | Informalidad total dentro de **±2 pp** del objetivo de `momentos.json`, **y** se respeta el orden micro > pyme > grande | 🔴 **no existe productor**: ningún script genera la corrida sin política que el candado necesita |
| **M1** | Backtest | Medición | Se publica. Sin umbral | ✅ **37,37 pp** |
| **M2** | Habilidad | Medición | Se publica, incluso negativo | ✅ **skill −8,182** |
| **M3** | Ablación | Medición | Se publica con su sensibilidad al factor prestacional | ✅ y ya **no** depende de ese factor (ver Candado 4) |
| **M4** | Rango entre paráfrasis | Medición | Cobertura **y** agudeza, siempre juntas | ✅ cobertura **0**, ancho 33,9 pp. **No es un p10/p90 calibrado** (ver *Método*) |

**Por qué G3 con ±2 pp.** El candado 1 es la condición de que todo lo demás signifique algo
(`docs/IDEA.md` §5.5). Laxo lo vuelve decorativo; apretado invita a ajustar parámetros hasta pegarle,
que es el riesgo que `docs/PLAN.md` §10 ya nombró. ±2 pp es holgado frente al ruido muestral de la
GEIH y estrecho frente a la brecha de 33 pp que estaba en disputa.

## Candado 1 · Calibración base

_PENDIENTE — el mundo corre SIN política y debe reproducir lo observado en la GEIH: informalidad por sector y tamaño de firma, distribución salarial, y el spike de masa salarial en el mínimo. Qué reprodujo y qué no._

### Objetivos de calibración con fuente (V8 — encontrado en H+1)

Los momentos contra los que se calibra no los escogemos nosotros: salen de literatura publicada y se citan acá antes de correr nada.

| Objetivo | Valor | Fuente | Uso |
|---|---|---|---|
| Elasticidad mínimo → informalidad | **+1 pp** en el ratio del mínimo ≈ **+0,21 pp** de probabilidad de empleo informal | Banco de la República, [WP 1104](https://ideas.repec.org/p/bdr/borrec/1104.html) — *Minimum wage effects on labour informality: heterogeneity across demographic groups in Colombia* | Nivel 2 de calibración. Si nuestra curva no pasa cerca de esta pendiente en el tramo bajo, algo está mal en el motor. |
| Heterogeneidad demográfica | Efecto concentrado en 18–25 años con menor educación | Misma fuente | Chequeo del mapa distributivo (dato A3): el efecto debe caer donde la literatura dice. |
| Informalidad de referencia — **la del candado 1** | **30,57%** (Bogotá, GEIH 2026 ene-jun, ponderada por factor de expansión) | `data/momentos.json`, calculado por `data/construir_poblacion.py` | Candado 1, nivel base. **Es el objetivo que el modelo tiene que reproducir en la ronda 0.** |
| Informalidad nacional de contexto | ~55–60% | Serie oficial DANE (✅ insumo jdtorres) · OIT | Solo contexto. **NO es comparable con la fila de arriba**: universo distinto (nacional vs Bogotá) y definición distinta (la nuestra usa proxy de cotización a seguridad social). Citar una donde va la otra es un error de 25 puntos. |
| Razón mínimo / salario mediano | ≈90% (Kaitz alto) | OIT | Contexto: explica por qué el mínimo colombiano muerde tanto. ⚠️ verificar cifra exacta y año antes de usarla en el pitch. |

### El objetivo, verificado contra el boletín oficial

La fila del candado 1 se confirmó contra la fuente primaria, no contra prensa:
[*Ocupación informal, trimestre abril–junio 2026*](https://www.dane.gov.co/files/operaciones/GEIH/bol-GEIHEISS-abr-jun2026.pdf)
(DANE, 13-ago-2026).

| Ámbito, abr–jun 2026 | |
|---|---|
| Total nacional | **54,5%** ← de aquí sale el ~55–60% de contexto |
| 13 ciudades y A.M. | 40,7% |
| **Bogotá D.C.** | **33,3%** ← la más baja de las 23 ciudades |

**Y cuánto se parece nuestro proxy a la definición oficial.** El DANE dice, textual:

> *"se considera como ocupados informales a todos los asalariados o empleados domésticos que no
> cuentan con cotizaciones a salud ni a pensión por concepto de su vínculo laboral con el empleador
> que los contrató. De igual forma [...] los Trabajadores por cuenta propia y Patrones o empleadores
> que hayan quedado clasificados en el sector Informal."*

| Medida, Bogotá | Valor |
|---|---|
| Proxy del repo, ene–jun, con filtro de ingreso | **30,57%** (el de `momentos.json`) |
| Proxy del repo, abr–jun, mismo filtro | 30,81% |
| Oficial DANE, abr–jun | 33,3% |
| **Brecha proxy − oficial** | **≈ −2,1 pp** |

**No podemos reproducir hoy la definición oficial**, por una razón concreta: clasificar a un
independiente en sector formal o informal exige saber si su unidad está registrada, y `P3045S1`
**solo se le pregunta a los asalariados** — los 2.315 independientes de la muestra la tienen vacía.
Reconstruirla exige variables del módulo de independientes que hoy no se extraen.

**Consecuencia de diseño, y es la central del backtest:** se puntúa **proxy contra proxy, con el
mismo código en los dos extremos**. Si el predicho saliera del proxy y el observado de un boletín, no
se mediría error del modelo sino deriva de definición. Los 2,1 pp contra el DANE quedan como
**limitación declarada**, no como fallo de validación.

**El matiz que importa para el pitch:** la elasticidad publicada es *una recta*. Nuestro aporte declarado (dato A2 del plan) es si existe un **codo** — un umbral donde la cascada se dispara y la recta deja de valer. Reproducir la recta en el tramo bajo es lo que nos da derecho a hablar del codo en el tramo alto.

## Candado 2 · Backtest fuera de muestra — el diseño V0

**La política del caso demo ya ocurrió.** El decreto 1469/2025 rige desde el 1-ene-2026 y la GEIH
2026 ene–jun es **posterior**. El modelo no necesita esperar a nada para ser puntuado.

```
GEIH 2025 (catalogo 853) --construir_poblacion.py, mismo codigo--> proxy PRE-politica  34,64 %
GEIH 2026 (catalogo 900) --el mismo script, sin cambios---------->  proxy POST         30,57 %

                         Delta observado = -4,07 pp
                         Delta predicho  = +33,3 pp
```

Verificado: 2025 tiene la misma estructura de variables que 2026 (`P3069`, `P6920`, `P6430`,
`P6426`, `P6800`, `INGLABO`, `FEX_C18`, `RAMA2D_R4`), así que no hay armonización de por medio. Y es
fuera de muestra de verdad: la población se instancia con 2025 y el modelo nunca ve 2026. El control
de contaminación se sostiene porque al LLM jamás se le nombra la política.

**Se excluyen 2020-2021** (COVID rompe cualquier backtest laboral) y se dice explícitamente: eso suma
credibilidad. Un segundo punto (GEIH 2024 → +9,5% → puntuar contra 2025) daría n=2, que sigue siendo
delgado y hay que decirlo.

### 🔴 Lo que V0 destapó: la ronda 0 está mal etiquetada

El modelo llama a su ronda 0 *"la proyección oficial, cumplimiento total"* y la inicializa con
**30,57%**. Pero ese dato se midió en GEIH 2026 ene–jun, o sea **seis meses después del decreto**: ya
contiene la adaptación que hubo. No es el contrafactual de cumplimiento total, es el resultado
observado. Sin la población de 2025, el punto de partida y el objetivo eran el mismo dato.

### Los baselines — el "¿mejor que qué?"

Un número de error sin baseline no dice nada.

| | Baseline | Qué predice | Resultado |
|---|---|---|---|
| **B0** | Proyección oficial | Informalidad sin cambio | El hombre de paja. Ganarle no prueba nada |
| **B1** | **Persistencia** | 2026 = 2025 | **Error 4,07 pp.** Le gana al modelo ocho veces |
| **B2** | Elasticidad econométrica | +0,21 a +0,99 pp por +1 pp del ratio | Es una recta; el aporte declarado (A2) era que hubiera un codo |

`skill = 1 - (error_modelo / error_baseline)`. Negativo es peor que el baseline, y se publica igual.

**Cómo se puntúa:** error absoluto en pp, **y el signo aparte** — acertar la magnitud con el signo
cambiado no es acertar. La banda se juzga por cobertura **y** agudeza a la vez: la cobertura sola se
gana siendo vago.

## Candado 3 · Control de contaminación de entrenamiento

_PENDIENTE — el doble mecanismo:_

**(a) Al modelo nunca se le nombra la política.** No ve "salario mínimo", ni "decreto", ni años. Solo la mecánica: *"tu costo laboral por empleado formal sube X%"*. Si el efecto agregado emerge igual, no es memoria.

**(b) Test de re-skinning.** La misma corrida con sectores y unidades renombrados a etiquetas inventadas debe dar el mismo agregado. Si difiere, hubo memorización, y lo reportamos nosotros antes de que lo pregunten.

**Resultado:**

**(a) ✅ implementado y activo.** `behavior/higiene.py` lo hace cumplir con 31 patrones y mata la
corrida si algo se filtra, sin bandera para desactivarlo.

**(b) 🟡 implementado, sin corrida comparativa registrada.** `Reskin` vive en `behavior/capa.py` y se
activa con `python -m behavior.demo --reskin`: renombra los sectores y **reescala todos los montos
por un factor derivado del seed**. Ese segundo mecanismo importa más de lo que parece — la higiene
filtra *términos*, no *magnitudes*, y los montos viajaban en pesos reales con la moda del parquet en
1.750.000, que es exactamente el piso salarial de 2026. Un modelo con memoria del país podía
reconocer el escenario por los números aunque nunca leyera su nombre.

**Lo que falta es correrlo y guardar el par:** la corrida canónica y la re-skinneada, para poder
compararlas. Hasta que ese par exista, el candado está implementado pero no medido, y se reporta así.

## Candado 4 · Ablación del LLM

Corrida con la capa conductual sustituida por reglas fijas. Si el resultado no cambia, el LLM no
aporta y hay que decirlo.

**Estado: medido, y ya no depende del factor prestacional.** Con la grilla real de empleadores el
resultado es estable en todo el rango 1,35–1,58 (ver *"Lo que sí mejoró"* más abajo). Antes se
volteaba en 1,4309 — el signo del candado dependía de un parámetro que el propio repo declaraba
incierto, y esa fragilidad quedó cerrada.

## Prueba opcional · Pico y placa

_PENDIENTE, condicionada a que C4 haya cerrado. A los agentes solo la mecánica ("no puedes usar tu vehículo 2 días a la semana"), jamás el nombre. Si emerge sola la estrategia "comprar un segundo carro barato", no es memoria. Corrida cualitativa: la salida es la decisión, no tiempos de viaje. Si no emerge, se reporta igual acá y no se menciona en el pitch._

## Método

- La barra de error se construye sobre **N≥5 paráfrasis del prompt**, no sobre temperatura.
- Se reporta **varianza además de media**: los LLM colapsan varianza, y lo decimos nosotros primero.
- **Ningún número sale sin banda.**

🔴 **La banda está mal nombrada, y hay que arreglarlo antes de publicar cualquiera.** Con N=5, el
`p10`/`p90` que emite `behavior/rondas.py` es literalmente **el mínimo y el máximo** de las cinco
(`k10 = int(0,10*4) = 0`, `k90 = round(0,90*4) = 4`). En esperanza son los percentiles **16,7 y
83,3**, no 10 y 90. Y promediar sobre paráfrasis y seeds a la vez es pseudorreplicación: son dos
fuentes de variación distintas. Lo correcto y barato: llamarlo **"rango entre paráfrasis"**, mostrar
las cinco curvas, y reportar la dispersión entre seeds por separado.

## Dónde NO hay que creerle

Los límites, escritos antes de que los pregunten. **No basta con decir "no lo
modelamos": hay que decir hacia dónde empuja la omisión.** Un límite con dirección
de sesgo es un dato sobre nuestro propio resultado; sin ella es una excusa.

| Lo que falta | Por qué no se agrega | **Hacia dónde sesga el resultado** |
|---|---|---|
| Productividad, demanda, capital, salario de eficiencia | Son piezas nuevas, no campos apagados: cero menciones en todo el código. El canal *"sube el mínimo → sube la productividad → baja el desempleo"* **no puede emerger** de este motor | Sin canales positivos, nuestra informalidad es una **cota superior** y nuestro empleo una **cota inferior**. Si el modelo se equivoca, se equivoca exagerando el daño |
| Tasa de desempleo | `data/momentos.json` solo trae ocupados: no hay fuerza laboral ni desocupados con los que construir el denominador | **No se reporta en ninguna forma.** Solo *empleo relativo a la línea base*. Decir "el desempleo sube a X%" sería sobreventa y es la palabra que más fácil nos hunde en el Q&A |
| Efecto faro sobre salarios informales | El alza solo encarece el lado formal; en la realidad los salarios informales cercanos al piso también suben | **Sobreestima la informalización**: si evadir también se encarece, evadir alivia menos de lo que decimos |
| Convergencia a equilibrio | Son 3 rondas de mejor respuesta (decisión D5), no una prueba de existencia de Nash | Se reporta como dinámica, nunca como equilibrio. Desde A5 además con la etiqueta de si la corrida **se estabilizó** o no |
| El despido como cálculo y no como muro | El agente propone y el motor veta; nunca compara "despedir vs. mantener" por costo esperado | Con A3 el agente al menos ve la caja correcta (la del periodo, la misma que juzga el veto). El mecanismo sigue siendo una restricción material, y así se dice |
| Traslado a precios como inflación | `traslado_precios_pct` es lo que las firmas **declaran** que trasladarían. No hay respuesta de demanda ni elasticidad | **No es un pronóstico de inflación.** Una firma que declara que subirá 10% puede no poder hacerlo. La cifra se publica con ese nombre pegado |
| Cuenta propia (23% de los ocupados) | `data/empresas.parquet` excluye a quien trabaja solo: no tiene a quién despedir ni a quién informalizar | El agregado cubre a los **3.235.639 ocupados con empleador**, no a los 4,2 millones. Se reporta aparte con su peso, en vez de dejar que el número se lea como si fuera toda la ciudad |
| El costo de la fiscalización sobre el Estado | Fuera de alcance declarado | Ninguno sobre las cifras publicadas |

### Dos parámetros que mueven el resultado y no tienen fuente

Se nombran acá porque son los que un juez debería atacar primero, y preferimos
señalarlos nosotros:

1. **El margen libre sobre nómina (0,18).** Es un supuesto heredado del andamio que
   `data/construir_empresas.py` declara como tal, con rango de barrido 0,05-0,40.
   Decide **dónde** cae el codo: con 0,18 y factor 1,40, absorber deja de ser
   pagable por encima de un alza de ~12,9%. Lo que el modelo dice es que **existe**
   un codo donde el margen libre se agota; **dónde** cae depende de un parámetro que
   no observamos, y por eso va con barrido y no con una cifra.
2. **La sanción equivalente a 12 meses de ingreso** (`multa_factor`). Decide si
   evadir paga. Su barrido es de R5.

### Lo que sí mejoró y cómo se verifica

- El **factor prestacional** ya no decide el signo del candado 4. Con la grilla real
  de empleadores —cada celda con su factor entre 1,3835 y 1,5829— el resultado es
  estable en todo el rango 1,35-1,58 (`python3 -m behavior.pruebas`, crítico #3).
  Antes se volteaba en 1,43, y esa fragilidad era el defecto §3.3.
- Los agentes dentro de un arquetipo se siguen suponiendo **intercambiables en su
  conducta** ([ADR 0002](docs/adr/0002-llm-por-arquetipo.md)). La heterogeneidad la
  pone la GEIH, no el LLM.

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

> Lo de arriba es **la transcripción literal del commit `2d4aa7e`**, sin una coma cambiada.
> Verificable:
> `diff <(git show 2d4aa7e:VALIDATION.md | sed -n '/^## Las dos ramas/,/^### Lo que ya se sabe/p') ...`
> Lo de abajo se escribió **después** de conocer el número, y por eso va separado.

**Se activó la B.** `error = 37,37 pp`, `skill = −8,182`, cobertura `NO`: ninguna de las dos
condiciones de la rama A se cumple, ni de cerca. Los tres movimientos se aplican tal como están
escritos arriba, sin agregar ninguno.

## Supuestos tomados

Todos los supuestos del código están marcados y son auditables:

```bash
grep -rnI --exclude-dir=__pycache__ "SUPUESTO:" engine behavior data api web scripts tests
# o, lo mismo con un nombre:  make supuestos
```

_Consolidar acá los que importan, con su impacto._

## Trabajo futuro (nombrado, no fingido)

- Refutación causal formal (DoWhy) — fuera de las 36 horas.
- Calibración bayesiana / MSM formal (`sbi`) — la calibración contra momentos cubre el nivel 1.
- Efecto faro y elasticidades de literatura como nivel 2 de calibración.
