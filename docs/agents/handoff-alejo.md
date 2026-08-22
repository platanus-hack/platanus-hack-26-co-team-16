# Handoff — Alejo · R1 · Datos / población

> **Tu memoria entre sesiones.** Léelo al abrir tu sesión de agente, actualízalo antes de cerrarla.
> Este archivo es solo tuyo: nadie más lo edita, así nunca da conflicto de merge.
> Tus carpetas: `data/, contracts/` · Tu rama: `rol/datos`
> Tu misión, entregables y prompt de arranque: [`docs/ROLES.md`](../ROLES.md)

## Dónde quedé

_Lo más reciente arriba. Qué existe, qué acabas de hacer, qué necesita saber tu próxima sesión para no arrancar de cero._

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
- [x] Review cruzada del PR #4 de Nico (CHANGES_REQUESTED, 2026-08-22)
- [ ] **Aval del ADR 0008** (me esperan Nico y los diagramas). Leer y responder en el grupo.
- [ ] Definir con Nico los arquetipos FINALES (~H+14). Hoy: 67 celdas
      sector×tamaño×formal×tercil con colapso <60 obs. Mi propuesta (dejada en la review
      del PR #4): que `behavior/desde_poblacion()` agrupe por MI columna `arquetipo` en
      vez de re-derivar cortes propios. Cambiar del lado mío = una función en
      `data/construir_poblacion.py` y regenerar.
- [ ] Si Manuel necesita empresas explícitas: derivarlas agrupando por sector×tamaño
      (está especificado en `contracts/README.md`, no construido).

## Bloqueado / esperando a alguien

- Nico: respuesta a la review del PR #4 (los 3 críticos, ~2h de fix) y la conversación
  de arquetipos. Pedida 2026-08-22 en la review.

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
