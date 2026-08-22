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

from behavior.ablacion import ClienteReglas
from behavior.arquetipos import (
    Arquetipo,
    arquetipos_falsos,
    desde_poblacion,
    informalidad_observada,
    particionar_por_peso,
)
from behavior.cache import Cache
from behavior.cliente import ClienteConductual, SinCredenciales
from behavior.rondas import correr


def veto_doble_prueba(decision: dict[str, Any], arquetipo: Arquetipo) -> dict[str, Any]:
    """Doble de prueba del veto de Manuel. NO es el veto.

    El veto real vive en `engine/` y lo escribe R2. Este solo implementa la
    restricción más obvia — no puedes despedir si no tienes con qué indemnizar —
    para que el camino de reintento se ejercite antes de que exista el motor.
    """
    estrategia = decision["estrategia_propuesta"]
    n = decision["detalle"].get("empleados_a_despedir", 0)
    if estrategia == "despedir" and n:
        costo = n * arquetipo.costo_despido
        if costo > arquetipo.flujo_caja:
            return {
                "factible": False,
                "razon": (
                    f"flujo de caja insuficiente para pagar indemnizaciones: "
                    f"necesitas {costo:,.0f} u y tienes {arquetipo.flujo_caja:,.0f} u"
                ),
            }
    if estrategia in {"informalizar_total", "informalizar_parcial"} and not arquetipo.formal:
        return {"factible": False, "razon": "esta unidad ya opera fuera de regla"}
    return {"factible": True, "razon": None}


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
    print(f"propuestas vetadas: {vetadas} · fallbacks a 'absorber': {fallbacks}")
    print(f"\ncontrato ronda.json de la última ronda:\n  {rondas[-1].a_contrato()}")

    presupuesto = getattr(cliente, "presupuesto", None)
    if presupuesto is not None:
        print(f"\n{presupuesto.informe()}")
    cache = getattr(cliente, "cache", None)
    if cache is not None:
        print(f"caché disco: {cache.aciertos} aciertos / {cache.fallos} fallos "
              f"({cache.tasa_acierto:.0%})")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--llm", action="store_true", help="usar la capa LLM real")
    ap.add_argument("--barrido", action="store_true", help="barrer aumento_pct para ver el codo")
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
    args = ap.parse_args(argv)

    arquetipos = (
        desde_poblacion("data/poblacion.parquet") if args.real else arquetipos_falsos()
    )
    if args.llm:
        from behavior.presupuesto import Presupuesto
        tope = args.tope if args.tope is not None else (5.0 if args.parafrasis >= 5 else 3.0)
        cliente = ClienteConductual(presupuesto=Presupuesto(tope_usd=tope))
    else:
        cliente = ClienteReglas()
    modo = "LLM (Haiku)" if args.llm else "ABLACIÓN (reglas fijas)"
    fuente = "poblacion.parquet" if args.real else "andamio"
    print(f"modo: {modo} · {len(arquetipos)} arquetipos ({fuente}) · "
          f"seed {args.seed} · {args.parafrasis} paráfrasis")
    # La ronda 0 es la proyección oficial: parte de la informalidad OBSERVADA.
    # Con datos reales sale de `momentos.json` (Alejo); con andamio es un número
    # de andamio y se dice.
    if args.real:
        tasa_inicial = informalidad_observada()
        print(f"informalidad observada (GEIH, momentos.json): {tasa_inicial:.1%}")
    else:
        # SUPUESTO: 42% es un número de andamio, no la GEIH. Con `--real` se
        # reemplaza por el observado.
        tasa_inicial = 0.42
    if args.cobertura:
        cabeza, cola = particionar_por_peso(arquetipos, args.cobertura)
        print(f"top-K: {len(cabeza)} arquetipos al LLM, {len(cola)} a reglas fijas")
    # ADR 0009: el par (seed, manifiesto) es lo que hace comparables dos corridas.
    print(f"seed {args.seed} · manifiesto de caché {Cache().manifiesto()}")

    aumentos = [7.0, 13.6, 23.0, 30.0] if args.barrido else [args.aumento]
    try:
        for aumento in aumentos:
            print(f"\n{'=' * 78}\npolítica: el costo laboral formal sube {aumento:g}%")
            rondas = correr(
                arquetipos,
                cliente,
                aumento_pct=aumento,
                seed=args.seed,
                veto=veto_doble_prueba,
                n_parafrasis=args.parafrasis,
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
