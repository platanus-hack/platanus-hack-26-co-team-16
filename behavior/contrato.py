"""El contrato del veto: qué produzco yo (R3) y qué me responde el motor (R2).

Qué modela: la interfaz `contracts/decision.json` ([ADR 0003](../docs/adr/0003-veto-de-factibilidad.md)).
Entradas: la salida cruda del LLM.
Salidas: un dict que cumple `contracts/decision.json`, listo para el veto.
Supuestos: mientras `contracts/decision.json` no exista en disco, se valida
  contra el ejemplo de `docs/PLAN.md` §4 embebido acá (`EJEMPLO`).

Frontera de responsabilidad: yo lleno `estrategia_propuesta`, `detalle` y
`justificacion`. Manuel llena `veto`. Ninguno de los dos toca el campo del otro.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_CONTRATO = Path(__file__).resolve().parents[1] / "contracts" / "decision.json"

# Copiado literal de `docs/PLAN.md` §4. Es la fuente de verdad hasta que Alejo
# cree el archivo; entonces `cargar_contrato()` prefiere el archivo.
EJEMPLO: dict[str, Any] = {
    "agente_id": "empresa-com-04-0083",
    "ronda": 2,
    "estrategia_propuesta": "informalizar_parcial",
    "detalle": {"empleados_a_informalizar": 2},
    "justificacion": "el costo formal supera la productividad de los 2 empleados de menor productividad",
    "veto": {"factible": True, "razon": None},
}

CAMPOS_MIOS = ("agente_id", "ronda", "estrategia_propuesta", "detalle", "justificacion")

# Estrategia conocida != estrategia permitida. El espacio es ABIERTO: esta lista
# solo sirve para agrupar en la pantalla de Dani y para el fallback. Lo que el
# modelo invente entra como está y lo filtra el veto de Manuel.
ESTRATEGIAS_CONOCIDAS = (
    "cumplir",
    "absorber",
    "informalizar_total",
    "informalizar_parcial",
    "despedir",
    "bajar_horas",
    "renegociar",
    "subir_precios",
)

FALLBACK = "absorber"  # tras 3 vetos seguidos: el agente se come el costo

# Esquema para `output_config.format` (salida estructurada de la API). Garantiza
# JSON válido sin cerrar el espacio de estrategias: `estrategia_propuesta` es
# string libre. Lo que sí tiene vocabulario fijo es el DETALLE numérico, porque
# el motor tiene que poder aplicarlo; `otro_detalle` es la válvula de escape
# para lo que el modelo invente.
ESQUEMA_SALIDA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "estrategia_propuesta": {
            "type": "string",
            "description": (
                "Nombre en snake_case de la estrategia. Puede ser una del menú "
                "conocido o una nueva que propongas."
            ),
        },
        "detalle": {
            "type": "object",
            "properties": {
                "empleados_a_informalizar": {"type": ["integer", "null"]},
                "empleados_a_despedir": {"type": ["integer", "null"]},
                "reduccion_horas_pct": {"type": ["number", "null"]},
                "reduccion_margen_pct": {"type": ["number", "null"]},
                "aumento_precios_pct": {"type": ["number", "null"]},
                "otro_detalle": {
                    "type": ["string", "null"],
                    "description": "Solo si la estrategia no cabe en los campos de arriba.",
                },
            },
            "required": [
                "empleados_a_informalizar",
                "empleados_a_despedir",
                "reduccion_horas_pct",
                "reduccion_margen_pct",
                "aumento_precios_pct",
                "otro_detalle",
            ],
            "additionalProperties": False,
        },
        "justificacion": {
            "type": "string",
            "description": "Una frase. Por qué esta salida y no otra.",
        },
    },
    "required": ["estrategia_propuesta", "detalle", "justificacion"],
    "additionalProperties": False,
}


def cargar_contrato() -> dict[str, Any]:
    """El ejemplo congelado: del archivo si existe, del plan si todavía no."""
    if _CONTRATO.exists():
        return json.loads(_CONTRATO.read_text(encoding="utf-8"))
    return EJEMPLO


def construir(agente_id: str, ronda: int, cruda: dict[str, Any]) -> dict[str, Any]:
    """Envuelve la salida del LLM en una decisión válida, sin veredicto todavía.

    `veto` queda en None a propósito: el motor lo llena. Una decisión con
    `veto=None` es una PROPUESTA, no un hecho.
    """
    detalle = {k: v for k, v in (cruda.get("detalle") or {}).items() if v is not None}
    estrategia = str(cruda.get("estrategia_propuesta", "")).strip().lower().replace(" ", "_")
    if not estrategia:
        raise ValueError(f"el modelo no propuso ninguna estrategia: {cruda!r}")
    return {
        "agente_id": agente_id,
        "ronda": int(ronda),
        "estrategia_propuesta": estrategia,
        "detalle": detalle,
        "justificacion": str(cruda.get("justificacion", "")).strip(),
        "veto": None,
    }


def decision_fallback(agente_id: str, ronda: int, razones: list[str]) -> dict[str, Any]:
    """Tras agotar los reintentos: el agente absorbe. Se marca como tal."""
    return {
        "agente_id": agente_id,
        "ronda": int(ronda),
        "estrategia_propuesta": FALLBACK,
        "detalle": {},
        "justificacion": (
            "fallback tras 3 propuestas vetadas: " + "; ".join(razones[-3:])
        ),
        "veto": {"factible": True, "razon": None},
        "fue_fallback": True,
    }


def validar(decision: dict[str, Any], exigir_veto: bool = False) -> dict[str, Any]:
    """Revienta si la decisión no cumple el contrato. Devuelve la decisión."""
    faltan = [c for c in CAMPOS_MIOS if c not in decision]
    if faltan:
        raise ValueError(f"decisión incompleta, faltan {faltan}: {decision!r}")
    if not isinstance(decision["detalle"], dict):
        raise TypeError(f"`detalle` debe ser objeto, llegó {type(decision['detalle'])}")
    if not isinstance(decision["ronda"], int):
        raise TypeError(f"`ronda` debe ser entero, llegó {decision['ronda']!r}")
    if exigir_veto:
        veto = decision.get("veto")
        if not isinstance(veto, dict) or "factible" not in veto:
            raise ValueError(f"el motor no devolvió veredicto de veto: {decision!r}")
        if not veto["factible"] and not veto.get("razon"):
            raise ValueError("un veto sin razón no es un veto: el agente no sabe qué reintentar")
    return decision
