# Propuesta de variación entre corridas — 2026-08-22

> **Qué es este archivo.** Una propuesta de R1 (Alejo) sobre de dónde debe salir la
> variación del simulador y cómo reportarla. **No es normativa:** toca `engine/` y
> `behavior/`, carpetas de Manuel (R2) y Nico (R3), y queda pendiente de su aval. Un informe
> con fecha es un hallazgo, no una decisión; si se acepta, se gradúa a ADR y al registro de
> supuestos de `../../engine/MODELO.md`.

## 1. El estado actual

La afirmación precisa es: **una corrida que hace llamadas LLM en vivo no está determinada
por el seed del repo y puede variar por una fuente que no representa dispersión poblacional**.
Una corrida con la misma caché sí es reproducible, como establece
[`ADR 0009`](../adr/0009-frontera-del-determinismo.md).

| Evidencia del repo | Resultado |
|---|---|
| `engine/seed.py:13-16` | Declara que el seed actual es decorativo y que ningún consumidor de producción llama todavía el muestreo. |
| Búsqueda de `generador_raiz`, `stream_de_ronda` y `stream_nombrado` fuera de `engine/test_seed.py` | No hay consumidores de producción. |
| `engine/fiscalizacion.py:111-126` | `prob_sancion()` calcula `p(E)`; no realiza un sorteo Bernoulli. |
| `engine/veto.py:70-71` y `:220-262` | El veto se declara y se implementa como función pura, sin azar. |
| `behavior/cliente.py:183-195` | La llamada no pasa `temperature`, `top_p` ni `seed`; el comportamiento de muestreo queda delegado al proveedor. ⚠️ El valor exacto de sus defaults no está documentado en el repo. |
| `engine/MODELO.md:91` · `behavior/README.md:80-82` | La banda actual se construye sobre N≥5 paráfrasis del prompt, no sobre temperatura ni semillas del mundo. |

El barrido guardado en `behavior/barrido-2026-08-22.log` confirma que la banda epistémica
es grande frente al efecto de mover la política:

| Aumento del costo formal | p10 | p90 | Ancho p90−p10 |
|---:|---:|---:|---:|
| 7,0% | 55,73% | 69,01% | 13,28 pp |
| 10,0% | 32,37% | 78,42% | 46,05 pp |
| 13,6% | 62,50% | 77,79% | 15,29 pp |
| 18,0% | 54,71% | 76,16% | 21,45 pp |
| 23,0% | 61,68% | 71,99% | 10,31 pp |
| 26,0% | 49,90% | 71,45% | 21,55 pp |
| 30,0% | 72,69% | 78,76% | 6,07 pp |

Ordenados, los anchos son 6,1 / 10,3 / 13,3 / 15,3 / 21,5 / 21,6 / 46,1 pp. La mediana
es **15,29 pp**. Las siete medias finales van de 58,95% a 75,62%, un rango de **16,67 pp**.
La banda mediana de una política es casi toda la variación observada entre políticas.

El dato que decide esta propuesta es la ablación documentada en
`behavior/README.md:394-419`: con el maximizador determinista, la informalidad final es 0,0%
por debajo del umbral medido `F = 1,4309` y 100,0% en los puntos ensayados por encima. El
objetivo interior publicado en `data/momentos.json` es **0,3057**.

> Un modelo cuyos agentes maximizan sin ruido solo puede producir esquinas. No se puede
> calibrar a un valor interior. La temperatura de decisión no es un adorno de realismo: es
> el grado de libertad que le falta al modelo para que el candado 1 cierre.

## 2. Determinismo y variación no son opuestos

El motor puede seguir siendo reproducible con las mismas versiones: una corrida deja de ser
la respuesta y pasa a ser un elemento de una distribución sobre un ensemble de semillas. El
seed permite que otra persona reproduzca los mismos rasgos, choques y agregados, no que el
mundo quede sin heterogeneidad.

Esto completa el vocabulario de `docs/adr/0009-frontera-del-determinismo.md`:

| Nivel de ADR 0009 | Garantía existente |
|---|---|
| 1 · Motor puro | Mismas decisiones y streams sembrados producen el mismo resultado. |
| 2 · Corrida completa con caché | Misma caché evita una llamada nueva al proveedor. |
| 3 · Ablación | Reglas fijas, sin dependencia externa. |
| **4 · Ensemble sembrado — propuesto** | Mismos seeds, parámetros, población, caché y versiones reproducen la misma distribución reportada. |

## 3. Siete niveles de variación

La lista requerida va de L0 a L6: son siete niveles, no seis. L4 es una capa de ejecución y
reporte que agrega los sorteos anteriores; no introduce por sí sola un mecanismo conductual.

| Nivel | Qué varía | Cuándo se sortea | De dónde sale |
|---|---|---|---|
| **L0 · Estructura** | Atributos observados | Nunca | GEIH |
| **L1 · Rasgos** | Prima de protección, aversión al riesgo, inercia | Una vez por agente al inicializar; constante entre rondas | `P1805`, `P1879`, `P6100`, `P7240` y distribuciones calibradas |
| **L2 · Choque idiosincrático** | Desempate entre opciones cercanas | Cada ronda | `Gumbel(0, λ_i)` sembrado |
| **L3 · Percepción** | Agregado que cada agente cree observar | Cada ronda, con rezago explícito | Señal parcial del agregado anterior |
| **L4 · Ensemble** | Realizaciones completas | Entre R semillas | Streams sembrados de L1–L3; es la banda principal |
| **L5 · Epistémica** | Estrategias que existen en el menú | Entre N paráfrasis | Capa LLM; ya existe y se reporta aparte |
| **L6 · Paramétrica** | Supuestos del modelo | Entre barridos | Sensibilidad; ya existe |

La distinción central es temporal. “Se levantó de mal humor ese día” es L2: transitorio y
nuevo en cada ronda. “Le tiene miedo al riesgo” es L1: permanente. Si todo queda en L2, los
agentes no conservan rasgos; si todo queda en L1, la misma persona responde siempre con el
mismo umbral. L1 convierte un umbral único en una distribución de umbrales y suaviza la curva
agregada. L2 genera flujos brutos mayores que el cambio neto.

## 4. Temperatura de decisión

La regla propuesta es:

```text
P(agente i elige estrategia k) ∝ π_k^arquetipo · exp(V_ik / λ_i)
```

| Término | Unidad y función |
|---|---|
| `π_k^arquetipo` | Peso adimensional de la estrategia que devuelve la capa LLM por arquetipo. El LLM aporta el menú y su prior, no la dispersión poblacional; el colapso de varianza está documentado en `docs/investigacion/1-teorica.md` §5. |
| `V_ik` | Pago neto mensual que calcula el motor para ese agente con sus atributos. Unidad: COP/mes. |
| `λ_i` | Temperatura en la misma unidad de `V`: COP/mes. `λ → 0` selecciona máximos de `V`; `λ → ∞` recupera `π`. Solo equivale a una moneda uniforme si `π` es uniforme. |

La forma es equivalente a sumar choques Gumbel a `V_ik + λ_i log(π_k)` y tomar el máximo.
La coherencia dimensional exige dividir un pago por una temperatura expresada también en
COP/mes; no cabe un “ruido de 0,2” sin unidad.

`λ` no se fija por gusto. `data/momentos.json` publica dos **familias** de momentos interiores:
informalidad por sector y por tamaño, además del total 0,3057. Por tamaño registra micro
0,6672, pyme 0,1057 y grande 0,0081. La propuesta de calibración usa esas familias para
estimar `λ_trabajador` y la pendiente de `λ_firma` con tamaño. Que esos momentos identifiquen
ambos parámetros es una hipótesis que debe demostrar el diagnóstico de R2, no una conclusión
de este informe.

El encaje de plomería ya existe. `engine/seed.py:109-122` expone
`stream_nombrado(seed, ronda, *nombre)`: L1 puede usar `ronda=0` y una clave estable por agente;
L2 usa el número de ronda. `engine/MODELO.md:65` declara
`engine/arquetipos.py::muestrear(arq, n, rng)`, pero `engine/arquetipos.py` no existe. Esa
pieza también desbloquea el mapa distributivo A3 (`engine/MODELO.md:37-39`).

## 5. La firma decide por interés y aun así varía

Se propone `λ_firma` pequeña y decreciente con el tamaño. El gradiente observado en
`data/momentos.json` —0,6672 micro, 0,1057 pyme y 0,0081 grande— es el ancla interna. La
dirección coincide con la revisión de cumplimiento en países en desarrollo:
<https://wol.iza.org/uploads/articles/489/pdfs/compliance-with-minimum-wage-laws-in-developing-countries.pdf>.
⚠️ La magnitud no se importa de esa literatura; se calibra localmente.

La variación de la firma sale de tres fuentes:

1. **Plantilla distinta.** `data/empresas.parquet` tiene 81 celdas: 9 sectores × 9 códigos
   observados de tamaño (`P3069` 2–10). Todas las firmas de una celda son idénticas. La
   propuesta instancia M firmas por celda remuestreando filas reales de trabajadores de esa
   celda; cada firma conserva salarios, antigüedades y contratos observados. Es heterogeneidad
   empírica, no números nuevos. Una búsqueda de `empresas.parquet` en el código fuera de
   `data/` no encuentra consumidores; `behavior/arquetipos.py:157-160` continúa usando
   `nómina × 0,18` e `ingreso × 1,5`.
2. **Información distinta y rezagada (L3).** La firma no observa el agregado verdadero de la
   misma ronda. La señal debe derivarse del agregado anterior que ya exige
   `engine/MODELO.md:66`.
3. **Inercia.** Toda opción distinta de la actual paga un costo `κ` en COP/mes. Es una QRE
   con sesgo de statu quo. Sin `κ`, diferencias pequeñas de pago pueden producir rotación de
   estrategia en cada ronda.

## 6. Del colectivo al individuo

Hoy hay un solo canal implementado en el motor: la dilución de capacidad
`p(E) = 1 − exp(−C/max(E,1))` de `engine/fiscalizacion.py:111-126`. Es el mecanismo principal
y se conserva.

| Canal | Veredicto | Tratamiento propuesto |
|---|---|---|
| **Visibilidad** | ✅ Ahora | `p_i` ponderada por inspeccionabilidad (`P6880`, tamaño, registro). La capacidad agregada sigue fija; aparece selección. |
| **Denuncia del trabajador** | 🔶 v2 | Una queja eleva `p_i` de la firma cuando la persona informalizada tiene colchón y baja tolerancia. Hace que importe a quién se informaliza. |
| **Salario informal endógeno** | 🔶 v2 | Más oferta informal reduce el salario informal y el retorno de informalizar. |
| **Efecto faro** | 🔶 v2 | El mínimo arrastra salarios informales. Ignorarlo sobreestima la cascada, en la misma dirección del supuesto S7 de `engine/MODELO.md:110`. ⚠️ La atribución a Maloney y Núñez no tiene una URL ni una ficha en el repo y debe verificarse antes de citarla. |
| **Norma social / moral fiscal** | ❌ Apagado | `docs/investigacion/1-teorica.md` §3 distingue explícitamente el canal aritmético de la conformidad. No se reabre. Como interruptor de ablación permite mostrar el resultado con norma apagada. |

## 7. Dónde no entra azar

| Componente | Razón |
|---|---|
| Veto | Es aritmética de cantidades y caja: alcanza o no alcanza. `engine/veto.py` lo declara puro. |
| Parámetros legales | Son estructura normativa con vigencia y fuente. |
| Factor prestacional | `data/parametros_legales.py:224-230` declara que su rango **no es incertidumbre, sino estructura** asignada por firma. |
| Temperatura del LLM como dispersión poblacional | `docs/investigacion/1-teorica.md` §5 documenta que ajustar temperatura no corrige el colapso de varianza. El LLM define L5, no L1/L2. |

## 8. Pruebas de que la variación no es decorativa

1. **Descomposición de varianza.** Reportar qué fracción de la varianza del resultado viene
   de L1, L2, L4, L5 y L6. L4 debe entenderse como agregación de realizaciones, no como fuente
   independiente. Si domina L2, el sistema es un generador de ruido; si domina L0/L1, la
   estructura observada carga el resultado. Es un diagnóstico de R2.
2. **Flujos brutos mayores que cambio neto.** Entre rondas deben coexistir entradas y salidas
   de informalidad aunque el saldo cambie poco. El test no fija una magnitud sin fuente; solo
   rechaza la esquina en que todo movimiento bruto coincide con el neto.

## 9. Lo que esta propuesta no pide

- No reabre ADR 0006: la capacidad de fiscalización sigue siendo estado del mundo y no una
  perilla.
- No reabre D5 de `docs/PLAN.md:42`: siguen siendo tres rondas de mejor respuesta, no una
  afirmación de convergencia a equilibrio.
- No cambia el presupuesto LLM: los sorteos se hacen con numpy sobre 6.692 filas.
- No pide fijar la temperatura del LLM; separa la variación epistémica L5 de la conductual
  L1/L2.
