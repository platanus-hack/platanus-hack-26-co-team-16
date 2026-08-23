#!/usr/bin/env python3
"""Genera las figuras del laboratorio a partir del histórico de corridas.

Qué modela: nada. Lee `web/laboratorio/historico.jsonl` —una línea por corrida
  terminada, escrita por la interfaz— y dibuja tres SVG.
Entradas: `web/laboratorio/historico.jsonl`.
Salidas: `web/laboratorio/figuras/*.svg`.
Supuestos: ninguno. Todos los números salen del contrato que ya viajó por el
  flujo SSE; acá solo se proyectan a coordenadas.

Por qué SOLO biblioteca estándar
--------------------------------
`AGENTS.md` congela dependencias nuevas en el feature freeze, y el proyecto no
tiene matplotlib ni ninguna librería de gráficas (`requirements.txt`: numpy,
pandas, pyarrow, requests, anthropic, pytest, fastapi, uvicorn). Un SVG es
texto, así que escribirlo a mano no necesita ninguna: esto corre en un clon
limpio sin instalar nada.

Por qué vive en `web/scripts/` y no en `scripts/`
-------------------------------------------------
`scripts/` es de R5 y `api/` de R2. El histórico y sus figuras son artefactos
de la interfaz, así que viven enteros bajo `web/`, que es la carpeta de R4. No
cruza carpetas de otros dueños.

Uso:
    python3 web/scripts/graficas_laboratorio.py
    python3 web/scripts/graficas_laboratorio.py --historico ruta.jsonl --salida dir/
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

RAIZ = Path(__file__).resolve().parent.parent  # web/
ANCHO, ALTO = 720, 360
MARGEN = {"l": 74, "r": 26, "t": 26, "b": 54}

FONDO = "#06080c"
TINTA = "#e9ecf2"
TENUE = "#5d6675"
LINEA = "rgba(233,236,242,0.14)"
COLOR_MODO = {"llm": "#79b1ff", "reglas": "#e8a33d"}


def leer(ruta: Path) -> list[dict[str, Any]]:
    """Lee el JSONL. Una línea corrupta se salta, no tumba el informe."""
    if not ruta.exists():
        return []
    filas: list[dict[str, Any]] = []
    for n, linea in enumerate(ruta.read_text(encoding="utf-8").splitlines(), 1):
        linea = linea.strip()
        if not linea:
            continue
        try:
            filas.append(json.loads(linea))
        except json.JSONDecodeError:
            print(f"  aviso: línea {n} ilegible, se salta")
    return filas


def _escala(vmin: float, vmax: float, desde: float, hasta: float):
    rango = (vmax - vmin) or 1.0
    return lambda v: desde + (v - vmin) / rango * (hasta - desde)


def _marco(titulo: str, eje_x: str, eje_y: str, cuerpo: str) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{ANCHO}" height="{ALTO}" \
viewBox="0 0 {ANCHO} {ALTO}" font-family="ui-monospace, monospace">
  <rect width="{ANCHO}" height="{ALTO}" fill="{FONDO}"/>
  <text x="{MARGEN['l']}" y="18" fill="{TENUE}" font-size="11" letter-spacing="1.8">{titulo}</text>
{cuerpo}
  <text x="{MARGEN['l'] + (ANCHO - MARGEN['l'] - MARGEN['r']) / 2:.0f}" y="{ALTO - 14}" \
text-anchor="middle" fill="{TENUE}" font-size="10">{eje_x}</text>
  <text x="{-(MARGEN['t'] + (ALTO - MARGEN['t'] - MARGEN['b']) / 2):.0f}" y="16" \
transform="rotate(-90)" text-anchor="middle" fill="{TENUE}" font-size="10">{eje_y}</text>
</svg>
"""


def _rejilla(vals: list[float], y, fmt) -> str:
    lo, hi = min(vals), max(vals)
    piezas = []
    for v in (hi, (hi + lo) / 2, lo):
        yy = y(v)
        piezas.append(
            f'  <line x1="{MARGEN["l"]}" y1="{yy:.1f}" x2="{ANCHO - MARGEN["r"]}" '
            f'y2="{yy:.1f}" stroke="{LINEA}"/>\n'
            f'  <text x="{MARGEN["l"] - 8}" y="{yy + 3:.1f}" text-anchor="end" '
            f'fill="{TENUE}" font-size="10">{fmt(v)}</text>'
        )
    return "\n".join(piezas)


def barrido(corridas: list[dict[str, Any]]) -> str | None:
    """Informalidad final contra el alza simulada: un punto por corrida."""
    if not corridas:
        return None
    xs = [c["aumento_pct"] for c in corridas]
    ys = [c["informalidad_final"] for c in corridas]
    x = _escala(min(xs), max(xs), MARGEN["l"], ANCHO - MARGEN["r"])
    y = _escala(min(ys), max(ys), ALTO - MARGEN["b"], MARGEN["t"])
    cuerpo = [_rejilla(ys, y, lambda v: f"{v * 100:.1f}%".replace(".", ","))]
    for c in corridas:
        color = COLOR_MODO.get(c.get("modo", ""), TENUE)
        cuerpo.append(
            f'  <circle cx="{x(c["aumento_pct"]):.1f}" cy="{y(c["informalidad_final"]):.1f}" '
            f'r="5" fill="{color}" opacity="0.85"/>'
        )
    for v in (min(xs), max(xs)):
        anchor = "start" if v == min(xs) else "end"
        cuerpo.append(
            f'  <text x="{x(v):.1f}" y="{ALTO - MARGEN["b"] + 16}" text-anchor="{anchor}" '
            f'fill="{TENUE}" font-size="10">{v:.1f}%</text>'
        )
    return _marco(
        f"INFORMALIDAD FINAL VS ALZA · {len(corridas)} corridas",
        "% de alza del salario mínimo",
        "informalidad final",
        "\n".join(cuerpo),
    )


def _serie_por_ronda(corridas, campo, titulo, eje_y, fmt) -> str | None:
    puntos = [(r["ronda"], r[campo]) for c in corridas for r in c["rondas"]]
    if not puntos:
        return None
    xs = [p[0] for p in puntos]
    ys = [p[1] for p in puntos]
    x = _escala(min(xs), max(xs), MARGEN["l"], ANCHO - MARGEN["r"])
    y = _escala(min(ys), max(ys), ALTO - MARGEN["b"], MARGEN["t"])
    cuerpo = [_rejilla(ys, y, fmt)]
    for c in corridas:
        color = COLOR_MODO.get(c.get("modo", ""), TENUE)
        pts = " ".join(f'{x(r["ronda"]):.1f},{y(r[campo]):.1f}' for r in c["rondas"])
        cuerpo.append(
            f'  <polyline points="{pts}" fill="none" stroke="{color}" '
            f'stroke-width="1.6" opacity="0.55"/>'
        )
    for v in sorted(set(xs)):
        cuerpo.append(
            f'  <text x="{x(v):.1f}" y="{ALTO - MARGEN["b"] + 16}" text-anchor="middle" '
            f'fill="{TENUE}" font-size="10">{int(v)}</text>'
        )
    return _marco(titulo, "ronda", eje_y, "\n".join(cuerpo))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--historico", type=Path, default=RAIZ / "laboratorio" / "historico.jsonl")
    ap.add_argument("--salida", type=Path, default=RAIZ / "laboratorio" / "figuras")
    args = ap.parse_args()

    corridas = leer(args.historico)
    if not corridas:
        print(f"histórico vacío o inexistente: {args.historico}")
        print("corre una simulación completa en la interfaz y vuelve a intentar.")
        return 0

    args.salida.mkdir(parents=True, exist_ok=True)
    figuras = {
        "barrido-politica.svg": barrido(corridas),
        "cascada-por-ronda.svg": _serie_por_ronda(
            corridas,
            "prob_fiscalizacion",
            "PROBABILIDAD DE SANCIÓN POR RONDA · el mecanismo de la cascada",
            "p(sanción) por trimestre",
            lambda v: f"{v * 100:.2f}%".replace(".", ","),
        ),
        "vetos-por-ronda.svg": _serie_por_ronda(
            corridas,
            "vetadas",
            "PROPUESTAS VETADAS POR RONDA · el veto de factibilidad no es decorativo",
            "propuestas rechazadas",
            lambda v: f"{v:.0f}",
        ),
    }

    escritas = 0
    for nombre, svg in figuras.items():
        if svg is None:
            continue
        (args.salida / nombre).write_text(svg, encoding="utf-8")
        print(f"  escrita {args.salida / nombre}")
        escritas += 1

    print(f"\n{escritas} figuras sobre {len(corridas)} corridas.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
