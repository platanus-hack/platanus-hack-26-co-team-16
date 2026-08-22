"""Tests del veto de factibilidad. Corren con pytest o solos.

    python3 -m pytest engine/test_veto.py -q
    python3 -m engine.test_veto

Viven en `engine/` y no en `tests/` a propósito: `tests/` es de R5 y esta
carpeta es mía. Cuando R5 cablee `make test`, esto se descubre igual.

Estos tests SÍ importan `behavior/` — el código de producción de `engine/` no lo
hace nunca. La razón es que lo que se prueba acá es justamente el contrato entre
las dos capas: que las razones del veto sobrevivan a la guardia de higiene de la
otra orilla, y que la firma del veto encaje en el `Protocol` que ella consume.
"""

from __future__ import annotations

from behavior import higiene
from behavior.arquetipos import Arquetipo
from behavior import contrato

from engine.veto import (
    ESTRATEGIA_TERMINAL,
    MAX_REINTENTOS,
    EstadoVivo,
    caja_de_la_ronda,
    planta_viva,
    razones_posibles,
    vetar,
    veto_del_motor,
)


def _firma(**kw) -> Arquetipo:
    """Una firma de prueba. Los defaults son los del andamio de `behavior/`."""
    base = dict(
        id="com-micr-for-t1",
        sector="comercio",
        tamano="micro",
        formal=True,
        tramo_ingreso="t1",
        n_trabajadores=10,
        ingreso_por_trabajador=1_000_000.0,
        flujo_caja=1_800_000.0,   # 0,18 × nómina mensual
        costo_despido=1_500_000.0,  # 1,5 × ingreso mensual
        peso=1.0,
    )
    base.update(kw)
    return Arquetipo(**base)


def _propuesta(estrategia: str, **detalle) -> dict:
    return {
        "agente_id": "com-micr-for-t1",
        "ronda": 1,
        "estrategia_propuesta": estrategia,
        "detalle": detalle,
        "justificacion": "prueba",
        "veto": None,
    }


# --- El compromiso público: las razones salen limpias ------------------------


def test_todas_las_razones_declaradas_pasan_la_higiene():
    """Compromiso del review del PR #4.

    `razones_posibles()` rinde TODAS las plantillas de `_RAZONES` con números
    adversarios (cuatro dígitos exactos, montos que sin agrupar se leerían como
    un año). Si alguien agrega una razón sucia, este test la encuentra sin que
    haya que acordarse de agregarla acá.
    """
    for razon in razones_posibles():
        assert higiene.revisar(razon) == [], f"razón contaminada: {razon}"


def test_las_razones_que_el_veto_emite_de_verdad_pasan_la_higiene():
    """Lo anterior prueba las plantillas; esto prueba las salidas reales."""
    casos = [
        # (firma, propuesta) que fuerzan cada rama con números peligrosos
        (_firma(n_trabajadores=2026), _propuesta("despedir", empleados_a_despedir=3000)),
        (_firma(costo_despido=1_990_000.0), _propuesta("despedir", empleados_a_despedir=9)),
        (_firma(), _propuesta("informalizar_parcial", empleados_a_informalizar=1990)),
        (_firma(), _propuesta("despedir", empleados_a_despedir=-2020)),
        (_firma(), _propuesta("bajar_horas", reduccion_horas_pct=2020.0)),
        (_firma(), _propuesta("despedir", empleados_a_despedir="dos mil veinte")),
    ]
    for firma, propuesta in casos:
        veredicto = vetar(propuesta, firma)
        assert not veredicto["factible"], f"debía vetarse: {propuesta}"
        assert higiene.revisar(veredicto["razon"]) == [], veredicto["razon"]


def test_una_razon_sucia_si_seria_detectada():
    """Control del control: la guardia de higiene no está apagada."""
    assert higiene.revisar("el gobierno subió el salario mínimo en 2026") != []


# --- Las reglas materiales ---------------------------------------------------


def test_despedir_sin_caja_para_indemnizar_se_veta_con_razon():
    firma = _firma(n_trabajadores=10, flujo_caja=100_000.0, costo_despido=1_500_000.0)
    veredicto = vetar(_propuesta("despedir", empleados_a_despedir=5), firma)
    assert veredicto["factible"] is False
    assert veredicto["razon"]  # un veto sin razón no es un veto


def test_despedir_lo_que_la_caja_aguanta_pasa():
    # Caja del trimestre = 1.800.000 × 3 = 5.400.000; despedir a 3 cuesta 4.500.000.
    firma = _firma()
    assert caja_de_la_ronda(firma) == 5_400_000.0
    veredicto = vetar(_propuesta("despedir", empleados_a_despedir=3), firma)
    assert veredicto["factible"] is True
    assert veredicto["razon"] is None


def test_no_se_puede_despedir_a_mas_gente_de_la_que_hay():
    veredicto = vetar(_propuesta("despedir", empleados_a_despedir=99), _firma())
    assert veredicto["factible"] is False


def test_no_se_puede_sacar_de_regla_a_mas_de_los_que_estan_en_regla():
    firma = _firma(n_trabajadores=4)
    assert vetar(_propuesta("informalizar_parcial", empleados_a_informalizar=4), firma)[
        "factible"
    ]
    assert not vetar(
        _propuesta("informalizar_parcial", empleados_a_informalizar=5), firma
    )["factible"]


def test_una_unidad_que_ya_esta_fuera_de_regla_no_puede_volver_a_salirse():
    """El bug que `firma.formal` no puede ver: es estado inicial, no vivo."""
    firma = _firma(n_trabajadores=6, formal=True)
    estado = EstadoVivo.inicial([firma])

    # Ronda 1: la planta está entera en regla, sacar a 6 es factible.
    assert vetar(_propuesta("informalizar_total", empleados_a_informalizar=6), firma, estado)[
        "factible"
    ]

    # El motor cierra la ronda: la planta quedó entera fuera de regla.
    estado.registrar("com-micr-for-t1", fraccion_informal=1.0, fraccion_empleada=1.0)

    # Ronda 2: `firma.formal` sigue diciendo True, pero ya no queda a quién sacar.
    veredicto = vetar(
        _propuesta("informalizar_parcial", empleados_a_informalizar=1), firma, estado
    )
    assert veredicto["factible"] is False
    assert higiene.revisar(veredicto["razon"]) == []


def test_el_estado_vivo_encoge_la_planta_para_el_veto_de_despido():
    firma = _firma(n_trabajadores=10)
    estado = EstadoVivo.inicial([firma])
    estado.registrar("com-micr-for-t1", fraccion_informal=0.0, fraccion_empleada=0.3)
    assert planta_viva(firma, estado) == (3, 3)
    assert not vetar(_propuesta("despedir", empleados_a_despedir=5), firma, estado)[
        "factible"
    ]


def test_los_porcentajes_no_pueden_pasar_de_cien_ni_ser_negativos():
    firma = _firma()
    assert not vetar(_propuesta("bajar_horas", reduccion_horas_pct=120.0), firma)["factible"]
    assert not vetar(_propuesta("bajar_horas", reduccion_horas_pct=-5.0), firma)["factible"]
    assert vetar(_propuesta("bajar_horas", reduccion_horas_pct=40.0), firma)["factible"]
    # Subir un precio más del 100% es caro, no imposible: el veto no opina.
    assert vetar(_propuesta("subir_precios", aumento_precios_pct=150.0), firma)["factible"]


# --- Las decisiones de diseño, probadas ---------------------------------------


def test_el_veto_juzga_el_detalle_y_no_el_nombre_de_la_estrategia():
    """El modelo inventa nombres; el veto no puede depender de que acierte."""
    firma = _firma(flujo_caja=1.0)
    por_nombre_conocido = vetar(_propuesta("despedir", empleados_a_despedir=4), firma)
    por_nombre_inventado = vetar(
        _propuesta("reducir_planta_operativa", empleados_a_despedir=4), firma
    )
    assert por_nombre_conocido == por_nombre_inventado
    assert not por_nombre_conocido["factible"]


def test_una_estrategia_sin_familia_no_se_puede_costear_y_pasa():
    """Límite declarado: sin `familia`, el veto no sabe que esto es absorber.

    La canonicalización de nombres es de `behavior/contrato.familia()` y viaja
    dentro de la decisión (la pone `behavior/capa.py` antes de llamar al veto).
    Una decisión que llega sin ella no se puede costear, y pasa. Es el precio de
    no duplicar la tabla de familias en `engine/`, y se prueba para que sea un
    límite conocido y no una sorpresa.
    """
    assert vetar(_propuesta("absorber"), _firma(), None, 30.0)["factible"] is True


def test_un_detalle_ilegible_se_veta_en_vez_de_reventar():
    """La lección del crítico #1: una respuesta mala no puede matar la corrida.

    Un veto devuelve un reintento; una excepción mata la ronda y además queda
    escrita en la caché, así que la re-corrida determinista revienta para siempre
    en el mismo punto.
    """
    veredicto = vetar(_propuesta("despedir", empleados_a_despedir={"raro": 1}), _firma())
    assert veredicto["factible"] is False
    assert veredicto["razon"]


def test_el_veto_es_puro_y_determinista():
    firma = _firma()
    propuesta = _propuesta("despedir", empleados_a_despedir=3)
    assert vetar(propuesta, firma) == vetar(propuesta, firma)
    assert propuesta["veto"] is None  # `vetar()` no muta la decisión


def test_el_veredicto_cumple_el_contrato_que_behavior_valida():
    firma = _firma(flujo_caja=1.0)
    for propuesta in (
        _propuesta("despedir", empleados_a_despedir=4),
        _propuesta("cumplir"),
    ):
        propuesta["veto"] = vetar(propuesta, firma)
        contrato.validar(propuesta, exigir_veto=True)


def test_veto_del_motor_encaja_en_la_firma_que_consume_behavior():
    """Dos argumentos posicionales, como el `Protocol Veto` de `behavior/capa.py`."""
    firma = _firma()
    estado = EstadoVivo.inicial([firma])
    veto = veto_del_motor(estado)
    assert veto(_propuesta("cumplir"), firma) == {"factible": True, "razon": None}


def test_la_estrategia_terminal_coincide_con_la_de_behavior():
    """Canon de `docs/IDEA.md` §5.3 y §5.7, y compromiso #2 del review del PR #4.

    Antes esto comparaba la constante contra su propio literal, así que no podía
    fallar — y por eso no detectó que el comentario de `engine/veto.py` afirmaba
    un import que no existe (hallazgo de la review del PR #5). Ahora compara las
    DOS definiciones, que es lo único que puede divergir de verdad.
    """
    assert ESTRATEGIA_TERMINAL == contrato.FALLBACK
    assert contrato.ORDEN_FALLBACK[0] == ESTRATEGIA_TERMINAL


def test_max_reintentos_coincide_entre_el_motor_y_la_capa():
    """El otro par duplicado que la review del PR #5 marcó: hoy coinciden, y el
    día que dejen de coincidir esto lo dice en vez de que nadie se entere."""
    from behavior.capa import MAX_REINTENTOS as MAX_CAPA

    assert MAX_REINTENTOS == MAX_CAPA


def test_el_fallback_no_manda_a_formalizarse_a_quien_no_puede_pagar():
    """ADR 0010: la razón de ser de A2, probada de punta a punta.

    Una planta EN REGLA y sin caja tiene vetadas las tres opciones del orden
    —formalizar no aplica, pero el alza no le cabe ni recortando jornada—, así
    que sale `sin_salida` y se queda como estaba. Con la regla vieja salía
    `cumplir`, o sea pagando el alza que acababa de demostrar que no podía.
    """
    firma = _firma(formal=True, flujo_caja=1.0)
    veto = veto_del_motor(EstadoVivo.inicial([firma]), 30.0)
    decision = contrato.decision_fallback("x", 1, ["sin caja"], veto=veto, arquetipo=firma)
    assert decision["sin_salida"] is True
    assert decision["familia"] == "absorber"
    assert decision["estrategia_propuesta"] != ESTRATEGIA_TERMINAL


def test_una_planta_toda_fuera_de_regla_no_paga_el_alza_ni_recortando_jornada():
    """El límite del caso anterior, explícito para que no se lea como un bug.

    Si NADIE está en regla, el alza del costo laboral formal no toca a esta
    firma: su sobrecosto es cero y `bajar_horas` le cabe. Por eso el fallback de
    una unidad totalmente informal NO es `sin_salida` — y es correcto: esa es
    justamente la ventaja que hace de la informalidad una salida.
    """
    firma = _firma(formal=False, flujo_caja=1.0)
    veto = veto_del_motor(EstadoVivo.inicial([firma]), 30.0)
    decision = contrato.decision_fallback("x", 1, ["sin caja"], veto=veto, arquetipo=firma)
    assert "sin_salida" not in decision
    assert decision["familia"] == "bajar_horas"


def test_bajar_horas_atenua_el_sobrecosto_en_proporcion_a_la_jornada():
    """A4 + A1: recortar la mitad de la jornada paga la mitad del alza."""
    firma = _firma()  # caja de periodo = 5.400.000
    alza = 20.0  # sobrecosto pleno = 10 × 1.000.000 × 1,40 × 0,20 × 3 = 8.400.000
    pleno = _propuesta("absorber")
    pleno["familia"] = "absorber"
    assert vetar(pleno, firma, None, alza)["factible"] is False

    recortado = _propuesta("bajar_horas", reduccion_horas_pct=50.0)
    recortado["familia"] = "bajar_horas"
    # La mitad de 8.400.000 son 4.200.000, que sí cabe en 5.400.000.
    assert vetar(recortado, firma, None, alza)["factible"] is True


def test_el_fallback_si_formaliza_a_quien_puede_pagar():
    """El canon de `IDEA.md` se conserva donde la caja alcanza."""
    firma = _firma(formal=True, flujo_caja=500_000_000.0)
    veto = veto_del_motor(EstadoVivo.inicial([firma]), 5.0)
    decision = contrato.decision_fallback("x", 1, ["r"], veto=veto, arquetipo=firma)
    assert decision["estrategia_propuesta"] == ESTRATEGIA_TERMINAL
    assert "sin_salida" not in decision


# --- A1: el veto revisa las cuatro jugadas, no dos ---------------------------
#
# Los tres tests que el plan de correcciones declara obligatorios: factible
# justo debajo del umbral, infactible justo encima, y las dos razones nuevas
# pasando la higiene (esto último lo cubre solo
# `test_todas_las_razones_declaradas_pasan_la_higiene`, porque
# `razones_posibles()` se construye desde `_RAZONES`).


def _absorber(aumento: float, **kw) -> dict:
    """Una propuesta de absorber con su familia ya canonicalizada."""
    p = _propuesta("absorber")
    p["familia"] = "absorber"
    return p


def test_absorber_cabe_en_la_caja_justo_debajo_del_umbral():
    """Con caja = 0,18 × nómina y factor 1,40, el techo del alza es ~12,9%.

    La aritmética: la caja del periodo es 0,18 × nómina × 3 y el sobrecosto es
    nómina × 1,40 × (alza/100) × 3, así que el alza límite es 0,18/1,40.
    """
    firma = _firma()  # 10 trabajadores × 1.000.000, caja 1.800.000/mes
    veredicto = vetar(_absorber(12.0), firma, None, 12.0)
    assert veredicto["factible"] is True, veredicto


def test_absorber_no_cabe_justo_encima_del_umbral():
    firma = _firma()
    veredicto = vetar(_absorber(14.0), firma, None, 14.0)
    assert veredicto["factible"] is False
    assert "margen" in veredicto["razon"]


def test_el_umbral_de_absorber_es_el_que_dice_la_aritmetica():
    """0,18/1,40 = 12,857%. Se prueba el borde por los dos lados."""
    firma = _firma()
    umbral = 0.18 / 1.40 * 100
    assert vetar(_absorber(umbral - 0.5), firma, None, umbral - 0.5)["factible"] is True
    assert vetar(_absorber(umbral + 0.5), firma, None, umbral + 0.5)["factible"] is False


def test_formalizar_una_planta_informal_no_cabe_en_la_caja():
    """El caso que producía el signo invertido: formalizarse gratis.

    Una unidad informal que se pone en regla paga el sobrecosto prestacional de
    toda su planta. Con 0,18 de caja contra ~0,40 de sobrecosto, no alcanza.
    """
    firma = _firma(formal=False)
    p = _propuesta("cumplir")
    p["familia"] = "cumplir"
    veredicto = vetar(p, firma, None, 10.0)
    assert veredicto["factible"] is False
    assert "en regla" in veredicto["razon"]


def test_formalizar_si_cabe_cuando_la_caja_alcanza():
    """El veto no es un muro: con caja suficiente, formalizarse pasa."""
    firma = _firma(formal=False, flujo_caja=50_000_000.0)
    p = _propuesta("cumplir")
    p["familia"] = "cumplir"
    assert vetar(p, firma, None, 5.0)["factible"] is True


def test_una_planta_ya_formal_que_cumple_solo_paga_el_alza():
    """Sin gente fuera de regla no hay costo de formalización, solo el alza."""
    firma = _firma(formal=True)
    p = _propuesta("cumplir")
    p["familia"] = "cumplir"
    assert vetar(p, firma, None, 5.0)["factible"] is True
    veredicto = vetar(p, firma, None, 40.0)
    assert veredicto["factible"] is False
    assert "margen" in veredicto["razon"]


def test_el_factor_prestacional_de_la_firma_mueve_el_umbral():
    """C1: cada celda trae su factor (1,3835-1,5829), no el promedio 1,40.

    El micro-empleador NO exonerado del Art. 114-1 paga más, así que su umbral
    de absorción es más bajo. Si el veto usara un factor promedio para todos,
    esta diferencia —que es donde vive el 66,7% de la informalidad— se borraría.
    """
    alza = 12.0
    barato = _firma(factor_prestacional=1.3835)
    caro = _firma(factor_prestacional=1.5829)
    assert vetar(_absorber(alza), barato, None, alza)["factible"] is True
    assert vetar(_absorber(alza), caro, None, alza)["factible"] is False


def test_veto_del_motor_lleva_el_aumento_adentro():
    """La política es constante en la corrida: entra al cierre, no a cada llamada."""
    firma = _firma()
    estado = EstadoVivo.inicial([firma])
    assert veto_del_motor(estado, 5.0)(_absorber(5.0), firma)["factible"] is True
    assert veto_del_motor(estado, 40.0)(_absorber(40.0), firma)["factible"] is False


def test_absorber_de_una_unidad_informal_no_paga_el_alza_de_los_que_no_estan_en_regla():
    """El alza encarece el costo laboral FORMAL. Quien no está en regla no la paga.

    Es la asimetría que hace que informalizarse sea una salida: si el veto le
    cobrara el alza a la planta fuera de regla, evadir no aliviaría nada.
    """
    firma = _firma(formal=False)
    assert vetar(_absorber(40.0), firma, None, 40.0)["factible"] is True


if __name__ == "__main__":  # pragma: no cover
    import sys
    import traceback

    fallidos = 0
    for nombre, fn in sorted(dict(globals()).items()):
        if not nombre.startswith("test_") or not callable(fn):
            continue
        try:
            fn()
            print(f"ok    {nombre}")
        except Exception:
            fallidos += 1
            print(f"FALLA {nombre}")
            traceback.print_exc()
    print(f"\n{fallidos} fallas")
    sys.exit(1 if fallidos else 0)
