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

def _prediccion() -> dict:
    """La prediccion del modelo, desde el artefacto versionado.

    Estaba como tres constantes sueltas aqui adentro. Un numero magico en el
    validador es exactamente lo que el repo prohibe: nadie podia rastrear de
    que corrida salio ni notar si quedaba viejo.
    """
    ruta = DATA / "prediccion_modelo.json"
    if not ruta.exists():
        raise FileNotFoundError("falta data/prediccion_modelo.json")
    return json.loads(ruta.read_text(encoding="utf-8"))["resultado"]


class Estado(str, Enum):
    """PASA/FALLA/BLOQUEADO son de COMPUERTAS. MEDIDO es de MEDICIONES.

    `VALIDATION.md` define la medicion como "se publica el numero que salga, sin
    pasa/falla". Imprimir [PASA] sobre una medicion contradecia el contrato del
    propio documento y, peor, metia el resultado en el exit code: una medicion
    no puede reprobar.
    """
    PASA = "PASA"
    FALLA = "FALLA"
    BLOQUEADO = "BLOQUEADO"
    MEDIDO = "MEDIDO"


# Solo las COMPUERTAS deciden el codigo de salida. Una medicion que sale mal no
# reprueba nada: publicar un numero feo es el resultado, no un fallo.
COMPUERTAS = (Estado.PASA, Estado.FALLA, Estado.BLOQUEADO)


Resultado = tuple[Estado, str]


def _ejecutar(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args], cwd=RAIZ, capture_output=True, text=True, check=False
    )


def candado_g1() -> Resultado:
    """Determinismo punta a punta: seed + caché + versiones.

    Acumula TODOS los motivos en vez de devolver el primero. Con retorno
    temprano, arreglar `anthropic` destapaba el siguiente bloqueo y daba la
    impresión de que la compuerta estaba a un paso de cerrar cuando le faltaban
    tres. Un estado que oculta lo que viene después no sirve para planear.
    """
    faltan = []
    requisitos = RAIZ / "requirements.txt"
    if not requisitos.exists():
        faltan.append("falta requirements.txt")
    elif "anthropic==" not in requisitos.read_text(encoding="utf-8").lower():
        faltan.append("anthropic sin fijar (no está instalado)")
    if not (RAIZ / "scripts" / "run_simulacion.py").exists():
        faltan.append("falta scripts/run_simulacion.py para comparar dos corridas completas")
    faltan.append("falta el artefacto canónico de salida y el manifiesto de caché")
    return Estado.BLOQUEADO, f"{len(faltan)} bloqueos: " + "; ".join(faltan)


def candado_g2() -> Resultado:
    """Higiene de prompts + corrida re-skinneada."""
    higiene = _ejecutar("-m", "behavior.higiene")
    if higiene.returncode != 0:
        detalle = (higiene.stdout + higiene.stderr).strip().splitlines()[-1]
        return Estado.FALLA, f"behavior.higiene salió {higiene.returncode}: {detalle}"
    # El re-skinning NO vive en un archivo propio: es `behavior.capa.Reskin`, y
    # se activa con `demo.py --reskin`. Buscarlo como `behavior/reskin.py`
    # reportaba "no implementado" sobre una pieza que sí existe.
    try:
        from behavior.capa import Reskin  # noqa: F401
    except ImportError:
        return Estado.BLOQUEADO, "higiene PASA; behavior.capa.Reskin no existe"
    return (
        Estado.BLOQUEADO,
        "higiene PASA; Reskin implementado (behavior/capa.py) pero falta "
        "registrar la corrida canónica y la re-skinneada para compararlas",
    )


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
    # V0 se computa desde los momentos VERSIONADOS. Antes exigia los seis
    # directorios crudos de GEIH 2025, que estan gitignorados: en un clon limpio
    # EL NUMERO quedaba bloqueado y la promesa de "lo reproduce un extrano con un
    # comando" era falsa. Los crudos solo hacen falta para el corte abr-jun, que
    # es un extra.
    momentos_2025 = DATA / "momentos_2025.json"
    if not momentos_2025.exists():
        return Estado.BLOQUEADO, "faltan data/momentos_2025.json y data/poblacion_2025.parquet", None

    pre_ene_jun = float(json.loads(momentos_2025.read_text(encoding="utf-8"))["tasa_informalidad_total"])
    post_ene_jun = float(json.loads((DATA / "momentos.json").read_text(encoding="utf-8"))["tasa_informalidad_total"])
    # El corte abr-jun es OPCIONAL: solo sirve para contrastar contra el
    # trimestre que publica el DANE, y necesita los crudos. Si no estan, V0
    # igual sale completo con la ventana ene-jun.
    crudos = all(
        (DATA / "raw" / f"GEIH_{anio}_{mes}" / "CSV").is_dir()
        for anio in (2025, 2026)
        for mes in ("abril", "mayo", "junio")
    )
    pre_abr_jun = _tasa_periodo(2025, ["abril", "mayo", "junio"]) if crudos else None
    post_abr_jun = _tasa_periodo(2026, ["abril", "mayo", "junio"]) if crudos else None

    pred = _prediccion()
    delta = (post_ene_jun - pre_ene_jun) * 100
    error_firmado = pred["brecha_pp"] - delta
    error_modelo = abs(error_firmado)
    error_baseline = abs(delta)
    skill = 1.0 - error_modelo / error_baseline if error_baseline else float("-inf")
    numeros = {
        "pre_ene_jun_pct": pre_ene_jun * 100,
        "post_ene_jun_pct": post_ene_jun * 100,
        "delta_ene_jun_pp": delta,
        "pre_abr_jun_pct": pre_abr_jun * 100 if crudos else None,
        "post_abr_jun_pct": post_abr_jun * 100 if crudos else None,
        "delta_abr_jun_pp": (post_abr_jun - pre_abr_jun) * 100 if crudos else None,
        "error_firmado_pp": error_firmado,
        "error_absoluto_pp": error_modelo,
        "error_baseline_pp": error_baseline,
        "skill_b1": skill,
        # B3: se llamaba "cobertura", y esa palabra invita a la pregunta que
        # hunde el numero: "¿cobertura de que nivel?". No hay nivel: es un
        # min-max sobre N=5 parafrasis, no un intervalo calibrado. El nombre
        # nuevo dice literalmente lo que se midio.
        "observado_en_rango": float(
            pred["rango_entre_parafrasis_pct"][0]
            <= post_ene_jun * 100
            <= pred["rango_entre_parafrasis_pct"][1]
        ),
        "ancho_banda_pp": pred["ancho_rango_pp"],
    }
    # SEGUNDO EPISODIO, si esta el momento de 2024: el alza de 2025 fue +9,5%,
    # otra magnitud de shock. Sirve para saber si el error del modelo es
    # sistematico o casualidad de un solo anio.
    momentos_2024 = DATA / "momentos_2024.json"
    if momentos_2024.exists():
        pre_2024 = float(json.loads(momentos_2024.read_text(encoding="utf-8"))["tasa_informalidad_total"])
        numeros["pre_2024_pct"] = pre_2024 * 100
        numeros["delta_2024_2025_pp"] = (pre_ene_jun - pre_2024) * 100

    sufijo = "" if crudos else " (sin crudos: sin el corte abr-jun, que es opcional)"
    return Estado.MEDIDO, f"proxy contra proxy desde momentos versionados{sufijo}", numeros


def medicion_m3() -> Resultado:
    try:
        from behavior.ablacion import barrer_factor

        filas = barrer_factor(real=True)
    except Exception as exc:  # pragma: no cover - evidencia operativa en CLI
        return Estado.BLOQUEADO, f"la ablación no pudo correr: {type(exc).__name__}: {exc}"
    hay_cascada = [factor for factor, tasa, _ in filas if tasa > 0.01]
    sin_cascada = [factor for factor, tasa, _ in filas if tasa <= 0.01]
    return Estado.MEDIDO, f"8 factores; cascada={hay_cascada}; sin cascada={sin_cascada}"


def _imprimir_v0(n: dict[str, float]) -> None:
    skill = n["skill_b1"]
    skill_txt = "-inf" if skill == float("-inf") else f"{skill:.3f}"
    print("\nEL NÚMERO · V0")
    print(f"  Error del backtest:          {n['error_absoluto_pp']:.2f} pp (firmado modelo-observado: {n['error_firmado_pp']:+.2f} pp)")
    print(f"  Skill vs persistencia (B1):  {skill_txt}")
    # "banda" NO: con N=5 el p10/p90 es el minimo y el maximo de las cinco
    # parafrasis (en esperanza, los percentiles 16,7 y 83,3). Llamarlo banda
    # sugiere un intervalo calibrado que no es. Ver VALIDATION.md, "Método".
    print(f"  ¿El observado cae en el rango? {'sí' if n['observado_en_rango'] else 'NO'}"
          "   (rango entre paráfrasis, N=5, min–max; no es un intervalo de confianza)")
    print(f"  Ancho del rango:             {n['ancho_banda_pp']:.1f} pp  (entre paráfrasis, no calibrado)")
    print("  Corridas:                    BLOQUEADO: el repo no registra N>=5 trayectorias comparables")
    print(f"  Proxy 2025 ene-jun:          {n['pre_ene_jun_pct']:.2f}%")
    print(f"  Proxy 2026 ene-jun:          {n['post_ene_jun_pct']:.2f}%")
    print(f"  Delta observado:             {n['delta_ene_jun_pp']:+.2f} pp")
    if "delta_2024_2025_pp" in n:
        print()
        print("  Serie de dos episodios (el modelo predice que SUBE en los dos, y mas en el grande):")
        print(f"    2024 -> 2025, alza  +9,5%:   {n['delta_2024_2025_pp']:+.2f} pp observado")
        print(f"    2025 -> 2026, alza +23,0%:   {n['delta_ene_jun_pp']:+.2f} pp observado")
        print("    Las direcciones se OPONEN, y el movimiento real es de unos pocos puntos.")


def medicion_m4(numeros: dict[str, float] | None) -> Resultado:
    """El rango entre paráfrasis: si el observado cae dentro, Y qué tan ancho es.

    Es una MEDICIÓN, así que devuelve MEDIDO: el resultado se publica, no se
    aprueba, y no entra al código de salida. Que el observado quede FUERA no es
    un fallo del
    candado, es el dato. Existe como fila propia porque `VALIDATION.md` la
    declara en la tabla, y un documento que anuncia una fila que el ejecutor no
    imprime es exactamente la deriva que este trabajo existe para evitar.
    """
    if numeros is None:
        return Estado.BLOQUEADO, "sin V0 no hay contra qué medir el rango"
    dentro = "SÍ" if numeros["observado_en_rango"] else "NO"
    return (
        Estado.MEDIDO,
        f"el observado {dentro} cae dentro del rango entre paráfrasis "
        f"({numeros['ancho_banda_pp']:.1f} pp de ancho, N=5, min–max; "
        "no es un p10/p90 calibrado ni un intervalo de confianza)",
    )


def main() -> int:
    resultados = [("G1 reproducibilidad", candado_g1()), ("G2 no contaminación", candado_g2()), ("G3 calibración base", candado_g3())]
    estado_v0, detalle_v0, numeros = medicion_v0()
    # M1 y M2 van SEPARADAS: `VALIDATION.md` declara siete filas y el ejecutor
    # imprimía seis porque las agrupaba. Un documento que anuncia una fila que el
    # ejecutor no tiene es la deriva que este trabajo existe para evitar.
    if numeros is None:
        resultados.extend([
            ("M1 backtest", (estado_v0, detalle_v0)),
            ("M2 habilidad vs baseline", (estado_v0, detalle_v0)),
        ])
    else:
        skill = numeros["skill_b1"]
        skill_txt = "-inf" if skill == float("-inf") else f"{skill:.3f}"
        resultados.extend([
            ("M1 backtest", (estado_v0, f"error {numeros['error_absoluto_pp']:.2f} pp "
                                        f"(firmado {numeros['error_firmado_pp']:+.2f}); {detalle_v0}")),
            ("M2 habilidad vs baseline", (estado_v0, f"skill B1 = {skill_txt}; "
                                                     f"persistencia erra {numeros['error_baseline_pp']:.2f} pp")),
        ])
    resultados.extend([
        ("M3 ablación", medicion_m3()),
        ("M4 rango entre paráfrasis", medicion_m4(numeros)),
    ])

    print("VALIDACIÓN PRE-REGISTRADA")
    for nombre, (estado, detalle) in resultados:
        print(f"  [{estado.value:9}] {nombre}: {detalle}")
    if numeros is None:
        print("\nEL NÚMERO · BLOQUEADO")
        print(f"  {detalle_v0}")
    else:
        _imprimir_v0(numeros)

    # Solo las compuertas deciden. Una medición no reprueba: publicar un número
    # feo ES el resultado.
    compuertas = [e for _, (e, _) in resultados if e in COMPUERTAS]
    return 0 if all(e is Estado.PASA for e in compuertas) else 1


if __name__ == "__main__":
    raise SystemExit(main())
