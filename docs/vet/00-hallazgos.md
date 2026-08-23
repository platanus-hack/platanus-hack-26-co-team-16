# Vet de `main` (c63343f) — tabla consolidada · 22-ago 22:15

Tres auditorías de solo lectura sobre el commit `c63343f`. Todo con evidencia.

## 🔴 Los cinco que matan

| id | qué | evidencia | costo | dueño |
|---|---|---|---|---|
| S1-1 | **`n_parafrasis>=2` REVIENTA.** `round(v,4)` sobre `banda.tipo` que es string → TypeError al serializar la 1a ronda. La banda que AGENTS.md declara no-negociable no está apagada: es **imposible de encender** | `behavior/rondas.py:119-122`, `_percentiles:584`. Reproducido | 0,5h | Nico |
| S3-1 | **El backtest NO es fuera de muestra**, contra lo que afirma VALIDATION.md. La corrida usa `poblacion.parquet` (2026) y arranca la ronda 0 en 30,57%, el dato POST-política. `poblacion_2025.parquet` existe y **ningún ejecutable lo lee** | `VALIDATION.md:159-163` vs `:167-171`, `behavior/rondas.py:228`, `prediccion_modelo.json` | 2h + $1,4 | Nico + Alejo |
| S2-1 | **`?modo=reglas` se ve idéntico a la corrida real**, con citas entre comillas incluidas. Un juez no puede saber si corrió con LLM o con una regla fija | `flujo.ts:44` solo hace console.info del modo; `simulacion.ts` no tiene campo; `BarraTiempo.tsx:69` no lo imprime | 1h | Dani + Manuel |
| S2-2 | **La interfaz nunca pide `parafrasis>1`**, así que la banda siempre sale degenerada y el área de la curva tiene altura cero | `flujo.ts:35` arma el query solo con `aumento_pct` y `seed` | 2h | Dani + Nico |
| S1-2 / S1-3 | `parafrasis_por_peso=True` → IndexError seguro. `parafrasis>=6` por la API → ValueError: solo existen 5 archivos de paráfrasis y la API acepta 9 | `rondas.py:551-563`; `cliente.py:37-43` vs `servidor.py:88`. Reproducidos | 1,5h | Nico |

## 🟠 Los que encuentra un juez

| id | qué | evidencia | costo | dueño |
|---|---|---|---|---|
| S2-5 | **La progresión de rondas: causa raíz encontrada.** `motorVisual` toma `rondas[length-1]` y descarta las intermedias. Con caché caliente llegan las 3 juntas y se ve el salto a 3/3 | `motorVisual.ts:79-81` | 3h | Dani |
| S3-2 | El **35,60%** (mitad del argumento de robustez) no tiene fuente en ninguna parte del repo | `VALIDATION.md:51` | 0,25h | Juanda |
| S3-9 | Hay un **segundo episodio de backtest** (2024→2025: +2,63pp con alza de 9,5%, dirección opuesta) medido, versionado e impreso, pero **ausente de VALIDATION.md** | `momentos_2024.json`, `validate.py:174-179` | 0,5h | Juanda |
| S3-6 | `behavior/README.md` sigue afirmando "el dato A1 aguanta, +28 a +45 pp" que VALIDATION.md ya declaró falsado | `behavior/README.md:86-90,309-316` | 0,5h | Nico |
| S1-8 | El agente lee su **planta original**, no la viva. Ya despidió y propone despedir sobre la planta vieja: el veto lo rechaza y lo empuja al fallback | `capa.py:188` vs `veto.py:316-320` | 1h | Nico |
| S1-7 | La banda de trayectorias (la honesta, 22,5pp) **no existe en el camino del producto**. La API corre una sola trayectoria | `servidor.py:169-181` | 3h | Manuel + Nico |
| S2-3 | `nJor` tiene un `+0.15` inventado en el front, sin marcar. Infla los puntos ámbar y no cuadra con la cifra real que se muestra al lado | `Personas.tsx:194` | 0,5h | Dani |
| S2-7 | `fraccion_fallback` y `sin_salida` viajan pero **ningún panel los lee**. Es lo primero que pide un juez técnico | `serializar.py:184-191` | 1h | Dani |
| S1-14 | El umbral de alarma de fallback (5%) vive solo en el CLI. **La corrida de reglas ya lo supera: 7,4%** | `demo.py:96-97`; medido | 0,5h | Nico |
| S3-4 | G3 compara la corrida sin política contra `momentos.json` (2026, post-política) en vez de `momentos_2025.json` | `validate.py:106-109` | 2h | Juanda |
| S3-7 | El test de clon limpio **pasa por construcción**: compara dos ramas que en un clon limpio son la misma | `test_reproducible_en_clon_limpio.py:74-88` | 1h | Juanda |
| S3-10 | **G1 nunca puede dar verde**: la tercera razón de bloqueo se agrega incondicionalmente | `validate.py:66-76` | 1h | Juanda |
| S2-4 | El radio de la onda salta de 0 a ~5 con una brecha de 0,05pp. Es el elemento más grande de la pantalla y nada dice qué mide | `Onda.tsx:57` | 1h | Dani |
| S2-8 | La conversión a pesos ("$X billones/mes") se hace **en el navegador**, fuera de la capa que declara "cero números inventados" | `Metricas.tsx:27,45` | 1h | Manuel + Dani |

## Correcciones a lo que yo había dicho

- **B6 (industrias) NO está roto.** `data/empresas.parquet` tiene 9 sectores con prefijos únicos y `desde_empresas` usa el `empresa_id` completo, sin truncar. Los 4 hardcodeados solo viven en `arquetipos_falsos()` (andamio). Baja de 🔴 a 🟡: **el comentario está mal, el código no** (S1-9, S1-10).
- **La clave de caché SÍ incluye la política.** Mover la perilla sí mueve la corrida. Verificado con hashes (S1-5).
- **La interpolación es honesta.** Ningún panel de texto lee estado interpolado; los 8 leen del contrato (S2-3 verificado).

## El pre-registro: se sostiene, con un matiz que hay que decir primero

Criterio commiteado en `2d4aa7e` a las **17:59:53**. Los datos llegaron en `93daba0` a las **18:17:04**, 18 minutos después. Bloque de las dos ramas **idéntico byte a byte** (1056 vs 1056). Ningún umbral se movió.

**Pero no fue ciego.** `2d4aa7e` ya traía "lo que ya se sabe apunta a la rama B" con el modelo en 63,8% y el observado en 31,2%. Es "umbral fijado sabiendo la dirección", no "fijado a ciegas". Ellos mismos lo declararon. **Si lo decimos nosotros primero es rigor; si lo encuentra un juez es fraude.**

---

## Apéndice · Verificación contra `b180d51` (22-ago 23:00)

`main` avanzó tres commits después de la línea base. Revisado uno por uno:

| Qué | Estado |
|---|---|
| **S1-1** (`round()` sobre `banda.tipo`) | 🔴 **sigue vivo**, ahora en `behavior/rondas.py:120`. `rondas.py` no se tocó |
| **C3** (`temperature` sin fijar) | 🔴 **sigue vivo**. `_llamar` (`cliente.py:197-200`) pasa solo `model` y `max_tokens` |
| S2-1, S2-2, S2-5 | sin cambios: `flujo.ts`, `simulacion.ts`, `motorVisual.ts` no se tocaron |
| S3-1 y el pre-registro | sin cambios: `VALIDATION.md` no se tocó |

### 🔴 V-1 · NUEVO: la caché quedó fría y nadie lo dijo

`13c5a5b` cambió `MODELO_MASA` de Haiku 4.5 a **`claude-sonnet-5`** (`behavior/cliente.py:34`) y subió
`max_tokens`. **La clave de caché incluye el modelo** (`cache.py:33-40`), así que **toda la caché
existente quedó invalidada**.

Tres consecuencias que cambian decisiones:

1. **Cada corrida vuelve a costar plata y a tardar de verdad.** El `tope_usd` de la API sigue en `3.0`
   por defecto (`api/servidor.py:89`), y ahora sobre un modelo más caro.
2. **Con `parafrasis=5`, que ya se decidió, son 5× llamadas** sobre ese modelo. Hay que remedir el costo
   de una corrida **antes** de cablearlo al front, no después.
3. **El síntoma de B1 puede haber desaparecido por accidente**: con caché fría las rondas ya no llegan en
   ráfaga. **Pero S2-5 sigue siendo un bug latente** (`motorVisual.ts:79` descarta las intermedias) y
   vuelve a morder en cuanto la caché se caliente. No se cierra por observación, se cierra con la cola.

**Dueño:** Nico (`behavior/`) mide el costo; Manuel (`api/`) ajusta `tope_usd`. **Costo: 0,5h de medición.**
