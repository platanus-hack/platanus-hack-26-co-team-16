# ADR 0009 — La frontera del determinismo con un LLM en el bucle

**Estado:** aceptado (R2), con una obligación para `behavior/` (R3) · **Fecha:** 2026-08-22 · **Fuente:** hueco H7

## Contexto

`AGENTS.md` promete, en la portada del repo: **"mismo seed, mismo resultado. Verificable
corriendo `make run` dos veces."**

El motor sí es determinista. La capa LLM no lo es: un modelo generativo puede devolver algo
distinto ante el mismo prompt. Si un revisor corre `make run` dos veces y obtiene números
distintos, la promesa más visible del repo queda desmentida en treinta segundos, y con ella
la credibilidad del resto.

El repo ya intuye el problema —el esqueleto de `ARCHITECTURE.md` pregunta "qué NO garantiza
(la capa LLM cacheada)"— pero nadie escribió la respuesta.

## Decisión

**La afirmación pasa a ser precisa, y se corrige en el texto del repo:**

> **Mismo seed + misma caché de decisiones + mismas versiones = mismo resultado.**

Tres niveles, declarados por separado:

| Nivel | Qué garantiza | Cómo se verifica |
|---|---|---|
| **1 · Motor puro** | Dado un conjunto de decisiones, `engine/` es **completamente determinista**. Toda aleatoriedad pasa por un `numpy.random.Generator` sembrado, con un sub-stream por ronda vía `SeedSequence.spawn()` | Test unitario: dos corridas del motor con las mismas decisiones dan resultados idénticos |
| **2 · Corrida completa con caché** | Con la caché de `behavior/` presente, la corrida entera es reproducible: el LLM no se vuelve a llamar | `make run` dos veces sobre la misma caché |
| **3 · Ablación (sin LLM)** | La corrida con reglas fijas es determinista **sin depender de nada externo**. Es el candado 4 de validación y además la garantía más fuerte que podemos ofrecerle a un tercero | `make validate` en una máquina limpia |

**Obligación que esto crea para `behavior/` (R3):** la caché deja de ser un archivo temporal
y pasa a ser un **artefacto versionado** que se entrega con el repo, con un hash de manifiesto
que la corrida imprime. Sin eso, el nivel 2 no existe para nadie que no seamos nosotros.

**Límite que se declara sin que lo pregunten:** el determinismo es *misma máquina, mismas
versiones*. Operaciones vectorizadas en punto flotante pueden diferir en el último bit entre
versiones de BLAS o arquitecturas distintas. Prometer "bit a bit en cualquier computador"
sería falso y es innecesario: las conclusiones no dependen del último bit.

## Alternativas descartadas

| Alternativa | Por qué no |
|---|---|
| **Prometer determinismo total con LLM en vivo** | Es falso y se desmiente corriendo el comando dos veces. El peor tipo de sobreventa: la que el propio repo refuta. |
| **Temperatura 0 y decir que basta** | Reduce la variación pero no la elimina, y no sobrevive a un cambio de versión del modelo del lado del proveedor. Además `PLAN.md` §5 ya decidió que la banda de error se construye sobre **paráfrasis del prompt**, no sobre temperatura. |
| **Quitar la promesa del README** | El determinismo es una de las cinco cosas que el insumo de Manuel §12 pidió que sobrevivieran, y es barato. Se precisa, no se abandona. |
| **Congelar las decisiones del LLM en un archivo fijo y no volver a llamarlo** | Es la caché, pero sin honestidad sobre su origen. Mejor la caché explícita y versionada, que además permite regenerarla. |

## Consecuencias

- **`AGENTS.md` y `README.md` (dueño Juanda) tienen una frase que hay que precisar.** Va al
  standup: no es un error de Juanda, es un hueco que nadie había cerrado.
- `make run` imprime el hash de la caché y el seed. Dos corridas comparables se reconocen a simple vista.
- La ablación gana importancia: pasa de ser solo el candado 4 a ser también **la
  demostración de reproducibilidad más fuerte** que le podemos dar a un tercero.
