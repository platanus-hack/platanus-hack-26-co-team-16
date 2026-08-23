# `20-auditoria.md` — el prompt de auditoría final

> **Creado el 23-ago 07:05 por Manuel (R2), sobre `ae64a90`.** Cierra el ciclo que abrió
> [`10-fusion.md`](10-fusion.md): la fusión decidió **qué arreglar**, este archivo verifica
> **qué se arregló de verdad**.
>
> No es un informe. Es el **prompt** que se pega en una sesión nueva para auditar el repo entero
> antes del congelamiento de las 09:30. Los hallazgos que produzca van a `docs/agents/<agente>/`.

## Por qué existe

El §3 de la fusión listó 9 arreglos con su criterio de verificación. A las 06:45 del domingo,
**verificados uno por uno con `grep` y con los comandos del `Makefile`, solo A1 (a medias) y A2
estaban tocados.** La distancia entre "está en la lista de corte" y "está hecho" resultó ser todo
el trabajo.

Y hay un precedente que justifica el tono de este archivo: **el criterio de verificación de B3
estaba roto.** Mandaba correr `python scripts/validate.py --dry`, un flag que no existe. Lo
encontró el cierre del Eje B (PR #34) y está corregido. Una lista de corte cuyos propios comandos
no corren produce arreglos que nadie puede confirmar.

## La regla que hace que sirva

**Cada afirmación del informe lleva pegado el comando que la produce.** Un auditor que escribe
*"C1 está arreglado"* sin la salida del `grep` está haciendo exactamente lo que este archivo existe
para evitar. `AGENTS.md` ya lo dice para los PR (*"antes de creer que algo se hizo:
`git diff --stat`"*); acá aplica a cada línea.

---

## El prompt

```
Eres el auditor final del repo team-16, a horas del congelamiento (domingo 09:30).
No escribes codigo. No arreglas nada. Produces UN informe con evidencia.

Tu unica regla: CADA afirmacion va con el comando que la produce y su salida. Si no
puedes correr el comando, la afirmacion no entra al informe: entra a una lista aparte
llamada "no verificable", con la razon. Un informe de agente es un reclamo, no
evidencia, y el tuyo tampoco es la excepcion.

CONTEXTO MINIMO (leelo en este orden, y no leas mas):
  docs/vet/revision-3ejes/10-fusion.md   la lista de corte: los 9 arreglos, su criterio,
                                         y al final la seccion "Despues del congelamiento"
  docs/agents/handoff-manuel.md          seccion "Sesion 4": lo medido el 23-ago 04:45-06:45
  AGENTS.md                              el contrato y las restricciones no-negociables

OJO CON LOS CRITERIOS DE LA PROPIA FUSION: uno ya resulto estar roto (el de B3 mandaba
`python scripts/validate.py --dry` y ese flag NO EXISTE; corregido en el PR #34). Si un
criterio no corre, eso ES un hallazgo: reportalo en vez de inventarte otro en silencio.

=== BLOQUE 1 · LOS 9 ARREGLOS DE LA FUSION ===

Para cada uno usa el criterio del §1 de la fusion, YA CORREGIDO. Reporta
HECHO / A MEDIAS / SIN TOCAR con la salida pegada.

  A1  deploy apunta a main
      SON DOS SERVICIOS (render.yaml:32 api, :52 web). Verifica LOS DOS por separado.
      web:  curl -o /dev/null -w "%{http_code}" URL/reporte   (404 = rama vieja, 200 = main)
      api:  make humo URL=...   Si responde "ya hay una corrida en curso", el proceso
            NO se reinicio y por lo tanto NO se redesplego.
  A2  cache-demo.json versionado
      git ls-tree origin/main behavior/cache-demo.json ; contar entradas y modelos.
      Toda entrada que no sea claude-sonnet-5 es peso muerto: el modelo es el primer
      campo de cache.clave() y no puede acertar jamas.
  A3  cap de gasto acumulado + fraccion_fallback y fraccion_sin_salida leidos por un panel
  B1  el mapa rebautizado a carga legal, con la nota al pie
  B2  grep -c "2,63\|2\.63" VALIDATION.md   y   grep -ic "ciego" VALIDATION.md
  B3  sed -n '160,175p' scripts/validate.py   (NO uses --dry, no existe)
      mas: grep -rn "obertura del rango" scripts/ web/
  C1  grep -rn "proyeccion oficial" web/enjambre
      OJO: la fusion solo miro web/enjambre. Revisa TAMBIEN el stdout de `make reproduce`
      y web/prototipo/mapa.html, que dicen lo mismo y nadie los conto.
  C2  ?modo=reglas&trayectorias=2 y ver el rotulo cambiar
  C3  el 37,37 se lee en / sin un clic

=== BLOQUE 2 · LOS COMANDOS QUE EL REPO PROMETE ===

AGENTS.md tiene una tabla "Como verificarlo tu mismo". Corre los cuatro y reporta la
salida REAL, no la prometida:

  make run      make test      make validate      python scripts/reproduce.py

Para cada uno di: corre / no corre / corre pero sale con codigo != 0. El exit code
importa: un juez que corre el comando estrella y ve "Error 1" no lee la salida.
Ademas: make humo URL=<la URL desplegada>   (ablacion, cuesta $0).

=== BLOQUE 3 · AUDITAR LA SESION 4, ADVERSARIALMENTE ===

Esto se hizo entre las 04:45 y las 07:00 y NADIE lo reviso. Buscale el error.

  a) PR #36 (mergeado como 318a019) mete behavior/cache-demo.json: 518 entradas Sonnet
     por USD 7,87. Verifica las tres cosas:
       - que las 518 sean todas claude-sonnet-5;
       - que api/servidor.py:209 las precargue al arrancar (levanta el servidor local y
         busca la linea "[cache] N entradas precargadas");
       - que una corrida modo=llm contra ese servidor local reporte llamadas_api=0 y
         cache_aciertos>0.
     SI LOS ACIERTOS SON 0, la cache no cubre el escenario y los USD 7,87 se perdieron.
     Ese es el hallazgo mas caro posible de esta auditoria: buscalo primero.
  b) El PR declara un limite conocido: `make reproduce` REVIENTA sin API key en vez de
     caer a la ablacion. Confirmalo o desmientelo corriendolo. Si es cierto es una
     regresion VIVA EN MAIN y va arriba de tu informe.
  c) El handoff afirma que enjambre-api no se redesplego, y su unica prueba es que el
     candado sigue trabado. Eso es inferencia, no medicion. Busca una prueba directa
     (algo que difiera entre main y la rama vieja y se vea por HTTP) o marcalo como
     no verificado.
  d) PR #34 (mergeado como ae64a90) cambia el comando de verificacion de B3. Comprueba
     que el comando NUEVO si corre y si muestra lo que dice mostrar.

=== BLOQUE 4 · DEFECTOS MEDIDOS QUE NO ESTAN EN LA LISTA DE CORTE ===

Confirma o desmiente cada uno, y decide si es de decir en voz alta o de arreglar:

  1. La ronda 0 arranca en 17,99% y /poblacion declara 30,57% de informalidad observada.
     `make humo ... LLM=1` falla por esto. Es sobre main, sin Render de por medio.
     Rastrea de donde sale CADA numero y di si es un bug o dos cosas distintas mal
     nombradas. Es una pregunta de juez sin respuesta ensayada.
  2. `tasa_informalidad` ponderada por empleo superviviente (behavior/rondas.py). Es un
     [SOSPECHA] sin verificar que trae el anexo del Eje B. Si una celda que despide media
     planta sigue aportando la misma masa informal, CONTAMINA EL NUMERO, no solo el mapa.
     Es el mas barato con mas consecuencia de todo el repo: cuesta $0 verificarlo.
  3. El candado `_ocupado` (api/servidor.py:167) no tiene timeout ni forma de resetearse
     sin reiniciar el proceso. El 23-ago dejo la URL publica muerta ~2 horas.
  4. scripts/humo_deploy.py:53 se traga la excepcion y reporta "ni /api/poblacion ni
     /poblacion respondieron 200" para CUALQUIER fallo, incluido un error de SSL local.
  5. alfa = 1,875 en engine/fiscalizacion.py (ADR 0007): si esta calibrado contra la
     informalidad que el modelo debe reproducir, es circular.
  6. Al deploy le faltaban 71 commits de main, no 15 como decia la fusion. Revisa si hay
     mas cifras de la fusion que envejecieron.

=== BLOQUE 5 · COHERENCIA DEL REPO CONSIGO MISMO ===

  - grep -rn "SUPUESTO:" — el informe de honestidad. Cuenta, y di si alguno quedo
    huerfano (marca un supuesto sobre codigo que ya no existe).
  - Todo numero de README.md, VALIDATION.md, project-description.md y de la pantalla:
    verifica que salga de un comando y no de prosa. Un numero que solo existe en texto
    es un numero inventado hasta que se demuestre.
  - AGENTS.md dice "cero TODO: implementar dentro de engine/". Compruebalo.
  - Los tres contracts/*.json contra lo que la API emite de verdad.
  - TRAMPA DE NOMBRE, no caigas: `demo.py --reparto` NO es el mapa distributivo, es el
    reparto de parafrasis por peso poblacional. Si atacas el mapa con ese flag mides
    otra cosa y reportas una mentira.

=== FORMATO DE SALIDA ===

Escribe en docs/agents/<tu-nombre>/2026-08-23-auditoria-final.md:

  1. VEREDICTO (3 lineas): que se puede demostrar, que no, y el riesgo mas grande vivo.
  2. TABLA de los 9 arreglos: # | estado | comando | salida recortada.
  3. LO QUE ESTA ROTO AHORA MISMO, ordenado por lo que un juez ve primero.
  4. LO QUE HAY QUE DECIR EN VOZ ALTA en vez de arreglar, con la frase ya redactada.
  5. NO VERIFICABLE: lo que no pudiste correr, y por que.

Si algo del BLOQUE 3 resulta mal, va en el punto 1. Es lo mas reciente, lo unico sin
review, y lo que mas facil se cuela.
```

## Cuándo usarlo

Una sola vez, después de que los dueños reporten sus arreglos y **antes** del ensayo del pitch.
En una sesión distinta y, si se puede, en un modelo distinto al que escribió los arreglos: el
punto 3 del flujo de trabajo de `AGENTS.md` aplica igual acá.

Si el tiempo alcanza para un solo bloque, corre el **3**. Es lo más nuevo, lo único sin review, y
lo que ya costó dinero.

## Lo que este prompt deja fuera a propósito

Los **6 pendientes de después del congelamiento** que trae el cierre del Eje B (§ *Después del
congelamiento* de [`10-fusion.md`](10-fusion.md)). Son trabajo de mejora, no de verificación, y
meterlos acá convertiría una auditoría de 40 minutos en un plan de dos días.

**Con una excepción, y está adentro del bloque 4:** el pendiente de `tasa_informalidad` ponderada
por empleo superviviente. Ese no es una mejora, es un `[SOSPECHA]` que puede contaminar **EL
NÚMERO**, cuesta $0 comprobarlo, y si es cierto cambia lo que se dice en el pitch.
