"""Las regresiones de los tres bugs críticos del review del PR #4.

Qué modela: nada. Es la prueba de que los bugs están cerrados.
Entradas: ninguna. Salidas: exit 0 si todo pasa, != 0 si algo se rompió.
Supuestos: ninguno. No llama a la API, no toca el caché del repo, cuesta $0.

    python3 -m behavior.pruebas

Por qué vive acá y no en `tests/`
---------------------------------
`tests/` es de R5 (Juanda) y nadie edita la carpeta de otro. Cuando `make test`
exista, esta función se llama desde allá; mientras tanto es ejecutable sola, como
`behavior.higiene`.

Cada prueba reproduce el bug tal como lo reportaron Alejo (R1) y Manuel (R2) y
verifica que hoy NO ocurre. Si alguna vuelve a fallar, el bug volvió.
"""

from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

from behavior import contrato
from behavior.arquetipos import Arquetipo, arquetipos_falsos
from behavior.cache import Cache
from behavior.capa import decidir_arquetipo, situacion_planta
from behavior.cliente import ClienteConductual, SinCredenciales
from behavior.presupuesto import Presupuesto, PresupuestoAgotado
from behavior.rondas import correr

_FALLOS: list[str] = []


def _check(condicion: bool, descripcion: str, detalle: str = "") -> None:
    if condicion:
        print(f"  ok    {descripcion}")
    else:
        print(f"  FALLA {descripcion}" + (f"\n          {detalle}" if detalle else ""))
        _FALLOS.append(descripcion)


# --- Dobles de prueba --------------------------------------------------------


class _Usage:
    input_tokens = 10
    output_tokens = 10
    cache_read_input_tokens = 0


class _Bloque:
    type = "text"

    def __init__(self, texto: str):
        self.text = texto


class _Respuesta:
    stop_reason = "end_turn"

    def __init__(self, texto: str):
        self.usage = _Usage()
        self.content = [_Bloque(texto)]


class _APIFalsa:
    """Devuelve siempre el mismo JSON crudo. Cuenta cuántas veces la llamaron."""

    def __init__(self, *textos: str):
        self.textos = list(textos)
        self.llamadas = 0
        self.messages = self

    def create(self, **_kw):
        i = min(self.llamadas, len(self.textos) - 1)
        self.llamadas += 1
        return _Respuesta(self.textos[i])


VACIA = '{"estrategia_propuesta": "", "detalle": {}, "justificacion": "x"}'
BUENA = '{"estrategia_propuesta": "absorber", "detalle": {}, "justificacion": "x"}'


def _decidir(cli, arq):
    return decidir_arquetipo(
        arq, cli, aumento_pct=23.0, ronda=1, tasa_informalidad=0.3057,
        prob_fiscalizacion=0.0633, multa=1_000_000.0,
    )


# --- Crítico #1 --------------------------------------------------------------


def critico_1_respuesta_invalida_no_llega_al_disco() -> None:
    """Una respuesta que no construye una decisión válida no mata la corrida NI
    queda grabada en el caché.

    El bug: `contrato.construir()` corría FUERA del `try` de `capa.py`, y
    `cliente.proponer()` cacheaba antes de que nadie validara. Con un
    `estrategia_propuesta: ""` —que el esquema JSON permite, no tiene
    `minLength`— la corrida moría con UNA sola llamada y la respuesta mala
    quedaba en disco, así que la re-corrida sin API reventaba idéntico. Se
    disparaba justo en la re-corrida barata delante de un juez.
    """
    print("\nCrítico #1 — una respuesta inválida nunca llega al disco")
    tmp = Path(tempfile.mkdtemp(prefix="behavior-pruebas-"))
    try:
        arq = arquetipos_falsos()[0]

        api = _APIFalsa(VACIA)
        cli = ClienteConductual(Presupuesto(tope_usd=1.0), Cache(tmp), api)
        res = _decidir(cli, arq)
        _check(True, "la corrida NO revienta con estrategia_propuesta vacía")
        _check(
            len(list(tmp.glob("*.json"))) == 0,
            "el caché queda vacío: la respuesta mala no se escribió",
            f"entradas encontradas: {[p.name for p in tmp.glob('*.json')]}",
        )
        _check(api.llamadas == 3, f"reintenta las 3 veces (llamadas: {api.llamadas})")
        _check(
            res.decisiones[0]["estrategia_propuesta"] == contrato.FALLBACK,
            f"cae al fallback canónico '{contrato.FALLBACK}'",
        )
        _check(res.fallos_tecnicos == 3, f"cuenta los 3 fallos ({res.fallos_tecnicos})")

        # La re-corrida SIN API es donde el bug dolía: leía la basura de disco y
        # reventaba idéntico, sin gastar una llamada que lo arreglara. Hoy tiene
        # que fallar por la razón HONESTA —"no tengo ese dato"— y no por releer
        # una respuesta mala. La diferencia entre las dos excepciones es
        # exactamente la diferencia entre el bug y su ausencia.
        cli2 = ClienteConductual(Presupuesto(tope_usd=1.0), Cache(tmp), None)
        cli2._api, cli2._api_intentada = None, True  # sin key y sin SDK
        try:
            _decidir(cli2, arq)
            _check(False, "sin API y sin caché tenía que pedir credenciales")
        except SinCredenciales:
            _check(True, "la re-corrida sin API falla por falta de dato, no por basura releída")
        except ValueError as e:
            _check(False, "el caché quedó envenenado: la re-corrida releyó basura", str(e))

        # Y una respuesta buena sí se cachea, y sí se relee sin API.
        cli3 = ClienteConductual(Presupuesto(tope_usd=1.0), Cache(tmp), _APIFalsa(BUENA))
        _decidir(cli3, arq)
        _check(len(list(tmp.glob("*.json"))) == 1, "una respuesta válida SÍ se cachea")

        cli4 = ClienteConductual(Presupuesto(tope_usd=1.0), Cache(tmp), None)
        cli4._api, cli4._api_intentada = None, True
        res4 = _decidir(cli4, arq)
        _check(
            res4.decisiones[0]["estrategia_propuesta"] == "absorber",
            "la re-corrida sin API relee la respuesta buena del caché",
        )
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def punto_7_fallos_tecnicos_se_cuentan_con_reintento_exitoso() -> None:
    """El caso común —un fallo y un reintento que funciona— tiene que contar.

    Antes solo se sumaba al llegar al fallback, así que la tasa de fallo del
    modelo que reporta el README salía subcontada.
    """
    print("\nPunto #7 — fallos_tecnicos fuera del `if`")
    tmp = Path(tempfile.mkdtemp(prefix="behavior-pruebas-"))
    try:
        arq = arquetipos_falsos()[0]
        cli = ClienteConductual(
            Presupuesto(tope_usd=1.0), Cache(tmp), _APIFalsa(VACIA, BUENA)
        )
        res = _decidir(cli, arq)
        _check(res.fallbacks == 0, "no hubo fallback: el reintento funcionó")
        _check(res.fallos_tecnicos == 1, f"el fallo se contó igual ({res.fallos_tecnicos})")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def punto_8_lo_pagado_queda_cacheado_aunque_dispare_el_corte() -> None:
    """Si el corte duro dispara, la respuesta ya pagada tiene que estar en disco.

    Con el orden inverso (`registrar()` antes de `escribir()`) se descartaba y se
    volvía a pagar en la corrida siguiente.
    """
    print("\nPunto #8 — cachear antes de registrar")
    tmp = Path(tempfile.mkdtemp(prefix="behavior-pruebas-"))
    try:
        cli = ClienteConductual(
            Presupuesto(tope_usd=1e-12), Cache(tmp), _APIFalsa(BUENA)
        )
        try:
            cli.proponer("sistema limpio", "usuario limpio")
            _check(False, "el corte duro debía dispararse")
        except PresupuestoAgotado:
            _check(True, "el corte duro dispara")
        _check(
            len(list(tmp.glob("*.json"))) == 1,
            "la respuesta YA PAGADA quedó en el caché, no se re-paga",
        )
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# --- Crítico #2 --------------------------------------------------------------

_FORMAL = Arquetipo(
    id="x-for", sector="comercio", tamano="pequena", formal=True, tramo_ingreso="t1",
    n_trabajadores=10, ingreso_por_trabajador=1_000_000.0, flujo_caja=1_800_000.0,
    costo_despido=1_500_000.0, peso=100.0,
)


class _Guion:
    """Cliente falso guionado por ronda. Guarda los prompts que vio."""

    def __init__(self, por_ronda: dict[int, dict[str, Any]], defecto: dict[str, Any]):
        self.por_ronda, self.defecto, self.prompts = por_ronda, defecto, []

    def proponer(self, sistema, usuario, modelo="guion", max_tokens=0, contexto=None):
        self.prompts.append((contexto["ronda"], usuario))
        return self.por_ronda.get(contexto["ronda"], self.defecto)


def _corre(guion) -> list:
    return correr(
        [_FORMAL], guion, aumento_pct=23.0, paralelismo=1,
        tasa_informalidad_inicial=0.3057,
    )


def critico_2_el_estado_vive_entre_rondas() -> None:
    """Lo que un arquetipo hizo en una ronda tiene que seguir siendo cierto en la
    siguiente: en el prompt, en la tasa y en el empleo.

    El bug: `ya_informal = not a.formal` era estático las 4 rondas. Una firma que
    informalizó su planta en R1 volvía a ser prompteada como "toda formal" en R2,
    y si respondía "mantener" contaba como cumpliendo — la tasa BAJABA por una
    razón espuria. Y `empleo_relativo` se recalculaba solo con los despidos de
    ESA ronda, así que los despedidos resucitaban.
    """
    print("\nCrítico #2 — el estado del agente vive entre rondas")

    informaliza = {1: {"estrategia_propuesta": "informalizar_total",
                       "detalle": {"empleados_a_informalizar": 10}, "justificacion": "-"}}
    mantiene = {"estrategia_propuesta": "mantener_status_quo", "detalle": {}, "justificacion": "-"}
    g = _Guion(informaliza, mantiene)
    rs = _corre(g)
    tasas = [r.tasa_informalidad for r in rs]
    _check(tasas[1] == 1.0, f"R1 informaliza toda la planta -> 100% ({tasas[1]:.0%})")
    _check(
        tasas[2] == 1.0 and tasas[3] == 1.0,
        "«mantener» en R2/R3 NO devuelve la tasa a 0",
        f"tasas: {[f'{t:.0%}' for t in tasas]}",
    )
    prompt_r2 = next(p for r, p in g.prompts if r == 2)
    _check(
        "Situación actual de tu planta: toda informal" in prompt_r2,
        "el prompt de R2 dice «toda informal», no contradice al historial",
    )
    _check(
        "toda formal" not in prompt_r2,
        "el prompt de R2 ya no dice «toda formal»",
    )

    despide = {1: {"estrategia_propuesta": "despedir",
                   "detalle": {"empleados_a_despedir": 1}, "justificacion": "-"}}
    absorbe = {"estrategia_propuesta": "absorber", "detalle": {}, "justificacion": "-"}
    empleos = [r.empleo_relativo for r in _corre(_Guion(despide, absorbe))]
    _check(abs(empleos[1] - 0.9) < 1e-9, f"despedir 1 de 10 en R1 -> 90% ({empleos[1]:.0%})")
    _check(
        abs(empleos[3] - 0.9) < 1e-9,
        "absorber en R2/R3 NO devuelve el empleo a 100%: los despedidos no resucitan",
        f"empleos: {[f'{e:.0%}' for e in empleos]}",
    )
    _check(
        all(empleos[i] >= empleos[i + 1] for i in range(len(empleos) - 1)),
        "el empleo relativo es monótono no creciente",
    )

    parcial = {
        1: {"estrategia_propuesta": "informalizar_parcial",
            "detalle": {"empleados_a_informalizar": 4}, "justificacion": "-"},
        2: {"estrategia_propuesta": "informalizar_parcial",
            "detalle": {"empleados_a_informalizar": 3}, "justificacion": "-"},
    }
    formaliza = {"estrategia_propuesta": "cumplir", "detalle": {}, "justificacion": "-"}
    ts = [r.tasa_informalidad for r in _corre(_Guion(parcial, formaliza))]
    _check(
        abs(ts[1] - 0.4) < 1e-9 and abs(ts[2] - 0.7) < 1e-9,
        f"informalizar parcial ACUMULA: 40% -> 70% ({ts[1]:.0%} -> {ts[2]:.0%})",
    )
    _check(ts[3] == 0.0, f"formalizarse lleva la planta entera a regla ({ts[3]:.0%})")

    _check(situacion_planta(0.0) == "toda formal", "situacion_planta(0) = toda formal")
    _check(situacion_planta(1.0) == "toda informal", "situacion_planta(1) = toda informal")
    _check("parte formal" in situacion_planta(0.4), "situacion_planta(0.4) es mixta")


def critico_2b_la_ronda_0_es_la_linea_base() -> None:
    """La ronda 0 es la proyección oficial: cumplimiento total, empleo intacto.
    Es la línea base contra la que `MODELO.md` define `empleo_relativo`."""
    print("\nCrítico #2b — la ronda 0 es la línea base sin política")
    r0 = _corre(_Guion({}, {"estrategia_propuesta": "absorber", "detalle": {},
                            "justificacion": "-"}))[0]
    _check(r0.empleo_relativo == 1.0, "empleo_relativo de la ronda 0 = 100%")
    _check(r0.tasa_informalidad == 0.3057, "parte de la informalidad observada (30,57%)")
    _check(r0.por_arquetipo == {}, "la ronda 0 no gasta LLM (ADR 0005)")


# --- Crítico #3 --------------------------------------------------------------


def critico_3_el_costo_de_formalizarse_es_el_costo_completo() -> None:
    """Formalizarse cuesta el costo formal COMPLETO, no solo el sobrecosto.

    El bug: comparar `0,23 x ingreso` contra la sanción esperada es comparar un
    delta contra un nivel. Dejaba el umbral en p > 1,92%, así que cualquier
    probabilidad realista formalizaba a todas las unidades informales en la
    ronda 1, la informalidad caía a 0, `p(E)` saltaba a 100% y el sistema se
    clavaba. El hallazgo "con reglas fijas no hay cascada" era en buena parte
    artefacto de esa comparación.
    """
    print("\nCrítico #3 — el costo real de formalizarse")
    from behavior.ablacion import FACTOR_PRESTACIONAL, ClienteReglas, barrer_factor

    informal = Arquetipo(
        id="y-inf", sector="comercio", tamano="micro", formal=False, tramo_ingreso="t1",
        n_trabajadores=3, ingreso_por_trabajador=1_000_000.0, flujo_caja=540_000.0,
        costo_despido=1_500_000.0, peso=100.0,
    )
    ctx = {
        "arquetipo": informal, "aumento_pct": 23.0, "prob_fiscalizacion": 0.0633,
        "multa": 12_000_000.0, "ronda": 1, "fraccion_informal_previa": 1.0,
    }
    salida = ClienteReglas().proponer("", "", contexto=dict(ctx))
    _check(
        "costo formal" in salida["justificacion"],
        "la justificación compara costo formal contra costo informal",
        salida["justificacion"],
    )

    # El punto de indiferencia analítico: F(1+a) = 1 + 12p
    p_ind = (FACTOR_PRESTACIONAL * 1.23 - 1) / 12
    _check(abs(p_ind - 0.0602) < 5e-4, f"punto de indiferencia p* = {p_ind:.2%} (era 1,92%)")

    # Por debajo de p* sigue informal; por encima se formaliza. La regla ya no
    # formaliza a todo el mundo ante cualquier probabilidad realista.
    baja = ClienteReglas().proponer("", "", contexto={**ctx, "prob_fiscalizacion": 0.03})
    alta = ClienteReglas().proponer("", "", contexto={**ctx, "prob_fiscalizacion": 0.09})
    _check(baja["estrategia_propuesta"] == "absorber", "con p=3% sigue fuera de regla")
    _check(alta["estrategia_propuesta"] == "cumplir", "con p=9% se formaliza")

    # Y el hallazgo que decide el candado 4: el signo se voltea dentro del rango
    # que `engine/MODELO.md` declara incierto para S1 (1,4-1,5).
    barrido = barrer_factor([1.40, 1.45])
    _check(barrido[0][1] < 0.01, f"con F=1,40 la ablación NO produce cascada ({barrido[0][1]:.1%})")
    _check(barrido[1][1] > 0.5, f"con F=1,45 la ablación SÍ produce cascada ({barrido[1][1]:.1%})")


# --- Punto #5 ----------------------------------------------------------------


def punto_5_el_fallback_es_cumplir() -> None:
    """El canon (`IDEA.md` §5.3 y §5.7, `engine/MODELO.md`) dice `cumplir`.

    No es cosmético: para una unidad informal `absorber` puntúa 1.0 fuera de
    regla y `cumplir` puntúa 0.0, así que las dos capas habrían reportado tasas
    distintas con exactamente las mismas decisiones.
    """
    print("\nPunto #5 — FALLBACK = cumplir")
    _check(contrato.FALLBACK == "cumplir", f"FALLBACK = {contrato.FALLBACK!r}")
    d = contrato.decision_fallback("x", 1, ["sin caja"])
    _check(d["fue_fallback"] is True, "el fallback queda marcado y se puede contar")
    _check(
        contrato.fraccion_fuera_de_regla(d, 10, 1.0) == 0.0,
        "una unidad informal que cae al fallback entra en regla",
    )


def punto_11_la_tasa_inicial_no_tiene_default_de_andamio() -> None:
    """`correr()` ya no acepta heredar un 0,42 sin fuente en silencio."""
    print("\nPunto #11 — la tasa inicial es obligatoria")
    try:
        correr([_FORMAL], _Guion({}, {}), aumento_pct=23.0)
        _check(False, "correr() sin tasa_informalidad_inicial debía fallar")
    except TypeError:
        _check(True, "correr() exige tasa_informalidad_inicial explícita")

    from behavior.arquetipos import informalidad_observada

    _check(
        abs(informalidad_observada() - 0.3057) < 1e-9,
        f"momentos.json publica {informalidad_observada():.4f}, no 0,42",
    )


def main() -> int:
    print("Regresiones del review del PR #4 — sin API, sin caché del repo, $0")
    for prueba in (
        critico_1_respuesta_invalida_no_llega_al_disco,
        critico_2_el_estado_vive_entre_rondas,
        critico_2b_la_ronda_0_es_la_linea_base,
        critico_3_el_costo_de_formalizarse_es_el_costo_completo,
        punto_5_el_fallback_es_cumplir,
        punto_7_fallos_tecnicos_se_cuentan_con_reintento_exitoso,
        punto_8_lo_pagado_queda_cacheado_aunque_dispare_el_corte,
        punto_11_la_tasa_inicial_no_tiene_default_de_andamio,
    ):
        prueba()
    print()
    if _FALLOS:
        print(f"{len(_FALLOS)} PRUEBAS FALLARON:")
        for f in _FALLOS:
            print(f"  - {f}")
        return 1
    print("todas las regresiones pasan")
    return 0


if __name__ == "__main__":
    sys.exit(main())
