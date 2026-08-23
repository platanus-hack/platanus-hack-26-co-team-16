# Auditoría técnica — 2026-08-23 04:02 · alcance eje-A-ejecucion

> Informe del agente `juez-tecnico`. Autocrítica interna del equipo, no una evaluación externa.
> **Alcance:** Eje A del reparto a tres ejes — ¿la simulación que corre HOY hace lo que la espina dice?
> Camino de datos completo: `web/` → `api/servidor.py` → `behavior/rondas.py` → `engine/veto.py` → vuelta.
> **Commit:** `9218dc3` · **Rama:** `main` (el prompt del reparto pedía `9cbd6f2`; el árbol de código es idéntico,
> la diferencia son 486 líneas de documentación en `docs/vet/revision-3ejes/`)
> **Comandos ejecutados:** `make run` (exit 0, imprime PENDIENTE) · `make test` (88 passed) · `pytest api/` (13 passed)
> · `make validate` (**exit 1**) · `make reproduce` ×2 + `diff` (idéntico) · `python3 -m behavior.higiene` (7/7)
> · `behavior.capa.renderizar` + `higiene.verificar` sobre las 81 celdas (0 contaminadas)
> · `correr(..., n_parafrasis=2)` y `parafrasis_por_peso=True` · conteo de modelos en `behavior/.cache` (503/503 Haiku)
> · `llamadas_de_la_corrida(0.80, 5)` = 465 · `curl` SSE contra `https://enjambre-web.onrender.com` en `modo=reglas`
> · `git diff --stat main origin/rol/integracion-deploy`.
> **Fallaron:** `scripts/humo_deploy.py` → "FALLO · ni /api/poblacion ni /poblacion respondieron 200" (causa real:
> `SSL: CERTIFICATE_VERIFY_FAILED` en el python3 del sistema; `curl` a la misma URL devuelve 200). `make validate` → exit 1.
> **Ninguno llamó al proveedor de LLM. Costo de esta auditoría: USD 0.**
> **Segunda opinión:** NO DISPONIBLE.
> **Veredicto:** el link público y `main` son dos simuladores distintos, y el único artefacto reproducible de `main`
> muestra 63% de agentes sin ninguna opción factible.

**Delta contra el informe previo** (`2026-08-22-1238-repo.md`, commit `158f689`): se cerró casi todo lo que señalé.
`engine/` ya tiene código (5 módulos, 88 tests pasan), `requirements.txt` existe, `contracts/` tiene consumidor,
`behavior/rondas.py` importa `engine/`, la fórmula prohibida `min(1, C/E)` ya no está, `n_parafrasis>=2` ya no revienta.
**Sigue igual, tercera auditoría consecutiva:** el `seed` no siembra nada (ahora está *declarado* en
`api/servidor.py:80`, que es honestidad, no arreglo), y `behavior/cache-demo.json` sigue sin existir, así que el
nivel 2 de la ADR 0009 sigue sin ser alcanzable por un tercero.

---

## 1 · MENTIRAS

> Ordenadas por qué tan rápido las encuentra un juez con un agente de código.

### M1 · El link que va a abrir el jurado NO corre el código de `main` [VERIFICADO]

**En cristiano:** hay dos simuladores. Uno vive en `main` y otro está en internet. Dan números distintos, y el que
el jurado va a ver es el viejo.

- `render.yaml:34` y `render.yaml:63`: los **dos** servicios dicen `branch: rol/integracion-deploy`.
  El comentario de `render.yaml:22-24` lo advierte: *"OJO al mergear a main: `branch:` de abajo apunta a la rama de
  trabajo. Cuando esto entre a main hay que cambiar los dos a `main`"*. Entró a main. No se cambiaron.
- `git diff --stat main origin/rol/integracion-deploy -- engine/ behavior/ api/ data/ scripts/ contracts/`
  → **24 archivos, 2.089 líneas de diferencia**. En la rama desplegada **no existen** `api/trayectorias.py`
  (las 5 trayectorias y la banda honesta), `engine/arquetipos.py`, `data/calibracion_visibilidad.json`
  ni `scripts/calibrar_visibilidad.py`. `data/momentos.json` difiere.
- Medido contra el deploy vivo, `modo=reglas`, aumento 23%, seed 42:
  `curl -sN "https://enjambre-web.onrender.com/api/simulaciones/flujo?aumento_pct=23&seed=42&modo=reglas"`
  → ronda 0: `tasa_informalidad = 0.3057`, `prob_fiscalizacion = 0.0169`.
- La misma corrida en `main` (`make reproduce`) → ronda 0: `18.0%` y `62.94%`.

**Consecuencia:** `p(sanción)` sale **37 veces más alta** en `main` que en el deploy. Un juez que clone el repo y corra
`make reproduce` obtiene una simulación que no se parece a la que acaba de ver en pantalla, y no hay ni una línea que
explique por qué. `docs/vet/`, `DEFECTOS.md` y este informe describen `main`; la demo muestra otra cosa.

### M2 · `make run` no corre nada, y es el comando que `AGENTS.md` pone como prueba del determinismo [VERIFICADO]

**En cristiano:** el README dice "corre esto dos veces y vas a ver que da igual". Eso que dice que corras no existe.

- `AGENTS.md`, sección *Cómo verificarlo tú mismo*: *"Determinismo: mismo seed, mismo resultado. Verificable
  corriendo `make run` dos veces."*
- `make run` → `PENDIENTE · make run / Falta: scripts/run_simulacion.py`. Exit 0. `ls scripts/run_simulacion.py` → no existe.
- El propio validador lo confirma: `make validate` → `[BLOQUEADO] G1 reproducibilidad: 2 bloqueos: falta
  scripts/run_simulacion.py para comparar dos corridas completas; falta el artefacto canónico de salida y el
  manifiesto de caché`. **`make validate` sale con exit code 1.**
- 3 de los 4 candados salen BLOQUEADOS (G1, G2, G3).

**Consecuencia:** los dos primeros comandos que un juez teclea son `make run` (no hace nada) y `make validate`
(termina en error). El número del backtest sí se imprime, pero después de dos comandos que fallaron.

### M3 · El `seed` es una etiqueta, no una semilla [VERIFICADO]

**En cristiano:** la perilla de la semilla no está conectada a nada. Muévela y el resultado es el mismo.

- `api/servidor.py:80`: `SEED_EFECTO = "etiqueta"  # "etiqueta" | "trayectoria"`.
- `api/servidor.py:228-231`, en la descripción del parámetro público: *"HOY NO CAMBIA NINGUNA DECISIÓN: nada del
  bucle de rondas sortea."*
- `api/servidor.py:68-70`, medido por el propio equipo: *"`modo=reglas`, seed 42 contra seed 99, las 4 rondas
  comparadas campo por campo → trayectorias IDÉNTICAS"*.
- `web/enjambre/estado/flujo.ts:35`: el front manda `seed: "42"` **hardcodeado**. La perilla ni siquiera se expone.

**Esto está declarado en el código, y declararlo es lo correcto.** La mentira no es del código: es de `AGENTS.md`,
que pone "mismo seed, mismo resultado" como la primera restricción no-negociable. Hoy es cierto de forma vacía:
mismo seed, distinto seed, cualquier seed → mismo resultado.

### M4 · `make reproduce` reproduce la ablación, no el producto [VERIFICADO]

**En cristiano:** el comando que dice "reproduce el resultado principal" corre una versión sin IA. La tesis del
proyecto es "la IA propone y la aritmética manda". Ahí no hay IA.

- `scripts/reproduce.py:64-73`: si no existe `behavior/cache-demo.json`, cae a `ClienteReglas()` (la ablación).
- `ls behavior/cache-demo.json` → **no existe**. `.gitignore:30` ya tiene el `!` que lo permitiría; el archivo nunca se creó.
- Salida real: `modo: ABLACIÓN (reglas fijas, sin API)`.
- Determinismo verificado: dos corridas seguidas, `diff` → **idénticas**. Eso sí se sostiene, y es lo único de esta lista que se sostiene.

**Consecuencia:** el único artefacto que un tercero sin API key puede reproducir es el que **no ejercita la mitad
LLM del argumento**. La ADR 0009 lo llama nivel 3 y es honesto; el problema es que `make reproduce` lo presenta
como "el resultado principal".

### M5 · Las rondas 2 y 3 no aportan un solo número nuevo [VERIFICADO]

**En cristiano:** el simulador dice que juega 4 rondas. En la práctica juega una y repite la foto tres veces.

Corrida real, `main`, ablación, seed 42, alza 23%:

| ronda | informalidad | p(sanción) | empleo | fallback | sin salida |
|---|---|---|---|---|---|
| 0 | 18.00% | 62.94% | 100.0% | 0.0% | 0.0% |
| 1 | **24.06%** | 62.94% | 100.0% | 69.1% | 63.0% |
| 2 | **24.06%** | 61.98% | 100.0% | 69.1% | 63.0% |
| 3 | **24.06%** | 61.98% | 100.0% | 69.1% | 63.0% |

Idénticas a 4 decimales en informalidad, fallback y sin_salida. El empleo **nunca se mueve**: 100,0% en las cuatro rondas.
La cascada, que es el mecanismo del modelo, mueve `p(sanción)` **0,96 pp una sola vez** y se congela.

**Consecuencia:** la barra de tiempo del front avanza 4 pasos sobre datos que son el mismo. Cualquiera que compare
la ronda 1 con la 3 en la consola ve tres números iguales.

### M6 · El veto no veta: elimina [VERIFICADO]

**En cristiano:** en la corrida que un juez puede reproducir, 2 de cada 3 empresas no tienen NINGUNA jugada
posible. No es que el árbitro les rechace una idea: es que se quedan sin ideas.

- Medido en `make reproduce` (main, ablación): `fraccion_fallback = 69.1%`, `fraccion_sin_salida = 63.0%`.
- El umbral de alarma del propio equipo es **5%** (`behavior/demo.py:96-97`). Se supera **13,8 veces**.
- `behavior/capa.py:337-340`: cuando ninguna propuesta pasa el veto se llama a `contrato.decision_fallback()`, y si
  ese fallback tampoco encuentra una opción factible, marca `sin_salida`.

**Consecuencia:** la frase del pitch —*"un LLM propone en espacio abierto, un árbitro determinista veta lo que la
aritmética no aguanta"*— en el camino reproducible se convierte en *"el árbitro rechaza todo y el 63% de la
población toma la decisión por defecto"*. El resultado agregado no lo produce el LLM ni el veto: lo produce el fallback.
El vet de anoche vio la punta de esto (S1-14, 7,4% en la corrida de reglas); hoy en `main` va en 63,0%.

### M7 · `parafrasis` es un parámetro público que no hace nada [VERIFICADO]

- `api/servidor.py:96`: `PARAFRASIS_EFECTO = "ninguno"`. La descripción del query param lo declara: *"HOY NO HACE
  NADA en este endpoint"* (`api/servidor.py:247-254`).
- Comprobado: `correr(..., n_parafrasis=2)` corre sin reventar (S1-1 del vet **está cerrado**) y devuelve
  `banda = {p10: 0.2406, p90: 0.2406, degenerada: True, tipo: 'intra_ronda'}`.
- La banda que se publica es la de entre trayectorias (`api/trayectorias.py`), que **no existe en la rama desplegada**.

**Consecuencia:** la regla no-negociable *"todo número sale con banda"* hoy se cumple solo en `main` y solo por el
camino LLM, que nadie ha corrido después del PR #12.

---

## 2 · HUÉRFANOS

Candidatos a salir de la DEMO (no del repo).

| Qué | Evidencia | Por qué es huérfano |
|---|---|---|
| **`engine/seed.py`** (156 líneas + 159 de test) | `api/servidor.py:73`: *"`engine/seed.py` tiene los streams buenos y hoy no lo importa nadie fuera de su propio test"* | El módulo que le da nombre a la restricción no-negociable #1 no tiene un solo consumidor en el camino de datos. [VERIFICADO] |
| **`parafrasis_por_peso=True`** | `correr(..., parafrasis_por_peso=True)` → `ValueError: se pidieron 9 paráfrasis y solo hay 5 en behavior/prompts` | Bandera de desarrollo que revienta seguro. S1-2 del vet: sigue abierto. [VERIFICADO] |
| **Familias `renegociar` y `otra`** | `grep -n "renegociar\|== \"otra\"" behavior/rondas.py` → **0 resultados** en la agregación. Solo `subir_precios` (`:787`), `empleados_a_despedir` (`:493`), `aumento_precios_pct` (`:789`) y `jornada_resultante` mueven campos | 2 de las 8 familias de `behavior/contrato.py:244-253` son etiquetas puras: el modelo las propone, la pantalla las muestra, ningún número cambia. DEFECTOS.md §1.1 dijo "quedan tres"; contando `absorber` como nulo legítimo, quedan **dos**. [VERIFICADO] |
| **`data/poblacion*.parquet` (3 archivos, 327 KB)** | La grilla sale de `data/empresas.parquet` (`api/servidor.py:172`, `scripts/reproduce.py:80`) | El parquet de población ya no alimenta la corrida. Es insumo de `data/`, no de la demo. [VERIFICADO] |
| **`scripts/humo_deploy.py`** como prueba de vida | Reporta `FALLO · ni .../api/poblacion ni .../poblacion respondieron 200` mientras `curl` a esa misma URL devuelve **200**. Causa real: `SSL: CERTIFICATE_VERIFY_FAILED`, tragado por el `except (HTTPError, URLError, TimeoutError)` de `scripts/humo_deploy.py:51` | Un `make humo` desde una máquina con el python del sistema dice "el deploy está caído" cuando está arriba. Es peor que no tener humo: da un falso negativo justo cuando hay que decidir rápido. [VERIFICADO] |
| **503 entradas de caché** | `behavior/.cache`: 503/503 entradas con `"modelo": "claude-haiku-4-5"`, **cero** con `claude-sonnet-5` (`behavior/cliente.py:34`) | La clave de caché incluye el modelo (`behavior/cache.py:33-40`). 2,0 MB de caché que ya no le pega a nada. [VERIFICADO] |

---

## 3 · FALTANTES

Lo que la espina promete y la capa de ejecución no entrega.

1. **`scripts/run_simulacion.py`.** No existe. Es lo que bloquea G1 (reproducibilidad) y lo que `AGENTS.md` promete
   como prueba del determinismo. [VERIFICADO: `ls`, `make validate`]
2. **`behavior/cache-demo.json`.** No existe. Sin él, el nivel 2 de la ADR 0009 —*mismo seed + misma caché =
   mismo resultado*— no es alcanzable por nadie fuera del equipo, y `make reproduce` cae a reglas fijas.
   `Cache.exportar()` ya está escrito (`behavior/cache.py:96`) y nadie lo ha llamado. [VERIFICADO]
3. **Una corrida LLM medida después del PR #12.** La caché está fría para el modelo actual. `DEFECTOS.md` §2.1 y
   §2.2 —el ruido y el signo, los dos 🔴 que le dan título al documento— siguen **sin remedir**, y ni la ablación
   ni el deploy pueden remedirlos. [VERIFICADO]
4. **Un tope de gasto acumulado.** `behavior/presupuesto.py` corta **por corrida**; `api/servidor.py:303-317`
   deriva un tope nuevo en cada request. No hay contador entre corridas.
   - Medido: `llamadas_de_la_corrida(0.80, 5)` = **465 llamadas**, `tope_derivado` = **USD 7,79**
     (USD 6,23 al costo medido de 0,0134/llamada, `api/servidor.py:128`).
   - `api/servidor.py:161`: `allow_origins=["*"]  # sin auth ni registro: regla no-negociable del repo`.
   - Con la caché fría, **cada clic en "simular" son ~USD 6**. Ocho clics = los USD 50 del corte duro del proyecto.
     El techo por corrida (`TOPE_USD_MAXIMO = 25.0`, `api/servidor.py:138`) no impide el noveno clic. [VERIFICADO]
5. **Visibilidad de `fraccion_fallback` y `sin_salida` en pantalla.** S2-7 del vet sigue abierto: los campos viajan
   en el contrato (`api/serializar.py`) y ningún panel los lee. Con 63% de sin_salida, es el número que decide si
   la demo es honesta. [VERIFICADO por grep en `web/enjambre/componentes/`]

**Lo que sí aguanta y no hay que tocar** (una línea, sin elogio): el determinismo del camino ablación es real
(`make reproduce` ×2 → `diff` vacío); la higiene es fail-closed de verdad y corre en caliente
(`behavior/cliente.py:130-131`), y verificada sobre los 81 prompts **renderizados con datos reales** dio
**0/81 contaminados**; 101 tests pasan (88 en `engine/`+`tests/`, 13 en `api/`).
[SOSPECHA, no verificable sin gastar]: `higiene.py` filtra términos, no magnitudes. El prompt renderizado dice
`Ingreso mensual por trabajador antes del cambio: 2.500.000 u` + `sube 23%` + `Sector: adm_publica_edu_salud`.
La unidad está anonimizada; el orden de magnitud y la separación de miles no. Un modelo puede reconocer el
escenario sin que la lista negra dispare.

---

## 4 · LOS 3 ARREGLOS

### A1 · Poner `main` en el deploy, o declarar cuál rama ES la demo

- **Carpeta dueña:** `render.yaml` + dashboard de Render → **Juanda (R5)**
- **Minutos:** 15 (editar dos líneas de `render.yaml` y esperar el rebuild) — pero **ojo**: la rama desplegada
  no tiene `api/trayectorias.py`, así que apuntar a `main` cambia la corrida que se ve. Hay que mirar la pantalla
  después del deploy, no solo el exit code.
- **Cómo se verifica:** `curl -sN "<URL>/api/simulaciones/flujo?aumento_pct=23&seed=42&modo=reglas" | head -3`
  y comparar `tasa_informalidad` y `prob_fiscalizacion` de la ronda 0 contra `make reproduce` local.
  Hoy: 0.3057 / 0.0169 (deploy) contra 0.1799 / 0.6294 (main). Queda listo cuando coinciden.
- **SI NO LO ARREGLAMOS:** el juez abre el link, le gusta, clona el repo, corre `make reproduce` y le salen otros
  números. En ese momento deja de creerle a todo lo demás, incluido el 37,37 pp, que es nuestro mejor activo.
  **Alternativa barata si no da tiempo:** una línea en `README.md` diciendo qué commit está desplegado y por qué
  difiere. Un límite declarado no es un hallazgo del jurado.

### A2 · Que `make run` corra, y que `make reproduce` diga qué está reproduciendo

- **Carpeta dueña:** `scripts/`, `Makefile` → **Juanda (R5)**; el `cache-demo.json` lo exporta **Nico (R3)** desde `behavior/`
- **Minutos:** 40 (25 el script + 15 el export de caché, que ya tiene función escrita: `behavior/cache.py:96`)
- **Cómo se verifica:** `make run > a.txt && make run > b.txt && diff a.txt b.txt` sale vacío **y** el encabezado
  imprime `seed`, `manifiesto de caché` y `modo (llm|reglas)`. `make validate` deja de listar G1 como bloqueado.
- **SI NO LO ARREGLAMOS:** los dos primeros comandos del README fallan delante del juez. Uno imprime "PENDIENTE"
  y el otro termina en error. No importa lo que diga el resto del repo: ya perdimos el beneficio de la duda.

### A3 · Cap de gasto acumulado + caché caliente del escenario demo

- **Carpeta dueña:** `api/` → **Manuel (R2)** el contador entre corridas; `behavior/` → **Nico (R3)** el calentado
- **Minutos:** 30 (un contador de módulo en `api/servidor.py` junto a `_ocupado`, que ya es un candado en memoria
  del proceso y `render.yaml:39-41` documenta que hay una sola instancia; + una corrida de calentado que **sí gasta ~USD 6**)
- **Cómo se verifica:** el evento `fin` del SSE trae `gastado_acumulado_usd`; al pasar el tope el endpoint responde
  con un mensaje explícito ("presupuesto de la demo agotado") en vez de un stack trace, y el front lo pinta distinto
  de un resultado. Y: `python3 -m behavior.cache` muestra entradas con `claude-sonnet-5` (hoy: 0 de 503).
- **SI NO LO ARREGLAMOS:** dos cosas. Primera, el juez hace clic, espera **minutos** (`render.yaml:10` mide 166 s
  para UNA trayectoria; la corrida por defecto son 5) y no sabe si se colgó. Segunda, el noveno clic del día se
  come los USD 50 y a partir de ahí la demo pública muestra un error de presupuesto a todo el que entre.

---

## 5 · LA PREGUNTA QUE NOS HUNDE

> **"Muéstrame ahora, en el link, una corrida en modo LLM con la banda de 5 trayectorias.
> ¿Cuánto tardó, cuánto costó, y qué fracción de tus agentes se quedó sin ninguna opción factible?"**

**Por qué duele:** es la única pregunta que ejercita la espina completa de una vez —el LLM propone, el veto manda,
la banda mide la incertidumbre— y hoy no hay una sola persona en el equipo que pueda contestarla con un número medido.

Lo que sabemos, y es lo que hace que la pregunta sea letal:

- La rama desplegada **no tiene `api/trayectorias.py`**, así que en el link esa corrida no existe.
- La caché está fría para `claude-sonnet-5` (0 de 503 entradas), así que en `main` esa corrida cuesta
  **465 llamadas · ~USD 6,23** y no está medida en tiempo.
- La única corrida reproducible que sí tenemos —la ablación— responde a la tercera parte de la pregunta con
  **63,0% sin salida**, que es 13 veces el umbral de alarma que el propio equipo escribió.

No la desactiva un argumento. La desactiva **una corrida LLM medida, guardada como `cache-demo.json` y desplegada**,
con su tiempo, su costo y su `fraccion_sin_salida` impresos en pantalla. Es el mismo gasto que ya está presupuestado
y hoy nadie lo ha hecho después del PR #12.
