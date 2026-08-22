# Prompt para la sesión de Claude Code de ALEJO (pegar completo como primer mensaje)

Estoy en un hackathon de 36 horas (PlatanusHack 26 Bogotá, track Simulations). El equipo construye un simulador de políticas públicas que responde "¿cuánta gente cumple la política y a quién le cae encima?", con población real de la GEIH del DANE, un motor determinista con veto de factibilidad, una capa LLM que descubre estrategias de adaptación, y rondas de mejor respuesta que producen una cascada de evasión. Caso demo: el aumento del salario mínimo del 23% en Bogotá.

**Antes de escribir una línea de código, lee:** `docs/PLAN.md` (secciones 1.1, 4, 5 y 6), `docs/ROLES.md` (sección Alejo) y `docs/FLUJO.md`.

## Mi rol

Soy **R1 · Datos/población**. Soy el **camino crítico** del proyecto: sin mis datos no hay proyecto.

- **Dueño exclusivo de:** `data/` y `contracts/`. NO toques `engine/`, `api/`, `behavior/`, `web/` ni los docs raíz.
- **Rama:** `rol/datos`. Créala si no existe. Commits pequeños; **PR a `main` mínimo cada 6 horas** (nadie pushea directo a `main` — ver `AGENTS.md`).
- Todo supuesto que tomemos se comenta en el punto exacto con el prefijo `# SUPUESTO:`.

## Orden de trabajo (estricto)

1. **AHORA (H+0 a H+2):** registrarme en `microdatos.dane.gov.co` (registro gratuito) y descargar la GEIH más reciente que tenga el módulo de **empleo informal y seguridad social** (catálogos 2022–2026 listados en el insumo de Juan David). Meta: **archivo crudo en disco antes de H+2** (checkpoint C1). Si a H+2 no baja, activamos el plan B SIN discusión: tablas agregadas del DANE (serie oficial de informalidad, descarga directa en dane.gov.co → mercado laboral → empleo informal). Se cambia de fuente, no de proyecto.
2. **H+2 a H+4:** publicar los contratos congelados en `contracts/` usando los ejemplos de `docs/PLAN.md` §4 (`agente.json`, `decision.json`, `ronda.json`) ajustados a las columnas REALES que trajo la GEIH. Esto desbloquea a Manuel, Nico y Dani — es más urgente que limpiar los datos.
3. **H+4 a H+8:** construir `data/poblacion.parquet` con pandas: una fila por agente-trabajador (id, ciudad=Bogotá, sector, tamaño de empresa, ingreso mensual, formal (bool), educación, factor de expansión, arquetipo asignado). Las empresas se derivan agrupando trabajadores por sector × tamaño. También `data/momentos.json`: tasa de informalidad por sector y por tamaño de firma, y distribución salarial — son los objetivos de calibración de Juanda.
4. **H+6:** verificar si el panel rotativo de la GEIH permite seguir a la misma persona entre trimestres (documentación técnica del DANE). Valioso pero NO bloqueante: si no se puede, seguimos sin transiciones observadas.
5. **H+8 a H+14:** definir con Nico los ~40–60 arquetipos (sector × tamaño × formal/informal × tramo de ingreso) y escribir la columna `arquetipo` en el parquet.
6. **Siempre:** `data/README.md` con la fuente exacta, URL, fecha de descarga y cada transformación aplicada. Los jueces revisan el repo con agentes de código: si el README dice "datos del DANE" tiene que haber un archivo del DANE trazable.

## Reglas duras

- **Ningún dato inventado.** Si una columna no existe en la GEIH, no se fabrica: se marca `# SUPUESTO:` y se avisa al equipo.
- La descarga y transformación deben ser reproducibles: script en `data/`, no pasos manuales sin documentar.
- El reporte de cualquier agente es un reclamo: verifica con `git diff --stat` y abriendo los archivos.

## Definición de listo

`data/poblacion.parquet` + `data/momentos.json` existen, se cargan con `pd.read_parquet` sin errores, el conteo expandido (suma de factores de expansión) da un número plausible para Bogotá, y `data/README.md` explica de dónde salió todo.
