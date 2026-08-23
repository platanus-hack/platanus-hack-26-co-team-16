# JUANDA · reporte — que se entienda sin traductor

> Pega esto en una sesión nueva. **Tu zona:** `web/enjambre/app/reporte/page.tsx`,
> `web/enjambre/componentes/reporte/Graficas.tsx`, `web/enjambre/lib/narrativa.ts` y docs raíz
> (`VALIDATION.md`, `README.md`, `AGENTS.md`). **No toques** `componentes/Paneles/*`,
> `componentes/enjambre/*`, `Menu.tsx`, `Carga.tsx` (Dani) ni `api/`, `behavior/` (Manu).
> `main` sin PR: commit chico, `git pull --rebase origin main` antes de cada push. **60 min.**

## 1 · Nivel de abstracción (item 1) — `app/reporte/page.tsx` y `componentes/reporte/Graficas.tsx`

**Ninguna sigla sin explicar.** Hoy el reporte suelta GEIH, DANE, CST, pp, p10/p90, celda,
arquetipo, backtest, ablación como si el lector los supiera. Cada una: primera aparición
explicada en una línea, o reemplazada por lenguaje llano.

**Lo que hay que subir de prioridad: las decisiones de los actores.** Es lo más valioso que
produce esta simulación y hoy casi no se ve. El material está medido en
[`docs/agents/hallazgos-dani-cache-decisiones.md`](../agents/hallazgos-dani-cache-decisiones.md)
y es fuerte:

- **211 de 518 decisiones (40,7%) fueron informalizar; solo 1 fue despedir.**
- **47% de las justificaciones (242) evalúan despedir y lo descartan explícitamente por caja.**
- **70% (361) invocan la caja o la liquidez.** El único que despidió, despidió exactamente los
  17 que su caja alcanzaba a indemnizar.
- El modelo **inventó 54 nombres fuera del menú** y ninguno cayó en el balde «otra».

**Incluye las trayectorias.** Corremos N corridas completas y publicamos la **mediana** con el
rango entre ellas. Hoy eso no se explica en el reporte y es justo lo que hace defendible la banda.
Con N chico, `p10`/`p90` **son el mínimo y el máximo** — el nombre honesto es «rango entre las N
corridas», no percentiles.

## 2 · Quitar «dónde no hay que creerle» (item 3)

Está en `app/reporte/page.tsx:238` (el título de la sección) y citado en `:71`, `:80`, `:273` y en
`componentes/reporte/Graficas.tsx:188`.

**Quita el rótulo, no el contenido.** Los límites declarados son el mejor activo del proyecto; lo
que no funciona es el nombre, que suena a confesión. Renómbralo a algo como **«Alcance del
modelo»** o **«Qué mide y qué no»** y deja los límites adentro.

> ⚠️ La frase también está en `componentes/Menu.tsx:74`. **Esa es de Dani, no la toques.**

## 3 · El PDF (item 4)

Sale cortado, muestra solo un fragmento. Es la impresión de `/reporte`. Mira los `@media print`
en `app/globals.css`… **pero ese archivo no está asignado a nadie** — si lo necesitas, avisa en el
grupo antes. Sospechosos: alturas fijas / `overflow: hidden` / `position: absolute` en los
contenedores del reporte, y gráficas que no reflowean. Verifica con Cmd+P → «Guardar como PDF».

## 4 · Lo que hay que declarar antes de que lo pregunten

Dos cosas medidas hoy que el reporte no dice y que un juez con un agente de código encuentra:

**a) `alfa = 1,875` es un parámetro libre ajustado.** `engine/fiscalizacion.py`. Está calibrado
contra el placebo (que la corrida sin política reproduzca lo observado), no contra datos de
fiscalización. Es tu pendiente #4 del handoff de auditoría, y aquí está el barrido que faltaba:

| `alfa` | informalidad final a 0% | a 23% | brecha | **placebo** |
|---|---|---|---|---|
| **0,000** (el reparto uniforme de la ADR 0007) | 0,9567 | 0,9567 | +77,68 pp | **+77,68 pp** |
| 1,000 | 0,1631 | 0,2857 | +10,58 pp | −1,68 pp |
| **1,875 (el que corre)** | **0,1707** | **0,2406** | **+6,07 pp** | **−0,92 pp** |
| 2,500 | 0,2124 | 0,2857 | +10,58 pp | +3,25 pp |

Frase sugerida: *«El reparto de la capacidad de inspección tiene un parámetro de visibilidad
calibrado contra el escenario sin política, porque no tenemos datos de fiscalización. Es el
parámetro más sensible del modelo y publicamos su barrido.»* Va en `VALIDATION.md`.

**b) Por qué no se despide (item 2 de la lista).** El 100% de empleo no es un error: el prompt le
dice al agente que **sus ingresos y su producción no cambian** (`behavior/prompts/arquetipo.md:12-14`)
y que **despedir cuesta indemnización hoy** mientras informalizar cuesta $0 hoy. Con demanda fija,
despedir solo destruye producto y encima cuesta caja: queda dominado por aritmética. **Que un alza
del mínimo se pague en informalidad y no en despidos es coherente con la evidencia colombiana** —
lo que no es defendible es presentarlo como un descubrimiento del modelo.

**c) Si te alcanza:** `subir_precios` es el 27% de las decisiones y **no mueve ninguna cifra del
agregado** (no hay respuesta de demanda; el propio `behavior/rondas.py:779` lo dice). Hoy se
agrega junto a decisiones que sí mueven el mundo. Merece una etiqueta que lo distinga.

---

## Verificación antes de decir que está hecho

```bash
cd web/enjambre && npx tsc --noEmit && npm run build     # los dos en exit 0
grep -rn "no hay que creerle" app/reporte componentes/reporte lib/narrativa.ts   # 0
git diff --stat
```
Y abre `/reporte`, imprímelo a PDF, y léelo como si no supieras qué es una GEIH.
