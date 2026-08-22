# `engine/MODELO.md` — el modelo, archivo por archivo

**Dueño: Manuel (R2)** · rama `rol/backend`

> **Qué es este archivo.** El mapa entre la teoría y el código: **de dónde sale cada pieza,
> en qué archivo vive, qué test la prueba y qué supuesto carga.** Se escribió **antes** que
> el código, a propósito: si una función no tiene fila en esta tabla, o no debería existir o
> le falta fundamento.
>
> La idea completa está en [`docs/IDEA.md`](../docs/IDEA.md). Las fuentes, en
> [`docs/investigacion/`](../docs/investigacion/). Este archivo es el puente.

---

## El mapa

| Concepto | Ancestro teórico | Archivo | Función | Test que lo prueba | Supuesto que carga |
|---|---|---|---|---|---|
| **Determinismo** | [`numpy` SeedSequence](https://numpy.org/doc/stable/reference/random/parallel.html) | `seed.py` | `generador_raiz(seed)` · `stream_de_ronda(k)` | Dos corridas, mismo seed, resultado idéntico | Misma máquina y versiones ([ADR 0009](../docs/adr/0009-frontera-del-determinismo.md)) |
| **Estado del mundo** | ODD elemento 2 | `mundo.py` | `cargar_poblacion()` · `EstadoFiscalizacion` · `EstadoMundo` | La población cargada valida contra `contracts/agente.json` | — |
| **La política** | — | `mundo.py` | `Politica.como_mecanica()` | La mecánica generada **no contiene** el nombre de la política ni años | — |
| **Costo formal** | Allingham-Sandmo 1972 | `costos.py` | `costo_formal(salario, factor_prestacional)` | Monotonía en el salario | ⚠️ **factor prestacional ≈ 1,4-1,5**, sin cifra exacta verificada. Barrido de sensibilidad |
| **Costo informal** | Allingham-Sandmo 1972 | `costos.py` | `costo_informal(salario, p, sancion)` | Crece con `p` | Pérdida de acceso a crédito y clientes formales **no se modela**. Se declara |
| **Fiscalización endógena** | A-S con `p` endógeno + [PNAS 2021](https://www.pnas.org/doi/10.1073/pnas.2108507118) | **`fiscalizacion.py`** | `prob_sancion(C, E)` = `1 − exp(−C/max(E,1))` | Decreciente en `E`; en `[0,1)` para todo `E`; **corrida de control con `p` fijo no produce cascada** | ⚠️ **inspecciones por inspector por trimestre**, sin fuente. Es el supuesto más importante del motor |
| **Capacidad de inspección** | MinTrabajo / OIT | `mundo.py` | `capacidad_trimestre()` | Cambiar la capacidad mueve `p` en la dirección esperada | ⚠️ planta de 904 cargos es de ~2015. Conversión anual→trimestral no es uniforme |
| **Veto de factibilidad** | [ADR 0003](../docs/adr/0003-veto-de-factibilidad.md) | **`veto.py`** | `vetar(decision, firma)` → `{factible, razon}` | Una propuesta sin caja se rechaza **con razón**; 3 reintentos y luego `cumplir` | Qué cuenta como "caja disponible" en un trimestre |
| **Decisión del trabajador** | 🔶 [ADR 0008](../docs/adr/0008-asimetria-firma-trabajador.md) | `trabajador.py` | `acepta_informal(neto_f, neto_i, prima)` | Con prima 0 acepta siempre que el neto informal sea mayor | ⚠️ **prima de protección**: cuánto vale pensión + salud + cesantías para el trabajador. Sensibilidad obligatoria |
| **Arquetipos** | [ADR 0002](../docs/adr/0002-llm-por-arquetipo.md) (idea de AgentTorch) | `arquetipos.py` | `construir_arquetipos()` · `muestrear(arq, n, rng)` | El muestreo con el mismo seed es idéntico; las proporciones respetan la distribución del arquetipo | Los agentes dentro de un arquetipo son **intercambiables en su conducta** |
| **Agregado** | Patrón de OASIS | `agregado.py` | `Agregado.de_ronda(estado)` | El agregado que ven los arquetipos es el de la ronda **anterior**, no el de la actual | — |
| **Métricas** | — | `agregado.py` | `tasa_informalidad()` · `empleo_relativo()` · `banda()` · `brecha()` | Salida valida contra `contracts/ronda.json`; la informalidad está **ponderada** por factor de expansión | La línea base de `empleo_relativo` es el mundo sin política |
| **Scheduler de rondas** | ODD elemento 3 · [ADR 0005](../docs/adr/0005-el-reloj-de-la-simulacion.md) | **`rondas.py`** | `correr(mundo, politica, seed)` → 4 rondas | Ronda 0 es la proyección ingenua; el orden dentro de la ronda es fijo | Mejor respuesta **con rezago**, no punto fijo simultáneo |
| **Barrido del codo** | Dato A2 · equilibrios múltiples ([JPubE 2007](https://www.sciencedirect.com/science/article/abs/pii/S0047272707000497)) | `barrido.py` | `barrer(rango_aumento)` | El barrido es reproducible y monótono donde debe serlo | La resolución del barrido no crea ni borra el codo |

**Si solo lees un archivo, lee `rondas.py`.** Es donde vive la tesis: el bucle de mejor
respuesta y el punto exacto donde la fiscalización se recalcula.

---

## Las cuatro métricas, sin ambigüedad

Van al frontend y al pitch. Definidas acá para que nadie las interprete distinto:

| Métrica | Definición | Trampa que evita |
|---|---|---|
| `tasa_informalidad` | `Σ(factor_expansion × informal) / Σ(factor_expansion)` | **Siempre ponderada.** Sin el factor no es la informalidad de la GEIH, es la de la muestra |
| `prob_fiscalizacion` | `p(E)` con el `E` de la ronda **anterior**, por trimestre | Usar el `E` de la ronda actual sería un punto fijo simultáneo que no resolvemos |
| `empleo_relativo` | Empleo ponderado de la ronda `k` / empleo ponderado de la **línea base sin política** | La base **no** es la ronda 0: la ronda 0 ya tiene el efecto ingenuo |
| `banda` (p10/p90) | Sobre **N≥5 paráfrasis del prompt × M seeds**, reportando las dos dimensiones por separado | Confundir variación de lenguaje con variación de muestreo |
| `brecha` | Ronda 3 − ronda 0 | Es el producto entero |
| `n_vetos` / `n_fallback` | Conteo por ronda | Si el fallback es alto, el veto está muy apretado y el resultado no dice lo que creemos |

---

## Registro de supuestos, pre-declarado

Los `# SUPUESTO:` que el motor **va a** tomar. Escribirlos antes evita reconstruirlos a las
7am, que es imposible y se nota. `grep -rn "SUPUESTO:" engine/` es el informe de honestidad.

| # | Supuesto | Impacto si está mal | Mitigación |
|---|---|---|---|
| S1 | **Factor prestacional ≈ 1,4-1,5** | Alto: mueve el costo formal, o sea todo | Barrido de sensibilidad y reporte del rango donde la conclusión aguanta |
| S2 | **Inspecciones por inspector por trimestre** | **Máximo**: es `C`, o sea la cascada | Barrido obligatorio + chequeo de cordura contra el ~1,4% anual de EE.UU. (AEA 2025) |
| S3 | **Prima de protección del trabajador** | Medio: mueve cuánta informalización se realiza | Sensibilidad; con prima 0 es el caso extremo y se reporta |
| S4 | **Capacidad se reparte uniforme al azar entre evasores** | Medio: es el micro-fundamento de `p(E)` | Declarado en el docstring. La fiscalización dirigida daría otra forma, y se dice |
| S5 | **Conversión de capacidad anual a trimestral** | Bajo-medio | La inspección no se reparte uniforme en el año; se declara |
| S6 | **Agentes del mismo arquetipo son intercambiables en conducta** | Medio | Consecuencia de [ADR 0002](../docs/adr/0002-llm-por-arquetipo.md), ya declarada en `VALIDATION.md` |
| S7 | **Costo informal ignora pérdida de crédito y de clientes formales** | Medio: subestima el costo de informalizar, o sea **sobreestima la cascada** | Sesgo de dirección **conocida**. Se declara: nuestra cascada es una cota superior por este canal |

S7 es del tipo que conviene decir primero: sabemos hacia dónde nos equivocamos.

---

## Lo que NO va en `engine/`

- **Ninguna llamada a un LLM.** El motor no opina: acepta o rechaza.
- **Ningún `TODO: implementar`.** Es la respuesta literal a *"¿qué parte es difícil?"* y un revisor lo encuentra en segundos.
- **Ninguna constante mágica.** Nombre y fuente, o `# SUPUESTO:`.
- **Ningún bucle OOP por agente.** Vectorizado sobre dataframe ([ADR 0001](../docs/adr/0001-motor-vectorizado-propio.md)).
- **Nada de `web/`, `data/` ni `behavior/`.**

## Cómo se verifica desde afuera

```bash
make test                      # determinismo · veto · fiscalización · contratos
make run                       # una corrida; imprime seed y hash de caché
grep -rn "SUPUESTO:" engine/   # el informe de honestidad
```
