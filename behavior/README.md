# `behavior/` — Capa conductual (LLM)

**Dueño: Nico (R3)** · rama `rol/conductual`

Descubre estrategias de adaptación que un economista no habría enumerado.
Propone; no aplica nada.

## Cómo verificarlo tú mismo

| Comando | Qué hace |
|---|---|
| `python3 -m behavior.higiene` | Escanea los prompts y falla si alguno nombra la política |
| `python3 -m behavior.demo` | Corrida completa de 4 rondas con reglas fijas — sin API key, $0 |
| `python3 -m behavior.demo --barrido` | Barre 7 / 13,6 / 23 / 30% para buscar el codo |
| `python3 -m behavior.demo --llm` | La capa LLM real (necesita credenciales) |
| `python3 -m behavior.cache` | Estado del caché en disco |

## La regla de oro

**Al LLM jamás se le nombra la política.** Ni "salario mínimo", ni "decreto", ni
años. Solo la mecánica: *"tu costo laboral por empleado formal sube X%"*. Es el
control de contaminación de entrenamiento y sostiene la mitad del argumento de
validación. Un prompt que la viole invalida la corrida.

Eso no es una promesa, es un candado: `behavior/higiene.py` tiene la lista negra
y **todo prompt pasa por `verificar()` antes de salir hacia la API**, sin bandera
para desactivarlo. Si algo se filtra, la corrida revienta en vez de producir un
número contaminado.

Fuimos más lejos de lo que pide el plan: los prompts tampoco nombran el país, la
ciudad, la moneda ni el año. Los montos van en **unidades (u)** abstractas. Eso
hace que el test de re-skinning (candado 3b) sea casi gratis: ya no hay etiqueta
real que renombrar.

Los prompts son legibles en [`behavior/prompts/`](prompts/) — `sistema.md` es el
contexto del mundo, `arquetipo.md` la plantilla por grupo, y `parafrasis/` las 5
variantes con las que se construye la barra de error.

## Verificación V10 — AgentTorch (`docs/PLAN.md` §6)

**Veredicto: se adopta la idea, no la dependencia.** El muestreo por arquetipos
está implementado a mano en [`arquetipos.py`](arquetipos.py) (~50 líneas), como
el plan ya anticipaba en §4.1.

Qué se abrió: [`AgentTorch/AgentTorch`](https://github.com/AgentTorch/AgentTorch),
`agent_torch/core/llm/archetype.py` y `behavior.py`.

**Sí tiene lo que buscábamos.** `Archetype`, `LLMArchetype` y `Behavior.sample()`
hacen exactamente el patrón de D4: se prompta a arquetipos representativos y los
agentes individuales muestrean de la distribución resultante. Nuestra decisión
D4 no era original, y eso es bueno: hay prior art y lo citamos.

**Aun así no entra, por cuatro razones concretas:**

1. **Licencia — es el bloqueo duro.** AgentTorch es **AGPL-3.0**. Nuestro repo es
   MIT y tiene que serlo (repo público, entregable del hackathon). Importar
   código AGPL a un proyecto MIT es un conflicto de licencia, no una molestia de
   ingeniería. Esto solo ya cierra la discusión.
2. **Forma equivocada de la salida.** Su `Behavior.sample()` promedia salidas
   **float** entre arquetipos: está hecho para una variable conductual escalar
   (p. ej. "número de viajes"). Lo nuestro es una **estrategia categórica** con
   veto de factibilidad y reintento. No es el mismo objeto.
3. **Acoplamiento.** Arrastra PyTorch más su `PromptManager`, su
   `LoadPopulation` y su sistema de `registry`/`substep`. Para usar 50 líneas
   habría que adoptar su runtime completo.
4. **No trae lo que de verdad nos cuesta.** No tiene veto de factibilidad, ni
   caché por hash de prompt, ni tope de presupuesto. Esas tres son el trabajo
   real de esta carpeta y las escribimos igual.

**Lo que sí tomamos:** la idea y la cita. Va al README como prior art, junto al
paper de *Large Population Models*, y es la línea para el Q&A: *"leímos
AgentTorch, adoptamos su patrón de arquetipos y decidimos no importar su runtime
— la licencia es incompatible con MIT y su muestreo es escalar, no categórico"*.

## Arquitectura

```
prompts/         los prompts, visibles y auditables
higiene.py       la lista negra + el candado que revienta la corrida
arquetipos.py    definición de arquetipos + muestreo determinista (reemplaza AgentTorch)
contrato.py      contracts/decision.json: construir, validar, fallback
cliente.py       API: ruteo de modelo, prompt caching, caché en disco, presupuesto
cache.py         caché en disco por hash del prompt
presupuesto.py   tope duro por corrida
capa.py          propuesta -> veto -> reintento (máx 3) -> fallback 'absorber'
rondas.py        el bucle de 4 rondas de mejor respuesta
ablacion.py      la misma corrida con reglas fijas (candado 4 de validación)
demo.py          corrida punta a punta sin motor y sin API key
```

El ciclo, que es la tesis del proyecto:

```
propuesta del LLM  ->  veto del motor  ->  ¿factible?
                                           sí -> entra al agregado de la ronda
                                           no -> reintento CON LA RAZÓN encima
                                                 (máximo 3, luego 'absorber')
```

`ablacion.py` es un reemplazo directo de `cliente.py`: misma firma de
`proponer()`, así que la corrida con LLM y la corrida con reglas fijas comparten
`capa.py` y `rondas.py` sin cambiar una línea. La diferencia entre las dos ES el
candado 4.

## Costo

48 arquetipos × 4 rondas = **192 llamadas** por corrida (dentro del rango de
~250 que estima el plan). Con Haiku 4.5 a ~900 tokens de entrada y ~120 de
salida:

| Corrida | Llamadas | Costo estimado |
|---|---|---|
| Normal (1 paráfrasis) | 192 | **~$0,29** |
| Con banda de error (5 paráfrasis) | 960 | **~$1,44** |
| Repetición con caché poblado | 0 | **~$0,00** |

Tope duro por corrida: **$3,00** (`presupuesto.TOPE_POR_DEFECTO_USD`). Al
llegar, la corrida se para.

⚠️ **Estos son estimados, no medidos** — todavía no se ha hecho ninguna llamada
real (ver *Lo que falta*). El costo real va acá en cuanto haya credenciales.

**Sobre el prompt caching de la API:** está cableado, pero el mínimo cacheable
de Haiku 4.5 es de 4096 tokens y nuestro prefijo estable es más corto, así que
probablemente **no** cachee. Se deja porque es gratis y se mide en
`usage.cache_read_input_tokens`. La palanca real de costo es el caché en disco.
Preferimos decirlo a que el juez lo descubra.

## Hallazgos que afectan a otros roles

**1. Con reglas fijas no hay cascada — hay un escalón.** En la ablación, la
informalidad se queda plana en todo el barrido (7 / 13,6 / 23 / 30%). La razón
no es un bug: en un maximizador simple el umbral de evadir es *"sobrecosto >
sanción esperada"*, y como ambos lados escalan con el ingreso, **el umbral es
idéntico para todos los arquetipos**. O cruzan todos o no cruza ninguno.

La retroalimentación sí funciona — forzando la sanción cerca del umbral se ve
50% → 100% con la probabilidad de sanción cayendo de 4,8% a 2,0% — pero es un
escalón, no una curva con codo.

**Consecuencia:** el **codo (dato A2) no puede salir de una regla fija.** Necesita
heterogeneidad en el *umbral*, no solo en los niveles. Eso lo puede dar la
población real de Alejo (márgenes y tamaños que no escalan proporcionalmente) o
el espacio de estrategias abierto del LLM. Es una buena noticia para el candado
4: si el codo aparece con LLM y no con reglas, esa diferencia es exactamente el
argumento de por qué la capa conductual se gana el puesto.

**2. `contracts/decision.json` todavía no existe en disco.** `contrato.py` valida
contra el ejemplo de `docs/PLAN.md` §4 embebido, y prefiere el archivo apenas
aparezca. Alejo/Manuel: al crearlo, `behavior/` lo toma solo.

**3. Los prompts no usan pesos colombianos.** Si el motor o el frontend esperan
COP en el texto que ve el agente, no lo van a encontrar: adentro todo es
"unidades". La conversión es responsabilidad del motor.

## Lo que falta

- [ ] **Una sola llamada real a la API.** Todo el camino LLM está escrito pero
      **nunca se ha ejecutado contra la API** (esta sesión no tenía credenciales).
      Es lo primero que hay que hacer cuando haya key.
- [ ] Congelar `contracts/decision.json` con Manuel (H+4) y enchufar el veto real.
- [ ] Reemplazar `arquetipos_falsos()` por `desde_poblacion()` cuando Alejo
      entregue `data/poblacion.parquet` (H+8–14). El código ya está escrito.
- [ ] Medir el costo real por corrida y reemplazar los estimados de arriba.
- [ ] Test de pico y placa (§5.5), solo si el checkpoint C4 cerró.

## Qué NO va aquí

- Aplicar decisiones al estado del mundo (eso lo hace `engine/`).
- Nada de `web/`, `data/` ni `engine/`.
