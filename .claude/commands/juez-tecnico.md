---
description: Somete el repo a la auditoría del juez técnico (Staff Engineer adversarial interno)
argument-hint: [repo|<carpeta>|diff] [--codex]
---

Invoca el subagente `juez-tecnico` (Agent tool, `subagent_type: "juez-tecnico"`) y pásale esto como tarea:

> Alcance y opciones: $ARGUMENTS

Reglas de despacho:

- Si `$ARGUMENTS` está vacío o no nombra un alcance, el alcance es **`repo`**: el repositorio completo, tal como lo abrirá el jurado con su propio agente de código.
- Si `$ARGUMENTS` nombra una carpeta (`engine/`, `behavior/`, `api/`, `web/`, `data/`), el alcance es esa carpeta — pero el agente igual lee el contrato del repo y corre la prueba de humo.
- Si `$ARGUMENTS` empieza por `diff`, el alcance es `git diff --stat main...HEAD` sobre la rama actual.
- **`--codex`** pide explícitamente la segunda opinión con `mcp__codex__codex`. Sin la bandera, el agente decide si la usa; si la herramienta no está disponible tiene que decirlo en el informe, no simularla.
- **Nunca autorices `make run`, `make validate` ni `make reproduce`** al despachar. El presupuesto de LLM tiene corte duro de $50 y quemarlo es daño real. Si el usuario lo pide expresamente, pásaselo escrito en la tarea.

Cuando el subagente termine, relaya su salida completa al usuario — las cinco secciones tal cual, sin resumirlas y sin suavizarlas — y dile en qué archivo de `docs/agents/juez-tecnico/` quedó guardado el informe.

Este es el juez de **ingeniería**. Para el juicio de negocio y pitch, el comando es `/juez`.
