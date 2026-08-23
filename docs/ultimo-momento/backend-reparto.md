# Backend · el reparto de lo que queda — 2 agentes en paralelo

> **Escrito:** 23-ago, tras cerrar 9 pendientes de backend en la rama `backend/ultimo-momento`.
> **Base:** todo lo de abajo cuelga del commit de esa rama. **Ninguno de los dos parte de `main`.**
>
> Los dos carriles **no comparten un solo archivo**. Esa es la única protección real cuando dos
> agentes trabajan a la vez: si nadie abre el archivo del otro, no hay conflicto que resolver.

## Qué YA se cerró (no lo vuelvan a tocar)

Verificado con el comando pegado al lado, no con el reporte del agente.

| # | Qué | Dónde | Verificación |
|---|---|---|---|
| 1 | Costo por llamada real + `FACTOR_REINTENTO` (el tope cortaba corridas legítimas) | `api/servidor.py` | `tope_derivado(0.50,2,3)` = $1,75 contra $0,9742 gastados |
| 2 | `paralelismo` es perilla derivada; `rondas` es `Query`; `perfil` viaja en `inicio` | `api/servidor.py`, `api/trayectorias.py` | maqueta = 2 olas, completa sigue en paralelismo 8 |
| 3 | `make reproduce` sale **exit 0** y da idéntico dos veces | `scripts/reproduce.py` | `make reproduce` × 2 + `diff` |
| 4 | `timeout=90.0, max_retries=1` en el SDK (heredaba 600 s) | `behavior/cliente.py` | `_construir_api().timeout` |
| 5 | `prob_fiscalizacion_evasores` **al lado** de la vieja | `behavior/rondas.py`, `api/serializar.py` | 62,94% contra 0,99% |
| 6 | **El corte de presupuesto es atómico** (DEFECTOS §3.7) | `behavior/presupuesto.py`, `behavior/cliente.py` | 40 hilos: sobregiro $0,58 → **$0,00** |
| 7 | `fraccion_fallback/sin_salida_ponderada` por población | `behavior/rondas.py`, `api/serializar.py` | 62,96% (decisiones) contra **73,27%** (población) |
| 8 | `# SUPUESTO:` en `cobertura=0.8` (es corte de presupuesto, no propiedad del modelo) | `api/servidor.py` | `/docs` del endpoint |
| 9 | `humo_deploy` deja de reportar "el deploy no responde" para cualquier fallo | `scripts/humo_deploy.py` | ahora dice `SSLCertVerificationError` cuando el problema es local |

**`api/` está terminado.** No queda nada de backend en esa carpeta: ninguno de los dos carriles la abre.

---

## CARRIL A · Reproducibilidad y herramientas

**Dueño exclusivo de:** `scripts/run_simulacion.py` (nuevo), `scripts/validate.py`, `Makefile`.
**No abre:** `engine/`, `behavior/`, `api/`, `web/`, `data/`, docs raíz.
**Anota en:** `docs/agents/handoff-backend-carril-A.md` (créalo; nadie más escribe ahí).

| # | Qué | Evidencia de que sigue abierto |
|---|---|---|
| **A1** | **`make run` no corre nada.** `scripts/run_simulacion.py` **no existe** y el target imprime `PENDIENTE`. Es el PRIMER comando que teclea un juez, y `AGENTS.md` lo pone como la prueba del determinismo | `make run` → `PENDIENTE · make run` |
| **A2** | **`make validate` sale con exit 1** y 3 de 4 candados salen `BLOQUEADO` (G1, G2, G3). G1 se desbloquea justamente con A1: pide dos corridas completas comparables | `make validate` → `make: *** [validate] Error 1` |
| **A3** | `scripts/validate.py` no tiene `argparse`, así que el `--dry` que el juez científico cita **no existe** | `grep -c argparse scripts/validate.py` → `0` |

**Orden:** A1 primero (A2 depende de él). A3 es el más barato y puede ir de último.

**Lo que el carril A tiene que saber del carril B:** B agrega campos NUEVOS a `Ronda`
(aditivos, nunca quita ni renombra), así que las importaciones de `behavior/` no se mueven
bajo tus pies. Si algo que importas deja de existir, **para y avisa**: significa que B se salió
de su carril.

---

## CARRIL B · El modelo y sus supuestos

**Dueño exclusivo de:** `engine/fiscalizacion.py`, `behavior/rondas.py`, `behavior/ablacion.py`, `behavior/pruebas.py`.
**No abre:** `scripts/`, `Makefile`, `api/`, `web/`, `data/`, docs raíz.
**Anota en:** `docs/agents/handoff-backend-carril-B.md` (créalo; nadie más escribe ahí).

| # | Qué | Evidencia de que sigue abierto |
|---|---|---|
| **B1** | **¿`alfa = 1,875` es circular?** `scripts/calibrar_visibilidad.py:103` minimiza `\|informalidad final − informalidad observada\|` **con `aumento_pct=0.0`**, o sea contra el PLACEBO. Eso es una condición de identificación, no una circularidad con el backtest (que mide el CAMBIO, no el nivel). **Pero hay que medirlo:** con `alfa=0` el modelo predice 95,67% y el placebo se mueve +77,68 pp, o sea que α tiene un apalancamiento enorme. Barre α y publica cuánto se mueve la predicción del 23%. Si se mueve mucho, α es un parámetro libre que carga el resultado y hay que decirlo en `engine/fiscalizacion.py` | `ELASTICIDAD_VISIBILIDAD = 1.875` sin sensibilidad publicada |
| **B2** | **`tasa_informalidad` se pondera por el peso ORIGINAL de la celda**, no por el empleo que sobrevive, mientras `empleo_relativo` justo debajo sí usa `fraccion_empleada`. Una celda que despide media planta sigue aportando su masa completa. **Medido: 0,00 pp en `modo=reglas`** (el empleo no se mueve) y **~0,4 pp** en el camino LLM. Es limpieza, no urgencia — y el patrón ya está: emitir la ponderada AL LADO, sin tocar la publicada (ver los puntos 5 y 7 de la tabla de arriba) | `behavior/rondas.py`, el bloque de `tasa = min(1.0, ...)` |
| **B3** | **Unidades en `behavior/ablacion.py`**: COP/mes sumado con COP/trimestre. Toca el camino determinista, que es **el que usa el backtest** y el que corre sin API key | señalado por el juez científico, sin verificar en código |

**Orden:** B3 primero (toca el número del backtest), después B1 (mide, no arregla), B2 al final.

**Lo que el carril B tiene que saber del carril A:** A va a crear `scripts/run_simulacion.py`,
que **importa** de `behavior/` y `engine/`. Agrega campos, no los quites ni los renombres.
Si necesitas cambiar una firma pública, **para y avisa** antes de tocarla.

---

## Reglas para los dos

1. **Ramas separadas, las dos colgando de `backend/ultimo-momento`:**
   `git checkout -b backend/carril-a backend/ultimo-momento` (y `backend/carril-b`).
   **Nadie pushea a `main`** y nadie trabaja directo sobre `backend/ultimo-momento`.
2. **Antes de decir que algo se hizo:** `git diff --stat` **y** el comando de verificación pegado
   con su salida. Un reporte sin salida es un reclamo, no evidencia.
3. **La suite tiene que quedar como está hoy:**
   `python3 -m pytest engine/ api/ tests/ -q` → **104 passed** ·
   `PYTHONPATH=. python3 behavior/pruebas.py` → *todas las regresiones pasan*.
4. **Cero datos inventados.** Todo supuesto se marca donde se toma con `# SUPUESTO:` y su fuente.
5. **Campos aditivos, nunca sustitutivos.** `contracts/ronda.json` está congelado: una cifra
   publicada se acompaña, no se reemplaza. Mover una cifra que la pantalla ya consume rompe el
   trabajo de dos personas.
6. **Nada que gaste LLM sin pedir OK.** Los 6 pendientes de arriba cuestan **$0**: todos corren
   por la ablación determinista.

## Lo que NINGUNO de los dos toca, y hay que avisarle a su dueño

- **`DEFECTOS.md` §3.7 dice «🔴 abierto» y ya no lo está** (punto 6 de la tabla). Es doc raíz,
  o sea de Juanda: hay que avisarle, no editarlo.
- **`data/prediccion_modelo.json` sigue siendo anterior al arreglo de denominador**, así que EL
  NÚMERO (37,37 pp) no se reproduce corriendo `main` hoy. Cuesta ~USD 8 y es decisión de equipo.
  Está declarado en `VALIDATION.md`; no es de backend resolverlo solo.
