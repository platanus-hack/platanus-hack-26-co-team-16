# Estado consolidado — 2026-08-22, tras mergear los 4 PR abiertos

> **Qué es este archivo.** La foto del repo en el momento en que las cuatro ramas se juntaron en `main`. Existe para que la replanificación se haga sobre hechos verificados y no sobre lo que cada uno recuerda de su rama. **No es normativo:** es una medición con fecha, no una decisión. Lo que se confirme y cambie el modelo se gradúa a un ADR o al registro de supuestos de `../../engine/MODELO.md`.
>
> **Método.** Todo lo de aquí se corrió o se grepeó. Lo que viene de un análisis que no reproduje va marcado como tal. Ningún número de este archivo sale de la memoria de nadie.

## Qué se mergeó

| PR | Rama | Autor | Review |
|---|---|---|---|
| #6 | `rol/conductual-top-k` | Nico | APPROVED (humana, previa) |
| #7 | `rol/backend` | Manuel | Agente de ingeniería, modelo y sesión distintos |
| #5 | `rol/datos` | Alejo | `peeky`, modelo y sesión distintos |
| #8 | `docs/contrato-agentes` | Alejo | Revisado a ojo: 15 líneas de documentación |

Los cuatro dieron `MERGEABLE/CLEAN` y **no compartían un solo archivo**. Cero conflictos.

## Qué corre hoy

```
python -c "import engine, behavior"   OK
pytest engine/ -q                      44 passed in 0.79s
python -m behavior.pruebas             todas las regresiones pasan
pytest tests/                          no tests ran
```

**El determinismo aguanta.** `data/parametros_legales.py` regenera su JSON byte por byte idéntico (SHA-256 `5c89b83ced7d…`). `peeky` verificó lo mismo para `empresas.parquet`.

## Qué existe

| Carpeta | `.py` | Líneas |
|---|---|---|
| `behavior/` | 12 | 2.586 |
| `engine/` | 7 | 1.466 |
| `data/` | 4 | 784 |
| `contracts/` `api/` `web/` `tests/` `scripts/` | 0 | 0 |

**34 supuestos** marcados con `# SUPUESTO:`. `web/` tiene el prototipo HTML de Dani; `api/`, `tests/` y `scripts/` siguen vacíos.

## Lo que el contrato promete y no está

1. **`engine/rondas.py` no existe.** `AGENTS.md:11` lo declara *"si solo lees un archivo… es donde vive la tesis"*. El bucle de mejor respuesta está en `behavior/rondas.py`. `engine/MODELO.md` lo cita **5 veces**, junto con otros cinco módulos que tampoco existen (`mundo.py`, `costos.py`, `trabajador.py`, `agregado.py`, `barrido.py`).
2. **`make test` está ciego a los 44 tests.** El target corre `pytest tests/`, `tests/` solo tiene un README, y el Makefile imprime *"No hay tests todavia"* mientras 44 pasan en `engine/`. **Es de Juanda (R5):** `Makefile` y `tests/` son suyos.
3. **No hay `requirements.txt` ni `pyproject.toml`** y el código usa numpy, pandas, requests y anthropic. Nadie puede reproducir el entorno desde cero.

## Las costuras rotas

Todas verificadas contra el código, con la línea en la mano.

### 1. 🔴 El veto del motor nunca se entera de nada

`veto_del_motor(estado)` captura un `EstadoVivo` y el veto consulta solo ese objeto (`engine/veto.py:254-262,332-341`). Pero **`behavior/rondas.py` no menciona `EstadoVivo` ni `registrar` ni una vez**. Si se cablea de la forma obvia, el veto ve el estado inicial para siempre: en la ronda 2+ puede autorizar despedir a quien ya fue despedido.

**Ningún test lo detecta:** `engine/test_veto.py` actualiza el estado a mano (2 llamadas a `.registrar()`) y **nunca llama a `correr()`**. Los tests prueban el veto aislado, que funciona, y jamás la composición, que no.

### 2. 🟠 La fiscalización se calcula dos veces con universos distintos

`behavior/rondas.py:118-141` toma `capacidad_fiscalizacion` como **fracción** (0.02) por factores de expansión. `engine/fiscalizacion.py:76-96` calcula una capacidad **absoluta** (3.900 inspecciones). Ninguna llama a la otra, y el `prob_fiscalizacion` que sale hacia el frontend viene solo de `behavior/`. Eso mueve la cascada, que es la tesis.

### 3. 🟠 El mismo código ordinal, dos traducciones

`data/construir_empresas.py:42-58` traduce el código 2 como **2.5** y el 3 como **4.5**; `behavior/arquetipos.py:35-45` los traduce como **3** y **5**. Además `data/` resta al dueño y `behavior/` no. `contracts/README.md:38-40` afirma que las dos tablas son idénticas. **No lo son.** Misma familia que el bug de `tamano_empresa` del PR #4.

### 4. 🟠 `empresas.parquet` no tiene ni un consumidor

`behavior/arquetipos.py:100-101` sigue con los coeficientes de andamio (`nomina*0.18`, `ingreso*1.5`) que `empresas.parquet` venía a reemplazar con fuente legal.

### 5. 🟠 La indemnización usa la tarifa equivocada arriba de 10 SMLMV

`data/parametros_legales.json:440-453` declara los dos tramos del Art. 64 CST pero solo materializa `meses_de_salario_bajo_10_smlmv`, y `construir_empresas.py:154-155` lo usa siempre. Costo de despido inflado ~40% en los tramos altos. **Bug de datos, de Alejo.**

### 6. 🟡 Deriva de contratos y constantes duplicadas

`contracts/ronda.json` no declara `degenerada`, pero `behavior/rondas.py:251` lo emite dentro de `banda`. `MAX_REINTENTOS = 3` vive duplicado en `engine/veto.py:90` y `behavior/capa.py:33`, y el comentario del motor afirma que `behavior` lo importa: no lo importa. Coinciden hoy; el día que dejen de coincidir nadie se entera.

*Reportado por el análisis y **no verificado por mí**: desajuste semántico de `fraccion_informal` — `behavior/contrato.py:191-229` la calcula sobre la planta original, `engine/veto.py:258-262` la interpreta sobre la planta sobreviviente. Si es cierto, no se arregla conectando los diccionarios: hay que elegir una unidad canónica primero.*

## La decisión que el equipo tiene que tomar

El motor y la capa conductual se importan sin error y las interfaces encajan — `Arquetipo` satisface el Protocol `Firma` campo por campo, y `veto_del_motor()` devuelve exactamente el callable que `correr()` acepta. **La conexión es posible hoy y nadie la ha hecho.** Pero cablearla sin decidir esto primero solo esconde el problema:

- **(a)** `engine/rondas.py` orquesta y `behavior/` solo propone decisiones.
- **(b)** `behavior/rondas.py` sigue orquestando, pero recibe y actualiza el `EstadoVivo` y el `EstadoFiscalizacion` del motor.

`docs/PLAN.md:197-198` no lo resuelve: le asigna "rondas" a R2 y "bucle de rondas" a R3. **Un wrapper vacío en `engine/rondas.py` sería peor que nada**: escondería los dos estados en vez de reconciliarlos.

## Lo primero que hay que escribir

**Un test de integración que corra dos rondas con `EstadoVivo`, `EstadoFiscalizacion` y `veto_del_motor` reales.** No existe, y es la razón por la que la costura #1 es invisible. Con ese test, el problema deja de ser una opinión y pasa a ser un fallo rojo.
