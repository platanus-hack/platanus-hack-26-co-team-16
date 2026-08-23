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

import pathlib

import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

from behavior import contrato
from dataclasses import replace

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
    # A1 CAMBIÓ ESTA EXPECTATIVA, y ese es el punto de la corrección.
    #
    # Antes: `cumplir` pasaba sin que nadie revisara si la firma podía pagarlo,
    # así que formalizarse llevaba la planta a 0% fuera de regla SIEMPRE, gratis.
    # Esa era la fuga que invertía el signo del modelo: cada veto empujaba al
    # agente hacia la única jugada que nadie le revisaba.
    #
    # Ahora el veto la costea. `_FORMAL` tiene caja de 1.800.000 al mes (5,4M en
    # el periodo) y poner en regla a 7 trabajadores cuesta 7 × 1.000.000 × 0,40 ×
    # 3 = 8,4M: no alcanza. La propuesta se veta y el agente cae al fallback.
    _check(
        ts[3] > 0.0,
        f"formalizarse ya NO es gratis: sin caja, el veto lo impide ({ts[3]:.0%} sigue fuera)",
    )

    # Y con caja suficiente sí formaliza: el veto es una restricción material,
    # no un muro. Si esto fallara, A1 se habría pasado de largo.
    rico = replace(_FORMAL, flujo_caja=500_000_000.0)
    ts_rico = [
        r.tasa_informalidad
        for r in correr([rico], _Guion(parcial, formaliza), aumento_pct=23.0,
                        paralelismo=1, tasa_informalidad_inicial=0.3057)
    ]
    _check(
        ts_rico[3] == 0.0,
        f"con caja suficiente, formalizarse sí lleva la planta a regla ({ts_rico[3]:.0%})",
    )

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

    # EL HALLAZGO CAMBIÓ, y el cambio es a favor del proyecto.
    #
    # Antes: el signo del candado 4 se volteaba dentro del rango que
    # `engine/MODELO.md` declara incierto para S1 — con F=1,40 no había cascada
    # y con F=1,45 sí. O sea que la conclusión dependía de un parámetro que
    # nadie había medido, y eso era el defecto §3.3.
    #
    # Ahora, con la grilla real de empleadores (C1: cada celda trae SU factor,
    # entre 1,3835 y 1,5829) y con la fiscalización del motor (C2: p(sanción)
    # con fuente de la OIT en vez del 0,02 inventado), el resultado es ESTABLE
    # en todo el rango declarado. El factor dejó de decidir el signo.
    #
    # Se prueba la robustez, no un valor: si mañana el resultado vuelve a
    # depender del factor, este test lo dice.
    barrido = barrer_factor([1.35, 1.40, 1.45, 1.50, 1.58])
    valores = [inf for _f, inf, _p in barrido]
    dispersion = max(valores) - min(valores)
    _check(
        dispersion < 0.02,
        f"el candado 4 ya NO depende del factor prestacional "
        f"(dispersión {dispersion:.1%} en el rango 1,35-1,58)",
        f"valores: {[f'{v:.1%}' for v in valores]}",
    )
    _check(
        all(0.0 < v < 1.0 for v in valores),
        f"y el resultado no está saturado en ninguno de los extremos ({valores[0]:.1%})",
    )


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

    # Se compara contra `momentos.json`, no contra un literal. Lo que este punto
    # protege es que la tasa SALGA DEL ARTEFACTO y no de un andamio (el 0,42 sin
    # fuente del PR #4); clavar el numero acá hacía que el candado se disparara
    # cuando el artefacto cambiaba por una razon legitima. Paso justo: al separar
    # empleados de firma de cuenta propia, el objetivo del motor paso de 0,3057
    # (todos los ocupados) a 0,1799 (los que el motor de verdad simula), y este
    # check fallaba señalando un cambio correcto.
    import json

    momentos = json.loads(
        (pathlib.Path(__file__).resolve().parents[1] / "data" / "momentos.json")
        .read_text(encoding="utf-8")
    )
    esperado = momentos.get(
        "tasa_informalidad_empleados_de_firma", momentos["tasa_informalidad_total"]
    )
    _check(
        abs(informalidad_observada() - esperado) < 1e-9,
        f"informalidad_observada() da {informalidad_observada():.4f} y "
        f"momentos.json publica {esperado:.4f}",
    )
    _check(
        abs(informalidad_observada() - 0.42) > 1e-9,
        "informalidad_observada() volvio al 0,42 de andamio, sin fuente",
    )


def s1_1_la_banda_con_tipo_sobrevive_a_a_contrato() -> None:
    """S1-1: `a_contrato()` redondeaba `banda.tipo`, que es un string.

    Mataba la corrida con `TypeError: type str doesn't define __round__ method`
    en la configuración POR DEFECTO del endpoint (5 trayectorias), no en una
    perilla apagada: desde la segunda trayectoria `_percentiles()` pone `tipo`.
    """
    print("\nS1-1 — el round() de a_contrato() no toca los strings de la banda")
    from behavior.rondas import Ronda, consolidar_trayectorias

    def _r(n, tasa, ingreso):
        return Ronda(
            simulacion_id="sim-s1-1", seed=42, ronda=n,
            politica={"tipo": "cambio_costo_laboral", "aumento_pct": 23},
            tasa_informalidad=tasa, prob_fiscalizacion=0.02, empleo_relativo=1.0,
            banda={"p10": tasa, "p90": tasa, "degenerada": True},
            ingreso_laboral_relativo=ingreso,
        )

    corridas = [[_r(0, 0.30, 1.0), _r(1, 0.50 + i * 0.05, 1.0 - i * 0.03)] for i in range(5)]
    mediana = consolidar_trayectorias(corridas)
    _check(mediana[-1].banda.get("tipo") == "entre_trayectorias",
           "con 5 trayectorias la banda queda etiquetada entre_trayectorias")
    try:
        contrato_json = mediana[-1].a_contrato()
        ok = True
    except TypeError as e:
        contrato_json, ok = {}, False
        _check(False, "a_contrato() no revienta con banda.tipo", str(e))
    if ok:
        _check(contrato_json["banda"]["tipo"] == "entre_trayectorias",
               "a_contrato() serializa banda.tipo sin redondearlo")
        # El contrato lo exige desde H+4: contracts/ronda.json declara `tipo`.
        _check(isinstance(contrato_json["banda"]["p10"], float),
               "los números de la banda sí se redondean")


def s1_2_la_banda_cubre_todas_las_metricas_publicadas() -> None:
    """Los rangos internos cubren los números reales del contrato.

    La prueba anterior comparaba la salida contra `METRICAS_PUBLICADAS`, la
    misma constante que construía la salida. Una omisión en la constante se
    verificaba a sí misma y pasaba; por eso `movimiento_pp` quedó afuera.
    """
    print("\nS1-2 — los rangos cubren los números reales de a_contrato()")
    from behavior.rondas import (
        Ronda,
        consolidar_trayectorias,
    )

    def _r(i):
        return Ronda(
            simulacion_id="s", seed=42, ronda=1,
            politica={}, tasa_informalidad=0.50 + i * 0.05,
            prob_fiscalizacion=0.02 + i * 0.001,
            empleo_relativo=1.0 - i * 0.01, banda={},
            traslado_precios_pct=float(i),
            ingreso_laboral_relativo=1.0 - i * 0.03,
            movimiento_pp=i * 0.1,
        )

    mediana = consolidar_trayectorias([[_r(i)] for i in range(5)])[-1]
    contrato = mediana.a_contrato()
    numericas = {
        k for k, v in contrato.items()
        if isinstance(v, (int, float)) and not isinstance(v, bool)
    } - {"seed", "ronda"}
    rangos = getattr(mediana, "rangos_metricas", {})
    cubiertas = set(rangos.get("metricas", {}))
    _check(
        cubiertas == numericas,
        f"los rangos cubren las {len(numericas)} métricas numéricas reales",
        f"faltan: {numericas - cubiertas}; sobran: {cubiertas - numericas}",
    )
    movimiento = rangos.get("metricas", {}).get("movimiento_pp", {})
    _check(
        movimiento.get("maximo", 0) > movimiento.get("minimo", 0),
        "movimiento_pp tiene su propio rango",
    )


def s1_4_la_banda_congelada_sigue_plana_y_el_rango_declara_metodo() -> None:
    """`banda.metricas` no existe en `contracts/ronda.json`.

    Los rangos adicionales quedan fuera de `a_contrato()` hasta que sus dueños
    los expongan como campo aditivo del evento API y congelen ese contrato.
    """
    print("\nS1-4 — banda queda plana; rangos declaran método y muestra")
    from behavior.rondas import (
        Ronda,
        consolidar_trayectorias,
        rangos_entre_trayectorias,
    )

    corridas = [
        [Ronda(
            simulacion_id="s", seed=42, ronda=1, politica={},
            tasa_informalidad=0.40 + i * 0.01,
            prob_fiscalizacion=0.02, empleo_relativo=1.0, banda={},
        )]
        for i in range(5)
    ]
    mediana = consolidar_trayectorias(corridas)[-1]
    publicada = mediana.a_contrato()["banda"]
    _check(
        set(publicada) == {"p10", "p90", "degenerada", "tipo"},
        "a_contrato() conserva la banda plana congelada",
        f"claves publicadas: {sorted(publicada)}",
    )
    rangos = getattr(mediana, "rangos_metricas", {})
    _check(
        rangos.get("metodo") == "rango_muestral"
        and rangos.get("n_efectivas") == 5
        and rangos.get("fuente_variacion") == "trayectorias_observadas",
        "el diagnóstico no promete percentiles ni réplicas iid",
        f"metadatos: {rangos}",
    )

    unica = consolidar_trayectorias([corridas[0]])[-1]
    diagnostico_unico = getattr(unica, "rangos_metricas", {})
    _check(
        diagnostico_unico.get("n_efectivas") == 1
        and unica.banda.get("tipo") != "entre_trayectorias",
        "una trayectoria declara n=1 sin inventar banda entre trayectorias",
        f"banda={unica.banda}; diagnóstico={diagnostico_unico}",
    )

    diagnostico_vacio = rangos_entre_trayectorias([])
    _check(
        diagnostico_vacio.get("n_efectivas") == 0
        and diagnostico_vacio.get("metricas") == {},
        "cero trayectorias no fabrica rangos 0–0",
        f"diagnóstico={diagnostico_vacio}",
    )


def s1_3_ancho_cero_se_rotula_degenerada() -> None:
    """`degenerada` medía «hubo 2+ valores», no «hay dispersión que dibujar».

    En modo=reglas la ablación es determinista: N trayectorias dan el mismo
    número y se publicaba una banda de ancho cero rotulada como real.
    """
    print("\nS1-3 — una banda de ancho cero se rotula degenerada")
    from behavior.rondas import Ronda, _percentiles

    iguales = _percentiles([0.42] * 5, tipo="entre_trayectorias")
    _check(iguales["degenerada"] is True,
           "5 valores idénticos -> degenerada=True (ancho 0, nada que dibujar)")
    distintos = _percentiles([0.40, 0.55], tipo="entre_trayectorias")
    _check(distintos["degenerada"] is False,
           "2 valores distintos -> degenerada=False (sí hay dispersión)")

    casi_iguales = _percentiles(
        [0.420001, 0.420002], tipo="entre_trayectorias"
    )
    ronda = Ronda(
        simulacion_id="s1-3", seed=42, ronda=1, politica={},
        tasa_informalidad=0.42, prob_fiscalizacion=0.02,
        empleo_relativo=1.0, banda=casi_iguales,
    )
    publicada = ronda.a_contrato()["banda"]
    _check(
        publicada["p10"] == publicada["p90"]
        and publicada["degenerada"] is True,
        "si el contrato publica un punto, degenerada=True",
        f"salió {publicada}",
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
        s1_1_la_banda_con_tipo_sobrevive_a_a_contrato,
        s1_2_la_banda_cubre_todas_las_metricas_publicadas,
        s1_3_ancho_cero_se_rotula_degenerada,
        s1_4_la_banda_congelada_sigue_plana_y_el_rango_declara_metodo,
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
