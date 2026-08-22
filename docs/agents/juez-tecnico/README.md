# Auditorías del agente `juez-tecnico`

Informes de autocrítica de **ingeniería**. Los escribe el agente [`.claude/agents/juez-tecnico.md`](../../../.claude/agents/juez-tecnico.md), que entra al repo con la mentalidad de un Staff / Principal Engineer revisando un prototipo: arquitectura, stack, escalabilidad, seguridad y viabilidad de producción, y sobre todo la distancia entre lo que la documentación promete y lo que el disco tiene.

Es el hermano técnico de [`juez-hackathon`](../juez-hackathon/README.md). La frontera:

| | `juez-hackathon` | `juez-tecnico` |
|---|---|---|
| Pregunta | ¿alguien usa esto y quién lo paga el lunes? | ¿esto corre, escala, es seguro y sobrevive a producción? |
| Sobre la demo | **asume que funciona** | **no asume nada** |
| Salida | 4 secciones, 500 palabras | 5 secciones, 900 palabras |

**Qué NO son estos archivos.** No son una evaluación externa, no son la opinión de ningún jurado real, y no intentan decirle a nadie qué concluir sobre el proyecto. Son el equipo buscándose los agujeros de ingeniería antes de que se los encuentre un revisor con el repo abierto. Que estén versionados es parte de la regla de `AGENTS.md`: documentar el estado real, incluido el incómodo.

## Cómo se generan

```
/juez-tecnico                # alcance repo (default) — auditoría completa
/juez-tecnico engine/        # auditoría enfocada en una carpeta
/juez-tecnico diff           # solo lo que cambió en la rama contra main
/juez-tecnico repo --codex   # pide explícitamente la segunda opinión de otro modelo
```

El agente **solo lee**: su única escritura permitida en todo el repo es su informe en esta carpeta. Y nunca ejecuta `make run`, `make validate` ni `make reproduce` — el presupuesto de LLM tiene corte duro y quemarlo es daño real.

## Convención de nombres

```
AAAA-MM-DD-HHMM-<alcance>.md
```

Un archivo por corrida, **nunca se sobrescribe uno anterior**. Cada informe abre comparándose con el anterior: qué se cerró y qué sigue abierto. Un hallazgo técnico que sobrevive tres auditorías ya no es una crítica, es una decisión que el equipo tomó sin decirlo.

## Segunda opinión

El agente puede pedirle una auditoría independiente a otro modelo vía `mcp__codex__codex`, con un prompt neutral que no incluye sus propias conclusiones. Coincidencia sube el hallazgo a `CONFIRMADO`; divergencia se reporta como divergencia, con las dos posturas, **nunca promediada**. Ese MCP es configuración personal de quien corre el agente: si no está, el informe dice `Segunda opinión: NO DISPONIBLE` y la auditoría sale completa igual. Es la regla 3 de `AGENTS.md` aplicada al propio auditor — quien revisa no debe ser el mismo modelo que escribió.
