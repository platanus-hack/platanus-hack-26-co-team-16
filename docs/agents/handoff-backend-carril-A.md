# Handoff · backend, CARRIL A (reproducibilidad y herramientas)

> **Rama:** `backend/carril-a`, colgada de `backend/ultimo-momento`. PR contra esa rama, no contra `main`.
> **Sesión:** 23-ago. Reparto: [`docs/ultimo-momento/backend-reparto.md`](../ultimo-momento/backend-reparto.md).
> **Archivos tocados:** `scripts/run_simulacion.py` (nuevo), `scripts/validate.py`, `Makefile`,
> `tests/test_validacion.py`, `artefactos/` (nuevo).
> **No se abrió** `engine/`, `behavior/`, `api/`, `web/`, `data/` ni docs raíz. Todo costó **$0**:
> ni una llamada al proveedor de LLM.

## Lo que quedó cerrado

### A1 · `make run` corre una simulación completa — CERRADO

`scripts/run_simulacion.py` no existía y el target imprimía `PENDIENTE`. Ahora corre por la
**ablación determinista** (nivel 3 de la ADR 0009): sin API key, sin red, $0.

Escribe dos archivos, que son justo las dos piezas que la compuerta G1 reclamaba por nombre:

| Archivo | Qué es |
|---|---|
| `artefactos/corrida.json` | el **artefacto canónico**: la corrida entera, claves ordenadas, sin reloj ni rutas absolutas |
| `artefactos/corrida.manifiesto.json` | el **manifiesto**: seed, versiones de lo que entra al cálculo, qué caché se usó (ninguna, y lo dice) y el SHA-256 del artefacto |

Verificación, con la salida pegada:

```
$ make run && make run     # (capturando cada una y comparando)
$ diff A.txt B.txt
(sin diferencias)
$ diff A.json B.json
(sin diferencias)
$ shasum -a 256 A.json B.json
3b4f21d715544bb41d7120b87b68e82f71034befe88426fcb078b0cdb066bf51  A.json
3b4f21d715544bb41d7120b87b68e82f71034befe88426fcb078b0cdb066bf51  B.json

$ make determinismo
  dos corridas con seed=42, comparando el artefacto canonico...
  IDENTICO · sha256 3b4f21d715544bb41d7120b87b68e82f71034befe88426fcb078b0cdb066bf51
```

La frase de `AGENTS.md` —*"mismo seed, mismo resultado, verificable corriendo `make run` dos
veces"*— pasó de ser una promesa a ser un comando. `make determinismo` la corre de una.

**Por qué la ablación y no el camino LLM.** `run_simulacion.py` demuestra el **determinismo del
motor**; `reproduce.py` reproduce **el resultado publicado** e intenta la caché versionada. Son
dos cosas distintas y conviven a propósito. Si `run_simulacion.py` llamara al proveedor dejaría
de ser gratis y dejaría de correr en la máquina de un jurado sin credenciales, que son las dos
razones por las que existe.

### A3 · `--dry` existe — CERRADO

`scripts/validate.py` no tenía `argparse`: la bandera que cita el juez científico se ignoraba en
silencio, así que el comando de su informe corría la validación completa mientras su autor creía
estar haciendo una pasada seca.

```
$ grep -c argparse scripts/validate.py
4                       # antes: 0
$ python3 scripts/validate.py --dry | head -2
VALIDACIÓN PRE-REGISTRADA  ·  --dry (pasada seca)
  [BLOQUEADO] G1 reproducibilidad: --dry: los requisitos están, pero no se corrieron las dos corridas que deciden el candado (quita --dry para ejecutarlo)
```

También entró `--json`, para que la validación se pueda consumir sin parsear texto.

## A2 · los candados, uno por uno

`make validate` **sigue saliendo con exit 1, y es correcto que salga así.** Lo que cambió es que
antes había tres compuertas en `BLOQUEADO` —tres cosas que nadie había medido— y ahora hay una
que **PASA**, una que **FALLA con un número** y una que sigue bloqueada **por una razón
declarada**. Un bloqueo dice "no sabemos"; un fallo dice "sabemos, y salió mal". Es un cambio
de estado del proyecto, no un cambio de cifra.

| Candado | Antes | Ahora | Por qué |
|---|---|---|---|
| **G1** reproducibilidad | 🔴 BLOQUEADO | ✅ **PASA** | dos corridas → `3b4f21d71554…` idéntico |
| **G2** no contaminación | 🔴 BLOQUEADO | 🔴 **BLOQUEADO** | no se puede cerrar sin gastar LLM — ver abajo |
| **G3** calibración base | 🔴 BLOQUEADO | ❌ **FALLA** | ya hay productor y hay número: el orden por tamaño se rompe |

### G1 — de BLOQUEADO a PASA

El candado no sólo estaba bloqueado por piezas faltantes: **terminaba con un
`faltan.append(...)` incondicional**, así que devolvía `BLOQUEADO` aunque todo lo demás
estuviera. Ningún trabajo podía cerrarlo nunca. Ahora **ejecuta**: corre
`run_simulacion.py --solo-hash` dos veces y compara los SHA-256, que es literalmente lo que
`VALIDATION.md` promete.

Además compara contra el artefacto publicado, y distingue dos casos que no son el mismo:

- mismas versiones y distinto hash → **FALLA** (o el motor no es determinista, o el artefacto
  está podrido);
- versiones distintas → **no comparable**, y lo dice en vez de reprobar. El candado compara
  *"(seed, manifiesto, versiones)"*; con otro entorno la premisa no se cumple.

Esto último importa para el carril B: cuando B cambie el modelo, el artefacto versionado va a
dejar de coincidir y G1 lo va a decir a gritos. **Regenerarlo con `make run` es parte del PR
que cambie el modelo**, igual que correr los tests.

### G2 — sigue bloqueado, y no se forzó

Se puede correr el par canónica/re-skinneada por la ablación gratis. **Se corrió, y por eso NO
se usó:**

```
factor de reskin: 0.48438192458988005
canonica final: 24.061782%
reskin   final: 24.061782%
diferencia: +0.000000 pp
```

Ese cero **no es evidencia de no-contaminación**. `Reskin` reescribe el *texto* del prompt
(`capa.renderizar()`), y las reglas fijas de la ablación no leen texto: deciden sobre los
números del arquetipo. Cerrar G2 por ahí sería medir un canal por el que la contaminación no
puede viajar, y publicar un PASA vacío en la compuerta que sostiene la mitad del argumento de
validación del proyecto.

G2 pregunta si **el modelo** reconoce el escenario por sus magnitudes. Sólo el camino LLM
responde eso, y cuesta créditos. **Queda abierto y declarado.**

### G3 — de BLOQUEADO a FALLA, con dos hallazgos

**Hallazgo 1 · el candado comparaba dos denominadores distintos.** `candado_g3` medía contra
`tasa_informalidad_total` (30,57%: **todos** los ocupados de Bogotá) una corrida que sólo
simula **empleados de firma** (17,99%). `data/empresas.parquet` excluye a propósito a los
964.004 cuenta propia —una unidad sin empleados no puede despedir ni informalizar a nadie— y
`arquetipos.informalidad_observada()` ya lo documentaba. Con el objetivo equivocado el candado
reportaba **12,58 pp** de error puramente contable y habría reprobado el modelo por un cambio
de universo. Corregido a `tasa_informalidad_empleados_de_firma`.

**Hallazgo 2 · el agregado acierta y el desglose no.** Ya existe productor
(`make calibracion`, o sea `run_simulacion.py --aumento 0`) y el número es:

```
[FALLA] G3 calibración base: error=0.92 pp sobre empleados de firma (umbral 2 pp);
        orden micro>pyme>grande=False;
        micro 67.10% vs 59.61% obs · pyme 0.00% vs 10.57% obs · grande 0.00% vs 0.81% obs
```

El **nivel** acierta: 0,92 pp, holgadamente dentro del umbral de 2 pp. El **desglose** no: con
alza 0% —o sea, sin política— el modelo formaliza pymes y grandes al 100% e informaliza micro
de 59,6% a 67,1%. El total se salva porque las desviaciones por tamaño se **cancelan entre sí**.

Vale la pena mirar la trayectoria, porque la ronda 0 sí reproduce la GEIH exactamente:

| ronda | micro | pyme | grande |
|---|---|---|---|
| 0 (GEIH) | 59,61% | 10,57% | 0,81% |
| 1 | 67,10% | **0,00%** | **0,00%** |
| 2–3 | 67,10% | 0,00% | 0,00% |

Todo el movimiento ocurre en la primera ronda del **placebo**. Esto es vecino del pendiente
**B1** del carril B (con `alfa=0` el placebo se mueve +77,68 pp): acá, con el α por defecto, el
agregado casi no se mueve pero por debajo hay una redistribución completa. **No es mío de
arreglar** —vive en `engine/` y `behavior/`— y no lo toqué. G3 ahora lo mide y lo publica.

## Lo que hay que saber antes de seguir

1. **`tests/test_validacion.py` se reescribió.** Los tres tests que se caían afirmaban el
   *estado* del proyecto (*"G1 sigue bloqueado"*, *"G3 sigue bloqueado"*), así que caducaron el
   día que ese estado cambió — y en el camino no protegían nada: no distinguían "se cerró bien"
   de "alguien lo forzó". Ahora prueban comportamiento: que G1 sólo pase si dos corridas de
   verdad coinciden, que `--dry` no regale un PASA, que G3 use el denominador correcto y exija
   orden estricto, y que una medición nunca decida el código de salida.

   ```
   $ python3 -m pytest engine/ api/ tests/ -q
   111 passed in 6.76s            # antes 104: −3 obsoletos, +10 nuevos
   $ PYTHONPATH=. python3 behavior/pruebas.py | tail -1
   todas las regresiones pasan
   ```

2. **Se arregló el filtro del código de salida.** Las compuertas se elegían por
   `estado in COMPUERTAS`, y `BLOQUEADO` está en esa tupla: bastaba que M3 no pudiera correr
   para que una **medición** entrara al exit code, justo lo que `VALIDATION.md` declara
   imposible (*"una medición no puede reprobar"*). Ahora se eligen por nombre — qué es compuerta
   lo dice el pre-registro, no el estado que le tocó hoy.

3. **`make test` corría `engine/ tests/` y se saltaba `api/`**, así que decía 95 mientras la
   suite que el equipo corre a mano decía 111. Dos cuentas distintas de lo mismo. Alineado.

## Pendientes que dejo abiertos (y de quién son)

| # | Qué | De quién |
|---|---|---|
| 1 | **G2 exige el camino LLM.** Correr el par canónica/re-skinneada con `ClienteConductual` y registrar las dos trayectorias. Cuesta créditos: es decisión de equipo | equipo (presupuesto) |
| 2 | **G3 falla por el desglose:** el placebo manda pyme y grande a 0%. Vive en `engine/`/`behavior/`, vecino de B1 | carril B / R2 |
| 3 | **`artefactos/` se versiona.** Cuando el carril B cambie el modelo, regenerar con `make run` en el mismo PR o G1 va a marcar el artefacto como podrido | quien toque el modelo |
| 4 | **`data/prediccion_modelo.json` sigue siendo anterior al arreglo de denominador**, así que el 37,37 pp no se reproduce corriendo `main` hoy. Ya estaba declarado en `VALIDATION.md`; **no lo toqué** | equipo (~USD 8) |
| 5 | `VALIDATION.md` describe G1 y G3 con su estado viejo (🔴 tres bloqueos / 🔴 no existe productor). Es **doc raíz**, o sea de Juanda: hay que avisarle, no editarlo | Juanda (R5) |

## Comandos nuevos

```
make run            corre una simulación completa ($0, sin API key)
make determinismo   dos corridas y compara: la prueba que promete AGENTS.md
make calibracion    la corrida SIN política que pide G3
make validate ARGS=--dry    pasada seca, sin correr simulaciones
python3 scripts/run_simulacion.py --help    # --seed --aumento --rondas --salida --solo-hash
python3 scripts/validate.py --json          # la validación sin parsear texto
```
