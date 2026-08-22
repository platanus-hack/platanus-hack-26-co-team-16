# `behavior/` — Capa conductual (LLM)

**Dueño: Nico (R3)** · rama `rol/conductual`

Descubre estrategias de adaptación que un economista no habría enumerado. Propone; no aplica nada.

## Qué va aquí

- Definición de arquetipos (sector × tamaño × formal/informal × tramo de ingreso, ~40-60).
- Prompts por arquetipo, **visibles en el repo**.
- Caché en disco por hash del prompt.
- Presupuesto tope por corrida con corte duro.
- Ruteo de modelos: Haiku con prompt caching para la masa, modelo grande solo para las 3-4 historias narradas.
- Bucle de rondas: propuesta → veto del motor → reintento → agregado.

## Qué NO va aquí

- Aplicar decisiones al estado del mundo (eso lo hace `engine/`).
- Nada de `web/`, `data/` ni `engine/`.

## La regla de oro

**Al LLM jamás se le nombra la política.** Ni "salario mínimo", ni "decreto", ni años. Solo la mecánica: *"tu costo laboral por empleado formal sube X%"*. Es el control de contaminación de entrenamiento y sostiene la mitad del argumento de validación. Un prompt que la viole invalida la corrida.
