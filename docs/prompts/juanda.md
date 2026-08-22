# Prompt para la sesión de Claude Code de JUANDA (pegar completo como primer mensaje)

Estoy en un hackathon de 36 horas (PlatanusHack 26 Bogotá, track Simulations). El equipo construye un simulador de políticas públicas que responde "¿cuánta gente cumple la política y a quién le cae encima?", con población real de la GEIH del DANE, un motor determinista con veto de factibilidad, una capa LLM que descubre estrategias de adaptación, y rondas de mejor respuesta que producen una cascada de evasión. Caso demo: el aumento del salario mínimo del 23% en Bogotá (el caso salió de MI investigación — la GEIH y los ~20 experimentos naturales de alzas históricas).

**Antes de escribir una línea de código, lee:** `docs/PLAN.md` COMPLETO (soy el único rol que necesita verlo todo), `docs/ROLES.md` (sección Juanda) y `docs/UML.md`.

## Mi rol

Soy **R5 · Integración / validación / pitch**. **NO escribo features** — por diseño: soy el único que ve el todo, arbitro los recortes en cada checkpoint, y mi entregable estrella es EL número de validación.

- **Dueño exclusivo de:** `tests/`, `scripts/`, `Makefile`, los docs raíz (`README.md`, `AGENTS.md`, `ARCHITECTURE.md`, `VALIDATION.md`, `LICENSE`) y el deploy. Leo todas las carpetas; no edito `engine/`, `behavior/`, `web/` ni `data/`.
- **Rama:** `rol/integracion`. Merge de docs/tests cuando sea; superviso que los demás mergeen a `main` cada 6 horas y que `main` siempre corra.

## Orden de trabajo (estricto)

1. **AHORA (H+0 a H+1):**
   - Conectar Render (API) y Vercel (web) al repo espejo `vibe-coders-team/platanus-hack-26-T16-simulations` (el doble push ya está configurado; el deploy sale del espejo porque las plataformas no conectan al repo de la organización).
   - Búsqueda de prior art de 20 minutos, literal (V6): googlear la idea, citar en el `README.md` lo que exista (Meghir-Narita-Robin sobre Brasil, AgentSociety, PoliSim) — nombrarlo nosotros antes de que el agente del juez lo encuentre.
   - Escribir `README.md` (qué es, cómo se corre, qué es lo no obvio — en 20 renglones) y `AGENTS.md` (qué es en una frase · la pieza difícil con ruta exacta · cómo verificarlo tú mismo · qué NO hace · mapa de archivos) CON LA IDEA, aunque no haya código. `LICENSE` MIT.
2. **Cena con el mentor (~H+2) — llevar escritas las preguntas (V5):** hora exacta de presentaciones del domingo · ¿el freeze de 09:30 es por commit o por rama? · ¿un backtest con error grande pero reportado honestamente puntúa como ejecución seria?
3. **H+2 a H+4:** hola-mundo desplegado punta a punta (checkpoint C2: abre desde el celular de otro). `Makefile` inicial: `make run`, `make test`, `make validate` (aunque validate imprima "sin datos aún").
4. **H+4 a H+10:** verificación V4: serie histórica de alzas del salario mínimo 2000–2026 en un CSV limpio en `data/` (coordino con Alejo, él es dueño de la carpeta — yo le entrego el contenido). V8 (elasticidades publicadas) y V9 (el spike salarial en el mínimo, con Alejo).
5. **H+12 a H+20 — calibración (checkpoint C4):** correr el mundo SIN política y comparar contra `data/momentos.json`. Si a H+20 no calibra: **se cambia la métrica de validación, no el proyecto** — yo ejecuto ese recorte.
6. **H+20 a H+26 — EL entregable (checkpoint C5):** el backtest: calibrar hasta un año de corte, predecir las alzas siguientes (excluyendo 2020–21 por COVID, y decirlo), medir el error. **Se publica sea bueno o malo.** `VALIDATION.md` completo: metodología, número, control de contaminación (la política sin nombre + re-skinning), ablación del LLM, límites admitidos. `make validate` imprime EL número — el agente del juez lo va a ejecutar.
7. **H+26 en paralelo (si C4 cerró, con Nico):** el test de pico y placa (§5.5). Se cae sin discusión si compite con el número principal.
8. **H+28 a entrega:** video de respaldo del demo ANTES de que nadie pula nada · deploy final probado desde celular con datos móviles sin sesión · `make test` y `make validate` corren en una MÁQUINA LIMPIA (no la del autor) · commits legibles · repo entregado domingo 09:30.
9. **09:30 a pitch:** mínimo 5 ensayos cronometrados del guion (`docs/PLAN.md` §12, 3:30). Nadie abre el editor — yo lo hago cumplir.

## Reglas duras

- Los checkpoints C1–C6 son míos: si uno se pasa, el recorte se decide EN ESE MOMENTO, no a las 3am.
- `VALIDATION.md` nunca sobrevende: cada afirmación del README tiene que ser verificable en el repo — sobrevender ante un agente de código es peor que no vender.
- Standup de pie cada 6 horas: qué corre, qué está roto, qué necesita cada quien. Sueño escalonado: nunca los 5 despiertos ni los 5 dormidos.
- El reporte de cualquier agente es un reclamo: `git diff --stat` es la fuente de verdad.

## Definición de listo

Repo entregado a las 09:30 con: URL pública funcionando desde cualquier celular, `make validate` imprimiendo el número del backtest en máquina limpia, los 4 docs raíz completos y honestos, video de respaldo grabado, y el pitch ensayado 5+ veces en ≤3:30.
