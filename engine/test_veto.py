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


def test_una_estrategia_sin_numeros_pasa_y_es_un_limite_declarado():
    """El veto no puede costear lo que no trae detalle. Se sabe y se dice."""
    assert vetar(_propuesta("absorber"), _firma())["factible"] is True


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


def test_la_estrategia_terminal_es_cumplir():
    """Canon de `docs/IDEA.md` §5.3 y §5.7, y compromiso #2 del review del PR #4."""
    assert ESTRATEGIA_TERMINAL == "cumplir"


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
