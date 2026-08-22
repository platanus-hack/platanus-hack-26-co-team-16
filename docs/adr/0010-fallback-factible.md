# ADR 0010 — El fallback deja de ser `cumplir` y pasa a ser la primera opción factible

**Estado:** propuesto (R3, con R2) · **Fecha:** 2026-08-22 · **Fuente:** A2 del [plan de correcciones](../agents/plan-correcciones-simulacion.md)

## Contexto

`docs/IDEA.md` §5.3 y §5.7 fijan la regla: *"hasta 3 reintentos; al agotarlos, la
estrategia terminal es `cumplir`"*. `engine/veto.py` la publica como
`ESTRATEGIA_TERMINAL` y `behavior/contrato.py` como `FALLBACK`. Esa constante fue,
además, el compromiso #2 del review del PR #4 —antes decía `absorber` y la
divergencia no era inocua—, así que cambiarla exige una ADR y no una decisión
suelta dentro de un commit.

El problema aparece con A1. Hasta A1, el veto revisaba dos estrategias —despedir e
informalizar— y dejaba pasar sin revisar las dos que cuestan plata: `cumplir` y
`absorber`. En ese mundo el fallback casi no se disparaba: en el barrido de 27
corridas del 2026-08-22 los fallbacks fueron **0**.

A1 cierra esa puerta y multiplica los vetos. Y ahí la regla vieja se vuelve un
problema serio: **manda a formalizarse —la jugada más cara de todas— a la firma que
acaba de demostrar tres veces seguidas que no puede pagar nada.** El signo invertido
que A1 corrige volvería a entrar por la puerta del fallback, y esta vez sin dejar
rastro en la lista de vetadas.

## Decisión

El fallback deja de ser una constante y pasa a ser **una búsqueda sobre un orden
canónico, arbitrada por el mismo veto** que rechazó las tres propuestas anteriores:

```
ORDEN_FALLBACK = ("cumplir", "bajar_horas", "absorber")
```

Se recorre en ese orden —de la más conservadora a la más barata— y se toma la
primera que el veto declare factible. `cumplir` sigue siendo el primer candidato,
así que **donde la firma puede pagar, el canon de `IDEA.md` se mantiene intacto**.

Si ninguna de las tres es factible, el agente **se queda exactamente como estaba**:
se emite `absorber`, que por construcción no cambia el estatus de regla de la planta
(`contrato.fraccion_fuera_de_regla` devuelve la fracción previa), y la decisión sale
marcada con `sin_salida=True`.

## Por qué `sin_salida` se publica y no se esconde

Una firma sin ninguna opción factible **no es un error del programa**: es el modelo
diciendo que la política es impagable para esa celda con cualquier jugada
disponible. Se cuenta por ronda y se imprime.

El plan de correcciones fija además el umbral de alarma **antes** de correr: si los
fallbacks superan el **5% de las decisiones**, la corrida lo reporta y eso es un
hallazgo publicable, no algo que se ajusta hasta que desaparezca.

## Alternativas descartadas

| Alternativa | Por qué no |
|---|---|
| **Dejar `cumplir` fijo** | Reintroduce la formalización gratis que A1 existe para cerrar, y encima la vuelve invisible: el fallback no aparece en la lista de vetadas |
| **Poner `absorber` fijo** | Es el error que el review del PR #4 ya corrigió: para una unidad informal `absorber` puntúa 1,0 fuera de regla y `cumplir` 0,0, así que motor y capa reportarían tasas distintas con las mismas decisiones |
| **Dejar que el LLM reintente sin límite** | Sin techo de reintentos el costo por corrida deja de ser acotable, y el corte duro de presupuesto es una restricción no-negociable del repo |
| **Que el veto proponga la alternativa** | Le daría al motor una función de política —decidir qué conviene— que por diseño es de la capa conductual. El motor veta, no aconseja |

## Consecuencias

- `behavior/contrato.decision_fallback()` recibe ahora `veto` y `arquetipo`. Sin
  ellos conserva el comportamiento viejo, para no romper los dobles de prueba.
- `ResultadoArquetipo` gana el contador `sin_salida`, que sube hasta el agregado.
- `engine/veto.ESTRATEGIA_TERMINAL` deja de describir la regla completa: pasa a ser
  el **primer candidato** del orden. Se documenta en el propio módulo.
- Aparece un supuesto nuevo y explícito: `REDUCCION_HORAS_FALLBACK = 20%`, la
  jornada que se recorta cuando `bajar_horas` es la opción que sobrevive. Dirección
  conocida: un valor más alto abarata más y por lo tanto **baja** los `sin_salida`.

## Cómo se falsa

Si con A1 y A2 puestos los `sin_salida` superan el 5% de las decisiones, la lectura
correcta **no** es que el fallback esté mal: es que el 0,18 de margen sobre nómina
—supuesto sin fuente heredado del andamio de `data/`— está apretando de más. Se
revisa ese parámetro con su barrido antes de tocar esta ADR.
