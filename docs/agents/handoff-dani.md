# Handoff — Dani · R4 · Diseño e interfaz

> **Tu memoria entre sesiones.** Léelo al abrir tu sesión de agente, actualízalo antes de cerrarla.
> Este archivo es solo tuyo: nadie más lo edita, así nunca da conflicto de merge.
> Tus carpetas: `web/` · Tu rama: `rol/interfaz`
> Tu misión, entregables y prompt de arranque: [`docs/ROLES.md`](../ROLES.md)

## Dónde quedé

_Lo más reciente arriba. Qué existe, qué acabas de hacer, qué necesita saber tu próxima sesión para no arrancar de cero. Corto: enlaza a commits y ADRs en vez de copiarlos._

- **2026-08-22 — Existe `web/prototipo/mapa.html`: el prototipo de movimiento (etapa 2).**
  Un solo archivo, cero dependencias, datos falsos, abre con doble clic. El mapa vivo de
  Bogotá: 4.500 celdas de 1.000 personas, campo de densidad del que emerge la silueta,
  cascada propagándose por presión económica, curva de la brecha y barrido del codo
  sincronizados al mismo reloj. Panel de afinación con `?tune`.
  **Todas las decisiones de diseño y su porqué están en [`web/DISENO.md`](../../web/DISENO.md) — léelo antes de tocar nada.**
- 2026-08-22 — Se descartó Claude Design para esta etapa: la pieza es movimiento y
  densidad, y un artboard estático no puede juzgar ninguna de las dos. Se reevalúa
  después, y solo para el aparato quieto (tipografía, paneles, tarjetas).
- 2026-08-22 — Repo scaffoldeado por Manuel. **`contracts/` sigue vacío** (solo README):
  los ejemplos de los tres JSON viven únicamente en `docs/PLAN.md` §4. El prototipo ya
  construye contra la forma exacta de `ronda.json`.

## En qué estoy trabajando

- [ ] Abrir el prototipo con `?tune` y congelar paleta y timings → actualizar los tokens en `web/DISENO.md`
- [ ] Etapa 3: esqueleto Next.js desplegado (con Juanda) — checkpoint C2, feo está bien
- [ ] Portar el motor visual del prototipo a `web/`, cambiando solo la fuente de datos

## Bloqueado / esperando a alguien

- **Alejo (R1):** confirmar el orden de magnitud de ocupados en Bogotá (~4,5M) — es lo
  que fija las 4.500 celdas. Y si la GEIH trae **algún** corte espacial dentro de la
  ciudad; si trae, el mapa deja de ser ilustrativo y gana muchísimo.
- **Manuel (R2):** congelar `contracts/ronda.json` como archivo, y el esquema de Supabase.
- **Juanda (R5):** conectar Vercel al repo espejo para poder desplegar.

## Supuestos que tomé

_Todo lo que decidiste sin dato duro. Además del `# SUPUESTO:` en el código, anótalo acá para que R5 lo recoja en `VALIDATION.md`._

Todos viven en `web/prototipo/mapa.html`, grepeables con `SUPUESTO:`. Ninguno afecta al
motor: son solo para que la animación tenga una forma plausible antes de que exista el dato.

- **~4,5 millones de ocupados en Bogotá** → 4.500 celdas × 1.000 personas. Sin verificar.
- **La silueta de Bogotá es un polígono dibujado a mano.** Aproximada, ilustrativa, y
  declarada como tal en pantalla. Ninguna conclusión depende de su forma.
- **Sectores, participaciones e informalidad base son placeholder.** Los reales salen de
  `data/momentos.json`.
- **Los parámetros de la cascada** (informalidad base 0,42, codo en 15%, amplitud 0,16)
  son inventados para dar forma a la animación. El motor de Manuel los reemplaza entero.
- **La mezcla de estrategias** es inventada; la real viene de `behavior/` agregada por arquetipo.
- **La posición de las celdas no es geográfica.** Es agrupación por sector. Rotulado en pantalla.
