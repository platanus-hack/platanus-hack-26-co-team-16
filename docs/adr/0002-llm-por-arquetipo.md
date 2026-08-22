# ADR 0002 — El LLM se llama por arquetipo, no por agente

**Estado:** aceptado · **Fecha:** 2026-08-22 · **Fuente:** `docs/PLAN.md` D4

## Contexto

Los insumos del equipo se contradecían: el de políticas proponía una llamada de LLM por agente (lo que hace *Generative Agents* de Stanford); los de Manuel y Juan David proponían lo contrario, con el argumento de que *"el LLM nunca va en el bucle caliente"*.

El presupuesto real es de $50 de API por persona. Miles de agentes × 4 rondas de llamada individual es inviable, y además hace la corrida no reproducible en el tiempo del pitch.

## Decisión

Se llama al LLM **por arquetipo**: sector × tamaño de empresa × formal/informal × tramo de ingreso, unos 40-60 grupos × 4 rondas ≈ ~250 llamadas, cacheadas en disco por hash del prompt. Los miles de agentes **muestrean** de esas distribuciones. Modelo pequeño (Haiku) con prompt caching para la masa; modelo grande solo para las 3-4 historias narradas del pitch. Presupuesto tope por corrida con corte duro.

## Alternativas descartadas

- **Una llamada por agente.** Costo y latencia insostenibles; sin caché útil (cada prompt es único); la corrida no se puede repetir en vivo.
- **Cero LLM, solo reglas fijas.** Descartada como diseño, **conservada como test**: es la ablación del candado 4 de validación. Si el resultado no cambia sin LLM, el LLM no se gana el puesto, y preferimos saberlo nosotros a la H+24.
- **Un solo fan-out de una pasada** (la arquitectura "Pulso" del insumo de Nico). Una sola pasada es una opinión, no una simulación: sin dinámica temporal no hay emergencia. Su capa de producto (feed en vivo, dashboard) sí se adoptó, encima del motor de rondas.

## Consecuencias

La calidad del muestreo por arquetipo pasa a ser un supuesto explícito del modelo: los agentes dentro de un arquetipo son intercambiables en su conducta. Debe quedar declarado en `VALIDATION.md` entre los límites.

El número de arquetipos es la palanca de costo: subirlo mejora la resolución y multiplica las llamadas.
