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

## Qué NO se puede responder con esto todavía

El **histograma de tamaños de cascada** (cuántos trabajadores arrastra cada
evento de informalización). No es solo que no se registre: en este modelo la
informalización ocurre a nivel de celda, promediada entre paráfrasis, y la
cascada es indirecta —más evasores bajan `p(sanción)` para todos— no un contagio
de celda a celda. Haría falta que el motor guardara el delta por celda y por
ronda, y sobre todo la **fracción de firmas fuera de regla**, que hoy se calcula
en `behavior/rondas.py` y se descarta. Pedido en
[`docs/VARIABLES-PENDIENTES.md`](../../docs/VARIABLES-PENDIENTES.md) B1 y B3.
