# `engine/` — El motor físico determinista

**Dueño: Manuel (R2)** · rama `rol/backend`

Es el corazón del proyecto y el archivo que un revisor va a leer completo. ~300 líneas de numpy/pandas que se entienden en una tarde: esa legibilidad es el entregable, no un accidente.

## Qué va aquí

- Costos formal vs informal (factor prestacional).
- Flujo de caja de cada agente.
- Probabilidad de fiscalización endógena: capacidad fija ÷ universo de evasores. De acá sale la cascada.
- **El veto de factibilidad** ([ADR 0003](../docs/adr/0003-veto-de-factibilidad.md)) — la interfaz con `behavior/`.
- Scheduler de rondas y barrido de `aumento_pct` para localizar el codo.

## Qué NO va aquí

- Ninguna llamada a un LLM. El motor no opina: acepta o rechaza.
- Nada de `web/`, `data/` ni `behavior/`.

## Reglas duras

- **Seed desde el primer commit.** Mismo seed, mismo resultado. Meterlo después es reescribir.
- **Cero `TODO: implementar`** en esta carpeta.
- **Un concepto por archivo**, con docstring de cabecera: qué modela, entradas, salidas, supuestos.
- Vectorizado sobre dataframe, no bucle OOP por agente ([ADR 0001](../docs/adr/0001-motor-vectorizado-propio.md)).
