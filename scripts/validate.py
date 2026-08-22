"""Ejecuta las compuertas y mediciones pre-registradas en VALIDATION.md.

No completa ni modifica el pre-registro. Un candado imposible de ejecutar se
reporta como BLOQUEADO y hace que el proceso termine con código distinto de 0.
"""

from __future__ import annotations

import json
import subprocess
import sys
from enum import Enum
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
DATA = RAIZ / "data"
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

DELTA_MODELO_PP = 33.3
RONDA_3_MODELO_PCT = 63.8
BANDA_MODELO_PCT = (47.9, 81.8)


class Estado(str, Enum):
    PASA = "PASA"
    FALLA = "FALLA"
    BLOQUEADO = "BLOQUEADO"


Resultado = tuple[Estado, str]


def _ejecutar(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args], cwd=RAIZ, capture_output=True, text=True, check=False
    )


def candado_g1() -> Resultado:
    """Determinismo punta a punta: seed + caché + versiones."""
    requisitos = RAIZ / "requirements.txt"
    if not requisitos.exists():
        return Estado.BLOQUEADO, "falta requirements.txt"
    texto = requisitos.read_text(encoding="utf-8").lower()
    if "anthropic==" not in texto:
        return Estado.BLOQUEADO, "anthropic no está instalado ni fijado; no hay entorno reconstruible"
    corredor = RAIZ / "scripts" / "run_simulacion.py"
    if not corredor.exists():
        return Estado.BLOQUEADO, "falta scripts/run_simulacion.py para comparar dos corridas completas"
    return Estado.BLOQUEADO, "falta un artefacto canónico de salida y manifiesto de caché para comparar"


def candado_g2() -> Resultado:
    """Higiene de prompts + corrida re-skinneada."""
    higiene = _ejecutar("-m", "behavior.higiene")
    if higiene.returncode != 0:
        detalle = (higiene.stdout + higiene.stderr).strip().splitlines()[-1]
        return Estado.FALLA, f"behavior.higiene salió {higiene.returncode}: {detalle}"
    if not (RAIZ / "behavior" / "reskin.py").exists():
        return Estado.BLOQUEADO, "higiene PASA (7/7); el re-skinning no está implementado"
    return Estado.BLOQUEADO, "existe reskin.py, pero falta una salida canónica comparable registrada"


def candado_g3() -> Resultado:
    """Corrida sin política contra proxy y orden micro > pyme > grande."""
    salida = DATA / "calibracion_base.json"
    if not salida.exists():
        return Estado.BLOQUEADO, "no existe data/calibracion_base.json de una corrida sin política"
    observado = json.loads((DATA / "momentos.json").read_text(encoding="utf-8"))
    calibrado = json.loads(salida.read_text(encoding="utf-8"))
    tasa = float(calibrado["tasa_informalidad_total"])
    objetivo = float(observado["tasa_informalidad_total"])
    tamanos = calibrado["tasa_informalidad_por_tamano"]
    orden = tamanos["micro"] > tamanos["pyme"] > tamanos["grande"]
    error_pp = abs(tasa - objetivo) * 100
    estado = Estado.PASA if error_pp <= 2.0 and orden else Estado.FALLA
    return estado, f"error={error_pp:.2f} pp; orden micro>pyme>grande={orden}"


def _tasa_periodo(anio: int, meses: list[str]) -> float:
    # Importación local: V0 solo intenta leer crudos cuando los seis meses están.
    from data.construir_poblacion import construir

    _, momentos = construir(anio, meses=meses)
    return float(momentos["tasa_informalidad_total"])


def medicion_v0() -> tuple[Estado, str, dict[str, float] | None]:
    requeridos = [DATA / "raw" / f"GEIH_2025_{mes}" / "CSV" for mes in (
        "enero", "febrero", "marzo", "abril", "mayo", "junio"
    )]
    faltantes = [p.parent.name for p in requeridos if not p.is_dir()]
    if faltantes:
        return Estado.BLOQUEADO, f"faltan crudos: {', '.join(faltantes)}", None

    momentos_2025 = DATA / "momentos_2025.json"
    if not momentos_2025.exists():
        return Estado.BLOQUEADO, "faltan data/momentos_2025.json y data/poblacion_2025.parquet", None

    pre_ene_jun = float(json.loads(momentos_2025.read_text(encoding="utf-8"))["tasa_informalidad_total"])
    post_ene_jun = float(json.loads((DATA / "momentos.json").read_text(encoding="utf-8"))["tasa_informalidad_total"])
    pre_abr_jun = _tasa_periodo(2025, ["abril", "mayo", "junio"])
    post_abr_jun = _tasa_periodo(2026, ["abril", "mayo", "junio"])

    delta = (post_ene_jun - pre_ene_jun) * 100
    error_firmado = DELTA_MODELO_PP - delta
    error_modelo = abs(error_firmado)
    error_baseline = abs(delta)
    skill = 1.0 - error_modelo / error_baseline if error_baseline else float("-inf")
    numeros = {
        "pre_ene_jun_pct": pre_ene_jun * 100,
        "post_ene_jun_pct": post_ene_jun * 100,
        "delta_ene_jun_pp": delta,
        "pre_abr_jun_pct": pre_abr_jun * 100,
        "post_abr_jun_pct": post_abr_jun * 100,
        "delta_abr_jun_pp": (post_abr_jun - pre_abr_jun) * 100,
        "error_firmado_pp": error_firmado,
        "error_absoluto_pp": error_modelo,
        "error_baseline_pp": error_baseline,
        "skill_b1": skill,
        "cobertura": float(BANDA_MODELO_PCT[0] <= post_ene_jun * 100 <= BANDA_MODELO_PCT[1]),
        "ancho_banda_pp": BANDA_MODELO_PCT[1] - BANDA_MODELO_PCT[0],
    }
    return Estado.PASA, "V0 computado proxy contra proxy", numeros


def medicion_m3() -> Resultado:
    try:
        from behavior.ablacion import barrer_factor

        filas = barrer_factor(real=True)
    except Exception as exc:  # pragma: no cover - evidencia operativa en CLI
        return Estado.BLOQUEADO, f"la ablación no pudo correr: {type(exc).__name__}: {exc}"
    hay_cascada = [factor for factor, tasa, _ in filas if tasa > 0.01]
    sin_cascada = [factor for factor, tasa, _ in filas if tasa <= 0.01]
    return Estado.PASA, f"8 factores; cascada={hay_cascada}; sin cascada={sin_cascada}"


def _imprimir_v0(n: dict[str, float]) -> None:
    skill = n["skill_b1"]
    skill_txt = "-inf" if skill == float("-inf") else f"{skill:.3f}"
    print("\nEL NÚMERO · V0")
    print(f"  Error del backtest:          {n['error_absoluto_pp']:.2f} pp (firmado modelo-observado: {n['error_firmado_pp']:+.2f} pp)")
    print(f"  Skill vs persistencia (B1):  {skill_txt}")
    print(f"  Cobertura de la banda:       {'sí' if n['cobertura'] else 'no'}")
    print(f"  Ancho de la banda:           {n['ancho_banda_pp']:.1f} pp")
    print("  Corridas:                    BLOQUEADO: el repo no registra N>=5 trayectorias comparables")
    print(f"  Proxy 2025 ene-jun:          {n['pre_ene_jun_pct']:.2f}%")
    print(f"  Proxy 2026 ene-jun:          {n['post_ene_jun_pct']:.2f}%")
    print(f"  Delta observado:             {n['delta_ene_jun_pp']:+.2f} pp")


def main() -> int:
    resultados = [("G1 reproducibilidad", candado_g1()), ("G2 no contaminación", candado_g2()), ("G3 calibración base", candado_g3())]
    estado_v0, detalle_v0, numeros = medicion_v0()
    resultados.extend([("M1/M2 backtest y habilidad", (estado_v0, detalle_v0)), ("M3 ablación", medicion_m3())])

    print("VALIDACIÓN PRE-REGISTRADA")
    for nombre, (estado, detalle) in resultados:
        print(f"  [{estado.value:9}] {nombre}: {detalle}")
    if numeros is None:
        print("\nEL NÚMERO · BLOQUEADO")
        print(f"  {detalle_v0}")
    else:
        _imprimir_v0(numeros)

    return 0 if all(estado is Estado.PASA for _, (estado, _) in resultados) else 1


if __name__ == "__main__":
    raise SystemExit(main())
