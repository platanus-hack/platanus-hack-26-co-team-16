# Handoff compartido — qué hay en `main` ahora mismo

> **Un solo escritor: Juanda (R5).** Los demás escriben en `docs/agents/handoff-<su-nombre>.md`.
> Este archivo dice qué está mergeado y funcionando en `main`, nada más. No es un diario ni un backlog personal.
> Escrito así a propósito: con 5 personas, un archivo de memoria compartido con 5 escritores da conflicto de merge en cada PR, justo en el archivo que carga el estado.

## Estado de `main`

- **2026-08-22 03:0x** — Reorganización de `docs/`: los 5 insumos pasaron a `docs/fuentes/` (renombrados por persona), el brainstorm y el transcript a `docs/historia/` (superados, se conservan por trazabilidad), y se agregó `docs/README.md` como índice con el nivel de autoridad de cada documento. Todas las rutas referenciadas quedaron corregidas. Los prompts de arranque quedaron alineados con la regla de PR.
- **2026-08-22 02:52** — Scaffold del repo. Contrato (`AGENTS.md` + `CLAUDE.md`), reglas de trabajo en paralelo, esqueleto de carpetas con dueño, handoffs por persona, ADRs de las decisiones ya tomadas, licencia MIT, espejo de deploy configurado. **Cero código de producto todavía.**

## Roadmap del equipo

Los entregables por rol viven en `docs/ROLES.md` y el cronograma en `docs/PLAN.md` §8. Acá solo lo transversal que no tiene dueño obvio y que se muere si nadie lo mira.

### Ahora

- [ ] **Espejo de deploy en la máquina de cada uno** (V7). Ya quedó en el clon de Manuel. Cada quien corre los dos `git remote set-url --add --push origin ...` (org + `vibe-coders-team/platanus-hack-26-T16-simulations`), o el repo de deploy se queda viejo.
- [ ] **Proteger `main` en GitHub** para que el PR obligatorio sea real y no honor system. Requiere admin del repo de la organización: preguntar al organizador. Si no se puede, activarlo en el espejo. — Juanda
- [ ] **Preguntas al mentor en la cena** (V5): hora exacta de presentaciones · si la entrega de 09:30 congela por commit o por rama · si un backtest negativo pero honesto puntúa como ejecución seria.

### Siguiente (bloqueado hasta que exista lo de arriba)

- [ ] **CI en PR** (~H+6, después del primer test): GitHub Action que corre `make test` en cada PR. Antes del primer test no se pone, porque un CI siempre rojo enseña a la gente a ignorarlo. — Juanda con Manuel
- [ ] **`contracts/*.json` congelados** (H+4) con los ejemplos del `PLAN.md` §4. — Alejo, Manuel, Nico
- [ ] **`Makefile`** con `run` / `test` / `validate`. — Juanda

### Entrega (no se toca hasta H+28, pero no puede olvidarse)

- [ ] `platanus-hack-project.jsonc` lleno (nombre, one-liner, descripción, deploy URL)
- [ ] `project-description.md` reemplazado
- [ ] Logo 1000x1000 PNG, máximo 500kb — el actual hay que verificar que cumpla
- [ ] `README.md` reescrito (20 renglones: qué es, cómo se corre, qué es lo no obvio) + prior art citado
- [ ] `ARCHITECTURE.md` y `VALIDATION.md` llenos
- [ ] **Video de respaldo del demo, grabado antes de pulir nada**
- [ ] Deploy final probado desde un celular ajeno, en datos móviles, sin sesión iniciada

### Hecho

- [x] 2026-08-22 — Scaffold del repo para trabajo concurrente con agentes
- [x] 2026-08-22 — Espejo de deploy configurado (clon de Manuel)
