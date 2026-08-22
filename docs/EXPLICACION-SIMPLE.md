# Explicado simple

> Todo el proyecto, sin jerga. Si algo de acá no se entiende, es culpa del texto.
> La versión completa está en [`IDEA.md`](IDEA.md).

---

# Parte 1 · La promesa y el producto

## El problema, con un salón de clase

El gobierno subió el salario mínimo un 23% y dijo: *"ahora 2,4 millones de personas van a
ganar más"*.

Eso es como que el profesor diga: **"nueva regla, todos tienen que compartir el almuerzo"**,
y después escriba en el tablero *"listo, ya todos comparten"*.

Pero nadie contó cuántos niños **de verdad** comparten.

Toda cuenta oficial da por hecho que **la gente cumple**. Ese supuesto nunca se mide. Y en un
país donde más o menos la mitad de la gente trabaja sin contrato, ese supuesto es justo el que
decide si la política funciona o no.

## Qué hacemos

Una máquina que responde una pregunta distinta. No *"¿la política es buena?"* sino:

> **"¿Cuánta gente la va a cumplir de verdad, y a quién le va a doler?"**

Funciona así, en cuatro pasos:

**1. No inventamos gente.** Agarramos personas reales de una encuesta gigante del DANE (sin
nombres, sin poder saber quién es quién). Cada una viene con lo suyo: cuánto gana, en qué
trabaja, si tiene contrato, hasta dónde estudió. Como sacar fichas de una caja de verdad en
vez de dibujarlas.

**2. Les preguntamos qué harían.** A los jefes, que son los que deciden. Una inteligencia
artificial propone: *"despido a uno"*, *"lo dejo sin contrato"*, *"me aguanto y gano menos"*.

**3. Una calculadora dice qué es posible.** Acá está el truco. La IA es como un niño con mucha
imaginación: puede decir *"me compro un helicóptero"*. La calculadora es el adulto que abre la
billetera y dice *"no te alcanza"*. **La IA propone, la calculadora manda.** Solo lo que pasa
los dos filtros cuenta.

**4. Preguntamos otra vez.** Porque la gente ve qué hicieron los demás y cambia de opinión.
Preguntamos tres veces, cada tres meses.

## El truco que nadie más ve

Este es el corazón. Presta atención acá.

Imagina que hay **un solo profesor** cuidando el recreo.

- Si **un** niño se cuela en la fila, lo pillan seguro.
- Si se cuelan **cincuenta**, el profesor no alcanza y casi nadie se pilla.

Entonces colarse se vuelve más barato. Y como es más barato, **se cuelan más todavía**. Y como
se cuelan más, el profesor alcanza aún menos.

**El profesor no se multiplica.** Los inspectores de trabajo en Colombia son 1.300 para todo
el país, y no aparecen 1.300 más porque la gente evada más.

A esa bola de nieve la llamamos **la cascada**, y es lo que la cuenta oficial no ve: ellos
dibujan una línea recta, nosotros mostramos dónde la línea se despega.

## Lo que ves en la pantalla

Una sola perilla: **cuánto sube el sueldo**. La mueves y aparecen:

- 📈 **La línea del gobierno contra lo que de verdad pasa.** La distancia entre las dos **es
  el producto entero**.
- 🗺️ **Un mapa de a quién le duele**, por tipo de trabajo y de ingreso.
- 📰 Las decisiones apareciendo en vivo, y tres o cuatro historias con cara.

Sin registrarse, sin cuenta, sin pagar. Abres el link y funciona.

## ¿Por qué creernos?

La pregunta correcta, y tenemos cuatro respuestas.

**1. Le pedimos que adivine el pasado.** Hubo como veinte subidas del salario mínimo antes.
Le tapamos el resultado y le pedimos que adivine. Después publicamos **en cuánto se
equivocó**, aunque quede feo. Es como un examen del que ya existe la respuesta correcta pero
el que responde no la vio.

**2. Nunca le decimos el nombre.** A la IA jamás le decimos *"salario mínimo"* ni *"decreto"*
ni el año. Solo le decimos: *"te subió el costo de cada empleado un X%"*. ¿Por qué? Porque si
le decimos el nombre, **puede estar acordándose en vez de pensando** — como preguntarle una
adivinanza a alguien que ya la escuchó. Si el resultado sale igual sin el nombre, no fue
memoria.

**3. Le quitamos la IA y volvemos a correr.** Si sale lo mismo sin IA, entonces la IA no
estaba haciendo nada, y **preferimos descubrirlo nosotros** antes que un juez.

**4. Nunca damos un número pelado.** Siempre un rango. Un número solito, sin decir cuánto te
puedes equivocar, es una mentira con decimales.

## Lo que NO hacemos

- **No adivinamos el futuro.** Damos un rango y decimos de qué tamaño es nuestro error.
- **No decimos si la política es buena o mala.** Mostramos qué pasa; opinar es de otros.
- **No servimos para todo.** Sirve para políticas donde **incumplir es una opción** que la
  gente puede pagar o no. No sirve para trancones ni para epidemias: eso es otra máquina.
- **No reemplazamos al DANE ni a los economistas.** Somos **el primer paso barato**: te
  mostramos cuál pregunta vale la pena estudiar en serio.

---

# Parte 2 · Por qué esto está bien construido

Lo mismo, pero contando de dónde sacamos cada pieza. **Casi nada lo inventamos nosotros**, y
eso es a propósito: es más creíble pararse sobre cosas que ya se probaron.

## La idea de "¿me conviene hacer trampa?" tiene 50 años

En **1972**, dos señores (Allingham y Sandmo) escribieron cómo decide alguien si hace trampa
con los impuestos. Es una cuenta simple:

> **Lo que me ahorro haciendo trampa, contra lo que pierdo si me pillan × qué tan probable es
> que me pillen.**

Eso es todo. Es el papá de toda esta literatura y lo copiamos tal cual.

## Nosotros cambiamos UNA sola cosa (y ahí está todo el proyecto)

Ellos suponen que **"qué tan probable es que me pillen" es un número fijo**. Siempre el mismo.

Nosotros **lo dejamos moverse**, porque el profesor del recreo es uno solo:

```
más gente evadiendo  →  menos probable que te pillen a ti
                     →  evadir sale más barato
                     →  más gente evadiendo   ↺
```

**Ese único cambio es la tesis del proyecto.** Todo lo demás es infraestructura.

Y no nos lo inventamos: hay estudios publicados donde modelos de este tipo, cuando la
probabilidad se mueve, producen **umbrales** — puntos donde todo se desbarata de golpe. Por
eso buscamos "el codo": el punto donde subir un poquito más rompe todo.

## La cuenta exacta, para que no sea un número mágico

Si hay `C` inspecciones repartidas al azar entre `E` evasores, la probabilidad de que te caiga
al menos una es:

```
p = 1 − e^(−C/E)
```

Suena feo, pero es **el problema de repartir caramelos entre niños** de toda la vida. Y lo
importante es que se porta bien:

- Nunca da más de 100% (la versión simple sí se pasaba, y eso es un error).
- Si hay muchos evasores, tiende a cero. Correcto.
- Si hay uno solo, tiende a uno. Correcto.
- **Y cuando hay pocos inspectores y muchos evasores, que es la vida real, da casi lo mismo
  que la versión simple.** O sea: no cambiamos el modelo, lo escribimos bien.

`C` sale de un dato real: **1.300 inspectores de trabajo en Colombia** (dato de la OIT). No de
un número que nos gustó.

## De dónde sale cada pieza

| La pieza | De dónde | Qué cambiamos |
|---|---|---|
| Decidir si evadir | Allingham y Sandmo, 1972 | Nada |
| Que la probabilidad se mueva | Nuestro cambio, apoyado en literatura de evasión | **Todo el proyecto está acá** |
| Que la gente sea real | Encuesta del DANE | Nadie más usa una encuesta nacional para esto |
| Que jefe y trabajador decidan distinto | Literatura de empleo formal/informal en América Latina | El jefe usa IA, el trabajador usa calculadora |
| Cómo escribir el modelo para que otro lo pueda revisar | Protocolo ODD, el estándar del área | Lo seguimos tal cual |
| Cuánto detalle meter | Un método de 2005 (*Pattern-Oriented Modeling*) | Regla: solo el detalle que hace falta para que el modelo copie **varias** cosas del mundo real a la vez |

**Ninguna pieza es nueva por separado. La combinación sí:** gente real de una encuesta
nacional + la probabilidad que se mueve + la calculadora que veta + nunca nombrar la política
+ el error publicado, todo dentro de algo que un desconocido abre sin registrarse.

## Dos detalles de ingeniería que importan más de lo que parecen

**El reloj.** Cada ronda son **tres meses**, porque así se publica la encuesta y porque un jefe
no cambia contratos en una semana. Sin reloj, decir "el efecto" no significa nada: ¿a los tres
meses? ¿a los dos años? Nuestra respuesta se mide **a nueve meses**, y lo escribimos **antes**
de ver el resultado para que no parezca escogido después.

**La semilla.** El programa usa una "semilla" — un número que decide todos los azares. Misma
semilla, mismo resultado, siempre. Así cualquiera puede correrlo y obtener exactamente lo
mismo que nosotros. Es lo que separa un experimento de una anécdota.

## Lo que decimos en voz alta antes de que nos pregunten

- Son **tres rondas**, no un final. No decimos que el mundo "se estabiliza" ahí, porque no lo
  sabemos.
- Los agentes **no aprenden ni adivinan el futuro**: reaccionan a lo que ya pasó.
- Hay cosas que suponemos sin dato duro. Están **marcadas una por una en el código** y se
  listan con un comando. Cualquiera puede ver de qué no estamos seguros.
- Nuestra cascada probablemente es **un poco más grande que la real**, porque no contamos
  algunos costos de ser informal (perder crédito, perder clientes). **Sabemos hacia dónde nos
  equivocamos**, y lo decimos.
