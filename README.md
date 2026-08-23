# team-16 Platanus Hack 26: Bogotá Project

**Current project logo:** project-logo.png

<img src="./project-logo.png" alt="Project Logo" width="200" />

Track: 🌐 Simulations

team-16

- Alejandro Davila Ceron ([@alejandrod-24](https://github.com/alejandrod-24))
- Daniel Rincón ([@danrin9](https://github.com/danrin9))
- Manuel Mejia Arana ([@manigreeen](https://github.com/manigreeen))
- Nicolás Sánchez ([@nicosanchport10](https://github.com/nicosanchport10))
- Juan David Torres Casas ([@jdtorres59](https://github.com/jdtorres59))

## Pruébalo

**→ [enjambre-web.onrender.com](https://enjambre-web.onrender.com)**, sin registro, sin cuenta, sin
instalar nada. Cada clic en *Simular* lanza una corrida **real** del motor contra la grilla de la
GEIH y transmite cada ronda a medida que ocurre: nada precomputado.

## Qué es

Un simulador que no responde *"¿funciona la política?"* sino **"¿cuánta gente la cumple y a quién le cae encima?"**, el supuesto que toda proyección oficial da por cierto y que nadie mide.

- **La población no se inventa.** Los agentes se instancian desde personas reales anonimizadas de los microdatos de la GEIH (DANE). Educación, sector, tamaño de empresa, ingreso e informalidad vienen en la misma fila de la encuesta: las correlaciones entre atributos son las observadas, no las que un modelo de lenguaje considere plausibles.
- **El LLM propone, el motor dispone.** Una capa LLM descubre estrategias de adaptación (informalizar, absorber, despedir, renegociar) en vez de escogerlas de un menú que escribió un economista. Un motor determinista con seed calcula el flujo de caja y **veta** lo que es materialmente imposible.
- **La fiscalización es endógena.** La capacidad de inspección laboral es fija: cada evasor adicional baja la probabilidad de que la sanción te caiga a ti. Eso convierte decisiones individuales en una **cascada**. Es el **mecanismo que el motor simula, no un hallazgo del proyecto**: la predicción agregada que produjo está falsada por nuestro propio backtest, y cuando medimos cuánto aporta la cascada al resultado en el camino determinista, dio **0,0 pp**. Las dos cosas están abajo.
- **Rondas de mejor respuesta.** Los agentes deciden 3 o 4 veces viendo lo que hicieron los demás. La distancia entre la ronda 0 (lo que proyecta el gobierno) y la ronda 3 es el producto entero.

**Caso demo:** el aumento del salario mínimo del 23% en Bogotá. Decretos 1469 y 1470 de 2025, cerca de 2,4 millones de trabajadores al mínimo, con litigio abierto en el Consejo de Estado. Es el primer caso que corre el motor; la misma mecánica está pensada para cualquier política que cambie costos o incentivos.

## Cómo se corre

```bash
make estado     # qué está cableado y corriendo, ahora mismo
make run        # una simulación completa (mismo seed, mismo resultado)
make test       # tests del núcleo determinista
make validate   # los 4 candados e imprime EL número del backtest
```

`make estado` responde en cualquier momento a "¿esto ya sirve?": lista archivo por archivo lo que existe y cuenta los supuestos marcados en el código. Los targets que dependen de una pieza que aún no está dicen qué falta y en qué checkpoint llega, en vez de fallar con un stack trace. Hoy el andamiaje, los contratos, el motor, la población y el número de validación están cableados y corren, y [`VALIDATION.md`](VALIDATION.md) lleva el marcador.

## Lo no obvio

- **Al modelo nunca se le nombra la política.** No ve "salario mínimo", ni "decreto", ni años: solo la mecánica (*"tu costo laboral por empleado formal sube X%"*). Es el control de contaminación de entrenamiento, hecho código y no promesa: vive en [`behavior/higiene.py`](behavior/higiene.py), que revisa **cada** prompt antes de enviarlo y mata la corrida entera si encuentra un término prohibido, un símbolo de moneda o un año de cuatro dígitos. Es fail-closed: no filtra, aborta. Si el agregado emerge igual sin el nombre, no es memoria, es mecánica.
- **El veto va al revés de lo habitual.** En casi toda simulación con agentes LLM el modelo también juzga. Acá el LLM solo propone; quien acepta o rechaza es aritmética determinista sobre el flujo de caja. Una empresa sin caja para pagar indemnizaciones no puede despedir, por convincente que suene la justificación.
- **Se llama al LLM por arquetipo, no por agente.** Unos 40 a 60 arquetipos (sector x tamaño x formal/informal x tramo de ingreso) por 4 rondas dan cerca de 250 llamadas cacheadas, y los miles de agentes muestrean de esas distribuciones. La heterogeneidad la pone la GEIH; el LLM solo aporta el espacio de estrategias.
- **El motor es nuestro y cabe en una tarde de lectura.** Cerca de 300 líneas de numpy/pandas vectorizadas, deliberadamente sin Mesa ni AgentSociety. El porqué, con las alternativas descartadas una por una, está en [`ARCHITECTURE.md`](ARCHITECTURE.md) y en [`docs/adr/`](docs/adr/).
- **La salida es un rango, nunca un veredicto.** Todo número sale con banda, y la interfaz muestra bajo qué parámetros cada una de las tres posturas del debate (7% / 13,6% / 23%) resulta razonable.

## El resultado, con el método escrito de antemano

Escribimos los criterios de éxito **antes** de tener los datos, en un commit fechado y verificable (`git log --date=iso -- VALIDATION.md`), y después corrimos el backtest fuera de muestra contra el episodio real de 2025→2026:

```
Error del backtest:          +37,37 pp
Skill vs. persistencia:       −8,182     (la persistencia le gana ocho veces al modelo)
Delta observado:              −4,07 pp   (la informalidad BAJÓ)
Delta predicho:              +33,3  pp   (el modelo dice que SUBE)
```

**El modelo falló, y el signo está al revés.** Se activó la rama que habíamos pre-escrito para ese caso: se publica el error, se acota el claim al margen formal→informal dentro de quienes ya tienen empleador, y se nombran los confusores que no cubrimos —la reforma laboral, la jornada de 42 horas, el ciclo— como límite declarado y no como excusa. El detalle completo, con los candados y la sección de dónde NO hay que creernos, está en [`VALIDATION.md`](VALIDATION.md).

**Y esto es el activo, no la vergüenza.** Un backtest negativo, medido contra un criterio que nadie movió y publicado con su signo, es más serio que una cifra que nadie puede refutar. El aparato de medición funciona: fue él quien encontró que el modelo está mal, antes del Q&A y no durante.

### Lo que el motor sí produce, medido

Lo que el backtest falsó es la **predicción agregada** para Bogotá. Lo que el motor sí hace, de forma reproducible sin API key y en 9,7 segundos, es más estrecho:

```bash
python scripts/barrido_politicas.py --desde 0 --hasta 30 --paso 2
```

| Alza | 0% | 2% | 4% | 6–12% | 14–16% | 23% |
|---|---:|---:|---:|---:|---:|---:|
| Brecha | +3,2 pp | +3,7 | +5,8 | +9,2 | +10,6 | **+10,58 pp** |

**Monótona no decreciente en los 16 puntos**, señal de 12,26 pp entre políticas y ruido/señal 0,00
(el camino determinista repite exacto). Sus límites van en la misma frase, y uno es serio:

- Es el camino de **reglas fijas**, no el de descubrimiento con LLM. Ahí la pendiente **no se
  sostiene**: dos corridas dan signos opuestos y el ruido de reformulación del prompt iguala a la
  señal.
- Hay una **meseta** entre 6% y 12%, y el "codo" del tramo alto aparece como techo, no como
  aceleración.
- 🔴 **El placebo dejó de ser cero.** Con alza 0% la informalidad sube +3,2 pp, cuando debería no
  moverse. Lo destapó el arreglo de unidades del PR #41, y significa que **α = 1,875 quedó
  descalibrado**: parte de la brecha no viene de la política. Se recalibra con
  `python scripts/calibrar_visibilidad.py` y está declarado.

Todo, con su comando y su línea base: [`docs/evidencia/2026-08-23-E1-E2-E3.md`](docs/evidencia/2026-08-23-E1-E2-E3.md).

## Prior art

Buscado a propósito y citado acá antes de que lo encuentre alguien más. Nada de esto es nuestro:

| Trabajo | Qué ya resolvió | Qué deja abierto |
|---|---|---|
| Meghir, Narita & Robin, *Wages and Informality in Developing Countries*, [AER 105(4), 2015](https://www.aeaweb.org/articles?id=10.1257/aer.20121110) | El modelo de equilibrio donde firmas de igual productividad eligen sector formal o informal, estimado con datos de Brasil. **La economía de la informalidad no es novedad nuestra.** | Es un modelo estimado, no un instrumento interrogable: no responde "quién concretamente" ni corre detrás de un slider. |
| [*Investigating Tax Evasion Emergence Using Dual LLM and DRL Powered Agent-based Simulation*](https://arxiv.org/abs/2501.18177) (2025) | Lo más cercano a nuestro control de contaminación: dejan emerger la evasión **sin avisarle al agente que evadir es una opción**. | Población sintética, no microdatos de una encuesta nacional; sin backtest fuera de muestra publicado. |
| [AgentSociety](https://arxiv.org/abs/2502.08691) (Tsinghua, 2025), 10.000 agentes, 5M interacciones, incluye experimentos de renta básica | Que una sociedad de agentes LLM a escala es viable y sirve de banco de pruebas de política. | Entorno urbano genérico: no trae GEIH, ni margen formal/informal, ni fiscalización endógena. |
| [PolicySim](https://dl.acm.org/doi/10.1145/3774904.3792555) (ACM Web Conference 2026) | Sandbox de agentes LLM para optimización de política pública. | Optimiza la política; nosotros evaluamos la que se nos dé y medimos el cumplimiento. |
| [PoliSim@CHI 2026](https://polisim.net/) | El campo tiene nombre y comunidad desde abril de 2026. No estamos inventando la categoría. | n/a |
| Banco de la República, [*Minimum wage effects on labour informality*](https://ideas.repec.org/p/bdr/borrec/1104.html) (WP 1104) | La elasticidad publicada para Colombia: +1 pp en el ratio del mínimo se asocia con +0,21 pp de probabilidad de empleo informal. | Es una elasticidad, o sea una recta: no dice si hay un umbral donde la cascada se dispara. **La usamos como objetivo de calibración, no como resultado.** |

**Qué es nuestro, entonces:** la composición. Población real de una encuesta nacional, más veto de factibilidad determinista, más fiscalización endógena, más backtest fuera de muestra con el método escrito de antemano, más la política jamás nombrada al modelo, todo dentro de una interfaz que un extraño puede interrogar sin registrarse. Ninguna pieza es inédita por separado; junta, sí.

### La objeción que nos hacemos nosotros

Luo, Arora y Guirado, [*We Need Strong Preconditions For Using Simulations In Policy*](https://arxiv.org/abs/2604.07838) (abril 2026), argumentan tres precondiciones para simular poblaciones en contextos de política pública. Nuestra posición, sin adornos:

- **Validar contra algo más que datos históricos, y declarar la heterogeneidad que el modelo no captura.** Lo hacemos: calibración contra momentos observados, backtest fuera de muestra con los criterios escritos antes de verlo, y una sección explícita de "dónde NO hay que creerle" en [`VALIDATION.md`](VALIDATION.md).
- **No simular poblaciones sin su participación.** Un proceso participativo con trabajadores informales excede lo que cabe en un hackathon de 36 horas, así que queda como el primer punto del trabajo futuro y lo dejamos dicho de frente, no dado por hecho.
- **Trazabilidad de las decisiones.** Repo público bajo MIT, cada supuesto marcado con `# SUPUESTO:` en el punto donde se toma (`grep -rn "SUPUESTO:"` es el informe de honestidad del proyecto), y el número de validación reproducible con un comando.

## Hacia dónde va

Lo que hoy es alcance acotado ya está escrito como hoja de ruta:

- **De una política a todas.** Hoy corre el salario mínimo; la misma arquitectura sirve para cualquier política monetaria o laboral que cambie costos o incentivos.
- **Del empleo que solo cae al empleo que se mueve.** Sumar contrataciones, productividad, demanda y precios endógenos, hoy tomados como dato exógeno.
- **De la grilla a la ciudad entera.** Incorporar a los trabajadores por cuenta propia, el 23% de los ocupados de Bogotá.
- **De 3 rondas a la convergencia.** Extender la dinámica de mejor respuesta y estudiar el equilibrio.

## Documentación

| Archivo | Para qué |
|---|---|
| [`AGENTS.md`](AGENTS.md) | El contrato del repositorio: la pieza difícil, cómo verificarla, qué NO hace, mapa de archivos |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | Las capas, el veto, y las alternativas descartadas con su porqué |
| [`VALIDATION.md`](VALIDATION.md) | Los 4 candados, EL número, y dónde no hay que creerle |
| [`docs/PLAN.md`](docs/PLAN.md) | La fuente de verdad del producto |
| [`docs/README.md`](docs/README.md) | Índice de la documentación, con cuánta autoridad tiene cada pieza |

## ⚠️ Deploying & integrations (Vercel, Render, etc.)

Deploy platforms like **Vercel**, **Render** or **Netlify** can only connect to
repositories **you own**, they can't be granted access to this organization repo.
To deploy (or add any integration) while keeping your commits here, mirror your
code to a personal repo:

1. Create a **personal** repository on your own GitHub account.
2. Point your local `origin` at **both** repos, so a single `git push` updates each one:

   ```bash
   # this org repo (keep it as a push target)...
   git remote set-url --add --push origin https://github.com/platanus-hack/platanus-hack-26-co-team-16.git
   # ...and your personal repo
   git remote set-url --add --push origin https://github.com/<your-user>/<your-repo>.git
   ```

   From now on `git push` sends every commit to **both** repositories.
3. Connect your deploy service (Vercel, Render, …) to your **personal** repo and deploy from there.

Your commits stay mirrored here for judging, while the deploy runs from the repo you control.

### Lo que está desplegado ahora

| Servicio | URL | Qué es |
|---|---|---|
| Interfaz | **https://enjambre-web.onrender.com** | La URL de la entrega. Next.js; también hace de proxy del SSE |
| API del motor | https://enjambre-api.onrender.com | FastAPI. `GET /poblacion` y `GET /simulaciones/flujo` |

Los dos corren en Render desde el espejo, con la configuración versionada en
[`render.yaml`](render.yaml). El runbook completo (cómo se redespliega, la trampa de `ENJAMBRE_API`,
qué hacer si se cae en vivo y los límites declarados de la URL pública) está en
[`docs/DEPLOY.md`](docs/DEPLOY.md). Para comprobar que la cadena completa transmite de verdad:

```bash
make humo URL=https://enjambre-web.onrender.com
```

**En este repo el doble push ya está cableado.** Verifícalo con `git remote -v`: deben
aparecer **dos** líneas `(push)`, la de la organización y la del espejo
`vibe-coders-team/platanus-hack-26-T16-simulations`. Si clonaste de cero, no lo tienes:
corre los dos comandos de arriba antes de tu primer push.

Have fun! 🚀
