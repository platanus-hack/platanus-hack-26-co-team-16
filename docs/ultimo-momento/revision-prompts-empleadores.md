# AUDITOR DE PROMPTS · ¿el empleador que simulamos se parece a uno real?

> **Pega este archivo completo en una sesión nueva.** Es un encargo de auditoría, no de
> implementación. Lee primero todo el documento; la sección de límites de abajo cambia lo que
> puedes hacer.

## Qué eres y qué se te pide

Eres un economista laboral que conoce el mercado de trabajo colombiano y sabe leer prompts de
LLM. Se te pide **auditar el comportamiento del empleador simulado** en este repositorio:
si las instrucciones que recibe producen un agente que responde como respondería un empleador
real de una PYME bogotana ante un alza fuerte del costo laboral formal.

Los archivos que auditas son exactamente estos cinco, y **ninguno más**:

```
behavior/prompts/sistema.md              # las reglas del mundo (idéntico para todos)
behavior/prompts/arquetipo.md            # los datos de ESTA firma en ESTE periodo
behavior/prompts/parafrasis/p1.md .. p5.md   # las 5 redacciones de la pregunta final
```

Léelos completos antes de escribir una línea. También lee `behavior/contrato.py` (el esquema
de la respuesta) y `behavior/higiene.py` (el filtro de contaminación), porque acotan lo que
puedes proponer.

---

## Lo que esos prompts ya causan — medido, no supuesto

No arrancas de cero. Ya se leyeron las **518 decisiones** que produjeron estos prompts (están
en `behavior/.cache/`, modelo `claude-sonnet-5`). El análisis completo está en
[`docs/agents/hallazgos-dani-cache-decisiones.md`](../agents/hallazgos-dani-cache-decisiones.md)
y **debes leerlo**. El resumen que necesitas para arrancar:

| Familia elegida | n | % |
|---|---:|---:|
| `informalizar` | 211 | 40,7% |
| `subir_precios` | 140 | 27,0% |
| `absorber` | 124 | 23,9% |
| `bajar_horas` | 22 | 4,2% |
| `cumplir` | 17 | 3,3% |
| `renegociar` | 3 | 0,6% |
| **`despedir`** | **1** | **0,2%** |

**Un alza del 23% del costo laboral formal y UN despido en 518 decisiones.** Esa es la pregunta
que originó este encargo. Las cuatro pistas que ya están confirmadas:

**1. La demanda está congelada por decreto** — `behavior/prompts/arquetipo.md:12-14`:

> «El costo de mantener a un trabajador bajo contrato formal **sube {aumento_pct}%** a partir de
> este periodo. **Nada más cambia: tus ingresos, tus clientes y tu capacidad de producción son
> los mismos.**»

Con ingreso fijo y producción fija, despedir solo destruye producto y encima cuesta plata.
**No existe estado del mundo en el que despedir sea la mejor respuesta.** El empleador real
despide *precisamente porque le cayó la venta*; este empleador no puede tener ese problema.

**2. Tres candados en la misma dirección y ninguno en la contraria** — `sistema.md:24-26`:
«No puedes gastar plata que no tienes. Tu flujo de caja es un tope duro» · «Despedir cuesta:
hay una indemnización» · «No puedes producir sin trabajadores: si te quedas sin gente, no hay
ingreso». Consecuencia medida: **47% de las justificaciones (242 de 518) evalúan el despido y
lo descartan explícitamente**, casi siempre por no alcanzar a pagar la indemnización. El único
que sí despidió, despidió **exactamente los 17 que su caja alcanzaba a indemnizar**.
**70% de las justificaciones (361) invocan caja o liquidez.**

**3. `subir_precios` es un almuerzo gratis** — `sistema.md:45` lo define como «Trasladas el
costo a tus clientes», y el mundo del prompt garantiza que los clientes no se van.
**140 agentes (27%) la tomaron, con alzas declaradas de hasta 98,1%.** El propio código lo
admite (`behavior/rondas.py:779`): *«no es inflación: no hay respuesta de demanda, no hay
elasticidad»*. Es una puerta de salida sin costo que además **no mueve ninguna cifra del
agregado**.

**4. La p(inspección) que reciben es bimodal, no una distribución.** De las 218 justificaciones
que la citan: mediana 76,7%, **73 casos en exactamente 100%**, 65 casos por debajo de 1%. Y los
agentes responden con limpieza mecánica: los que informalizan citan una mediana de 0,3%; los que
suben precios o absorben citan 100,0%. **Los agentes son racionales; el insumo es el problema.**
Una p(inspección) de 100% no existe en ningún régimen de fiscalización real.

> **Ojo con la conclusión fácil.** Que un alza del mínimo se pague en informalidad y no en
> despidos **es coherente con la evidencia colombiana**, y la indemnización del CST es un costo
> de caja real. El resultado puede ser defendible. Lo que no es defendible es presentarlo como
> un hallazgo del modelo cuando las frases de arriba lo hacían inevitable antes de llamar al LLM.
> Tu trabajo incluye decirnos en cuál de los dos casos estamos.

---

## Los límites. No son sugerencias

**1. Al LLM JAMÁS se le nombra la política.** Solo la mecánica («tu costo laboral por empleado
formal sube X%»). Nunca «salario mínimo», ni «decreto», ni años, ni Colombia, ni Bogotá.
`behavior/higiene.py` lo hace cumplir con una lista negra y **tumba la corrida** si algo se
filtra. Cualquier texto que propongas se verifica con `python3 -m behavior.higiene`. Es la mitad
del argumento de validación del proyecto: si el modelo sabe qué política es, sus respuestas
pueden venir de lo que leyó, no de la mecánica que le dimos.

**2. Cambiar el prompt invalida la caché y cuesta plata de verdad.** La clave de caché es
`sha256({modelo, sistema, usuario, esquema})` — `behavior/cache.py:40`. **Cambiar una coma de
`sistema.md`, `arquetipo.md` o del esquema quema las 518 respuestas ya pagadas (~USD 7,87)** y
deja `scripts/reproduce.py` cayendo a la ablación de reglas fijas en vez de reproducir el
resultado publicado (nivel 2 de la ADR 0009). No hay presupuesto ni tiempo para volver a
pagarlas.

**3. Por eso: NO APLICAS NINGÚN CAMBIO.** No edites `behavior/`. Entregas diagnóstico y parche
propuesto en forma de diff; la decisión de pagarlo es del equipo.

**4. El resultado probable de tu auditoría es que documentemos el límite, no que reescribamos
el prompt.** Se te dice de frente para que no gastes tu tiempo puliendo un parche que quizá no
se pueda mergear. **La parte de tu entrega que con seguridad se va a usar es el diagnóstico y
el párrafo de límite declarado** (entregable C). Priorízalos.

**5. Un cambio en el esquema de respuesta (`behavior/contrato.py`) es más caro que uno en el
texto**: rompe la caché igual, y además toca el veto de `engine/veto.py`, que es de otro dueño.
Si tu diagnóstico exige un campo nuevo, dilo, pero márcalo como la opción cara.

---

## Qué entregas

Escribe **un solo archivo**: `docs/agents/revision-prompts/2026-08-23-empleador.md`.
No toques nada más del repo.

**A · Diagnóstico, una entrada por frase problemática.** Formato fijo:

```
### [archivo:línea] «la cita literal»

**Qué causa:** el comportamiento observado, con la cifra medida que lo prueba.
**Qué haría un empleador real:** una o dos frases, y de dónde sale (evidencia, CST,
  experiencia de PYME). Si no tienes fuente, escribe "sin fuente, es mi juicio".
**Reemplazo propuesto:** el texto exacto que iría en su lugar.
**Qué se rompería:** caché / esquema / veto / higiene / nada.
```

Ordénalas por cuánto mueven el resultado, no por orden de aparición en el archivo.

**B · El parche, como diff**, al final del documento. Que se pueda aplicar sin pensar si
alguien decide pagarlo. Incluye el resultado esperado de `python3 -m behavior.higiene`.

**C · El párrafo de límite declarado**, listo para pegar en `VALIDATION.md`: qué NO puede
producir este empleador y por qué, escrito para un lector externo, en lenguaje llano, sin
siglas. Máximo 6 líneas. **Este es el entregable que sí se va a usar hoy.**

**D · Veredicto, una línea.** ¿Es defendible ante un jurado técnico tal como está, si lo
declaramos? `SÍ` / `SÍ, PERO` / `NO`, y la razón en la misma línea.

---

## Cómo verificas lo que afirmas

Todo lo que digas sobre lo que el modelo hace se comprueba contra la caché, gratis y sin red:

```bash
# conteo por familia
python3 -c "
import json,glob,sys,collections; sys.path.insert(0,'.')
from behavior.contrato import familia
S=[json.load(open(f))['salida'] for f in glob.glob('behavior/.cache/*.json')]
print(collections.Counter(familia(s['estrategia_propuesta']) for s in S).most_common())"

# las justificaciones que hablan de despido o indemnización
python3 -c "
import json,glob,re
for f in sorted(glob.glob('behavior/.cache/*.json')):
    s=json.load(open(f))['salida']
    if re.search(r'despid|indemniz', s['justificacion'], re.I):
        print(f\"[{s['estrategia_propuesta']}] {s['justificacion']}\")"

# el filtro de contaminación sobre cualquier texto que propongas
python3 -m behavior.higiene
```

**Toda afirmación va con evidencia:** `archivo:línea`, o salida real de un comando. Si algo es
tu juicio y no una medición, escribe **HIPÓTESIS** al lado. No inventes problemas para llenar el
informe: un diagnóstico corto y cierto vale más que uno largo. Y si concluyes que el prompt está
bien como está, **dilo** — es una respuesta válida y es la que más tiempo nos ahorra.
