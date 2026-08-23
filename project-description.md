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

## La fiscalización es endógena

La capacidad de inspección laboral es **fija**, derivada de la cifra de inspectores de la OIT, así
que cada evasor adicional diluye la probabilidad de que la sanción te caiga a ti. Las decisiones
individuales se vuelven una **cascada** que el modelo oficial, que asume cumplimiento, no puede ver.

Eso es el **mecanismo del modelo, no un resultado del proyecto.** La diferencia importa y la
sostenemos abajo — incluso contra nosotros mismos: cuando medimos cuánto aporta esa cascada al
resultado en el camino determinista, la respuesta fue **0,0 pp**
([evidencia](docs/evidencia/2026-08-23-E1-E2-E3.md) §E2). El mecanismo opera —p(sanción) se mueve de
67,8% a 62,0% según cuánta gente evade— pero ese movimiento todavía no cambia el agregado. Está
publicado porque lo medimos nosotros.

## El número, publicado salga como salga

Escribimos los criterios de éxito **antes** de tener los datos, en un commit fechado y verificable
(`git log --date=iso -- VALIDATION.md`). Después corrimos el backtest fuera de muestra contra el
episodio real de 2025→2026:

```
Error del backtest:          +37,37 pp
Skill vs. persistencia:       −8,182     (la persistencia le gana ocho veces al modelo)
Delta observado:              −4,07 pp   (la informalidad BAJÓ)
Delta predicho:              +33,3  pp   (el modelo dice que SUBE)
```

**El modelo falló, y el signo está al revés.** Se activó la rama que habíamos pre-escrito para ese
caso: se publica el error, se acota el claim al margen formal→informal dentro de quienes ya tienen
empleador, y se nombran los confusores que no cubrimos —la reforma laboral, la jornada de 42 horas,
el ciclo— como límite declarado y no como excusa. Un backtest negativo pero medido y reportado con
honestidad sigue siendo más serio que una cifra que nadie puede refutar.

## Lo que el modelo sí produce, medido

Lo que el backtest falsó es la **predicción agregada** para Bogotá. Lo que el motor sí hace, de
forma consistente y reproducible sin API key, es otra cosa y más estrecha:

```bash
python scripts/barrido_politicas.py --desde 0 --hasta 30 --paso 2
```

16 políticas, 9,7 segundos, USD 0,00:

| Alza | 0% | 2–12% | 14% | 16% | 18% | 20% | 22–30% |
|---|---:|---:|---:|---:|---:|---:|---:|
| Brecha | **−0,92 pp** | +3,25 | +4,02 | +4,33 | +4,90 | +5,79 | **+6,07 pp** |

**Monótona no decreciente en los 16 puntos** (Spearman 0,96), con el placebo en cero y las tres
posturas del debate colombiano —7%, 13,6%, 23%— ordenadas. Con sus límites en la misma frase: es el
camino de **reglas fijas**, no el de descubrimiento con LLM; hay una **meseta** entre 2% y 12%; y
**satura desde 22%**, así que el "codo" aparece como techo y no como aceleración. En el camino con
LLM la pendiente **no se sostiene**: dos corridas dan signos opuestos y el ruido de reformulación
del prompt iguala a la señal. Todo eso está en
[`docs/evidencia/2026-08-23-E1-E2-E3.md`](docs/evidencia/2026-08-23-E1-E2-E3.md).

## Qué NO modela

Límites declarados, no omisiones. Están en el repo con la dirección del sesgo de cada uno:

- **No hay contrataciones**: el empleo solo puede caer. **No hay productividad, demanda, capital ni
  precios endógenos.**
- **La tasa de desempleo no es computable** con lo que el motor mueve.
- **Los trabajadores por cuenta propia (23% de los ocupados de Bogotá) están fuera de la grilla**: el
  enjambre no es la ciudad entera.
- **No prueba convergencia a equilibrio**: son 3 rondas de mejor respuesta, y así se reporta.
- **La calibración base falla por tamaño de firma**: el modelo produce cero informalidad en pyme y
  en grande, y toda la suya vive en micro (+7,5 pp). El candado G3 no se cumple y está declarado.
- Hoy la corrida arranca de la población posterior a la política; corregirlo cambia el número, y
  **está pre-comprometido por escrito** qué se hace con el número nuevo salga como salga.

## Hacia dónde va

Lo que hoy es alcance acotado ya está escrito como hoja de ruta, no improvisado. El detalle, con
costo y comando de verificación por fase, está en [`ROADMAP.md`](ROADMAP.md):

- **De una política a todas.** Hoy corre el salario mínimo; la misma arquitectura sirve para
  cualquier política que cambie costos o incentivos. Es la fase 2 del roadmap.
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
make test        # el núcleo determinista, 104 tests
make validate    # los candados e imprime EL número (sale 1 mientras haya compuertas bloqueadas)
make supuestos   # cada supuesto marcado en el punto donde se toma
python scripts/barrido_politicas.py --desde 0 --hasta 30 --paso 2   # la curva, sin API key
```

Mismo seed, mismo resultado. Repo público, licencia MIT, y `grep -rn "SUPUESTO:"` es el informe de
honestidad del proyecto.
