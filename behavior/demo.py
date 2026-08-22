"""Corrida punta a punta de la capa conductual, sin motor y sin API key.

    python3 -m behavior.demo              # ablación (reglas fijas, $0, sin key)
    python3 -m behavior.demo --llm        # capa LLM real (necesita credenciales)
    python3 -m behavior.demo --barrido    # el codo: varias políticas seguidas
    python3 -m behavior.demo --real       # la población real de data/poblacion.parquet
    python3 -m behavior.demo --real --cobertura 0.8   # top-K: solo el 80% al LLM

Qué prueba: que las rondas corren, que el veto se encaja y se reintenta, y que
la cascada aparece. El calendario es el de la ADR 0005: la ronda 0 es la
proyección oficial (sin LLM) y las 1-3 son mejor respuesta. Los números NO son un resultado del proyecto: el motor real
es `engine/` (Manuel) y la población real es `data/` (Alejo). Esto es el andamio
que permite construir antes de que existan los dos.
"""

from __future__ import annotations

import argparse
import sys
from typing import Any

from behavior import contrato
from behavior.ablacion import ClienteReglas
from behavior.arquetipos import (
    Arquetipo,
    arquetipos_falsos,
    desde_empresas,
    informalidad_observada,
    particionar_por_peso,
    poblacion_cuenta_propia,
)
from behavior.cache import Cache
from behavior.capa import Reskin
from behavior.cliente import ClienteConductual, SinCredenciales
from behavior.rondas import UMBRAL_ESTABILIDAD_PP, correr


def _imprimir(rondas, cliente) -> None:
    print(f"\n{'ronda':>5} {'informalidad':>13} {'p.sanción':>10} {'empleo':>8} "
          f"{'varianza':>9}  estrategia dominante")
    print("-" * 78)
    for r in rondas:
        desglose = r.desglose_estrategias()
        top = next(iter(desglose)) if desglose else "-"  # ponderado, no por conteo
        print(
            f"{r.ronda:>5} {r.tasa_informalidad:>12.1%} {r.prob_fiscalizacion:>9.1%} "
            f"{r.empleo_relativo:>7.1%} {r.varianza_media:>9.2f}  {top}"
        )

    # `brecha` = última ronda − ronda 0, y la ronda 0 es la proyección oficial
    # (ADR 0005). Es el producto entero del proyecto: cuánta informalidad hay de
    # más respecto de lo que el modelo oficial asumió (dato A1).
    oficial, final = rondas[0].tasa_informalidad, rondas[-1].tasa_informalidad
    print(f"\nproyección oficial (ronda 0): {oficial:.1%}")
    print(f"brecha (dato A1): {oficial:.1%} -> {final:.1%}  "
          f"({(final - oficial) * 100:+.1f} pp)")
    if rondas[-1].fraccion_poblacion_llm < 1.0:
        print(f"top-K: {rondas[-1].fraccion_poblacion_llm:.1%} de la población "
              f"decidida por LLM; el resto por reglas fijas")
    print("\ndesglose final (dato A4) — ponderado por factor de expansión:")
    for k, v in rondas[-1].desglose_estrategias().items():
        print(f"  {k:22s} {v:6.1%} de la población")
    print(f"  (por conteo de arquetipos, sin ponderar: "
          f"{rondas[-1].desglose_estrategias_conteo()})")

    vetadas = sum(len(x.vetadas) for r in rondas for x in r.por_arquetipo.values())
    fallbacks = sum(x.fallbacks for r in rondas for x in r.por_arquetipo.values())
    sin_salida = sum(x.sin_salida for r in rondas for x in r.por_arquetipo.values())
    ultima = rondas[-1]

    # A5 — la regla de corte, declarada antes de correr y estampada acá.
    sello = "ESTABILIZADA" if ultima.estabilizada else "NO ESTABILIZADA"
    print(f"\nmovimiento de la última ronda: {ultima.movimiento_pp:+.1f} pp · {sello}"
          f"  (umbral {UMBRAL_ESTABILIDAD_PP:g} pp)")
    # B2 — qué dispersión se está publicando. La etiqueta viaja con el número.
    banda = ultima.banda
    tipo = banda.get("tipo", "intra_ronda")
    if banda.get("degenerada"):
        print(f"banda ({tipo}): degenerada — una sola trayectoria, no hay dispersión que medir")
    else:
        print(f"banda ({tipo}): p10 {banda['p10']:.1%} / p90 {banda['p90']:.1%}"
              f"  = {(banda['p90'] - banda['p10']) * 100:.1f} pp de ancho")
    # A4 — la cuarta cifra: quien conserva el empleo pero pierde ingreso.
    if ultima.fraccion_jornada_recortada > 0:
        perdida = (1.0 - ultima.ingreso_laboral_relativo / max(ultima.empleo_relativo, 1e-9))
        print(f"jornada: {ultima.fraccion_jornada_recortada:.1%} de la población conserva el "
              f"empleo con jornada recortada · masa salarial relativa "
              f"{ultima.ingreso_laboral_relativo:.1%} (pierde {perdida:.1%} por horas)")
    # C3 — el traslado declarado, con su nombre honesto.
    if ultima.traslado_precios_pct > 0:
        print(f"traslado a precios DECLARADO por las firmas: {ultima.traslado_precios_pct:.2f}% "
              f"(no es un pronóstico de inflación: no hay respuesta de demanda)")
    print(f"propuestas vetadas: {vetadas} · fallbacks: {fallbacks} "
          f"({ultima.fraccion_fallback:.1%} de las decisiones) · sin ninguna opción "
          f"factible: {sin_salida} ({ultima.fraccion_sin_salida:.1%})")
    if ultima.fraccion_fallback > 0.05:
        print("  ATENCIÓN: los fallbacks superan el 5% declarado ANTES de correr. "
              "Se reporta, no se ajusta: revisar el 0,18 de margen sobre nómina.")
    print(f"\ncontrato ronda.json de la última ronda:\n  {rondas[-1].a_contrato()}")

    presupuesto = getattr(cliente, "presupuesto", None)
    if presupuesto is not None:
        print(f"\n{presupuesto.informe()}")
    # En modo ablación el presupuesto cuenta 0 llamadas —correcto, no se llamó a
    # ninguna API— pero se leía como si no hubiera pasado nada. Las decisiones de
    # la regla fija sí se cuentan, en su propio contador.
    if getattr(cliente, "llamadas", None) and not presupuesto.llamadas:
        print(f"decisiones por regla fija: {cliente.llamadas} (sin API, $0)")
    cache = getattr(cliente, "cache", None)
    if cache is not None:
        print(f"caché disco: {cache.aciertos} aciertos / {cache.fallos} fallos "
              f"({cache.tasa_acierto:.0%})")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--llm", action="store_true", help="usar la capa LLM real")
    ap.add_argument("--barrido", action="store_true", help="barrer aumento_pct para ver el codo")
    ap.add_argument("--puntos", type=str, default=None,
                    help="puntos del barrido separados por coma (p.ej. 7,13.6,23,30)")
    ap.add_argument("--aumento", type=float, default=23.0)
    ap.add_argument("--parafrasis", type=int, default=1, help="N>=5 para banda de error")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--paralelismo", type=int, default=8,
                    help="arquetipos concurrentes por ronda (1 = secuencial)")
    ap.add_argument("--real", action="store_true",
                    help="usar data/poblacion.parquet en vez de los arquetipos de andamio")
    ap.add_argument("--cobertura", type=float, default=None,
                    help="modo top-K: fracción de población que va al LLM (p.ej. 0.8)")
    ap.add_argument("--tope", type=float, default=None,
                    help="tope de presupuesto USD (default 3.00; sube a 5 con --parafrasis 5)")
    ap.add_argument("--reparto", action="store_true",
                    help="B1: repartir las paráfrasis por peso poblacional (3 a 9 por arquetipo)")
    ap.add_argument("--sin-cascada", action="store_true",
                    help="B4: congelar p(sanción) en su valor de la ronda 0")
    ap.add_argument("--reskin", action="store_true",
                    help="C6: renombrar sectores y reescalar montos (candado 3b)")
    args = ap.parse_args(argv)

    # C1 — la grilla real es la de EMPLEADORES, no la de personas. Antes salía de
    # `poblacion.parquet` y esta capa re-derivaba caja, indemnización y factor
    # prestacional con coeficientes de andamio; `empresas.parquet` los trae con
    # fuente legal, celda por celda.
    arquetipos = (
        desde_empresas("data/empresas.parquet") if args.real else arquetipos_falsos()
    )
    if args.llm:
        from behavior.presupuesto import Presupuesto
        tope = args.tope if args.tope is not None else (5.0 if args.parafrasis >= 5 else 3.0)
        cliente = ClienteConductual(presupuesto=Presupuesto(tope_usd=tope))
    else:
        cliente = ClienteReglas()
    modo = "LLM (Haiku)" if args.llm else "ABLACIÓN (reglas fijas)"
    fuente = "empresas.parquet" if args.real else "andamio"
    print(f"modo: {modo} · {len(arquetipos)} arquetipos ({fuente}) · "
          f"seed {args.seed} · {args.parafrasis} paráfrasis")
    # La ronda 0 es la proyección oficial: parte de la informalidad OBSERVADA,
    # que se lee de `data/momentos.json` (R1) en los dos modos. Antes el modo
    # andamio usaba un 0,42 sin fuente que el propio repo contradice — no era un
    # número sin respaldo, era un número refutado por un dato ya mergeado. Y no
    # es cosmético: `p(E) = 1 − exp(−C/tasa)` sube de 4,65% a 6,33% al corregirlo,
    # y ese salto cruza el umbral de decisión de la ablación (ver README §4).
    tasa_inicial = informalidad_observada()
    print(f"informalidad observada (GEIH, momentos.json): {tasa_inicial:.1%}")
    if not args.real:
        # SUPUESTO: el dato observado se aplica sobre una grilla de arquetipos de
        # andamio, cuya composición formal/informal es inventada. Es coherente
        # para la ronda 0 (una tasa agregada del universo) pero la corrida de
        # andamio sigue sin ser un resultado. Con `--real` desaparece la mezcla.
        print("  (dato real sobre la grilla de andamio: la corrida no es un resultado)")
    if args.cobertura:
        cabeza, cola = particionar_por_peso(arquetipos, args.cobertura)
        print(f"top-K: {len(cabeza)} arquetipos al LLM, {len(cola)} a reglas fijas")
    # ADR 0009: el par (seed, manifiesto) es lo que hace comparables dos corridas.
    print(f"seed {args.seed} · manifiesto de caché {Cache().manifiesto()}")

    if args.puntos:
        aumentos = [float(x) for x in args.puntos.split(",")]
    elif args.barrido:
        aumentos = [7.0, 13.6, 23.0, 30.0]
    else:
        aumentos = [args.aumento]
    try:
        for aumento in aumentos:
            print(f"\n{'=' * 78}\npolítica: el costo laboral formal sube {aumento:g}%")
            rondas = correr(
                arquetipos,
                cliente,
                aumento_pct=aumento,
                seed=args.seed,
                # C2 — `veto=None` significa el veto REAL del motor, con el
                # estado vivo adentro. Antes acá iba `veto_doble_prueba`, así
                # que toda corrida hecha hasta hoy usó el doble de prueba y
                # ninguna probó el motor. La función se borró, no se dejó de
                # adorno: mientras existiera, alguien la iba a volver a pasar.
                veto=None,
                n_parafrasis=args.parafrasis,
                parafrasis_por_peso=args.reparto,
                congelar_prob_fiscalizacion=args.sin_cascada,
                reskin=(
                    Reskin.desde_seed([a.sector for a in arquetipos], args.seed)
                    if args.reskin
                    else None
                ),
                paralelismo=args.paralelismo,
                cobertura_llm=args.cobertura,
                tasa_informalidad_inicial=tasa_inicial,
            )
            _imprimir(rondas, cliente)
    except SinCredenciales as e:
        print(f"\n{e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
