# Juicios del agente `juez-hackathon`

Informes de autocrítica del equipo. Los escribe el agente [`.claude/agents/juez-hackathon.md`](../../../.claude/agents/juez-hackathon.md), que entra al proyecto con la mentalidad de un juez de hackathon e inversionista ángel: asume que la demo funciona y pregunta si alguien usaría y pagaría esto.

Es uno de los cuatro críticos internos del repo, y el único que juzga el **negocio**. La frontera:

| | `juez-hackathon` | `juez-tecnico` | `juez-cientifico` | `peeky` |
|---|---|---|---|---|
| Pregunta | ¿alguien usa esto y quién lo paga el lunes? | ¿esto corre, escala y es reproducible? | ¿esto es cierto? | ¿es consistente consigo mismo? |
| Vara | el mercado | los estándares de la industria | la matemática | **el propio repo** |
| Sobre la demo | **asume que funciona** | **no asume nada** | le da igual si corre: pregunta si el número significa algo | no la mira: mira las costuras entre piezas |
| Salida | 4 secciones, 500 palabras | 5 secciones, 900 palabras | 5 secciones, 1000 palabras | 4 secciones, 800 palabras |

Los tres jueces miden contra una vara externa; [`peeky`](../peeky/README.md) reconcilia el repositorio contra sí mismo. Un hallazgo de arquitectura le toca a [`juez-tecnico`](../juez-tecnico/README.md), uno de derivación o de unidades a [`juez-cientifico`](../juez-cientifico/README.md).

**Qué NO son estos archivos.** No son una evaluación externa, no son la opinión de ningún jurado real, y no intentan decirle a nadie qué concluir sobre el proyecto. Son el equipo buscándose los agujeros antes de que se los encuentren en la sala. Que estén en el repo es parte de la regla de `AGENTS.md`: documentar el estado real, incluido el incómodo.

## Cómo se generan

```
/juez              # modo pitch (default) — juzga el guion de docs/PLAN.md §12
/juez repo         # auditoría del día después — promesa en los .md contra lo que hay en disco
/juez qa           # simulacro interactivo — una pregunta asesina por turno
/juez pitch <ruta> # juzga el texto de pitch que le pases
```

## Convención de nombres

```
AAAA-MM-DD-HHMM-<modo>.md
```

Un archivo por corrida, **nunca se sobrescribe uno anterior**. La serie es el valor: cada informe nuevo abre comparándose con el anterior — qué se cerró y qué sigue abierto. Un hallazgo que sobrevive tres juicios seguidos ya no es una crítica, es una decisión que el equipo tomó sin decirlo.
