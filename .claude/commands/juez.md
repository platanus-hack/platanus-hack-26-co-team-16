---
description: Somete el pitch o el repo al juez veterano de hackathon (crítico adversarial interno)
argument-hint: [pitch|repo|qa] [texto del pitch o ruta a un archivo]
---

Invoca el subagente `juez-hackathon` (Agent tool, `subagent_type: "juez-hackathon"`) y pásale esto como tarea:

> Modo y material: $ARGUMENTS

Reglas de despacho:

- Si `$ARGUMENTS` está vacío o no nombra un modo, el modo es **`pitch`** y el material es el guion cronometrado de `docs/PLAN.md` §12.
- Si `$ARGUMENTS` empieza por `repo`, el modo es **`repo`**: auditoría del día después sobre el estado real del disco.
- Si `$ARGUMENTS` empieza por `qa`, el modo es **`qa`**: simulacro interactivo, una pregunta por turno. **No lo despaches a un subagente** — el modo `qa` necesita ida y vuelta con el usuario, así que carga `.claude/agents/juez-hackathon.md` y actúa tú como el juez en esta misma conversación.
- Si `$ARGUMENTS` trae una ruta a un archivo, ese archivo es el material a juzgar.

Cuando el subagente termine, relaya su salida completa al usuario — las cuatro secciones tal cual, sin resumirlas y sin suavizarlas — y dile en qué archivo de `docs/agents/juez-hackathon/` quedó guardado el informe.
