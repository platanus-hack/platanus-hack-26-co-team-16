# Auditorías del agente `peeky`

Informes de **coherencia interna**. Los escribe el agente [`.claude/agents/peeky.md`](../../../.claude/agents/peeky.md), que recorre el repositorio elemento por elemento y le exige a cada uno que responda tres preguntas: **qué es, para qué existe y cómo encaja en el flujo**. Lo que no las responde, se reporta.

**Peeky no es un cuarto juez.** Los tres jueces evalúan calidad contra una vara externa; Peeky reconcilia el repositorio contra sí mismo. Su hallazgo tipo nunca es *"esto está mal diseñado"*, sino *"estos dos hechos del repo no pueden ser ciertos a la vez, y aquí están las dos líneas"*.

| | `juez-hackathon` | `juez-tecnico` | `juez-cientifico` | `peeky` |
|---|---|---|---|---|
| Pregunta | ¿quién usa esto y quién lo paga el lunes? | ¿esto corre, escala y es seguro? | ¿esto es cierto? | ¿es consistente consigo mismo? |
| Vara | el mercado | los estándares de la industria | la matemática | **el propio repo** |
| Altitud | el producto | el sistema | el modelo | **la costura entre piezas** |
| Verbo | juzga | juzga | juzga | **reconcilia** |

Peeky es el único que **no consulta nada externo**: no tiene `WebSearch` ni `WebFetch` a propósito. Todo lo que afirma sale de dos líneas del repositorio que se contradicen entre sí.

**Qué NO son estos archivos.** No son una evaluación externa, no son la opinión de ningún jurado real, y no intentan decirle a nadie qué concluir sobre el proyecto. Son el equipo buscándose las desconexiones antes de que se las encuentre un revisor con el repo abierto. Que estén versionados es parte de la regla de `AGENTS.md`: documentar el estado real, incluido el incómodo.

## Qué audita

Diez ejes. Cinco son de este repo y de ningún otro:

1. **Contaminación del LLM** — no si la guardia de `behavior/higiene.py` existe, sino si hay algún camino a la API que la esquive, y si el escáner de prompts lo dispara alguien.
2. **Determinismo** — si el seed se propaga hasta cada fuente de azar, o se fija en la superficie y promete lo que no cumple.
3. **El informe de honestidad** — que todo supuesto esté marcado y sea greppable. Si además es *cierto* es de `juez-cientifico`.
4. **Contratos huérfanos** — campo por campo de `contracts/*.json`: quién lo produce, quién lo consume, quién lo espera y no lo recibe.
5. **Deriva del glosario** — términos que `docs/agents/context.md` prohíbe, apareciendo en nombres de funciones y campos, no solo en la prosa.

Los otros cinco son el oficio: promesa contra disco a nivel de elemento, dependencias declaradas, configuración y secretos, fallos silenciosos, presupuesto y caché del LLM, y código zombie e higiene de git.

## Cómo se generan

```
/peeky                 # repo completo (default) — los diez ejes
/peeky data/           # una carpeta y sus costuras con el resto
/peeky --diff          # solo lo que cambió contra main — antes de abrir el PR
/peeky behavior/ --fast   # sin el pase de verificación cross-modelo
```

El agente **solo lee**: su única escritura permitida en todo el repo es su informe en esta carpeta. No tiene `Edit`. Y nunca ejecuta `make run`, `make validate`, `make reproduce` ni `behavior/demo.py` — el presupuesto de LLM tiene corte duro de $50 y quemarlo auditando sería una ironía cara.

## Convención de nombres

```
AAAA-MM-DD-HHMM-<alcance>.md
```

Un archivo por corrida, **nunca se sobrescribe uno anterior**. Cada informe abre comparándose con el anterior: qué se cerró, qué persiste y qué no se pudo reevaluar. Un hallazgo que sobrevive tres auditorías ya no es una inconsistencia: es una decisión que el equipo tomó sin escribirla.

Peeky también lee los informes de [`juez-tecnico`](../juez-tecnico/README.md) antes de barrer. Un hallazgo que el otro auditor ya publicó no se repite: se cita en una línea si sigue abierto.

## Verificación cross-modelo

Obligatoria salvo `--fast`. Cerrado el barrido y antes de redactar, Peeky manda **todos** sus hallazgos candidatos en una sola llamada batch a `mcp__codex__codex` (sandbox de solo lectura), con la afirmación falsable de cada uno y **qué observación lo refutaría**. El otro modelo abre cada ruta y devuelve `CONFIRMADO` / `REFUTADO` / `NO VERIFICABLE` con evidencia.

Lo refutado **se cae y no llega al informe**. Lo no verificable va marcado y redactado como sospecha, nunca como hecho.

Es la regla 3 de `AGENTS.md` aplicada al propio auditor: *"un modelo que revisa su propio trabajo valida sus propios sesgos"*. Ese MCP es configuración personal de quien corre el agente; si no está, el informe lo declara en su primera línea y sale completo igual. Un informe sin el pase cruzado sigue siendo útil; uno que oculta que no lo tuvo, no.
