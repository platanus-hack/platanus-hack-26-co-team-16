# Validación — ¿por qué creerle a esta simulación?

> **Esqueleto, sin llenar.** Dueño: Juanda (R5). El número existe en el checkpoint C5 (H+20 a H+26).
> **Regla del proyecto: el número se publica salga como salga.** Un backtest negativo pero medido y reportado con honestidad sigue siendo el resultado más serio de la sala, porque el resto va a presentar cifras que nadie puede refutar.
> Metodología completa: `docs/PLAN.md` §5.

## EL número

_PENDIENTE hasta C5._

```
Error del backtest:      ___
Varianza:                ___
Banda (p10 / p90):       ___
Corridas:                ___ (N≥5 paráfrasis del prompt)
```

Reproducible con: `make validate`

## Candado 1 · Calibración base

_PENDIENTE — el mundo corre SIN política y debe reproducir lo observado en la GEIH: informalidad por sector y tamaño de firma, distribución salarial, y el spike de masa salarial en el mínimo. Qué reprodujo y qué no._

### Objetivos de calibración con fuente (V8 — encontrado en H+1)

Los momentos contra los que se calibra no los escogemos nosotros: salen de literatura publicada y se citan acá antes de correr nada.

| Objetivo | Valor | Fuente | Uso |
|---|---|---|---|
| Elasticidad mínimo → informalidad | **+1 pp** en el ratio del mínimo ≈ **+0,21 pp** de probabilidad de empleo informal | Banco de la República, [WP 1104](https://ideas.repec.org/p/bdr/borrec/1104.html) — *Minimum wage effects on labour informality: heterogeneity across demographic groups in Colombia* | Nivel 2 de calibración. Si nuestra curva no pasa cerca de esta pendiente en el tramo bajo, algo está mal en el motor. |
| Heterogeneidad demográfica | Efecto concentrado en 18–25 años con menor educación | Misma fuente | Chequeo del mapa distributivo (dato A3): el efecto debe caer donde la literatura dice. |
| Informalidad de referencia — **la del candado 1** | **30,57%** (Bogotá, GEIH 2026 ene-jun, ponderada por factor de expansión) | `data/momentos.json`, calculado por `data/construir_poblacion.py` | Candado 1, nivel base. **Es el objetivo que el modelo tiene que reproducir en la ronda 0.** |
| Informalidad nacional de contexto | ~55–60% | Serie oficial DANE (✅ insumo jdtorres) · OIT | Solo contexto. **NO es comparable con la fila de arriba**: universo distinto (nacional vs Bogotá) y definición distinta (la nuestra usa proxy de cotización a seguridad social). Citar una donde va la otra es un error de 25 puntos. |
| Razón mínimo / salario mediano | ≈90% (Kaitz alto) | OIT | Contexto: explica por qué el mínimo colombiano muerde tanto. ⚠️ verificar cifra exacta y año antes de usarla en el pitch. |

**El matiz que importa para el pitch:** la elasticidad publicada es *una recta*. Nuestro aporte declarado (dato A2 del plan) es si existe un **codo** — un umbral donde la cascada se dispara y la recta deja de valer. Reproducir la recta en el tramo bajo es lo que nos da derecho a hablar del codo en el tramo alto.

## Candado 2 · Backtest fuera de muestra

_PENDIENTE — año de corte, alzas predichas, error publicado. **Se excluyen 2020-2021** (COVID rompe cualquier backtest laboral) y se dice explícitamente: eso suma credibilidad._

## Candado 3 · Control de contaminación de entrenamiento

_PENDIENTE — el doble mecanismo:_

**(a) Al modelo nunca se le nombra la política.** No ve "salario mínimo", ni "decreto", ni años. Solo la mecánica: *"tu costo laboral por empleado formal sube X%"*. Si el efecto agregado emerge igual, no es memoria.

**(b) Test de re-skinning.** La misma corrida con sectores y unidades renombrados a etiquetas inventadas debe dar el mismo agregado. Si difiere, hubo memorización, y lo reportamos nosotros antes de que lo pregunten.

_Resultado: PENDIENTE._

## Candado 4 · Ablación del LLM

_PENDIENTE — corrida con la capa conductual sustituida por reglas fijas. Si el resultado no cambia, el LLM no aporta y hay que decirlo. Si cambia, la diferencia ES el argumento de por qué el LLM se gana el puesto._

## Prueba opcional · Pico y placa

_PENDIENTE, condicionada a que C4 haya cerrado. A los agentes solo la mecánica ("no puedes usar tu vehículo 2 días a la semana"), jamás el nombre. Si emerge sola la estrategia "comprar un segundo carro barato", no es memoria. Corrida cualitativa: la salida es la decisión, no tiempos de viaje. Si no emerge, se reporta igual acá y no se menciona en el pitch._

## Método

- La barra de error se construye sobre **N≥5 paráfrasis del prompt**, no sobre temperatura.
- Se reporta **varianza además de media**: los LLM colapsan varianza, y lo decimos nosotros primero.
- **Ningún número sale sin banda.**

## Dónde NO hay que creerle

Los límites, escritos antes de que los pregunten. **No basta con decir "no lo
modelamos": hay que decir hacia dónde empuja la omisión.** Un límite con dirección
de sesgo es un dato sobre nuestro propio resultado; sin ella es una excusa.

| Lo que falta | Por qué no se agrega | **Hacia dónde sesga el resultado** |
|---|---|---|
| Productividad, demanda, capital, salario de eficiencia | Son piezas nuevas, no campos apagados: cero menciones en todo el código. El canal *"sube el mínimo → sube la productividad → baja el desempleo"* **no puede emerger** de este motor | Sin canales positivos, nuestra informalidad es una **cota superior** y nuestro empleo una **cota inferior**. Si el modelo se equivoca, se equivoca exagerando el daño |
| Tasa de desempleo | `data/momentos.json` solo trae ocupados: no hay fuerza laboral ni desocupados con los que construir el denominador | **No se reporta en ninguna forma.** Solo *empleo relativo a la línea base*. Decir "el desempleo sube a X%" sería sobreventa y es la palabra que más fácil nos hunde en el Q&A |
| Efecto faro sobre salarios informales | El alza solo encarece el lado formal; en la realidad los salarios informales cercanos al piso también suben | **Sobreestima la informalización**: si evadir también se encarece, evadir alivia menos de lo que decimos |
| Convergencia a equilibrio | Son 3 rondas de mejor respuesta (decisión D5), no una prueba de existencia de Nash | Se reporta como dinámica, nunca como equilibrio. Desde A5 además con la etiqueta de si la corrida **se estabilizó** o no |
| El despido como cálculo y no como muro | El agente propone y el motor veta; nunca compara "despedir vs. mantener" por costo esperado | Con A3 el agente al menos ve la caja correcta (la del periodo, la misma que juzga el veto). El mecanismo sigue siendo una restricción material, y así se dice |
| Traslado a precios como inflación | `traslado_precios_pct` es lo que las firmas **declaran** que trasladarían. No hay respuesta de demanda ni elasticidad | **No es un pronóstico de inflación.** Una firma que declara que subirá 10% puede no poder hacerlo. La cifra se publica con ese nombre pegado |
| Cuenta propia (23% de los ocupados) | `data/empresas.parquet` excluye a quien trabaja solo: no tiene a quién despedir ni a quién informalizar | El agregado cubre a los **3.235.639 ocupados con empleador**, no a los 4,2 millones. Se reporta aparte con su peso, en vez de dejar que el número se lea como si fuera toda la ciudad |
| El costo de la fiscalización sobre el Estado | Fuera de alcance declarado | Ninguno sobre las cifras publicadas |

### Dos parámetros que mueven el resultado y no tienen fuente

Se nombran acá porque son los que un juez debería atacar primero, y preferimos
señalarlos nosotros:

1. **El margen libre sobre nómina (0,18).** Es un supuesto heredado del andamio que
   `data/construir_empresas.py` declara como tal, con rango de barrido 0,05-0,40.
   Decide **dónde** cae el codo: con 0,18 y factor 1,40, absorber deja de ser
   pagable por encima de un alza de ~12,9%. Lo que el modelo dice es que **existe**
   un codo donde el margen libre se agota; **dónde** cae depende de un parámetro que
   no observamos, y por eso va con barrido y no con una cifra.
2. **La sanción equivalente a 12 meses de ingreso** (`multa_factor`). Decide si
   evadir paga. Su barrido es de R5.

### Lo que sí mejoró y cómo se verifica

- El **factor prestacional** ya no decide el signo del candado 4. Con la grilla real
  de empleadores —cada celda con su factor entre 1,3835 y 1,5829— el resultado es
  estable en todo el rango 1,35-1,58 (`python3 -m behavior.pruebas`, crítico #3).
  Antes se volteaba en 1,43, y esa fragilidad era el defecto §3.3.
- Los agentes dentro de un arquetipo se siguen suponiendo **intercambiables en su
  conducta** ([ADR 0002](docs/adr/0002-llm-por-arquetipo.md)). La heterogeneidad la
  pone la GEIH, no el LLM.

## Supuestos tomados

Todos los supuestos del código están marcados y son auditables:

```bash
grep -rnI --exclude-dir=__pycache__ "SUPUESTO:" engine behavior data api web scripts tests
# o, lo mismo con un nombre:  make supuestos
```

_Consolidar acá los que importan, con su impacto._

## Trabajo futuro (nombrado, no fingido)

- Refutación causal formal (DoWhy) — fuera de las 36 horas.
- Calibración bayesiana / MSM formal (`sbi`) — la calibración contra momentos cubre el nivel 1.
- Efecto faro y elasticidades de literatura como nivel 2 de calibración.
