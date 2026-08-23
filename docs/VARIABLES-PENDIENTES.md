# Variables que no estamos midiendo (y por qué importan)

> **Qué es esto:** una lista de variables que hoy el modelo no registra y que, si se pudieran registrar, mejorarían mucho lo que podemos concluir y lo que podemos mostrar.
> **Qué NO es:** un requerimiento para esta iteración. Es una consulta de viabilidad.
> **Lo que pedimos:** por cada punto, un veredicto — *ya existe* / *barato de agregar* / *caro* / *imposible sin rediseñar* — más una estimación gruesa de esfuerzo.
> **Origen:** revisión del frontend (rol interfaz). No proponemos cambios a la lógica del motor; solo preguntamos qué se puede **registrar y exponer** de lo que el motor ya hace.

---

## A. Variables por agente

### A1 · Exposición al mínimo (*bite* / índice de Kaitz)
**Qué es:** qué fracción de la nómina de cada empresa está en el salario mínimo o muy cerca de él.
**Por qué importa:** es la variable que explica *por qué cae quien cae*. Dos empresas del mismo sector y tamaño reciben golpes radicalmente distintos si una tiene el 90% de su nómina en el mínimo y la otra el 10%. Sin esto, el resultado se puede describir pero no explicar, y en el Q&A "¿por qué esta empresa se informalizó y esta no?" no tiene respuesta.
**Qué desbloquea:** el hover de la interfaz podría mostrar la causa real; y permitiría ordenar los resultados por exposición en vez de por sector.
**Sospecha:** los datos de la GEIH deberían permitir calcularla al construir la población. ¿Es así?

### A2 · Colchón financiero
**Qué es:** cuánto puede absorber una empresa antes de que la estrategia "cumplir" deje de ser viable.
**Por qué importa:** el veto de factibilidad ya usa algo así ("flujo de caja insuficiente"). Si ya se calcula internamente, exponerlo debería ser casi gratis y da una segunda dimensión de vulnerabilidad además del tamaño.

### A3 · Intensidad laboral
**Qué es:** qué proporción de los costos totales de la empresa es nómina.
**Por qué importa:** un alza del costo laboral golpea distinto a un restaurante que a una empresa de capital intensivo. Explica heterogeneidad que hoy queda invisible.

### A4 · Capacidad de trasladar a precios
**Qué es:** si el sector puede subir precios o no (transable vs. no transable).
**Por qué importa:** es probablemente el determinante más fuerte entre "absorber" y "despedir", y hoy no lo distinguimos.

### A5 · Tramo de edad de los trabajadores
**Qué es:** composición etaria por empresa, si la GEIH lo permite.
**Por qué importa:** es la única vía para observar el efecto sobre empleo juvenil, que es uno de los efectos contraintuitivos que nos interesan.

---

## B. Registros de proceso (no son variables nuevas, son cosas que pasan y no se anotan)

### B1 · Tamaño de cada cascada
**Qué es:** cada vez que una empresa se informaliza o despide, cuántos trabajadores (ponderados) arrastra ese evento.
**Por qué importa:** es la medición de mayor valor científico de toda la lista. Con el histograma de estos tamaños se puede mostrar si el sistema produce muchos eventos pequeños y pocos enormes — la firma de un sistema en estado crítico. Es un resultado, no una ilustración.
**Costo esperado:** parece ser solo *anotar* algo que ya ocurre. ¿Lo es?

### B2 · Orden de caída
**Qué es:** en qué ronda cae cada tipo de empresa.
**Por qué importa:** responde "¿quién cae primero?", que es la pregunta política.

### B3 · Propuestas vetadas por ronda
**Qué es:** cuántas propuestas del LLM rechaza el motor en cada ronda.
**Por qué importa:** ya se calcula y ya se ve en pantalla, pero no se guarda como serie. Es evidencia directa de que el veto de factibilidad hace algo — uno de nuestros argumentos centrales.

### B4 · Rondas hasta estabilizar
**Qué es:** si el resultado converge o no, y en cuántas rondas.
**Por qué importa:** hoy la interfaz muestra "no estabilizada" sin poder decir cuánto faltaría.

---

## C. Nivel de método (afecta lo que podemos afirmar)

### C1 · Barrido de política
Correr el modelo en todo el rango de alzas (0–25%) en vez de un solo valor, para graficar el resultado contra el parámetro. Sin esto tenemos un punto, no una curva; y el hallazgo interesante (dónde se quiebra el sistema) vive en la curva.

### C2 · Ensemble de corridas
Correr la misma configuración N veces para reportar un rango en vez de una línea. Hoy la interfaz muestra literalmente *"banda degenerada: una sola trayectoria"*. Es la respuesta a "¿y si corre otra vez, da lo mismo?".

### C3 · Aleatorización de parámetros (Monte Carlo / sensibilidad)
Perturbar los parámetros supuestos y ver cómo se distribuyen los resultados. Además de dar bandas de confianza, dice **cuál parámetro manda** — y eso sí es una conclusión de política pública.

---

## Preguntas concretas para el agente de backend

1. De A1 a A5: ¿cuáles ya existen o son derivables de `poblacion.parquet` sin tocar el motor?
2. De B1 a B4: ¿cuáles son solo "anotar y serializar" y cuáles exigen cambiar el bucle de rondas?
3. ¿Qué habría que agregar al contrato `ronda.json` para que estos datos lleguen al frontend, sin romper los campos existentes?
4. De C1 a C3: costo aproximado en tiempo de cómputo y en presupuesto de LLM. ¿Cuáles caben antes de la entrega y cuáles quedan como trabajo futuro declarado?
5. Si solo pudiéramos hacer **una** cosa de toda esta lista, ¿cuál da más valor por esfuerzo?
