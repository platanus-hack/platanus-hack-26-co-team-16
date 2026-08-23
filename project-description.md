# El simulador que falsó su propia tesis

**Track: 🌐 Simulations · team-16 · Bogotá**

Toda proyección de política pública asume que la gente va a cumplir la norma. Esa es la parte que nadie mide.

Construimos un simulador que no pregunta *"¿funciona esta política?"* sino **"¿cuánta gente la cumple, y a quién le cae encima?"**. El caso: el aumento del salario mínimo del 23% en Colombia — decretos 1469 y 1470 de 2025, cerca de 2,4 millones de trabajadores al mínimo, con litigio abierto en el Consejo de Estado.

Después lo pusimos a predecir un año que ya ocurrió, para ver si acertaba.

No acertó. **Y ese es el resultado que estamos presentando.**

---

## El número

```
Error del backtest:          37,37 pp
Habilidad vs. persistencia:  -8,182
```

El modelo predijo que la informalidad en Bogotá **subiría 33 puntos** con el alza del 23%. **Bajó 4.**

| | 2025 → 2026 | cambio |
|---|---|---|
| Nuestro proxy (GEIH ene–jun, mismo código en los dos extremos) | 34,64% → 30,57% | **−4,07 pp** |
| Oficial DANE (abr–jun, otra definición) | 35,60% → 33,30% | **−2,30 pp** |
| **Lo que predijo el modelo** | | **+33,3 pp** |

Signo contrario, un orden de magnitud, y el valor real cae **fuera del propio rango de incertidumbre del modelo**. Predecir simplemente *"2026 será igual que 2025"* erra por 4,07 puntos; nuestro modelo erra por 37,37. La regla más tonta posible nos gana ocho veces.

Con dos episodios el problema se ve mejor todavía:

```
2024 → 2025, alza  +9,5%:   +2,63 pp observado
2025 → 2026, alza +23,0%:   -4,07 pp observado
```

El modelo predice que sube en los dos, y más en el grande. En el grande bajó. **Las direcciones se oponen.**

---

## Por qué publicamos esto en vez de esconderlo

El criterio de éxito se escribió **antes** de correr el modelo y se commiteó con fecha, con los datos de 2026 todavía sin descargar. Está en el historial de git, verificable con un comando. La regla que nos pusimos entonces fue: *el número se publica salga como salga.*

Un umbral escrito después de ver el resultado no es un umbral, es una racionalización.

Podríamos haber presentado la cascada de evasión como hallazgo — la curva es vistosa y nadie en la sala habría podido refutarla en tres minutos. Elegimos medirla contra la realidad. La realidad dijo que no.

**Lo que falló es el modelo de comportamiento. La maquinaria que lo midió funciona,** y hay una prueba independiente: el pico de la distribución salarial se movió solo, de 1.420.000 pesos en 2025 a 1.750.000 en 2026, siguiendo el mínimo legal de cada año (1.423.500 y 1.750.905) sin que nadie se lo dijera. Los datos leen bien la realidad.

El aparato de medición encontró que el modelo estaba mal **antes del Q&A, no durante**. Para eso sirve un aparato de medición.

---

## Qué construimos, concretamente

**La población no se inventa.** Los agentes se instancian desde personas y empresas reales anonimizadas de los microdatos de la GEIH, la encuesta de hogares del DANE. Educación, sector, tamaño de firma, ingreso e informalidad vienen todos de la misma fila de la encuesta: las correlaciones entre atributos son las observadas, no las que un modelo de lenguaje considere plausibles.

**Al modelo de lenguaje jamás se le nombra la política.** Solo la mecánica: *"tu costo laboral por empleado formal sube un X%"*. Nunca "salario mínimo", nunca "decreto", nunca el año. Es el control contra contaminación por memoria del modelo, y un test automático lo verifica en cada corrida.

**El LLM propone, el motor dispone.** La capa de lenguaje descubre estrategias de adaptación — informalizar, absorber el costo, recortar jornada, despedir, subir precios — en vez de elegirlas de un menú que escribió un economista. Un motor determinista con semilla calcula el flujo de caja y **veta** lo materialmente imposible. El veto es aritmética, no criterio.

**La fiscalización es endógena.** La capacidad de inspección laboral es fija: cada evasor adicional baja la probabilidad de que la sanción te caiga a vos.

**Todo número sale con banda.** La incertidumbre se mide sobre trayectorias completas e independientes, y cuando no hay dispersión que mostrar la banda se marca como degenerada, en vez de dibujar una precisión inexistente.

---

## Qué NO hace

Límites declarados, no omisiones.

- **No es un modelo macro.** Inflación, crecimiento y tasa de cambio entran como datos observados, nunca como resultado.
- **No prueba convergencia a equilibrio.** Son rondas de mejor respuesta, y así se reportan.
- **No optimiza políticas.** Evalúa la que se le dé; no busca la mejor.
- **No entrega el futuro.** Entrega un rango, con el error del backtest publicado al lado.
- **No podemos afirmar la cascada agregada.** Nuestro propio backtest la falsó, y retiramos la afirmación del repositorio cuando llegó el dato.

**Tres de las compuertas de validación siguen bloqueadas** — falta el script que genera la corrida canónica, falta fijar la versión de una dependencia y falta registrar el par de prompts canónico y re-skinneado. Por eso el comando de validación **sale con código de error a propósito**. Preferimos que falle ruidosamente a que pase en silencio.

---

## Verificalo vos

```bash
make validate                 # imprime EL número; sale con código 1 mientras haya compuertas bloqueadas
make test                     # el núcleo determinista
python scripts/reproduce.py   # reproduce el resultado principal, sin API key
```

El número se reproduce en un clon limpio **sin descargar nada**: los momentos que necesita están versionados, así que no hacen falta los ~370 MB de microdatos crudos. Hay un test que lo verifica, y existe porque una auditoría interna encontró que la promesa era falsa — el validador exigía los crudos y funcionaba solo en la máquina de quien lo escribió.

Mismo seed, mismo resultado. Corrélo dos veces y compará.
