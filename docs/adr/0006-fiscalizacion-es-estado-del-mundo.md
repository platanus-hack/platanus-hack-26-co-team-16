# ADR 0006 — La capacidad de fiscalización es estado del mundo, no un campo de la política

**Estado:** aceptado (R2) · **Fecha:** 2026-08-22 · **Fuente:** hueco H2 · **Supera:** el diagrama de `docs/UML.md`

## Contexto

En `docs/UML.md`, la clase `Politica` tiene tres campos: `tipo`, `aumento_pct` y
**`capacidad_fiscalizacion`**.

Eso contradice el argumento central del proyecto. `docs/PLAN.md` §10 dice, textualmente,
que *"la fiscalización endógena se deriva de capacidad fija, no se ajusta a mano"*, y el
prompt de R2 lo repite: *"la capacidad NUNCA se ajusta a mano para producir la cascada"*.

Pero si la capacidad es un campo de la política, y la política es lo que el usuario mueve
con el slider, entonces **sí es una perilla ajustable a mano**, y la primera pregunta de un
revisor técnico va a ser por qué la cascada aparece justo en el valor que elegimos.

Además es incorrecto conceptualmente: la capacidad de inspección laboral existía antes del
decreto y seguirá existiendo después. No es parte de la política que se evalúa.

## Decisión

Se separan dos objetos con dueños distintos:

- **`Politica`** — solo cambia pagos: `{ tipo, aumento_pct }`. Es lo único que el usuario
  mueve. Es lo único que se traduce a mecánica para el LLM (`como_mecanica()`).
- **`EstadoFiscalizacion`** — parte del estado del mundo, junto con la población. Contiene
  la capacidad de inspección del período, derivada de fuentes:
  planta efectiva de inspectores × inspecciones por inspector por trimestre × fracción
  dirigida al universo del modelo.

**`EstadoFiscalizacion` no es un input de la interfaz.** Se construye una vez al inicializar
el mundo, sale de las fuentes documentadas en
[`docs/investigacion/1-teorica.md`](../investigacion/1-teorica.md) §3, y lo que no tenga
fuente va con `# SUPUESTO:` y **barrido de sensibilidad obligatorio**.

## Alternativas descartadas

| Alternativa | Por qué no |
|---|---|
| **Dejarla en `Politica`** (el statu quo) | Vuelve ajustable a mano lo que el pitch promete que no lo es. Es la crítica más fácil de hacernos. |
| **Exponerla como segundo slider en la interfaz** | Es tentador ("¿qué pasa si contratamos más inspectores?") y es una pregunta legítima de política, pero convierte el resultado principal en algo que depende de dos perillas y hace irrefutable cualquier cosa. **Queda como trabajo futuro nombrado**, no como feature. |
| **Fijarla como constante mágica en el código** | Un número sin fuente en `engine/` es exactamente lo que `docs/fuentes/manuel.md` §9.4 dice que un revisor detecta en segundos. |

## Consecuencias

- `docs/UML.md` cambia: `Politica` pierde el campo y aparece `EstadoFiscalizacion`.
- La frase para el Q&A queda limpia: *"la política cambia costos; la capacidad de
  inspección es un dato del mundo que nosotros no tocamos, y su valor está citado"*.
- Obliga a que exista el número de capacidad **con fuente antes de la primera corrida seria**.
  Hoy la mejor fuente primaria es la planta de 904 cargos de MinTrabajo, con la advertencia
  de que es de ~2015 (ver `1-teorica.md` §3). Conseguir la cifra vigente es la tarea de
  investigación más urgente del motor.
- El análisis de sensibilidad sobre la capacidad deja de ser opcional: es lo que responde
  *"¿y si el número está mal?"* sin tener que acertarle.
