# `10-fusion.md` — la lista de corte de la revisión a tres ejes

> **Esqueleto creado el 23-ago 04:29 por Manuel (R2), con el Eje A ya pegado.**
> Este archivo NO es el informe de ningún agente: los tres informes viven en
> `docs/agents/<agente>/` y son la fuente. **Esto es la decisión del equipo** sobre qué se
> arregla antes del congelamiento y qué se dice en voz alta en vez de arreglarse.
>
> Manda sobre el corte de la madrugada. No manda sobre el producto (`docs/PLAN.md`) ni sobre
> la validación (`VALIDATION.md`). Las reglas de fusión están copiadas abajo, así que este
> archivo se puede usar sin volver al [`README.md`](README.md).

## Reloj

| Hito | Hora |
|---|---|
| Congelamiento del repo | **domingo 09:30** |
| Colchón obligatorio | 1 hora |
| **Corte real: nada nuevo empieza después de** | **08:30** |

## Estado de los tres informes

Un eje sin informe no se espera: se marca como **NO ENTREGADO** y la fusión sale con dos.
Un informe tarde vale cero.

| Eje | Agente | Ruta del informe | Estado |
|---|---|---|---|
| **A · Ejecución** | `juez-tecnico` | [`docs/agents/juez-tecnico/2026-08-23-0402-eje-A-ejecucion.md`](../../agents/juez-tecnico/2026-08-23-0402-eje-A-ejecucion.md) | ✅ **ENTREGADO** 04:02 · sin segunda opinión · 4 hallazgos verificados a mano |
| **B · Fundamentación** | `juez-cientifico` | `docs/agents/juez-cientifico/2026-08-23-HHMM-eje-B-fundamentacion.md` | ⬜ pendiente |
| **C · Pantalla** | `juez-hackathon` | `docs/agents/juez-hackathon/2026-08-23-HHMM-eje-C-pantalla.md` | ⬜ pendiente |

> ⚠️ **Trampa de nombres en la carpeta C.** `docs/agents/juez-hackathon/` ya tiene un
> `2026-08-23-0009-repo.md` que es de las 00:09 y es modo `repo`, **no** el Eje C. Que el
> informe del Eje C diga `eje-C-pantalla` en el nombre para que a las 8am nadie fusione el
> archivo equivocado.

---

## §1 · Los 9 arreglos posibles

Tres por eje, como pide el contrato de salida. Se llena pegando el bloque 4 de cada informe.

| # | Arreglo | Carpeta dueña | Min | Cómo se verifica | SI NO LO ARREGLAMOS |
|---|---|---|---|---|---|
| **A1** | Deploy apunta a `main` (o declarar qué commit está vivo) | Juanda (R5) | 15 | `curl` SSE ronda 0 del deploy == `make reproduce` local | El juez clona, corre, le salen otros números y deja de creer el 37,37 pp |
| **A2** | `make run` que corra + `cache-demo.json` exportado | Juanda (R5) + Nico (R3) | 40 | `make run` ×2 con `diff` vacío; G1 deja de estar bloqueado | Los dos primeros comandos del README fallan delante del jurado |
| **A3** | Cap de gasto acumulado + caché caliente | Manuel (R2) + Nico (R3) | 30 | `fin` trae gasto acumulado; `python3 -m behavior.cache` muestra entradas Sonnet | El juez espera minutos sin saber si se colgó, y el clic nº9 quema los USD 50 |
| **B1** | _(pegar del bloque 4 del informe B)_ | | | | |
| **B2** | | | | | |
| **B3** | | | | | |
| **C1** | _(pegar del bloque 4 del informe C)_ | | | | |
| **C2** | | | | | |
| **C3** | | | | | |

---

## §2 · Lo que aparece en dos ejes o más — VA PRIMERO

**La regla:** un defecto que dos revisores ven por separado, mirando capas distintas, no es una
opinión. Es estructural. Estos se ordenan arriba de todo, sin importar sus minutos.

Se llena al final, cruzando los bloques MENTIRAS / HUÉRFANOS / FALTANTES de los tres informes.

| Defecto | Ejes que lo vieron | Evidencia de cada uno | Arreglo asociado |
|---|---|---|---|
| _(vacío hasta tener B y C)_ | | | |

**Candidatos que el Eje A ya dejó servidos.** Si B o C tocan lo mismo, suben a la tabla de arriba:

- **La brecha deploy ↔ `main`** (A · M1). Si el Eje C mira `web/` contra el link desplegado, va a
  chocar con esto por su lado.
- **El fallback produce el agregado, no el veto:** `fraccion_fallback = 69,1%`,
  `fraccion_sin_salida = 63,0%` contra el umbral de alarma de 5% del propio equipo (A · M6).
  Toca la espina de frente: *"un LLM propone, un árbitro determinista veta"*. **Este es el que
  hay que buscar en el informe B**, porque si el Eje B lo confirma por el lado de la
  fundamentación, es el hallazgo #1 de toda la revisión.
- **Las rondas 2 y 3 no mueven nada** (A · M5): informalidad 24,06% idéntica a 4 decimales en
  las tres rondas. Si el Eje C encuentra que la pantalla igual anima tres rondas, es mentira en
  dos capas.

---

## §3 · El corte

**Regla dura del congelamiento:** lo que no está en "LOS 3 ARREGLOS" de al menos un revisor,
**no se toca**. Sin excepciones y sin "es que son dos minutos". Todo lo demás baja al §4.

### Suma global — lo que pide el `README.md`

| Con los 3 ejes | Minutos |
|---|---|
| Eje A (A1+A2+A3) | 85 |
| Eje B | _pendiente_ |
| Eje C | _pendiente_ |
| **Total** | **85 + B + C** |

### Suma por dueño — el número que de verdad manda

La suma global engaña: los arreglos los hacen personas distintas **en paralelo**, pero una
persona no puede hacer dos a la vez. El cuello de botella es el dueño más cargado, no el total.

| Dueño | Arreglos que le tocan | Min acumulados |
|---|---|---|
| Juanda (R5) | A1, A2 | 55 |
| Nico (R3) | A2, A3 | 70 |
| Manuel (R2) | A3 | 30 |
| Alejo (R1) | — | 0 |
| Dani (R4) | — | 0 |

> Añadido operativo de este archivo, no un cambio a la regla del reparto. La regla sigue siendo
> la suma global; esta tabla es el chequeo de realidad de si cabe.

### Lo que entra

1. _(vacío hasta cortar)_

### Lo que NO entra, y por qué

1. _(vacío hasta cortar)_

---

## §4 · Límites declarados — lo que se dice en voz alta en vez de arreglarse

No es la lista de la vergüenza. Es la lista que **se dice antes de que la pregunten**, que es la
diferencia entre un límite y un hallazgo del jurado.

- _(se llena al cortar, con todo lo que quedó fuera del §3)_

**Ya declarados por el Eje A, fuera de sus 3 arreglos:**

- `api/servidor.py:200-201` cae a corrida en frío **en silencio** cuando falta
  `behavior/cache-demo.json`; `scripts/reproduce.py:70-72` sí lo anuncia. El camino silencioso
  es el que el juez clickea. Dueño: Manuel (R2).
- `engine/seed.py` (315 líneas con test) no tiene un solo consumidor fuera de su propio test.
- Las 503 entradas de caché son **todas Haiku**, cero Sonnet.
- La higiene filtra términos, no magnitudes: `"2.500.000 u"` + 23% pasa el filtro. `[SOSPECHA]`
  del Eje A, sin verificar.

---

## §5 · Las tres preguntas que nos hunden — el Q&A real

Se contestan **por escrito antes de la demo**. Una pregunta sin respuesta escrita es una pregunta
que se contesta improvisando delante del jurado.

### A · Ejecución

> **"Muéstrame ahora, en el link, una corrida en modo LLM con la banda de 5 trayectorias.
> ¿Cuánto tardó, cuánto costó y qué fracción de tus agentes se quedó sin ninguna opción
> factible?"**

**Respuesta:** _(pendiente de escribir)_

### B · Fundamentación

> _(pegar del bloque 5 del informe B)_

**Respuesta:** _(pendiente)_

### C · Pantalla

> _(pegar del bloque 5 del informe C)_

**Respuesta:** _(pendiente)_

---

## Cómo se fusiona — el procedimiento, copiado del `README.md`

1. Pegar el bloque 4 de cada informe en la tabla del §1.
2. Cruzar MENTIRAS / HUÉRFANOS / FALTANTES de los tres. **Lo que aparece en dos listas o más
   sube al §2 y va primero.**
3. Sumar minutos. Cortar en 08:30, mirando la tabla por dueño y no solo el total.
4. Lo que no entró y no está en ningún "LOS 3 ARREGLOS" baja al §4 como límite declarado.
5. Contestar las tres preguntas del §5 por escrito.

**Una sola persona fusiona.** Dos personas fusionando en paralelo producen dos listas de corte
distintas, que es peor que no tener ninguna.
