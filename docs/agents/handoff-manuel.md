# Handoff — Manuel · R2 · Backend

> **Tu memoria entre sesiones.** Léelo al abrir tu sesión de agente, actualízalo antes de cerrarla.
> Este archivo es solo tuyo: nadie más lo edita, así nunca da conflicto de merge.
> Tus carpetas: `engine/`, `api/` · Tu rama: `rol/backend`
> Tu misión, entregables y prompt de arranque: [`docs/ROLES.md`](../ROLES.md)

## Dónde quedé

_Lo más reciente arriba._

- **2026-08-22 — Sesión de fundamentación. Cero código, a propósito.**

  El repo estaba **escrito, no decidido**: documentación densa y buena, pero con huecos
  tapados por buena prosa. Se encontraron **10, todos de backend**, y se cerraron 9. La
  sesión produjo el fundamento para que el motor se escriba rápido y sin devolverse.

  **Lo que existe ahora:**
  - [`docs/IDEA.md`](../IDEA.md) — **la espina dorsal.** La idea completa contra una rúbrica
    de viabilidad (protocolo ODD + Pattern-Oriented Modeling + Epstein + la anatomía y los
    filtros que ya eran nuestros). Sin un campo en blanco. Es la respuesta al problema del
    audio: *"nadie puede explicar la idea completa"*.
  - [`docs/investigacion/`](../investigacion/) — el fundamento del backend en tres esferas:
    **teórica** (qué está probado), **tools** (stack y estándares), **live** (empresas vivas).
    Cada entrada dice qué sirve, **qué no**, y dónde aterriza en `engine/`.
  - [`engine/MODELO.md`](../../engine/MODELO.md) — el mapa *teoría → archivo → función →
    test → supuesto*, con los 10 archivos de `engine/` definidos antes de escribirlos, las
    métricas sin ambigüedad, y **7 supuestos pre-declarados** (S1-S7).
  - **ADR 0005 a 0009**, `docs/UML.md` y `docs/FLUJO.md` actualizados, glosario extendido.

  **Los tres hallazgos que más cambian el motor:**
  1. **No existía el tiempo.** "Ronda" nunca se mapeó a calendario, y sin eso el backtest no
     se puede puntuar. Ahora: **una ronda = un trimestre, horizonte de 9 meses**
     ([ADR 0005](../adr/0005-el-reloj-de-la-simulacion.md)).
  2. **`prob_sancion = capacidad / n_evasores` no era una probabilidad** (no acotada,
     indefinida en 0, sin unidades). Ahora `p(E) = 1 − exp(−C/max(E,1))`, que **sale de
     repartir C inspecciones al azar entre E evasores** (Poisson) y **coincide con la
     fórmula del plan en el régimen relevante**. No cambia el modelo, lo define
     ([ADR 0007](../adr/0007-forma-funcional-prob-sancion.md)).
  3. **La capacidad de fiscalización estaba dentro de `Politica`**, o sea era una perilla
     del usuario — justo lo que el pitch promete que no es
     ([ADR 0006](../adr/0006-fiscalizacion-es-estado-del-mundo.md)).

## En qué estoy trabajando

- [ ] **Siguiente sesión: escribir `engine/`.** El orden está en
      [`engine/MODELO.md`](../../engine/MODELO.md). Empezar por `seed.py` y `fiscalizacion.py`
      (determinismo desde el primer commit, y el corazón de la cascada).
- [ ] Abrir PR de `rol/backend` → `main`. **Lo revisa alguien distinto de mí** (regla 3 de `AGENTS.md`).

## Bloqueado / esperando a alguien

Cuatro cosas, todas para el próximo standup:

1. **Alejo (R1) y Nico (R3)** — aval de [ADR 0008](../adr/0008-asimetria-firma-trabajador.md)
   🔶: la firma propone vía LLM, el trabajador acepta por regla determinista. Toca
   `contracts/` (Alejo) y la interfaz del veto (Nico). **Sin aval no se implementa**; el plan
   B es el statu quo y se declara como límite en `VALIDATION.md`.
2. **Juanda (R5)** — hay una frase que precisar en `README.md` y `AGENTS.md`: *"mismo seed,
   mismo resultado"* es falso con un LLM en el bucle. Lo correcto es **"mismo seed + misma
   caché + mismas versiones"** ([ADR 0009](../adr/0009-frontera-del-determinismo.md)). No es
   error suyo: era un hueco que nadie había cerrado.
3. **Dani (R4) y Alejo (R1)** — `contracts/ronda.json` gana campo de tiempo (`trimestre`) y
   dos de diagnóstico (`n_vetos`, `n_fallback`). Cambio aditivo, no rompe nada.
4. ~~La cifra vigente de inspectores de trabajo~~ **RESUELTO por Mani:** la OIT publica
   **1.300 inspectores del trabajo en 36 direcciones territoriales** (proyecto ago-2023 a
   ago-2024). Reemplaza los 904 de ~2015. Con ~23M de ocupados son ≈**1 por cada 18.000
   trabajadores**, casi el doble del estándar OIT/OCDE de 1 por 10.000 que el propio
   ministerio invoca. **`C` ya tiene fuente**; lo que sigue sin fuente es cuántas inspecciones
   hace cada inspector por trimestre (supuesto S2). Detalle en
   [`docs/investigacion/1-teorica.md`](../investigacion/1-teorica.md) §3.

## Supuestos que tomé

Los 7 del motor están pre-declarados con impacto y mitigación en
[`engine/MODELO.md`](../../engine/MODELO.md). Los que R5 tiene que recoger en `VALIDATION.md`:

- **S2 · inspecciones por inspector por trimestre** — sin fuente. **Es el supuesto más
  importante del proyecto**: es el numerador de `p(E)`. Barrido de sensibilidad obligatorio.
- **S1 · factor prestacional ≈ 1,4-1,5** — ya estaba previsto (V3 del plan), sigue sin cifra exacta.
- **S3 · prima de protección del trabajador** — sin fuente. Con prima 0 es el caso extremo y se reporta.
- **S7 · el costo informal ignora la pérdida de crédito y de clientes formales** — sesgo de
  dirección **conocida**: subestima el costo de informalizar, luego **nuestra cascada es una
  cota superior por ese canal**. Conviene decirlo antes de que lo pregunten.
- **Reloj:** el backtest se mide **a 9 meses del decreto**. Escrito antes de conocer el
  resultado, a propósito.
