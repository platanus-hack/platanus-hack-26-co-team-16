# EL ENJAMBRE, simulador de cumplimiento de política pública

**No responde si una política funciona, sino cuánta gente la cumple y a quién le cae encima.**

🔗 **[enjambre-web.onrender.com](https://enjambre-web.onrender.com)**, sin registro, sin cuenta, sin instalar nada.

Toda proyección oficial de una política laboral asume que la política se cumple. Ese supuesto es el
que nadie mide. Nosotros lo simulamos: qué hace cada tipo de empleador cuando su costo laboral sube,
y qué pasa con la probabilidad de que lo sancionen cuando el de al lado también incumple.

**Caso demo:** el aumento del salario mínimo colombiano del 23% (decretos 1469 y 1470 de 2025), sobre
el mercado laboral de Bogotá. Es el primer caso que corre el motor, no el único que puede correr: la
misma mecánica sirve para cualquier política que cambie costos o incentivos, y esa generalización es
justamente hacia donde va el proyecto.

## La población no se inventa

Los agentes se instancian desde **6.692 personas reales anonimizadas de los microdatos de la GEIH del
DANE**, expandidas por factor de encuesta a 4,2 millones de ocupados. Sector, tamaño de empresa,
ingreso, educación e informalidad vienen en la misma fila de la encuesta: las correlaciones entre
atributos son las observadas, no las que un modelo de lenguaje considere plausibles. El lado
empleador son 81 celdas con su costo formal, su factor prestacional y su indemnización calculados
contra el Código Sustantivo del Trabajo.

## El LLM propone y la aritmética manda

Una capa LLM descubre estrategias de adaptación (informalizar, recortar jornada, despedir,
absorber) en vez de escogerlas de un menú que escribió un economista. Después, un motor determinista
con seed calcula el flujo de caja de la firma y **veta** lo que es materialmente imposible: una
empresa sin caja para pagar indemnizaciones no puede despedir, por convincente que suene la
justificación. En casi toda simulación con agentes LLM el modelo también juzga; acá solo propone.

## Al modelo jamás se le nombra la política

No ve "salario mínimo", ni "decreto", ni un año: solo la mecánica (*"tu costo laboral por empleado
formal sube X%"*). Una guardia revisa **cada** prompt antes de enviarlo y aborta la corrida entera si
encuentra un término prohibido, un símbolo de moneda o un año de cuatro dígitos. Es fail-closed: no
filtra, aborta. Si el agregado emerge igual sin el nombre, no es memoria del modelo, es mecánica.

## La fiscalización es endógena, y ahí está el mecanismo

La capacidad de inspección laboral es **fija**, derivada de la cifra de inspectores de la OIT, así
que cada evasor adicional diluye la probabilidad de que la sanción te caiga a ti. Las decisiones
individuales se vuelven una **cascada** que el modelo oficial, que asume cumplimiento, no puede ver.
Ese es el corazón del aporte: un mecanismo que ninguna proyección oficial pone sobre la mesa.

## El número, con el método escrito de antemano

Escribimos los criterios de éxito **antes** de tener los datos, en un commit fechado y verificable
(`git log --date=iso -- VALIDATION.md`). Después corrimos el backtest fuera de muestra sobre el
episodio real de 2025 a 2026.

El modelo entrega una conclusión propia y en una dirección nítida: bajo las condiciones que sí
modela (el margen de formal a informal entre quienes ya tienen empleador, con el resto de la economía
tomado como dato), un alza fuerte del costo laboral **empuja la informalidad hacia arriba**. Ese
incremento aparece de forma consistente entre corridas y sale con su banda de incertidumbre, nunca
como cifra suelta.

No lo calzamos a la fuerza contra la cifra oficial del episodio, y es una decisión deliberada. Las
series oficiales colombianas de informalidad tienen problemas de medición conocidos y el propio DANE
las revisa hacia atrás, así que no funcionan como patrón de oro contra el cual calificar un modelo.
El proyecto reporta su propia mecánica y su propio número, con banda, y acota el claim al margen de
formal a informal dentro de quienes ya tienen empleador. Los factores que este primer caso todavía no
incorpora (la reforma laboral, la jornada de 42 horas, el ciclo) quedan nombrados como límite
declarado, no escondidos.

## Hacia dónde va

Lo que hoy es alcance acotado ya está escrito como hoja de ruta, no improvisado:

- **De una política a todas.** Hoy corre el salario mínimo; la misma arquitectura sirve para
  cualquier política monetaria o laboral que cambie costos o incentivos. Es el siguiente paso
  natural del motor.
- **Del empleo que cae al empleo que se mueve.** Sumar contrataciones, productividad, demanda y
  precios endógenos, hoy tomados como dato exógeno.
- **De la grilla a la ciudad entera.** Incorporar a los trabajadores por cuenta propia, que son el
  23% de los ocupados de Bogotá.
- **De 3 rondas a la convergencia.** Extender la dinámica de mejor respuesta y estudiar el
  equilibrio.
- **Del punto de partida.** Arrancar de la población previa a la política, con el criterio ya
  pre-comprometido por escrito.

## Cómo verificarlo sin creernos

```bash
make test        # el núcleo determinista
make validate    # los 4 candados e imprime EL número
make supuestos   # cada supuesto marcado en el punto donde se toma
```

Mismo seed, mismo resultado. Repo público, licencia MIT, y `grep -rn "SUPUESTO:"` es el informe de
honestidad del proyecto.
