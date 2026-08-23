Corrí un vet completo sobre `main` (c63343f) con tres auditorías de solo lectura. Todo lo de abajo
tiene archivo:línea o comando. Adjunto las dos tablas.

**Lo bueno primero, y no es poco.** El pre-registro se sostiene: criterio commiteado a las 17:59:53,
datos 18 minutos después, bloque idéntico byte a byte. La pantalla SÍ se alimenta del motor, cadena
cerrada de punta a punta, y ningún panel de texto lee un número interpolado. El veto no lee nombres.
Y el pico salarial se movió solo tres años seguidos siguiendo al mínimo legal, sin que nadie se lo
dijera al pipeline.

**Cinco cosas rojas:**

1. `n_parafrasis>=2` REVIENTA. `round()` sobre `banda.tipo` que es string. La banda que AGENTS.md
   declara no-negociable no está apagada, es imposible de encender. Media hora de arreglo.
2. `VALIDATION.md` dice "fuera de muestra de verdad" y el código lo contradice: la corrida usa la
   población 2026 y arranca del dato post-política. `poblacion_2025.parquet` existe y nadie lo lee.
3. La demo se ve IDÉNTICA con LLM y con `?modo=reglas`, con citas entre comillas incluidas.
4. El front nunca pide más de una paráfrasis, así que la banda siempre sale degenerada.
5. `deploy-url` sigue en `<FILL THIS>` y `project-description.md` sigue siendo el placeholder.

**Y la causa del salto a "Ronda 3/3":** `motorVisual.ts:79` se queda con la última ronda y descarta
las intermedias. Con caché caliente siempre llegan juntas.

**Cuatro cosas que necesito que decidamos entre todos, no las decido yo:**

1. **El pre-compromiso.** Arreglar el punto 2 va a cambiar EL NÚMERO. Propongo commitear ANTES de
   correrlo: el número nuevo reemplaza al viejo, salga como salga, y los dos quedan publicados con su
   hash. Correr, mirar y quedarse con el más bonito es lo que el pre-registro existe para impedir.
2. **El pre-registro no fue ciego** y hay que decirlo en el pitch. `2d4aa7e` ya traía "lo que ya se
   sabe apunta a la rama B". Dicho por nosotros es rigor; encontrado por un juez es fraude.
3. **Dani:** tienes 664 líneas en `rol/interfaz` sin PR (`plan-correcciones-simulacion.md`), y
   `DEFECTOS.md:27` en main las cita. ¿Las metemos por PR o borramos la referencia?
4. **El reparto.** Lo ordené en tres oleadas por dependencia, dos agentes por persona. Si alguien no
   está de acuerdo con lo suyo, ahora, no a las 04:00.

**Tres dependencias duras que si se rompen nos traban a todos:**
S1-1 antes que S2-2 · el pre-compromiso antes que el backtest nuevo · C1 antes que C2.

**Juanda, el deploy arranca ya**, en paralelo a todo. Es lo único que puede fallar por razones que no
controlamos y descubrirlo a las 06:00 no tiene arreglo.
