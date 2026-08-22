# Prompt para la sesión de Claude Code de DANI (pegar completo como primer mensaje)

Estoy en un hackathon de 36 horas (PlatanusHack 26 Bogotá, track Simulations). El equipo construye un simulador de políticas públicas que responde "¿cuánta gente cumple la política y a quién le cae encima?", con población real de la GEIH del DANE, un motor determinista con veto de factibilidad, una capa LLM que descubre estrategias de adaptación, y rondas de mejor respuesta que producen una cascada de evasión. Caso demo: el aumento del salario mínimo del 23% en Bogotá.

**Antes de escribir una línea de código, lee:** `docs/PLAN.md` (secciones 1.1, 4 y 12), `docs/ROLES.md` (sección Dani) y `docs/FLUJO.md`.

## Mi rol

Soy **R4 · Diseño e interfaz**. La interfaz ES el 20% de impacto de la rúbrica, y además el premio de voto público exige que **un extraño con el link la use sin manual, sin registro y sin nadie al lado**.

- **Dueño exclusivo de:** `web/`. NO toques `engine/`, `api/`, `behavior/`, `data/` ni los docs raíz.
- **Rama:** `rol/interfaz`. Commits pequeños; merge a `main` mínimo cada 6 horas.
- **Stack:** Next.js + Supabase (Realtime para el feed). Charts 2D ligeros (la decisión del plan: canvas/SVG 2D le gana a cualquier 3D en tiempo de hackathon).

## La regla que ordena todo mi trabajo

Cada elemento de pantalla existe para mostrar UNO de los cuatro datos del plan (§1.1). Si un componente no sirve a ninguno, no se construye:

| Dato | Componente | Prioridad |
|---|---|---|
| A2 — dónde está el codo | **La curva de la brecha**: línea de la proyección oficial (ronda 0) vs la cascada (rondas 1–3), + vista del barrido de % con el umbral | **1 — es LA imagen del pitch** |
| (palanca) | **Slider de política**: 7% / 13,6% / 23% + barrido fino precomputado | **1** |
| A3 — a quién le cae encima | **Mapa distributivo**: quién gana/pierde por sector × tramo de ingreso, SIEMPRE con banda de incertidumbre (nunca un número pelado) | **2** |
| A4 — por qué evade cada quien | **Desglose de estrategias** por segmento (cumplir/informalizar/despedir/absorber…) | **3** |
| (vida) | **Feed Realtime** de decisiones llegando + **3–4 historias con cara** ("panadería de 4 empleados en Suba: informaliza a 2") | **3** |

## Orden de trabajo (estricto)

1. **AHORA (H+0 a H+4):** esqueleto Next.js desplegado (Juanda conecta Vercel/Render al repo espejo — coordina con él). Feo está bien; desplegado es obligatorio (checkpoint C2: abre desde el celular de otro).
2. **H+0 en adelante — NO esperes a nadie:** construye contra `contracts/ronda.json` y `contracts/decision.json` (ejemplos concretos en `docs/PLAN.md` §4) con datos falsos generados por ti. Cuando el backend real exista, solo cambias la fuente.
3. **H+4 a H+10:** la corrida punta a punta SE VE (checkpoint C3): mover el slider dispara `POST /simulaciones`, el feed se llena por Realtime, la curva se dibuja ronda a ronda.
4. **H+10 a H+20:** mapa distributivo con bandas + desglose de estrategias. Esquema de Supabase acordado con Manuel.
5. **H+20 a H+28:** pulido visual, las historias narradas (vienen de la capa de Nico), y los **escenarios de la demo precomputados** (el pitch de 3:30 no puede esperar una corrida en vivo de 4 minutos; todo lo que se muestra en el pitch carga instantáneo). **H+28 = feature freeze absoluto.**

## Reglas duras

- Sin auth, sin registro, sin onboarding. Link → pantalla → slider. Un desconocido decide en 10 segundos si entiende.
- Todo número con banda; la incertidumbre es un feature del diseño, no un adorno.
- Mobile importa: el voto público y el checkpoint C2 se prueban desde un celular.
- Estados de carga y error diseñados: el wifi del hackathon se cae siempre.
- El reporte de cualquier agente es un reclamo: verifica con `git diff --stat` y abriendo la página.

## Definición de listo

La URL pública abre desde un celular con datos móviles sin sesión; mover el slider al 23% muestra la curva de la brecha con la cascada, el mapa de quién pierde con bandas, y el desglose de estrategias; los escenarios del pitch cargan precomputados sin latencia.
