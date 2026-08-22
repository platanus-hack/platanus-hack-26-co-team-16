# `contracts/` — La especificación viva

**Dueño: Alejo (R1)**, congelados con Manuel (R2) y Nico (R3)

Los tres JSON que definen cómo se hablan los módulos. Son la única forma de que cinco personas construyan en paralelo sin bloquearse.

| Archivo | Qué describe | Quién lo congela |
|---|---|---|
| `agente.json` | Una fila de la GEIH transformada | Alejo con Manuel |
| `decision.json` | Propuesta de la capa LLM + veredicto del veto | Manuel ↔ Nico |
| `ronda.json` | El agregado por ronda, hacia los agentes y hacia el frontend | Manuel con Dani |

## Reglas

- **Se congelan en H+4.** Después de eso, cambiar uno exige avisar en el grupo ANTES de tocar nada.
- **Con ejemplos concretos, nunca tipos vacíos.** Los ejemplos completos están en `docs/PLAN.md` §4: se copian de ahí. Un stub sin datos de ejemplo es la principal fuente de divergencia entre agentes.
- Mientras el dato real no llegue (H+8), **todos construyen contra estos ejemplos**.
