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

# Tras 3 vetos seguidos, la estrategia terminal. Era la constante `cumplir` por
# canon de `docs/IDEA.md` §5.3 y §5.7. La [ADR 0010](../docs/adr/0010-fallback-factible.md)
# la reemplaza por una BÚSQUEDA sobre el orden de abajo, por una razón que solo
# se ve después de A1: mandar a `cumplir` a quien acaba de demostrar que no
# puede pagar nada es formalizarlo gratis, que es justo la fuga que A1 cierra.
# Sin este cambio, cada veto nuevo de A1 se convertiría en una formalización
# gratis y el signo seguiría invertido por otra puerta.
#
# Se conserva el nombre `FALLBACK` como el primer candidato del orden, que es lo
# que el canon fijaba, para que nada que lo importe se rompa en silencio.
FALLBACK = "cumplir"

# El orden canónico del fallback: de la más conservadora a la más barata. Se
# recorre hasta encontrar una que el veto acepte.
ORDEN_FALLBACK = ("cumplir", "bajar_horas", "absorber")

# SUPUESTO: `bajar_horas` en el fallback reduce la jornada un 20%. Es el escalón
# intermedio entre cumplir y quedarse igual, y necesita un número porque A4 le
# dio efecto real. Es un supuesto de dirección conocida: más reducción abarata
# más, así que un valor más alto haría el fallback MÁS factible y bajaría los
# `sin_salida`. Va al barrido de sensibilidad de R5.
REDUCCION_HORAS_FALLBACK = 20.0

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


def _detalle_fallback(estrategia: str) -> dict[str, Any]:
    """El detalle numérico mínimo que cada candidata del fallback necesita."""
    if estrategia == "bajar_horas":
        return {"reduccion_horas_pct": REDUCCION_HORAS_FALLBACK}
    return {}


def decision_fallback(
    agente_id: str,
    ronda: int,
    razones: list[str],
    *,
    veto: Any = None,
    arquetipo: Any = None,
) -> dict[str, Any]:
    """Tras agotar los reintentos: la primera opción del orden que SÍ sea factible.

    Antes era la constante `cumplir`, y eso mandaba a formalizarse —la jugada
    más cara de todas— a quien acababa de demostrar tres veces que no podía
    pagar. Mientras el veto no revisaba `cumplir` (antes de A1) eso pasaba
    inadvertido porque el fallback nunca se disparaba: en la corrida medida los
    fallbacks eran 0. Con A1 los vetos se multiplican, y sin esta corrección el
    fallback se volvería la fuga nueva por donde el signo se vuelve a invertir.

    Si NINGUNA opción es factible, el agente se queda exactamente como estaba
    (`absorber` no cambia el estatus de regla de la planta) y la decisión sale
    marcada con `sin_salida=True`. Eso se cuenta y se imprime: *"N% de las
    decisiones no tuvo ninguna opción factible"* es un resultado del modelo
    —dice que la política es impagable para esa parte de la población—, no un
    error del programa.

    Sin `veto` ni `arquetipo` se comporta como antes (devuelve `FALLBACK`), para
    que los dobles de prueba y los tests que no los pasan sigan funcionando.
    """
    sin_salida = False
    if veto is None or arquetipo is None:
        estrategia = FALLBACK
    else:
        for candidata in ORDEN_FALLBACK:
            tentativa = {
                "agente_id": agente_id,
                "ronda": int(ronda),
                "estrategia_propuesta": candidata,
                "detalle": _detalle_fallback(candidata),
                "justificacion": "tentativa de fallback",
                "familia": familia(candidata),
                "veto": None,
            }
            try:
                veredicto = veto(tentativa, arquetipo)
            except Exception:  # noqa: BLE001 - un veto que revienta no puede
                continue       # matar la corrida; se prueba la siguiente
            if veredicto.get("factible"):
                estrategia = candidata
                break
        else:
            # Ninguna opción es pagable: se queda como está.
            estrategia = "absorber"
            sin_salida = True

    razon_texto = "; ".join(razones[-3:]) if razones else "sin razones registradas"
    decision = {
        "agente_id": agente_id,
        "ronda": int(ronda),
        "estrategia_propuesta": estrategia,
        "detalle": _detalle_fallback(estrategia),
        "justificacion": (
            ("sin ninguna opción factible tras 3 propuestas vetadas: " if sin_salida
             else "fallback tras 3 propuestas vetadas: ") + razon_texto
        ),
        "familia": familia(estrategia),
        "veto": {"factible": True, "razon": None},
        "fue_fallback": True,
    }
    if sin_salida:
        decision["sin_salida"] = True
    return decision


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


def jornada_resultante(decision: dict[str, Any], jornada_previa: float = 1.0) -> float:
    """Qué fracción de la jornada original queda DESPUÉS de esta decisión (A4).

    `bajar_horas` era una de las cinco estrategias que el modelo elegía y el
    agregado botaba: se registraba el nombre y `reduccion_horas_pct` no movía
    ningún número. Eso importa más de lo que parece ahora que A1 le cerró la
    puerta a "me aguanto": sin una válvula intermedia, todos los agentes que ya
    no pueden absorber se van a informalizar y el modelo miente por el otro lado
    —satura la informalidad en ~100%— en vez de mentir por el lado de antes.

    Es **acumulativa**, igual que el empleo: quien recortó 20% en la ronda 1 y
    otro 20% en la ronda 2 queda en 0,8 × 0,8 = 0,64 de la jornada original, no
    en 0,6. Una ronda no puede deshacer el recorte de la anterior.

    NO cambia el estatus de regla de la planta: recortar jornada es legal. Eso lo
    decide `fraccion_fuera_de_regla()`, que ignora esta familia a propósito.
    """
    previa = max(0.0, min(1.0, float(jornada_previa)))
    if familia(decision["estrategia_propuesta"]) != "bajar_horas":
        return previa
    pct = decision.get("detalle", {}).get("reduccion_horas_pct")
    if pct is None:
        # SUPUESTO: `bajar_horas` sin número es una etiqueta sin contenido y no
        # mueve nada. Se prefiere no mover a inventarle un recorte: el veto ya
        # acota el campo a [0,100] cuando sí viene.
        return previa
    try:
        recorte = float(pct)
    except (TypeError, ValueError):
        return previa
    recorte = max(0.0, min(100.0, recorte))
    return previa * (1.0 - recorte / 100.0)


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
