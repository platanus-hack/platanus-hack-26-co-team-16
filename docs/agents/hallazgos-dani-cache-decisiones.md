# Hallazgos — qué decidieron los 518 agentes, y por qué

> **Autor:** Dani (R4) · **Fecha:** 2026-08-23 07:50 · **Material:** los 518 archivos de
> `behavior/.cache/`, versionados en `ca1a4c2` · **Modelo:** `claude-sonnet-5`, ya pagado.
>
> **Qué es esto.** Un hallazgo con fecha, no una decisión. Nació de una pregunta concreta:
> *«hubo un alza del 23% del salario mínimo y ni un solo empleador decidió despedir; eso no tiene
> sentido»*. La pregunta era correcta y la respuesta está abajo.
>
> **Qué NO es.** No propongo cambiar `behavior/` ni `engine/` — no son mías y estamos a menos de
> dos horas del congelamiento. Esto documenta **por qué el modelo produce lo que produce**, para
> que nadie tenga que descubrirlo en vivo delante de un jurado.
>
> **Cómo se reproduce:** los comandos están al final. Todo sale de leer la caché, cero corridas
> nuevas, cero dólares.

## 0. La respuesta en una línea

**Los agentes no despiden porque no pueden pagar la indemnización, y no pueden despedir con
provecho porque el prompt les congela los ingresos.** El «cero despidos» no es un resultado del
modelo: es una consecuencia aritmética de dos frases del prompt.

## 1. Qué decidieron — el conteo completo

518 decisiones, agrupadas por `behavior/contrato.familia()`:

| Familia | n | % | ¿Mueve informalidad? | ¿Mueve empleo? |
|---|---:|---:|---|---|
| `informalizar` | 211 | 40,7% | **sí** ↑ | no |
| `subir_precios` | 140 | 27,0% | no | no |
| `absorber` | 124 | 23,9% | no | no |
| `bajar_horas` | 22 | 4,2% | no (jornada) | no |
| `cumplir` | 17 | 3,3% | **sí** → 0 | no |
| `renegociar` | 3 | 0,6% | no | no |
| **`despedir`** | **1** | **0,2%** | no | **sí** ↓ |

**1 de 518.** Ese único despido botó 17 trabajadores.

Las columnas de la derecha salen del `SUPUESTO:` explícito de `behavior/contrato.py:337`:
*«ninguna otra estrategia cambia el estatus de regla de la planta»*. Sumando:

> **El 51,5% de las decisiones no mueve ninguna de las dos cifras de portada.**
> `subir_precios` + `absorber` + `renegociar` dejan informalidad y empleo exactamente donde
> estaban. Solo el 48,4% hace algo que la pantalla pueda mostrar.

**Magnitudes declaradas** (cuando el campo viene con número, no `null`):

| Campo | n con valor | mín | mediana | máx |
|---|---:|---:|---:|---:|
| `empleados_a_informalizar` | 182 | 0 | 2 | 74 |
| `aumento_precios_pct` | 149 | 5,0 | 12 | 98,1 |
| `reduccion_margen_pct` | 126 | 5,0 | 8,5 | 100,0 |
| `reduccion_horas_pct` | 24 | 0 | 41 | 50,0 |
| `empleados_a_despedir` | 23 | 0 | **0** | 17 |

La mediana de `empleados_a_despedir` es **0** incluso entre los 23 que llenaron el campo.

## 2. LO IMPORTANTE — por qué no despiden

**47% de las justificaciones (242 de 518) mencionan el despido explícitamente y lo descartan.**
No lo ignoran: lo evalúan y lo botan. Y siempre por la misma razón.

> «Con caja casi nula (2.835.000u) que **ni alcanza para indemnizar a un trabajador**, y una
> probabilidad de inspección de apenas 1.1% […] conviene pasar al único trabajador formal
> restante a informal.»

> «Como ambos trabajadores ya están fuera de regla y **no tengo caja para indemnizar
> (3.733.280 u por trabajador supera mi flujo de 1.296.000 u)**, mantengo la operación informal
> actual.»

> «Con el 95% de la planta ya fuera de regla, **la caja no alcanza para indemnizar
> (3.849.945 u por trabajador contra 3.118.500 u disponibles)** ni para formalizar con el alza
> del 23%.»

> «…sin recurrir a despidos, y el riesgo esperado de sanción sigue siendo menor que el ahorro.»
> «…sin incurrir en **costos de despido que agotarían mi caja disponible**.»
> «…con caja limitada e **indemnización inalcanzable**.»

**El mecanismo, en cristiano:** el prompt le da a cada agente un `costo_despido` por trabajador
(`behavior/prompts/arquetipo.md:8`) y un tope duro de caja
(`behavior/prompts/sistema.md:24`: *«No puedes gastar plata que no tienes. Tu flujo de caja es un
tope duro»*). Despedir exige **desembolsar la indemnización hoy**. Informalizar cuesta **$0 hoy**
y solo arriesga una multa probabilística. **Despedir queda dominado por aritmética, no por
criterio moral ni por blandura del modelo.**

**La prueba está en el único que sí despidió.** Eligió 17 trabajadores, y su justificación dice
por qué exactamente 17:

> «Con la caja disponible **solo alcanza para indemnizar a 17 trabajadores
> (115.884.000 u / 6.766.570 u)**, reduciendo la nómina informal y así la exposición a la sanción
> esperada, ya que formalizar es inviable y seguir absorbiendo el costo total pondría en riesgo la
> caja frente a una probabilidad de inspección del 76,7%.»

Despidió **exactamente los que su caja alcanzaba a indemnizar**. La restricción de liquidez no es
un factor entre varios: es *la* variable que decide.

**70% de todas las justificaciones (361 de 518) invocan la caja o la liquidez.** Este modelo, en
la práctica, es un modelo de restricción de caja con una capa de riesgo encima.

> ### Y esto NO está mal del todo
> Que un alza del mínimo se pague en informalidad y no en despidos es coherente con la
> evidencia colombiana, y la indemnización del CST es un costo de caja real. **El resultado es
> defendible; lo que no es defendible es presentarlo como un descubrimiento del modelo**, porque
> las dos frases del §3 lo hacían inevitable antes de llamar al LLM.

## 3. LO IMPORTANTE — las dos frases del prompt que hacen irreal al empleador

### 3.1 Los ingresos están congelados por decreto

`behavior/prompts/arquetipo.md:12-14`:

> «El costo de mantener a un trabajador bajo contrato formal **sube {aumento_pct}%** a partir de
> este periodo. **Nada más cambia: tus ingresos, tus clientes y tu capacidad de producción son los
> mismos.**»

Con ingreso fijo y producción fija, **despedir solo destruye producto y encima cuesta plata**.
No existe ningún estado del mundo en el que despedir sea la mejor respuesta. El prompt refuerza el
cierre dos veces más (`sistema.md:25-26`): *«Despedir cuesta: hay una indemnización»* y *«No
puedes producir sin trabajadores: si te quedas sin gente, no hay ingreso»*.

**Tres candados en la misma dirección y ninguno en la contraria.** El empleador real de una PYME
bogotana enfrenta demanda que cae cuando sube precios, y despide precisamente porque le cayó la
venta. Este empleador no puede tener ese problema.

### 3.2 Subir precios es un almuerzo gratis

El menú ofrece `subir_precios` como *«Trasladas el costo a tus clientes»* (`sistema.md:45`), y el
mundo del prompt garantiza que **los clientes no se van**. Es una salida sin costo, y **140
agentes (27%) la tomaron** — con alzas declaradas de hasta 98,1%.

El propio código lo admite (`behavior/rondas.py:779`):

> «Su nombre honesto es *traslado declarado por las firmas*. **NO es inflación: no hay respuesta
> de demanda, no hay elasticidad**, y una firma que declara que subirá 10% puede no poder
> hacerlo.»

Cuatro justificaciones típicas, todas del mismo molde:

> «…informalizar es **económicamente suicida**, así que la respuesta óptima es trasladar el 23%
> de aumento del costo formal a los precios, manteniendo la planta formal intacta.»
> «…informalizar es **ruinoso**, y la caja no alcanza para absorber el 23%, así que traslado el
> sobrecosto vía precios sin comprometer el flujo de caja.»

**Consecuencia:** más de la cuarta parte de la población escapa de la política por una puerta que
no tiene costo y que **no mueve ninguna cifra del agregado**. La pantalla lo lee como
«adaptación»; el motor lo lee como nada.

### 3.3 La p(inspección) es un interruptor, no un riesgo

Extraído por regex del texto de 218 justificaciones que la citan (es lo que el agente **dice que
vio**, no el campo del motor — tratar como indicativo):

| | valor |
|---|---|
| mínimo | 0,0% |
| percentil 25 | 0,7% |
| **mediana** | **76,7%** |
| percentil 75 | 100,0% |
| máximo | 100,0% |
| casos en exactamente 100% | **73** |
| casos por debajo de 1% | **65** |

**No hay distribución: hay dos polos.** Y los agentes responden a ellos con una limpieza casi
mecánica:

| Familia elegida | n | mediana de p(inspección) que citan |
|---|---:|---:|
| `informalizar` | 93 | **0,3%** |
| `subir_precios` | 68 | **100,0%** |
| `absorber` | 43 | **100,0%** |
| `cumplir` | 8 | 100,0% |

**Los agentes son perfectamente racionales. El problema es el insumo.** Con p(inspección) ≈ 0,3%
informalizar es obvio; con p = 100% es suicida. Una probabilidad de inspección del **100%** no
existe en ningún régimen de fiscalización real, y es la que está empujando al 27% hacia la puerta
gratis del §3.2.

### 3.4 Toda empresa tiene el mismo colchón

`data/construir_empresas.py:70`, marcado `SUPUESTO:` y sin fuente:

> «margen operacional sobre la nómina […] La GEIH no lo observa y no hay fuente en el repo
> todavía. **0.18** se hereda del andamio de `behavior/`.»

Como despedir se decide **contra la caja** (§2), ese único número decide el resultado de las 518
decisiones. Es exactamente el fondo del hallazgo **B1** de la revisión a tres ejes.

## 4. Lo que el modelo inventó por su cuenta

**54 de 518 (10,4%) proponen un nombre fuera del menú de 8.** Es a propósito — el espacio es
abierto por diseño (`behavior/contrato.py:31`) — y `familia()` los reagrupa sin perder nada:

`mantener_informalidad` ×30 · `mantener_informalidad_total` ×15 · `formalizar_total` ×4 ·
`mantener_informal` ×2 · `formalizar_parcial` ×2 · `formalizar` ×1

**Ninguno cayó en el balde `otra`.** Es un punto a favor: el vocabulario abierto no rompió la
agregación, y el modelo no inventó ninguna estrategia genuinamente nueva.

## 5. Límite de este análisis

**La caché no sabe quién preguntó.** La clave es un `sha256` de
`{modelo, sistema, usuario, esquema}` (`behavior/cache.py:40`) y el archivo guarda solo
`{modelo, salida, usage}`. Por eso **este documento cuenta decisiones, no las atribuye a
empresas**: no se puede decir «los restaurantes hicieron X» sin volver a correr la simulación con
la caché caliente (que costaría $0, pero exige tocar código que no es mío).

## 6. Reproducir

```bash
# el conteo por familia
python3 -c "
import json,glob,sys,collections; sys.path.insert(0,'.')
from behavior.contrato import familia
S=[json.load(open(f))['salida'] for f in glob.glob('behavior/.cache/*.json')]
print(collections.Counter(familia(s['estrategia_propuesta']) for s in S).most_common())"

# las 242 justificaciones que evalúan y descartan el despido
python3 -c "
import json,glob,re
for f in sorted(glob.glob('behavior/.cache/*.json')):
    s=json.load(open(f))['salida']
    if re.search(r'despid|indemniz', s['justificacion'], re.I):
        print(f\"[{s['estrategia_propuesta']}] {s['justificacion']}\")"
```

## 7. Qué haría con esto (no lo decido yo)

1. **Decirlo antes de que lo pregunten.** Va en los límites declarados: *«el modelo no produce
   despidos porque la demanda es exógena y fija; el ajuste sale por informalidad, que es lo que
   la evidencia colombiana observa»*. Dicho por nosotros es rigor; encontrado por el jurado es
   humo.
2. **`subir_precios` necesita una etiqueta en pantalla.** Hoy se agrega junto a decisiones que sí
   mueven el mundo, y es la única que no le cuesta nada a nadie.
3. **La p(inspección) bimodal es de R2/R3.** No la toco. Pero es el insumo que más está moviendo
   el reparto de estrategias, más que el `aumento_pct`.
4. **Un informe por corrida** (`scripts/informe_decisiones.py` → `informes/`) que haga esto mismo
   **con atribución por empresa**. Es la herramienta que falta para no volver a discutir esto a
   ciegas. Corre con la caché caliente, cuesta $0, y no modifica cómo se calcula nada.
