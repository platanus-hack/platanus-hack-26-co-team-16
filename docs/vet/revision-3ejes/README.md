# `docs/vet/revision-3ejes/` — el reparto de la revisión a tres ejes

> **Escrito el 23-ago 03:50 por Manuel (R2).** Toca `docs/vet/`, que es carpeta compartida:
> por eso todo entra en **subcarpeta nueva** y **no se editó ni un archivo existente**.
> Manda sobre el reparto de la revisión de la madrugada; no manda sobre el producto
> (eso sigue en `docs/PLAN.md`) ni sobre la validación (eso sigue en `VALIDATION.md`).

## Qué hay acá

| Archivo | Qué es | Quién lo usa |
|---|---|---|
| [`00-espina-paso0-BORRADOR.md`](00-espina-paso0-BORRADOR.md) | **La espina.** El problema que el proyecto dice resolver, como Paso 0. **Borrador, necesita 5 min del equipo.** Va destinado a pegarse arriba de `02-la-idea-en-3-pasos.md`, pero eso se hace en otro PR y con aviso | todos, primero |
| [`PROMPT-A-ejecucion.txt`](PROMPT-A-ejecucion.txt) | Prompt completo para `/juez-tecnico` | quien NO sea dueño de `engine/` ni `behavior/` |
| [`PROMPT-B-fundamentacion.txt`](PROMPT-B-fundamentacion.txt) | Prompt completo para `/juez-cientifico` | quien NO sea dueño de `data/` |
| [`PROMPT-C-pantalla.txt`](PROMPT-C-pantalla.txt) | Prompt completo para `/juez` apuntado a `web/` | quien NO sea dueño de `web/` |

**Los tres prompts son autocontenidos:** la espina va copiada adentro de cada uno, así que
funcionan aunque el Paso 0 nunca se apruebe. Se pega el contenido del archivo como argumento
del comando.

## En qué rama se corre esto: en ninguna

Las tres revisiones son **solo lectura** y las tres miden el **mismo árbol**, para que los tres
informes se puedan fusionar:

```bash
git fetch origin && git checkout main && git pull --ff-only && git rev-parse --short HEAD
```

Los arreglos que salgan los hace después el **dueño de cada carpeta**, en su rama de rol, por PR.

---

**Congelamiento: domingo 09:30.** Diseñado para caber en 45 minutos: 25 de revisión en paralelo + 20 de fusión.

## El error que este método existe para evitar

Tres revisiones independientes a las 4am producen **tres listas de quejas sin relación y cero
decisiones**. Por eso las tres miden contra el mismo documento, devuelven el mismo formato, y hay
una sola persona que fusiona.

## El orden, y no se puede invertir

1. **Primero la espina** ([`00-espina-paso0-BORRADOR.md`](00-espina-paso0-BORRADOR.md)). 10 minutos, la escribe una
   persona sola, el equipo la aprueba o la corrige en 5. Sin esto las tres revisiones no tienen
   contra qué medir y se vuelven opinión.
2. **Después las tres revisiones**, en paralelo, una por persona, cada una en su propia sesión.
3. **Al final la fusión**, una sola persona.

## Quién lanza qué

| Eje | Agente que ya existe en el repo | Quién lo lanza |
|---|---|---|
| **A · Ejecución** (¿la simulación hace lo que dice que hace?) | `/juez-tecnico` | el que NO es dueño de `engine/` ni `behavior/` |
| **B · Fundamentación** (¿es cierto?) | `/juez-cientifico` | el que NO es dueño de `data/` |
| **C · Pantalla** (¿la información que se muestra es la que sostiene la espina?) | `/juez` (juez-hackathon) apuntado a `web/` | el que NO es dueño de `web/` |

**No se construye un agente nuevo.** Los tres ya existen, ninguno tiene `Edit`, y a las 4am construir
un agente cuesta más de lo que ahorra. El prompt completo de cada eje está en esta carpeta y va como argumento del comando.

**Nadie revisa su propia carpeta.** Es la única regla del reparto que no se negocia: un revisor que
audita su propio código valida sus propios sesgos.

## El contrato de salida — idéntico para los tres

Cada revisión devuelve exactamente estos cinco bloques, en este orden, y nada más:

1. **MENTIRAS** — donde la capa afirma algo que la espina no sostiene. Con `archivo:línea`. Ordenadas
   por qué tan rápido las encuentra un juez.
2. **HUÉRFANOS** — lo que existe y no sirve a ningún paso de la espina. Candidato a **salir de la
   demo** (no del repo).
3. **FALTANTES** — lo que la espina promete y la capa no entrega.
4. **LOS 3 ARREGLOS** — máximo tres, ordenados por (impacto en la espina) ÷ (horas). Cada uno con:
   carpeta dueña · minutos estimados · **cómo se verifica que quedó**.
5. **LA PREGUNTA QUE NOS HUNDE** — la única pregunta de esa capa que hoy no se puede contestar.

Con los tres en el mismo formato, la fusión es mecánica.

## Reglas anti-enamoramiento

Van copiadas dentro de cada prompt, textuales:

- **Asume que el proyecto se está recortando.** Nombrar qué se borra es parte del trabajo, no una
  concesión. Una revisión sin lista de recortes es una revisión que no se hizo.
- **Evidencia o no existe.** Cada afirmación con `archivo:línea`, cifra de corrida, o comando. Marca
  cada hallazgo como `VERIFICADO` (lo corriste/leíste) o `SOSPECHA` (te huele).
- **Prohibido el elogio.** Nada de "el proyecto está sólido". No aporta y gasta el turno.
- **El backtest ya falsó la cascada agregada.** No es una hipótesis que revisar, es el punto de
  partida. Una revisión que la trate como hallazgo vivo está desactualizada.

## La fusión — 20 minutos, una sola persona

1. Pega los tres informes en un solo archivo.
2. **Lo que aparece en dos listas o más, va primero.** Un defecto que dos ejes ven por separado es
   estructural.
3. Suma los minutos de los 9 arreglos posibles. Corta donde se acabe el tiempo hasta 09:30 menos una
   hora de colchón.
4. **Regla dura del congelamiento: lo que no está en "LOS 3 ARREGLOS" de al menos un revisor, no se
   toca.** Todo lo demás pasa a una sección de límites declarados, que se dice en voz alta en el
   pitch en vez de arreglarse.
5. Las tres "PREGUNTAS QUE NOS HUNDEN" se contestan por escrito antes de la demo. Son el Q&A real.

## Si sobra tiempo

`/peeky` como cuarta pasada. No es un cuarto juez: no mide calidad, mide si el repo se contradice a
sí mismo. Es el que encuentra que `README.md` y `VALIDATION.md` afirman cosas distintas, que es
justo lo que un juez con un agente encuentra en 30 segundos.
