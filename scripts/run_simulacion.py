#!/usr/bin/env python3
"""Una corrida completa punta a punta, determinista y sin API key.

    python3 scripts/run_simulacion.py --seed 42

Qué hace: instancia los arquetipos desde `data/empresas.parquet`, corre las
rondas de mejor respuesta con el cliente de reglas fijas (`behavior.ablacion`) y
escribe DOS archivos:

  * el **artefacto canónico** (`artefactos/corrida.json`): la corrida entera,
    serializada con claves ordenadas y sin nada que dependa del reloj ni de la
    ruta desde la que se invocó;
  * el **manifiesto** (`artefactos/corrida.manifiesto.json`): con qué se produjo
    —seed, versiones de las dependencias que entran al cálculo, qué caché se
    usó— y el SHA-256 del artefacto.

Por qué existe. `AGENTS.md` promete *"mismo seed, mismo resultado, verificable
corriendo `make run` dos veces"*, y hasta hoy `make run` imprimía `PENDIENTE`:
la frase era una promesa sin ejecutor. La compuerta **G1** de `VALIDATION.md`
—*"dos corridas con el mismo (seed, manifiesto de caché, versiones) dan salida
idéntica"*— también estaba bloqueada por este archivo, por su nombre, desde
`scripts/validate.py`.

Cuesta $0 y no toca la red. Corre el **nivel 3 de la ADR 0009**
(`docs/adr/0009-frontera-del-determinismo.md`): la ablación con reglas fijas,
que es determinista por construcción y no depende de credenciales ni de una
caché comprada. El nivel 2 (caché versionada del escenario demo) es lo que
reproduce `scripts/reproduce.py`; los dos conviven a propósito y no son
intercambiables:

    reproduce.py       -> reproduce EL RESULTADO PUBLICADO (intenta la caché del LLM)
    run_simulacion.py  -> demuestra EL DETERMINISMO DEL MOTOR (nunca sale a la red)

Si este script llamara al proveedor de LLM, `make run` dejaría de ser gratis y
dejaría de correr en la máquina de un jurado sin credenciales, que son las dos
razones por las que existe.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from pathlib import Path
from typing import Any

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from behavior.ablacion import ClienteReglas  # noqa: E402
from behavior.arquetipos import (  # noqa: E402
    Arquetipo,
    desde_empresas,
    informalidad_observada,
)
from behavior.rondas import UMBRAL_ESTABILIDAD_PP, Ronda, correr  # noqa: E402

EMPRESAS = RAIZ / "data" / "empresas.parquet"
MOMENTOS = RAIZ / "data" / "momentos.json"
ARTEFACTOS = RAIZ / "artefactos"

# El escenario demo: el alza del 23% de `docs/PLAN.md`. Se cambia por CLI.
AUMENTO_DEMO = 23.0
SEED_DEMO = 42
RONDAS_DEMO = 4

ESQUEMA = "corrida-canonica/v1"

# SUPUESTO: los flotantes se redondean a 12 decimales antes de serializar.
# Fuente: ninguna — es una decisión de SERIALIZACIÓN, no un dato del modelo. El
# motor es determinista bit a bit en una misma máquina, pero el orden de suma
# bajo `ThreadPoolExecutor` puede mover el último ulp entre plataformas, y un
# candado que se cae por el dígito 17 no mide reproducibilidad, mide ruido de
# coma flotante. 12 decimales dejan intacta cualquier cifra que el proyecto
# publique (la más fina se publica con 4).
DECIMALES_CANONICOS = 12


def _canonizar(valor: Any) -> Any:
    """Redondea flotantes y ordena claves, recursivamente.

    `bool` se atrapa ANTES que `float` a propósito: en Python `isinstance(True,
    float)` es `False` pero `isinstance(True, int)` es `True`, y basta con que
    alguien agregue una rama para `int` para que `estabilizada` se vuelva `1`.
    """
    if isinstance(valor, bool):
        return valor
    if isinstance(valor, float):
        return round(valor, DECIMALES_CANONICOS)
    if isinstance(valor, dict):
        return {k: _canonizar(valor[k]) for k in sorted(valor, key=str)}
    if isinstance(valor, (list, tuple)):
        return [_canonizar(v) for v in valor]
    return valor


def _volcar(obj: Any) -> str:
    """El texto canónico: claves ordenadas, UTF-8 literal, salto de línea final."""
    return json.dumps(
        _canonizar(obj), ensure_ascii=False, indent=2, sort_keys=True
    ) + "\n"


def _por_tamano(ronda: Ronda, arquetipos: list[Arquetipo]) -> dict[str, float]:
    """Informalidad al cierre de la ronda, desagregada por tamaño de firma.

    Usa la MISMA ponderación con la que `behavior/rondas.py` construye la tasa
    publicada: `peso` (suma de factores de expansión) por
    `estado_por_arquetipo[id]["fraccion_informal"]`. No es un recálculo
    alternativo — es el mismo numerador partido en tres denominadores, que es lo
    que pide el orden `micro > pyme > grande` de la compuerta G3.
    """
    tamanos: dict[str, list[float]] = {}
    for a in arquetipos:
        estado = ronda.estado_por_arquetipo.get(a.id)
        if estado is None:
            continue
        peso = ronda.pesos.get(a.id, a.peso)
        acum = tamanos.setdefault(a.tamano, [0.0, 0.0])
        acum[0] += peso * float(estado["fraccion_informal"])
        acum[1] += peso
    return {
        tamano: (num / den if den else 0.0)
        for tamano, (num, den) in sorted(tamanos.items())
    }


def _versiones() -> dict[str, str]:
    """Lo que entra al cálculo. Sin esto el manifiesto no dice nada.

    `anthropic` va aunque este script NO lo use: el manifiesto describe el
    entorno con el que se comparan dos corridas, y G1 nombra las versiones como
    parte de la llave. Si el paquete falta se declara `ausente` en vez de
    romper — la ablación corre igual sin él, y ese es justamente el punto.
    """
    versiones = {
        "python": platform.python_version(),
        "implementacion": platform.python_implementation(),
    }
    for modulo in ("numpy", "pandas", "pyarrow", "anthropic"):
        try:
            versiones[modulo] = __import__(modulo).__version__
        except Exception:  # noqa: BLE001 - ausente es un estado legítimo
            versiones[modulo] = "ausente"
    return versiones


def _artefacto(
    rondas: list[Ronda],
    arquetipos: list[Arquetipo],
    *,
    aumento: float,
    seed: int,
    rondas_totales: int,
    tasa_inicial: float,
) -> dict[str, Any]:
    ultima, primera = rondas[-1], rondas[0]
    return {
        "esquema": ESQUEMA,
        "escenario": {
            "aumento_pct": aumento,
            "seed": seed,
            "rondas_pedidas": rondas_totales,
            "modo": "ablacion-determinista",
            "nivel_adr_0009": 3,
            "llamadas_al_proveedor_llm": 0,
            "costo_usd": 0.0,
        },
        "entradas": {
            "arquetipos": len(arquetipos),
            "peso_total": sum(a.peso for a in arquetipos),
            "firmas": sum(a.n_empresas for a in arquetipos),
            "tasa_informalidad_inicial": tasa_inicial,
            # Cuál de las dos tasas de `momentos.json` es ésta. El repo ya se
            # tropezó una vez con los dos denominadores (30,57% de todos los
            # ocupados contra 17,99% de empleados de firma); el artefacto lo
            # dice en vez de dejarlo a la memoria de quien lo lea.
            "universo": "empleados_de_firma",
            "fuente_momentos": "data/momentos.json",
            "fuente_poblacion": "data/empresas.parquet",
        },
        "rondas": [
            dict(
                r.a_contrato(),
                fraccion_fallback=r.fraccion_fallback,
                fraccion_fallback_ponderada=r.fraccion_fallback_ponderada,
                fraccion_sin_salida=r.fraccion_sin_salida,
                fraccion_sin_salida_ponderada=r.fraccion_sin_salida_ponderada,
                prob_fiscalizacion_evasores=r.prob_fiscalizacion_evasores,
                fraccion_jornada_recortada=r.fraccion_jornada_recortada,
                desglose_estrategias=r.desglose_estrategias(),
                tasa_informalidad_por_tamano=_por_tamano(r, arquetipos),
            )
            for r in rondas
        ],
        "final": {
            "tasa_informalidad": ultima.tasa_informalidad,
            "tasa_informalidad_por_tamano": _por_tamano(ultima, arquetipos),
            "brecha_pp": (ultima.tasa_informalidad - primera.tasa_informalidad) * 100,
            "movimiento_ultima_ronda_pp": ultima.movimiento_pp,
            "estabilizada": ultima.estabilizada,
            "umbral_estabilidad_pp": UMBRAL_ESTABILIDAD_PP,
            "empleo_relativo": ultima.empleo_relativo,
            "ingreso_laboral_relativo": ultima.ingreso_laboral_relativo,
        },
    }


def _manifiesto(texto_artefacto: str, *, seed: int, aumento: float) -> dict[str, Any]:
    return {
        "esquema": "manifiesto-corrida/v1",
        "seed": seed,
        "aumento_pct": aumento,
        # El manifiesto de CACHÉ que nombra G1. En este camino la respuesta es
        # "ninguna", y eso no es una omisión: la ablación no consulta caché
        # porque no consulta al proveedor. Un manifiesto vacío y un manifiesto
        # que dice "no se usó caché" son cosas distintas.
        "cache": {
            "usada": False,
            "motivo": "ablacion determinista: no hay llamadas que cachear",
            "archivo": None,
            "aciertos": 0,
            "fallos": 0,
        },
        "versiones": _versiones(),
        "sha256_artefacto": hashlib.sha256(texto_artefacto.encode("utf-8")).hexdigest(),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Corre una simulación completa por la ablación determinista.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="El determinismo se verifica corriendo esto dos veces y comparando "
               "el SHA-256 que imprime al final.",
    )
    ap.add_argument("--seed", type=int, default=SEED_DEMO,
                    help=f"semilla del motor (default {SEED_DEMO})")
    ap.add_argument("--aumento", type=float, default=AUMENTO_DEMO,
                    help=f"alza del costo laboral en %% (default {AUMENTO_DEMO:g}); "
                         "0 produce la corrida SIN política que pide G3")
    ap.add_argument("--rondas", type=int, default=RONDAS_DEMO,
                    help=f"rondas de mejor respuesta (default {RONDAS_DEMO})")
    ap.add_argument("--salida", type=Path, default=None,
                    help="artefacto canónico (default artefactos/corrida.json, o "
                         "artefactos/calibracion_base.json con --aumento 0)")
    ap.add_argument("--manifiesto", type=Path, default=None,
                    help="manifiesto (default: el nombre de --salida con sufijo "
                         "'.manifiesto.json')")
    ap.add_argument("--sin-artefacto", action="store_true",
                    help="no escribe archivos; solo imprime el sha256")
    ap.add_argument("--solo-hash", action="store_true",
                    help="imprime UNA línea con el sha256 y nada más; no escribe "
                         "archivos. Es la forma en que la compuerta G1 de "
                         "scripts/validate.py compara dos corridas")
    args = ap.parse_args(argv)

    if not EMPRESAS.exists():
        # A stderr: con `--solo-hash` la stdout es UNA línea que un candado
        # parsea, y un error mezclado ahí lo haría leer un hash que no existe.
        print(f"falta {EMPRESAS.relative_to(RAIZ)} — es un entregable de R1 (data/).",
              file=sys.stderr)
        return 2

    def out(*a: Any, **k: Any) -> None:
        """La narración. `--solo-hash` la calla entera y deja la stdout limpia."""
        if not args.solo_hash:
            print(*a, **k)

    sin_politica = args.aumento == 0.0
    salida = args.salida or ARTEFACTOS / (
        "calibracion_base.json" if sin_politica else "corrida.json"
    )
    manifiesto_ruta = args.manifiesto or salida.with_suffix(".manifiesto.json")

    arquetipos = desde_empresas(EMPRESAS, MOMENTOS)
    tasa = informalidad_observada(MOMENTOS)

    out("CORRIDA · ablación determinista (sin API key, sin red, $0)")
    out(f"  seed {args.seed} · alza {args.aumento:g}% · {args.rondas} rondas")
    out(f"  {len(arquetipos)} arquetipos desde data/empresas.parquet")
    out(f"  informalidad observada (empleados de firma, GEIH): {tasa:.2%}")
    if sin_politica:
        out("  alza 0%: es la corrida SIN política que pide la compuerta G3")
    out()

    rondas = correr(
        arquetipos,
        ClienteReglas(),
        aumento_pct=args.aumento,
        seed=args.seed,
        rondas_totales=args.rondas,
        tasa_informalidad_inicial=tasa,
    )

    out("ronda  informalidad  p.sanción  p.sanc.evasores   empleo  masa salarial")
    for r in rondas:
        out(f"{r.ronda:5d} {r.tasa_informalidad:12.2%} {r.prob_fiscalizacion:10.2%}"
              f" {r.prob_fiscalizacion_evasores:16.2%} {r.empleo_relativo:8.2%}"
              f" {r.ingreso_laboral_relativo:14.2%}")

    ultima, primera = rondas[-1], rondas[0]
    brecha = (ultima.tasa_informalidad - primera.tasa_informalidad) * 100
    sello = "ESTABILIZADA" if ultima.estabilizada else "NO ESTABILIZADA"
    out(f"\nbrecha contra la proyección oficial: {brecha:+.2f} pp")
    out(f"movimiento de la última ronda: {ultima.movimiento_pp:+.2f} pp · {sello} "
          f"(umbral {UMBRAL_ESTABILIDAD_PP:g} pp)")
    out("informalidad final por tamaño de firma: " + " · ".join(
        f"{k} {v:.2%}" for k, v in _por_tamano(ultima, arquetipos).items()
    ))
    out(f"fallbacks: {ultima.fraccion_fallback_ponderada:.2%} de la población "
          f"· sin ninguna opción factible: {ultima.fraccion_sin_salida_ponderada:.2%}")

    artefacto = _artefacto(
        rondas, arquetipos,
        aumento=args.aumento, seed=args.seed,
        rondas_totales=args.rondas, tasa_inicial=tasa,
    )
    if sin_politica:
        # Las llaves que `scripts/validate.py::candado_g3` lee por nombre. Van
        # ADEMÁS del bloque `final`, no en su lugar.
        artefacto["tasa_informalidad_total"] = ultima.tasa_informalidad
        artefacto["tasa_informalidad_por_tamano"] = _por_tamano(ultima, arquetipos)
        artefacto["universo"] = "empleados_de_firma"

    texto = _volcar(artefacto)
    manifiesto = _manifiesto(texto, seed=args.seed, aumento=args.aumento)

    if args.solo_hash:
        print(manifiesto["sha256_artefacto"])
        return 0

    if args.sin_artefacto:
        out(f"\nsha256 del artefacto: {manifiesto['sha256_artefacto']}")
        out("(--sin-artefacto: no se escribió nada en disco)")
        return 0

    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(texto, encoding="utf-8")
    manifiesto_ruta.parent.mkdir(parents=True, exist_ok=True)
    manifiesto_ruta.write_text(_volcar(manifiesto), encoding="utf-8")

    out(f"\nartefacto canónico: {salida.relative_to(RAIZ)}")
    out(f"manifiesto:         {manifiesto_ruta.relative_to(RAIZ)}")
    out(f"sha256:             {manifiesto['sha256_artefacto']}")
    out("\nDeterminismo: corre esto dos veces y compara el sha256.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
