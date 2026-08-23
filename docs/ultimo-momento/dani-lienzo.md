# DANI · lienzo — lo que se ve mientras corre

> Pega esto en una sesión nueva. **Tu zona:** `web/enjambre/componentes/` (menos `reporte/`) y
> `app/page.tsx`. **No toques** `app/reporte/*`, `componentes/reporte/*`, `lib/narrativa.ts`
> (Juanda está ahí) ni `api/`, `behavior/` (Manu).
> `main` sin PR: commit chico, `git pull --rebase origin main` antes de cada push. **60 min.**
> Explora los archivos; abajo están los puntos de entrada, no la solución.

**El hilo que une todo:** lo más valioso de esta simulación es **qué decidió cada empresa y por
qué** — está medido que el 47% de las justificaciones evalúan despedir y lo descartan por caja
(`docs/agents/hallazgos-dani-cache-decisiones.md`). Hoy eso casi no se ve. Todo lo de abajo es
quitar ruido visual para que esa señal aparezca.

## 1 · Animaciones del enjambre (item 5) — `componentes/enjambre/`

- **`Empresas.tsx`** — las celdas nacen con `popNacimiento()` (línea ~24) más un **halo aditivo
  de color** (`halos`, ~línea 49-110) y **anillos de decisión por familia** (~112-130). Se pide:
  aparición con **pop simple, sin círculo de color alrededor**. El halo es el sospechoso #1.
  Ojo: los anillos de decisión son *información* (color = familia de la estrategia); si los
  quitas, quitas señal. Evalúa dejarlos y matar solo el halo.
- **`Onda.tsx`** — es el **círculo azul gigante** que encapsula industrias. Son 3 capas de anillos
  (`AZUL = #5b9dff`, `capas` ~línea 22) que se expanden desde el centro de masa del incumplimiento.
  Se monta en `Escena.tsx:76`. **Quitarlo:** borra el `<Onda motor={motor} />` de `Escena.tsx`.
  El archivo puede quedarse (no estorba).
- **Al ganar espacio visual, gana la visibilidad de decisiones.** Si algo aparece al hacer
  hover/clic en una celda con su decisión y su justificación, ese es el mayor valor de la hora.

## 2 · Cifras arriba a la derecha (item 6) — `componentes/Paneles/Hero.tsx`

Hoy muestra una cifra principal (informalidad) más un array `secundarias` (brecha, sanción,
fallback, sin-salida). Se pide: **solo informalidad**, que **diga que es informalidad** (hoy la
etiqueta sale al pasar el mouse) y que **muestre el cambio con el valor inicial**.
Ya tienes todo calculado ahí: `inicial = rondas[0].contrato.tasa_informalidad` y `delta`.
Algo como `24,1% informalidad · desde 18,0% (+6,1 pp)`.

> Nota: `fallback` y `sin_salida` estaban ahí porque son lo primero que pide un juez técnico. Si
> los sacas del hero, que aparezcan en la carta de ronda del punto 3.

## 3 · Info de la ronda (item 7) — `componentes/Paneles/BarraTiempo.tsx`

Hoy es una barra centrada abajo que se despliega. Se pide: **carta / pop-up a la derecha, bajo el
porcentaje de informalidad**. La posición la fija su `style` (`className="panel"` + inline).
El `Hero` vive arriba a la derecha; esta carta va debajo. Los datos ya los tiene:
`rondaMostrada`, `avance`, `poblacion.rondas_totales`, `meses_por_ronda`.

> ⚠️ Manu está haciendo que las rondas totales sean **3** en modo maqueta. `BarraTiempo` ya lee
> `poblacion.rondas_totales` (no lo hardcodees) — pero verifica que el `?? 4` de la línea ~27 no
> te mienta si el campo no llega.

## 4 · Leyenda de decisiones (item 8) — `componentes/Paneles/Leyenda.tsx` y `Estrategias.tsx`

Están apiladas en `ColumnaIzquierda.tsx` abajo a la izquierda. Se pide **la leyenda de decisiones
más grande y fácil de seguir**. Hoy `Leyenda` usa fichas de 8 px y `fontSize: 11.5`; `Estrategias`
es el reparto de familias. Súbelas de tamaño y dales jerarquía — es la clave para leer el mapa.

## 5 · Pantalla de entrada (item 9) — `componentes/Menu.tsx` y `Carga.tsx`

En `Menu.tsx`:
- **línea ~27**: «¿Qué política quieres **estresar**?» → **simular**. Y busca `estresar` en todo
  `web/` por si aparece en otro lado.
- **línea ~25**: borra el kicker `mercado laboral de Bogotá · GEIH-DANE 2026`.
- **líneas ~51-75**: el bloque del backtest («El backtest falsa este modelo… dónde no hay que
  creerle →»). **Quítalo de esta pantalla.** *(Juanda borra la copia del reporte; tú la de acá.)*
- **Pon el logo aquí.** Está en `Carga.tsx:54` como `<img src="/hive-logo.png">`. Muévelo:
  logo en el menú, no en la pantalla de carga.

---

## Verificación antes de decir que está hecho

```bash
cd web/enjambre && npx tsc --noEmit && npm run build     # los dos en exit 0
grep -rn "estresar\|no hay que creerle" componentes/ app/page.tsx   # 0 resultados en TU zona
git diff --stat
```
Y míralo corriendo: `make servidor` en una terminal, `make enjambre` en otra, `modo=reglas`
para no gastar.
