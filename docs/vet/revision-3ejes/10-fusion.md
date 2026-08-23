# `10-fusion.md` — la lista de corte de la revisión a tres ejes

> **Esqueleto creado el 23-ago 04:29 por Manuel (R2). Fusionado el 23-ago 04:35, con los tres ejes.**
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
| Fusión cerrada | 04:35 |
| Congelamiento del repo | **domingo 09:30** |
| Colchón obligatorio | 1 hora |
| **Corte real: nada nuevo empieza después de** | **08:30** |

**Quedan ~3 h 55 min de trabajo real.** El cuello de botella (§3) son 100 minutos por persona.
Cabe, y cabe con holgura. El riesgo de esta fusión no es el tiempo: es qué se decide mostrar.

## Estado de los tres informes

| Eje | Agente | Ruta del informe | Estado |
|---|---|---|---|
| **A · Ejecución** | `juez-tecnico` | [`…/juez-tecnico/2026-08-23-0402-eje-A-ejecucion.md`](../../agents/juez-tecnico/2026-08-23-0402-eje-A-ejecucion.md) | ✅ **ENTREGADO** 04:02 · sin segunda opinión · 4 hallazgos verificados a mano |
| **B · Fundamentación** | `juez-cientifico` | [`…/juez-cientifico/2026-08-23-eje-B-fundamentacion.md`](../../agents/juez-cientifico/2026-08-23-eje-B-fundamentacion.md) | ✅ **ENTREGADO** 04:14 · **con segunda opinión** (`codex`/GPT-5, coincidencia independiente) |
| **C · Pantalla** | `juez-hackathon` | [`…/juez-hackathon/2026-08-23-eje-C-pantalla.md`](../../agents/juez-hackathon/2026-08-23-eje-C-pantalla.md) + [**ADENDA del deploy vivo**](../../agents/juez-hackathon/2026-08-23-eje-C-pantalla-ADENDA-deploy.md) | ✅ **ENTREGADO** 04:17 · sin segunda opinión · adenda verificada por navegador y por comando |

> ⚠️ **Trampa de nombres en la carpeta C.** `docs/agents/juez-hackathon/` tiene un
> `2026-08-23-0009-repo.md` que es de las 00:09 y es modo `repo`, **no** el Eje C.
>
> ⚠️ **Los tres midieron árboles distintos.** B midió `9218dc3`, A midió `9218dc3`, C midió
> `f9e705c`. Entre los tres solo hay `docs/`, 0 líneas de código: los tres miden el mismo motor.
> **Ninguno midió lo que está desplegado**, que es el hallazgo #1 de abajo.

---

## §1 · Los 9 arreglos posibles

| # | Arreglo | Carpeta dueña | Min | Cómo se verifica | SI NO LO ARREGLAMOS |
|---|---|---|---|---|---|
| **A1** | Deploy apunta a `main` (o declarar qué commit está vivo) **+ recalentar la caché detrás** | Juanda (R5) | **20** (15 + 3 de calentamiento, y **cuesta una corrida**) | `curl` SSE ronda 0 del deploy == `make reproduce` local, **y** `event: fin` trae `cache_aciertos > 0` | El juez clona, corre, le salen otros números y deja de creer el 37,37 pp. **Y si se hace a medias, la demo se cae** (ver el recuadro de abajo) |
| **A2** | `make run` que corra + `cache-demo.json` exportado — **es la obligación pendiente del ADR 0009**, no un extra | Juanda (R5) + Nico (R3) | 40 | `make run` ×2 con `diff` vacío; G1 deja de estar bloqueado; **`git ls-files behavior/ \| grep cache-demo` devuelve el archivo** | Los dos primeros comandos del README fallan delante del jurado, y el nivel 2 de determinismo **no existe para nadie fuera del equipo** |

> ### ⚠️ A1 en dos pasos, y el segundo no es opcional
>
> **Cambiar el branch dispara un redeploy, y el redeploy borra la caché.** Lo dice el propio repo:
> `docs/DEPLOY.md:118` («la caché en disco del contenedor **no sobrevive a un redeploy**») y
> `:152` («no hay disco montado»). Esa caché es la que tiene los **117 aciertos** que hacen que la
> demo dure 0,6 s.
>
> ```bash
> # 1. apuntar a main
> #    render.yaml:32,52  →  branch: main
> #    OJO: si los servicios se crearon a mano en el dashboard y no desde el Blueprint,
> #    render.yaml es decoración y el branch se cambia en la UI de Render.
> # 2. recalentar, inmediatamente después del último deploy
> make humo URL=https://enjambre-web.onrender.com LLM=1   # ~3 min, PAGA una corrida
> ```
>
> **Si se hace el paso 1 y no el 2, la demo pasa de 0,6 s a 90 segundos de pantalla en negro.**
> Medido: con `aumento_pct=17` (fuera de caché) el stream no emite un solo byte en 90 s, ni el
> evento `inicio`.
>
> ### Por qué A2 no es un «nice to have»
>
> El [ADR 0009](../../adr/0009-frontera-del-determinismo.md) define la promesa del repo como
> *«mismo seed + misma caché de decisiones + mismas versiones = mismo resultado»* (`:22`) y le deja
> una obligación explícita a `behavior/` (`:32-34`): *«la caché deja de ser un archivo temporal…
> sin eso, el nivel 2 no existe para nadie que no seamos nosotros»*.
>
> **Verificado: nunca se cumplió.** `behavior/.gitignore` contiene `.cache/` y no existe
> `cache-demo.json` en `main` ni en la rama desplegada. Por eso la caché del deploy vive solo dentro
> del contenedor. **A2 es deuda de un ADR aprobado, no una mejora.**
>
> Nota aparte, por si alguien los confunde: **el seed no reemplaza a la caché.** El seed siembra el
> azar del motor; la caché congela las respuestas del LLM. Y hoy el seed **no hace nada**:
> `api/servidor.py:80` dice `SEED_EFECTO = "etiqueta"`, y `engine/seed.py` no lo importa nadie fuera
> de sus propios tests (`api/servidor.py:73`).
| **A3** | Cap de gasto acumulado + caché caliente | Manuel (R2) + Nico (R3) | 30 | `fin` trae gasto acumulado; `python3 -m behavior.cache` muestra entradas Sonnet | El juez espera minutos sin saber si se colgó, y el clic nº9 quema los USD 50 |
| **B1** | Rebautizar el mapa y decir de qué está hecho: «carga legal por celda (sobrecosto prestacional + costo de despido del CST)» | Dani (R4) + Juanda (R5) | 20 | `grep -rn "no puede pagar\|quién aprieta" web/` = 0; la nota al pie existe en la lámina | Un juez abre `construir_empresas.py:70`, ve que todas las empresas tienen el mismo colchón, y pregunta *«¿su mapa solo dice que el informal es informal?»* |
| **B2** | Meter el **segundo episodio** (2024→2025: +9,5% de alza → **+2,63 pp**, signo opuesto) y la **no-ceguera del pre-registro** en `VALIDATION.md` | Juanda (R5) | 25 | `grep -n "2,63" VALIDATION.md` y `grep -n "no fue ciego" VALIDATION.md` ≥ 1 | El jurado los encuentra solo (están en el repo público) y lo que era rigor se lee como cifra escondida |
| **B3** | Quitar la palabra «cobertura» del número: `Cobertura del rango: NO` → «el observado NO cae dentro del rango entre paráfrasis (33,9 pp, N=5, min–max)» | Juanda (R5) + Dani (R4) | 15 | `sed -n '160,175p' scripts/validate.py` muestra la frase nueva; `grep -rn "Cobertura" scripts/ web/` = 0 en contexto de banda | Basta preguntar *«¿cobertura de qué nivel?»* para que la barra de error, lo más honesto que tenemos, sea lo menos defendible |
| **C1** | Rebautizar la brecha: «proyección oficial» → «escenario sin adaptación · ronda 0 del modelo» | Dani (R4) | 20 | `grep -rn "proyección oficial\|cumplimiento total" web/enjambre` = 0 | El juez pide ver esa proyección oficial, no existe, y la cifra grande de la pantalla pasa a ser inventada |
| **C2** | Que la espera diga la verdad (leer `d.trayectoria`) y que la banda diga qué es | Dani (R4) | 25 | `?modo=reglas&trayectorias=2` y ver el rótulo cambiar | La pantalla parece colgada varios minutos y el rango se lee como un intervalo de confianza que no calculamos |
| **C3** | Subir el error del backtest (37,37 pp) a la primera pantalla | Dani (R4) | 15 | Se lee sin un clic, en `/` | Lo único que ningún otro simulador entrega queda en el pie de una página secundaria |

**Fuera de la cuota de tres, por la ADENDA del Eje C** (verificado por navegador, no por el agente):

| # | Arreglo | Carpeta dueña | Min | Cómo se verifica |
|---|---|---|---|---|
| **C0** | **Es A1.** Mismo arreglo, encontrado por el otro lado. Ver §2. | Juanda (R5) | — | — |

> ⚠️ **Corrección al comando de verificación de B3.** El informe del Eje B propone
> `python scripts/validate.py --dry` y **ese flag no existe**: `scripts/validate.py` no tiene
> `argparse` (único `__main__` en `:279`, cero `add_argument`; verificado en `9218dc3`). Quien
> intente verificar B3 con ese comando a las 6am va a ver un error y va a creer que el arreglo
> falló. La verificación de la tabla ya quedó corregida a inspección estática.

---

## §2 · Lo que aparece en dos ejes o más — VA PRIMERO

**La regla:** un defecto que dos revisores ven por separado, mirando capas distintas, no es una
opinión. Es estructural.

**Salieron cuatro.** Los cuatro son de la familia *«la pantalla afirma algo que el motor no hace»*.

| # | Defecto | Ejes | Evidencia de cada uno | Arreglo |
|---|---|---|---|---|
| **E1** | **Lo desplegado NO es `main`.** La rama del deploy es un **ancestro estricto** de `main`: le faltan 15 commits, incluidos los que devolvían la procedencia y quitaban la cascada como hallazgo | **A + C** | **A·M1:** los números del deploy no cuadran con `make reproduce` local. **C·ADENDA:** `git merge-base main origin/rol/integracion-deploy` = `1aef592` = la punta de la rama desplegada; `main..deploy` vacío; `render.yaml:32,52` | **A1** |
| **E2** | **El agregado lo produce el `fallback`, no el LLM ni el veto — y la pantalla dice lo contrario** | **A + C** | **A·M6:** `fraccion_fallback = 69,1%`, `fraccion_sin_salida = 63,0%` contra el umbral de alarma de 5% del propio equipo (`behavior/capa.py:337-340`). **A·FALTANTES 5:** los campos viajan en el contrato y ningún panel los lee. **C (vivo):** la pantalla dice «Población decidida por LLM (top-K) **80,2 %**» y, tres centímetros abajo, «**0 llamadas API · $0.00 USD**» | **A3** + **C2** |
| **E3** | **La cascada falsada, dibujada como resultado** | **B + C** | **B·HUÉRFANOS:** grep encuentra «cascada» en `CurvaBrecha.tsx`, `reporte/Graficas.tsx`, `laboratorio/Graficas.tsx`, y B declara explícitamente que *«el texto exacto de cada leyenda es del Eje C»*. **C (vivo):** «LA BRECHA · **PROYECCIÓN OFICIAL VS CORRIDA REAL**» (`CurvaBrecha.tsx:40`), línea rotulada «oficial 30,6 %» (`:63`), y el comentario del archivo la llama «la cascada real» (`:3-4`) | **C1** |
| **E4** | **La banda está mal nombrada en los dos sitios donde aparece** | **B + C** | **B·3:** `Cobertura del rango: NO` invita a *«¿cobertura de qué nivel?»*. **C·M3:** `Procedencia.tsx:44` la llama «Banda de incertidumbre (p10–p90)» cuando el backend dice `PARAFRASIS_EFECTO = "ninguno"` (`api/servidor.py:96`) | **B3** + **C2** |

> **E1 y E3 se cruzan de la peor forma.** El commit que el deploy NO tiene es, textualmente,
> `024340b` *«reporte: la procedencia vuelve, y **la cascada deja de ser un hallazgo**»*. O sea: el
> arreglo de E3 ya está escrito y mergeado en `main`, y el juez no lo va a ver. **Arreglar E1
> arregla medio E3 gratis.**

---

## §3 · El corte

**Regla dura del congelamiento:** lo que no está en «LOS 3 ARREGLOS» de al menos un revisor,
**no se toca**. Sin excepciones y sin «es que son dos minutos».

### Suma global

| Eje | Minutos |
|---|---|
| Eje A (A1+A2+A3) | **90** (A1 subió de 15 a 20 por el recalentamiento de caché) |
| Eje B (B1+B2+B3) | 60 |
| Eje C (C1+C2+C3) | 60 |
| **Total** | **210** (3 h 30 min) |

### Suma por dueño — el número que de verdad manda

Los arreglos los hacen personas distintas **en paralelo**, pero una persona no puede hacer dos a
la vez. El cuello de botella es el dueño más cargado, no el total.

| Dueño | Arreglos que le tocan | Min acumulados |
|---|---|---|
| **Juanda (R5)** | A1, A2, B2, B3 | **100** |
| **Dani (R4)** | B1, B3, C1, C2, C3 | **95** |
| Nico (R3) | A2, A3 | 70 |
| Manuel (R2) | A3 | 30 |
| Alejo (R1) | — | 0 |

**Caben los nueve.** 100 minutos contra 235 disponibles. Eso no significa que sobre tiempo: son
estimaciones hechas a las 4am por quien no va a ejecutarlas, y `main` todavía tiene que llegar al
deploy y volver a probarse.

> **El calentamiento de A1 va al final de todo, no al hacer A1.** Cada deploy posterior vuelve a
> borrar la caché. Si Dani mergea C1/C2/C3 después de que Juanda calentó, hay que volver a calentar.
> **La última acción antes del pitch es siempre `make humo URL=... LLM=1`**, pase lo que pase.

### Lo que entra — en este orden, y el orden importa

1. **A1 (E1) primero, antes que nada.** Sin esto, B1, C1, C2 y C3 se aplican sobre código que el
   juez no va a ver. Es el único arreglo que **desbloquea a otros cinco**.
2. **B2.** Es el único hallazgo de toda la revisión que puede costar el proyecto entero en vez de
   un punto, y no depende de nadie.
3. **C1 + C3** (Dani), **B3** (Juanda+Dani): los tres rótulos que mienten.
4. **C2** (E2 en pantalla) y **A3** (E2 en el motor). Son el mismo defecto por los dos lados.
5. **B1.** Baja la afirmación del mapa a lo que el dato aguanta.
6. **A2**, que es el más largo. Va acá por tiempo, no por importancia: **si A2 existiera, el paso 2
   de A1 sobraría**, porque `cache-demo.json` versionado sobrevive al redeploy y la caché del
   contenedor no. Mientras A2 no esté, cada deploy se paga con una corrida.
7. **Recalentar la caché.** No es un arreglo, es el cierre obligatorio:
   `make humo URL=... LLM=1` **después del último deploy que se haga**, sea cual sea.

### Lo que NO entra, y por qué

1. **Nada de los tres bloques de HUÉRFANOS se borra.** Borrar código a las 5am con cinco ramas
   vivas produce conflictos, no claridad. Los huérfanos **salen de la demo** (no se muestran), que
   es lo que pedía el contrato de salida. Cero commits.
2. **`/laboratorio`.** Se queda 404 y no se arregla. Sus 5 líneas de `historico.jsonl` sobre disco
   efímero no sostienen el título «Lo que sabemos después de 5 corridas».
3. **La heterogeneidad de capacidad de pago** (el fondo de B1). Meter un margen por sector a esta
   hora es tocar `data/` y `engine/` a la vez, sin tiempo de re-validar. Se declara (§4).
4. **La trampa del slider** (abajo). Es un hallazgo real y verificado, y **no está en los tres
   arreglos de ningún revisor**. La regla dice que no se toca. Ver §4: se declara y se maneja
   demostrando solo el escenario cacheado.

---

## §4 · Límites declarados — lo que se dice en voz alta en vez de arreglarse

No es la lista de la vergüenza. Es la lista que **se dice antes de que la pregunten**.

### El que hay que decir sí o sí, del Eje C

- **La demo es una repetición grabada, y hay que decirlo en la frase de apertura.** El deploy corre
  en `modo: "llm"` y hace **0 llamadas**: `{"llamadas_api": 0, "cache_aciertos": 117,
  "cache_fallos": 0}`. El escenario del pitch (23 %, seed 42) está cacheado entero.
- **El slider solo responde en el valor grabado.** Medido: con `aumento_pct=17` el stream **no
  emite un solo byte en 90 segundos**, ni el evento `inicio`. **En la demo no se mueve el slider**,
  y si un juez pide moverlo, la respuesta honesta es *«esa corrida tarda minutos y cuesta dinero;
  el escenario que le muestro está pregrabado y es reproducible con `make reproduce`»*.

### Del Eje B

- El margen sobre nómina es **uniforme (0,18) para las 81 celdas** y **no observado**
  (`data/construir_empresas.py:70`). El salario y el tamaño **se cancelan algebraicamente** en el
  veto (`engine/veto.py:443-445`). El ranking de presión correlaciona **ρ = 0,94** con el
  `share_formal` de entrada: el mapa es, en buena parte, un re-dibujo del insumo.
- Lo que **sí** tiene un dato legal real detrás y es lo que hay que mostrar: el **costo de despido
  del CST** (`data/construir_empresas.py:155-156`), que el veto cobra de verdad.
- El pre-registro **no fue ciego**: `2d4aa7e` ya apuntaba a la rama B.

### Del Eje A

- `api/servidor.py:200-201` cae a corrida en frío **en silencio** cuando falta
  `behavior/cache-demo.json`; `scripts/reproduce.py:70-72` sí lo anuncia. El camino silencioso es
  el que el juez clickea.
- `engine/seed.py` (315 líneas con test) no tiene un solo consumidor fuera de su propio test.
- Las 503 entradas de caché son **todas Haiku**, cero Sonnet.
- La higiene filtra términos, no magnitudes: `"2.500.000 u"` + 23% pasa el filtro. `[SOSPECHA]`.

### Del Eje C, fuera de sus tres

- `/reporte` y `/laboratorio` responden **404** en producción hasta que A1 se haga.
- Titulares de un **medio ficticio** («EL CENTINELA») en el producto que vende *«publicamos nuestro
  error»*. No se borra; **no se muestra**.
- El botón «SIMULAR POLÍTICA PERSONALIZADA · BLOQUEADO · PRÓXIMA ITERACIÓN» está vivo en producción.

---

## §5 · Las tres preguntas que nos hunden — el Q&A real

Se contestan **por escrito antes de la demo**. Estas respuestas son un borrador de quien fusionó:
**cada dueño valida la suya antes de las 08:30.**

### A · Ejecución

> **«Muéstrame ahora, en el link, una corrida en modo LLM con la banda de 5 trayectorias. ¿Cuánto
> tardó, cuánto costó y qué fracción de tus agentes se quedó sin ninguna opción factible?»**

**Respuesta (borrador):** lo que está en el link es una corrida pregrabada: 0,6 s, $0.00, 117
aciertos de caché y 0 llamadas. La corrida en vivo con 5 trayectorias tarda minutos y sí gasta;
está presupuestada y la podemos lanzar, pero no cabe en la demo. Y el número que importa de esa
pregunta lo publicamos igual: **63 % de las celdas termina sin ninguna opción factible** y cae al
`fallback`. Ese es un resultado del modelo, no un error de ejecución, y es la razón por la que no
afirmamos el nivel.

### B · Fundamentación

> **«Ustedes dicen que el nivel falló pero el reparto se sostiene. ¿Qué variable de su modelo hace
> que una empresa aguante el alza y otra no, una que NO sea la informalidad que ya traía de la
> encuesta?»**

**Respuesta (borrador, y es la incómoda):** hoy, ninguna. El margen es 0,18 para las 81 celdas, y
el salario y el tamaño se cancelan en el veto. Por eso a partir de las 09:30 **no llamamos a eso un
mapa de capacidad de pago**: es un **ranking de carga legal estatutaria** (sobrecosto prestacional
del CST + costo de despido del CST), y esa parte sí tiene una fuente legal real detrás. La
heterogeneidad de caja por sector es el siguiente dato que hay que traer, y no lo teníamos.

### C · Pantalla

> **«¿Por qué la pantalla dice que un LLM decidió el 80 % de la población y al lado dice 0 llamadas
> a la API y $0.00? ¿Me está mostrando una corrida o una grabación?»**

**Respuesta (borrador):** una grabación, y está mal rotulado. El 80 % describe qué fracción de la
población **entra por la ruta LLM** en el diseño; la corrida que usted acaba de ver salió entera de
caché, por eso son 0 llamadas. Las dos cifras son ciertas y juntas se leen como una mentira: es el
arreglo **C2**. Lo que hay detrás es verificable sin nosotros: `make reproduce` da el mismo
resultado en su máquina, sin API key.

---

## Cómo se fusiona — el procedimiento, copiado del `README.md`

1. Pegar el bloque 4 de cada informe en la tabla del §1.
2. Cruzar MENTIRAS / HUÉRFANOS / FALTANTES de los tres. **Lo que aparece en dos listas o más
   sube al §2 y va primero.**
3. Sumar minutos. Cortar en 08:30, mirando la tabla por dueño y no solo el total.
4. Lo que no entró y no está en ningún «LOS 3 ARREGLOS» baja al §4 como límite declarado.
5. Contestar las tres preguntas del §5 por escrito.

**Una sola persona fusiona.** Dos personas fusionando en paralelo producen dos listas de corte
distintas, que es peor que no tener ninguna.

---

## Lo que esta fusión NO decidió

- **No priorizó entre A1 y B2.** Los dos son «primero». A1 desbloquea a cinco; B2 es el que puede
  costar el proyecto. Los hacen personas distintas, así que arrancan a la vez y el conflicto es
  teórico, pero si hay que elegir, elige el equipo, no este archivo.
- **No tocó `docs/PLAN.md` ni `VALIDATION.md`.** B2 los toca y es de Juanda.
- **No verificó los arreglos de los otros dos ejes.** A y C corrieron sin segunda opinión. Solo B
  tuvo una. Un informe de agente es un reclamo con fecha.

---

## Después del congelamiento — por dónde se sigue puliendo

Esta fusión corta a las 08:30 y decide **qué se muestra el domingo**. Lo que sigue es lo que queda
**después**, para no volver a arrancar de cero. Nada de esto entra antes del congelamiento.

**El grueso ya está escrito**, en el anexo del informe del Eje B:
[`…/juez-cientifico/2026-08-23-eje-B-fundamentacion.md` §C](../../agents/juez-cientifico/2026-08-23-eje-B-fundamentacion.md)
— **7 pendientes, cada uno con el comando real, el dueño y el costo**.

**Lo que hay que saber antes de correr cualquier cosa:**

- **`make run` todavía no existe.** `scripts/run_simulacion.py` no está en el repo y el target
  imprime `PENDIENTE`. Es justo lo que arregla **A2**. Mientras tanto, las corridas entran por
  `behavior/demo.py`, `behavior/ablacion.py`, `scripts/barrido_politicas.py` y `scripts/validate.py`.
- **Sin `--llm` todo corre por la ablación determinista y cuesta $0**, repetible sin límite.
  **6 de los 7 pendientes cuestan $0**; solo el de la banda toca presupuesto.
- **Trampa de nombre:** `demo.py --reparto` **no** es el mapa distributivo — es repartir las
  paráfrasis por peso poblacional. Quien ataque el mapa con ese flag va a medir otra cosa.

**El orden en que valen la pena, y por qué:**

| # | Qué resuelve | Dueño | Costo |
|---|---|---|---|
| **1** | **Margen heterogéneo por celda.** Es el fondo de **B1** y lo que el §3 dejó explícitamente fuera. Decide si el mapa es un resultado o un re-plot del insumo: hoy correlaciona **0,94** con `share_formal`. Si tras el cambio no baja de ~0,85, el mapa hay que rebautizarlo igual y para siempre | Alejo (R1) | $0 |
| **2** | **`tasa_informalidad` ponderada por empleo superviviente** (`behavior/rondas.py`). Si una celda que despide media planta sigue aportando la misma masa informal, **contamina EL NÚMERO**, no solo el mapa. Es `[SOSPECHA]` sin verificar: el más barato con más consecuencia | Nico (R3) | $0 |
| **3** | **La cascada demostrada en vez de afirmada.** El flag ya existe: `--sin-cascada` congela `p(sanción)` en ronda 0. Contrastarlo contra la corrida normal convierte **E3** de mentira en lámina honesta | Nico (R3) + Dani (R4) | $0 |
| **4** | **α = 1,875 derivado, no heredado** (`engine/fiscalizacion.py`, ADR 0007). Si está calibrado contra la informalidad que el modelo debe reproducir, es circular | Manuel (R2) | $0 |
| **5** | **Unidades en `behavior/ablacion.py:71-102`** (COP/mes sumado con COP/trimestre). Toca el camino determinista con el que se reproduce todo sin API key | Nico (R3) | $0 |
| **6** | **La banda con N mayor.** Con N=5 el rango es literalmente el mínimo y el máximo. Con más paráfrasis empieza a poder llamarse algo | Nico (R3) | **gasta LLM** |

**Y la pregunta de B sigue sin respuesta escrita** (§5): *¿qué variable hace que una empresa aguante
el alza y otra no, que no sea la informalidad que ya traía de la encuesta?* El pendiente **1** es el
único que puede llegar a contestarla. Hasta entonces, la respuesta honesta es la del §5.
