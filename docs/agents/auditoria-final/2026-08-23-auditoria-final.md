# Auditoria final de `main` — 23-ago 2026, 06:45–08:15

> Producida corriendo el prompt de [`docs/vet/revision-3ejes/20-auditoria.md`](../../vet/revision-3ejes/20-auditoria.md)
> sobre `9674539`, y **con los arreglos aplicados durante la misma sesion** — a diferencia del
> prompt original, que pedia auditar sin tocar. El equipo decidio arreglar sobre la marcha.
>
> **Regla que se respeto:** cada afirmacion va con el comando que la produce. Lo que no se pudo
> correr esta en el §5 y no se afirmo.

---

## 1 · VEREDICTO

**Lo que se puede demostrar:** el motor es determinista y reproducible sin API key, los 27 tests
pasan, el frontend compila, el deploy sirve `main` (`/reporte` → 200), y el error del backtest se
publica con su signo en la primera pantalla. La cache de 518 respuestas Sonnet ya pagadas viaja
con el repo y se precarga al arrancar — verificado, no supuesto.

**Lo que NO se puede demostrar:** que el 37,37 pp se reproduzca corriendo el codigo de hoy. Sale
de `data/prediccion_modelo.json`, un artefacto generado **antes** del arreglo de denominador: su
ronda 0 es 30,6 % y la del motor actual es 17,99 %. La aritmetica es exacta
(`33,3 + 4,07 = 37,37`), pero la corrida que la produjo ya no es la que el repo corre.

**El riesgo mas grande vivo:** ese. Esta declarado en `VALIDATION.md` y regenerarlo es el
pendiente numero uno. Todo lo demas que se encontro esta arreglado o dicho en voz alta.

---

## 2 · LOS 9 ARREGLOS DE LA FUSION

Estado **al empezar** (06:45) y **al cerrar** (08:15). A las 06:45 solo A2 estaba completo.

| # | Al empezar | Al cerrar | Comando | Salida |
|---|---|---|---|---|
| **A1** deploy→main | SIN TOCAR | **HECHO** | `grep -n "branch:" render.yaml` · `curl` a `/reporte` | `main` en `:32` y `:52` · **200** (404 habria sido rama vieja) |
| **A2** cache versionada | HECHO | **HECHO** | `git ls-tree origin/main behavior/cache-demo.json` + conteo | blob presente · **518 entradas, las 518 `claude-sonnet-5`**, cero peso muerto |
| **A3** fracciones en panel | A MEDIAS | **HECHO (parcial, declarado)** | `grep -rln "fraccion_fallback" web/enjambre` | 5 archivos las leen. **El cap acumulado NO se anadio a proposito** — ver §4 |
| **B1** mapa → carga legal | A MEDIAS | **HECHO** | `grep -rn "no puede pagar\|quien aprieta" web/` | 0 · y la nota al pie declara margen 0,18 uniforme + costo de despido CST |
| **B2** 2º episodio | SIN TOCAR | **HECHO** | `grep -c "2,63" VALIDATION.md` · `grep -ic "ciego" VALIDATION.md` | **1** y **1** (eran 0 y 0) |
| **B3** quitar "cobertura" | SIN TOCAR | **HECHO** | `python scripts/validate.py` | `¿El observado cae en el rango? NO (rango entre parafrasis, N=5, min–max…)` |
| **C1** "proyeccion oficial" | SIN TOCAR | **HECHO** | `grep -rn "proyeccion oficial" web/enjambre` | 0 visibles · **20 sitios** cambiados, incl. 5 de `web/prototipo/mapa.html` que la fusion no conto |
| **C2** espera y banda | SIN TOCAR | **A MEDIAS** | `grep -rn "incertidumbre" web/enjambre` | banda **corregida**; la espera sigue sin leer `d.trayectoria` — ver §5 |
| **C3** 37,37 en `/` | SIN TOCAR | **HECHO** | `grep -n "37,37" web/enjambre/componentes/Menu.tsx` | se lee en la primera pantalla, sin un clic |

---

## 3 · LO QUE ESTABA ROTO Y SE ARREGLO, por lo que un juez ve primero

### 3.1 · La corrida tardaba 23 minutos — **ARREGLADO** (`a4e1429`)

Medido en `web/laboratorio/historico.jsonl`: **1398 s / 522 llamadas / USD 7,86** y
**1157 s / 566 llamadas / USD 7,91**.

Causa, declarada por el propio repo en el docstring de `_parafrasis_fijada`: las 5 trayectorias
iban **en serie** porque la unica forma de elegir la parafrasis era parchear
`behavior.capa.parafrasis`, un global de modulo, y dos hilos con parches distintos se pisan.

Arreglado como el propio docstring proponia: la redaccion viaja por parametro (`parafrasis_fija`)
y las N corren con `ThreadPoolExecutor`. **Medido despues:** 5 hilos distintos y **21,6x** contra
el camino totalmente serial, con cliente falso y coste $0. Sobre la API real el factor que este
cambio aporta es ~5x (de ~23 min a ~5); **eso no esta medido contra el proveedor todavia**.

### 3.2 · El candado mataba la URL publica — **ARREGLADO** (`8083ce0`)

`_ocupado` era un `Lock` pelado que solo se soltaba en el `finally` del generador SSE. Si el
generador se abandona, queda tomado para siempre. **El 23-ago dejo `enjambre-api` muerta ~2 horas.**
Ahora se recupera solo a los 15 min, con token por turno para que un `finally` tardio no suelte la
corrida ajena, y el mensaje dice cuanto falta.

### 3.3 · La pantalla enfrentaba dos denominadores — **ARREGLADO** (`7a76410`)

`/poblacion` servia `tasa_informalidad_observada: 0.3057` sobre un `peso_total` de 3.235.639 —
pero esos 3,23 M son empleados de firma, cuya informalidad es **17,99 %**. El reporte decia
*"informalidad observada de partida 30,6 %"* al lado de una ronda 0 de 17,99 %. La pregunta
*"¿su modelo arranca 12 puntos por debajo de la realidad?"* no tenia respuesta ensayada; la
respuesta es **no**, arranca donde su propia poblacion esta. Ahora viajan las dos con nombre propio.

### 3.4 · El artefacto de la prediccion esta desactualizado — **DECLARADO, no arreglado**

Ver §1 y el recuadro de `VALIDATION.md`. **Es el pendiente #1.**

---

## 4 · LO QUE SE DICE EN VOZ ALTA EN VEZ DE ARREGLARSE

Frases ya redactadas, para usarlas tal cual.

**Sobre el numero:**
> «El 37,37 pp sale de una corrida congelada en `data/prediccion_modelo.json` que es anterior a
> un arreglo de denominador del motor. La aritmetica es auditable y esta publicada; lo que todavia
> no puedo prometerle es que ese numero exacto salga corriendo el repo hoy. Regenerarlo cuesta
> ocho dolares y cinco minutos, y es lo primero que hacemos despues de esto.»

**Sobre la demo:**
> «Lo que ve es una repeticion grabada: 0 llamadas a la API, 518 respuestas ya pagadas que viajan
> en el repositorio. Es reproducible con un comando y sin API key. Una corrida en vivo tarda ~5
> minutos y cuesta ocho dolares — puedo lanzarla, pero no cabe en la demo.»

**Sobre el mapa:**
> «No es un mapa de capacidad de pago y dejamos de llamarlo asi. El margen sobre nomina es 0,18
> uniforme para las 81 celdas y la GEIH no lo observa. Es un ranking de carga legal estatutaria,
> y esa parte si tiene el Codigo Sustantivo del Trabajo detras.»

**Sobre el tope de gasto:** existe **por corrida** (`TOPE_USD_MAXIMO = 25`, `tope_derivado()`, y el
corte duro de `behavior/presupuesto.py`). **No se anadio un tope acumulado entre corridas**, y es
una decision: cortaria la demo a mitad del pitch, que es peor que el problema que resolveria.

**Sobre la cascada:** sigue siendo el **mecanismo** del modelo y **no** un resultado del proyecto.
El backtest la falsa. Eso ya esta en `VALIDATION.md` y no se toca.

---

## 5 · NO VERIFICABLE, y por que

| Que | Por que no se pudo |
|---|---|
| `make run` / `make test` / `make validate` | **`make` no existe en la maquina de esta sesion** (Windows). Se corrieron los scripts directamente: `python scripts/validate.py` sale con **exit 1**, que el propio `VALIDATION.md` ya declara como esperado mientras haya compuertas bloqueadas. En Linux/Mac el `Makefile` no se probo. |
| El 5x real de la corrida LLM | Medir el antes/despues contra la API cuesta ~USD 8 y no se gasto. El 21,6x reportado es con cliente falso: prueba que el paralelismo **ocurre**, no cuanto ahorra contra el proveedor. |
| `make humo URL=... LLM=1` | Paga una corrida. No se lanzo. |
| Que el API haya redesplegado a `main` | `/poblacion` responde 200 y sirve datos, pero **el campo nuevo `tasa_informalidad_total_ciudad` todavia no aparece** en la respuesta viva — senal de que ese servicio corre un commit anterior a este PR. Se confirma solo despues del proximo deploy. |
| α = 1,875 circular (ADR 0007) | No se investigo: quedo fuera por tiempo. Sigue abierto. |
| `scripts/humo_deploy.py:53` se traga excepciones | Confirmado por lectura, no arreglado. Sigue abierto. |

---

## 6 · Lo que quedo abierto

Esta en [`docs/agents/handoff-auditoria.md`](../handoff-auditoria.md), con el prompt para retomar.
