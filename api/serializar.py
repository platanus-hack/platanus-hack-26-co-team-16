"""Serialización de la corrida hacia el frontend (el enjambre).

Qué modela: nada. Traduce los objetos de `behavior/` a los eventos JSON que
  viajan por el flujo SSE de `api/servidor.py`.
Entradas: `Arquetipo`, `Ronda`, `ResultadoArquetipo` (behavior/) y los datos
  estáticos de `data/`.
Salidas: dicts listos para `json.dumps`.

Regla de esta capa: TODO número que sale de acá es derivable de datos reales de
la GEIH o del motor. Lo que no existe (contrataciones, productividad, utilidad)
no se serializa, y la interfaz no lo muestra. El contrato `contracts/ronda.json`
viaja intacto bajo la llave `contrato`; lo demás va en llaves separadas para no
tocar el contrato congelado.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from behavior.arquetipos import Arquetipo
from behavior.capa import ResultadoArquetipo
from behavior.rondas import Ronda

_RAIZ = Path(__file__).resolve().parent.parent


def parametros_legales() -> dict[str, Any]:
    return json.loads((_RAIZ / "data" / "parametros_legales.json").read_text(encoding="utf-8"))


def momentos() -> dict[str, Any]:
    return json.loads((_RAIZ / "data" / "momentos.json").read_text(encoding="utf-8"))


def piso_salarial_anterior() -> float:
    """El piso ANTES de la política simulada. El `smlmv_cop` de 2026 ya trae el
    alza del 23% adentro; el escenario contrafactual parte del anterior."""
    return float(parametros_legales()["salario"]["smlmv_anterior_cop"])


def arquetipo_a_dict(a: Arquetipo) -> dict[str, Any]:
    """Los campos estáticos y REALES de una celda empleadora GEIH."""
    return {
        "id": a.id,
        "sector": a.sector,
        "tamano": a.tamano,
        "tramo_ingreso": a.tramo_ingreso,
        "n_trabajadores": a.n_trabajadores,
        "ingreso_por_trabajador": round(a.ingreso_por_trabajador, 0),
        "flujo_caja_mensual": round(a.flujo_caja, 0),
        "peso": round(a.peso, 1),
        "n_empresas": round(a.n_empresas, 1),
        "factor_prestacional": round(a.factor_prestacional, 4),
        "fraccion_informal_inicial": round(a.fraccion_informal_inicio, 4),
    }


def evento_poblacion(
    arquetipos: list[Arquetipo],
    cuenta_propia: dict[str, float],
    *,
    rondas_totales: int,
) -> dict[str, Any]:
    """Los datos estáticos de la corrida. `rondas_totales` entra por parámetro
    a propósito: esta capa traduce, no decide. Quien lo declara es
    `api.servidor.RONDAS_TOTALES`, que es el mismo valor que recibe `correr()`."""
    m = momentos()
    return {
        "arquetipos": [arquetipo_a_dict(a) for a in arquetipos],
        "peso_total": round(sum(a.peso for a in arquetipos), 1),
        "tasa_informalidad_observada": float(m["tasa_informalidad_total"]),
        "ocupados_expandidos": float(m["ocupados_expandidos"]),
        # Un tercio de los ocupados de Bogotá es cuenta propia y la grilla de
        # empleadores no los cubre: se reporta para que el enjambre no se lea
        # como la ciudad entera.
        "cuenta_propia": cuenta_propia,
        "piso_salarial_anterior": piso_salarial_anterior(),
        "rondas_totales": rondas_totales,
        "meses_por_ronda": 3,
    }


def _resultado_a_dict(r: ResultadoArquetipo) -> dict[str, Any]:
    """El desglose por arquetipo, compacto: decisión dominante + su porqué."""
    dominante = r.estrategia_dominante if r.distribucion else None
    justificacion = None
    detalle = None
    estrategia_cruda = None
    for d in r.decisiones:
        if d.get("familia") == dominante:
            justificacion = d.get("justificacion")
            detalle = d.get("detalle")
            estrategia_cruda = d.get("estrategia_propuesta")
            break
    vetos = [
        str(v.get("veto", {}).get("razon"))
        for v in r.vetadas
        if v.get("veto", {}).get("razon")
    ]
    return {
        "dominante": dominante,
        "estrategia_cruda": estrategia_cruda,
        "distribucion": r.distribucion,
        "justificacion": justificacion,
        "detalle": detalle,
        "vetadas": len(r.vetadas),
        "razones_veto": vetos[:2],
        "fallbacks": r.fallbacks,
        "sin_salida": r.sin_salida,
    }


def evento_decision(
    ronda: int, arquetipo_id: str, r: ResultadoArquetipo, decididos: int, total: int
) -> dict[str, Any]:
    """Progreso intra-ronda: UNA celda ya decidió. Orden de terminación real."""
    return {
        "ronda": ronda,
        "arquetipo_id": arquetipo_id,
        "avance": {"decididos": decididos, "total": total},
        **_resultado_a_dict(r),
    }


def masa_salarial_relativa(
    ronda: Ronda, arquetipos: list[Arquetipo], aumento_pct: float
) -> float | None:
    """Proxy de PIB: masa salarial de la ronda / masa salarial en reposo.

    Derivable de campos reales: peso, fraccion_empleada, horas, salario mediano
    de la celda. # SUPUESTO: el alza se aplica solo al empleo FORMAL de las
    celdas con salario pegado al piso (tramo t1) — el motor no re-fija salarios
    (los ingresos están congelados; límite declarado en VALIDATION.md), así que
    el término de precio es aritmética sobre la política, no un resultado del
    motor. El empleo informal no recibe el alza por definición.
    """
    if not ronda.estado_por_arquetipo:
        return None
    factor = aumento_pct / 100.0
    base = sum(a.peso * a.ingreso_por_trabajador for a in arquetipos)
    if base <= 0:
        return None
    total = 0.0
    for a in arquetipos:
        e = ronda.estado_por_arquetipo.get(a.id)
        if e is None:
            return None
        alza = factor if a.tramo_ingreso == "t1" else 0.0
        formal = 1.0 - e["fraccion_informal"]
        precio = 1.0 + alza * formal
        total += a.peso * e["fraccion_empleada"] * e["horas"] * a.ingreso_por_trabajador * precio
    return total / base


def fraccion_bajo_minimo(
    ronda: Ronda, arquetipos: list[Arquetipo], aumento_pct: float
) -> float | None:
    """Qué fracción de los que conservan el empleo gana bajo el piso NUEVO.

    # SUPUESTO: el piso nuevo es `smlmv_anterior_cop × (1 + aumento/100)`. El
    empleo formal cumple el piso por definición legal; el informal conserva su
    salario mediano congelado (el motor no re-fija salarios), así que queda por
    debajo cuando esa cifra no alcanza el piso nuevo.
    """
    if not ronda.estado_por_arquetipo:
        return None
    piso_nuevo = piso_salarial_anterior() * (1.0 + aumento_pct / 100.0)
    empleada = 0.0
    bajo = 0.0
    for a in arquetipos:
        e = ronda.estado_por_arquetipo.get(a.id)
        if e is None:
            return None
        peso_empleado = a.peso * e["fraccion_empleada"]
        empleada += peso_empleado
        if a.ingreso_por_trabajador < piso_nuevo:
            bajo += peso_empleado * e["fraccion_informal"]
    return (bajo / empleada) if empleada > 0 else None


def evento_ronda(
    ronda: Ronda, arquetipos: list[Arquetipo], aumento_pct: float
) -> dict[str, Any]:
    """El agregado de una ronda cerrada, con el contrato intacto adentro."""
    return {
        "contrato": ronda.a_contrato(),
        "desglose_estrategias": {
            k: round(v, 4) for k, v in ronda.desglose_estrategias().items()
        },
        "desglose_estrategias_conteo": ronda.desglose_estrategias_conteo(),
        "fraccion_jornada_recortada": round(ronda.fraccion_jornada_recortada, 4),
        "fraccion_fallback": round(ronda.fraccion_fallback, 4),
        "fraccion_sin_salida": round(ronda.fraccion_sin_salida, 4),
        "fraccion_poblacion_llm": round(ronda.fraccion_poblacion_llm, 4),
        "varianza_media": round(ronda.varianza_media, 4),
        "estado_por_arquetipo": {
            aid: {k: round(v, 4) for k, v in e.items()}
            for aid, e in ronda.estado_por_arquetipo.items()
        },
        "por_arquetipo": {
            aid: _resultado_a_dict(r) for aid, r in ronda.por_arquetipo.items()
        },
        "masa_salarial_relativa": _redondear(
            masa_salarial_relativa(ronda, arquetipos, aumento_pct)
        ),
        "fraccion_bajo_minimo": _redondear(
            fraccion_bajo_minimo(ronda, arquetipos, aumento_pct)
        ),
    }


def _redondear(x: float | None, ndigitos: int = 4) -> float | None:
    return None if x is None else round(x, ndigitos)
