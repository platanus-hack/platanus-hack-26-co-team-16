#!/usr/bin/env python3
"""Reproduce el resultado principal en una máquina limpia, SIN API key.

    python3 scripts/reproduce.py

Qué hace: importa la caché versionada del escenario demo (`behavior/cache-demo.json`)
y corre la simulación. Si la caché cubre todas las llamadas, no se toca la red y el
resultado es idéntico al publicado. Si no está, cae a la ablación con reglas fijas,
que es determinista por construcción y no necesita credenciales.

Por qué existe (C4 del plan de correcciones): un jurado que clone el repo sin API
key recibía `SinCredenciales` y no podía correr nada. La promesa de determinismo del
proyecto —"mismo seed, mismo resultado"— era verificable solo por nosotros, que es
lo mismo que decir que no era verificable.

Esto implementa el **nivel 2** de la [ADR 0009](../docs/adr/0009-frontera-del-determinismo.md):
*mismo seed + misma caché + mismas versiones = mismo resultado*. El nivel 3 (la
ablación sin LLM) es el respaldo automático de este script.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from behavior.ablacion import ClienteReglas  # noqa: E402
from behavior.arquetipos import (  # noqa: E402
    desde_empresas,
    informalidad_observada,
)
from behavior.cache import Cache  # noqa: E402
from behavior.cliente import SinCredenciales  # noqa: E402
from behavior.presupuesto import Presupuesto, PresupuestoAgotado  # noqa: E402
from behavior.rondas import UMBRAL_ESTABILIDAD_PP, correr  # noqa: E402

CACHE_DEMO = RAIZ / "behavior" / "cache-demo.json"
EMPRESAS = RAIZ / "data" / "empresas.parquet"
MOMENTOS = RAIZ / "data" / "momentos.json"

# El escenario que se reproduce: el aumento del 23% del caso demo.
AUMENTO_DEMO = 23.0
SEED_DEMO = 42


class _ConCaida:
    """La caché primero; lo que no esté cacheado lo resuelve la regla fija.

    Existe porque este script PROMETE reproducir con un comando en una máquina
    limpia, y antes no cumplía: en cuanto una sola llamada no estaba en la
    caché, `ClienteConductual` levantaba `SinCredenciales` y el script moría con
    un stack trace. La promesa del repo —"un extraño con el link tiene que poder
    usarlo"— se caía en la primera celda.

    La caché deja de cubrir la corrida entera cada vez que cambia algo que entra
    al texto del prompt (la probabilidad de inspección por celda, o los propios
    `behavior/prompts/*.md`), porque la clave es un sha256 de ese texto. Cuando
    eso pasa, la salida sigue siendo determinista y el script lo DICE: reporta
    cuántas decisiones vinieron del modelo y cuántas de la regla.
    """

    def __init__(self, llm, reglas: ClienteReglas) -> None:
        self._llm = llm
        self._reglas = reglas
        self.presupuesto = llm.presupuesto
        self.aciertos = 0
        self.caidas = 0

    def proponer(self, *a, **kw):
        try:
            salida = self._llm.proponer(*a, **kw)
        except (SinCredenciales, PresupuestoAgotado):
            self.caidas += 1
            return self._reglas.proponer(*a, **kw)
        self.aciertos += 1
        return salida


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--aumento", type=float, default=AUMENTO_DEMO)
    ap.add_argument("--seed", type=int, default=SEED_DEMO)
    args = ap.parse_args(argv)

    if not EMPRESAS.exists():
        print(f"falta {EMPRESAS.relative_to(RAIZ)} — es un entregable de R1 (data/).")
        return 2

    reglas = ClienteReglas()
    cliente = reglas
    modo = "ABLACIÓN (reglas fijas, sin API)"
    if CACHE_DEMO.exists():
        n = Cache().importar(CACHE_DEMO)
        print(f"caché del escenario demo importada: {n} respuestas ya pagadas")
        try:
            from behavior.cliente import ClienteConductual

            # Tope 0 a propósito: este script NO puede gastar. Con credenciales
            # en el entorno, una llamada fuera de caché moriría en
            # `presupuesto.comprobar()` antes de salir a la red, y de ahí cae a
            # la regla fija igual que si no hubiera key.
            cliente = _ConCaida(
                ClienteConductual(presupuesto=Presupuesto(tope_usd=0.0)), reglas
            )
            modo = "LLM sobre caché versionada (nivel 2 de la ADR 0009)"
        except Exception as e:  # noqa: BLE001 - sin credenciales es el caso normal
            print(f"  no se pudo usar la capa LLM ({type(e).__name__}); se usa la ablación")
    else:
        print(f"no hay {CACHE_DEMO.relative_to(RAIZ)}: se reproduce con la ablación,")
        print("  que es determinista sin depender de nada externo (nivel 3 de la ADR 0009).")

    arquetipos = desde_empresas(EMPRESAS, MOMENTOS)
    tasa = informalidad_observada(MOMENTOS)
    print(f"\nmodo: {modo}")
    print(f"{len(arquetipos)} arquetipos de empresas.parquet · seed {args.seed} · "
          f"alza {args.aumento:g}%")
    print(f"informalidad observada (GEIH): {tasa:.1%}\n")

    rondas = correr(
        arquetipos,
        cliente,
        aumento_pct=args.aumento,
        seed=args.seed,
        tasa_informalidad_inicial=tasa,
    )

    print("ronda  informalidad  p.sanción   empleo   masa salarial")
    for r in rondas:
        print(f"{r.ronda:5d} {r.tasa_informalidad:12.1%} {r.prob_fiscalizacion:10.2%}"
              f" {r.empleo_relativo:8.1%} {r.ingreso_laboral_relativo:15.1%}")

    ultima, primera = rondas[-1], rondas[0]
    brecha = (ultima.tasa_informalidad - primera.tasa_informalidad) * 100
    sello = "ESTABILIZADA" if ultima.estabilizada else "NO ESTABILIZADA"
    print(f"\nbrecha contra la proyección oficial: {brecha:+.1f} pp")
    print(f"movimiento de la última ronda: {ultima.movimiento_pp:+.1f} pp · {sello} "
          f"(umbral {UMBRAL_ESTABILIDAD_PP:g} pp)")
    print(f"fallbacks: {ultima.fraccion_fallback:.1%} de las decisiones · "
          f"sin ninguna opción factible: {ultima.fraccion_sin_salida:.1%}")
    if isinstance(cliente, _ConCaida):
        print(f"\norigen de las decisiones: {cliente.aciertos} del modelo (caché ya "
              f"pagada) · {cliente.caidas} de la regla fija por no estar en caché")
        if cliente.caidas:
            print("  La caché no cubre esta corrida: se pagó antes de un cambio que entra")
            print("  al texto del prompt. La corrida sigue siendo determinista, pero esas")
            print("  decisiones NO son del modelo. Ver AGENTS.md, pendientes declarados.")
    print("\nPara verificar el determinismo: corre esto dos veces y compara.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
