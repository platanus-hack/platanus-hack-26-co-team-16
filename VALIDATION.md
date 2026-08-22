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
| Informalidad de referencia | ~55–60% | Serie oficial DANE (✅ insumo jdtorres) · OIT | Candado 1, nivel base. |
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

_PENDIENTE — los límites, escritos antes de que los pregunten:_

- Es **dinámica de mejor respuesta a 3 rondas**, no convergencia a equilibrio ni prueba de existencia de Nash.
- **No es un modelo macro**: inflación, crecimiento y tasa de cambio son exógenos observados.
- El **factor prestacional** es un parámetro (rango ≈1,4-1,5) con análisis de sensibilidad, no un dato exacto.
- Los agentes dentro de un arquetipo se suponen **intercambiables en su conducta** (consecuencia de [ADR 0002](docs/adr/0002-llm-por-arquetipo.md)).
- _Qué reproduce bien el modelo y en qué segmentos falla: PENDIENTE tras C5._

## Supuestos tomados

Todos los supuestos del código están marcados y son auditables:

```bash
grep -rn "SUPUESTO:" .
```

_Consolidar acá los que importan, con su impacto._

## Trabajo futuro (nombrado, no fingido)

- Refutación causal formal (DoWhy) — fuera de las 36 horas.
- Calibración bayesiana / MSM formal (`sbi`) — la calibración contra momentos cubre el nivel 1.
- Efecto faro y elasticidades de literatura como nivel 2 de calibración.
