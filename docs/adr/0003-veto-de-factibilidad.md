# ADR 0003 — El veto de factibilidad como interfaz entre el LLM y el motor

**Estado:** aceptado · **Fecha:** 2026-08-22 · **Fuente:** `docs/PLAN.md` §4, `docs/FLUJO.md`

## Contexto

Una capa LLM que propone conductas produce siempre una respuesta plausible, incluso cuando es materialmente imposible (despedir sin plata para indemnizaciones, absorber un costo que excede el flujo de caja). Ese es exactamente el modo de falla que un revisor técnico va a buscar: *"¿cómo sé que esto no es puro invento?"*.

Al mismo tiempo, enumerar a mano el menú de estrategias posibles mata lo que el LLM aporta: encontrar adaptaciones que un economista no habría listado.

## Decisión

El LLM **propone** y el motor determinista **veta**. Cada propuesta pasa por una comprobación de factibilidad (plata, reglas, restricciones) que devuelve `factible: true/false` con razón. Si hay veto, el arquetipo reintenta con otra estrategia. El contrato es `contracts/decision.json`.

Lo que sobrevive a los dos filtros es la salida del sistema.

## Alternativas descartadas

- **Menú de estrategias fijo, sin LLM.** Pierde el dato A4 (por qué evade cada quien, qué estrategia domina en qué segmento), que es una de las cuatro razones de existir del proyecto.
- **LLM sin veto.** Produce narrativa plausible e infalsable. Es literalmente el problema que el proyecto dice resolver.
- **Validar la propuesta con otro LLM.** Un juez estocástico sobre un proponente estocástico: no da determinismo ni reproducibilidad, y no se puede defender con un seed.

## Consecuencias

El veto es la frontera de responsabilidad entre R2 (Manuel, `engine/`) y R3 (Nico, `behavior/`), y por eso `contracts/decision.json` se congela entre los dos en H+4 y no lo cambia ninguno por su cuenta.

Es también la frase del proyecto: *el LLM inventa lo que un economista no enumeraría; el motor mata lo que la plata no permite.*
