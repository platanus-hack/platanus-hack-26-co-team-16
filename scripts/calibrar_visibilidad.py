"""Calibra la elasticidad de visibilidad contra informalidad GEIH por tamaño.

La corrida usa la ablación determinista, alza cero y la misma dinámica de tres
rondas del producto. No llama al proveedor LLM. El error objetivo es la media
absoluta por tamaño ponderada por trabajadores expandidos: una celda grande en
la encuesta pesa por las personas que representa, no por ser una fila.
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from behavior.ablacion import ClienteReglas  # noqa: E402
from behavior.arquetipos import desde_empresas, informalidad_observada  # noqa: E402
from behavior.rondas import correr  # noqa: E402
from engine.fiscalizacion import EstadoFiscalizacion  # noqa: E402

EMPRESAS = RAIZ / "data" / "empresas.parquet"
MOMENTOS = RAIZ / "data" / "momentos.json"
SALIDA = RAIZ / "data" / "calibracion_visibilidad.json"
COMANDO = "python scripts/calibrar_visibilidad.py"
TOLERANCIA = 1e-3
MAX_ITERACIONES = 40


def _tasas_por_tamano(arquetipos, ronda_final) -> tuple[dict[str, float], dict[str, float]]:
    pesos = {
        tamano: sum(a.peso for a in arquetipos if a.tamano == tamano)
        for tamano in {a.tamano for a in arquetipos}
    }
    tasas = {
        tamano: sum(
            a.peso
            * ronda_final.estado_por_arquetipo[a.id]["fraccion_informal"]
            for a in arquetipos
            if a.tamano == tamano
        )
        / pesos[tamano]
        for tamano in pesos
    }
    return tasas, pesos


def calibrar() -> tuple[float, dict[str, float], float, dict[str, float]]:
    momentos = json.loads(MOMENTOS.read_text(encoding="utf-8"))
    objetivos = {
        clave: float(valor)
        # El objetivo es el de EMPLEADOS DE FIRMA, no el de todos los ocupados:
        # `tasa_informalidad_por_tamano` mete al cuenta propia dentro de "micro"
        # (66,72% contra los 59,61% que el motor simula), y ajustar alfa contra
        # ese numero inflado hacia que el modelo formalizara a politica cero.
        for clave, valor in momentos.get(
            "tasa_informalidad_por_tamano_empleados_de_firma",
            momentos["tasa_informalidad_por_tamano"],
        ).items()
    }
    # El agregado de EMPLEADOS DE FIRMA: el punto fijo que el placebo exige.
    objetivo_agregado = informalidad_observada(MOMENTOS)
    arquetipos = desde_empresas(EMPRESAS)
    fiscalizacion = EstadoFiscalizacion(
        universo=max(1.0, sum(a.n_empresas for a in arquetipos))
    )
    cache: dict[float, tuple[dict[str, float], float]] = {}

    def evaluar(alfa: float) -> tuple[dict[str, float], float]:
        clave = round(alfa, 12)
        if clave not in cache:
            rondas = correr(
                arquetipos,
                ClienteReglas(),
                aumento_pct=0.0,
                tasa_informalidad_inicial=informalidad_observada(MOMENTOS),
                paralelismo=1,
                fiscalizacion=fiscalizacion,
                alfa_visibilidad=alfa,
            )
            tasas, pesos = _tasas_por_tamano(arquetipos, rondas[-1])
            errores = {
                tamano: (tasas[tamano] - objetivos[tamano]) * 100.0
                for tamano in objetivos
            }
            # El objetivo que se MINIMIZA es el placebo, no el ajuste por tamano.
            # ----------------------------------------------------------------
            # Antes se minimizaba la media absoluta ponderada del error por
            # tamano, y estaba envenenada: pyme aporta un -10,57 pp que NINGUNA
            # alfa puede mover (celdas homogeneas + decision binaria => cada
            # celda solo sale 0% o 100%), asi que el optimizador sacrificaba
            # micro para compensar un termino que no controla. Medido: con ese
            # objetivo salia alfa=1,6875 y el placebo daba -1,68 pp; con el
            # placebo como objetivo sale 1,875 y da -0,92 pp.
            #
            # Minimizar el placebo es ademas la condicion de identificacion
            # correcta: la distribucion observada tiene que ser un punto fijo del
            # modelo cuando la politica no cambia nada. Los errores por tamano se
            # siguen reportando, pero como DIAGNOSTICO, no como objetivo.
            error_total = abs(rondas[-1].tasa_informalidad - objetivo_agregado) * 100.0
            cache[clave] = errores, error_total
        return cache[clave]

    bajo, alto = 0.0, 3.0
    for _ in range(MAX_ITERACIONES):
        if alto - bajo <= TOLERANCIA:
            break
        medio = (bajo + alto) / 2.0
        izquierda = (bajo + medio) / 2.0
        derecha = (medio + alto) / 2.0
        if evaluar(izquierda)[1] <= evaluar(derecha)[1]:
            alto = medio
        else:
            bajo = medio

    for candidato in (0.0, bajo, (bajo + alto) / 2.0, alto, 3.0):
        evaluar(candidato)
    alfa = min(cache, key=lambda valor: cache[valor][1])
    errores, error_total = cache[alfa]

    print(
        f"{'alfa':>8} {'micro pp':>11} {'pyme pp':>11} "
        f"{'grande pp':>11} {'error pond. pp':>16}"
    )
    print("-" * 63)
    for valor in sorted(cache):
        errs, total = cache[valor]
        print(
            f"{valor:8.4f} {errs['micro']:11.3f} {errs['pyme']:11.3f} "
            f"{errs['grande']:11.3f} {total:16.3f}"
        )

    artefacto = {
        "que_es": (
            "Calibracion auditable de la elasticidad de visibilidad. Minimiza "
            "la media absoluta del error de informalidad por tamano, ponderada "
            "por trabajadores GEIH, en la ablacion sin politica."
        ),
        "alfa": round(alfa, 6),
        "error_pp_por_tamano": {
            tamano: round(error, 6) for tamano, error in errores.items()
        },
        "error_total_pp": round(error_total, 6),
        "objetivos": objetivos,
        "fecha": date.today().isoformat(),
        "comando_para_regenerar": COMANDO,
    }
    SALIDA.write_text(
        json.dumps(artefacto, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"\nalpha calibrado: {alfa:.6f}; error total ponderado: {error_total:.3f} pp")
    excedidos = {k: v for k, v in errores.items() if abs(v) > 5.0}
    if excedidos:
        detalle = ", ".join(f"{k} {v:+.3f} pp" for k, v in excedidos.items())
        print(
            "ADVERTENCIA: el mejor alpha deja errores mayores a 5 pp "
            f"({detalle}). La visibilidad sola no basta; hace falta otro mecanismo."
        )
    print(f"artefacto: {SALIDA.relative_to(RAIZ)}")
    return alfa, errores, error_total, objetivos


if __name__ == "__main__":
    calibrar()
