# Auditoría matemática — 2026-08-23 04:14 · EJE B · fundamentación

> Informe del agente `juez-cientifico`. Autocrítica interna del equipo, no una evaluación externa.
> **Modo:** eje-B (fundamentación) · revisión a tres ejes, `docs/vet/revision-3ejes/`
> **Commit:** `9218dc3` · **Rama:** `worktree-vet-eje-b` (worktree de solo lectura colgado de `origin/main`)
> **Comandos ejecutados:** `git rev-parse --short HEAD` · `ls engine/ behavior/ data/ docs/adr/` · `wc -l engine/*.py behavior/*.py data/*.py` · `sed -n` sobre `VALIDATION.md`, `DEFECTOS.md`, `engine/veto.py`, `data/construir_empresas.py`, `behavior/arquetipos.py`, `scripts/validate.py` · `grep -rn` (varios) · 4 × `python -c` sobre `data/empresas.parquet` y `data/momentos*.json`. **Falló 1:** `pd.Series.corr(method='spearman')` → `ModuleNotFoundError: No module named 'scipy'` (exit 1); resuelto recalculando Spearman como Pearson sobre rangos con `numpy`. **Ninguno llamó al proveedor de LLM.**
> **Segunda opinión:** `mcp__codex__codex` (GPT-5, read-only, approval never) — CONSULTADA. Coincidencia independiente en el veredicto de la pregunta principal.
> **Veredicto:** el reparto no sobrevive como aporte del modelo; sobrevive como re-dibujo del dato de entrada.

---

## ¿SOBREVIVE EL REPARTO AUNQUE EL NIVEL ESTÉ FALSADO? — **NO como está.**

**En cristiano:** el mapa de "quién no puede pagar el alza" no lo calcula el modelo. Lo copia de la
GEIH. El modelo dice que sufre primero el que ya era informal — que es exactamente el dato con el que
se le alimentó. No es una predicción, es la foto de entrada con otro color.

**La derivación** [VERIFICADO]. En `engine/veto.py:405-450` la única prueba que decide si una celda
puede absorber el alza es:

```
sobrecosto = en_regla · ingreso · factor · (a/100) · 3      (engine/veto.py:443-445)
caja       = flujo_caja · 3 = 0,18 · nómina · 3             (engine/veto.py:297, data/construir_empresas.py:153)
nómina     = ingreso · n_empleados                          (data/construir_empresas.py:122)
```

⇒ `sobrecosto/caja = share_formal · factor · a / 0,18`.

**El salario se cancela exactamente.** El tamaño se cancela exactamente. Lo único que queda es la
formalidad inicial de la celda y el factor prestacional, que toma 10 valores en `[1,3835 · 1,5829]`
(verificado sobre `data/empresas.parquet`). Lo mismo para `cumplir`:
`costo/caja = (1−share_formal)(factor−1)/0,18` (`engine/veto.py:420`).

**Medido sobre las 81 celdas reales** (`python -c` sobre `data/empresas.parquet`, a = 23%):

| correlación de rangos (Spearman) | valor |
|---|---|
| ranking de presión ↔ `share_formal` | **0,943** |
| ranking de presión ↔ salario mediano | 0,642 (inducida: el salario solo entra vía formalidad) |
| margen implícito, valores distintos entre las 81 celdas | **uno solo: 0,18** |
| celdas donde absorber ya es infactible a 23% | **67 / 81** |

**Y el ranking observado ya era estático sin modelo** [VERIFICADO]: la informalidad sectorial de
`momentos_2024/2025/2026.json` tiene Spearman **0,967 / 0,983 / 0,983** entre años consecutivos. El
mismo baseline de persistencia que le ganó 8 veces al nivel (`VALIDATION.md:20-21`) también reproduce
el reparto. Un mapa que correlaciona 0,94 con su propio insumo, en un dominio cuyo orden no se mueve
en tres años, **no tiene skill demostrable**.

**El argumento de la "cota superior" no rescata el reparto, y además está mal aplicado.** Su lugar es
`VALIDATION.md:275` y ahí solo se afirma sobre el **nivel** (informalidad ↑, empleo ↓). Extenderlo al
**orden** exige monotonía del operador completo, que nadie demostró. Peor: el canal que faltaría para
que el reparto fuera un resultado — productividad, demanda, traslado a precios — es justamente el que
haría el margen **heterogéneo**, y hoy el margen es constante `0,18` para las 81 celdas. Los canales
ausentes no son un factor común: reordenan.

**Segunda opinión, independiente, misma conclusión:** *"no, el orden relativo de celdas por presión de
costo no es robusto a productividad, demanda, capital y contratación (…) el ranking queda dominado por
formalidad inicial, factor legal y redondeos, no por capacidad económica real"*, con la misma álgebra
(`s_c f_c a / 0,18`) derivada por su cuenta. Sin divergencias con mi lectura en este punto.

**Qué sí se puede afirmar:** un **ranking de carga legal estatutaria** (cuánto sobrecosto legal cae
sobre cada celda), que es descriptivo y sale del CST, no del motor. Eso hay que decirlo con ese
nombre.

---

## 1 · MENTIRAS

*(ordenadas por qué tan rápido lo encuentra un juez con un agente)*

**1.1 · "El mapa dice quién no puede pagar" — el mapa dice quién ya era informal** · CRÍTICO · [VERIFICADO] · Tipo: **especificación**
- **En cristiano:** todas las empresas del modelo tienen el mismo colchón: 18 céntimos por cada peso
  de nómina. Ninguna es más frágil que otra. Así, la única razón por la que una celda "no puede pagar"
  es que ya tenía gente informal.
- **Evidencia:** `data/construir_empresas.py:70` (`MARGEN_SOBRE_NOMINA = 0.18`), `:153`; `engine/veto.py:297`, `:443-445`. Margen implícito único en el parquet: `0.18` para las 81 celdas.
- **Consecuencia:** la lámina distributiva es un re-plot de `share_formal`. Un juez que pregunte *"¿de
  dónde sale la heterogeneidad de capacidad de pago?"* recibe: "no hay".
- **Barato:** rotular la lámina **"carga legal estatutaria por celda"** y decir que el ordenamiento
  proviene del CST y de la formalidad observada, no del motor.

**1.2 · El alza del mínimo se cobra al 100% de la nómina, esté donde esté el salario** · CRÍTICO · [VERIFICADO] · Tipo: **especificación**
- **En cristiano:** si sube el salario mínimo 23%, a una empresa cuyos empleados ganan 3 mínimos no le
  sube el costo 23%. En el modelo sí.
- **Evidencia:** `engine/veto.py:443-445` aplica `aumento_pct` sobre `en_regla · ingreso · factor`,
  con `ingreso = salario_mediano` de la celda (`behavior/arquetipos.py:285`). No existe ninguna
  variable de exposición al mínimo en `engine/` ni en `data/empresas.parquet` (20 columnas, verificado).
- **Medido:** solo **18 de 81** celdas tienen salario mediano ≤ 1,05 SMLMV (**18,2%** de los
  trabajadores expandidos). El salario mediano ponderado es **1,52 SMLMV**; el p75 es 1,48 y el máximo
  11,42 SMLMV. Es decir: **más del 80% de la masa recibe un shock que no le corresponde.**
- **Dónde colapsa:** exactamente donde el proyecto quiere ser fuerte — el "bite" heterogéneo del
  mínimo. Con exposición `b_c`, el orden de las celdas cambia: las de salario alto caen al fondo.
- **Barato:** no se arregla en la ventana. Se **declara** en la lámina de límites, con dirección de
  sesgo (sobreestima el daño en celdas de salario alto).

**1.3 · El pre-registro se defiende en `VALIDATION.md` sin la retractación que el propio equipo escribió** · ALTO · [VERIFICADO] · Tipo: **reporte**
- **En cristiano:** decimos "escribimos el criterio antes de ver los datos". Es cierto. Lo que no
  decimos en ese archivo es que ya sospechábamos el resultado.
- **Evidencia:** `VALIDATION.md:8-11` argumenta el orden temporal y nunca menciona que `2d4aa7e` ya
  traía *"lo que ya se sabe apunta a la rama B"*. La retractación existe, pero vive en
  `docs/vet/00-hallazgos.md:44`, `docs/vet/README.md:31` y `docs/vet/02-la-idea-en-3-pasos.md:59` —
  documentos internos de revisión, no el archivo que abre el jurado.
- **Consecuencia:** *"si lo decimos nosotros primero es rigor; si lo encuentra un juez es fraude"* —
  palabras del propio equipo. Hoy el juez lo encuentra primero, porque no está donde mira.
- **Dictamen:** el pre-registro **sigue significando algo** (el bloque de las dos ramas es idéntico
  byte a byte, 1056 vs 1056, y el comparador está publicado en `VALIDATION.md:333`). Lo que hay que
  dejar de llamar es **"ciego"**. Nombre correcto: **umbral fijado antes del dato, con la dirección ya
  sospechada y declarada**.

**1.4 · La banda de 33,9 pp está bien nombrada en el texto y mal usada en el número** · ALTO · [VERIFICADO] · Tipo: **reporte**
- **En cristiano:** esa barra no dice "hay 80% de probabilidad de caer aquí". Dice "esto es lo más
  alto y lo más bajo que salió con 5 formas de preguntarle al modelo".
- **Evidencia:** `VALIDATION.md:22` y `:88` ya la rotulan *"entre paráfrasis, NO calibrado"*, y
  `VALIDATION.md:260-264` deriva correctamente que con N=5 el `p10/p90` es el mínimo y el máximo (en
  esperanza, percentiles 16,7 y 83,3). **El texto está bien.** El problema es que `scripts/validate.py:165-171`
  computa `cobertura` con esos extremos como si fueran un intervalo con nivel nominal, y la línea
  `Cobertura del rango: NO` se imprime junto a EL NÚMERO como si un fallo de cobertura significara
  algo estadístico. Una "cobertura" sobre un min-max de 5 paráfrasis no tiene nivel nominal: no puede
  fallar ni acertar.
- **Barato:** en pantalla y en el print, `cobertura` sale como **"el observado cae / no cae dentro del
  rango entre paráfrasis"**, sin la palabra cobertura.

**1.5 · El backtest de 37,37 pp no puntúa el estimando que hoy calcula el motor** · ALTO · [VERIFICADO] · Tipo: **reporte**
- **En cristiano:** el número famoso mide una cosa y el modelo de hoy calcula otra.
- **Evidencia:** `data/prediccion_modelo.json` arranca en 30,6% (informalidad de **todos** los
  ocupados) y `data/momentos.json` ahora publica además `tasa_informalidad_empleados_de_firma = 0,1799`,
  que es el universo que el motor cubre (`VALIDATION.md:275`, fila de cuenta propia: el agregado cubre
  3.235.639 con empleador, no 4,2 millones). Confirmado independientemente por la segunda opinión
  (`behavior/arquetipos.py:521-548`).
- **Y además** `VALIDATION.md:180-188` ya se retracta: la corrida arranca de GEIH **2026**, seis meses
  después del decreto — *"el modelo parte del resultado que debía predecir"*.
- **Consecuencia:** decir "37,37 pp de error fuera de muestra" es más fuerte de lo que el artefacto
  aguanta. El pre-compromiso de `VALIDATION.md:349-372` ya cubre qué hacer; **falta que la frase del
  pitch lo diga.**

**1.6 · El `+0.15` del front: CERRADO** · [VERIFICADO] · `web/enjambre/componentes/enjambre/Personas.tsx:280-282` ya lo eliminó y dejó escrito por qué. No es hallazgo. El otro `0.15` del repo (`ControlPolitica.tsx:95`) es `letterSpacing`. Nada que hacer.

---

## 2 · HUÉRFANOS — candidatos a salir de la DEMO (no del repo)

- **La curva de cascada como pieza narrativa.** `web/enjambre/componentes/Paneles/CurvaBrecha.tsx`,
  `web/enjambre/componentes/reporte/Graficas.tsx`, `web/enjambre/componentes/laboratorio/Graficas.tsx`
  mencionan cascada [VERIFICADO por grep; el texto exacto de cada leyenda es del Eje C]. La cascada
  está **falsada** por el propio backtest y es mecanismo, no resultado. En la demo debe aparecer una
  sola vez, rotulada *"mecanismo del motor"*, o no aparecer.
- **`sobrecosto_formal_pct` y `auxilio_transporte_cop` y `costo_formal_mensual_cop`** de
  `data/empresas.parquet` (`data/construir_empresas.py:128-152`): se calculan bien, incluyen el
  auxilio de transporte —que pesa desproporcionadamente sobre salarios bajos, justo lo que daría
  heterogeneidad real— y **`behavior/arquetipos.py:245-291` no los consume**. Solo pasa el factor
  porcentual. Trabajo hecho que no llega a ningún número [VERIFICADO, coincide con la segunda opinión].
- **`subir_precios`** (1,4% de la población lo elige, `DEFECTOS.md` §1.1): la estrategia se registra y
  el agregado la bota. Como pieza de demo es una etiqueta sin número.

---

## 3 · FALTANTES — lo que la espina promete y esta capa no entrega

1. **"Un mapa ex-ante de quién absorbe el costo".** Falta la variable que lo haría ex-ante:
   heterogeneidad de capacidad de pago. Margen uniforme 0,18 ⇒ el mapa es endógeno al insumo (ρ = 0,94).
2. **"Sin caja para indemnizar no puedes despedir".** Esto **sí** existe y es la parte más limpia:
   `costo_despido_por_empleado_cop` sale del CST (`data/construir_empresas.py:155-156`) y el veto lo
   cobra. Es el único ranking del proyecto con un dato legal real detrás y **es lo que hay que mostrar**.
3. **El segundo episodio (2024→2025).** Está medido y versionado (`scripts/validate.py:174-179`,
   `momentos_2024.json`: 32,01% → 34,64% = **+2,63 pp con alza de 9,5%**) y **no aparece en
   `VALIDATION.md`** [VERIFICADO por grep: cero coincidencias de `2,63` en ese archivo].
   **Dictamen: REFUERZA la honestidad y DEBILITA el modelo, y por eso hay que publicarlo.** El
   episodio 2025 subió la informalidad; el 2026 la bajó. Un modelo que solo sabe subir acierta el
   signo en 1 de 2 con n = 2 — que es lo que se espera de una moneda. Publicarlo convierte "un mal
   backtest" en "un aparato de medición que se aplicó dos veces". Ocultarlo es el hallazgo.
4. **Ninguna prueba de estabilidad de la dinámica.** `behavior/rondas.py:798-817` etiqueta
   `estabilizada` con un umbral de 2 pp sobre la última variación de **una sola** coordenada (la
   informalidad agregada). `DEFECTOS.md:157-171` reporta reversión entre rondas 2 y 3 en 7 de 9
   políticas. La ronda 3 es un corte de calendario, no un atractor [VERIFICADO en disco + coincidencia
   independiente].

---

## 4 · LOS 3 ARREGLOS

**A · Rebautizar el mapa y decir de qué está hecho** · dueño: **Dani (R4, `web/`) + Juanda (R5, docs raíz)** · **20 min**
- El eje distributivo deja de llamarse "quién no puede pagar" y pasa a **"carga legal por celda:
  sobrecosto prestacional y costo de despido del CST"**. Una línea al pie: *"el orden lo fija la
  formalidad observada en la GEIH y el factor prestacional del CST; el margen sobre nómina es
  uniforme (0,18) y no observado."*
- **Verificación:** `grep -rn "no puede pagar\|quién aprieta" web/` devuelve 0; la nota al pie existe
  en la lámina distributiva.
- **SI NO LO ARREGLAMOS:** un juez con un agente abre `construir_empresas.py:70`, ve que todas las
  empresas tienen el mismo colchón, y pregunta en voz alta *"¿entonces su mapa solo dice que el
  informal es informal?"*. No hay respuesta.

**B · Meter el segundo episodio y la no-cegera en `VALIDATION.md`** · dueño: **Juanda (R5)** · **25 min**
- Dos párrafos: (i) 2024→2025, +9,5% de alza, **+2,63 pp** observados, dirección opuesta al episodio
  2025→2026 (−4,07 pp), con el comando que lo imprime; (ii) *"el pre-registro no fue ciego: `2d4aa7e`
  ya decía que lo que se sabía apuntaba a la rama B"*, con el link a `docs/vet/00-hallazgos.md:44`.
- **Verificación:** `grep -n "2,63" VALIDATION.md` y `grep -n "no fue ciego" VALIDATION.md` devuelven
  ≥ 1 cada uno.
- **SI NO LO ARREGLAMOS:** el jurado encuentra los dos por su cuenta —están en el repo público— y lo
  que era rigor se lee como cifra escondida. Es el único hallazgo del eje B que puede costar el
  proyecto entero en vez de un punto.

**C · Quitar la palabra "cobertura" del número** · dueño: **Juanda (R5, `scripts/`) + Dani (R4, `web/`)** · **15 min**
- En `scripts/validate.py:165-171` y en pantalla, `Cobertura del rango: NO` pasa a **`El observado NO
  cae dentro del rango entre paráfrasis (33,9 pp, N=5, min–max)`**. Sin tocar el cálculo.
- **Verificación:** `python scripts/validate.py --dry` (no llama al LLM) imprime la frase nueva;
  `grep -rn "Cobertura" scripts/ web/` devuelve 0 en contexto de banda.
- **SI NO LO ARREGLAMOS:** basta que un juez pregunte *"¿cobertura de qué nivel?"* para que la barra
  de error, que es lo más honesto que tenemos, quede como el número menos defendible de la lámina.

**Recortes propuestos (nombrarlos es parte del trabajo):** fuera de la demo la curva de cascada como
resultado; fuera `subir_precios` como estrategia visible; fuera cualquier lectura del mapa como
predicción. Dentro: costo de despido del CST, EL NÚMERO con sus dos episodios, y el rango entre
paráfrasis bien nombrado.

---

## 5 · LA PREGUNTA QUE NOS HUNDE

> **"Ustedes dicen que el nivel falló pero el reparto se sostiene. ¿Qué variable de su modelo hace que
> una empresa aguante el alza y otra no — una que NO sea la informalidad que ya traía de la encuesta?"**

- **Por qué duele:** no existe. El margen es `0,18` para las 81 celdas
  (`data/construir_empresas.py:70`), el salario y el tamaño se cancelan algebraicamente en el veto
  (`engine/veto.py:443-445`), y lo que queda correlaciona **0,94** con el `share_formal` de entrada.
  El ranking sectorial observado, además, no se mueve en tres años (ρ ≈ 0,98): la persistencia que ya
  ganó en nivel también gana en reparto.
- **¿El equipo tiene respuesta hoy? No.** La única respuesta honesta disponible es bajar la afirmación
  a *"ranking de carga legal estatutaria"* y decirlo a las 09:30, no en el Q&A.

---

### Lo que quedó sin mirar (caja de 25 min)

- `behavior/rondas.py:334-349` y `:489-513` — la segunda opinión reporta que `tasa_informalidad` no se
  pondera por empleo superviviente, así que una celda que despide media planta sigue aportando la
  misma masa informal. **No lo verifiqué línea por línea.** [SOSPECHA, heredada]. Experimento que lo
  resuelve: correr la ablación con una política que fuerce `despedir` y comprobar si
  `Σw·q/Σw` cambia al mismo tiempo que el empleo.
- `engine/fiscalizacion.py:142-171` — el exponente de visibilidad `α = 1,875` calibrado contra la
  informalidad que el modelo debe reproducir. Lo leí; no lo derivé. Es materia del ADR 0007 y del
  Eje A/próxima corrida.
- Coherencia temporal de `behavior/ablacion.py:71-102` (COP/mes sumado con COP/trimestre). No
  verificado por mí.

---
---

# ANEXO — para iterar después con corridas reales

> **Escrito el 23-ago por la sesión que lanzó el Eje B (Claude Opus 5), no por `juez-cientifico`.**
> Va debajo y **no toca ni una línea del informe de arriba**: el informe es el reclamo del agente,
> esto es lo que la sesión verificó por su cuenta y lo que queda pendiente de corrida.
> Sigue sin ser normativo. Los arreglos los hace el dueño de cada carpeta, en su rama, por PR.

## A · Qué se verificó en disco (independiente del agente)

Un informe de agente es un reclamo, no evidencia. Estas cuatro se comprobaron aparte:

| Afirmación del informe | Estado | Evidencia |
|---|---|---|
| `MARGEN_SOBRE_NOMINA = 0.18` uniforme para las 81 celdas | **CONFIRMADO** | `data/construir_empresas.py:70`, aplicado en `:153` como `flujo_caja = nomina · 0,18`. No hay ninguna otra fuente de caja. |
| El álgebra del sobrecosto en el veto | **CONFIRMADO con una corrección** | `engine/veto.py:443-445`. Ver A.1. |
| `VALIDATION.md` no menciona el segundo episodio | **CONFIRMADO** | `grep -c "2,63\|2\.63" VALIDATION.md` → **0** |
| `VALIDATION.md` no menciona la no-cegera | **CONFIRMADO** | `grep -c "no fue ciego" VALIDATION.md` → **0** |

### A.1 · Corrección al álgebra: falta el término `jornada`

El informe escribe `sobrecosto = en_regla · ingreso · factor · (a/100) · 3`. La línea real
(`engine/veto.py:442-445`) lleva un factor más:

```
jornada    = 1 − reduccion_horas_pct/100          # engine/veto.py:442
sobrecosto = en_regla · ingreso · factor · (a/100) · 3 · jornada
```

**No rescata el veredicto, y conviene saber por qué antes de que lo pregunte un juez:**
`jornada = 1` exactamente para `absorber` y `cumplir` (ninguna de las dos trae
`reduccion_horas_pct`), que son las ramas sobre las que se calculó el ranking. Solo baja de 1 en
`bajar_horas`. Y aun ahí es una **variable de decisión del agente**, no un atributo de la celda:
no introduce heterogeneidad *entre* celdas, que es lo que el veredicto necesitaría para caerse.
La cancelación de salario y tamaño se sostiene.

### A.2 · Un comando del informe no existe

`LOS 3 ARREGLOS · C` propone verificar con `python scripts/validate.py --dry`. **Ese flag no
existe:** `scripts/validate.py` no tiene `argparse` (único `__main__` en `:279`, cero
`add_argument`). El comando correcto para verificar el arreglo C es la inspección estática:

```bash
grep -rn "Cobertura" scripts/ web/     # debe dar 0 en contexto de banda
sed -n '160,175p' scripts/validate.py  # la frase nueva en su sitio
```

## B · Qué árbol se midió, y por qué importa para la fusión

- **Medido: `9218dc3`** — el commit más reciente de `main`, en un worktree de solo lectura.
- **El `PROMPT-B` fija `9cbd6f2`** y ese SHA quedó viejo: el propio PR #29 que trajo el reparto de
  la revisión se mergeó *después*. La diferencia entre los dos es **solo `docs/vet/revision-3ejes/`**,
  no toca código, así que ningún hallazgo de este informe cambia.
- **Para el que fusione:** si los ejes A y C se lanzaron con el SHA literal del prompt, los tres
  informes no están midiendo el mismo árbol. Verificarlo antes de fusionar, o la regla de "lo que
  aparece en dos listas va primero" compara contra árboles distintos.

## C · Pendientes que solo se resuelven corriendo

Ordenados por cuánto mueven el veredicto. **Ninguno se corrió en esta sesión.**

> **Antes de correr nada:** `make run` **no existe todavía** — `scripts/run_simulacion.py` no está
> en el repo y el target imprime `PENDIENTE`. Las corridas reales de hoy entran por
> `behavior/demo.py`, `behavior/ablacion.py`, `scripts/barrido_politicas.py` y `scripts/validate.py`.
>
> **Costo:** sin `--llm` todo corre por la **ablación determinista** y cuesta **$0**, repetible sin
> límite. Con `--llm` se gasta del presupuesto de $50/persona; `barrido_politicas.py` acepta
> `--tope` en USD.
>
> **Trampa de nombre:** `demo.py --reparto` **no** es el mapa distributivo. Es "repartir las
> paráfrasis por peso poblacional" (B1). Quien vaya a atacar C.1 con ese flag va a medir otra cosa.

### C.1 · El experimento que decide el veredicto principal — margen heterogéneo

- **Qué se resuelve:** si el ranking de celdas es un resultado del modelo o un re-plot de `share_formal`.
- **Cómo:** reemplazar el `0,18` constante por un margen por celda con fuente (EAM, Supersociedades,
  o el que haya) y recalcular Spearman `ranking ↔ share_formal`. Es cambio en `data/` — **dueño: Alejo (R1)**.
- **Qué resultado cambiaría el veredicto:** que la correlación baje sustancialmente de **0,94**.
  Si se queda arriba de ~0,85, el mapa sigue siendo endógeno al insumo y hay que rebautizarlo igual.
- **Costo: $0** (recálculo sobre parquet, sin LLM).

### C.2 · La ponderación de `tasa_informalidad` por empleo superviviente — [SOSPECHA, heredada, SIN VERIFICAR]

- **Qué se resuelve:** si una celda que despide media planta sigue aportando la misma masa informal
  al agregado (`behavior/rondas.py:334-349`, `:489-513`). Si es cierto, **contamina EL NÚMERO**, no
  solo el mapa.
- **Cómo:** corrida de ablación con una política que fuerce `despedir`, comprobando si `Σw·q/Σw`
  se mueve al mismo tiempo que el empleo.
  ```bash
  python -m behavior.ablacion --real --aumento 23
  ```
- **Costo: $0.** **Dueño: Nico (R3).** Es el pendiente más barato con más consecuencia.

### C.3 · El exponente de visibilidad α = 1,875 — leído, no derivado

- **Qué se resuelve:** si α está calibrado contra la informalidad que el modelo debe reproducir
  (`engine/fiscalizacion.py:142-171`, ADR 0007). Si lo está, es circular.
- **Cómo:** `python scripts/calibrar_visibilidad.py` y contrastar con `data/calibracion_visibilidad.json`.
- **Costo: $0.** **Dueño: Manuel (R2).** Materia compartida con el Eje A.

### C.4 · Coherencia temporal en `behavior/ablacion.py:71-102` — COP/mes sumado con COP/trimestre

- **Qué se resuelve:** un error de unidades de factor 3 en la ablación, que es justo el camino
  determinista con el que se reproduce todo sin API key (ADR 0009).
- **Costo: $0**, es lectura. **Dueño: Nico (R3).**

### C.5 · La cascada como mecanismo, demostrada en vez de afirmada

- **Qué se resuelve:** la lámina puede decir "esto es el mecanismo, y así se ve cuando lo apagamos"
  en vez de afirmar la cascada como resultado (que el backtest ya falsó).
- **Cómo:** el flag B4 ya existe — congela `p(sanción)` en su valor de ronda 0:
  ```bash
  python -m behavior.demo --real --sin-cascada --aumento 23
  python -m behavior.demo --real --aumento 23            # el contraste
  ```
- **Costo: $0** sin `--llm`. **Dueño: Nico (R3) + Dani (R4)** para la lámina.

### C.6 · El segundo episodio, con el comando que lo imprime

- **Qué se resuelve:** el arreglo **B** necesita la cifra citable, no la recordada.
- **Cómo:** `python scripts/validate.py` (sin flags) — el segundo episodio se computa en `:174-179`.
- **Costo: $0.** **Dueño: Juanda (R5).**

### C.7 · La banda de 33,9 pp, medida de nuevo

- **Qué se resuelve:** hoy el rango es min–max de N=5 paráfrasis. Con N mayor deja de ser
  "el mínimo y el máximo que salieron" y empieza a poder llamarse algo.
- **Cómo:** `python -m behavior.demo --real --llm --parafrasis 9 --tope 5`
- **Costo: SÍ gasta LLM.** Es el único pendiente de esta lista que toca presupuesto. **Dueño: Nico (R3).**

## D · Lo que este eje NO miró

Queda declarado para que la fusión no lo dé por cubierto:

- **La pantalla.** Qué dice cada leyenda de `web/` es del **Eje C**. Este eje solo marcó por `grep`
  que tres componentes mencionan cascada; el texto exacto no se leyó.
- **La ejecución.** Si la simulación corre, escala y es reproducible es del **Eje A**.
- **Cualquier corrida.** Este informe es 100% lectura estática más 4 cálculos sobre
  `data/empresas.parquet` y `data/momentos*.json`. **Cero corridas del motor**, cero llamadas al
  proveedor de LLM, cero gasto.
