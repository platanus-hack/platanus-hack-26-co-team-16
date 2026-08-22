# Handoff — Alejo · R1 · Datos / población

> **Tu memoria entre sesiones.** Léelo al abrir tu sesión de agente, actualízalo antes de cerrarla.
> Este archivo es solo tuyo: nadie más lo edita, así nunca da conflicto de merge.
> Tus carpetas: `data/, contracts/` · Tu rama: `rol/datos`
> Tu misión, entregables y prompt de arranque: [`docs/ROLES.md`](../ROLES.md)

## Dónde quedé

_Lo más reciente arriba. Qué existe, qué acabas de hacer, qué necesita saber tu próxima sesión para no arrancar de cero._

- 2026-08-22 (3ª sesión) — **PR #4 APROBADO Y MERGEADO a `main`. Advertencia `tamano_empresa` en `contracts/README.md`.**
  - **Segunda review del PR #4 (APPROVE, 15:08 UTC), con evidencia reproducida, no creída:**
    higiene 7/7 · demo 4 rondas / 96 vetos / $0 · dos corridas byte a byte idénticas ·
    `desde_poblacion()` contra el parquet real → 101 arquetipos, 36/34/31 por tamaño,
    `n` 1–300, 0 ids duplicados, peso total 4.199.644 (= los ocupados expandidos exactos) ·
    `EMPLEADOS_POR_CODIGO` cuadra código a código con los rangos P3069 del README.
  - **⚠️ Conflicto de reviews a resolver con cabeza fría:** la review de la 2ª sesión
    (CHANGES_REQUESTED, 14:27 UTC, "3 críticos") fue sobre el MISMO tip (`afee16d`, 13:12 UTC)
    que yo aprobé. En mi pasada no encontré los 3 tal como están descritos abajo. Lo que SÍ
    veo latente y hay que llevar al PR top-K de Nico como issues (el merge ya está, no se
    re-litiga): (a) **caché envenenable** — si el modelo devuelve JSON válido al esquema pero
    con `estrategia_propuesta` vacía, `cliente.py` lo cachea ANTES de que
    `contrato.construir()` reviente con ValueError, y el reintento usa el mismo prompt → mismo
    hash → mismo veneno; los 3 intentos queman contra la entrada cacheada. (b) **La crítica a
    la ablación es metodológicamente válida**: la regla fija formaliza a todos por
    construcción (con aumento 0, sobrecosto 0 < sanción → `cumplir`), así que el "0% vs
    75,6%" del candado 4 es en parte artefacto de cómo se escribió la regla. El PR lo
    matiza ("a parámetros de andamio"), pero conviene endurecer la regla nula antes de
    presentar el candado 4.
  - **`contracts/README.md`:** bloque de advertencia (código ordinal 1–10, no headcount, con
    puntero a `EMPLEADOS_POR_CODIGO`) commiteado y pusheado en `rol/datos` (llegó a los dos
    remotos: el doble pushurl del espejo SÍ está en este clon). **PR #5 retitulado** para
    cubrir handoff + advertencia; sigue abierto **sin revisor** — no auto-mergear, pedirlo.
  - **Borrador del mensaje al grupo listo** (quedó en el chat de la sesión): aval ADR 0008
    con la precisión de Nico + aviso de contratos congelados para `realizacion` en
    `decision.json` y `trimestre`/`n_vetos`/`n_fallback` en `ronda.json`. **FALTA ENVIARLO.**
- 2026-08-22 (2ª sesión) — **PR #2 MERGEADO. Review de PR #4 (Nico) publicada: CHANGES_REQUESTED.**
  - Revisé `behavior/` completo + pasada profunda verificada. 3 críticos (caché envenenado
    por respuestas vacías `capa.py:179`, estado estático entre rondas `rondas.py:189`,
    ablación sesgada `ablacion.py:60`), 3 de integración con `engine/` y 5 menores.
    El detalle está en la review del PR #4.
  - **Me están esperando para el aval del ADR 0008** (rama del trabajador que acepta/rechaza
    informalizarse) — pendiente de Alejo y Nico; FLUJO/UML ya lo dan por hecho. Leerlo y decidir.
  - Inconsistencias detectadas en los docs mergeados del PR #3 (de Manuel), avisadas a Alejo
    para pasar al grupo: `docs/UML.md` usa `arquetipo_id` contra los contratos congelados
    (`agente_id`/`arquetipo`); cifra de inspectores contradictoria (ADR 0006 dice pendiente/904,
    handoff-manuel dice resuelta/1.300 OIT); `docs/README.md` con edición a medio merge.
- 2026-08-22 — **Pipeline completo entregado en `rol/datos` (PR #2 a `main`):**
  - **C1 ✅** GEIH 2026 enero–junio descargada del catálogo 900 del ANDA (descarga directa,
    sin login). Trazabilidad con URL + sha256 en `data/raw/DESCARGA.json`.
  - **Contratos ✅** `contracts/agente.json|decision.json|ronda.json` + README con la
    procedencia campo→variable GEIH verificada contra el diccionario del ANDA.
  - **`data/poblacion.parquet` ✅** 6.692 agentes de Bogotá (AREA=11), 4.199.644 ocupados
    expandidos, 67 arquetipos preliminares. Esquema = contrato. Incluido en el repo
    (107 KB; excepción en `data/.gitignore` al `*.parquet` del raíz — **avisado en el PR
    para que Juanda lo valide**).
  - **`data/momentos.json` ✅** informalidad total 30,6% (proxy pensión), por sector y por
    tamaño (micro 66,7% / pyme 10,6% / grande 0,8%), percentiles salariales, terciles.
  - **V9 (hallazgo para Juanda):** el spike salarial EXISTE — 12,1% de la masa salarial de
    Bogotá exactamente en 1.750.000 COP (moda observada; confirmar = SMLMV 2026 con V4).
  - **V2 ✅ resuelta: NO.** 0 `DIRECTORIO` repetidos entre meses en microdatos públicos →
    no hay transiciones observables de la misma persona. Se calibra contra historia
    agregada (plan B previsto). Bonus: el pooling de 6 meses no duplica personas.

## En qué estoy trabajando

- [x] Descarga GEIH (C1) · contratos (H+4) · parquet + momentos (H+8) · README · V2
- [x] Review cruzada del PR #4 de Nico — cerrada: APPROVE con evidencia reproducida, mergeado
- [x] Advertencia `tamano_empresa` en `contracts/README.md` (en PR #5, abierto)
- [ ] **Enviar el mensaje al grupo** (borrador listo): aval ADR 0008 + aviso de cambio
      aditivo en contratos (`realizacion` en `decision.json`; `trimestre`/`n_vetos`/
      `n_fallback` en `ronda.json`). Tras el ok del grupo: hacer los dos cambios en un PR.
- [ ] Llevar los dos hallazgos latentes del PR #4 (caché envenenable por estrategia vacía,
      regla nula de la ablación demasiado blanda) al PR top-K de Nico como comentarios.
- [ ] Definir con Nico los arquetipos FINALES (~H+14). Hoy: 67 celdas
      sector×tamaño×formal×tercil con colapso <60 obs. Mi propuesta (dejada en la review
      del PR #4): que `behavior/desde_poblacion()` agrupe por MI columna `arquetipo` en
      vez de re-derivar cortes propios. Cambiar del lado mío = una función en
      `data/construir_poblacion.py` y regenerar.
- [ ] Si Manuel necesita empresas explícitas: derivarlas agrupando por sector×tamaño
      (está especificado en `contracts/README.md`, no construido).

## Bloqueado / esperando a alguien

- **PR #5 espera un revisor distinto de mí** (regla 3). Es docs-only (mi handoff + la
  advertencia en `contracts/README.md`); cualquiera del equipo puede mergearlo en 2 min.
- Nico: la conversación de arquetipos (mi 67 vs su 101) sigue pendiente — para el standup.

## Supuestos que tomé

_Todo greppable con `# SUPUESTO:` en `data/construir_poblacion.py`; R5 los recoge en VALIDATION.md._

- **`formal` = cotiza a pensión (`P6920==1`; pensionados `==3` cuentan como formales).**
  Proxy de la definición OIT del DANE (la oficial cruza más módulos). El sesgo se mide en
  el candado 1: nuestro 30,6% vs la serie oficial de informalidad de Bogotá.
- **`P3069` faltante (independientes) → tamaño 1 ("trabaja solo")**, el caso modal.
- **Registros sin `INGLABO` se descartan, no se imputan** (conteo en `momentos.json`).
- **Pooling 6 meses con `FEX_C18/6`** — práctica estándar GEIH para promedios de período;
  verificado que ningún hogar aparece en dos meses.
- **La moda salarial (1.750.000 COP) se reporta como observada**, no se afirma que sea el
  SMLMV 2026 hasta que V4 (Juanda) lo confirme con los decretos.
