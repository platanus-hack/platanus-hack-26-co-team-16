# Handoff — sesion de auditoria final, 23-ago 06:45–08:20

> Que se hizo: correr el prompt de `docs/vet/revision-3ejes/20-auditoria.md` sobre `main` Y
> arreglar lo que encontro, en la misma sesion. El informe con la evidencia esta en
> [`auditoria-final/2026-08-23-auditoria-final.md`](auditoria-final/2026-08-23-auditoria-final.md).
>
> Rama de trabajo: `fix/producto-funcional`. Los commits `a4e1429` y `2c051c1` ya estan en `main`;
> `8083ce0` y `7a76410` y la documentacion van por el **PR #38**.

## Lo que se cerro

| Que | Commit |
|---|---|
| **La corrida bajo de ~23 min a ~5**: las 5 trayectorias corren en paralelo | `a4e1429` |
| **El candado ya no mata la URL publica**: se recupera solo a los 15 min | `8083ce0` |
| **La pantalla dejo de enfrentar dos denominadores** (17,99 % vs 30,57 %) | `7a76410` |
| A1 deploy→main, B1, B2, B3, C1, C3, y media C2 | `2c051c1` |

27 tests verdes · `tsc --noEmit` exit 0 · `npm run build` exit 0 · EL NUMERO no se movio (37,37 pp).

---

## LO QUE QUEDA ABIERTO

### 1. Regenerar `data/prediccion_modelo.json` — PRIORIDAD, y decision de equipo

**El hallazgo mas grande de la auditoria.** EL NUMERO (37,37 pp) sale de cruzar el dato observado
con ese artefacto congelado, y el artefacto se genero **antes** del arreglo de denominador del
motor: su `ronda_0_pct` es **30,6** y el motor de hoy arranca en **17,99**. Ademas declara
`arquetipos: 101` y la grilla viva tiene **81**.

La aritmetica es exacta y auditable (`33,3 + 4,07 = 37,37`), pero **el numero no se reproduce
corriendo `main` hoy**, y eso es justo lo que `VALIDATION.md` promete que si pasa.

- Comando: el que trae el propio artefacto en `como_regenerarlo`.
- Cuesta ~USD 8 y ahora ~5 min (antes ~23, ver `a4e1429`).
- **El numero nuevo es desconocido.** Puede mejorar o empeorar, y se publica salga como salga:
  esa regla del proyecto no cambia porque el numero cambie.
- Ya esta declarado en `VALIDATION.md` en un recuadro, asi que si no se regenera, no se esta
  escondiendo nada.

### 2. La espera no lee `d.trayectoria` (mitad de C2)

La banda ya quedo bien nombrada. Falta que la pantalla de espera diga en cual de las 5 trayectorias
va, en vez de parecer colgada. Criterio de la fusion: `?modo=reglas&trayectorias=2` y ver el rotulo
cambiar. Bajo impacto ahora que la demo sale de cache en 0,6 s.

### 3. Confirmar que `enjambre-api` redesplego

`/poblacion` responde 200, pero el campo nuevo `tasa_informalidad_total_ciudad` **todavia no
aparece** en la respuesta viva. Es la prueba directa de que ese servicio corre un commit anterior.
Se comprueba con:

    curl -s https://enjambre-api.onrender.com/poblacion | grep -o "tasa_informalidad_total_ciudad"

Si no sale nada despues de mergear el PR #38, el servicio no se redesplego.

### 4. `alfa = 1,875` puede ser circular (ADR 0007)

`engine/fiscalizacion.py`. Si esta calibrado contra la informalidad que el modelo debe reproducir,
el argumento se muerde la cola. No se investigo por tiempo. Cuesta $0.

### 5. `scripts/humo_deploy.py:53` se traga la excepcion

Reporta "ni /api/poblacion ni /poblacion respondieron 200" para CUALQUIER fallo, incluido un error
de SSL local. Confirmado leyendo el codigo, no arreglado. Cuesta $0.

### 6. `make` no se probo en Linux/Mac

En la maquina de esta sesion (Windows) `make` no existe; se corrieron los scripts directamente.
`python scripts/validate.py` sale con **exit 1**, que `VALIDATION.md` ya declara como esperado.
Vale la pena que alguien con Mac/Linux corra los cuatro comandos de la tabla de `AGENTS.md`.

### 7. Los 6 pendientes de despues del congelamiento

Siguen intactos en `docs/vet/revision-3ejes/10-fusion.md`, seccion *Despues del congelamiento*.
**Uno ya se midio en esta sesion y se puede cerrar:**

> **`tasa_informalidad` ponderada por empleo superviviente** (`behavior/rondas.py:513`). El
> `[SOSPECHA]` **es real**: la tasa se pondera por el peso ORIGINAL de la celda
> (`sum(a.peso * fraccion_informal) / peso_total`), no por el empleo que sobrevive, mientras que
> `empleo_relativo` justo debajo si usa `fraccion_empleada`. Una celda que despide media planta
> sigue aportando su masa completa.
>
> **Pero medido, no contamina EL NUMERO:** en el camino determinista (`modo=reglas`, que es el que
> usa el backtest) el empleo **no se mueve** — 100 % en las 4 rondas — asi que la diferencia es
> **exactamente 0,00 pp**. En el camino LLM el empleo bajo a 98,98 % en la peor corrida observada,
> lo que da una correccion de **~0,4 pp**: real, y dos ordenes de magnitud por debajo del error de
> 37,37. Es de arreglar por limpieza, no por urgencia.

---

## PROMPT PARA RETOMAR

Pega esto en una sesion nueva:

    Repo team-16. Lee primero:
      docs/agents/handoff-auditoria.md                           <- este archivo
      docs/agents/auditoria-final/2026-08-23-auditoria-final.md   <- la evidencia
      VALIDATION.md, el recuadro del artefacto desactualizado

    Contexto: la auditoria del 23-ago cerro los 9 arreglos de la lista de corte y arreglo
    tres defectos medidos (corrida de 23 min -> 5, candado que mataba la URL publica, y la
    pantalla que enfrentaba dos denominadores). Quedaron 7 cosas abiertas, listadas en el
    handoff.

    Empieza por la #1 y no por la que parezca mas facil: regenerar
    data/prediccion_modelo.json. Es lo unico que decide si EL NUMERO del proyecto es
    reproducible desde main o no. Cuesta ~USD 8 y ~5 min.

    Antes de correrlo, dime que numero esperas y por que, para que quede el pre-registro.
    Despues correlo, compara contra 37,37 pp y publica el resultado con su signo salga como
    salga. Si cambia, hay que actualizar VALIDATION.md, README.md y las laminas del pitch:
    dime cuales tocar antes de tocarlas.

    Regla del repo: cada afirmacion va con el comando que la produce. Un reporte sin la
    salida pegada es un reclamo, no evidencia.
