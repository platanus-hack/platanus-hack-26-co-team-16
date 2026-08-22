# Índice de `docs/` — qué leer y con cuánta autoridad

Todo lo que un agente o una persona necesita para trabajar en este repo está acá. **Los documentos no valen lo mismo**: esta tabla dice cuáles mandan y cuáles son historia. Si dos se contradicen, gana el de más autoridad.

## Vigente y normativo — esto manda

| Documento | Qué es | Cuándo leerlo |
|---|---|---|
| [`EXPLICACION-SIMPLE.md`](EXPLICACION-SIMPLE.md) | **Todo el proyecto sin jerga**, en dos partes: la promesa y el producto · por qué está bien construido. Para explicárselo a alguien que llega de cero, y para ensayar el pitch. | Si es tu primer contacto con el proyecto |
| [`IDEA.md`](IDEA.md) | **La espina dorsal.** La idea completa y llenada: las 5 W y la H, propuesta de valor, la anatomía de la simulación (estado del mundo, actores, Δt, palanca, métricas), el flujo punta a punta y lo que NO es. Si solo vas a leer un documento del repo, es este. | Antes que `PLAN.md` si estás llegando |
| [`PLAN.md`](PLAN.md) | **La fuente de verdad del producto.** Qué se construye, decisiones D1-D10, arquitectura, validación, cronograma, lo que NO se construye. | Antes de escribir cualquier línea de código |
| [`ROLES.md`](ROLES.md) | Quién es dueño de qué carpeta, en qué rama, con qué entregables y en qué hora | Al arrancar tu sesión |
| [`prompts/`](prompts/) | El prompt de arranque de cada persona + el orden de desbloqueo entre roles | Primer mensaje de tu sesión de agente |
| [`FLUJO.md`](FLUJO.md) | Diagramas: cómo corre una simulación y cómo corre la validación | Cuando necesites el panorama |
| [`UML.md`](UML.md) | La estructura de la idea | Junto con FLUJO |
| [`investigacion/`](investigacion/) | **El fundamento del backend, en tres esferas:** teórica (papers y métodos probados), tools (stack y estándares), live (empresas y productos vivos). Cada entrada dice qué nos sirve, **qué no**, y dónde aterriza en `engine/`. | Antes de escribir una función del motor |
| [`../engine/MODELO.md`](../engine/MODELO.md) | El mapa *teoría → archivo → función → test → supuesto*, más el registro de supuestos pre-declarado | Antes de tocar `engine/` |
| [`adr/`](adr/) | Decisiones de arquitectura **con las alternativas descartadas y su porqué** | Antes de cambiar un área ya decidida. No se re-litigan |
| [`agents/context.md`](agents/context.md) | El glosario del dominio | Antes de nombrar una variable, función o archivo |
| [`agents/handoff-<tu-nombre>.md`](agents/) | Tu memoria entre sesiones | Al abrir y al cerrar cada sesión |
| [`agents/handoff.md`](agents/handoff.md) | Qué está mergeado en `main` + el roadmap transversal | Cuando quieras saber el estado real |

El contrato de trabajo (dueños, ramas, PR, restricciones no-negociables) está un nivel arriba, en [`../AGENTS.md`](../AGENTS.md), porque lo carga toda herramienta de agentes automáticamente.

## Materia prima — se consulta, no manda

| Carpeta | Qué es |
|---|---|
| [`fuentes/`](fuentes/) | Los 5 insumos individuales **escritos antes de que la idea existiera**. Consolidados y extendidos en [`investigacion/`](investigacion/), que es la que manda para decisiones de motor. Los 5 insumos de investigación individuales (`alejo`, `dani`, `juanda`, `manuel`, `nico`) que se fusionaron en `PLAN.md`. Útiles para el detalle y las fuentes citadas de cada afirmación. **Donde difieran de `PLAN.md`, gana `PLAN.md`.** |

## Historia — superado, se conserva por trazabilidad

| Archivo | Qué es |
|---|---|
| [`historia/brainstorm.md`](historia/brainstorm.md) | La exploración inicial: seis ideas candidatas, incluida la de TransMilenio. **Superado por `PLAN.md`.** No saques ideas de acá: las que sobrevivieron ya están en el plan y las descartadas están descartadas por una razón escrita ([ADR 0004](adr/0004-geih-y-salario-minimo.md), `PLAN.md` §9). |
| [`historia/transcript-kickoff.md`](historia/transcript-kickoff.md) | Autotranscripción del kickoff, calidad baja. Vacío por ahora. |

## Cómo encontrar algo rápido

```bash
grep -rn "SUPUESTO:" .          # todos los supuestos tomados en el código
grep -rn "PENDIENTE" docs/ *.md # todo lo que falta por llenar
ls docs/adr/                    # por qué se decidió cada cosa
```
