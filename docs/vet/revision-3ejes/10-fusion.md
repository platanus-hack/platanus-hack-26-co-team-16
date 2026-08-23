# `10-fusion.md` — la lista de corte de la revisión a tres ejes

> **Esqueleto creado el 23-ago 04:29 por Manuel (R2), con el Eje A ya pegado.**
> Este archivo NO es el informe de ningún agente: los tres informes viven en
> `docs/agents/<agente>/` y son la fuente. **Esto es la decisión del equipo** sobre qué se
> arregla antes del congelamiento y qué se dice en voz alta en vez de arreglarse.
>
> Manda sobre el corte de la madrugada. No manda sobre el producto (`docs/PLAN.md`) ni sobre
> la validación (`VALIDATION.md`). Las reglas de fusión están copiadas abajo, así que este
> archivo se puede usar sin volver al [`README.md`](README.md).

## Reloj

| Hito | Hora |
|---|---|
| Congelamiento del repo | **domingo 09:30** |
| Colchón obligatorio | 1 hora |
| **Corte real: nada nuevo empieza después de** | **08:30** |

## Estado de los tres informes

Un eje sin informe no se espera: se marca como **NO ENTREGADO** y la fusión sale con dos.
Un informe tarde vale cero.

| Eje | Agente | Ruta del informe | Estado |
|---|---|---|---|
| **A · Ejecución** | `juez-tecnico` | [`docs/agents/juez-tecnico/2026-08-23-0402-eje-A-ejecucion.md`](../../agents/juez-tecnico/2026-08-23-0402-eje-A-ejecucion.md) | ✅ **ENTREGADO** 04:02 · sin segunda opinión · 4 hallazgos verificados a mano |
| **B · Fundamentación** | `juez-cientifico` | [`docs/agents/juez-cientifico/2026-08-23-0414-eje-B-fundamentacion.md`](../../agents/juez-cientifico/2026-08-23-0414-eje-B-fundamentacion.md) | ✅ **ENTREGADO** 04:14 · con segunda opinión (`codex`/GPT-5, coincide) · medido sobre `9218dc3` |
| **C · Pantalla** | `juez-hackathon` | `docs/agents/juez-hackathon/2026-08-23-HHMM-eje-C-pantalla.md` | ⬜ pendiente |

> ⚠️ **Trampa de nombres en la carpeta C.** `docs/agents/juez-hackathon/` ya tiene un
> `2026-08-23-0009-repo.md` que es de las 00:09 y es modo `repo`, **no** el Eje C. Que el
> informe del Eje C diga `eje-C-pantalla` en el nombre para que a las 8am nadie fusione el
> archivo equivocado.

> ⚠️ **Los tres ejes no midieron el mismo árbol, y la regla del §2 supone que sí.**
> Los `PROMPT-*.txt` fijan `9cbd6f2`, que **quedó viejo** en cuanto se mergeó el PR #29 con el
> propio reparto. El **Eje B corrió sobre `9218dc3`** (el `main` más reciente al momento de
> lanzarlo) y lo dice en su encabezado. **Antes de aplicar "lo que aparece en dos listas va
> primero", anotá acá contra qué commit corrió cada eje** — si A y C usaron el SHA literal del
> prompt, un defecto puede aparecer en una lista y no en otra solo porque el árbol cambió.
> La diferencia `9cbd6f2..9218dc3` es únicamente `docs/vet/revision-3ejes/`, así que **para el
> código no cambia nada**; el riesgo real está en `main` moviéndose durante la madrugada
> (entre que B se lanzó y B se entregó, entraron los PR #30 y #32).

---

## §1 · Los 9 arreglos posibles

Tres por eje, como pide el contrato de salida. Se llena pegando el bloque 4 de cada informe.

| # | Arreglo | Carpeta dueña | Min | Cómo se verifica | SI NO LO ARREGLAMOS |
|---|---|---|---|---|---|
| **A1** | Deploy apunta a `main` (o declarar qué commit está vivo) | Juanda (R5) | 15 | `curl` SSE ronda 0 del deploy == `make reproduce` local | El juez clona, corre, le salen otros números y deja de creer el 37,37 pp |
| **A2** | `make run` que corra + `cache-demo.json` exportado | Juanda (R5) + Nico (R3) | 40 | `make run` ×2 con `diff` vacío; G1 deja de estar bloqueado | Los dos primeros comandos del README fallan delante del jurado |
| **A3** | Cap de gasto acumulado + caché caliente | Manuel (R2) + Nico (R3) | 30 | `fin` trae gasto acumulado; `python3 -m behavior.cache` muestra entradas Sonnet | El juez espera minutos sin saber si se colgó, y el clic nº9 quema los USD 50 |
| **B1** | Rebautizar el mapa: de "quién no puede pagar" a **"carga legal estatutaria por celda"**, con nota al pie de qué lo ordena | Dani (R4) + Juanda (R5) | 20 | `grep -rn "no puede pagar\|quién aprieta" web/` → 0, y la nota al pie existe en la lámina distributiva | Un juez abre `data/construir_empresas.py:70`, ve que las 81 celdas tienen el mismo colchón y pregunta *"¿entonces su mapa solo dice que el informal es informal?"*. Hoy no hay respuesta |
| **B2** | Meter en `VALIDATION.md` el **segundo episodio** (2024→2025, +2,63 pp, dirección opuesta) y la **no-cegera** del pre-registro | Juanda (R5) | 25 | `grep -n "2,63" VALIDATION.md` y `grep -n "no fue ciego" VALIDATION.md` → ≥1 cada uno (hoy dan **0**, verificado) | El jurado los encuentra solo — están en el repo público — y lo que era rigor se lee como cifra escondida. **Es el único hallazgo de B que puede costar el proyecto entero en vez de un punto** |
| **B3** | Quitar la palabra **"cobertura"** del número: pasa a "el observado cae / no cae dentro del rango entre paráfrasis" | Juanda (R5, `scripts/`) + Dani (R4, `web/`) | 15 | `grep -rn "Cobertura" scripts/ web/` → 0 en contexto de banda. **Ojo:** el informe propone `validate.py --dry` y **ese flag no existe** (el script no tiene `argparse`); se verifica leyendo `scripts/validate.py:160-175` | Basta un *"¿cobertura de qué nivel?"* para que la barra de error, que es lo más honesto que tenemos, quede como el número menos defendible de la lámina |
| **C1** | _(pegar del bloque 4 del informe C)_ | | | | |
| **C2** | | | | | |
| **C3** | | | | | |

---

## §2 · Lo que aparece en dos ejes o más — VA PRIMERO

**La regla:** un defecto que dos revisores ven por separado, mirando capas distintas, no es una
opinión. Es estructural. Estos se ordenan arriba de todo, sin importar sus minutos.

Se llena al final, cruzando los bloques MENTIRAS / HUÉRFANOS / FALTANTES de los tres informes.

| Defecto | Ejes que lo vieron | Evidencia de cada uno | Arreglo asociado |
|---|---|---|---|
| **El veto no está produciendo el resultado que la espina promete** | **A + B** | **A · M6:** `fraccion_fallback = 69,1%`, `fraccion_sin_salida = 63,0%` contra el umbral de alarma de 5%. · **B:** **67 de 81 celdas** ya son infactibles en la rama `absorber` a 23% (`engine/veto.py:443-445` sobre `data/empresas.parquet`) — la aritmética de por qué casi todo el mundo cae al fallback | A3 (parcial) + **B1** |
| **Qué pasa en las rondas 2 y 3 — los dos ejes lo describen distinto** | **A + B** | **A · M5:** informalidad 24,06% **idéntica a 4 decimales** en las tres rondas. · **B · FALTANTES 4:** `DEFECTOS.md:157-171` reporta **reversión** entre rondas 2 y 3 en **7 de 9** políticas, y `behavior/rondas.py:798-817` marca `estabilizada` con un umbral de 2 pp sobre **una sola** coordenada | **Ninguno todavía — hay que reconciliar primero** |
| _(pendiente el cruce con C)_ | | | |

> ⚠️ **La segunda fila no es un defecto confirmado, es una contradicción entre dos informes.**
> "No se mueve nada" y "revierte en 7 de 9" no pueden ser ciertas sobre la misma corrida. O miran
> corridas distintas (ablación vs LLM, andamio vs `--real`), o una de las dos está mal. **Se
> resuelve antes de fusionar, no después:** quien fusione pregunta a A y a B con qué comando
> corrió cada uno. Si resulta que la ronda 3 no es un atractor y además la pantalla la anima como
> si lo fuera, es mentira en tres capas y sube al primer lugar de la lista.

**Candidatos que el Eje A ya dejó servidos.** Si B o C tocan lo mismo, suben a la tabla de arriba:

- **La brecha deploy ↔ `main`** (A · M1). Si el Eje C mira `web/` contra el link desplegado, va a
  chocar con esto por su lado.
- **El fallback produce el agregado, no el veto:** `fraccion_fallback = 69,1%`,
  `fraccion_sin_salida = 63,0%` contra el umbral de alarma de 5% del propio equipo (A · M6).
  Toca la espina de frente: *"un LLM propone, un árbitro determinista veta"*. **Este es el que
  hay que buscar en el informe B**, porque si el Eje B lo confirma por el lado de la
  fundamentación, es el hallazgo #1 de toda la revisión.
  - **RESPUESTA DEL EJE B: lo corrobora por el mecanismo, no por la cifra.** B **no midió**
    `fraccion_fallback` (no corrió el motor: su informe es lectura estática más 4 cálculos sobre
    parquet). Lo que sí aporta es **por qué** ese número tiene que salir alto: a 23%, **67 de las
    81 celdas** ya no pueden absorber, porque `sobrecosto/caja = share_formal · factor · a / 0,18`
    y el margen de caja es uniforme. El fallback masivo no es un bug de la capa LLM: es lo que
    la parametrización obliga. **Sube a la tabla del §2.**
- **Las rondas 2 y 3 no mueven nada** (A · M5): informalidad 24,06% idéntica a 4 decimales en
  las tres rondas. Si el Eje C encuentra que la pantalla igual anima tres rondas, es mentira en
  dos capas.
  - **EL EJE B DICE LO CONTRARIO.** Ver la fila 2 del §2: hay que reconciliarlo antes de fusionar.

**Candidatos que el Eje B deja servidos.** Si C toca lo mismo, suben a la tabla de arriba:

- **La cascada afirmada como resultado.** B marcó por `grep` que `CurvaBrecha.tsx`,
  `reporte/Graficas.tsx` y `laboratorio/Graficas.tsx` mencionan cascada, **pero no leyó el texto
  de las leyendas: eso es del Eje C.** La cascada está falsada por el propio backtest y es
  mecanismo, nunca resultado. Si C encuentra que una leyenda la afirma, es mentira en dos capas.
- **La banda de 33,9 pp presentada como si fuera intervalo de confianza.** B verificó que el
  *texto* de `VALIDATION.md:22,88,260-264` la nombra bien ("entre paráfrasis, NO calibrado") y que
  el *cálculo* de `scripts/validate.py:165-171` la trata como si tuviera nivel nominal. **Falta
  saber qué hace la pantalla con ella** — si el front la dibuja como banda de confianza, sube.
- **El mapa distributivo rotulado como predicción.** Si C encuentra en `web/` la frase "quién no
  puede pagar" o equivalente, confirma B1 desde la capa de pantalla.

---

## §3 · El corte

**Regla dura del congelamiento:** lo que no está en "LOS 3 ARREGLOS" de al menos un revisor,
**no se toca**. Sin excepciones y sin "es que son dos minutos". Todo lo demás baja al §4.

### Suma global — lo que pide el `README.md`

| Con los 3 ejes | Minutos |
|---|---|
| Eje A (A1+A2+A3) | 85 |
| Eje B (B1+B2+B3) | **60** |
| Eje C | _pendiente_ |
| **Total** | **145 + C** |

### Suma por dueño — el número que de verdad manda

La suma global engaña: los arreglos los hacen personas distintas **en paralelo**, pero una
persona no puede hacer dos a la vez. El cuello de botella es el dueño más cargado, no el total.

| Dueño | Arreglos que le tocan | Min acumulados |
|---|---|---|
| **Juanda (R5)** | A1, A2, **B2**, **B3** | **95** ← nuevo cuello de botella |
| Nico (R3) | A2, A3 | 70 |
| Dani (R4) | **B1**, **B3** | **35** |
| Manuel (R2) | A3 | 30 |
| Alejo (R1) | — | 0 |

> Añadido operativo de este archivo, no un cambio a la regla del reparto. La regla sigue siendo
> la suma global; esta tabla es el chequeo de realidad de si cabe.

> ⚠️ **Al entrar el Eje B, el cuello de botella se mudó: era Nico (70), ahora es Juanda (95)** —
> y eso es **antes** de que llegue el Eje C, cuyos arreglos casi seguro también caen en `web/`
> (Dani) y en docs raíz (Juanda). **B1 y B3 tienen dueño compartido** y acá se contaron en los
> dos, así que 95 y 35 son cotas superiores: si Dani hace la rotulación de `web/` y Juanda solo
> lo suyo, Juanda baja a ~80. Vale la pena repartirlos explícitamente antes de arrancar.

### Lo que entra

1. _(vacío hasta cortar)_

### Lo que NO entra, y por qué

1. _(vacío hasta cortar)_

---

## §4 · Límites declarados — lo que se dice en voz alta en vez de arreglarse

No es la lista de la vergüenza. Es la lista que **se dice antes de que la pregunten**, que es la
diferencia entre un límite y un hallazgo del jurado.

- _(se llena al cortar, con todo lo que quedó fuera del §3)_

**Ya declarados por el Eje A, fuera de sus 3 arreglos:**

- `api/servidor.py:200-201` cae a corrida en frío **en silencio** cuando falta
  `behavior/cache-demo.json`; `scripts/reproduce.py:70-72` sí lo anuncia. El camino silencioso
  es el que el juez clickea. Dueño: Manuel (R2).
- `engine/seed.py` (315 líneas con test) no tiene un solo consumidor fuera de su propio test.
- Las 503 entradas de caché son **todas Haiku**, cero Sonnet.
- La higiene filtra términos, no magnitudes: `"2.500.000 u"` + 23% pasa el filtro. `[SOSPECHA]`
  del Eje A, sin verificar.

**Ya declarados por el Eje B, fuera de sus 3 arreglos** (ninguno cabe antes de las 08:30; los
cinco se dicen en voz alta):

- **El alza se cobra sobre el 100% de la nómina, gane quien gane.** No existe variable de
  exposición al mínimo (`engine/veto.py:443-445`; 20 columnas en `data/empresas.parquet`). Solo
  **18 de 81** celdas tienen salario mediano ≤ 1,05 SMLMV; el mediano ponderado es **1,52 SMLMV**.
  Más del 80% de la masa recibe un shock que no le corresponde. **Dirección del sesgo:
  sobreestima el daño en celdas de salario alto.** No se arregla en la ventana.
- **El margen de caja es un supuesto uniforme (`0,18`), no un dato observado**
  (`data/construir_empresas.py:70`). Es la razón de fondo de B1.
- **El backtest de 37,37 pp no puntúa el estimando que hoy calcula el motor:**
  `data/prediccion_modelo.json` arranca en 30,6% (todos los ocupados) y el motor cubre empleados
  de firma (`tasa_informalidad_empleados_de_firma = 0,1799`). Además `VALIDATION.md:180-188` ya se
  retracta de que la corrida arranca de GEIH 2026, seis meses **después** del decreto.
- **Ninguna prueba de estabilidad de la dinámica.** La ronda 3 es un corte de calendario, no un
  atractor (`behavior/rondas.py:798-817`). Relacionado con la fila 2 del §2.
- **Huérfanos de la demo:** `sobrecosto_formal_pct`, `auxilio_transporte_cop` y
  `costo_formal_mensual_cop` se calculan bien en `data/construir_empresas.py:128-152` —el auxilio
  de transporte es justo lo que daría heterogeneidad real— y `behavior/arquetipos.py:245-291`
  **no los consume**. También `subir_precios` (1,4% lo elige y el agregado lo bota).

> **Lo que B verificó y NO es hallazgo:** el `+0.15` del front que marcaba el vet **ya está
> cerrado** (`web/enjambre/componentes/enjambre/Personas.tsx:280-282` lo eliminó y dejó escrito
> por qué). El otro `0.15` del repo es un `letterSpacing`. No gastar tiempo ahí.

---

## §5 · Las tres preguntas que nos hunden — el Q&A real

Se contestan **por escrito antes de la demo**. Una pregunta sin respuesta escrita es una pregunta
que se contesta improvisando delante del jurado.

### A · Ejecución

> **"Muéstrame ahora, en el link, una corrida en modo LLM con la banda de 5 trayectorias.
> ¿Cuánto tardó, cuánto costó y qué fracción de tus agentes se quedó sin ninguna opción
> factible?"**

**Respuesta:** _(pendiente de escribir)_

### B · Fundamentación

> **"Ustedes dicen que el nivel falló pero el reparto se sostiene. ¿Qué variable de su modelo
> hace que una empresa aguante el alza y otra no — una que NO sea la informalidad que ya traía
> de la encuesta?"**

**Respuesta:** _(pendiente de escribir — y el Eje B avisa que **hoy no existe**)_

**Con qué hay que escribirla, según B:** no hay una variable así. El margen es `0,18` para las 81
celdas, el salario y el tamaño **se cancelan algebraicamente** en el veto
(`sobrecosto/caja = share_formal · factor · a / 0,18`, `engine/veto.py:443-445`), y lo que queda
correlaciona **0,94 (Spearman)** con el `share_formal` de entrada. El ranking sectorial observado
además no se mueve en tres años (ρ ≈ 0,98 entre años consecutivos en `momentos_2024/2025/2026`):
la misma persistencia tonta que ya ganó en nivel **también reproduce el reparto**.

**La única respuesta honesta disponible** es bajar la afirmación a *"ranking de carga legal
estatutaria"* —que sí sale del CST y del `costo_despido_por_empleado_cop` de
`data/construir_empresas.py:155-156`— **y decirlo a las 09:30, no en el Q&A.** Eso es exactamente
lo que hace el arreglo **B1**, y es la razón por la que B1 no es cosmético.

### C · Pantalla

> _(pegar del bloque 5 del informe C)_

**Respuesta:** _(pendiente)_

---

## Cómo se fusiona — el procedimiento, copiado del `README.md`

1. Pegar el bloque 4 de cada informe en la tabla del §1.
2. Cruzar MENTIRAS / HUÉRFANOS / FALTANTES de los tres. **Lo que aparece en dos listas o más
   sube al §2 y va primero.**
3. Sumar minutos. Cortar en 08:30, mirando la tabla por dueño y no solo el total.
4. Lo que no entró y no está en ningún "LOS 3 ARREGLOS" baja al §4 como límite declarado.
5. Contestar las tres preguntas del §5 por escrito.

**Una sola persona fusiona.** Dos personas fusionando en paralelo producen dos listas de corte
distintas, que es peor que no tener ninguna.
