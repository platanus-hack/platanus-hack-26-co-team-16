"""Barrido de políticas para el reporte de estado. Dueño: Juanda (R5 · integración).

Qué modela: nada. Es el arnés que cruza las tres capas que ya existen y las corre
  sobre una rejilla de políticas, para poder decir con evidencia qué tan bien
  funciona lo que tenemos hoy.
Entradas: `data/empresas.parquet` (R1), `behavior/rondas.correr()` (R3),
  `engine/fiscalizacion.py` y `engine/veto.py` (R2).
Salidas: un JSON por corrida en `--salida` y un reporte por terminal.

**Qué hace este arnés que `behavior/demo.py` no hace.** `demo.py` corre UNA
política, una vez. Acá lo que se mide es lo que solo aparece al cruzar la
rejilla completa:

  1. **Cada repetición es una TRAYECTORIA COMPLETA e independiente**, fijada a
     una paráfrasis distinta del prompt y arrastrando su propia historia desde
     la ronda 1. Es lo que le da sentido a `banda_entre_trayectorias()`: la
     banda honesta de B2 necesita N corridas enteras, no N paráfrasis dentro de
     una misma ronda partiendo todas del mismo estado previo.
  2. **El semáforo de aceptación de la §9 del plan de correcciones.** Ruido
     sobre señal, signo de la correlación en el tramo 5-11% y reflujo de la
     última ronda son razones ENTRE políticas: no existen dentro de una corrida
     sola, así que ningún otro comando del repo las puede calcular.
  3. **El control de determinismo**, que repite exacto la primera corrida y
     compara campo a campo (ADR 0009, nivel 2).

**Lo que este archivo ya NO hace, y por qué.** Hasta el PR #12 el arnés cableaba
el veto real a mano, llevaba su propio `EstadoVivo` con una función de sutura y
se derivaba el factor prestacional por sector. Las tres cosas se fueron:

  - El veto real y el estado vivo los lleva ahora `correr()` con `veto=None`
    (C2). Había dos estados que podían divergir; ahora hay uno.
  - El factor prestacional lo trae `data/empresas.parquet` celda por celda,
    calculado contra el CST (C1). La derivación que vivía acá discrepaba del
    parquet en **10 de las 81 celdas**, siempre por los ~13,5 puntos de la
    exoneración del Art. 114-1 y siempre subestimando: contaba la exoneración
    sobre un headcount que C1 redefinió (`n_empleados` ya no incluye al dueño).
    Diez celdas de micro-empleador, que es justo donde vive la informalidad.
  - La capacidad de fiscalización sale de `EstadoFiscalizacion` (C2). El `0,02`
    que estaba acá eran 64.713 inspecciones por trimestre contra las 3.900 que
    el motor deriva de la cifra de la OIT.

Supuestos: los de las capas que llama. Este archivo no toma ninguno propio, a
propósito — un arnés que introduce supuestos deja de poder medir a nadie.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from behavior.ablacion import ClienteReglas  # noqa: E402
from behavior.arquetipos import (  # noqa: E402
    Arquetipo,
    desde_empresas,
    informalidad_observada,
    particionar_por_peso,
    universo_de_firmas,
)
from behavior.rondas import Ronda, banda_entre_trayectorias, correr  # noqa: E402
from engine.fiscalizacion import EstadoFiscalizacion  # noqa: E402

# C1 — la grilla de la corrida es la de EMPLEADORES, con factor prestacional,
# costo de despido y flujo de caja calculados contra el CST celda por celda.
EMPRESAS = RAIZ / "data" / "empresas.parquet"


# --- La corrida ---------------------------------------------------------------


def _correr_una(
    arquetipos: list[Arquetipo],
    *,
    aumento: float,
    modo: str,
    tasa_inicial: float,
    seed: int,
    n_parafrasis: int,
    cobertura: float | None,
    tope_usd: float,
    multa_factor: float,
    fiscalizacion: EstadoFiscalizacion,
    congelar_cascada: bool = False,
) -> tuple[list[Ronda], Any]:
    """Una política, una corrida. Devuelve las rondas y el cliente (para el gasto)."""
    if modo == "llm":
        from behavior.cliente import ClienteConductual
        from behavior.presupuesto import Presupuesto

        cliente = ClienteConductual(presupuesto=Presupuesto(tope_usd=tope_usd))
        paralelismo = 8
    else:
        # C1 — `factor_prestacional=None` (el default) significa "el factor de
        # CADA celda", que es el que trae el parquet. Pasarle un float acá
        # volvería a promediar 81 celdas en un número, que es lo que C1 quitó.
        cliente = ClienteReglas()
        paralelismo = 1

    rondas = correr(
        arquetipos,
        cliente,
        aumento_pct=aumento,
        seed=seed,
        simulacion_id=f"barrido-{aumento:g}-s{seed}",
        # C2 — `veto=None` es el veto REAL del motor. `correr()` construye el
        # `EstadoVivo`, lo cierra con `registrar()` al final de cada ronda y le
        # pasa al veto ese mismo objeto. Acá vivía un segundo estado paralelo.
        veto=None,
        n_parafrasis=n_parafrasis,
        paralelismo=paralelismo,
        cobertura_llm=cobertura,
        tasa_informalidad_inicial=tasa_inicial,
        multa_factor=multa_factor,
        fiscalizacion=fiscalizacion,
        congelar_prob_fiscalizacion=congelar_cascada,
    )
    return rondas, cliente


def _evasores_implicitos(capacidad: float, p: float) -> float:
    """Invierte `p = −expm1(−C / max(E,1))` para leer `max(E, 1)`.

    Sirve para poder correr los dos detectores de borde del motor sobre una
    ronda ya terminada: `Ronda` publica la `p` pero no la fracción de FIRMAS
    fuera de regla que la produjo, y recalcularla acá sería volver a duplicar
    `behavior/rondas.py`, que es justo lo que C2 borró.

    El `max(E,1)` del motor hace que por debajo de un evasor la inversión
    devuelva exactamente 1,0: por eso el régimen degenerado se detecta con
    `<= 1`, no con `< 1`.
    """
    if p <= 0.0:
        return math.inf
    if p >= 1.0:
        return 0.0  # meseta del double: la inversión ya no tiene información
    return capacidad / -math.log1p(-p)


def _resumen(
    rondas: list[Ronda],
    aumento: float,
    seed: int,
    fiscalizacion: EstadoFiscalizacion,
) -> dict[str, Any]:
    r0, rf = rondas[0], rondas[-1]
    C = fiscalizacion.capacidad()

    def _bordes(r: Ronda) -> tuple[bool, bool]:
        """(saturada, degenerada) con los detectores de `engine/fiscalizacion.py`."""
        p = r.prob_fiscalizacion
        saturada = p >= 1.0
        degenerada = (not saturada) and _evasores_implicitos(C, p) <= 1.0 + 1e-9
        return saturada, degenerada

    bordes = [_bordes(r) for r in rondas]

    # A5 — reflujo: cuánto se DEVUELVE la informalidad en la última ronda
    # respecto del máximo que alcanzó antes. El criterio 5 de la §9 pide que
    # ninguna política se devuelva más de 2 pp, o que salga etiquetada.
    previas = [r.tasa_informalidad for r in rondas[:-1]]
    reflujo_pp = (max(previas) - rf.tasa_informalidad) * 100 if previas else 0.0

    return {
        "aumento_pct": aumento,
        "seed": seed,
        # --- El resultado
        "informalidad_r0": r0.tasa_informalidad,
        "informalidad_final": rf.tasa_informalidad,
        "brecha_pp": (rf.tasa_informalidad - r0.tasa_informalidad) * 100,
        "empleo_relativo_final": rf.empleo_relativo,
        "empleo_perdido_pp": (1.0 - rf.empleo_relativo) * 100,
        # --- C3 + A4: los canales que antes se elegían y se botaban
        # `traslado_precios_pct` NO es un pronóstico de inflación: es el alza
        # que las firmas DECLARAN. No hay respuesta de demanda en el modelo.
        "traslado_precios_pct": rf.traslado_precios_pct,
        # A4 — masa salarial que sobrevive (empleo × jornada). Un trabajador a
        # media jornada no es un empleo intacto, y `bajar_horas` no movía nada.
        "ingreso_laboral_relativo": rf.ingreso_laboral_relativo,
        "fraccion_jornada_recortada": rf.fraccion_jornada_recortada,
        # --- A5: la regla de corte, declarada antes de correr
        "movimiento_pp": rf.movimiento_pp,
        "estabilizada": bool(rf.estabilizada),
        "reflujo_pp": reflujo_pp,
        # --- A2 + ADR 0010: salud de las decisiones
        "fraccion_fallback": rf.fraccion_fallback,
        "fraccion_sin_salida": rf.fraccion_sin_salida,
        # --- La cascada
        "prob_sancion_r0": r0.prob_fiscalizacion,
        "prob_sancion_final": rf.prob_fiscalizacion,
        "caida_prob_pp": (r0.prob_fiscalizacion - rf.prob_fiscalizacion) * 100,
        "rondas_saturadas": [i for i, (s, _) in enumerate(bordes) if s],
        "rondas_degeneradas": [i for i, (_, d) in enumerate(bordes) if d],
        # --- B2: la banda que emite la ronda, con su tipo declarado
        "banda_p10": rf.banda.get("p10"),
        "banda_p90": rf.banda.get("p90"),
        "banda_tipo": rf.banda.get("tipo", "intra_ronda"),
        "banda_degenerada": bool(rf.banda.get("degenerada", False)),
        "ancho_banda_pp": (rf.banda.get("p90", 0) - rf.banda.get("p10", 0)) * 100,
        "fraccion_poblacion_llm": rf.fraccion_poblacion_llm,
        "estrategias": rf.desglose_estrategias(),
        "por_ronda": [
            {
                "ronda": r.ronda,
                "informalidad": r.tasa_informalidad,
                "prob_sancion": r.prob_fiscalizacion,
                "empleo_relativo": r.empleo_relativo,
                "traslado_precios_pct": r.traslado_precios_pct,
                "ingreso_laboral_relativo": r.ingreso_laboral_relativo,
                "movimiento_pp": r.movimiento_pp,
                "estabilizada": bool(r.estabilizada),
                "fraccion_fallback": r.fraccion_fallback,
                "fraccion_sin_salida": r.fraccion_sin_salida,
            }
            for r in rondas
        ],
    }


# --- El semáforo de aceptación (§9 del plan de correcciones) -------------------


def _ruido_sobre_senal(
    por_pol: dict[float, list[dict[str, Any]]],
) -> tuple[float | None, float | None, str]:
    """Criterio 2: dispersión DENTRO de una política ÷ rango ENTRE políticas.

    Devuelve `(ruido_pp, senal_pp, razon)`, no el cociente. La razón es no
    vacía cuando el cociente no existe, y ese caso se reporta aparte a
    propósito: con ruido 0 y señal 0 el cociente sale `inf` y se leería como
    "demasiado ruido", cuando lo que pasa es lo contrario —no hay ruido, no hay
    NADA—. Es la diferencia entre mandar al equipo a cazar varianza y mandarlo
    a averiguar por qué la política no mueve el resultado.

    El ruido es la mediana de las dispersiones intra-política, no la máxima: una
    sola política ruidosa no debe decidir el veredicto de la rejilla.
    """
    disp = [
        (max(f) - min(f)) * 100
        for f in ([c["informalidad_final"] for c in cs] for cs in por_pol.values())
        if len(f) > 1
    ]
    meds = [
        statistics.median([c["informalidad_final"] for c in cs])
        for cs in por_pol.values()
    ]
    if not disp or len(meds) < 2:
        return None, None, "hacen falta ≥2 políticas y ≥2 trayectorias"
    ruido = statistics.median(disp)
    senal = (max(meds) - min(meds)) * 100
    if senal <= 1e-12:
        return ruido, senal, "sin señal: la informalidad no se mueve entre políticas"
    return ruido, senal, ""


def _correlacion_tramo(
    por_pol: dict[float, list[dict[str, Any]]], lo: float, hi: float
) -> tuple[float | None, str]:
    """Criterio 3: correlación alza → informalidad en el tramo con literatura.

    Banrep WP 1104 la tiene POSITIVA: +1 pp de Kaitz ≈ +0,21 pp de informalidad.
    Se calcula sobre las corridas individuales, no sobre las medianas, para que
    la dispersión intra-política entre a la cuenta en vez de borrarse.

    Devuelve `(correlacion, razon)`: cuando no se puede calcular, la razón dice
    CUÁL de las dos cosas faltó —pocas políticas en el tramo, o una serie
    constante—, que son diagnósticos distintos y llevan a arreglos distintos.
    """
    xs, ys = [], []
    for pol, cs in por_pol.items():
        if lo - 1e-9 <= pol <= hi + 1e-9:
            for c in cs:
                xs.append(pol)
                ys.append(c["informalidad_final"])
    n_pol = len(set(xs))
    if n_pol < 2:
        return None, f"solo {n_pol} política(s) en el tramo"
    if len(set(ys)) < 2:
        return None, "la informalidad es constante en el tramo: no hay qué correlacionar"
    try:
        return statistics.correlation(xs, ys), ""
    except statistics.StatisticsError:
        return None, "la serie no admite correlación"


# --- Reporte por terminal -----------------------------------------------------


def _pp(x: float) -> str:
    return f"{x:+.1f}"


def _ok(bien: bool) -> str:
    return "OK   " if bien else "FALLA"


def _reporte(corridas: list[dict[str, Any]], meta: dict[str, Any]) -> str:
    L: list[str] = []
    A = L.append
    A("")
    A("=" * 100)
    A("  BARRIDO DE POLÍTICAS — informe de estado del simulador")
    A(f"  {meta['fecha']} · modo {meta['modo'].upper()} · {meta['n_arquetipos']} celdas "
      f"de empleador · {meta['repeticiones']} trayectorias por política")
    A("=" * 100)
    A("")
    A(f"  Población: {meta['poblacion']}  ·  informalidad observada (GEIH): "
      f"{meta['tasa_inicial']:.1%}")
    f = meta["fiscalizacion"]
    A(f"  Fiscalización (engine/fiscalizacion.py): C = {f['capacidad']:,.0f} inspecciones/trimestre"
      .replace(",", "."))
    A(f"      universo = {f['universo']:,.0f} FIRMAS  ·  fracción del universo (S10) = "
      f"{f['fraccion_universo']:.2f}  ·  inspectores (OIT) = {f['inspectores']:,}"
      .replace(",", "."))
    A(f"  Veto: engine/veto.py, con el EstadoVivo que lleva `correr()`  ·  multa: "
      f"{meta['multa_factor']:g} meses")
    if meta.get("gasto_usd") is not None:
        A(f"  Gasto: ${meta['gasto_usd']:.2f}  ·  llamadas: {meta['llamadas']}")
    A("")

    por_pol: dict[float, list[dict[str, Any]]] = {}
    for c in corridas:
        por_pol.setdefault(c["aumento_pct"], []).append(c)

    # --- Detalle: cada trayectoria, una línea. Es lo que permite ver la dispersión
    A("  CADA TRAYECTORIA (r = repetición; cada una es una corrida completa e independiente)")
    A("  " + "-" * 96)
    A(f"  {'alza':>6} {'r':>3} {'informalidad':>13} {'brecha':>10} "
      f"{'p(sanción)':>12} {'empleo':>9} {'ingr.lab.':>10} {'Δprecios':>10}")
    A("  " + "-" * 96)
    for pol in sorted(por_pol):
        for c in sorted(por_pol[pol], key=lambda x: x.get("repeticion", 0)):
            A(f"  {pol:>5.0f}% {c.get('repeticion', 0):>3} "
              f"{c['informalidad_final']:>12.1%} {_pp(c['brecha_pp']):>7} pp "
              f"{c['prob_sancion_final']:>11.2%} {c['empleo_relativo_final']:>8.1%}"
              f" {c['ingreso_laboral_relativo']:>9.1%} {c['traslado_precios_pct']:>9.2f}%")
        fs = [c["informalidad_final"] for c in por_pol[pol]]
        es = [c["empleo_relativo_final"] for c in por_pol[pol]]
        if len(fs) < 2:
            continue  # con una sola trayectoria no hay dispersión que medir
        d_inf, d_emp = (max(fs) - min(fs)) * 100, (max(es) - min(es)) * 100
        veredicto = ("IDÉNTICAS" if d_inf < 1e-9 and d_emp < 1e-9
                     else f"varían: informalidad ±{d_inf:.1f} pp, empleo ±{d_emp:.1f} pp")
        A(f"  {'':>6} {'':>3} └─ entre las {len(fs)} trayectorias: {veredicto}")
    A("  " + "-" * 96)
    A("")

    # --- Salud de la corrida: lo que dice si el resultado es interpretable
    A("  SALUD DE LA CORRIDA (mediana de las trayectorias)")
    A("  " + "-" * 96)
    A(f"  {'alza':>6} {'movimiento r3':>15} {'estabilizada':>14} {'fallback':>11} "
      f"{'sin salida':>12} {'jornada rec.':>14}")
    A("  " + "-" * 96)
    for pol in sorted(por_pol):
        cs = por_pol[pol]
        est = sum(1 for c in cs if c["estabilizada"])
        A(f"  {pol:>5.0f}% "
          f"{statistics.median([c['movimiento_pp'] for c in cs]):>12.2f} pp "
          f"{f'{est}/{len(cs)}':>14} "
          f"{statistics.median([c['fraccion_fallback'] for c in cs]):>10.1%} "
          f"{statistics.median([c['fraccion_sin_salida'] for c in cs]):>11.1%} "
          f"{statistics.median([c['fraccion_jornada_recortada'] for c in cs]):>13.1%}")
    A("  " + "-" * 96)
    A("      fallback   = decisiones que el veto tumbó y cayeron a la salida factible (ADR 0010)")
    A("      sin salida = arquetipos sin NINGUNA estrategia factible. Alto = el veto ahoga el modelo")
    A("")

    # --- Resumen por política, con la banda ENTRE trayectorias (B2)
    A("  RESUMEN POR POLÍTICA (mediana de las trayectorias)")
    A("  " + "-" * 96)
    A(f"  {'alza':>6} {'informal. final':>17} {'brecha':>9} {'p(sanción)':>12} "
      f"{'empleo':>9}   banda entre trayectorias")
    A("  " + "-" * 96)
    bandas = meta.get("bandas_entre_trayectorias", {})
    for pol in sorted(por_pol):
        cs = por_pol[pol]
        b = bandas.get(str(pol)) or bandas.get(pol) or {}
        if b.get("p10") is None:
            texto_b = "—"
        elif b.get("degenerada"):
            texto_b = f"{b['p10']:.1%} (degenerada: un punto)"
        else:
            texto_b = (f"{b['p10']:.1%} – {b['p90']:.1%}  "
                       f"({(b['p90'] - b['p10']) * 100:.1f} pp)")
        A(f"  {pol:>5.0f}% "
          f"{statistics.median([c['informalidad_final'] for c in cs]):>15.1%}   "
          f"{_pp(statistics.median([c['brecha_pp'] for c in cs])):>7} pp "
          f"{statistics.median([c['prob_sancion_final'] for c in cs]):>11.2%} "
          f"{statistics.median([c['empleo_relativo_final'] for c in cs]):>8.1%}   "
          f"{texto_b}")
    A("  " + "-" * 96)
    A("      La banda es la de TRAYECTORIAS COMPLETAS (B2), no la de paráfrasis dentro de una")
    A("      ronda: esa parte del mismo estado previo y por construcción es más angosta.")
    A("")

    # --- Monotonía
    meds = [(p, statistics.median([c["informalidad_final"] for c in por_pol[p]]),
             statistics.median([c["empleo_relativo_final"] for c in por_pol[p]]))
            for p in sorted(por_pol)]
    rupturas_inf = [meds[i][0] for i in range(1, len(meds)) if meds[i][1] < meds[i - 1][1]]
    rupturas_emp = [meds[i][0] for i in range(1, len(meds)) if meds[i][2] > meds[i - 1][2]]
    A("  MONOTONÍA")
    A(f"      informalidad baja al subir el alza en: "
      f"{', '.join(f'{p:g}%' for p in rupturas_inf) or 'ningún punto (monótona)'}")
    A(f"      empleo SUBE al subir el alza en:       "
      f"{', '.join(f'{p:g}%' for p in rupturas_emp) or 'ningún punto (monótona)'}")
    A("      Una ruptura NO es un error: puede ser un mecanismo real. Pero hoy el modelo no")
    A("      tiene productividad, demanda ni capital (bloque D), así que una ruptura acá es")
    A("      ruido hasta que se demuestre lo contrario.")
    A("")

    # --- El semáforo de la §9
    A("  SEMÁFORO DE ACEPTACIÓN (§9 del plan de correcciones)")
    A("  " + "-" * 96)
    ruido, senal, razon = _ruido_sobre_senal(por_pol)
    if ruido is None or senal is None:
        A(f"   2  ruido/señal ..........................   no medible   ({razon})")
    elif razon:
        A(f"   2  ruido/señal ..........................   no medible   ({razon})")
        A(f"      ruido = {ruido:.2f} pp · señal = {senal:.2f} pp. El cociente no existe, y el")
        A("      problema NO es la varianza: es que la política no mueve el resultado.")
    else:
        rs = ruido / senal
        A(f"   2  ruido/señal .......................... {rs:>12.2f}   meta ≤ 0,25    "
          f"[{_ok(rs <= 0.25)}]")
        A(f"      ruido = {ruido:.2f} pp (mediana intra-política) · "
          f"señal = {senal:.2f} pp (rango entre políticas)")
    corr, razon_c = _correlacion_tramo(por_pol, 5.0, 11.0)
    if corr is None:
        A(f"   3  correlación alza→informalidad 5-11% ..   no medible   ({razon_c})")
    else:
        A(f"   3  correlación alza→informalidad 5-11% .. {corr:>+12.3f}   meta positiva  "
          f"[{_ok(corr > 0)}]")
    reflujos = {p: statistics.median([c["reflujo_pp"] for c in por_pol[p]]) for p in por_pol}
    peor = max(reflujos.values()) if reflujos else 0.0
    quien = [p for p, v in reflujos.items() if v > 2.0]
    A(f"   5  reflujo máx. en la última ronda ....... {peor:>9.1f} pp   meta ≤ 2,0 pp  "
      f"[{_ok(peor <= 2.0)}]")
    if quien:
        A(f"      se devuelven más de 2 pp: {', '.join(f'{p:g}%' for p in sorted(quien))}")
    if meta.get("cascada"):
        c4 = meta["cascada"]
        A(f"   B4 aporte de la cascada ................. {c4['aporte_pp']:>+10.1f} pp   "
          f"(brecha con cascada − brecha con p congelada)")
    else:
        A("   B4 aporte de la cascada ................. no medido      "
          "(corre con --cascada-apagada)")
    A("   1  make reproduce en máquina limpia ...... no lo mide este comando")
    A("   9  tabla del bloque D .................... no lo mide este comando (VALIDATION.md)")
    A("  " + "-" * 96)
    A("      Una casilla que no cierra se publica sin cerrar. Es la regla de VALIDATION.md:4")
    A("      y este comando no la cambia.")
    A("")

    if meta.get("control"):
        c = meta["control"]
        A("  CONTROL DE DETERMINISMO (repetir exacto la misma corrida)")
        A(f"      política {c['politica']:g}%, misma paráfrasis, misma semilla → "
          + ("IDÉNTICA (el pipeline es determinista con caché)"
             if c["identica"] else f"DIFIERE: {c['diferencias']}"))
        A("")

    # --- Trayectoria de la política central
    centro = sorted(por_pol)[len(por_pol) // 2]
    A(f"  Trayectoria por ronda — alza {centro:g}% (mediana de las trayectorias):")
    A("")
    A(f"      {'ronda':>6} {'informalidad':>14} {'p(sanción)':>12} {'empleo':>9} "
      f"{'ingr.lab.':>10} {'Δprecios':>10} {'movim.':>9}")
    for i in range(len(por_pol[centro][0]["por_ronda"])):
        def _m(campo: str) -> float:
            return statistics.median([c["por_ronda"][i][campo] for c in por_pol[centro]])
        etiqueta = "0 (of.)" if i == 0 else str(i)
        A(f"      {etiqueta:>6} {_m('informalidad'):>13.1%} "
          f"{_m('prob_sancion'):>11.2%} {_m('empleo_relativo'):>8.1%} "
          f"{_m('ingreso_laboral_relativo'):>9.1%} "
          f"{_m('traslado_precios_pct'):>9.2f}% {_m('movimiento_pp'):>7.2f} pp")
    A("")

    # --- Estrategias
    est_tot: dict[str, float] = {}
    for c in corridas:
        for k, v in (c.get("estrategias") or {}).items():
            est_tot[k] = est_tot.get(k, 0.0) + v
    if est_tot:
        n = len(corridas)
        A("  Estrategias dominantes (fracción de población, promedio del barrido):")
        for k, v in sorted(est_tot.items(), key=lambda kv: -kv[1]):
            A(f"      {k:<24} {v / n:>6.1%}")
        A("")
    A("=" * 100)
    return "\n".join(L)


# --- CLI ----------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--desde", type=float, default=5.0)
    ap.add_argument("--hasta", type=float, default=20.0)
    ap.add_argument("--paso", type=float, default=2.0)
    ap.add_argument("--repeticiones", type=int, default=3)
    ap.add_argument("--llm", action="store_true", help="capa LLM real (necesita key)")
    ap.add_argument("--cobertura", type=float, default=0.80,
                    help="top-K: fracción de población que va al LLM")
    ap.add_argument("--tope", type=float, default=12.0, help="tope de gasto USD")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--multa-factor", type=float, default=12.0)
    # C2 — la capacidad ya NO es un argumento de `correr()`. Lo único que queda
    # para forzar acá es el `# SUPUESTO:` S10 de `engine/fiscalizacion.py`, que
    # el criterio 8 de la §9 obliga a barrer: un parámetro sin fuente tiene que
    # salir con barrido publicado o no sale. `None` = el default del motor.
    ap.add_argument("--fraccion-universo", type=float, default=None,
                    help="fuerza S10 (fracción del universo inspeccionable) para "
                         "el barrido de sensibilidad. Alimenta EstadoFiscalizacion")
    ap.add_argument("--cascada-apagada", action="store_true",
                    help="B4: corre la rejilla otra vez con p(sanción) congelada "
                         "en su valor de la ronda 0 y reporta el aporte en pp. "
                         "DUPLICA el costo en modo --llm")
    ap.add_argument("--salida", type=str, default="scripts/salidas")
    args = ap.parse_args(argv)

    # La rejilla. Se incluye el extremo superior aunque el paso no caiga justo.
    puntos: list[float] = []
    x = args.desde
    while x <= args.hasta + 1e-9:
        puntos.append(round(x, 4))
        x += args.paso
    if abs(puntos[-1] - args.hasta) > 1e-9:
        puntos.append(args.hasta)

    modo = "llm" if args.llm else "ablacion"
    arquetipos = desde_empresas(str(EMPRESAS))
    tasa_inicial = informalidad_observada()

    # C2 — un solo `EstadoFiscalizacion` para todo el barrido. Es estado del
    # mundo (ADR 0006), no una perilla de la política: construirlo por política
    # sería dejar que la política mueva la capacidad de inspección.
    fisc = EstadoFiscalizacion(universo=max(1.0, universo_de_firmas(arquetipos)))
    if args.fraccion_universo is not None:
        fisc = fisc.con(fraccion_universo=args.fraccion_universo)

    if args.cobertura and modo == "llm":
        cabeza, cola = particionar_por_peso(arquetipos, args.cobertura)
        print(f"top-K: {len(cabeza)} celdas al LLM, {len(cola)} a reglas fijas")

    print(f"modo {modo} · {len(arquetipos)} celdas de empleador · {len(puntos)} políticas "
          f"({', '.join(f'{p:g}%' for p in puntos)}) · {args.repeticiones} trayectorias")
    print(f"informalidad observada (GEIH): {tasa_inicial:.1%}")
    print(f"fiscalización: C = {fisc.capacidad():,.0f}/trimestre sobre "
          f"{fisc.universo:,.0f} firmas".replace(",", "."))
    if modo == "llm":
        est = len(puntos) * args.repeticiones * len(arquetipos)
        print(f"estimado ~{est} llamadas · tope ${args.tope:.2f}")
    print()

    corridas: list[dict[str, Any]] = []
    trayectorias: dict[float, list[list[Ronda]]] = {}
    gasto = 0.0
    llamadas = 0
    t0 = time.time()

    # Cada repetición es una TRAYECTORIA COMPLETA e independiente, fijada a una
    # paráfrasis distinta del prompt. Es más fuerte que `n_parafrasis=N`, donde
    # las N parten todas del mismo estado previo: acá divergen desde la ronda 1
    # y arrastran su propia historia. Es lo que `banda_entre_trayectorias()`
    # necesita para que la banda de B2 sea la honesta.
    #
    # No se usan semillas distintas porque la caché se indexa por prompt y el
    # prompt no lleva seed: 3 semillas serían 3 aciertos de caché idénticos.
    # Eso se COMPRUEBA abajo con la corrida de control, no se da por hecho.
    import behavior.capa as _capa
    from behavior.cliente import parafrasis as _parafrasis

    _TODAS = _parafrasis(5)

    def _fijar(indice: int) -> None:
        _capa.parafrasis = lambda n=1, _i=indice: [_TODAS[_i % len(_TODAS)]]

    def _una(pol: float, i: int, *, congelar: bool = False,
             guardar: bool = True) -> dict[str, Any] | None:
        nonlocal gasto, llamadas
        _fijar(i)
        try:
            rondas, cliente = _correr_una(
                arquetipos, aumento=pol, modo=modo,
                tasa_inicial=tasa_inicial, seed=args.seed,
                n_parafrasis=1, cobertura=args.cobertura if modo == "llm" else None,
                tope_usd=max(0.01, args.tope - gasto), multa_factor=args.multa_factor,
                fiscalizacion=fisc, congelar_cascada=congelar,
            )
        except Exception as e:  # noqa: BLE001
            print(f"  {pol:>5g}%  r{i + 1}  FALLÓ: {type(e).__name__}: {e}",
                  file=sys.stderr)
            return None
        res = _resumen(rondas, pol, args.seed, fisc)
        res["repeticion"] = i + 1
        res["parafrasis"] = i + 1
        if guardar:
            trayectorias.setdefault(pol, []).append(rondas)
        g = getattr(getattr(cliente, "presupuesto", None), "gastado_usd", 0.0) or 0.0
        gasto += g
        llamadas += getattr(cliente, "llamadas", 0)
        return res

    def _linea(pol: float, i: int, res: dict[str, Any], marca: str = "") -> None:
        print(f"  {pol:>5g}%  r{i + 1}{marca}  informalidad {res['informalidad_final']:>6.1%}"
              f"  brecha {res['brecha_pp']:>+6.1f} pp"
              f"  p(sanción) {res['prob_sancion_final']:>6.2%}"
              f"  empleo {res['empleo_relativo_final']:>6.1%}"
              + ("  [$%.2f]" % gasto if modo == "llm" else ""))

    for pol in puntos:
        for i in range(args.repeticiones):
            res = _una(pol, i)
            if res is None:
                continue
            corridas.append(res)
            _linea(pol, i, res)

    if not corridas:
        print("\nninguna corrida terminó. Nada que reportar.", file=sys.stderr)
        return 2

    # --- B4: el experimento que cuantifica la cascada -------------------------
    cascada: dict[str, Any] = {}
    if args.cascada_apagada:
        print("\n  --- cascada apagada (p(sanción) congelada en la ronda 0) ---")
        sin: list[dict[str, Any]] = []
        for pol in puntos:
            for i in range(args.repeticiones):
                res = _una(pol, i, congelar=True, guardar=False)
                if res is None:
                    continue
                sin.append(res)
                _linea(pol, i, res, marca="*")
        if sin:
            con_med = statistics.median([c["brecha_pp"] for c in corridas])
            sin_med = statistics.median([c["brecha_pp"] for c in sin])
            cascada = {
                "brecha_con_cascada_pp": con_med,
                "brecha_sin_cascada_pp": sin_med,
                "aporte_pp": con_med - sin_med,
                "corridas": sin,
            }

    # --- Control de determinismo (ADR 0009 nivel 2) ---------------------------
    # Se repite EXACTAMENTE la primera corrida (misma política, misma paráfrasis,
    # misma semilla). Si el pipeline es determinista tiene que salir idéntica.
    control: dict[str, Any] = {}
    pol0 = corridas[0]["aumento_pct"]
    rep = _una(pol0, 0, guardar=False)
    if rep is not None:
        campos = ("informalidad_final", "prob_sancion_final",
                  "empleo_relativo_final", "brecha_pp",
                  "ingreso_laboral_relativo", "traslado_precios_pct")
        difs = {k: (corridas[0][k], rep[k]) for k in campos
                if abs(corridas[0][k] - rep[k]) > 1e-12}
        control = {"politica": pol0, "identica": not difs, "diferencias": difs}

    # --- B2: la banda entre trayectorias completas ----------------------------
    bandas = {
        str(pol): banda_entre_trayectorias(cs)
        for pol, cs in trayectorias.items()
        if cs
    }

    meta = {
        "fecha": datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M"),
        "modo": modo,
        "n_arquetipos": len(arquetipos),
        "repeticiones": args.repeticiones,
        "poblacion": "data/empresas.parquet (empleadores GEIH Bogotá 2026)",
        "tasa_inicial": tasa_inicial,
        "fiscalizacion": {
            "capacidad": fisc.capacidad(),
            "universo": fisc.universo,
            "inspectores": fisc.inspectores,
            "inspecciones_por_inspector": fisc.inspecciones_por_inspector,
            "fraccion_universo": fisc.fraccion_universo,
        },
        "multa_factor": args.multa_factor,
        "segundos": round(time.time() - t0, 1),
        "gasto_usd": gasto if modo == "llm" else None,
        "llamadas": llamadas,
        "control": control,
        "cascada": cascada,
        "bandas_entre_trayectorias": bandas,
    }

    salida = RAIZ / args.salida
    salida.mkdir(parents=True, exist_ok=True)
    marca = datetime.now().strftime("%Y%m%d-%H%M")
    destino = salida / f"barrido-{modo}-{marca}.json"
    with open(destino, "w", encoding="utf-8") as f:
        json.dump({"meta": meta, "corridas": corridas}, f, ensure_ascii=False, indent=2)

    print(_reporte(corridas, meta))
    print(f"  JSON crudo: {destino.relative_to(RAIZ)}")
    print(f"  Duración: {meta['segundos']}s")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
