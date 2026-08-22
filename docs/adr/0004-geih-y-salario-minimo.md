# ADR 0004 — GEIH + salario mínimo como caso, no TransMilenio

**Estado:** aceptado · **Fecha:** 2026-08-22 · **Fuente:** `docs/PLAN.md` D1

## Contexto

Había dos casos candidatos con la misma estructura de incentivos: evasión del salario mínimo (informalidad) y colados en TransMilenio. Había que elegir uno antes de escribir código, y la elección la decide la disponibilidad de datos, no el atractivo del caso.

## Decisión

**Salario mínimo (+23%) → margen formal/informal, acotado a Bogotá**, con la población construida desde los microdatos de la GEIH del DANE.

Regla de prioridad aplicada: **evidencia verificada > razonamiento**. La GEIH está verificada contra fuente (portal, catálogos, registro gratuito). Todos los datos de TransMilenio estaban marcados como plausibles sin verificar (Encuesta de Movilidad, cifras de evasión, GTFS).

Además: el salario mínimo tiene ~20 experimentos naturales para backtest y una controversia viva (litigio en el Consejo de Estado).

## Alternativas descartadas

- **TransMilenio / colados.** Queda como plan B nombrado (verificación V1 del plan). Lo mejor de esa propuesta, el bucle de fiscalización en cascada, **se transfiere intacto**: la capacidad de inspección laboral también es fija.
- **Simulador de opinión electoral.** Es el ejemplo literal que dieron los organizadores y por lo tanto el terreno más saturado del track.
- **Múltiples ciudades o políticas en la demo.** El motor es general (recibe cualquier política como cambio de pagos + capacidad de fiscalización + población); la pantalla muestra una sola.

## Consecuencias

Los microdatos son el **punto único de falla** del proyecto y el camino crítico (H+2 para tenerlos en disco). El plan B está escrito y es cambiar de fuente (tablas agregadas del DANE), **no cambiar de proyecto**.

La generalidad se pitchea como tesis, no como catálogo: toda política que cambia incentivos tiene un supuesto de cumplimiento, y este motor lo mide. El dominio exacto de lo que el motor cubre y lo que no está en `docs/PLAN.md` §4.2.
