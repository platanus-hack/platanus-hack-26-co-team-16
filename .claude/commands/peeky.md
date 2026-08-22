---
description: Audita la coherencia interna del repo con Peeky (reconciliador adversarial: qué es, para qué existe, cómo encaja)
argument-hint: [<carpeta>|--diff] [--fast]
---

Invoca el subagente `peeky` (Agent tool, `subagent_type: "peeky"`) y pásale esto como tarea:

> Alcance y opciones: $ARGUMENTS

Reglas de despacho:

- Si `$ARGUMENTS` está vacío, el alcance es el **repositorio completo**: los diez ejes sobre todo lo rastreado.
- Si `$ARGUMENTS` nombra una ruta (`data/`, `behavior/`, `contracts/`, `behavior/capa.py`), el alcance es ese objetivo **y sus costuras** — quién lo llama, qué contratos toca, qué promete de él la documentación. Nunca como una isla.
- Si `$ARGUMENTS` empieza por `--diff`, el alcance es `git diff main...HEAD` sobre la rama actual, incluidos archivos nuevos, borrados y renombrados. Es el modo de antes de abrir un PR.
- **`--fast`** salta el pase de verificación cross-modelo con `mcp__codex__codex`. Sin la bandera el pase es **obligatorio**, y si la herramienta no está disponible el agente tiene que declararlo en el informe, nunca simularlo. `--fast` significa "sin segunda opinión", no "revisión superficial".
- Los ejes de **contaminación del LLM** y **determinismo** se corren siempre, aunque el alcance no los toque.
- **Nunca autorices `make run`, `make validate`, `make reproduce` ni `behavior/demo.py`** al despachar. El presupuesto de LLM tiene corte duro de $50 y quemarlo auditando es daño real.

Cuando el subagente termine, relaya su salida completa al usuario — las cuatro secciones tal cual, sin resumirlas y sin suavizarlas — y dile en qué archivo de `docs/agents/peeky/` quedó guardado el informe.

Peeky **no es un cuarto juez**: los tres jueces evalúan calidad contra una vara externa, él reconcilia el repositorio contra sí mismo, elemento por elemento. Para el juicio de negocio, `/juez`; para el de ingeniería, `/juez-tecnico`; para el del modelo matemático, `/juez-cientifico`.
