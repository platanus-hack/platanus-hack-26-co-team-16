# `docs/vet/` — el vet del 22-ago 22:00 y el reparto que sale de él

> **EMPIEZA AQUÍ si abres el repo después del 22-ago 22:00.** Esto es lo más reciente que hay sobre el
> estado real del proyecto y sobre qué está haciendo cada quien. Manda sobre cualquier plan anterior en
> cuanto al **reparto de trabajo**; no manda sobre el producto (eso sigue en `docs/PLAN.md`) ni sobre la
> validación (eso sigue en `VALIDATION.md`).

## Qué es esto

Un vet completo de `main` corrido el 22-ago a las 22:00 con tres auditorías de solo lectura, más las
decisiones que el equipo tomó a partir de él y el reparto en cinco tracks paralelos.

**Línea base de la auditoría: `c63343f`.** Verificado después contra `b180d51`: los hallazgos siguen en
pie, y apareció uno nuevo (V-1, la caché fría).

## Orden de lectura

| # | Archivo | Qué contesta |
|---|---|---|
| 1 | [`01-decisiones-y-tracks.md`](01-decisiones-y-tracks.md) | **Qué se decidió y qué te toca a ti.** Si solo lees uno, este |
| 2 | [`03-arranque-por-track.md`](03-arranque-por-track.md) | **El prompt de arranque de tu agente**, copiar y pegar. Uno por track |
| 3 | [`00-hallazgos.md`](00-hallazgos.md) | Los 5 rojos y los 14 naranjas, con `archivo:línea` |
| 4 | [`02-la-idea-en-3-pasos.md`](02-la-idea-en-3-pasos.md) | El guion de la demo, sobre lo que sobrevive al backtest |
| 5 | [`99-mensaje-al-grupo.md`](99-mensaje-al-grupo.md) | El resumen que se pasó por WhatsApp |

## Las tres cosas que no se pueden ignorar

1. **`n_parafrasis>=2` revienta** (`behavior/rondas.py:120`). La banda que `AGENTS.md` declara
   no-negociable no está apagada: es **imposible de encender**. Media hora de arreglo, y desbloquea
   todo lo demás sobre bandas.
2. **El pre-registro se sostiene pero NO fue ciego.** `2d4aa7e` ya traía *"lo que ya se sabe apunta a la
   rama B"*. **Se dice en el pitch de frente.** Dicho por nosotros es rigor; encontrado por un juez es
   fraude.
3. **La cascada agregada está falsada** (`VALIDATION.md`). No se afirma como hallazgo en ninguna parte.
   Sigue siendo el **mecanismo** del modelo y así se nombra.

## Reglas que este documento NO cambia

- Nadie pushea a `main`. Todo entra por PR, revisado por alguien distinto de quien lo escribió.
- Nadie edita la carpeta de otro. El vet **acusa**; los dueños arreglan.
- Un hallazgo de agente es un **reclamo con fecha**, no una decisión. Lo que se confirme y cambie el
  modelo se gradúa a un ADR o al registro de supuestos de `engine/MODELO.md`.
