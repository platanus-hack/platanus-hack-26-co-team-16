"""Corrida punta a punta de la capa conductual, sin motor y sin API key.

    python3 -m behavior.demo              # ablación (reglas fijas, $0, sin key)
    python3 -m behavior.demo --llm        # capa LLM real (necesita credenciales)
    python3 -m behavior.demo --barrido    # el codo: varias políticas seguidas

Qué prueba: que las 4 rondas corren, que el veto se encaja y se reintenta, y que
la cascada aparece. Los números NO son un resultado del proyecto: el motor real
es `engine/` (Manuel) y la población real es `data/` (Alejo). Esto es el andamio
que permite construir antes de que existan los dos.
"""

from __future__ import annotations

import argparse
import sys
from typing import Any

from behavior.ablacion import ClienteReglas
from behavior.arquetipos import Arquetipo, arquetipos_falsos
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
        top = next(iter(desglose)) if desglose else "-"
        print(
            f"{r.ronda:>5} {r.tasa_informalidad:>12.1%} {r.prob_fiscalizacion:>9.1%} "
            f"{r.empleo_relativo:>7.1%} {r.varianza_media:>9.2f}  {top}"
        )

    inicial, final = rondas[0].tasa_informalidad, rondas[-1].tasa_informalidad
    print(f"\ncascada: {inicial:.1%} -> {final:.1%}  ({(final - inicial) * 100:+.1f} pp)")
    print(f"desglose final (dato A4): {rondas[-1].desglose_estrategias()}")

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
    ap.add_argument("--tope", type=float, default=None,
                    help="tope de presupuesto USD (default 3.00; sube a 5 con --parafrasis 5)")
    args = ap.parse_args(argv)

    arquetipos = arquetipos_falsos()
    if args.llm:
        from behavior.presupuesto import Presupuesto
        tope = args.tope if args.tope is not None else (5.0 if args.parafrasis >= 5 else 3.0)
        cliente = ClienteConductual(presupuesto=Presupuesto(tope_usd=tope))
    else:
        cliente = ClienteReglas()
    modo = "LLM (Haiku)" if args.llm else "ABLACIÓN (reglas fijas)"
    print(f"modo: {modo} · {len(arquetipos)} arquetipos · seed {args.seed} · "
          f"{args.parafrasis} paráfrasis")

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
            )
            _imprimir(rondas, cliente)
    except SinCredenciales as e:
        print(f"\n{e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
