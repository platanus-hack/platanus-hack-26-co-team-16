# team-16 · Simulador de cumplimiento de política pública

Simulador que no responde *"¿funciona la política?"* sino **"¿cuánta gente la cumple y a quién le cae encima?"**. La población se instancia desde personas reales anonimizadas de los microdatos de la GEIH (DANE), no se inventa nadie. Un motor determinista con seed calcula costos y **veta** las reacciones imposibles que propone una capa LLM que descubre estrategias de adaptación. Los agentes deciden en 3-4 rondas de mejor respuesta: como la capacidad de fiscalización es fija, más evasión baja la probabilidad de sanción y produce una **cascada** que el modelo oficial no ve. Caso demo: el aumento del salario mínimo del 23% en Bogotá.

> **Qué es este archivo.** El contrato del repositorio. Lo leen dos audiencias y sirve a las dos: los agentes de código del equipo (5 personas trabajando en paralelo, cada una en su sesión) y quien revise el proyecto. Documenta el estado real; no intenta dirigir a ningún lector.
>
> **Fuente de verdad del producto:** [`docs/PLAN.md`](docs/PLAN.md). Este archivo no lo duplica, lo indexa. Si los dos se contradicen, gana `PLAN.md` y este se corrige.

## Si solo lees un archivo

`engine/rondas.py` — el bucle de mejor respuesta y el veto de factibilidad. Es donde vive la tesis del proyecto. *(PENDIENTE hasta H+10; hasta entonces la referencia es `docs/FLUJO.md`.)*

## Cómo verificarlo tú mismo

| Comando | Qué hace |
|---|---|
| `make run` | Corre una simulación completa |
| `make test` | Tests del núcleo determinista |
| `make validate` | Los 4 candados de validación e **imprime EL número** del backtest |
| `python scripts/reproduce.py` | Reproduce el resultado principal con un comando |

*(PENDIENTE: `Makefile` y `scripts/reproduce.py` son entregables de R5.)*

**Determinismo:** mismo seed, mismo resultado. Verificable corriendo `make run` dos veces.

## Qué NO hace

Límites declarados, no omisiones. La tabla completa está en `docs/PLAN.md` §9 y el dominio del motor en §4.2.

- **No es un modelo macro.** Inflación, crecimiento y tasa de cambio entran como datos exógenos observados, nunca como resultado.
- **No prueba convergencia a equilibrio.** Son 3 rondas de dinámica de mejor respuesta, y así se reporta.
- **No optimiza políticas.** Evalúa la política que se le dé; no busca la mejor.
- **No cubre física de flujo** (tráfico, evacuación, contagio). El motor sirve a una clase de problema: cambio de costos/incentivos + capacidad de fiscalización + población, donde incumplir es una opción.
- **No entrega el futuro, entrega el rango** con banda de incertidumbre y con el error del backtest publicado.

## Mapa de archivos

```
docs/README.md       índice de la documentación: qué leer y con cuánta autoridad — EMPIEZA AQUÍ
docs/PLAN.md         el plan completo — la fuente de verdad del producto
docs/ROLES.md        quién hace qué, en qué carpeta, en qué rama
docs/prompts/        prompt de arranque por persona + orden de desbloqueo entre roles
docs/FLUJO.md        diagramas de la corrida y de la validación
docs/UML.md          estructura de la idea
docs/agents/         contexto para agentes: handoff por persona + glosario
docs/adr/            decisiones de arquitectura y por qué (con alternativas descartadas)
docs/fuentes/        los 5 insumos de investigación que se fusionaron en el plan
docs/historia/       brainstorm y transcript — superados, se conservan por trazabilidad
contracts/           los 3 JSON de ejemplo — la especificación viva, congelada en H+4
data/                ingesta GEIH -> poblacion.parquet + momentos.json
engine/              EL CORAZÓN: costos, fiscalización endógena, veto, rondas, seed
behavior/            capa LLM: prompts por arquetipo, caché, presupuesto
api/                 FastAPI: POST /simulaciones -> persiste rondas en Supabase
web/                 Next.js: slider, curva de cascada, mapa distributivo, feed
tests/ scripts/      núcleo verificable + reproducción
ARCHITECTURE.md      las capas, el veto, y las alternativas descartadas con su porqué
VALIDATION.md        los 4 candados, el número, y dónde no hay que creerle
```

## Módulos y dueños

Un dueño por carpeta. **Nadie edita la carpeta de otro.** Los agentes de código respetan límites de carpeta mucho mejor que los acuerdos verbales: díselo a tu agente en el primer mensaje de la sesión. Detalle completo y prompts de arranque en [`docs/ROLES.md`](docs/ROLES.md).

| Quién | Rol | Dueño exclusivo de | Rama | No toca |
|---|---|---|---|---|
| **Alejo** | R1 · Datos / población | `data/`, `contracts/` | `rol/datos` | `engine/`, `behavior/`, `web/` |
| **Manuel** | R2 · Backend: motor + API | `engine/`, `api/` | `rol/backend` | `behavior/`, `web/`, `data/` |
| **Nico** | R3 · Conductual + equilibrio | `behavior/` | `rol/conductual` | `engine/`, `web/`, `data/` |
| **Dani** | R4 · Diseño e interfaz | `web/` | `rol/interfaz` | `engine/`, `behavior/`, `data/`, docs raíz |
| **Juanda** | R5 · Integración / validación / pitch | `tests/`, `scripts/`, `Makefile`, docs raíz, deploy | `rol/integracion` | `engine/`, `behavior/`, `web/`, `data/` (los lee, no los edita) |

**Camino crítico:** Alejo (H+2 GEIH → H+8 `poblacion.parquet`). Nadie lo bloquea; él bloquea a todos.

El prompt de arranque de cada sesión está en [`docs/prompts/<nombre>.md`](docs/prompts/) y el orden de desbloqueo entre roles en su `README.md`.

## Flujo de trabajo en paralelo

Cinco personas, cinco agentes, un solo `main`. Estas reglas existen para que el producto llegue limpio al domingo.

1. **Nadie pushea a `main`.** Se trabaja en la rama del rol (`rol/datos`, `rol/backend`, …) o en una rama de feature colgada de ella (`rol/backend/veto`).
2. **Todo entra a `main` por Pull Request.** Sin excepción, incluida la rama de integración. La plantilla está en `.github/pull_request_template.md`.
3. **El PR lo revisa alguien distinto de quien lo escribió** — y, si se usó un agente, en una sesión o modelo distinto al que escribió el código. Un modelo que revisa su propio trabajo valida sus propios sesgos.
4. **Antes de creer que algo se hizo: `git diff --stat`.** El reporte de un agente de código es un reclamo, no evidencia.
5. **PR pequeño y frecuente** > PR gigante al final. Un PR que toca dos carpetas de dueños distintos se parte en dos.
6. **Conflicto de merge en una carpeta ajena = se para y se avisa** en el grupo. No se resuelve por encima del trabajo de otro.
7. **Antes de abrir sesión:** lee tu `docs/agents/handoff-<tu-nombre>.md`. **Antes de cerrarla:** actualízalo. Es tu memoria entre sesiones y lo único que evita que tu agente arranque de cero.

## Restricciones no-negociables

La constitución del proyecto. No las cambia una persona sola.

- **Determinismo:** seed desde el primer commit. Mismo seed, mismo resultado, verificable. Meterlo después es reescribir el motor.
- **Cero datos inventados.** Ningún número disfrazado de cálculo. Todo supuesto se marca en el punto donde se toma con un comentario `# SUPUESTO:` grepeable. `grep -rn "SUPUESTO:"` es el informe de honestidad del proyecto.
- **Cero `TODO: implementar` dentro de `engine/`.** Es el archivo que el revisor va a leer completo.
- **Al LLM jamás se le nombra la política.** Solo la mecánica (*"tu costo laboral por empleado formal sube X%"*). Nunca "salario mínimo", ni "decreto", ni años. Es el control de contaminación y es la mitad del argumento de validación.
- **Contratos congelados en H+4.** Después de eso, cambiar `contracts/*.json` exige avisar en el grupo ANTES de tocar nada.
- **Todo número sale con banda.** Varianza además de media; barra de error sobre N≥5 paráfrasis del prompt, no sobre temperatura.
- **Presupuesto de LLM con corte duro** por corrida. $50 por persona es el techo real.
- **Feature freeze en H+28.** Ninguna dependencia nueva después de esa hora.
- **Repo público, licencia MIT, desplegado y accesible** sin registro. Un extraño con el link tiene que poder usarlo.
- **Documentar sí, manipular jamás.** Ningún texto del repo intenta instruir a un lector externo sobre qué concluir.

## Contratos

| Contrato | Dónde vive | Quién lo congela |
|---|---|---|
| `agente.json` — una fila de GEIH transformada | `contracts/`, ejemplo en `docs/PLAN.md` §4 | Alejo (con Manuel) |
| `decision.json` — propuesta LLM + veredicto del veto | `contracts/`, ejemplo en `docs/PLAN.md` §4 | Manuel ↔ Nico (la interfaz entre ambos) |
| `ronda.json` — agregado por ronda hacia frontend y agentes | `contracts/`, ejemplo en `docs/PLAN.md` §4 | Manuel (con Dani) |

Todos construyen contra los **ejemplos concretos** del §4, nunca contra un tipo vacío. Un stub sin datos de ejemplo es una fuente de divergencia entre 5 agentes.

## Feedback loops

Stack decidido en `docs/PLAN.md` D7: Python (numpy/pandas) para motor y datos, FastAPI para la API, Next.js para la interfaz, Supabase para estado y streaming.

- **Test:** `make test` — *PENDIENTE: pytest, lo cablea R5 con R2 (~H+6)*
- **Typecheck / lint:** *PENDIENTE: `ruff check` en Python, `tsc --noEmit` en `web/`*
- **Run:** `make run` — *PENDIENTE*
- **Validación:** `make validate` — imprime el número del backtest. Es el entregable estrella de R5.

Cuando cables uno de estos, actualiza la línea aquí en el mismo PR.

## Permisos

`.claude/settings.json` fija el piso: comandos destructivos denegados (`rm -rf`, force-push, reset duro) y una allow-list de lo cotidiano (`git`, `make`, `pytest`, `npm`) para que los agentes no se traben pidiendo permiso a las cuatro de la mañana. Otras herramientas (Cursor, Codex) traen su propia configuración; el principio es el mismo. Amplía la allow-list si tu rol lo necesita; **no toques la deny-list**.

## Agentes y skills locales

El repo puede alojar automatización propia cuando una necesidad se repita: skills en `.claude/skills/<nombre>/`, agentes en `.claude/agents/<nombre>/`. No hay carpetas ni placeholders pre-creados a propósito: un agente construido antes de que la necesidad sea real es peor que no tenerlo. En 36 horas, la barra para crear uno es alta.

Los que pasaron esa barra son **cuatro críticos adversariales internos**: tres jueces, uno por eje, y un reconciliador. Ninguno tiene `Edit`, ninguno toca la carpeta de un dueño, ninguno corre nada que llame al proveedor de LLM, y los cuatro escriben su informe en `docs/agents/<nombre-del-agente>/`.

| Agente | Comando | Qué pregunta | Su vara | Cuándo se usa |
|---|---|---|---|---|
| `juez-hackathon` | `/juez` | *¿quién usa esto y quién lo paga el lunes?* — negocio, pitch y propuesta de valor | el mercado | Antes de cada ensayo del pitch |
| `juez-tecnico` | `/juez-tecnico` | *¿esto corre, escala y es reproducible?* — arquitectura, stack y ejecución real | los estándares de la industria | Antes de cada PR grande y del feature freeze |
| `juez-cientifico` | `/juez-cientifico` | *¿esto es cierto?* — formas funcionales, coherencia dimensional, estabilidad, bandas | la matemática | Antes de cada PR que toque `engine/`, `behavior/` o `data/` |
| `peeky` | `/peeky` | *¿el repo es consistente consigo mismo?* — que cada elemento diga qué es, para qué existe y cómo encaja | **el propio repo** | Antes de abrir un PR, o cuando una carpeta se sienta pegada con cinta |

**`peeky` no es un cuarto juez.** Los tres jueces miden la calidad contra una vara externa; él reconcilia el repositorio contra sí mismo, y su hallazgo tipo nunca es *"esto está mal diseñado"* sino *"estos dos hechos del repo no pueden ser ciertos a la vez, y aquí están las dos líneas"*. Es el único sin `WebSearch`, a propósito: cinco personas en cinco ramas producen deriva más rápido de lo que cualquiera la detecta a mano, y esa deriva no se arregla consultando afuera.

Un informe de agente **no es normativo**: es un hallazgo con fecha, no una decisión. Lo que se confirme y cambie el modelo se gradúa a un ADR en `docs/adr/` o a una fila del registro de supuestos de `engine/MODELO.md`. Si no se gradúa, no pasó.

La regla de review del punto 3 del flujo de trabajo aplica use quien use la herramienta que use, y no depende de ningún modelo en particular. Un agente de crítica **no sustituye** esa review: es una sesión más, y su reporte también es un reclamo.
