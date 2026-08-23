# `web/` — Interfaz (Next.js)

**Dueño: Dani (R4)** · rama `rol/interfaz`

La interfaz es el 20% de impacto de la rúbrica. Un extraño con el link, sin manual y sin registrarse, tiene que entenderla.

## Dónde está

**`enjambre/` es la interfaz** (Next.js + three.js, conectada al motor real por
SSE contra `api/servidor.py`). Se corre con `make servidor` + `make enjambre`;
su documentación está en [`enjambre/README.md`](enjambre/README.md).

`prototipo/mapa.html` es el prototipo de movimiento con datos falsos, superado.
`PLAN-VISUAL.md` es la dirección que `enjambre/` ejecuta.

De los cuatro elementos de abajo, `enjambre/` trae hoy la **curva de la brecha**,
el **slider de política** y el **desglose de estrategias** con feed de decisiones
en vivo. El mapa distributivo sector × tramo sigue pendiente.

## Qué va aquí

Los cuatro elementos, en este orden:
1. **Curva de la brecha** — escenario sin adaptación (línea recta, ronda 0) vs corrida con adaptación, rondas 0→3. Es la imagen del pitch.
2. **Slider de política** — 7 / 13,6 / 23% más el barrido fino precomputado que muestra el codo.
3. **Mapa distributivo** — sector × tramo de ingreso, con bandas de incertidumbre.
4. **Desglose de estrategias** por segmento, feed Realtime de decisiones, y 3-4 historias con cara.

## Qué NO va aquí

- Lógica de simulación de ningún tipo.
- Auth, registro, cuentas.
- `engine/`, `behavior/`, `data/`, ni los docs raíz.

## Cómo desbloquearte

Construye contra el ejemplo de `contracts/ronda.json` con datos falsos desde ya. No esperes a nadie.
