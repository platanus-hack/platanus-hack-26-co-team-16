# ADR 0005 — El reloj de la simulación: una ronda es un trimestre

**Estado:** aceptado (R2, dueño de `engine/`) · **Fecha:** 2026-08-22 · **Fuente:** hueco H1 · **Supera:** nada, llena un vacío

## Contexto

Ni `docs/PLAN.md`, ni `docs/UML.md`, ni `docs/FLUJO.md` dicen **cuánto tiempo dura una
ronda**. `MotorEquilibrio` tiene `max_rondas = 4` y `Ronda` tiene métricas, pero no existe
`t` en ninguna parte del modelo.

Eso no es un detalle: sin reloj, **el candado 2 de validación no se puede puntuar**. El
backtest consiste en predecir el efecto de un alza histórica del salario mínimo, y "el
efecto" solo significa algo con una fecha de medición. ¿La informalidad a los tres meses del
decreto? ¿A los doce? Sin responder eso, `empleo_relativo` es un número sin unidades y el
error del backtest no se puede comparar contra nada.

## Decisión

**Una ronda = un trimestre.** El calendario de una corrida es:

| Ronda | Momento | Qué representa |
|---|---|---|
| 0 | `t = 0`, el decreto (enero) | La reacción ingenua: **la proyección oficial**, que asume cumplimiento total |
| 1 | primer trimestre | Primera mejor respuesta, viendo el agregado de la ronda 0 |
| 2 | segundo trimestre | Segunda mejor respuesta |
| 3 | tercer trimestre | Tercera. **Es la ronda que se reporta** |

**El horizonte de la corrida es de 9 meses**, dentro del mismo año calendario del decreto, y
esa es la ventana contra la que se mide el backtest.

Tres razones, en orden de peso:

1. **Es el reloj de los datos.** La GEIH se publica en trimestres móviles. Si el modelo
   corre en trimestres, el backtest compara lo mismo contra lo mismo sin interpolar nada.
   Un modelo mensual obligaría a inventar una desagregación que la encuesta no da, y eso es
   exactamente el tipo de número inventado que el proyecto prohíbe.
2. **Es el reloj de la decisión que modelamos.** Cambiar la forma de contratación
   (informalizar, despedir, renegociar) tiene ciclos de nómina y plazos legales. El
   trimestre es el período más corto en el que una firma puede plausiblemente completar una.
3. **Deja la ventana dentro del año del decreto**, que es donde vive la controversia pública
   y donde hay dato observado para contrastar.

## Alternativas descartadas

| Alternativa | Por qué no |
|---|---|
| **Ronda = un mes** | Más rápido de lo que una firma puede cambiar contratos, y la GEIH mensual es más ruidosa. Ganaríamos resolución falsa. |
| **Ronda = un año** | Con 3-4 rondas el horizonte sería de 3-4 años, fuera de la ventana del decreto, y la cascada dejaría de ser un fenómeno de corto plazo para convertirse en una proyección de largo plazo que no podemos defender (`PLAN.md` D8: no somos un modelo macro). |
| **Dejar la ronda abstracta, sin tiempo** (el statu quo) | Es lo que rompe el backtest. Además convierte "3 rondas de mejor respuesta" en una frase sin contenido empírico. |
| **Que el usuario elija el Δt** | Una perilla más que ajustar hasta que salga el resultado bonito. Va contra el principio de que nada se ajusta a mano para producir la cascada. |

## Consecuencias

- `Ronda` gana un campo de tiempo explícito, y `contracts/ronda.json` también. Es un cambio
  aditivo al contrato: **avisar a Dani (R4) y a Alejo (R1) en el próximo standup.**
- El backtest mide a 9 meses del decreto. Se escribe así en `VALIDATION.md` **antes** de
  conocer el resultado, para que no parezca escogido después.
- La probabilidad de sanción se expresa **por trimestre**, no por año. Toda cifra de
  capacidad de inspección tomada de una fuente anual hay que convertirla, y la conversión
  queda marcada con `# SUPUESTO:` porque la inspección no se reparte uniforme en el año.
- Si el equipo decide otra ventana, cambia **un parámetro**, no el motor. El reloj está
  centralizado a propósito.
