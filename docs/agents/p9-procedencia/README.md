# Auditorías del verificador `P9 · procedencia`

Informes que trazan **cada número que la pantalla le muestra a un humano hasta su fuente última**, y lo etiquetan: `DATO GEIH` · `NORMA citada` · `CALCULADO` (¿por qué script?) · `SUPUESTO` (¿marcado o no?).

P9 sale del reparto de verificadores del vet ([`docs/vet/03-arranque-por-track.md:211-216`](../../vet/03-arranque-por-track.md)) y le toca a **R1 / Alejo**, por una razón concreta: es quien mejor conoce la cadena de datos, que es donde P9 empieza.

## Qué lo separa de los otros cuatro

| | `juez-hackathon` | `juez-tecnico` | `juez-cientifico` | `peeky` | **`P9 procedencia`** |
|---|---|---|---|---|---|
| Pregunta | ¿alguien usa esto? | ¿esto corre y escala? | ¿esto es cierto? | ¿es consistente consigo mismo? | **¿de dónde salió este número?** |
| Vara | el mercado | la industria | la matemática | el propio repo | **la cadena de custodia del dato** |
| Empieza en | el pitch | la arquitectura | las fórmulas | las costuras | **el píxel, y va hacia atrás** |

La frontera con `peeky` es la que más se confunde: `peeky` cruza dos afirmaciones del repo y muestra que no pueden ser ciertas a la vez. **P9 toma una sola cifra y la persigue hacia atrás hasta que se acaba el rastro** — y su hallazgo tipo no es *"esto se contradice"* sino *"esto se afirma en voz alta y no se puede rastrear"*.

Su salida obligatoria tiene dos secciones que ningún otro verificador produce:

1. **"Los que matan en el Q&A"** — números afirmados en voz alta cuya procedencia no se pudo establecer, ordenados por qué tan citables son en un pitch.
2. **"Lo que el equipo hizo mejor de lo esperado"** — obligatoria por diseño. Un auditor que solo reporta agujeros deja de ser leído, y la cadena que **sí** está cerrada es material de pitch que conviene decir en voz alta.

## Qué NO son estos archivos

No son una evaluación externa, no son la opinión de ningún jurado real, y no intentan decirle a nadie qué concluir sobre el proyecto. Son el equipo buscándose los números indefendibles antes de que se los encuentre un revisor con el repo abierto.

Y **no son normativos**: `AGENTS.md` manda que un informe de agente es *"un hallazgo con fecha, no una decisión"*. Lo que se confirme y cambie el modelo se gradúa a un ADR de `docs/adr/` o a una fila del registro de supuestos de `engine/MODELO.md`. Si no se gradúa, no pasó.

## Convenciones

- **Nombre:** `AAAA-MM-DD-HHMM-<alcance>.md`, uno por corrida. **Nunca se sobrescribe un informe anterior**; cada uno abre comparándose con el previo.
- **Encabezado:** blockquote con alcance · commit · rama · comandos ejecutados **con su resultado, incluidos los que fallaron** · segunda opinión · veredicto en una frase.
- **Cada hallazgo:** `CRÍTICO|ALTO|MEDIO` · `CONFIRMADO|PLAUSIBLE` · evidencia con `archivo:línea` y cita literal · etiqueta de origen `[disco]` / `[disco, medido]` / `[pendiente]`.
- **Segunda opinión** (`mcp__codex__codex`, read-only): las divergencias se reportan **como divergencia, nunca promediadas**.
- El verificador **solo lee**. Su única escritura permitida es su propio informe.

## Informes

| Fecha | Alcance | Veredicto en una línea |
|---|---|---|
| [2026-08-23 00:27](2026-08-23-0027-repo.md) | repo | La cadena de datos duros no tiene hueco; el riesgo está en el último tramo — la única cifra en pesos de la pantalla se calcula en el navegador, y `web/enjambre/` tiene cero `// SUPUESTO:`. |
