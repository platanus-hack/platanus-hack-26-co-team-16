# `web/laboratorio/` — la evidencia que se acumula entre corridas

## Qué hay acá

- **`historico.jsonl`** — una línea JSON por corrida terminada. Lo escribe la
  interfaz sola, al cerrar la última ronda, vía `POST /laboratorio/registro`.
  **No está en el repo hasta que alguien corra el simulador**: se llena con el
  uso y se commitea como cualquier otro artefacto.
- **`figuras/*.svg`** — las mismas gráficas de la página `/laboratorio`, pero
  estáticas, para pegar en el pitch o en un documento. Las genera
  `web/scripts/graficas_laboratorio.py`.

## Por qué existe

Sin esto, cada corrida se pierde al cerrar la pestaña y el proyecto solo puede
mostrar un punto: un alza, un resultado. La curva interesante —dónde se quiebra
el sistema— vive en el barrido completo, y el barrido se construye **usando** el
simulador, una corrida a la vez.

## Cómo se llena

```bash
make servidor            # la API en :8000
make enjambre            # la interfaz en :3000
# corre una simulación completa; al terminar se archiva sola
python3 web/scripts/graficas_laboratorio.py   # regenera los SVG
```

El script usa **solo biblioteca estándar**: `AGENTS.md` congela dependencias
nuevas en el feature freeze y el proyecto no tiene matplotlib. Un SVG es texto.

## La trampa del deploy

En un host serverless el sistema de archivos es de solo lectura, así que el
`POST` falla y la página sirve lo que esté commiteado. Es deliberado: la
evidencia se acumula corriendo el simulador en local y se publica por git, no
por escrituras en producción. La página lo dice cuando el histórico está vacío.

## Qué hay hoy en el histórico, y qué se descartó

Las 5 corridas commiteadas son un barrido de alza con `seed=42` en **`modo=reglas`**,
corridas todas contra el mismo código (después de mergear `main` en `rol/interfaz`):

| alza | informalidad final | empleo final | brecha |
|---:|---:|---:|---:|
| 0 % | 17,07 % | 100,0 % | −0,92 pp |
| 7 % | 21,24 % | 100,0 % | +3,25 pp |
| 13,6 % | 21,90 % | 100,0 % | +3,91 pp |
| 23 % | 24,06 % | 100,0 % | +6,07 pp |
| 25 % | 24,06 % | 100,0 % | +6,07 pp |

**Se descartaron 3 corridas anteriores** (13,5 % y 23 % ×2, todas con
`informalidad_final = 0,3101`). No se borraron por incómodas: se borraron porque
**ya no reproducen**. Se generaron antes de mergear `main`, y las correcciones de
saturación que entraron por los PR #20 y #24 cambiaron el resultado del motor —
hoy la misma configuración (`alza=23`, `seed=42`, `modo=reglas`) da 0,2406, no
0,3101. Dejar en el archivo de evidencia números que el código actual no vuelve a
producir es peor que no tenerlos. Quedan acá anotados para que el cambio sea
rastreable, no silencioso.

De paso, eso corrige el diagnóstico del PR #25: **en `modo=reglas` el slider ya
no está saturado.** El PR reportaba 31,010 % de informalidad idéntica en 5 %,
13,5 % y 23 %; el barrido de arriba se mueve 7 puntos entre 0 % y 23 %. Lo
arreglaron las correcciones de `behavior/`, no `web/`.

## Lo que este histórico NO tiene

**Corridas en `modo=llm`.** Las 5 son de la ablación determinista, que es el modo
que corre sin credenciales. Sembrarlo en modo LLM —que es lo que pidió la review
de R2— necesita `ANTHROPIC_API_KEY`: el caché de `behavior/.cache/` está
gitignorado y no cubre los prompts de después del merge, así que la corrida corta
en la ronda 1 con «sin credenciales y el prompt no está en el caché». Queda
pendiente para quien tenga la key. La tabla de `/laboratorio` rotula el modo de
cada fila, así que lo que hay no se confunde con lo que falta.

## Qué NO se puede responder con esto todavía

El **histograma de tamaños de cascada** (cuántos trabajadores arrastra cada
evento de informalización). No es solo que no se registre: en este modelo la
informalización ocurre a nivel de celda, promediada entre paráfrasis, y la
cascada es indirecta —más evasores bajan `p(sanción)` para todos— no un contagio
de celda a celda. Haría falta que el motor guardara el delta por celda y por
ronda, y sobre todo la **fracción de firmas fuera de regla**, que hoy se calcula
en `behavior/rondas.py` y se descarta. Pedido en
[`docs/VARIABLES-PENDIENTES.md`](../../docs/VARIABLES-PENDIENTES.md) B1 y B3.
