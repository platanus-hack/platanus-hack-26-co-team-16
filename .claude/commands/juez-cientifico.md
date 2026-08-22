---
description: Somete el núcleo matemático al juez científico (PhD en modelado, segunda opinión obligatoria)
argument-hint: [nucleo|formula|defensa] [ruta o concepto]
---

Invoca el subagente `juez-cientifico` (Agent tool, `subagent_type: "juez-cientifico"`) y pásale esto como tarea:

> Modo y material: $ARGUMENTS

Reglas de despacho:

- Si `$ARGUMENTS` está vacío o no nombra un modo, el modo es **`nucleo`**: barrido del núcleo cuantitativo (`engine/`, `behavior/`, `data/` y los ADR que los gobiernan).
- Si `$ARGUMENTS` empieza por `formula`, el modo es **`formula`** y lo que sigue es la pieza a auditar — una ruta (`docs/adr/0007-forma-funcional-prob-sancion.md`) o un concepto (`prob_sancion`, `banda`, `factor de expansión`). Es el modo de mayor rigor: el agente deriva, acota y evalúa los bordes.
- Si `$ARGUMENTS` empieza por `defensa`, el modo es **`defensa`**: pasada sobre `VALIDATION.md`, `ARCHITECTURE.md`, `README.md` y el guion del pitch buscando afirmaciones cuantitativas que el código no sostiene.
- Si `$ARGUMENTS` trae una ruta sin modo, el modo es **`formula`** sobre esa ruta.

Recuérdale dos cosas en la tarea, porque son las que más caro cuestan si se saltan:

- **Presupuesto:** nunca `make run`, `make validate` ni nada que llame al proveedor de LLM. El corte duro es de $50.
- **Segunda opinión obligatoria** vía `mcp__codex__codex`, con el prompt **neutral** (sin sus conclusiones ni sus severidades). Si no está disponible, que lo escriba literal: `Segunda opinión: NO DISPONIBLE`.

Cuando el subagente termine, relaya su salida completa al usuario — las cinco secciones tal cual, sin resumirlas y sin suavizarlas — y dile en qué archivo de `docs/agents/juez-cientifico/` quedó guardado el informe.
