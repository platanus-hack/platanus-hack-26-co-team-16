# EL ENJAMBRE — la interfaz

Next.js (App Router) + React Three Fiber. Muestra **la corrida real** del motor,
transmitida ronda a ronda desde `api/servidor.py`. Nada precomputado.

## Correr

Dos procesos, dos terminales, desde la raíz del repo:

```bash
make servidor     # API Python en :8000 (venv activo)
make enjambre     # esta interfaz en :3000
```

`next.config.mjs` reescribe `/api/*` hacia `http://localhost:8000` (variable
`ENJAMBRE_API` para apuntarlo a otro lado en deploy).

## El flujo de pantallas

`carga` → `menu` → `politica` → `simulacion`. La máquina vive en `app/page.tsx`
y el estado en `estado/simulacion.ts` (zustand). `estado/flujo.ts` abre el
`EventSource` contra la API y vierte los eventos al almacén; también imprime en
la consola del navegador el debug por ronda, espejo de los prints del servidor.

## El enjambre (three.js)

`componentes/enjambre/` — todo instanciado, sin física:

| Pieza | Qué dibuja |
|---|---|
| `motorVisual.ts` | El estado interpolado que se dibuja a 60 fps. React no re-renderiza por frame: la escena lee de acá. La interpolación es estética, entre dos estados que el motor **sí** calculó. |
| `Empresas.tsx` | Las 81 celdas empleadoras. Área ∝ empleo vivo (una celda que despide se encoge), color hueso→**azul** según su fracción informal real, anillo del color de la familia cuando la celda decide, nacimiento con pop escalonado. |
| `Personas.tsx` | Los puntos-persona, en un shader de `THREE.Points`. Verde = formal, ámbar = jornada recortada, **azul** = informal, aro hueco = expulsado (deriva fuera de su celda). |
| `Onda.tsx` | La onda de informalización: anillos que crecen con la informalidad **nueva** de la grilla, centrados en su centro de masa. |
| `Escena.tsx` | Composición, hover y el LOD. |

**LOD (`lib/disposicion.ts`)**: el zoom decide cuántas personas representa un
punto — 8.000 → 3.000 → 1.000. Al cruzar un umbral los puntos se subdividen y
los hijos vuelan desde la posición de su padre (`tEntrada`), en vez de saltar.
El piso de 1.000 es la unidad visual que declara `DISENO.md`: la GEIH expande
~630 personas por fila encuestada, así que bajar de ahí sería dibujar una
resolución que la encuesta no tiene.

## Qué NO se dibuja, a propósito

El motor no modela contrataciones (el empleo solo baja), ni salarios que
cambian, ni productividad, ni utilidad, ni subsidios, ni deuda. Nada de eso
aparece en pantalla ni en el globo de hover. Un nodo es una **celda sector ×
tamaño de la GEIH**, no una empresa individual, y la leyenda lo dice.

## Verificación

`?modo=reglas` corre la ablación determinista ($0, sin API key) — para
desarrollo. `?prueba=1` reemplaza `requestAnimationFrame` por un bucle de
`MessageChannel`: Chrome estrangula rAF en pestañas ocultas y sin eso el
enjambre no anima bajo automatización. Ninguno de los dos afecta al usuario.
