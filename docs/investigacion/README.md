# `docs/investigacion/` — El fundamento del backend

**Dueño: Manuel (R2)** · rama `rol/backend`

Tres esferas. Existen porque el motor no puede apoyarse en *"yo creo"*: cada pieza de
`engine/` tiene que poder trazarse a algo que ya está probado afuera, o quedar marcada
como supuesto nuestro con su sensibilidad medida.

| Esfera | Archivo | Pregunta que responde |
|---|---|---|
| **1 · Teórica** | [`1-teorica.md`](1-teorica.md) | ¿Qué ya está probado en este campo, para no inventar desde cero? |
| **2 · Tools** | [`2-tools.md`](2-tools.md) | ¿Qué herramientas y estándares reales existen, y en cuáles nos apoyamos? |
| **3 · Live** | [`3-live.md`](3-live.md) | ¿Quién está vivo hoy, cómo lo vende y cómo resuelve lo que nosotros resolvemos? |

## Esto no es `docs/fuentes/`

`docs/fuentes/` son los **cinco insumos individuales escritos antes de que la idea
existiera**. Son materia prima histórica: buenos, verificados, y organizados alrededor de
*"qué podríamos construir"*.

Esta carpeta está organizada alrededor de **el motor que sí vamos a construir**. Consolida
lo que sirve de aquellos cinco insumos, lo extiende con investigación nueva, y descarta
explícitamente lo que no aplica. Donde difieran, manda esta carpeta para decisiones de
`engine/` y `api/`; `docs/PLAN.md` sigue mandando para alcance de producto.

## Reglas de esta carpeta

1. **Nada entra sin URL abierta.** Regla heredada de `docs/PLAN.md` §4.1 e insumo de
   Manuel §4.8. Una dependencia o una cita alucinada descubierta a las 4am cuesta el proyecto.
2. **Toda entrada dice qué NO nos sirve.** Es la casilla que separa fundamentar de decorar,
   y es obligatoria en las tres esferas. El resto del formato se adapta al material:
   la esfera 1 usa *qué prueba · qué nos sirve · **qué NO** · dónde aterriza*; la esfera 2 usa
   el build-vs-buy del repo (*qué ahorra · **qué construiríamos igual o qué NO nos da** ·
   veredicto*); la esfera 3 usa *qué vende · a quién · **cómo responde "¿por qué te creo?"** ·
   dónde no competimos*. En los tres casos la casilla del medio es la del "no".
3. **Lo no verificado se marca `⚠️` y no se enuncia como hecho.** Tampoco se enuncia en el pitch.
4. **La vigencia importa.** Un dato de 2015 se cita con su año, no como si fuera de hoy.

## Cómo se usa

- Antes de escribir una función de `engine/`, busca su ancestro acá. Si no lo tiene, es un
  supuesto nuestro: va con `# SUPUESTO:` en el código y con sensibilidad medida.
- El mapa de *teoría → archivo → función → test* vive en [`engine/MODELO.md`](../../engine/MODELO.md).
- La idea completa, llenada contra la rúbrica de viabilidad, vive en [`docs/IDEA.md`](../IDEA.md).

## Estado de verificación de las fuentes

Comprobado el 2026-08-22 sobre las **50 URLs citadas** en esta carpeta, en `docs/IDEA.md`,
en `engine/MODELO.md` y en los ADR 0005-0009:

| Resultado | Cuántas | Qué significa |
|---|---|---|
| ✅ Abren (HTTP 200) | 45 | Verificadas |
| 🔒 Editorial bloquea el acceso automático (HTTP 403) | 5 | **No están muertas.** Son `science.org`, `pnas.org`, `journals.uchicago.edu`, `sciencedirect.com` y `oecd.org`, que bloquean clientes no-navegador. Un humano las abre |

A las cinco bloqueadas se les agregó **espejo de acceso abierto o ficha bibliográfica**
(NBER, KNAW, RePEc) donde existía, para que cualquiera pueda leer el trabajo y no solo la
referencia. Reproducir la comprobación:

```bash
grep -rhoE "https?://[^ )\`\"]+" docs/investigacion/ docs/IDEA.md engine/MODELO.md docs/adr/000[5-9]*.md \
  | sort -u | while read -r u; do
      printf "%s %s\n" "$(curl -s -o /dev/null -w '%{http_code}' -L --max-time 15 -A 'Mozilla/5.0' "$u")" "$u"
    done
```
