# Plan de ejecución visual — la pieza

**Dueño: Dani (R4)** · rama `rol/interfaz`
Reemplaza el enfoque de `web/DISENO.md` §"proceso". Las decisiones de contenido de ese
documento (celda, incumplimiento nuevo, vocabulario, honestidad geográfica) siguen vigentes.

> **Objetivo declarado:** una web reactiva de nivel awwwards. No un dashboard. Una pieza
> donde se entienda, sin manual, por qué esta simulación importa.

---

## 0. La verdad técnica, antes de repartir trabajo

Sitios como igloo.inc o lusion.co no son video generado ni plantillas: son **WebGL con
shaders escritos a mano**, geometría instanciada en GPU, y un timeline que orquesta cámara,
materiales y DOM al mismo tiempo. Eso define quién puede hacer qué.

| Herramienta | Qué SÍ entrega | Qué NO entrega — no insistir |
|---|---|---|
| **Claude Design** | Artboards estáticos del *chrome*: retícula, escala tipográfica, tokens de color, composición de paneles, estilo de las gráficas, la pantalla de entrada, los estados vacío/carga/error | El mapa. Cualquier animación. Cualquier shader. Nada con datos |
| **Higgsfield** (o Midjourney / nano-banana) | Los 4 retratos de las historias. Texturas si las quisiéramos como imagen | Nada interactivo, nada data-driven, ni un frame del mapa. Genera píxeles, no sistemas |
| **Claude Code** | **Todo lo que corre**: la escena 3D, los shaders, el timeline, la cámara, el dashboard, los charts, la integración con el motor | — |
| **Descarga (no IA)** | La geometría real de Bogotá y sus vecinos | — |

**¿Hay física?** No hay cuerpos rígidos ni colisiones, pero sí hay ecuaciones y son las que
hacen la diferencia entre "se ve bien" y "se siente vivo":

- **Oscilador armónico amortiguado** (spring) para el pop de cada punto y para la cámara.
  Es lo que da el rebote apenas perceptible que separa un movimiento vivo de un `ease-out`.
- **Curl noise** para una deriva mínima en reposo. Sin esto, una nube de puntos quieta se ve muerta.
- **Interpolación en shader** de color y escala: la GPU hace 45.000 puntos sin despeinarse.
- **Stagger por atributo** (presión económica), no por índice: el orden de la cascada significa algo.

**Sobre la ambición, una vez y sigo:** un sitio awwwards es de dos a cuatro semanas de un
especialista. En este hackathon, con freeze en H+28, lo alcanzable es *notoriamente superior
al resto del track y memorable* — no lusion.co. El plan de abajo está ordenado para que si se
corta por tiempo, se corte por el final y lo que quede siga siendo bueno.

---

## 1. Qué es el producto, redefinido

Tres actos, uno detrás de otro, sin cortes de pantalla:

**Acto I · El planteamiento.** Pantalla blanca, casi vacía. El usuario compone una situación
en lenguaje natural: *política pública + efecto fiscal directo + población afectada*. Enter.

**Acto II · El nacimiento del mundo.** Los puntos empiezan a aparecer con pop, de a pocos,
y la cámara hace **zoom out** a medida que aparecen más. Termina con la ciudad completa
formada: el polígono de Bogotá delimitado, y alrededor los vecinos rotulados —
**Chía** al norte, **Mosquera** y **Funza** al occidente, **Soacha** al sur, **La Calera** al
oriente. Ahí se sabe que es Bogotá sin haber afirmado dónde vive nadie.

**Acto III · La simulación.** Mapa interactivo: zoom, pan, hover. Corren las rondas, la
cascada se propaga, el dashboard reacciona en vivo. El usuario puede volver a intervenir.

### El compositor de lenguaje natural — cómo se resuelve honestamente

El motor recibe una política **estructurada**, no texto. La solución que da la sensación sin
la mentira: tres ranuras que se leen como una frase, más un campo libre opcional que una
llamada a Haiku traduce a esos parámetros, mostrando en pantalla la traducción antes de correr.

Y el caso "no cabe" deja de ser una falla y se vuelve **un momento de credibilidad**: si
alguien escribe *"simula una epidemia"*, el sistema responde, diseñado y elegante, que eso
no cabe en este motor y por qué (`docs/PLAN.md` §4.2). Un juez que vea eso entiende que
sabemos dónde están nuestros límites. Es de los mejores 15 segundos posibles del demo.

---

## 2. Stack

| Capa | Qué | Por qué |
|---|---|---|
| Base | Next.js + **TypeScript** | Ya decidido (D7). TS porque los contratos son el eje del trabajo en paralelo |
| 3D | **React Three Fiber** + drei | Three.js con el modelo mental de React. Instancias en GPU |
| Shaders | GLSL propio (vertex + fragment) | Es el 70% de la sensación. No hay atajo |
| Post | `@react-three/postprocessing` — bloom sutil | Un bloom bien calibrado es la mitad del "se ve caro" |
| Timeline | **GSAP** | Un reloj maestro que manda sobre cámara, shaders y DOM a la vez |
| Estilos | **Tailwind** + CSS modules para lo específico | Velocidad sin pelear con la cascada |
| Charts | SVG propio + Framer Motion | Recharts se ve a Recharts. A este nivel, los charts se dibujan |
| Estado | Zustand | Ligero, sin ceremonia |
| Scroll | Lenis, solo si hay narrativa por scroll | Decisión abierta (pregunta 4) |
| Datos | `contracts/ronda.json` → Supabase Realtime | Sin cambios respecto al plan |

---

## 3. Fases, con entregable verificable cada una

### Fase 0 · Referencias y decisiones — **Dani, ~1 hora. Bloquea todo lo demás**
No es papeleo: sin esto, todos los demás pasos adivinan.
- **Salida:** carpeta `web/referencias/` con 8–12 capturas o clips de **momentos específicos**
  que te gustan (no sitios completos: "este pop", "esta cámara", "esta transición").
- Nombre del producto decidido.
- Tipografía elegida (ver assets).

### Fase 1 · Assets duros — en paralelo con la fase 2
Ver la tabla de la sección 4. El único bloqueante real es **la geometría de Bogotá**.

### Fase 2 · Claude Design — el chrome, no el mapa
- **Entrada:** las referencias de la fase 0 + un prompt que yo escribo.
- **Salida:** artboards de → pantalla de entrada (Acto I) · dashboard en simulación ·
  estilo de las tres gráficas · panel de historia · estados de vacío, carga y error ·
  la escala tipográfica y los tokens de color.
- **Explícitamente fuera:** el mapa. Design no lo puede juzgar y pedírselo desperdicia la herramienta.
- **Verificación:** los tokens salen de ahí y se pegan como variables CSS. Si un artboard no
  se puede traducir a tokens, no sirve.

### Fase 3 · El motor visual — Claude Code, es el corazón
Cinco sub-etapas, cada una abrible y juzgable por separado:

| # | Qué | Cómo se verifica |
|---|---|---|
| 3.1 | Escena R3F + 45.000 puntos instanciados + shader de pop con spring | Abre y los puntos nacen con rebote, a 60fps |
| 3.2 | Cámara: el zoom-out del Acto II, más zoom/pan libres del Acto III | Se puede acercar hasta ver puntos individuales |
| 3.3 | Campo de densidad en GPU (render a textura + blur + composición) | La silueta emerge, sin granulado y sin mancha |
| 3.4 | Cascada: transición por rondas con stagger por presión, en shader | Se ve propagarse, no parpadear |
| 3.5 | Interacción: hover sobre una zona → qué sector es, qué le pasó | El mapa responde al mouse |

**Nota de escala:** con GPU, 1 punto = 100 personas (≈45.000 puntos) en vez de 1.000. Diez veces
más denso, mismo costo. Cambia por completo cómo se lee.

### Fase 4 · El chrome reactivo — Claude Code
El compositor de lenguaje natural, el dashboard, las gráficas animadas, la historia con cara.
Se construye contra los artboards de la fase 2.

### Fase 5 · Datos reales
Cambia la fuente: `contracts/ronda.json` real + Supabase Realtime. Nada visual se toca acá.

### Fase 6 · Pulido
Micro-interacciones, sonido (si entra), estados de carga diseñados, **escenarios del pitch
precomputados** para que nada dependa de una corrida en vivo.

**Orden de corte si falta tiempo:** cae la 6, luego 3.5, luego el campo libre del compositor
(quedan las tres ranuras). Las fases 3.1–3.4 son el piso: sin eso no hay pieza.

---

## 4. Lista de assets — qué necesito, con qué se hace, quién

| # | Asset | Qué es exactamente | Con qué | Quién | Bloquea |
|---|---|---|---|---|---|
| 1 | **Geometría de Bogotá** | GeoJSON del polígono del D.C. y, si se puede, de las 20 localidades | **Descarga, no IA.** Datos Abiertos Bogotá (IDECA) o el Marco Geoestadístico Nacional del DANE. Hay que verificar el formato al bajarlo | Dani | **Fase 3.3** — es el bloqueante crítico |
| 2 | **Vecinos** | Polígonos y centroides de Soacha, Chía, Mosquera, Funza, Cota, La Calera, Cajicá, Sibaté | Mismo origen (municipios de Cundinamarca) | Dani | Fase 3.2 |
| 3 | **Tipografía** | Una display con carácter + una de texto con cifras tabulares | Fontshare o Google Fonts. Candidatas a mirar: Satoshi, General Sans, Instrument Serif, Newsreader. **Verificar licencia** | Dani decide | Fase 2 |
| 4 | **Retratos** | 4 retratos, mismo estilo, gente colombiana verosímil, cuadrados, fondo neutro | **Higgsfield** / Midjourney / nano-banana | Dani genera | Fase 4 |
| 5 | **Referencias** | 8–12 capturas o clips de momentos concretos que te gustan | Grabación de pantalla tuya | Dani | **Fase 0 — bloquea el prompt de Design** |
| 6 | **Nombre + wordmark** | El nombre del producto | Decisión de equipo | Equipo | Fase 2 |
| 7 | **Sonido** (opcional) | 3–4 micro-sonidos: pop, transición de ronda, hover | Freesound o generador de SFX | Dani | Fase 6 |
| 8 | Video de respaldo | La demo grabada antes de pulir | OBS. Nunca generado | Juanda (ya en `PLAN.md`) | — |

**Texturas:** no se generan como imagen. El grano y el ruido salen procedurales en el shader —
pesan cero, escalan a cualquier pantalla y se ven mejor.

**Sobre los retratos, una advertencia:** son caras generadas que ilustran arquetipos. Van
rotuladas como ilustrativas, siempre. Presentarlas como personas reales de la GEIH sería
exactamente el tipo de cosa que este proyecto se comprometió a no hacer.

---

## 5. Cómo se mezcla todo al final

```
Fase 0 (referencias) ──┬──▶ prompt de Claude Design ──▶ artboards ──▶ tokens CSS ──┐
                       │                                                            │
Assets 1,2 (geometría) ─────────────────────────────────────┐                       │
Asset 3 (tipografía) ───────────────────────────────────────┼───────────────────────┤
Asset 4 (retratos) ─────────────────────────────────────────┤                       │
                                                            ▼                       ▼
                                              Fase 3 · motor visual (R3F+GLSL) → Fase 4 · chrome
                                                                                    │
                                              Fase 5 · datos reales ────────────────┤
                                                                                    ▼
                                                                          Fase 6 · pulido → deploy
```

El punto de unión es **el sistema de tokens**: Design produce los valores, el motor visual los
consume como uniforms del shader y el chrome como variables CSS. Un solo lugar donde vive el
color, y el mapa y el dashboard nunca se desincronizan.

---

## 6. Lo que se arregla del prototipo anterior

| Falla | Causa | Cómo se resuelve |
|---|---|---|
| La curva salta y desaparece | Se reasignaba `canvas.width` cada frame → relayout del panel → salto de scroll | Dimensionar una sola vez, en resize |
| Los puntos ya están ahí | No había nacimiento, solo recoloreo | Pop con spring, aparición escalonada, zoom-out sincronizado |
| No hay zoom | No se implementó | Cámara con zoom/pan desde 3.2 |
| No se siente Bogotá | Silueta que emergía de una mancha, sin referencias | Polígono real delimitado + vecinos rotulados |
| Estático | Sin deriva, sin cámara, sin reacción al mouse | Curl noise en reposo, cámara viva, hover |
| Pobre como dashboard | Se priorizó el instrumento sobre la pieza | Fase 2 dedicada al chrome, con artboards |

---

## 7. Sigue vigente de `web/DISENO.md`

El color mide **incumplimiento nuevo**, no informalidad total (con la medición que lo respalda) ·
el vocabulario del glosario · la posición no es geográfica y se declara en pantalla ·
la banda de incertidumbre en todo número · sin auth ni registro.
