"""Barrido de políticas para el reporte de estado. Dueño: Juanda (R5 · integración).

Qué modela: nada. Es el arnés que cruza las tres capas que ya existen y las corre
  sobre una rejilla de políticas, para poder decir con evidencia qué tan bien
  funciona lo que tenemos hoy.
Entradas: `data/poblacion.parquet` (R1), `behavior/rondas.correr()` (R3),
  `engine/veto.py` (R2), `data/parametros_legales.json` (R1).
Salidas: un JSON por corrida en `--salida` y un reporte por terminal.

Tres cosas que este arnés hace y que `behavior/demo.py` NO hace hoy:

  1. **Cablea el veto REAL de `engine/`.** `demo.py:179` sigue pasando
     `veto_doble_prueba`, el doble de prueba que Nico escribió cuando `engine/`
     no existía. Manuel dejó `veto_del_motor(estado)` hecho para enchufarse
     (`engine/veto.py`) y nadie lo enchufó. Los dos PR se mergearon el mismo día
     sin que nadie corriera el uno contra el otro.

  2. **Asigna el factor prestacional POR FIRMA, no uno global.**
     `behavior/ablacion.py:39` toma un solo `factor_prestacional` para toda la
     población. `data/parametros_legales.json` dice literalmente: *"El rango NO
     es incertidumbre: es estructura. El motor debe asignar el factor que
     corresponde a cada firma, no promediar."* Acá se hace lo que ese dato pide.

  3. **Registra el estado vivo en el `EstadoVivo` del motor**, para que el veto
     de la ronda n+1 vea lo que pasó en la ronda n.

Supuestos: los de las capas que llama, más `# SUPUESTO:` marcados abajo.
"""

from __future__ import annotations

import argparse
import json
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
    desde_poblacion,
    informalidad_observada,
    particionar_por_peso,
)
from behavior.rondas import Ronda, correr  # noqa: E402
from engine.veto import EstadoVivo, veto_del_motor  # noqa: E402

PARAMETROS = RAIZ / "data" / "parametros_legales.json"
POBLACION = RAIZ / "data" / "poblacion.parquet"


# --- El factor prestacional por firma ----------------------------------------


def _cargar_parametros() -> dict[str, Any]:
    with open(PARAMETROS, encoding="utf-8") as f:
        return json.load(f)


class ClienteReglasPorSector(ClienteReglas):
    """La ablación, pero con el factor prestacional que le toca a cada firma.

    `ClienteReglas` usa un factor único para toda la población. Eso es
    exactamente lo que la nota de `parametros_legales.json` prohíbe: el rango
    1,38-1,58 no es incertidumbre, es estructura (clase de riesgo del sector ×
    si el empleador está exonerado del 114-1).

    # SUPUESTO: se está exonerado con 2+ trabajadores. El tope de 10 SMLMV
    # también aplica en la ley, pero la moda del parquet está muy por debajo, así
    # que el que discrimina es el conteo. La frontera cae justo en el
    # micro-empleador, que es donde vive el 66,7% de la informalidad de Bogotá.
    """

    def __init__(self, parametros: dict[str, Any]) -> None:
        super().__init__()
        self._por_sector = parametros["factor_prestacional_por_sector"]
        self._min_trab = parametros["exoneracion_114_1"]["min_trabajadores"]
        self.factores_usados: dict[str, float] = {}

    def factor_de(self, arq: Arquetipo) -> float:
        entrada = self._por_sector.get(arq.sector) or self._por_sector["no_informa"]
        clave = "exonerado" if arq.n_trabajadores >= self._min_trab else "no_exonerado"
        sub = entrada.get(clave) or next(iter(entrada.values()))
        return 1.0 + float(sub["sobrecosto_pct"])

    def proponer(self, sistema, usuario, modelo="reglas-fijas", max_tokens=0,
                 contexto=None):
        if contexto is None:
            raise ValueError("la ablación necesita `contexto`")
        arq = contexto["arquetipo"]
        # Se muta el atributo justo antes de delegar. Es seguro porque este
        # cliente se corre con paralelismo=1 (ver `_correr_una`): una regla fija
        # no espera red, así que el paralelismo no compraba nada y sí abría una
        # carrera sobre este atributo.
        self.factor_prestacional = self.factor_de(arq)
        self.factores_usados[arq.id] = self.factor_prestacional
        return super().proponer(sistema, usuario, modelo, max_tokens, contexto)


# --- La corrida ---------------------------------------------------------------


def _correr_una(
    arquetipos: list[Arquetipo],
    *,
    aumento: float,
    modo: str,
    parametros: dict[str, Any],
    tasa_inicial: float,
    seed: int,
    n_parafrasis: int,
    cobertura: float | None,
    tope_usd: float,
    multa_factor: float,
    capacidad: float,
) -> tuple[list[Ronda], Any]:
    """Una política, una corrida. Devuelve las rondas y el cliente (para el gasto)."""
    if modo == "llm":
        from behavior.cliente import ClienteConductual
        from behavior.presupuesto import Presupuesto

        cliente = ClienteConductual(presupuesto=Presupuesto(tope_usd=tope_usd))
        paralelismo = 8
    else:
        cliente = ClienteReglasPorSector(parametros)
        paralelismo = 1

    # El estado vivo del MOTOR, y el veto real encima. Esto es lo que `demo.py`
    # no hace: acá el veto que corre es `engine/veto.py`, no el doble de prueba.
    estado = EstadoVivo.inicial(arquetipos)
    por_id = {a.id: a for a in arquetipos}

    def al_terminar(r: Ronda) -> None:
        """Sutura: lo que decidió la ronda entra al estado que verá el veto.

        Se recalcula igual que `behavior/rondas.py:324-336` —promediando entre
        paráfrasis y acumulando sobre la fracción previa— porque `Ronda` expone
        las decisiones crudas, no la fracción ya agregada. Es duplicación, y es
        exactamente el PUNTO DE SUTURA que `rondas.py:197` dice que debe
        desaparecer cuando el motor lleve el estado. Acá el motor SÍ lo lleva:
        `EstadoVivo` es la fuente, y esta función la alimenta.
        """
        from behavior import contrato as _c

        for aid, res in r.por_arquetipo.items():
            a = por_id.get(aid)
            if a is None or not res.decisiones:
                continue
            prev_inf = estado.fraccion_informal_previa(aid)
            prev_emp = estado.fraccion_empleada_previa(aid)
            ds = res.decisiones
            frac = sum(
                _c.fraccion_fuera_de_regla(d, a.n_trabajadores, prev_inf) for d in ds
            ) / len(ds)
            despidos = sum(
                min(1.0, d["detalle"].get("empleados_a_despedir", 0)
                    / max(1, a.n_trabajadores))
                for d in ds
            ) / len(ds)
            estado.registrar(
                aid,
                fraccion_informal=frac,
                fraccion_empleada=max(0.0, prev_emp - despidos),
            )

    rondas = correr(
        arquetipos,
        cliente,
        aumento_pct=aumento,
        seed=seed,
        simulacion_id=f"barrido-{aumento:g}-s{seed}",
        veto=veto_del_motor(estado),
        n_parafrasis=n_parafrasis,
        paralelismo=paralelismo,
        cobertura_llm=cobertura,
        tasa_informalidad_inicial=tasa_inicial,
        multa_factor=multa_factor,
        capacidad_fiscalizacion=capacidad,
        al_terminar_ronda=al_terminar,
    )
    return rondas, cliente


def _resumen(rondas: list[Ronda], aumento: float, seed: int) -> dict[str, Any]:
    from engine.fiscalizacion import es_degenerado, prob_sancion, satura

    r0, rf = rondas[0], rondas[-1]
    # Los dos detectores que Manuel escribió para que un resultado de borde no se
    # lea como un resultado del modelo (`engine/fiscalizacion.py`), en las MISMAS
    # unidades que usa `behavior/rondas.py:_prob_fiscalizacion`: pesos absolutos
    # de población expandida, no tasas.
    peso_total = sum(rf.pesos.values()) or 1.0
    capacidad_abs = 0.02 * peso_total

    def _e(r: Ronda) -> float:
        return r.tasa_informalidad * peso_total

    # Paridad entre las dos implementaciones de la MISMA ADR 0007. Se comparan
    # con los MISMOS argumentos —la `p` de la ronda k sale de la informalidad de
    # la ronda k-1, no de la de k—, porque cruzarlas mal fabrica una divergencia
    # que no existe.
    #
    # Verificado: coinciden al bit en todo el régimen del proyecto. Difieren solo
    # con capacidad absoluta baja (< ~20 inspecciones), donde
    # `behavior/rondas.py:145` corta con `return 1.0` y
    # `engine/fiscalizacion.py` aplica `max(E, 1)` — hasta 37 pp con C=1. Hoy no
    # muerde (C ≈ 84.000), pero muerde en cuanto la capacidad sea una perilla.
    motor = [prob_sancion(capacidad_abs, _e(rondas[i - 1]) if i else _e(rondas[0]))
             for i in range(len(rondas))]
    capa = [r.prob_fiscalizacion for r in rondas]
    delta = max(abs(a - b) for a, b in zip(motor, capa))
    return {
        "rondas_degeneradas": [i for i, r in enumerate(rondas) if es_degenerado(_e(r))],
        "rondas_saturadas": [i for i, r in enumerate(rondas)
                             if satura(capacidad_abs, _e(r))],
        "absorbente": bool(satura(capacidad_abs, _e(rf))),
        "prob_motor_final": motor[-1],
        "prob_capa_final": capa[-1],
        "divergencia_motor_capa": delta,
        "aumento_pct": aumento,
        "seed": seed,
        "informalidad_r0": r0.tasa_informalidad,
        "informalidad_final": rf.tasa_informalidad,
        "brecha_pp": (rf.tasa_informalidad - r0.tasa_informalidad) * 100,
        "prob_sancion_r0": r0.prob_fiscalizacion,
        "prob_sancion_final": rf.prob_fiscalizacion,
        "empleo_relativo_final": rf.empleo_relativo,
        "empleo_perdido_pp": (1.0 - rf.empleo_relativo) * 100,
        "banda_p10": rf.banda.get("p10"),
        "banda_p90": rf.banda.get("p90"),
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
            }
            for r in rondas
        ],
    }


# --- Reporte por terminal -----------------------------------------------------


def _pp(x: float) -> str:
    return f"{x:+.1f}"


def _reporte(corridas: list[dict[str, Any]], meta: dict[str, Any]) -> str:
    L: list[str] = []
    A = L.append
    A("")
    A("=" * 92)
    A("  BARRIDO DE POLÍTICAS — informe de estado del simulador")
    A(f"  {meta['fecha']} · modo {meta['modo'].upper()} · {meta['n_arquetipos']} arquetipos "
      f"· {meta['repeticiones']} repeticiones por política")
    A("=" * 92)
    A("")
    A(f"  Población: {meta['poblacion']}  ·  informalidad observada (GEIH): "
      f"{meta['tasa_inicial']:.1%}")
    A(f"  Veto: {meta['veto']}  ·  capacidad fiscalización: {meta['capacidad']}  "
      f"·  multa: {meta['multa_factor']:g} meses")
    if meta.get("gasto_usd") is not None:
        A(f"  Gasto: ${meta['gasto_usd']:.2f}  ·  llamadas: {meta['llamadas']}")
    A("")

    # Agregado por política
    por_pol: dict[float, list[dict[str, Any]]] = {}
    for c in corridas:
        por_pol.setdefault(c["aumento_pct"], []).append(c)

    # --- Detalle: cada corrida, una línea. Es lo que permite ver la dispersión
    A("  CADA SIMULACIÓN (r = repetición, cada una con una paráfrasis distinta)")
    A("  " + "-" * 88)
    A(f"  {'alza':>6} {'r':>3} {'informalidad':>13} {'brecha':>10} "
      f"{'p(sanción)':>12} {'empleo':>9}  estrategia dominante")
    A("  " + "-" * 88)
    for pol in sorted(por_pol):
        for c in sorted(por_pol[pol], key=lambda x: x.get("repeticion", 0)):
            est = c.get("estrategias") or {}
            dom = max(est, key=est.get) if est else "—"
            A(f"  {pol:>5.0f}% {c.get('repeticion', 0):>3} "
              f"{c['informalidad_final']:>12.1%} {_pp(c['brecha_pp']):>7} pp "
              f"{c['prob_sancion_final']:>11.2%} {c['empleo_relativo_final']:>8.1%}"
              f"  {dom} ({est.get(dom, 0):.0%})")
        # Dispersión entre las repeticiones de esta misma política
        fs = [c["informalidad_final"] for c in por_pol[pol]]
        es = [c["empleo_relativo_final"] for c in por_pol[pol]]
        d_inf, d_emp = (max(fs) - min(fs)) * 100, (max(es) - min(es)) * 100
        veredicto = ("IDÉNTICAS" if d_inf < 1e-9 and d_emp < 1e-9
                     else f"varían: informalidad ±{d_inf:.1f} pp, empleo ±{d_emp:.1f} pp")
        A(f"  {'':>6} {'':>3} {'└─ entre las ' + str(len(fs)) + ' repeticiones: ' + veredicto}")
    A("  " + "-" * 88)
    A("")

    # --- Resumen por política
    A("  RESUMEN POR POLÍTICA (mediana de las repeticiones)")
    A("  " + "-" * 88)
    A(f"  {'alza':>6} {'informal. final':>17} {'brecha':>9} {'p(sanción)':>12} "
      f"{'empleo':>9} {'dispersión':>14}")
    A("  " + "-" * 88)
    for pol in sorted(por_pol):
        cs = por_pol[pol]
        finales = [c["informalidad_final"] for c in cs]
        empleos = [c["empleo_relativo_final"] for c in cs]
        disp = (max(finales) - min(finales)) * 100
        A(f"  {pol:>5.0f}% {statistics.median(finales):>15.1%}   "
          f"{_pp(statistics.median([c['brecha_pp'] for c in cs])):>7} pp "
          f"{statistics.median([c['prob_sancion_final'] for c in cs]):>11.2%} "
          f"{statistics.median(empleos):>8.1%} {disp:>11.1f} pp")
    A("  " + "-" * 88)
    A("")

    # --- Monotonía: ¿la serie sube parejo o no?
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
    A("")

    if meta.get("control"):
        c = meta["control"]
        A("  CONTROL DE DETERMINISMO (repetir exacto la misma corrida)")
        A(f"      política {c['politica']:g}%, misma paráfrasis, misma semilla → "
          + ("IDÉNTICA (el pipeline es determinista con caché)"
             if c["identica"] else f"DIFIERE: {c['diferencias']}"))
        A("")

    # Trayectoria de la política central
    centro = sorted(por_pol)[len(por_pol) // 2]
    A(f"  Trayectoria por ronda — alza {centro:g}% (mediana de las repeticiones):")
    A("")
    rondas_n = len(por_pol[centro][0]["por_ronda"])
    A(f"      {'ronda':>6} {'informalidad':>14} {'p(sanción)':>12} {'empleo':>9}")
    for i in range(rondas_n):
        infs = [c["por_ronda"][i]["informalidad"] for c in por_pol[centro]]
        prs = [c["por_ronda"][i]["prob_sancion"] for c in por_pol[centro]]
        emp = [c["por_ronda"][i]["empleo_relativo"] for c in por_pol[centro]]
        etiqueta = "0 (oficial)" if i == 0 else str(i)
        A(f"      {etiqueta:>6} {statistics.median(infs):>13.1%} "
          f"{statistics.median(prs):>11.2%} {statistics.median(emp):>8.1%}")
    A("")

    # Estrategias
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
    A("=" * 92)
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
    ap.add_argument("--capacidad", type=float, default=0.02)
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
    parametros = _cargar_parametros()
    arquetipos = desde_poblacion(str(POBLACION))
    tasa_inicial = informalidad_observada()

    if args.cobertura and modo == "llm":
        cabeza, cola = particionar_por_peso(arquetipos, args.cobertura)
        print(f"top-K: {len(cabeza)} arquetipos al LLM, {len(cola)} a reglas fijas")

    print(f"modo {modo} · {len(arquetipos)} arquetipos · {len(puntos)} políticas "
          f"({', '.join(f'{p:g}%' for p in puntos)}) · {args.repeticiones} repeticiones")
    print(f"informalidad observada (GEIH): {tasa_inicial:.1%}")
    if modo == "llm":
        est = len(puntos) * args.repeticiones * 100
        print(f"estimado ~{est} llamadas · tope ${args.tope:.2f}")
    print()

    corridas: list[dict[str, Any]] = []
    gasto = 0.0
    llamadas = 0
    t0 = time.time()

    # Cada repetición es una TRAYECTORIA COMPLETA e independiente, fijada a una
    # paráfrasis distinta del prompt. Es más fuerte que `n_parafrasis=N`, donde
    # las N parten todas del mismo estado previo (`rondas.py:_banda` lo declara):
    # acá las 3 divergen desde la ronda 1 y arrastran su propia historia.
    #
    # No se usan semillas distintas porque la caché se indexa por prompt y el
    # prompt no lleva seed: 3 semillas serían 3 aciertos de caché idénticos.
    # Eso se COMPRUEBA abajo con la corrida de control, no se da por hecho.
    import behavior.capa as _capa
    from behavior.cliente import parafrasis as _parafrasis

    _TODAS = _parafrasis(5)

    def _fijar(indice: int) -> None:
        _capa.parafrasis = lambda n=1, _i=indice: [_TODAS[_i % len(_TODAS)]]

    def _una(pol: float, i: int) -> dict[str, Any] | None:
        nonlocal gasto, llamadas
        _fijar(i)
        try:
            rondas, cliente = _correr_una(
                arquetipos, aumento=pol, modo=modo, parametros=parametros,
                tasa_inicial=tasa_inicial, seed=args.seed,
                n_parafrasis=1, cobertura=args.cobertura if modo == "llm" else None,
                tope_usd=max(0.01, args.tope - gasto), multa_factor=args.multa_factor,
                capacidad=args.capacidad,
            )
        except Exception as e:  # noqa: BLE001
            print(f"  {pol:>5g}%  r{i + 1}  FALLÓ: {type(e).__name__}: {e}",
                  file=sys.stderr)
            return None
        res = _resumen(rondas, pol, args.seed)
        res["repeticion"] = i + 1
        res["parafrasis"] = i + 1
        g = getattr(getattr(cliente, "presupuesto", None), "gastado_usd", 0.0) or 0.0
        gasto += g
        llamadas += getattr(cliente, "llamadas", 0)
        return res

    for pol in puntos:
        for i in range(args.repeticiones):
            res = _una(pol, i)
            if res is None:
                continue
            corridas.append(res)
            print(f"  {pol:>5g}%  r{i + 1}  informalidad {res['informalidad_final']:>6.1%}"
                  f"  brecha {res['brecha_pp']:>+6.1f} pp"
                  f"  p(sanción) {res['prob_sancion_final']:>6.2%}"
                  f"  empleo {res['empleo_relativo_final']:>6.1%}"
                  + ("  [$%.2f]" % gasto if modo == "llm" else ""))

    # --- Control de determinismo (ADR 0009 nivel 2) ---------------------------
    # Se repite EXACTAMENTE la primera corrida (misma política, misma paráfrasis,
    # misma semilla). Si el pipeline es determinista tiene que salir idéntica.
    control: dict[str, Any] = {}
    if corridas:
        pol0 = corridas[0]["aumento_pct"]
        rep = _una(pol0, 0)
        if rep is not None:
            campos = ("informalidad_final", "prob_sancion_final",
                      "empleo_relativo_final", "brecha_pp")
            difs = {k: (corridas[0][k], rep[k]) for k in campos
                    if abs(corridas[0][k] - rep[k]) > 1e-12}
            control = {
                "politica": pol0,
                "identica": not difs,
                "diferencias": difs,
            }

    if not corridas:
        print("\nninguna corrida terminó. Nada que reportar.", file=sys.stderr)
        return 2

    meta = {
        "fecha": datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M"),
        "modo": modo,
        "n_arquetipos": len(arquetipos),
        "repeticiones": args.repeticiones,
        "poblacion": "data/poblacion.parquet (GEIH Bogotá 2026)",
        "tasa_inicial": tasa_inicial,
        "veto": "engine/veto.py (el real)",
        "capacidad": args.capacidad,
        "multa_factor": args.multa_factor,
        "segundos": round(time.time() - t0, 1),
        "gasto_usd": gasto if modo == "llm" else None,
        "llamadas": llamadas,
        "control": control,
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
