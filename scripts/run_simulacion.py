#!/usr/bin/env python3
"""Una corrida completa del simulador, con artefacto canónico y manifiesto de caché.

    python scripts/run_simulacion.py --seed 42
    make run

Es el comando que `README.md` y `AGENTS.md` publican como entrada principal, y el que
sostiene el claim de determinismo del proyecto: **"mismo seed, mismo resultado,
verificable corriendo `make run` dos veces"**. Hasta hoy ese archivo no existía y el
target imprimía `PENDIENTE` saliendo con código 0, así que la promesa no era
comprobable por nadie —ni por el equipo.

## Qué emite, y por qué así

Un **artefacto canónico** en `scripts/salidas/` que **no lleva fecha ni ninguna otra cosa
que cambie entre dos corridas idénticas**. Esa omisión es deliberada y es el punto entero
del archivo: si el artefacto llevara timestamp, dos corridas con el mismo seed producirían
archivos distintos y el determinismo dejaría de ser verificable comparando bytes. La fecha
va por pantalla, no al disco.

Junto al resultado va el **par que identifica la corrida**: `(seed, manifiesto de caché)`.
Es el nivel 2 de la [ADR 0009](../docs/adr/0009-frontera-del-determinismo.md) — *mismo seed
+ misma caché + mismas versiones = mismo resultado*—: dos corridas se reconocen comparables
porque imprimen el mismo par, y el manifiesto cubre el contenido de la caché, no los nombres
de archivo, así que editar una entrada a mano se nota.

## Los dos modos

- `--modo reglas` (por defecto): la ablación determinista. **No necesita API key, cuesta
  USD 0,00** y es la que corre un tercero que acaba de clonar. Es el nivel 3 de la ADR 0009.
- `--modo llm`: la capa conductual real. Usa `behavior/cache-demo.json` si cubre las
  llamadas; si falta la credencial **falla ruidosamente** en vez de caer a reglas en
  silencio, porque una corrida que dice "LLM" y corrió con reglas fijas es un resultado
  falso que nadie detecta.

Verificar el determinismo, que es para lo que existe:

    make run && make run       # el segundo dice "IDÉNTICO al anterior"
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from behavior.ablacion import ClienteReglas  # noqa: E402
from behavior.arquetipos import desde_empresas, informalidad_observada  # noqa: E402
from behavior.cache import Cache  # noqa: E402
from behavior.rondas import correr  # noqa: E402

CACHE_DEMO = RAIZ / "behavior" / "cache-demo.json"
EMPRESAS = RAIZ / "data" / "empresas.parquet"
MOMENTOS = RAIZ / "data" / "momentos.json"
SALIDAS = RAIZ / "scripts" / "salidas"

AUMENTO_DEMO = 23.0
SEED_DEMO = 42

# Las que deciden el resultado numérico. Van en el artefacto porque el nivel 2 de la
# ADR 0009 dice "mismas versiones": un cambio de numpy puede mover el último decimal, y
# entonces dos corridas legítimamente distintas se verían como un fallo de determinismo.
DEPENDENCIAS = ("numpy", "pandas", "pyarrow", "anthropic")


def _versiones() -> dict[str, str]:
    from importlib.metadata import PackageNotFoundError, version

    salida = {}
    for paquete in DEPENDENCIAS:
        try:
            salida[paquete] = version(paquete)
        except PackageNotFoundError:
            salida[paquete] = "ausente"
    return salida


def _cliente(modo: str) -> tuple[object, str, str]:
    """Devuelve (cliente, etiqueta, manifiesto de caché)."""
    if modo == "reglas":
        return ClienteReglas(), "ablacion-reglas-fijas", "sin-cache"

    if not CACHE_DEMO.exists():
        raise SystemExit(
            f"--modo llm necesita {CACHE_DEMO.relative_to(RAIZ)}, que no está en el repo.\n"
            "Corre con --modo reglas, que es determinista y no depende de nada externo."
        )
    cache = Cache()
    n = cache.importar(CACHE_DEMO)
    print(f"caché del escenario demo importada: {n} respuestas ya pagadas")
    try:
        from behavior.cliente import ClienteConductual

        cliente = ClienteConductual()
    except Exception as e:  # noqa: BLE001
        # A propósito NO se cae a reglas. Ver el docstring: un resultado rotulado "llm"
        # que salió de reglas fijas es indistinguible del bueno y contamina el registro.
        raise SystemExit(
            f"--modo llm no pudo inicializar la capa conductual ({type(e).__name__}: {e}).\n"
            "Si no tienes ANTHROPIC_API_KEY, corre con --modo reglas."
        ) from e
    return cliente, "llm-sobre-cache-versionada", cache.manifiesto()


def _artefacto(rondas, arquetipos, args, etiqueta: str, manifiesto: str, tasa: float) -> dict:
    """El artefacto canónico. Sin fecha: ver el docstring del módulo."""
    return {
        "que_es": (
            "Corrida canónica del simulador. NO lleva fecha a propósito: dos corridas con "
            "el mismo (seed, manifiesto, versiones) deben producir este archivo byte a byte "
            "idéntico, y un timestamp lo haría imposible de comparar."
        ),
        "identidad": {
            "seed": args.seed,
            "manifiesto_cache": manifiesto,
            "versiones": _versiones(),
            "modo": etiqueta,
        },
        "politica": {"tipo": "cambio_costo_laboral", "aumento_pct": args.aumento},
        "poblacion": {
            "fuente": "data/empresas.parquet (empleadores GEIH Bogotá 2026)",
            "n_arquetipos": len(arquetipos),
            "peso_total": round(sum(a.peso for a in arquetipos), 6),
            "informalidad_observada": round(tasa, 6),
            "universo": "ocupados con empleador; excluye cuenta propia",
        },
        "rondas": [
            {
                "ronda": r.ronda,
                "tasa_informalidad": round(r.tasa_informalidad, 10),
                "prob_fiscalizacion": round(r.prob_fiscalizacion, 10),
                "empleo_relativo": round(r.empleo_relativo, 10),
                "ingreso_laboral_relativo": round(r.ingreso_laboral_relativo, 10),
                "movimiento_pp": round(r.movimiento_pp, 10),
                "estabilizada": bool(r.estabilizada),
            }
            for r in rondas
        ],
        "brecha_pp": round(
            (rondas[-1].tasa_informalidad - rondas[0].tasa_informalidad) * 100, 10
        ),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Una corrida completa, con artefacto canónico.")
    ap.add_argument("--seed", type=int, default=SEED_DEMO)
    ap.add_argument("--aumento", type=float, default=AUMENTO_DEMO)
    ap.add_argument("--modo", choices=("reglas", "llm"), default="reglas")
    ap.add_argument("--cobertura", type=float, default=None,
                    help="top-K: fracción de población que va al LLM (solo --modo llm)")
    ap.add_argument("--salida", type=Path, default=None)
    args = ap.parse_args(argv)

    if not EMPRESAS.exists():
        print(f"falta {EMPRESAS.relative_to(RAIZ)} — es un entregable de R1 (data/).")
        return 2

    cliente, etiqueta, manifiesto = _cliente(args.modo)
    arquetipos = desde_empresas(EMPRESAS, MOMENTOS)
    tasa = informalidad_observada(MOMENTOS)

    print(f"\nmodo: {etiqueta}")
    print(f"{len(arquetipos)} arquetipos · alza {args.aumento:g}% · "
          f"informalidad observada (GEIH): {tasa:.2%}")
    print(f"IDENTIDAD DE LA CORRIDA  seed={args.seed}  manifiesto={manifiesto}")
    print("  (dos corridas son comparables si imprimen este mismo par — ADR 0009)")
    # Se dice acá y no solo en un comentario: quien mueva la perilla y no vea nada
    # cambiar merece saber por qué antes de concluir que el motor está roto.
    print("  OJO: hoy el seed es una ETIQUETA, no una perilla (api/servidor.py:80).")
    print("  Medido: --seed 42 y --seed 99 dan rondas idénticas; solo cambia este rótulo.")
    print("  Cambiará el día que el seed elija las paráfrasis de la banda.\n")

    rondas = correr(
        arquetipos,
        cliente,
        aumento_pct=args.aumento,
        seed=args.seed,
        tasa_informalidad_inicial=tasa,
        cobertura_llm=args.cobertura,
    )

    print("ronda  informalidad  p.sanción   empleo   masa salarial")
    for r in rondas:
        print(f"{r.ronda:5d} {r.tasa_informalidad:12.2%} {r.prob_fiscalizacion:10.2%}"
              f" {r.empleo_relativo:8.1%} {r.ingreso_laboral_relativo:15.1%}")

    brecha = (rondas[-1].tasa_informalidad - rondas[0].tasa_informalidad) * 100
    print(f"\nbrecha ronda 0 → ronda {rondas[-1].ronda}: {brecha:+.2f} pp")

    artefacto = _artefacto(rondas, arquetipos, args, etiqueta, manifiesto, tasa)
    texto = json.dumps(artefacto, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    sha = hashlib.sha256(texto.encode("utf-8")).hexdigest()[:16]

    destino = args.salida or (
        SALIDAS / f"corrida-{args.modo}-{args.aumento:g}-{args.seed}.json"
    )
    destino.parent.mkdir(parents=True, exist_ok=True)
    ya_estaba = destino.exists() and destino.read_text(encoding="utf-8") == texto
    destino.write_text(texto, encoding="utf-8")

    print(f"\nartefacto canónico: {destino.relative_to(RAIZ)}")
    print(f"sha256[:16] del artefacto: {sha}")
    if ya_estaba:
        print("DETERMINISMO: IDÉNTICO al anterior — el artefacto no cambió un byte.")
    else:
        print("primera corrida con esta configuración (o el resultado cambió).")
        print("Corre el comando otra vez: debe decir IDÉNTICO.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
