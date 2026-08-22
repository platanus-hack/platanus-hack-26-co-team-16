# Arquitectura

> **Esqueleto, sin llenar.** Dueño: Juanda (R5), con insumo de cada dueño de módulo. Se llena entre H+20 y H+30.
> Existe desde ahora para que a la hora 28 nadie tenga que *diseñar* este documento, solo *llenarlo*.
> Regla: acá va la **síntesis** y el porqué. El detalle de cada decisión vive en `docs/adr/` y se enlaza, no se copia.

## Qué es este sistema

_PENDIENTE — dos párrafos. Base: `docs/PLAN.md` §1._

## Las capas

_PENDIENTE — el diagrama de `docs/PLAN.md` §4 y `docs/FLUJO.md`, con un párrafo por capa: `data/`, `engine/`, `behavior/`, `api/`, `web/`. Qué responsabilidad tiene cada una y qué NO le corresponde._

## El veto de factibilidad

_PENDIENTE — la pieza central. Por qué el LLM propone y el motor veta, y qué pasa con una propuesta rechazada. Ver [ADR 0003](docs/adr/0003-veto-de-factibilidad.md)._

## La cascada: fiscalización endógena

_PENDIENTE — por qué la capacidad fija de inspección produce el resultado no obvio, y por qué el modelo oficial no lo ve._

## Determinismo y reproducibilidad

_PENDIENTE — dónde entra el seed, qué garantiza exactamente ("mismo seed, mismo resultado"), qué NO garantiza (la capa LLM cacheada), y cómo lo verifica un tercero._

## Alternativas descartadas y por qué

_PENDIENTE — la sección que responde "¿hay ingeniería real acá?". Sintetiza y enlaza:_

- [ADR 0001](docs/adr/0001-motor-vectorizado-propio.md) — motor propio en vez de Mesa / AgentSociety / OASIS / AgentTorch
- [ADR 0002](docs/adr/0002-llm-por-arquetipo.md) — LLM por arquetipo en vez de por agente
- [ADR 0003](docs/adr/0003-veto-de-factibilidad.md) — veto determinista en vez de menú fijo o juez LLM
- [ADR 0004](docs/adr/0004-geih-y-salario-minimo.md) — GEIH y salario mínimo en vez de TransMilenio
- _Lo que no se construyó y por qué: `docs/PLAN.md` §9_

## Dominio del motor: qué cabe y qué no

_PENDIENTE — la tabla de `docs/PLAN.md` §4.2. Declarar los límites es parte de la credibilidad, no una debilidad._

## Costo y presupuesto de LLM

_PENDIENTE — arquetipos × rondas × modelo, la caché en disco, el corte duro de presupuesto._
