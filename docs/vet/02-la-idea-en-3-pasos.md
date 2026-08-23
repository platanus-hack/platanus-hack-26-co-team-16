# La idea en tres pasos — el guion de la demo

Construido **solo sobre lo que sobrevive al backtest.** La cascada agregada no aparece como hallazgo
en ninguno de los tres pasos, porque está falsada.

El arco: **los datos son reales → el árbitro es duro → y aun así nos equivocamos, y lo medimos.**

---

## Paso 1 · La población no se inventa, y se prueba en veinte segundos

**Qué se ve.** Las 81 celdas de empleador apareciendo. Al pasar el mouse: cuántos trabajadores
representa, su salario mediano, su caja mensual, su costo de despido.

**Qué se dice.**
> "Nadie acá es un personaje. Son empleadores reconstruidos de los microdatos de la GEIH del DANE, y su
> costo laboral sale del Código Sustantivo del Trabajo, artículo por artículo, con la norma citada en el
> archivo."

**La prueba, y es la parte fuerte.** Nadie le dijo al pipeline cuál era el salario mínimo de cada año.
El pico del ingreso se movió solo: **1.300.000 → 1.420.000 → 1.750.000**, contra mínimos legales de
1.300.000 → 1.423.500 → 1.750.905. Tres años seguidos.

**Qué pregunta contesta:** *"¿cómo sé que esto no lo está inventando el modelo?"*, en la capa de datos,
antes de que la hagan.

---

## Paso 2 · El modelo propone, la aritmética manda ← **la pieza difícil**

**Qué se ve.** La corrida ronda a ronda. Cada celda decide, se prende su anillo, y en el hover aparece
qué propuso, qué le vetaron y por qué.

**Qué se dice.**
> "El espacio de estrategias es **abierto**: el agente propone lo que se le ocurra, no escoge de un menú.
> El veto es determinista y lo mide contra su propia caja: si no le alcanza para indemnizar, no puede
> despedir, por más que lo proponga. Y el veto **no lee nombres**, lee la aritmética."

**El detalle que remata:** a la política **jamás se le nombra**. El agente solo ve que su costo por
empleado formal sube X%. Nunca "salario mínimo", ni "decreto", ni un año. Hay una guardia que revisa cada
prompt antes de enviarlo, con 31 patrones, y un test que la corre contra todas las razones de veto.

**Qué pregunta contesta:** *"¿qué parte de esto es difícil?"* Un espacio de estrategias abierto con un
árbitro determinista que no se desincroniza. No es "integramos varias APIs".

---

## Paso 3 · Le pusimos número a nuestro propio error, y perdimos ← **el que gana**

**Qué se ve.** `make validate` corriendo en vivo, y el número saliendo.

**Qué se dice.**
> "Escribimos el criterio de éxito y lo commiteamos. **Dieciocho minutos después** bajamos los datos con
> los que se iba a juzgar. El modelo dice que la informalidad sube 33 puntos. Entre 2025 y 2026 bajó 4.
> Erramos **nueve veces más** que la predicción más tonta posible, que es decir 'el año que viene igual
> que este'. Está publicado en la línea 17 del `VALIDATION.md`, arriba de todo."

**Y de inmediato, sin que lo pregunten:**
> "Y el pre-registro **no fue ciego**: cuando fijamos el umbral ya sospechábamos hacia dónde iba. Está
> escrito en el mismo commit. Lo decimos nosotros porque es lo que hace que el resto sea creíble."

**El cierre.**
> "No traemos el futuro. Traemos el aparato que le pone un número a **qué tan equivocado está** un
> simulador de política pública. Lo primero que hizo fue refutarnos a nosotros. Casi ningún simulador de
> política del mundo puede hacerse esto a sí mismo, y ese es el punto."

**Qué pregunta contesta:** *"¿por qué debería creerte?"* Con el único movimiento que no se puede fingir.

---

## Lo que NO va en los tres pasos, y por qué

| Fuera | Por qué |
|---|---|
| La cascada de fiscalización como **hallazgo** | Falsada por el propio backtest. Sigue siendo el **mecanismo** del modelo y así se nombra, nunca como resultado |
| "Fuera de muestra de verdad" | El código lo contradice. Se retracta (decisión C1) |
| Cualquier proyección a futuro | El modelo perdió contra la persistencia. Afirmar futuro después de eso es insostenible |
| "Autómata celular" | Es refutable en el Q&A. Lo correcto es **función pura del estado**, y campo medio por el acoplamiento |
| "Aprende entre corridas" | No hay entrenamiento. **La caché es memoización, no aprendizaje** |

## La lámina de límites, que va ADENTRO del pitch y no en el Q&A

No modela productividad, ni demanda, ni capital, ni contrataciones. La tasa de desempleo no es
computable. Los cuenta propia (≈1/3 de Bogotá) están fuera de la grilla por construcción.
**Y la dirección del sesgo se publica:** sin canales positivos, nuestra informalidad es una **cota
superior**. Si nos equivocamos, nos equivocamos exagerando el daño.
