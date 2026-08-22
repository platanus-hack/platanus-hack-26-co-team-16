# Auditorías del agente `juez-cientifico`

Informes de autocrítica de **modelado matemático**. Los escribe el agente [`.claude/agents/juez-cientifico.md`](../../../.claude/agents/juez-cientifico.md), que entra al repo con la mentalidad de un PhD en Matemáticas Aplicadas revisando un motor de simulación: de dónde se deriva cada forma funcional, si las unidades cuadran, qué pasa en los bordes, si la dinámica hace lo que se dice que hace, y si los números salen con la incertidumbre que de verdad tienen.

Completa la tríada de jueces con [`juez-hackathon`](../juez-hackathon/README.md) y [`juez-tecnico`](../juez-tecnico/README.md); el cuarto crítico del repo, [`peeky`](../peeky/README.md), no es un juez. La frontera:

| | `juez-hackathon` | `juez-tecnico` | `juez-cientifico` | `peeky` |
|---|---|---|---|---|
| Pregunta | ¿alguien usa esto y quién lo paga el lunes? | ¿esto corre, escala y es reproducible? | ¿esto es cierto? | ¿es consistente consigo mismo? |
| Vara | el mercado | los estándares de la industria | la matemática | **el propio repo** |
| Sobre la demo | **asume que funciona** | **no asume nada** | le da igual si corre: pregunta si el número significa algo | no la mira: mira las costuras entre piezas |
| Salida | 4 secciones, 500 palabras | 5 secciones, 900 palabras | 5 secciones, 1000 palabras | 4 secciones, 800 palabras |

El reparto evita el solapamiento: determinismo y seed le tocan a `juez-tecnico` como problema de ingeniería, y a `juez-cientifico` solo su consecuencia estadística — varianza de Monte Carlo y tamaño de muestra efectivo. Un hallazgo de arquitectura, caché o despliegue **no es suyo**.

**Qué NO son estos archivos.** No son una evaluación externa, no son un peer review, y no intentan decirle a nadie qué concluir sobre el proyecto. Son el equipo buscándose los agujeros de modelado antes de que se los encuentre un juez con formación en econometría. Que estén versionados es parte de la regla de `AGENTS.md`: documentar el estado real, incluido el incómodo.

**Un informe no es normativo.** Es un hallazgo con fecha, no una decisión. Lo que se confirme y cambie el modelo se gradúa a un ADR en [`docs/adr/`](../../adr/) o a una fila del registro de supuestos de [`engine/MODELO.md`](../../../engine/MODELO.md). Si no se gradúa, no pasó.

## Cómo se generan

```
/juez-cientifico                                  # modo nucleo (default): engine/, behavior/, data/ y sus ADR
/juez-cientifico formula docs/adr/0007-...md      # una pieza en profundidad: deriva, acota, evalúa los bordes
/juez-cientifico formula prob_sancion             # también acepta un concepto, no solo una ruta
/juez-cientifico defensa                          # afirmaciones cuantitativas que el código no sostiene
```

El modo `formula` es el de mayor rigor y menor alcance: ahí el agente **escribe la derivación** — el límite, la derivada, la desigualdad — y verifica los bordes numéricamente con `python -c`, que no gasta presupuesto.

El agente **solo lee**: su única escritura permitida en todo el repo es su informe en esta carpeta. Tiene prohibido tocar los `handoff-*.md` y `context.md` que viven un nivel arriba. Y nunca ejecuta `make run`, `make validate` ni `make reproduce` — el presupuesto de LLM tiene corte duro y quemarlo es daño real.

## Convención de nombres

```
AAAA-MM-DD-HHMM-<modo>.md
```

Donde `<modo>` es `nucleo`, `formula-<pieza>` o `defensa`. Un archivo por corrida, **nunca se sobrescribe uno anterior**. Cada informe abre comparándose con el anterior: qué se cerró y qué sigue abierto. Un hallazgo de modelado que sobrevive tres auditorías ya no es una crítica: es una decisión que el equipo tomó sin escribirla en un ADR.

## Segunda opinión: obligatoria

A diferencia de sus hermanos, acá el tercer par de ojos **no es opcional**. El agente le pide una auditoría independiente a otro modelo vía `mcp__codex__codex`, con un prompt **neutral** que no incluye sus propias conclusiones ni severidades — un prompt contaminado devuelve su propio eco y destruye el valor de la corroboración.

Coincidencia independiente sobre el mismo hecho sube el hallazgo a `CONFIRMADO`; divergencia se reporta como divergencia, con las dos posturas y **qué experimento la resolvería**, nunca promediada. Lo que el segundo modelo reporte y el agente no haya visto, lo verifica él antes de incluirlo: un reporte también es un reclamo.

Ese MCP es configuración personal de quien corre el agente: si no está, el informe dice `Segunda opinión: NO DISPONIBLE` y la auditoría sale completa igual. Es la regla 3 de `AGENTS.md` aplicada al propio auditor — quien revisa no debe ser el mismo modelo que escribió.
