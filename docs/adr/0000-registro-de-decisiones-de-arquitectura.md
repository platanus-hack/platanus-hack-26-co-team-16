# ADR 0000 — Registro de decisiones de arquitectura

**Estado:** aceptado · **Fecha:** 2026-08-22

## Contexto

Cinco personas con cinco agentes construyendo en paralelo. Sin un registro, la razón de cada decisión vive en la cabeza de quien la tomó, y el agente del siguiente la re-litiga o la contradice sin saberlo. Además, quien revise el proyecto va a preguntar exactamente esto: *¿por qué así y no de otra forma?*

## Decisión

Cada decisión técnica difícil de revertir se escribe como un ADR numerado en esta carpeta.

**Se escribe un ADR cuando se cumplen los tres criterios:**
1. Es difícil de revertir.
2. Sorprende sin contexto (alguien podría preguntar "¿y por qué no usaron X?").
3. Es resultado de un trade-off real, no de la única opción disponible.

**Formato:** contexto · decisión · **alternativas descartadas y por qué** · consecuencias.
La sección de alternativas descartadas no es opcional: es la que convierte "no usamos esa librería" en una decisión de ingeniería documentada.

**Los ADRs son append-only.** No se editan: si una decisión cambia, se escribe uno nuevo que la reemplaza y se marca la vieja como *superseded por NNNN*.

## Consecuencias

`ARCHITECTURE.md` sintetiza y enlaza estos archivos; no los duplica. Quien lea el repo entra por `ARCHITECTURE.md` y baja acá cuando quiere el detalle.
