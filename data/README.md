# `data/` — Ingesta GEIH y población sintética

**Dueño: Alejo (R1)** · rama `rol/datos` · camino crítico del proyecto

## Qué va aquí

- Scripts de ingesta de los microdatos de la GEIH (DANE).
- `poblacion.parquet` — los agentes, con el esquema de `contracts/agente.json`.
- `momentos.json` — objetivos de calibración: informalidad por sector y tamaño, distribución salarial.
- **La procedencia:** fuente exacta, URL, fecha de descarga y toda transformación aplicada. Quien revise el repo va a leer esto primero para saber si los datos son reales.

## Qué NO va aquí

- Lógica de simulación (eso es `engine/`).
- Prompts ni llamadas a LLM (eso es `behavior/`).
- Datos inventados disfrazados de cálculo. Si un número no viene de la fuente, va con `# SUPUESTO:` en el punto donde se toma.

## Ojo

Los archivos crudos y los `.parquet` están en `.gitignore`: pesan y se regeneran. Lo que se commitea es el **script que los produce** más la procedencia.
