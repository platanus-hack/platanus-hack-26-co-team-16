"""Tests de la banda entre trayectorias. Corren con pytest o solos, y cuestan $0.

    python3 -m pytest api/test_trayectorias.py -q
    python3 -m api.test_trayectorias

Qué prueban: que el cableado de `api/trayectorias.py` de verdad hace divergir las
N corridas y que lo que sale publicado es una trayectoria que ocurrió. Nada de
esto llama a la API de Anthropic: el agente es un cliente falso cuya respuesta
depende de la REDACCIÓN que le tocó, que es exactamente el fenómeno que la banda
entre trayectorias existe para medir.

Por qué hace falta un cliente falso y no sirve `modo=reglas`, que es lo que ya
está a mano: `ClienteReglas` no lee la paráfrasis —no puede, es una fórmula—, así
que sus 5 trayectorias son idénticas y la banda sale de ancho 0. Medido además un
detalle peor para este propósito: entre factor prestacional 1,30 y 1,70 cambian
**0 de 81** decisiones de la ablación, porque `costo_formal` y `costo_informal`
están tan separados que el factor nunca voltea la comparación. La ablación es
insensible por construcción; sirve para el candado determinista y no para esto.

Lo que NO se prueba acá, y se declara: CUÁNTO se abre la banda con el modelo real.
Eso solo lo dice una corrida con LLM y cuesta dinero. El ancho de estos tests sale
de un cliente inventado y no es un resultado del proyecto; el dato medido que sí
existe son los 22,5 pp del barrido (`scripts/barrido_politicas.py`).
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from behavior.arquetipos import informalidad_observada
from behavior.cliente import parafrasis

from api.servidor import RONDAS_TOTALES, _grilla
from api.trayectorias import N_TRAYECTORIAS, correr_consolidada

RAIZ = Path(__file__).resolve().parents[1]
TEXTOS = parafrasis(N_TRAYECTORIAS)


class ClienteSegunLaRedaccion:
    """Un agente cuya decisión depende de cómo le preguntaron.

    Saca cuántas celdas se salen de la regla del ÍNDICE de la paráfrasis que
    encuentra en el prompt. Si `_parafrasis_fijada()` no llegara hasta acá, las N
    trayectorias verían la misma redacción y saldrían idénticas: ese es el modo de
    falla que estos tests atrapan.
    """

    # Cuántas celdas (de 81, en orden de id) se informalizan según la redacción.
    CUANTAS = {0: 0, 1: 16, 2: 32, 3: 48, 4: 64}

    def __init__(self, orden: dict[str, int]) -> None:
        self.orden = orden
        self.presupuesto = None
        self.llamadas = 0
        self.indices_vistos: set[int] = set()

    def proponer(
        self,
        sistema: str,
        usuario: str,
        modelo: str = "falso",
        max_tokens: int = 0,
        contexto: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        self.llamadas += 1
        indice = next((i for i, t in enumerate(TEXTOS) if t in usuario), None)
        self.indices_vistos.add(indice)
        arq = contexto["arquetipo"]
        if indice is not None and self.orden[arq.id] < self.CUANTAS[indice]:
            return {
                "estrategia_propuesta": "informalizar_total",
                "detalle": {"empleados_a_informalizar": arq.n_trabajadores},
                "justificacion": "cliente de prueba",
            }
        return {
            "estrategia_propuesta": "absorber",
            "detalle": {},
            "justificacion": "cliente de prueba",
        }


def _correr(n_trayectorias: int = N_TRAYECTORIAS):
    """Devuelve (rondas publicadas, n_efectivas, cliente, tasa final por trayectoria)."""
    grilla = _grilla()
    orden = {a.id: i for i, a in enumerate(sorted(grilla, key=lambda x: x.id))}
    cliente = ClienteSegunLaRedaccion(orden)
    finales: dict[int, float] = {}
    rondas, n = correr_consolidada(
        grilla,
        cliente,
        n_trayectorias=n_trayectorias,
        aumento_pct=23.0,
        rondas_totales=RONDAS_TOTALES,
        seed=42,
        simulacion_id="test-banda",
        cobertura_llm=None,
        tasa_informalidad_inicial=informalidad_observada(RAIZ / "data" / "momentos.json"),
        al_terminar_ronda=lambda t, r: finales.__setitem__(t, r.tasa_informalidad),
    )
    return rondas, n, cliente, finales


def test_cada_trayectoria_corre_con_una_parafrasis_distinta():
    """El eslabón que todo lo demás asume: que fijar la paráfrasis LLEGA.

    Es el único test que atrapa el modo de falla silencioso de este módulo. Si el
    parche de `behavior.capa.parafrasis` dejara de llegar, nada reventaría: las N
    corridas darían el mismo número, la banda saldría de ancho 0 y se leería como
    "el modelo es muy preciso", que es la conclusión contraria a la verdadera.
    """
    _, n, cliente, _ = _correr()
    assert n == N_TRAYECTORIAS
    assert cliente.indices_vistos == set(range(N_TRAYECTORIAS)), (
        f"el agente solo vio las paráfrasis {sorted(cliente.indices_vistos)}"
    )


def test_las_trayectorias_divergen_y_la_banda_se_abre():
    rondas, _, _, finales = _correr()
    assert len(set(round(v, 6) for v in finales.values())) == N_TRAYECTORIAS, (
        f"las trayectorias no divergieron: {finales}"
    )
    banda = rondas[-1].banda
    assert banda["tipo"] == "entre_trayectorias"
    assert not banda["degenerada"]
    assert banda["p90"] > banda["p10"], "la banda salió de ancho cero"


def test_lo_que_se_publica_es_una_trayectoria_que_ocurrio():
    """La mediana, no la media. Una media no corresponde a ninguna corrida real."""
    rondas, _, _, finales = _correr()
    ocurridas = {round(v, 6) for v in finales.values()}
    assert round(rondas[-1].tasa_informalidad, 6) in ocurridas


def test_la_banda_cubre_las_trayectorias_medidas():
    rondas, _, _, finales = _correr()
    banda = rondas[-1].banda
    # Con N=5, `_percentiles` deja p10=mínimo y p90=máximo (medido: los
    # percentiles solo se vuelven interiores desde N=9). Mientras eso sea así, la
    # banda tiene que contener TODAS las trayectorias, no la mayoría.
    assert banda["p10"] <= min(finales.values())
    assert banda["p90"] >= max(finales.values())


def test_con_una_sola_trayectoria_la_banda_no_miente():
    """Una corrida sola no puede publicar la banda entre trayectorias.

    Importa porque el tope duro de presupuesto puede cortar la corrida en la
    primera: si eso pasa, lo que sale NO puede venir rotulado como si se hubieran
    pagado las N.
    """
    rondas, n, _, _ = _correr(n_trayectorias=1)
    assert n == 1
    assert rondas[-1].banda.get("tipo") != "entre_trayectorias"


def test_el_tope_paga_la_corrida_que_promete():
    """V-1. El tope derivado tiene que cubrir la corrida que se pidió.

    No prueba una fórmula, prueba que la plata alcanza. Si el tope se queda
    corto la corrida no falla: termina bien y publica una banda sobre menos
    trayectorias de las declaradas, que es peor que un error porque parece un
    resultado. Este test es el que grita.
    """
    from api.servidor import (
        MARGEN_TOPE,
        TOPE_USD_MAXIMO,
        USD_POR_LLAMADA_EN_FRIO,
        llamadas_de_la_corrida,
        tope_derivado,
    )

    llamadas = llamadas_de_la_corrida(0.80, N_TRAYECTORIAS)
    en_frio = llamadas * USD_POR_LLAMADA_EN_FRIO
    assert tope_derivado(0.80, N_TRAYECTORIAS) >= en_frio, (
        f"el tope no paga las {N_TRAYECTORIAS} trayectorias (${en_frio:.2f} en frío)"
    )
    assert MARGEN_TOPE > 1.0, "sin margen, una corrida un poco más cara se corta"
    # La corrida de máxima calidad (las 81 celdas, las N trayectorias) tiene que
    # caber bajo el techo: si no, el techo estaría prohibiendo la mejor corrida.
    assert tope_derivado(1.0, N_TRAYECTORIAS) <= TOPE_USD_MAXIMO


def test_la_cuenta_de_llamadas_cuadra_con_lo_medido():
    """93 calculadas contra 94 medidas (`behavior/README.md` §Costo).

    Es el ancla de toda la aritmética del presupuesto: si la fórmula se separa
    de la medición, el tope deja de significar dinero.
    """
    from api.servidor import llamadas_de_la_corrida

    assert llamadas_de_la_corrida(0.80, 1) == 93


def test_una_corrida_cara_no_queda_autorizada_como_una_barata():
    """Lo que un tope de UN número no podía hacer.

    El costo de la corrida no es constante: depende de la cobertura, de cuántas
    trayectorias y de cuántas paráfrasis. Un número fijo o corta la corrida cara
    (y miente) o autoriza a la barata a gastar como la cara (y cuesta).
    """
    from api.servidor import tope_derivado

    barata = tope_derivado(0.50, 1)
    producto = tope_derivado(0.80, N_TRAYECTORIAS)
    cara = tope_derivado(1.0, N_TRAYECTORIAS)
    assert barata < producto < cara


def test_la_parafrasis_queda_neutralizada_y_esta_declarada():
    """La perilla `parafrasis` no hace nada en el camino de trayectorias.

    Es coherente (una trayectoria ESTÁ definida por su paráfrasis) pero tiene que
    estar dicho, no escondido. Este test obliga a que la declaración y el hecho no
    se separen: si alguien vuelve a hacer funcionar la perilla, esto falla y le
    recuerda cambiar `PARAFRASIS_EFECTO`.

    REESCRITO cuando las N trayectorias pasaron a correr en paralelo. Antes el
    mecanismo era `_parafrasis_fijada()`, un context manager que parcheaba el
    global `behavior.capa.parafrasis` — y ese parche global era justamente lo que
    obligaba a correr las N EN SERIE (~25 min por corrida). Hoy la redacción viaja
    como parámetro (`parafrasis_fija`), así que el invariante se comprueba por
    donde de verdad pasa: **si la redacción llega por parámetro, el global no se
    consulta ni una vez**.
    """
    import behavior.capa as _capa

    from api.servidor import PARAFRASIS_EFECTO

    original = _capa.parafrasis
    consultas: list[int] = []

    def _espia(n=1):
        consultas.append(n)
        return original(n)

    _capa.parafrasis = _espia
    try:
        _, n, cliente, _ = _correr()
    finally:
        _capa.parafrasis = original

    # 1. El global no se tocó: la redacción entró por parámetro en las N.
    assert consultas == [], (
        f"`behavior.capa.parafrasis` se consultó {len(consultas)} veces; "
        "la redacción debería llegar por `parafrasis_fija`"
    )
    # 2. Y aun así cada trayectoria vio SU redacción: neutralizar `n_parafrasis`
    #    no puede costar la divergencia, que es lo que hace la banda.
    assert n == N_TRAYECTORIAS
    assert cliente.indices_vistos == set(range(N_TRAYECTORIAS))
    # 3. Sin parche pegado: el global sigue entero después de la corrida.
    assert len(_capa.parafrasis(5)) == 5
    assert PARAFRASIS_EFECTO == "ninguno"


if __name__ == "__main__":  # pragma: no cover
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
