"""El contrato del veto: qué produzco yo (R3) y qué me responde el motor (R2).

Qué modela: la interfaz `contracts/decision.json` ([ADR 0003](../docs/adr/0003-veto-de-factibilidad.md)).
Entradas: la salida cruda del LLM.
Salidas: un dict que cumple `contracts/decision.json`, listo para el veto.
Supuestos: ninguno. `contracts/decision.json` está congelado en `main` y este
  módulo coincide con él campo a campo.

Frontera de responsabilidad: yo lleno `estrategia_propuesta`, `detalle` y
`justificacion`. Manuel llena `veto`. Ninguno de los dos toca el campo del otro.
"""

from __future__ import annotations

from typing import Any

# Copiado literal de `contracts/decision.json`, que Alejo ya congeló en `main`
# (verificado campo a campo). Se conserva embebido como referencia legible del
# contrato; el archivo del repo es la fuente de verdad.
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

# Tras 3 vetos seguidos, la estrategia terminal. Es `cumplir` por canon:
# `docs/IDEA.md` §5.3 y §5.7 ("hasta 3 reintentos; al agotarlos, la estrategia
# terminal es cumplir") y `engine/MODELO.md`, fila del veto de factibilidad.
# Antes acá decía `absorber`, y esa divergencia NO era inocua: para una unidad
# informal, `absorber` puntúa 1.0 fuera de regla y `cumplir` puntúa 0.0, así que
# el motor y esta capa habrían reportado tasas distintas con las mismas
# decisiones. Si alguna vez se cambia, se cambia en la ADR primero.
FALLBACK = "cumplir"

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
    """Tras agotar los reintentos: el agente cumple. Se marca como tal."""
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

# --- Familias canónicas: agregar sin cerrar el espacio -----------------------
#
# El modelo INVENTA nombres, y eso es exactamente lo que queremos: en la primera
# corrida real de 193 llamadas propuso `mantener_informal`, `mantener_informalidad`,
# `mantener_status_quo`, `mantener_operacion_informal` y `mantener_informalidad_total`
# — cinco nombres para la misma conducta. Si agregamos por el nombre crudo, el
# dato A4 sale fragmentado en sinónimos y la pantalla de Dani no dice nada.
#
# La solución NO es cerrar el menú con un enum: eso mata lo que aporta el LLM.
# Guardamos las dos cosas: `estrategia_propuesta` (cruda, tal como la inventó) y
# `familia` (canónica, para agregar). El juez puede ver las dos columnas.

_FAMILIAS: tuple[tuple[str, tuple[str, ...]], ...] = (
    # (familia, subcadenas que la delatan) — se evalúa en orden.
    ("despedir", ("despedir", "despido", "reducir_planta", "recortar_personal")),
    ("bajar_horas", ("bajar_horas", "reducir_horas", "media_jornada", "jornada")),
    ("informalizar", ("informalizar", "informalidad", "informal")),
    ("cumplir", ("cumplir", "formalizar", "formalizarse", "regularizar")),
    ("subir_precios", ("subir_precios", "trasladar_precio", "aumentar_precios")),
    ("renegociar", ("renegociar", "renegociacion")),
    ("absorber", ("absorber", "status_quo", "mantener", "asumir_costo")),
)


def familia(estrategia: str) -> str:
    """Agrupa una estrategia cruda en su familia canónica.

    Devuelve `"otra"` cuando el modelo propuso algo genuinamente nuevo — y ese
    balde es interesante, no un error: es donde vive el hallazgo del dato A4.
    """
    n = estrategia.lower()
    for fam, marcas in _FAMILIAS:
        if any(m in n for m in marcas):
            return fam
    return "otra"


def fraccion_fuera_de_regla(
    decision: dict[str, Any], n_trabajadores: int, fraccion_previa: float
) -> float:
    """Qué fracción de la planta queda fuera de regla DESPUÉS de esta decisión,
    partiendo de la fracción con la que el arquetipo llegó a la ronda.

    Es **acumulativa**: el tercer parámetro es el estado vivo, no el estado
    inicial del arquetipo. Antes era un booleano fijo (`ya_informal`) leído del
    dataclass, y eso hacía que una unidad que informalizó toda su planta en la
    ronda 1 volviera a contar como formal en la ronda 2; si ahí respondía
    "mantener", la tasa de informalidad BAJABA por una razón espuria. El estado
    de una ronda tiene que ser el que dejó la anterior.

    Tres correcciones que salieron de correr de verdad:

    1. `informalizar_parcial` NO saca a toda la unidad de regla — solo a los
       trabajadores que efectivamente pasa a acuerdo informal. Contarlo como
       total era lo que saturaba la tasa en 100% desde la ronda 0.
    2. La misma etiqueta significa cosas distintas según de dónde venga el
       agente: `mantener_status_quo` en una unidad formal es cumplir, y en una
       informal es seguir fuera de regla. Por eso hace falta el estado previo.
    3. Informalizar se ACUMULA sobre lo que ya estaba fuera de regla; formalizar
       lo lleva a cero de una.
    """
    previa = max(0.0, min(1.0, float(fraccion_previa)))
    fam = familia(decision["estrategia_propuesta"])
    if fam == "cumplir":
        # Formalizarse entra a toda la planta en regla, venga de donde venga.
        return 0.0
    if fam == "informalizar":
        n = decision["detalle"].get("empleados_a_informalizar")
        delta = 1.0 if n is None else max(0.0, min(1.0, float(n) / max(1, n_trabajadores)))
        return min(1.0, previa + delta)
    # SUPUESTO: ninguna otra estrategia cambia el estatus de regla de la planta.
    # `absorber`, `despedir`, `bajar_horas`, `renegociar`, `subir_precios` y lo
    # que el modelo invente mueven márgenes, headcount o precios, no el registro
    # laboral. Es el supuesto que decide si una unidad informal que "absorbe"
    # sigue contando como informal — y sí sigue, que es lo correcto.
    return previa
