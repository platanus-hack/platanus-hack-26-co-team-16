# Diseño de la interfaz — decisiones y su porqué

**Dueño: Dani (R4)** · rama `rol/interfaz`

Este documento existe para que nadie (ni un agente de código, ni yo dentro de 20 horas)
tenga que readivinar por qué la pantalla se ve como se ve. Las decisiones de abajo
están tomadas; cambiarlas es posible, pero requiere leer el porqué primero.

## El proceso, en cuatro etapas

| Etapa | Qué es | Estado |
|---|---|---|
| 1 · Sistema visual | Definir cómo se ve cada momento | **Fusionada con la 2.** Se descartó Claude Design: la pieza es movimiento y densidad, y un artboard estático no puede juzgar ninguna de las dos |
| 2 · Prototipo de movimiento | `web/prototipo/mapa.html` — un archivo, cero dependencias, datos falsos. Responde "¿se siente bien?" | **Hecho** |
| 3 · Producto real | Next.js en `web/`, contra `contracts/ronda.json`, luego Supabase Realtime | Pendiente |
| 4 · Escenarios precomputados | Lo que el pitch muestra carga instantáneo, sin esperar una corrida | Pendiente |

El prototipo **no es el producto**: es la especificación del producto en forma
ejecutable. Se puede tirar a la basura sin costo, y por eso es donde toca equivocarse.

## Las decisiones

### La unidad visual es una celda de 1.000 personas, no una persona

El problema: el proyecto entero se vende sobre *"no inventamos a nadie, son personas
reales del DANE"*, y **la GEIH no georreferencia dentro de la ciudad**. Pintar un punto
por persona en una localidad sería inventar el dato justo en la pantalla que el jurado
mira, y el agente del juez lo detecta abriendo `poblacion.parquet` y no encontrando la
columna.

La solución: el punto es una **celda de población**, y una celda no tiene dirección.
El territorio se organiza por **sector económico** —que sí es un atributo observado—
y la pantalla lo dice en un rótulo permanente.

- 4.500 celdas × 1.000 personas. `SUPUESTO:` el orden de magnitud de ocupados en
  Bogotá (~4,5M) **está sin verificar** — pendiente confirmarlo con Alejo contra la GEIH.
- 4.500 es la cifra que hace que se lea como territorio y no como diagrama de dispersión.
  A 10.000 personas por celda quedaban ~450 puntos: muy pocos.

### El color mide el incumplimiento NUEVO, no la informalidad total

Es la decisión más importante del diseño y salió de una medición, no de una intuición.
Pintando informalidad total, el mapa arranca con ~570 celdas ya rojas: el 42% de
informalidad **existe antes de la política**. Eso arruina la narrativa y responde la
pregunta equivocada.

El color mide cuánto se movió cada celda **por culpa del aumento**. Resultado:

| Momento | Celdas que cruzan el umbral |
|---|---|
| Reposo | 0 |
| Ronda 0 — el escenario sin adaptación | **0** |
| Ronda 1 | 992.000 personas |
| Ronda 2 | 1.422.000 |
| Ronda 3 | **1.598.000** |

El contador demuestra el codo solo: a 7% no cruza nadie, a 13,6% cruzan 527.000, a 23%
cruzan 1,6 millones. Ese salto **es** el dato A2.

### El contorno de Bogotá no se dibuja: emerge

Nada de un panel oscuro con borde. Cada celda deposita un halo gris suave en una capa
de densidad, los halos se suman, y la silueta aparece sola por acumulación. La
saturación es automática: sumar alfas bajas tiende a opaco de forma asintótica, así que
nunca hay un corte brusco.

El mismo campo sirve para el daño: cuando las celdas viran, el halo vira con ellas, y
el incumplimiento deja de ser un puntico de color para volverse **una zona que se enciende**.

`SUPUESTO:` la silueta es un polígono dibujado a mano, aproximado. Ninguna conclusión
del modelo depende de su forma. Reemplazable por el Marco Geoestadístico del DANE.

### La cascada se propaga por presión económica, no por cercanía

Tentación evidente: que el rojo se expanda como un contagio desde un foco. Sería
mentira — el modelo no tiene contagio espacial. En cambio, el orden en que caen las
celdas lo da su **presión económica** (informalidad base del sector + tramo de ingreso).
Se ve igual de vivo y además el orden significa algo.

### Fondo claro, color solo funcional

Interfaz casi monocromática: papel blanco, grises, y **un único color saturado que es
el daño**. Nada de paleta de dashboard. La tipografía de la narración es serif
(editorial, seria); la de los datos es sans con cifras tabulares.

### La entrada se ve como una frase, funciona como un parámetro

*"Si el salario mínimo sube [23,0 %], ¿cuánta gente cumple de verdad?"* — el número se
arrastra y se edita, con el slider debajo.

Se descartó el campo de texto libre: el motor recibe una política estructurada, nadie
tiene asignado interpretar lenguaje natural, y abriría la puerta a que alguien escriba
"simula una epidemia" y el sistema falle en público, contra `docs/PLAN.md` §4.2.

### Vocabulario

El de `docs/agents/context.md`, sin excepciones: **brecha, cascada, el codo, arquetipo,
veto, mejor respuesta**. Nunca "equilibrio", nunca "convergencia".

## Tokens (los valores congelados del prototipo)

```
--halo: #6b7280      --dano: #bf3b2b      --oficial: #9aa0a6
--halo-op: 0.30      --dano-op: 0.62      --halo-r: 17
--celda-r: 1.7       --umbral: 0.60
--dur-ronda: 1500ms  --stagger: 0.55
```

Se afinan en vivo abriendo el prototipo con `?tune`. El panel escupe la línea de tokens
lista para pegar aquí. **Cuando se congelen para el producto, se actualizan acá.**

## Cada elemento contra los cuatro datos (`PLAN.md` §1.1)

| Dato | Elemento | Dónde |
|---|---|---|
| A1 — cuánta gente cumple | El contador de celdas que cruzaron el umbral + la cifra de la brecha | Prototipo ✅ |
| A2 — dónde está el codo | La curva de la brecha + el barrido de aumento con el codo marcado | Prototipo ✅ |
| A3 — a quién le cae encima | El mapa por sector, con banda p10–p90 en la curva | Parcial: falta el corte explícito sector × tramo de ingreso |
| A4 — por qué evade cada quien | Desglose de estrategias por ronda | Prototipo ✅ (con datos falsos) |
| (vida) | Historia con cara | Prototipo ✅ (una, ilustrativa) |

Falta y va en la etapa 3: el feed Realtime de decisiones y el corte distributivo
sector × ingreso como vista propia.

## Descartado explícitamente

- **3D y mapas con tiles.** No suman y cuestan horas.
- **WebGL.** Canvas 2D en dos capas basta a 4.500 celdas; WebGL sería complejidad sin retorno.
- **Física de partículas.** Bonito, no significa nada.
- **Texto libre como entrada.** Ver arriba.
- **Millones de puntos.** La escala se afirma con el factor de expansión de la GEIH, no con el runtime.
- **Auth, registro, onboarding.** Link → pantalla → slider.

## Lo que el prototipo todavía no prueba

Se verificó la lógica y el rendimiento del cálculo en Node (400 fotogramas de datos en
214 ms, sin excepciones). **No se pudo medir el costo real de dibujado** porque no había
navegador automatizable en la sesión. Si al abrirlo se cae de 60fps, la salida es bajar
la frecuencia de repintado del campo de densidad —no cambiar de tecnología.
