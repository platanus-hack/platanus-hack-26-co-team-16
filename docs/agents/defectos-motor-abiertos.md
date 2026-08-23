# Defectos abiertos del motor y la agregación

> **Origen.** Esta tabla venía dentro de `docs/ultimo-momento/`, una carpeta de coordinación de la
> última hora del hackathon que se eliminó el 23-ago (ver *Por qué se movió* al final). Los
> defectos son un activo del proyecto y merecen un archivo propio, con dueño y estado, en vez de
> vivir dentro de un reparto de tareas caducado.
>
> **Todos están medidos con un comando, no inferidos leyendo.** Un defecto listado acá no es una
> decisión: es un hallazgo con fecha. Lo que se confirme y cambie el modelo se gradúa a un ADR o al
> registro de supuestos de `engine/MODELO.md`.

## Estado al 23-ago

| # | Qué | Evidencia | Estado |
|---|---|---|---|
| **H-1** | `make reproduce` reventaba con exit 1: no pasaba `cobertura_llm` y mandaba 81 celdas a una caché de 31 | corrido: `exit 1` | ✅ **cerrado**. `scripts/reproduce.py` pasa `cobertura_llm=0.80` y, si la caché no cubre, **repite con la ablación y lo dice en voz alta** en vez de morir. Sale 0 |
| **H-7** | El tope de gasto no cuenta los reintentos del veto | `tope_derivado(0.50, 2)` = **$0,60** y el costo real @1,31× es **$0,72**: **corta en las 4 configuraciones** de la maqueta | ❌ abierto · Manu (R2) |
| **H-2** | `prob_fiscalizacion` publica **62,94%**; el riesgo real del evasor es **0,99%** | `behavior/rondas.py:356`. 18 de 81 celdas clavadas en p=100%, con 51,8% del peso y 0,03% de los evasores | ❌ abierto · **es la cifra que la UI muestra** |
| **H-5** | `fallback`/`sin_salida` cuentan decisiones, no población | `behavior/rondas.py:546`. Publicado **0,6296** vs ponderado **0,7327** (**+10,3 pp**) | ❌ abierto · Manu / Nico |
| **H-10** | El SDK va sin `timeout` ni `max_retries`, así que hereda 600 s | `behavior/cliente.py:105` | ❌ abierto · Manu (R2) |
| **H-4** | `subir_precios` y `renegociar` **no mueven ningún número**, y son las únicas dos que el veto **nunca** rechaza. **El 81,5% del peso poblacional termina en decisiones inertes** | 27% de las decisiones | ❌ abierto · *declarar, no arreglar* |
| **H-3** | **`alfa = 1,875` es un parámetro libre ajustado.** Con `alfa=0` el placebo se mueve **+77,68 pp** | ver abajo | 🟡 **investigado el 23-ago** |
| **O1** | `paralelismo` fijo en `8` (`behavior/rondas.py:220`) y no es perilla de la API | `grep -n paralelismo api/servidor.py` → 0 resultados | ❌ abierto · cosmético |

## H-3, resuelto en parte: α está calibrado, pero no contra lo que se temía

La sospecha era circularidad: *"si α está calibrado contra la informalidad que el modelo debe
reproducir, el argumento se muerde la cola"* (pendiente #4 de la auditoría final).

**Se corrió** `python scripts/calibrar_visibilidad.py` y la respuesta está en
`scripts/calibrar_visibilidad.py:89-103`: lo que se minimiza es **el placebo**, no la brecha.

```python
# El objetivo que se MINIMIZA es el placebo, no el ajuste por tamano.
error_total = abs(rondas[-1].tasa_informalidad - objetivo_agregado) * 100.0
```

α se elige para que el modelo sea **punto fijo cuando la política no cambia nada** (alza = 0). Esa
es la condición de identificación estándar: el parámetro no ve la brecha ni la cascada. **No es
circular en el sentido acusado.**

Lo que sí queda declarado, y es serio: **el ajuste base falla por tamaño de firma.** El modelo
produce **cero informalidad en pyme y en grande**, y toda la suya vive en micro (+7,49 pp). El
candado **G3** de `VALIDATION.md` exige ±2 pp por tamaño: no se cumple en dos de los tres.

Detalle y tabla completa: [`../evidencia/2026-08-23-E1-E2-E3.md`](../evidencia/2026-08-23-E1-E2-E3.md) §E3.

## Dos defectos nuevos, encontrados corriendo los experimentos

1. 🔴 **`scripts/barrido_politicas.py` revienta en Windows** al imprimir el informe final:
   `UnicodeEncodeError` con la `Δ` de la columna `Δprecios`. El barrido ya corrió y el JSON ya se
   escribió, así que **falla después de trabajar**. Se sortea con `PYTHONIOENCODING=utf-8`.
2. **`--salida` se trata como directorio** en el mismo script: pasar `--salida ruta/archivo.json`
   crea un *directorio* con ese nombre.
3. **Correr `scripts/calibrar_visibilidad.py` destruye documentación.**
   `data/calibracion_visibilidad.json` tiene tres campos escritos a mano
   (`objetivo_minimizado`, `por_que_ese_objetivo`, `piso_de_granularidad`) que el script no
   regenera. Además su docstring (`:1-6`) describe el objetivo **viejo** (MAE por tamaño) y no el
   que el código minimiza.

## Por qué se movió este contenido

`docs/ultimo-momento/` se eliminó el 23-ago. Contenía dos cosas muy distintas:

- **Un activo** — esta tabla de defectos medidos, que se conserva acá.
- **Un reparto de tareas de 60 minutos que ya pasó**, y que incluía instrucciones para quitar de la
  interfaz el bloque del backtest y la sección *"dónde no hay que creerle"*
  (*"suena a confesión. Renómbralo"*).

**Esas instrucciones nunca se ejecutaron** —`Menu.tsx` sigue publicando el error de 37,37 pp y la
sección sigue viva— pero quedaron commiteadas. Un repo que declara *"Documentar sí, manipular
jamás"* (`AGENTS.md`) y publica su backtest fallido no puede a la vez versionar el plan de
esconderlo: la contradicción hace más daño que el resultado negativo, y cualquiera la encuentra con
un `git log`. Se eliminó el plan y se conservó la evidencia.
