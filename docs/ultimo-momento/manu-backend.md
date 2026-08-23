# MANU · backend — la simulación maqueta que cabe en la demo

> **Pega esto completo en una sesión nueva.** Tus carpetas: `api/`, `behavior/`, `engine/`,
> `scripts/`. **No toques `web/`** — Dani y Juanda están ahí en este momento.
> Trabajas en `main` sin PR: commit pequeño, `git pull --rebase origin main` antes de cada push.
> **60 minutos.** El orden de abajo está por dependencia, no por gusto.

## El problema que resuelves

La demo dura 3 minutos y la corrida en vivo tarda ~5 (antes 23; tú la bajaste en `a4e1429`).
No podemos mostrar caché: reproducir una grabación no demuestra que la máquina funciona.
**Hay que poder correr la simulación de verdad, en vivo, en menos de 60 segundos.**

La aritmética que manda no es cuántos agentes hay: es **cuántas OLAS de llamadas** ocurren.

```
olas = ceil(celdas / paralelismo) × rondas_con_LLM
tiempo ≈ olas × 23,3 s        (23,3 s/llamada = tu medición: 1398 s / 60 olas)
```

Hoy: 31 celdas ÷ 8 × 3 rondas = **12 olas ≈ 4,7 min**. Bajar celdas sin subir el paralelismo
**no baja el tiempo**. Objetivo: **2 olas ≈ 47 s**.

**Configuración elegida:** `cobertura=0.50` (9 celdas, 51,2% del peso) · `paralelismo=9` ·
`RONDAS_TOTALES=3` (2 rondas con LLM) · `trayectorias=2` (ya corren en paralelo).

---

## PASO 0 · Sin esto, la maqueta se corta sola (10 min)

**Medido hoy, con tu propio código:**

```
tope_derivado(0.50, 2) = $0,60   ·   costo real @1,31x reintentos = $0,72   -> CORTA
```

Y corta en **las cuatro** configuraciones posibles de la maqueta (RT 3 o 4 × trayectorias 1 o 2).

**La causa:** `api/servidor.py:141 llamadas_de_la_corrida()` cuenta **una llamada por
celda-ronda**. Pero `MAX_REINTENTOS = 3` y cada veto dispara una llamada nueva. Factor de
reintento medido:

| Corrida | previstas | reales | factor |
|---|---|---|---|
| Tu corrida pagada (cobertura 0,80, 5 tray.) | 465 | **518** | 1,11× |
| Camino LLM desde caché | 93 | 122 | **1,31×** |
| Ablación al 23% | 93 | 219 | 2,35× |

Y `USD_POR_LLAMADA_EN_FRIO = 1.26/94 = 0,0134` está **9-13% bajo**: tu corrida real dio
`7,8731 / 518 = 0,0152`.

**Lo grave no es que se pare la corrida.** `correr_consolidada()` consolida con las trayectorias
que alcanzaron, así que la corrida **termina bien** y publica una banda sobre 1 donde prometió 2.
Un tope mal puesto no se ve como error: se ve como resultado.

**Arreglo:**
1. `USD_POR_LLAMADA_EN_FRIO` → `0.0152` (tu medición, no la de Haiku).
2. Un `FACTOR_REINTENTO = 1.4` (conservador sobre el 1,31× medido) dentro de `tope_derivado()`,
   con comentario `# SUPUESTO:` citando la tabla de arriba.
3. **No toques `llamadas_de_la_corrida()`**: el evento `inicio` publica `llamadas_previstas` y esa
   cifra debe seguir siendo el piso exacto, no una estimación.

**Verifica:** `tope_derivado(0.50, 2)` tiene que quedar ≥ $0,90 y `tope_derivado(0.80, 5)` ≥ $9,00
(tu corrida costó $7,87 contra un tope de $7,79 — se habría cortado a sí misma).

---

## PASO 1 · `paralelismo` como perilla, y la maqueta (20 min)

**Hoy `paralelismo` no existe para la API:** `grep -n paralelismo api/servidor.py` → 0 resultados.
Se queda en el default `8` de `behavior/rondas.py:220`. Con 9 celdas y paralelismo 8 son **2 olas
por ronda**, no 1, y la maqueta no cabe.

Dos formas, elige la que menos toque:

- **A (mínima):** en `api/servidor.py`, al llamar a `correr_consolidada`, pasar
  `paralelismo=len(cabeza)` acotado a un techo (`min(len(celdas), 12)`). Una línea, ningún
  parámetro público nuevo.
- **B:** exponer `paralelismo` como `Query(...)`. Más flexible, más superficie.

**Recomiendo A.** El techo importa: 31 conexiones simultáneas contra el proveedor no está probado
y el rate limit de la cuenta es desconocido. Con 9 celdas nunca pasas de 9.

**Después, el modo maqueta.** No dupliques el motor — es la misma `correr()` con otros parámetros:

- `RONDAS_TOTALES` es constante de módulo (`api/servidor.py:59`). La maqueta necesita **3**.
  Hazlo un parámetro de la corrida con default 4, o un `Query(rondas=...)`. **Que la elección
  viaje en el evento `inicio`**, para que la pantalla pueda decir «2 rondas, no 3».
- `cobertura=0.50` y `trayectorias=2` ya son perillas: **no hay que tocar nada**, solo llamarlas.

**Verifica sin gastar un peso:**
```bash
.venv/bin/python -m uvicorn api.servidor:app --port 8000 &
time curl -sN "http://localhost:8000/simulaciones/flujo?aumento_pct=23&cobertura=0.50&trayectorias=2&rondas=3&modo=reglas" | grep -c "^event:"
```
Tiene que cerrar con `event: fin`. En `modo=reglas` cuesta $0 y tarda milisegundos: lo que estás
verificando es que la orquestación no se rompió, no el tiempo.

---

## PASO 2 · La corrida real de verificación (10 min, ~$0,70) — PIDE OK ANTES

**No la lances sin que Dani o Juanda digan que sí.** Cuesta plata.

```bash
set -a && source .env && set +a   # el .env dice ANTHROPIC_KEY y el SDK lee ANTHROPIC_API_KEY
time curl -sN "http://localhost:8000/simulaciones/flujo?aumento_pct=23&cobertura=0.50&trayectorias=2&rondas=3&modo=llm"
```

**Usa un `aumento_pct` que NO esté cacheado** (23 sí lo está). Si sale de caché no probaste nada.
Prueba con **17** o **28**.

Anota y reporta: segundos totales, `llamadas_api`, `gasto_usd`, `cache_aciertos`,
`trayectorias_efectivas` y `banda_tipo` del evento `fin`. Si `trayectorias_efectivas` < 2, el
tope volvió a cortar y el paso 0 quedó corto.

> ⚠️ **Lo que va a cambiar y hay que decirlo:** con 9 celdas en vez de 31 **el resultado se
> mueve**. La respuesta a la política es escalonada (medido: +3,25 pp idéntico en 5/10/12%,
> +6,07 pp idéntico en 23/30%), así que cambiar qué celdas deciden puede saltar de escalón
> entero. **La maqueta no es «el simulador más pequeño»: es otra corrida.** Rotúlala en el evento
> `inicio` con algo que la pantalla pueda mostrar (`perfil: "maqueta"` / `"completo"`) y dile a
> Dani qué campo es.

---

## PASO 3 · Si sobra tiempo, en este orden

1. **`make reproduce` (2 líneas, $0).** Corrido hoy: **exit 1**. `scripts/reproduce.py:74` llama a
   `correr()` **sin `cobertura_llm`**, o sea manda 81 celdas a una caché que tiene 31. Cobertura
   medida: **6,3%** contra 85,9% si se le pasa `cobertura_llm=0.80`. Pásaselo y envuelve la
   construcción del cliente para caer a la ablación si la caché no cubre.
2. **Timeout del SDK (2 min, $0).** `behavior/cliente.py:105` no pasa `timeout` ni `max_retries`:
   hereda **600 s de read timeout y 2 reintentos**. Una llamada colgada retiene un worker diez
   minutos. `timeout=60.0, max_retries=1`.
3. **La cifra de sanción (20 min, aditivo).** `prob_fiscalizacion` publica **62,94%** y el riesgo
   de una firma que de verdad evade es **0,99%**. La misma `p`, cuatro denominadores:

   | ponderación | valor |
   |---|---|
   | por trabajadores, todas las celdas (**la publicada**) | **62,94%** |
   | por firmas | 4,72% |
   | **por firmas evasoras** (el riesgo del que evade) | **0,99%** |
   | fórmula de la ADR 0007 sobre el total | 1,69% |

   18 de 81 celdas están clavadas en `p = 100%`: tienen el **51,8% del peso** y el **0,03% de los
   evasores**. Como medio peso está clavado en el techo, **la cascada no puede verse en el número
   que la debería mostrar** (medida con `congelar_prob_fiscalizacion`: aporta **0,000 pp**).
   **Emite `prob_fiscalizacion_evasores` AL LADO. No cambies el campo viejo** — mover una cifra
   publicada a esta hora rompe la pantalla de dos personas.

**No hagas** (mueven todos los agregados y queman las 518 respuestas pagadas): costear
`subir_precios` en el veto, cambiar de modelo, tocar `MAX_REINTENTOS`, tocar el esquema de salida.

## Antes de decir que terminaste

```bash
.venv/bin/python -m pytest engine/ api/ tests/ -q     # hoy: 104 passed
git diff --stat
```
