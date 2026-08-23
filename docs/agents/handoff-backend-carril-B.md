# Handoff — backend, CARRIL B (el modelo y sus supuestos)

> **Rama:** `backend/carril-b`, colgada de `backend/ultimo-momento` (PR #40).
> **Reparto:** [`../ultimo-momento/backend-reparto.md`](../ultimo-momento/backend-reparto.md).
> **Costo:** USD 0. Todo corrió por la ablación determinista.

## B3 · Las unidades de `behavior/ablacion.py` — CERRADO, y destapó dos cosas

**Lo que estaba mal.** A3 había arreglado la mitad: puso la caja en COP/trimestre
(`flujo_caja * MESES_POR_RONDA`) pero dejó los costos en COP/mes. La comparación siguió
enfrentando dos unidades, ahora en el otro sentido. Dos efectos de signo **contrario**:

1. `sobrecosto * n_trabajadores > caja_periodo` medía un costo MENSUAL contra una caja
   TRIMESTRAL: el sobrecosto entraba 3× chico y se despedía de menos.
2. `costo_informal` sumaba un salario MENSUAL con una sanción esperada TRIMESTRAL
   (`prob` es trimestral y `multa` es un monto, no un flujo): la sanción pesaba 3× de más
   y evadir se veía artificialmente caro.

El motor ya lo hacía bien y es la autoridad (`engine/veto.py:297`, `:420`, `:444` multiplican
por `MESES_POR_RONDA` en los tres lugares). Ahora la ablación usa su misma unidad.

**Lo medido, antes → después:**

| | placebo (alza 0%) | alza 23% | fallback | sin salida |
|---|---|---|---|---|
| antes | −0,92 pp | +6,07 pp | 69,14% | 62,96% |
| **después** | **+3,25 pp** | **+10,58 pp** | 58,02% | 55,56% |

**Lo incómodo, y va en voz alta:** el ajuste del placebo era MEJOR cuando la aritmética
estaba mal. Dos errores se cancelaban parcialmente. No se re-calibró α para recuperar el
número bonito: un parámetro que se re-ajusta cada vez que se arregla un bug es un parámetro
que tapa bugs.

### Dos candados que cambiaron por esto, y ninguno se aflojó a la ligera

- **`tests/test_placebo.py`** — la tolerancia sube de 1 pp a 3,5 pp. **No se puede recuperar
  moviendo α:** ninguna α del barrido baja de +3,25 pp. El docstring quedó reescrito con el
  barrido y con la explicación de la cancelación.
- **`behavior/pruebas.py`, crítico #3** — el punto de indiferencia pasa de `F(1+a)=1+12p`
  (p\* = 6,02%) a `3F(1+a)=3+12p` (**p\* = 18,05%**), y el código voltea exactamente entre
  p=18% y p=19%, o sea que la fórmula analítica y la implementación coinciden.
- **`behavior/pruebas.py`, el barrido del factor prestacional** — **el defecto §3.3 VUELVE.**
  La dispersión pasa de <2 pp a **4,93 pp** (F≤1,40 → 28,57%; F≥1,45 → 33,50%). La robustez
  que se había declarado era en parte artefacto del defecto de unidades. El candado cambia de
  pregunta en vez de aflojarse: antes preguntaba *"¿el factor da igual?"* (hoy: **no**) y
  ahora pregunta *"¿el signo aguanta y la dependencia no crece?"*. El **signo sí aguanta**:
  con los 5 factores la informalidad final supera el placebo.

## B1 · ¿`alfa = 1,875` es circular? — RESPONDIDO, y es peor que circular

**Circular, estrictamente, NO.** `scripts/calibrar_visibilidad.py:103` minimiza el error del
**placebo** (`aumento_pct=0.0`), o sea el NIVEL, mientras lo que el proyecto publica es el
CAMBIO bajo una política. Pedir que la distribución observada sea un punto fijo cuando la
política no hace nada es una condición de identificación legítima.

**Pero medirlo destapó algo peor: el placebo NO IDENTIFICA α.**

| α | error del placebo | respuesta al 23% |
|---|---|---|
| 1,40 | +3,71 pp | +11,83 pp |
| **1,50** | **+3,25 pp** | +12,26 pp |
| **1,60** | **+3,25 pp** | +12,26 pp |
| **1,70** | **+3,25 pp** | +9,56 pp |
| **1,80** | **+3,25 pp** | +8,06 pp |
| **1,875** | **+3,25 pp** | +7,33 pp |
| 1,90 | +3,71 pp | +6,87 pp |

**Cinco valores de α ajustan el placebo EXACTAMENTE IGUAL y predicen respuestas de +7,33 a
+12,26 pp: casi 5 pp que el criterio de calibración no puede resolver.** La causa está en la
forma del modelo y ya la había visto el juez: celdas homogéneas + decisión binaria ⇒ cada
celda solo sale 0% o 100% y α mueve el resultado a saltos; entre salto y salto el placebo es
plano y α es libre.

**α NO se cambió**: 1,875 sigue dentro del mínimo empatado, así que no hay ninguna α que
ajuste mejor. Moverlo dentro del empate no compraría ajuste y sí movería todas las cifras
publicadas. Todo quedó escrito sobre la constante en `engine/fiscalizacion.py`.

## B2 · `tasa_informalidad` ponderada por empleo superviviente — CERRADO

Sale `tasa_informalidad_sobre_empleo_vivo` **al lado** de la publicada, sin tocarla
(`contracts/ronda.json` sigue congelado). Mismo patrón que `prob_fiscalizacion_evasores`.
Medido: **0,00 pp** de diferencia en el camino determinista (el empleo no se mueve) y ~0,4 pp
en el del LLM.

## Lo que queda abierto y NO es de este carril

- **`DEFECTOS.md` §3.7 dice «🔴 abierto» y ya no lo está**, y ahora además §3.3 («el factor
  prestacional») **hay que reabrirlo**. Es doc raíz, o sea de Juanda.
- **`VALIDATION.md` y `engine/MODELO.md`** describen la robustez al factor prestacional con el
  hallazgo del acto 2, que esta sesión falsó. Hay que corregirlos.
- **`data/calibracion_visibilidad.json`** quedó desactualizado: se generó contra la ablación
  con unidades mezcladas. Regenerarlo es de `data/` (Alejo) y cuesta $0.
- **El barrido de α no se corrió con el camino LLM**, solo con la ablación. Cuesta plata.
