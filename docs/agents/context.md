# Glosario del dominio — la lengua común

Este archivo es **solo un glosario**: qué significa cada palabra. Sin implementación (eso es el código), sin decisiones (eso es `docs/adr/`), sin alcance (eso es `docs/PLAN.md`).

Existe porque cinco agentes que nombran distinto la misma cosa producen cinco modelos distintos. Antes de nombrar una variable, una función o un archivo, mira si el término ya está acá. Si acuñas uno nuevo, agrégalo en el mismo PR.

Los términos de abajo salen de `docs/PLAN.md`, no están inventados.

## Lengua

**Agente**
Una persona real anonimizada de la GEIH, instanciada en la simulación con sus atributos observados (sector, tamaño de empresa, ingreso, formalidad, educación, factor de expansión).
*Evitar:* individuo, entidad.

**Arquetipo**
Un grupo de agentes que comparten sector × tamaño de empresa × formal/informal × tramo de ingreso. Son ~40-60 y son la unidad a la que se le llama al LLM (nunca al agente individual).

**Factor de expansión**
El peso muestral que trae cada registro de la GEIH: a cuántas personas de la población real representa ese encuestado. Es de dónde sale la escala del proyecto, no del runtime.

**Momento**
Una estadística observada en los datos reales contra la cual se calibra el modelo (informalidad por sector, distribución salarial). Vive en `data/momentos.json`.

**Motor físico**
La capa determinista que calcula costos, flujo de caja y fiscalización. No opina ni propone: acepta o rechaza.

**Veto de factibilidad**
El veredicto del motor sobre una estrategia propuesta por la capa LLM: factible o no, con razón. Es la interfaz entre la creatividad y la física: el LLM inventa lo que un economista no enumeraría, el motor mata lo que la plata no permite.

**Ronda**
Un ciclo de mejor respuesta: los arquetipos ven el agregado, proponen estrategia, el motor veta o aplica, y se recalcula la fiscalización. La simulación son 3-4 rondas.

**Mejor respuesta**
La decisión de cada arquetipo dada la conducta observada de los demás en la ronda anterior. **No** es convergencia a equilibrio, y no se llama así en ningún texto del proyecto.

**Cascada**
El efecto de retroalimentación que produce el resultado no obvio: como la capacidad de fiscalización es fija, más evasores bajan la probabilidad de sanción de cada uno, lo que induce más evasión.

**Fiscalización endógena**
La probabilidad de sanción calculada dentro del modelo (capacidad fija ÷ universo de evasores), en vez de fijada como parámetro externo.

**Brecha**
La distancia entre la proyección oficial (que asume cumplimiento total) y el resultado simulado. Es el dato A1 y la imagen central del pitch.

**El codo**
El punto del barrido de `aumento_pct` donde la cascada se dispara. Dato A2: si existe, el debate deja de ser "23 vs 13,6" y pasa a ser "antes o después del umbral".

**Contaminación (de entrenamiento)**
Que el LLM reproduzca de memoria un resultado histórico que ya conoce, en vez de simularlo. Se combate no nombrándole nunca la política, solo la mecánica.

**Re-skinning**
El test de contaminación: correr lo mismo con sectores y unidades renombrados a etiquetas inventadas. Si el agregado cambia, hubo memorización.

**Ablación**
Correr la simulación sustituyendo la capa LLM por reglas fijas. Si el resultado no cambia, el LLM no está aportando.

**Backtest**
Predecir un alza histórica del salario mínimo ya ocurrida, sin dejar ver el resultado, y publicar el error. Se excluyen 2020-2021 por COVID.

---

## Términos añadidos por R2 (2026-08-22, rama `rol/backend`)

Salen de [`docs/IDEA.md`](../IDEA.md) y de los ADR 0005-0009. Se agregan acá siguiendo la
regla de arriba: quien acuña un término lo registra en el mismo PR.

**Ronda (precisión)**
Ya estaba definida como un ciclo de mejor respuesta. Ahora tiene reloj: **una ronda es un
trimestre**, y el horizonte de una corrida son nueve meses desde el decreto
([ADR 0005](../adr/0005-el-reloj-de-la-simulacion.md)).
*Evitar:* "tick", "paso", "iteración".

**Agregado**
El resumen del estado del sistema que los arquetipos ven al inicio de cada ronda: tasa de
evasión y probabilidad de sanción vigente. **Es lo único que ven** — nadie observa agentes
individuales. Es el mecanismo por el que la cascada ocurre sin costo cuadrático.
*Evitar:* "estado global", "contexto".

**EstadoFiscalizacion**
La capacidad de inspección del período (inspectores efectivos × inspecciones por inspector
por trimestre × fracción del universo). Es **estado del mundo, no parte de la política**, y
**no es una palanca del usuario** ([ADR 0006](../adr/0006-fiscalizacion-es-estado-del-mundo.md)).
*Evitar:* llamarla "parámetro de fiscalización", que sugiere que se ajusta.

**Capacidad (`C`)**
El número esperado de inspecciones efectivas en un trimestre. Es el numerador de la
probabilidad de sanción y el supuesto más importante del motor.

**Prima de protección**
Cuánto vale para el trabajador la protección del empleo formal (pensión, salud, cesantías),
expresada como fracción del salario. Es lo que decide si acepta una oferta informal
([ADR 0008](../adr/0008-asimetria-firma-trabajador.md) 🔶).

**Estrategia terminal**
La estrategia a la que cae un arquetipo cuando el veto le rechaza tres propuestas seguidas:
**cumplir**. Se cuenta en `n_fallback`, y un `n_fallback` alto significa que el veto está
demasiado apretado, no que todos decidieron cumplir.

**Mejor respuesta con rezago**
Precisión de "mejor respuesta": los arquetipos deciden contra el agregado de la ronda
**anterior**, no contra el de la actual. No resolvemos un punto fijo simultáneo, y por eso
nunca decimos "equilibrio".

**Corrida de control**
La corrida con `p` **fijo** (sin fiscalización endógena). Si la cascada aparece igual, viene
de otra parte. Es distinta de la **ablación**, que quita el LLM, no la endogeneidad.
