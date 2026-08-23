# ADENDA al Eje C — lo que el juez ve NO es lo que el agente revisó

> **Escrita el 23-ago 04:30 por Manuel (R2), que lanzó el Eje C.** Verificada a mano: navegador
> sobre el deploy vivo + `git` sobre la rama desplegada. Va aparte del informe del agente
> ([`2026-08-23-eje-C-pantalla.md`](2026-08-23-eje-C-pantalla.md)) porque **no lo corrige: lo
> reordena**. El agente midió `web/` en `main`. El juez del domingo mide otra cosa.
>
> **No es normativo.** Es un hallazgo con fecha. Los arreglos los hace el dueño de `web/` (Dani),
> en su rama, por PR.

---

## El hecho, en una frase

**La URL que el equipo va a mostrar corre un commit viejo: le faltan 15 commits que ya están en
`main`, y esos 15 son justo los que arreglaban lo que el Eje C vino a buscar.**

Verificado, con los comandos:

```
git merge-base f9e705c origin/rol/integracion-deploy   →  1aef592
git log --oneline f9e705c..origin/rol/integracion-deploy  →  (vacío)
```

El merge-base **es** la punta de la rama desplegada. O sea: la rama del deploy es un **ancestro
estricto** de `main`. No es una rama divergente que haya que reconciliar; es `main` de hace rato.
`render.yaml:32,52` fija `branch: rol/integracion-deploy` para los dos servicios.

Entre los 15 commits que el deploy NO tiene:

| Commit | Qué arreglaba |
|---|---|
| `024340b` | «reporte: la procedencia vuelve, y **la cascada deja de ser un hallazgo**» |
| `c6aa889` | «huérfanos y laboratorio: que cada archivo diga si se monta» |
| `e4ff8a2` | «paneles: el **rótulo de modo** deja de quedar debajo de las burbujas» |
| `3b58866`, `c8b2df3` | el logo de HIVE |

## Qué implica, pregunta por pregunta del PROMPT-C

- **#3 · la ruta del recorte:** ya está recortada, y no por decisión. `/reporte` responde **404** y
  `/laboratorio` responde **404** en producción. La rama desplegada tiene un solo archivo de ruta
  (`web/enjambre/app/page.tsx`). La pregunta «¿cuál pantalla mostrarías?» está contestada por los
  hechos: solo existe `/`.
- **#4 · procedencia:** `Paneles/Procedencia.tsx` **no existe** en la rama desplegada. El panel
  DATO / NORMA / CALCULADO / SUPUESTO que el agente auditó no está en pantalla. Lo que hay vivo es
  una línea de pie: «celdas empleadoras GEIH-DANE · cifras de esta corrida · masa salarial y
  bajo-mínimo con supuesto declarado».
- **#8 · el error del backtest:** el agente lo ubicó en `/reporte`. `/reporte` es 404. **En vivo,
  los 37,37 pp no aparecen en ninguna parte.** La mitad del producto, según la espina, hoy es
  inalcanzable desde la URL.
- **#9 · la cascada:** el agente listó `Metricas.tsx` y `CurvaBrecha.tsx` como **huérfanos** (en
  `main` lo son: `Metricas.tsx:3` se autodeclara muerto). **En la rama desplegada están vivos y
  montados**: `Simulacion.tsx:43` monta `<Metricas />`, y `Metricas.tsx:84` monta `<CurvaBrecha />`.
  Es decir: el código que el informe manda borrar de la demo es exactamente el que el juez ve.

## Lo que se lee en pantalla, textual, corriendo la simulación en vivo

Corrida real del 23-ago 04:23, +23,0 %, deploy `https://enjambre-web.onrender.com`:

1. **La contradicción que hunde, y está en la MISMA pantalla, sin un clic:**
   - «**Población decidida por LLM (top-K) · 80,2 %**» (`Paneles/Metricas.tsx:74`)
   - «corrida terminada · 0,6 s · **0 llamadas API · $0.00 USD**» (`Paneles/BarraTiempo.tsx:69`)

   En cristiano: la pantalla dice que un LLM decidió por el 80 % de la población, y tres centímetros
   más abajo dice que no se llamó al LLM ni una vez. Las dos son ciertas (el default vivo es
   `modo=reglas`), y juntas se leen como que el proyecto miente. Es la pregunta #6 del PROMPT-C
   contestada de la peor forma posible.

2. **La cascada falsada, dibujada como el resultado:**
   «**LA BRECHA · PROYECCIÓN OFICIAL VS CORRIDA REAL** / oficial 30,6 % / real 88,3 %»
   (`CurvaBrecha.tsx:40`, `:63`). El comentario del propio archivo la llama «la cascada real»
   (`CurvaBrecha.tsx:3-4`). Y la cifra de portada: «**+57,7 pp sobre la proyección oficial**»
   (`Hero.tsx:48`). La «proyección oficial» es la ronda 0 del propio modelo (`Relato.tsx:53`).

3. **La informalidad salta de 30,6 % a 88,3 %** en 3 rondas. Un juez que conoce Bogotá rechaza ese
   número de entrada, y no hay banda que lo acompañe: «banda degenerada: una sola trayectoria».

4. **Titulares inventados en el producto que vende «publicamos nuestro error»:** «EL CENTINELA ·
   MEDIO FICTICIO · RONDA 3» con el titular «La sombra se traga 62,5 % de la nómina».

5. **Cero copy del problema** antes de la corrida: el menú dice «¿Qué política quieres estresar? ·
   81 celdas empleadoras · 3,2 millones de trabajadores representados». Nada sobre que la proyección
   oficial supone cumplimiento. Confirma el hallazgo #1 del agente, en vivo.

6. El botón «SIMULAR POLÍTICA PERSONALIZADA · BLOQUEADO · PRÓXIMA ITERACIÓN» está vivo en producción.

## El cronómetro (pregunta #2), que cambia de signo

El agente estimó 10-14 min y lo marcó [SOSPECHA]. **Medido: 0,6 s.** No hay problema de tiempo,
y esa es la mala noticia: es rápido **porque no está haciendo lo que el pitch dice que hace**.
Confirmado dos veces por vías independientes:

```
python3 scripts/humo_deploy.py https://enjambre-web.onrender.com
→ OK · la cadena completa transmite (0.7s, modo reglas)
→ 243 decisiones · 4 rondas · 0 llamadas a la API · $0.0000
→ final: informalidad 31.01% · banda degenerada [31.01%, 31.01%]
```

### Y esto es lo que de verdad hunde: **la demo es una repetición grabada**

No es que el deploy corra en modo reglas. **Corre en modo LLM y no llama al LLM ni una vez**,
porque el 100 % de las decisiones sale de una caché en disco. La API viva lo dice sola:

```
curl -N ".../api/simulaciones/flujo?aumento_pct=23&seed=42"
event: inicio → {"modo": "llm", "parafrasis": 1, "n_arquetipos": 81}
event: fin    → {"segundos": 0.6, "modo": "llm", "llamadas_api": 0, "gasto_usd": 0.0,
                 "cache_aciertos": 117, "cache_fallos": 0}
```

**117 aciertos de caché, 0 fallos.** El escenario del pitch (23 %, seed 42) está grabado entero.
Nada se le pregunta al modelo en vivo.

**Y el slider es una trampa.** Con un valor que no está en la caché, la pantalla se queda muda:

```
curl -N ".../api/simulaciones/flujo?aumento_pct=17&seed=42"
→ 04:26:34 … 04:28:04 · 90 segundos, CERO bytes. Ni el evento `inicio`.
```

Con 23 % el `inicio` llega instantáneo. Con 17 % no llega nada en 90 s. En cristiano: **si un juez
mueve el slider, la demo se queda en negro y no vuelve.** Esto no se arregla subiendo una API key:
con key sería peor, porque entonces sí llamaría 81 celdas × 4 rondas en serie y tardaría minutos
en vez de segundos. La caché es lo único que hace que la demo quepa en el pitch.

(Nota de entorno, no defecto del repo: `humo_deploy.py` falló primero por certificados locales de
Python 3.14 y reportó «ni /api/poblacion ni /poblacion respondieron 200», que es un mensaje que
apunta al deploy cuando el problema era la máquina. Se resolvió con `SSL_CERT_FILE=$(python3 -m
certifi)`. Es de `scripts/`, dueño R5, y es menor.)

## El arreglo que manda sobre los tres del agente

**A0 · Desplegar `main`.** Dueño: R5 (integración/deploy), no `web/`. **5 minutos.**
Cambiar `branch:` en `render.yaml:32,52` a `main`, o mergear `main` en `rol/integracion-deploy`.
**Verificación:** `curl -o /dev/null -w "%{http_code}" https://enjambre-web.onrender.com/reporte`
devuelve `200`, y `grep "logo pendiente"` sobre el HTML servido no encuentra nada.

**SI NO LO ARREGLAMOS:** los tres arreglos del agente se aplican sobre código que el juez nunca va a
ver, y el domingo se muestra una versión sin procedencia, sin `/reporte`, sin el error del backtest,
y con la cascada falsada dibujada como resultado.

> **Ojo, y esto no es un detalle:** A0 no es gratis. Desplegar `main` hace que el juez vea el `web/`
> que el agente acaba de auditar, con sus 4 mentiras y sus 5 huérfanos intactos. El orden correcto es
> **A0 primero** (para que los arreglos caigan donde se ven) y los tres del agente encima. A0 solo
> mueve el problema si se hace último.

**A0-bis · Que el slider no pueda salirse de lo cacheado, o que avise.** Dueño: `web/` (Dani) con
R5. **15 minutos.** Dos opciones honestas: (a) fijar el slider a los valores cacheados y decirlo
(«escenarios pregrabados»), o (b) dejarlo libre y mostrar «esto tarda ~N minutos y cuesta $X» antes
de arrancar. **Verificación:** mover el slider a 17 % y que la pantalla diga algo en menos de 3 s.
**SI NO LO ARREGLAMOS:** el juez mueve el slider, la pantalla se queda en negro 90 segundos, y ahí
se acabó el pitch.

## La pregunta que nos hunde, versión deploy

> **«¿Por qué la pantalla dice que un LLM decidió el 80 % de la población y al lado dice 0 llamadas
> a la API y $0.00? ¿Me está mostrando una corrida o una grabación?»**

Hoy la respuesta honesta es: una grabación. 117 aciertos de caché, 0 fallos, 0 llamadas. El rótulo
del 80 % describe el diseño del sistema, no la corrida que el juez acaba de ver. Y el único valor
del slider que responde es el que está grabado.
