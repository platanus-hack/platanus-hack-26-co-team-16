# ADR 0007 — Forma funcional de la probabilidad de sanción

**Estado:** aceptado (R2) · **Fecha:** 2026-08-22 · **Fuente:** hueco H3 · **Supera:** la fórmula abreviada de `docs/PLAN.md` §4 y del prompt de R2

> ⚠️ **Avisar en el standup.** Esto refina una fórmula escrita en el plan. No cambia el
> modelo (coincide con ella en el régimen relevante, ver abajo), pero cambia el código y las
> propiedades en los bordes.

## Contexto

El plan y el prompt de R2 escriben la pieza central del motor así:

```
prob_sancion = capacidad_fija / n_evasores
```

Como taquigrafía comunica la idea correcta. Como código es un error:

- **No está acotada.** Si hay pocos evasores, devuelve un número mayor que 1, que no es una probabilidad.
- **Está indefinida** cuando `n_evasores = 0`.
- **No declara unidades.** ¿"Capacidad" son inspectores? ¿inspecciones al año? ¿al trimestre?
  Sin unidades, el cociente no significa nada.

Y es la línea de la que sale toda la tesis del proyecto: si está floja, la tesis está floja.

## Decisión

Con `C` = número esperado de inspecciones efectivas en el trimestre sobre el universo del
modelo, y `E` = número de unidades evasoras observado en la ronda anterior:

```
p(E) = 1 − exp(−C / max(E, 1))
```

**Con micro-fundamento, no con conveniencia.** Si las `C` inspecciones se reparten al azar
entre las `E` unidades evasoras, el número de inspecciones que le caen a una unidad dada se
aproxima por una Poisson de media `C/E`. La probabilidad de recibir **al menos una** es
entonces `1 − e^(−C/E)`. Es el problema clásico de repartir bolas en cajas, no una curva
elegida para que la gráfica se vea bien.

Propiedades, que son la razón de elegirla:

| Propiedad | Valor |
|---|---|
| Rango | `p ∈ [0, 1)` para todo `E ≥ 1`. **Siempre es una probabilidad** |
| Monotonía | Estrictamente decreciente en `E`. **Más evasores ⇒ menos riesgo para cada uno: la cascada** |
| Borde superior | `E → 1` ⇒ `p = 1 − e^(−C)`. Con capacidad apreciable y un solo evasor, casi seguro lo agarran |
| Borde inferior | `E → ∞` ⇒ `p → 0`. La fiscalización se diluye hasta desaparecer |
| `E = 0` | Definida por continuidad; **irrelevante**, no hay a quién aplicarla |
| **Coincidencia con la fórmula del plan** | Para `C/E` pequeño, `e^(−x) ≈ 1 − x`, luego **`p ≈ C/E`**. En el régimen real (pocas inspecciones, muchos evasores) es la misma fórmula |

Esa última fila es lo que importa: **no estamos cambiando el modelo del plan, le estamos
dando la forma bien definida que coincide con él donde ocurre la acción y se comporta en los
bordes donde la versión abreviada se rompía.**

`C` se descompone y cada factor declara su origen:

```
C = inspectores_efectivos × inspecciones_por_inspector_trimestre × fraccion_universo
```

- `inspectores_efectivos` — de fuente ([`1-teorica.md`](../investigacion/1-teorica.md) §3).
- `inspecciones_por_inspector_trimestre` — **`# SUPUESTO:`, sin fuente hoy.** Barrido de sensibilidad obligatorio.
- `fraccion_universo` — participación de Bogotá y de los sectores modelados en el empleo nacional. De la GEIH.

**Chequeo de cordura, no de calibración:** la literatura de cumplimiento del salario mínimo
en EE.UU. reporta ~1,4% de probabilidad anual de investigación para una firma infractora
(AEA 2025). Si nuestro `p` inicial sale de un orden de magnitud muy distinto a un dígito
porcentual, el error está en `C`, no en el fenómeno.

## Alternativas descartadas

| Alternativa | Por qué no |
|---|---|
| **`min(1, C/E)`** | Acota, pero introduce un codo artificial en `C = E` que se confundiría con **el codo** que el proyecto dice descubrir. Inaceptable: sería fabricar el resultado con una función de recorte. |
| **`C / (C + E)`** | Bien acotada y suave, pero no se deriva de ningún proceso: es una curva escogida. La forma Poisson sale de un mecanismo que se puede explicar en una frase. |
| **Logística con parámetros libres** | Dos parámetros más que ajustar hasta que aparezca el umbral. Es exactamente el riesgo "la cascada sale de parámetros escogidos a conveniencia" del registro de riesgos. |
| **`p` exógeno y fijo** (Allingham-Sandmo original) | Es el supuesto que el proyecto existe para romper. Se conserva como **corrida de control**: con `p` fijo no debe haber cascada, y eso es un test. |

## Consecuencias

- Vive en `engine/fiscalizacion.py`, un concepto por archivo, con el docstring que explica la derivación Poisson.
- **Genera un test obligatorio** (`tests/README.md` #3): `p` es decreciente en `E`, y está en `[0,1)` para todo `E`.
- **Genera una corrida de control:** con `p` fijo, la cascada desaparece. Si no desaparece, la cascada viene de otra parte y hay que averiguar de dónde antes del pitch.
- El barrido de sensibilidad sobre `C` deja de ser opcional. Es la respuesta a *"¿y si le erraron a la capacidad?"*: se muestra el rango de `C` en el que la conclusión se mantiene.
