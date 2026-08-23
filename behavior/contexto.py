"""El mundo alrededor de la firma: lo que un empleador real sabe y no le dábamos.

Qué modela: el contexto idiosincrático de UNA unidad productiva en UN periodo —
  quién le compra y cómo se fija ese precio, cómo viene la venta, contra quién
  compite, quién está en su planta, qué le consta de las inspecciones, hasta
  dónde puede apretar su propio margen y qué tiene comprometido de su caja.
Entradas: el `Arquetipo`, la ronda, la tasa de informalidad observada y el seed.
Salidas: un `Contexto` de siete cadenas que `capa.renderizar()` inyecta en
  `prompts/arquetipo.md`.
Supuestos: todos los repartos están marcados `# SUPUESTO:` en el cuerpo.

Por qué existe
--------------
La lectura de las 518 decisiones cacheadas
([`docs/agents/hallazgos-dani-cache-decisiones.md`](../docs/agents/hallazgos-dani-cache-decisiones.md))
midió que un alza del 23% del costo laboral formal producía **UN despido en 518
decisiones** y que el 27% escapaba por `subir_precios`. Ninguna de las dos cosas
era criterio del modelo: eran consecuencia de dos frases del prompt.

1. *«Nada más cambia: tus ingresos, tus clientes y tu capacidad de producción son
   los mismos»* congelaba la demanda. Con ingreso fijo, despedir solo destruye
   producto y encima cuesta la indemnización: **no existía estado del mundo en el
   que despedir fuera la mejor respuesta**. El empleador real no despide por el
   costo laboral en abstracto; despide cuando no ve de dónde va a volver la venta.
2. `subir_precios` se ofrecía como *«trasladas el costo a tus clientes»* en un
   mundo donde los clientes no se pueden ir. Era una puerta sin costo.

Este módulo le devuelve al agente las tres cosas que un empleador sí tiene y que
el prompt le quitaba: **una expectativa de venta**, **un límite a lo que puede
trasladar** y **un piso a lo que puede absorber**. Ninguna es un dato del caso:
todas se derivan de la mecánica del choque.

Tres reglas de diseño, y ninguna es negociable
----------------------------------------------
**1. Nada de acá es un número que el motor también calcule.** La lección del
defecto A3 (`capa.renderizar`) es que un agente que razona con una cifra que el
veto no tiene produce justificaciones que contradicen al árbitro con toda la
razón — estaban mirando billeteras distintas. Todo lo de este módulo es
cualitativo: ordena preferencias, no entra a ninguna aritmética. La caja, la
indemnización y la sanción siguen siendo los únicos números del prompt, y son
exactamente los del motor.

**2. Los rasgos persisten; los choques no.** Quién te compra, contra quién
compites, quién está en tu planta y cuánto margen aguantas se sortean SIN la
ronda: son la firma, y la firma es la misma en el periodo 1 y en el 3. Cómo
viene la venta y qué pasó este periodo se sortean CON la ronda. Sin esta
separación un mismo arquetipo cambiaría de identidad cada ronda y su historial
dejaría de querer decir nada.

**3. Nunca se nombra la actividad, solo el régimen de precio.** `Reskin` (el
candado 3(b) de `VALIDATION.md`) existe para que el modelo no reconozca el
escenario por sus etiquetas. Un texto que dijera "eres un restaurante"
devolvería por la ventana lo que el re-skin saca por la puerta. Acá el sector
solo elige un reparto entre tres formas de fijar el precio, y lo que el agente
lee es la forma, nunca la actividad.

Determinismo
------------
Todo sale de `arquetipos._semilla(seed, ...)`, que ya es la semilla estable del
proyecto. Mismo seed, mismo contexto, misma decisión. Y a la inversa: **hasta
hoy el seed no llegaba al prompt** —`api/servidor.py` lo declara: la perilla
`seed` de la API era una etiqueta— así que dos semillas daban dos aciertos del
mismo caché. Con este módulo el seed elige la trayectoria, que es lo que la
perilla siempre dijo que hacía.

Verificable a mano:

    python3 -m behavior.contexto      # imprime el contexto de un arquetipo en 3 rondas
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from behavior.arquetipos import Arquetipo, _semilla


@dataclass(frozen=True)
class Contexto:
    """Las siete cadenas que van al prompt. Ninguna lleva un monto."""

    clientes: str
    perspectiva_venta: str
    competencia: str
    planta_gente: str
    experiencia_inspeccion: str
    tope_margen: str
    compromisos: str


def _elegir(rng: random.Random, opciones: list[tuple[float, str]]) -> str:
    """Sorteo por pesos declarados. `opciones` es [(peso, texto), ...]."""
    total = sum(p for p, _ in opciones)
    corte = rng.random() * total
    acumulado = 0.0
    for peso, texto in opciones:
        acumulado += peso
        if corte < acumulado:
            return texto
    return opciones[-1][1]


# --- 1. Cómo se fija el precio de lo que vendes -----------------------------
#
# El régimen de precio es la variable que decide si `subir_precios` es una
# salida o una fantasía, y es la que el prompt no tenía. Tres regímenes, que son
# los tres que un empleador reconoce sin que nadie se los explique:
#
#   mostrador — el precio lo pones tú y el cliente decide cada vez que compra.
#   pactado   — el precio quedó cerrado con un comprador por un plazo. Hasta que
#               toque volver a sentarse, el alza de costos la pagas tú entera.
#   tomador   — no pones el precio: tomas el que se esté pagando afuera.
#
# SUPUESTO: el reparto por sector. No sale de una fuente: sale de cómo se cobra
# en cada actividad, y su dirección es la que importa. Quien le vende a hogares
# de a poco puede mover el precio mañana; quien firmó un contrato por término, o
# una obra a precio cerrado, no lo puede mover hasta que el contrato se venza.
# Ese es el punto del reparto, no los decimales. Va al barrido de sensibilidad.
REGIMEN_POR_SECTOR: dict[str, list[tuple[float, str]]] = {
    # Venta al menudeo: el precio está a la vista y cambia cuando el dueño quiere.
    "comercio": [(0.85, "mostrador"), (0.15, "pactado"), (0.00, "tomador")],
    "alojamiento_comida": [(0.90, "mostrador"), (0.10, "pactado"), (0.00, "tomador")],
    "otros_servicios": [(0.80, "mostrador"), (0.20, "pactado"), (0.00, "tomador")],
    # Le vendes a otra unidad bajo un acuerdo por término: aseo, vigilancia,
    # contabilidad, personal en misión. El precio se firmó ANTES del alza.
    "servicios_empresariales": [(0.15, "mostrador"), (0.85, "pactado"), (0.00, "tomador")],
    # Un comprador grande, un acuerdo por todo el periodo, cero margen de mover.
    "adm_publica_edu_salud": [(0.10, "mostrador"), (0.90, "pactado"), (0.00, "tomador")],
    # La obra se cotizó a precio cerrado antes de empezar; el sobrecosto es tuyo.
    "construccion_utilities": [(0.05, "mostrador"), (0.95, "pactado"), (0.00, "tomador")],
    # Pedidos contra lista de precios acordada, con algo de margen por pedido.
    "industria": [(0.25, "mostrador"), (0.70, "pactado"), (0.05, "tomador")],
    # Tarifa pactada con quien te contrata, o carrera suelta.
    "transporte": [(0.30, "mostrador"), (0.60, "pactado"), (0.10, "tomador")],
    # El precio no lo pone quien produce: lo pone la plaza.
    "agro_mineria": [(0.10, "mostrador"), (0.20, "pactado"), (0.70, "tomador")],
}

# SUPUESTO: el reparto de respaldo para un sector que no esté en la tabla (el
# grid falso de `arquetipos_falsos()` usa nombres cortos). Mitad y mitad, que es
# el reparto que menos supone.
REGIMEN_DEFECTO: list[tuple[float, str]] = [
    (0.45, "mostrador"),
    (0.45, "pactado"),
    (0.10, "tomador"),
]

TEXTO_CLIENTES: dict[str, str] = {
    "mostrador": (
        "hogares que te compran de a poco y pagan en el momento. El precio lo "
        "pones tú y lo puedes cambiar cuando quieras"
    ),
    "pactado": (
        "otra unidad más grande, con un precio que quedó cerrado por varios "
        "periodos. Ese precio no se mueve hasta que toque volver a sentarse, y "
        "el alza de costos que te llegó hoy la pagas tú entera hasta entonces"
    ),
    "tomador": (
        "quien te compra paga lo que se esté pagando afuera. Tú no pones ese "
        "precio: lo tomas. Si tu costo sube y ese precio no, la diferencia es tuya"
    ),
}


# --- 2. Cómo viene la venta -------------------------------------------------
#
# Esta es la pieza que faltaba, y la razón por la que había UN despido en 518.
# El mecanismo económico, dicho sin nombrar el caso: el alza que te subió el
# costo laboral formal es un piso que se movió para TODOS, y del otro lado del
# mostrador ese piso es el ingreso de tus clientes. Quien le vende a hogares que
# viven de ese piso puede ver la venta sostenerse o subir. Quien vende contra un
# precio cerrado no ve nada de eso: el valor de su venta está congelado y solo le
# subió el costo. La misma alza es demanda para unos y pinza para otros, y esa
# asimetría es real. Antes el prompt se la negaba a los dos por igual.
#
# SUPUESTO: los tres repartos de abajo. La DIRECCIÓN es la del párrafo anterior;
# las magnitudes son de andamio y van al barrido de sensibilidad de R5.
PERSPECTIVA_POR_REGIMEN: dict[str, list[tuple[float, str]]] = {
    "mostrador": [
        (0.30, "tus clientes están comprando algo más que el periodo pasado: a "
               "ellos también les subió lo que reciben, y una parte de eso vuelve "
               "a tu mostrador"),
        (0.45, "la venta viene igual que el periodo pasado, ni mejor ni peor"),
        (0.25, "la venta viene cayendo y no ves de dónde vaya a volver en los "
               "próximos periodos"),
    ],
    "pactado": [
        (0.10, "quien te compra te avisó que va a pedirte más volumen el "
               "próximo periodo"),
        (0.55, "el volumen que te compran es el mismo de siempre, y el precio "
               "que te pagan por él también"),
        (0.35, "el acuerdo que te sostiene se vence pronto y quien lo renueva ya "
               "te dijo que no va a pagar más por lo mismo"),
    ],
    "tomador": [
        (0.20, "lo que te pagan afuera viene subiendo"),
        (0.40, "lo que te pagan afuera viene igual"),
        (0.40, "lo que te pagan afuera viene bajando y tu costo va para el otro lado"),
    ],
}

# SUPUESTO: el choque idiosincrático del periodo. Dos unidades de la misma celda
# de la encuesta no son la misma unidad: a una se le fue un cliente y a la otra
# le entró un pedido. Es la heterogeneidad que la celda promedia y borra, y sin
# ella los arquetipos deciden todos igual por construcción. El 55% de "nada
# fuera de lo normal" es a propósito: la mayoría de los periodos no pasa nada.
CHOQUE_DEL_PERIODO: list[tuple[float, str]] = [
    (0.15, "además, se te fue uno de los clientes grandes y todavía no lo has "
           "reemplazado"),
    (0.15, "además, el que más te compra te está pagando tarde: la plata entra, "
           "pero un periodo después de que la necesitas"),
    (0.15, "además, te entró un pedido nuevo que te ocupa la planta un buen rato"),
    (0.55, ""),
]


# --- 3. Contra quién compites en precio -------------------------------------
#
# El canal que conecta la cascada con el precio, y que además es el que hace que
# `subir_precios` deje de ser gratis. Si el que te compite de frente opera fuera
# de regla, a él el alza no le llegó: puede sostener su precio y quedarse con tu
# venta. Y la probabilidad de que tu competencia esté fuera de regla ES la
# proporción de unidades fuera de regla que el agente ya observa en el prompt.
#
# Eso agrega un segundo canal a la tesis del proyecto, y va en la misma
# dirección que el primero: más evasión no solo baja la probabilidad de que te
# inspeccionen, también le quita capacidad de traslado a quien se quedó adentro.
#
# El umbral `u` se sortea UNA vez por firma y se compara contra la tasa de cada
# ronda. Así el rasgo persiste (la misma firma tiene la misma competencia) pero
# responde al agregado (si la evasión crece, cruza el umbral y la competencia le
# cambia). Sortearlo cada ronda haría que la competencia parpadeara sin razón.
#
# SUPUESTO: el 15% sin competencia cercana. Una unidad de barrio cuyos clientes
# no tienen a quién más comprarle tiene un traslado que las demás no tienen.
SIN_COMPETENCIA = 0.15

TEXTO_COMPETENCIA: dict[str, str] = {
    "fuera_de_regla": (
        "el que te compite de frente opera fuera de regla. A él este alza no le "
        "llegó y puede sostener su precio: si tú subes, la venta se le va para allá"
    ),
    "en_regla": (
        "los que te compiten de frente cargan los mismos costos que tú y les "
        "subió lo mismo. Si el alza se traslada al precio, se traslada para todos "
        "y ninguno pierde la venta contra el otro"
    ),
    "sin_competencia": (
        "no tienes a nadie cerca haciendo lo mismo. Tus clientes te compran a ti "
        "o les toca irse lejos, y eso te da margen para mover el precio"
    ),
}


# --- 4. Tu planta no son casillas -------------------------------------------
#
# Un empleador no reduce "trabajadores": reduce personas concretas, y no las
# elige al azar. En una unidad chica parte de la planta es familia o lleva años,
# y esa es la última que sale. En una más grande hay gente que entró hace poco y
# todavía no rinde como el resto, y esa es la primera. Las dos cosas son reales y
# empujan en direcciones contrarias, que es justo lo que el prompt no tenía: los
# tres candados que ya traía empujaban todos contra el despido y ninguno a favor.
#
# SUPUESTO: los cortes de tamaño y los repartos. La dirección —entre más chica la
# unidad, más atada está su planta— es lo que se está modelando.
def _texto_planta(rng: random.Random, n: int) -> str:
    if n <= 5:
        return _elegir(rng, [
            (0.55, "en una planta de este tamaño casi todos llevan años contigo o "
                   "son de tu familia. Sacar a uno no es mover un número"),
            (0.30, "uno de los que tienes entró hace poco y todavía no rinde como "
                   "el resto; los demás llevan años"),
            (0.15, "los tienes a todos hace poco: es gente que puedes reemplazar "
                   "si toca, aunque perderías el oficio que ya aprendieron"),
        ])
    if n <= 20:
        return _elegir(rng, [
            (0.35, "el núcleo de tu planta lleva años y sabe el oficio; encima de "
                   "ese núcleo tienes gente más nueva"),
            (0.40, "buena parte de tu planta entró en los últimos periodos y "
                   "todavía no rinde como los que llevan tiempo"),
            (0.25, "tu planta es pareja: casi todos llevan el mismo tiempo y "
                   "rinden parecido"),
        ])
    return _elegir(rng, [
        (0.30, "tienes un núcleo con años de oficio y una capa grande de gente "
               "que entró en los últimos periodos"),
        (0.45, "una parte de tu planta está de más para el volumen que estás "
               "moviendo hoy, y lo sabes"),
        (0.25, "tu planta está justa para lo que produces: no te sobra nadie"),
    ])


# --- 5. Qué te consta de las inspecciones -----------------------------------
#
# La probabilidad que el prompt le entrega al agente la calcula el motor y no se
# toca acá: es el mecanismo de la cascada y es de R2. Lo que sí es irreal es que
# todos los empleadores la lean igual. Un empleador no conoce la probabilidad de
# ser inspeccionado: conoce lo que le pasó a él y a la gente que conoce, y de ahí
# arma su expectativa. Dos unidades con la misma probabilidad en el papel se
# comportan distinto según si alguna vez vieron caer una visita.
#
# Esto NO cambia el número: cambia cuánta atención le presta el agente, que es
# exactamente lo que ocurre. Y ataca de frente el hallazgo §3.3: los que veían
# 0,3% informalizaban y los que veían 100% no, con una limpieza mecánica que
# ningún grupo de empleadores reales tiene.
#
# SUPUESTO: el reparto. La mayoría de los pequeños empleadores nunca ha visto una
# visita, y por eso la cifra del papel les dice poco.
EXPERIENCIA_INSPECCION: list[tuple[float, str]] = [
    (0.55, "nunca has visto que le caiga una visita a nadie que conozcas, así que "
           "el número de arriba te suena más a papel que a algo que vaya a pasar"),
    (0.25, "a un conocido tuyo le cayó una visita y le cobraron. Sabes de primera "
           "mano que no es un cuento, y te acuerdas de cuánto le costó"),
    (0.20, "a ti te visitaron una vez y saliste bien parado, pero te acuerdas del "
           "susto y de las semanas que perdiste atendiendo eso"),
]


# --- 6. Hasta dónde puedes apretar tu propio margen -------------------------
#
# `absorber` aparecía en el menú como *«pagas el costo y reduces tu propio
# margen»*, sin piso. En la caché hay decisiones con `reduccion_margen_pct` de
# 100,0: el dueño trabajando gratis. Ningún dueño hace eso — cierra antes.
#
# Lo que hace real este límite es de dónde sale: en una unidad chica el margen
# NO es una utilidad contable, es el ingreso del hogar del dueño. Por eso el
# techo depende del tamaño y de si en esa casa entra plata por otro lado.
#
# El porcentaje es un tope de PREFERENCIA, no una restricción del motor: el veto
# no revisa `reduccion_margen_pct` (`engine/veto.py`, bloque 1, solo lo acota
# entre 0 y 100). Por eso puede vivir en el prompt sin crear una segunda
# billetera.
#
# SUPUESTO: los tres topes. La dirección —entre más chica la unidad, menos
# margen puede ceder, porque es lo que come su casa— es lo que se modela.
def _texto_tope_margen(rng: random.Random, n: int) -> str:
    if n <= 5:
        return _elegir(rng, [
            (0.60, "tu margen es lo que come tu casa y no entra plata por ningún "
                   "otro lado. Recortarlo más de una quinta parte no lo aguantas "
                   "ni un periodo completo"),
            (0.40, "en tu casa entra algo más aparte de esto, así que puedes ceder "
                   "hasta un tercio de tu margen y aguantar un par de periodos"),
        ])
    if n <= 20:
        return _elegir(rng, [
            (0.55, "puedes ceder hasta un tercio de tu margen por un tiempo; más "
                   "abajo no te alcanza para reponer lo que se daña ni para pagar "
                   "lo que ya debes"),
            (0.45, "puedes ceder hasta la mitad de tu margen si crees que el golpe "
                   "no es permanente"),
        ])
    return _elegir(rng, [
        (0.50, "puedes ceder hasta la mitad de tu margen por varios periodos"),
        (0.50, "puedes ceder hasta la mitad de tu margen, pero por debajo de eso "
               "el capital que tienes metido acá rinde más en otra cosa y lo "
               "sensato es cerrar"),
    ])


# --- 7. Qué tienes comprometido de esa caja ---------------------------------
#
# Ojo con este: es el único que podría crear una segunda billetera, y por eso
# está escrito al revés de como se escribiría solo. Los tres textos declaran que
# la caja del prompt **ya viene neta** de lo que esté comprometido. Así el agente
# entiende POR QUÉ su caja es tan chica —que es lo real: al pequeño empleador el
# arriendo y las cuotas le salen antes que todo— sin restarle nada a la cifra
# que el veto usa. Un texto que dijera "de tu caja, tanto ya está comprometido"
# haría que el agente calculara con una caja y el veto con otra: exactamente el
# defecto A3.
#
# SUPUESTO: el reparto. Que la mayoría de las unidades pequeñas tenga arriendo y
# alguna cuota corriendo es lo que se está afirmando.
COMPROMISOS: list[tuple[float, str]] = [
    (0.60, "el arriendo del local y la cuota de lo que compraste a crédito salen "
           "antes que cualquier otra cosa. La caja de arriba es lo que te queda "
           "DESPUÉS de eso"),
    (0.25, "no le debes nada a nadie. La caja de arriba es tuya entera para este "
           "periodo"),
    (0.15, "vienes de un periodo apretado y estás pagando a proveedores con "
           "retraso. La caja de arriba ya cuenta con eso"),
]


def contexto_de(
    arquetipo: Arquetipo,
    ronda: int,
    tasa_informalidad: float,
    seed: int = 42,
) -> Contexto:
    """El contexto de esta firma en este periodo. Determinista en `seed`.

    Los rasgos (quién te compra, competencia, planta, margen, compromisos,
    experiencia de inspección) se sortean SIN la ronda: son la firma. La
    perspectiva de venta y el choque del periodo se sortean CON la ronda.
    """
    # Rasgos: la ronda NO entra. La misma firma en el periodo 1 y en el 3.
    rasgo = random.Random(_semilla(seed, arquetipo.id, "rasgos"))
    regimen = _elegir(rasgo, REGIMEN_POR_SECTOR.get(arquetipo.sector, REGIMEN_DEFECTO))
    umbral_competencia = rasgo.random()
    planta = _texto_planta(rasgo, arquetipo.n_trabajadores)
    tope = _texto_tope_margen(rasgo, arquetipo.n_trabajadores)
    experiencia = _elegir(rasgo, EXPERIENCIA_INSPECCION)
    compromiso = _elegir(rasgo, COMPROMISOS)

    # Choques: la ronda SÍ entra. Lo que cambia de un periodo al siguiente.
    choque = random.Random(_semilla(seed, arquetipo.id, ronda, "choques"))
    perspectiva = _elegir(choque, PERSPECTIVA_POR_REGIMEN[regimen])
    extra = _elegir(choque, CHOQUE_DEL_PERIODO)
    if extra:
        perspectiva = f"{perspectiva}; {extra}"

    # La competencia depende del agregado observado, contra un umbral fijo de la
    # firma: persiste, pero responde a la cascada.
    if umbral_competencia < SIN_COMPETENCIA:
        competencia = TEXTO_COMPETENCIA["sin_competencia"]
    elif umbral_competencia < SIN_COMPETENCIA + (1.0 - SIN_COMPETENCIA) * max(
        0.0, min(1.0, tasa_informalidad)
    ):
        competencia = TEXTO_COMPETENCIA["fuera_de_regla"]
    else:
        competencia = TEXTO_COMPETENCIA["en_regla"]

    return Contexto(
        clientes=TEXTO_CLIENTES[regimen],
        perspectiva_venta=perspectiva,
        competencia=competencia,
        planta_gente=planta,
        experiencia_inspeccion=experiencia,
        tope_margen=tope,
        compromisos=compromiso,
    )


if __name__ == "__main__":  # pragma: no cover - inspección a mano
    from behavior.arquetipos import arquetipos_falsos

    a = arquetipos_falsos()[0]
    for n in (1, 2, 3):
        c = contexto_de(a, n, 0.42, seed=42)
        print(f"--- {a.id} · periodo {n} ---")
        for campo, valor in c.__dict__.items():
            print(f"  {campo}: {valor}")
