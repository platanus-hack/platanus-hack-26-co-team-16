"""El veto de factibilidad: el motor mata lo que la caja no permite.

Qué modela: la frontera **material** de una firma en un trimestre — a cuánta
  gente puede dejar sin empleo, a cuánta puede sacar de regla, y con cuánta caja
  cuenta para pagarlo ([ADR 0003](../docs/adr/0003-veto-de-factibilidad.md)).
Entradas: una propuesta que cumple `contracts/decision.json` **sin veredicto**
  (`veto = None`) y la firma que la propuso.
Salidas: `{"factible": bool, "razon": str | None}` — exactamente el campo `veto`
  del contrato. `vetar()` no muta la decisión: la llena `behavior/capa.py`.
Supuestos: S8 (la caja de la ronda) y S9 (redondeo de la planta), abajo.

Es la frontera de responsabilidad con R3: el LLM propone, el motor veta. Este
archivo reemplaza los dos dobles de prueba que había (`capa.veto_permisivo` y
`demo.veto_doble_prueba`).

El veto juzga el DETALLE, no el nombre
--------------------------------------
El espacio de estrategias es abierto a propósito: el modelo inventa nombres, y
en la primera corrida real inventó cinco para la misma conducta. Un veto que
compare `estrategia_propuesta == "despedir"` deja pasar `reducir_planta` con el
mismo número de gente adentro — que es el bug del doble de prueba.

Así que el veto no lee el nombre. Lee los campos numéricos de `detalle`, que sí
tienen vocabulario cerrado (`contrato.ESQUEMA_SALIDA`) y son lo único que el
motor puede aplicar al estado del mundo. La canonicalización de nombres es de
`behavior/contrato.familia()` y sigue siendo suya: acá no se duplica.

Las razones salen hacia el modelo
---------------------------------
La razón de un veto viaja **dentro del prompt de reintento** que arma
`behavior/capa.py`, y ese prompt pasa por `behavior/higiene.verificar()`. Una
razón con un símbolo de moneda, un año de cuatro dígitos o la palabra "gobierno"
mata la corrida entera con `ContaminacionError`.

Por eso las razones no se escriben sueltas: salen de `_RAZONES`, se rinden con
`_num()` (que agrupa miles con punto y de paso vuelve imposible que un monto se
lea como un año), y `engine/test_veto.py` las revisa **todas** contra
`higiene.revisar()`. Ese test es la prueba del compromiso público del review del
PR #4, no una preferencia.

El estado vivo: el motor es la fuente única
-------------------------------------------
`firma.formal` es el estado **inicial** del arquetipo, no el de la ronda en
curso: una unidad que se sacó de regla en la ronda 1 llega a la ronda 2 con
`formal=True`. Si el veto lo creyera, dejaría informalizar dos veces a la misma
gente.

`EstadoVivo` es donde vive esa fracción, y es la **única** fuente: es lo que
`behavior/rondas.py` pide en su `PUNTO DE SUTURA` bajo el nombre
`fraccion_informal_previa` (float en [0,1], por `arquetipo_id`, al empezar cada
ronda). Cuando el bucle de rondas lo consuma, los dos dicts de andamio que hoy
lleva `behavior/` se borran y no hay dos estados que puedan divergir.

Quién *avanza* ese estado es otra pregunta y hoy tiene otra respuesta: aplicar
una decisión al mundo es de `engine/rondas.py`, que no está escrito. Hasta
entonces `registrar()` recibe la fracción ya calculada. El dueño del dato no
cambia; cambia quién le pasa el número.

Lo que este veto NO rechaza — límites declarados, no olvidos
------------------------------------------------------------
- **"Me como el costo".** Comparar el sobrecosto contra la caja exige el
  `aumento_pct` y el costo formal, y ninguno de los dos está en
  `contracts/decision.json`, congelado en H+4. Una propuesta de absorber pasa
  siempre. Es el chequeo que gana `engine/costos.py` cuando exista.
- **Legalidad.** El veto es material, no jurídico: no juzga si una jornada o un
  pago están permitidos, solo si la plata alcanza.
- **Estrategias sin números.** Lo que no trae detalle numérico no se puede
  costear, y lo que no se puede costear no se puede vetar. Pasa, y se sabe.

Determinismo: `vetar()` es una función pura, sin estado global y sin azar. No
consume el generador de `engine/seed.py` porque no hay nada que sortear.

Cómo verificarlo a mano
-----------------------
    python3 -m engine.veto        # imprime el catálogo de razones y su higiene
    python3 -m engine.test_veto   # corre los tests sin pytest
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Protocol

# Una ronda es un trimestre ([ADR 0005](../docs/adr/0005-el-reloj-de-la-simulacion.md)).
MESES_POR_RONDA = 3

# Canon de `docs/IDEA.md` §5.3 y §5.7 y compromiso público del review del PR #4:
# tras agotar los reintentos la estrategia terminal es `cumplir`, NO `absorber`.
# Viven acá para que haya un solo lugar donde cambiarlos; `behavior/` los importa.
MAX_REINTENTOS = 3
ESTRATEGIA_TERMINAL = "cumplir"


class Firma(Protocol):
    """Lo que el veto necesita leer de quien propone. Nada más.

    `behavior.arquetipos.Arquetipo` lo satisface estructuralmente: el motor no
    importa `behavior/` ni al revés se le exige heredar de nada.
    """

    id: str
    n_trabajadores: int
    flujo_caja: float
    costo_despido: float
    formal: bool


# --- Formato de números: la mitad de la higiene está acá ---------------------


def _num(x: float) -> str:
    """Entero con miles separados por punto: `1450000` -> `1.450.000`.

    El punto no es cosmético. `higiene.TERMINOS_PROHIBIDOS` rechaza cualquier
    corrida de cuatro dígitos por leerse como un año, y agrupar de a tres hace
    que ningún número —por grande que sea— deje cuatro dígitos seguidos.
    """
    return f"{x:,.0f}".replace(",", ".")


def _plata(x: float) -> str:
    """Un monto en unidades abstractas. La moneda real jamás sale hacia el modelo."""
    return f"{_num(x)} u"


# --- El estado vivo ----------------------------------------------------------


@dataclass
class EstadoVivo:
    """La fracción de cada planta que está fuera de regla y la que sigue empleada.

    Ambas son fracciones en [0,1] por `arquetipo_id`, medidas **al empezar** la
    ronda. `fraccion_empleada` es acumulativa contra la línea base sin política,
    que es como `engine/MODELO.md` define `empleo_relativo`: arranca en 1,0 y
    solo baja.
    """

    fraccion_informal: dict[str, float]
    fraccion_empleada: dict[str, float]

    @classmethod
    def inicial(cls, firmas: list[Firma]) -> EstadoVivo:
        """El mundo antes de la primera decisión: nadie ha despedido a nadie."""
        return cls(
            fraccion_informal={f.id: (0.0 if f.formal else 1.0) for f in firmas},
            fraccion_empleada={f.id: 1.0 for f in firmas},
        )

    def fraccion_informal_previa(self, arquetipo_id: str) -> float:
        """Lo que `behavior/rondas.py` pide en su PUNTO DE SUTURA."""
        return self.fraccion_informal[arquetipo_id]

    def fraccion_empleada_previa(self, arquetipo_id: str) -> float:
        return self.fraccion_empleada[arquetipo_id]

    def registrar(
        self, arquetipo_id: str, *, fraccion_informal: float, fraccion_empleada: float
    ) -> None:
        """Cierra la ronda para un arquetipo. Ambas fracciones se acotan a [0,1]."""
        self.fraccion_informal[arquetipo_id] = _acotar(fraccion_informal)
        self.fraccion_empleada[arquetipo_id] = _acotar(fraccion_empleada)


def _acotar(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


# --- Las razones, en un solo lugar para poder revisarlas todas ---------------

_RAZONES: dict[str, str] = {
    "detalle_ilegible": (
        "el número que diste en {campo} no se puede leer como cantidad, "
        "así que no hay forma de aplicarlo"
    ),
    "conteo_negativo": "{campo} llegó en negativo y no existe una planta negativa",
    "despido_sobre_planta": (
        "tu planta tiene {planta} trabajadores y la salida propone dejar sin "
        "empleo a {pedidos}: no hay tantos"
    ),
    "despido_sin_caja": (
        "no alcanza para las indemnizaciones: dejar sin empleo a {pedidos} "
        "cuesta {costo} y la caja del trimestre es {caja}"
    ),
    "informalizacion_sobre_planta": (
        "solo {en_regla} de tus trabajadores están hoy en regla y la salida "
        "propone sacar de regla a {pedidos}: no hay tantos"
    ),
    "porcentaje_fuera_de_rango": (
        "{campo} tiene que quedar entre 0 y 100 y llegó en {valor}"
    ),
}

# Los dos porcentajes que se acotan. `aumento_precios_pct` queda fuera a
# propósito: subir un precio más del 100% es caro, no imposible, y el veto es
# de factibilidad material, no de sensatez comercial.
_PORCENTAJES_ACOTADOS = ("reduccion_horas_pct", "reduccion_margen_pct")

FACTIBLE: dict[str, Any] = {"factible": True, "razon": None}


def _infactible(clave: str, **campos: Any) -> dict[str, Any]:
    return {"factible": False, "razon": _RAZONES[clave].format(**campos)}


# --- El veto -----------------------------------------------------------------


def _entero(valor: Any) -> int | None:
    """`None` si el campo no viene; `NotImplemented` si vino pero es ilegible."""
    if valor is None:
        return None
    try:
        return int(valor)
    except (TypeError, ValueError):
        return NotImplemented


def _real(valor: Any) -> float | None:
    if valor is None:
        return None
    try:
        return float(valor)
    except (TypeError, ValueError):
        return NotImplemented


def caja_de_la_ronda(firma: Firma) -> float:
    """La plata con la que la firma cuenta para pagar un desembolso del trimestre.

    # SUPUESTO: S8 — `flujo_caja` es un flujo MENSUAL (así lo construye
    # `behavior/arquetipos.py`: 0,18 × nómina del mes) y la ronda es un trimestre
    # (ADR 0005), así que la caja del periodo son tres meses de ese flujo. Se
    # asume además que la firma puede destinarla completa a un desembolso de una
    # vez: sin reservas acumuladas y sin crédito. Es un supuesto de dirección
    # conocida — sin crédito el veto es MÁS estricto, luego sobreestima los vetos
    # y por lo tanto los fallbacks. Sensibilidad a cargo de R5.
    """
    return firma.flujo_caja * MESES_POR_RONDA


def planta_viva(firma: Firma, estado: EstadoVivo | None = None) -> tuple[int, int]:
    """`(empleados hoy, de esos cuántos están en regla)`.

    Sin `estado` se responde con el estado INICIAL de la firma, que es lo
    correcto en la ronda 0 y en cualquier uso suelto del veto.

    # SUPUESTO: S9 — la planta se redondea al entero más cercano. Un arquetipo de
    # 3 trabajadores con 50% fuera de regla tiene 2 en regla, no 1,5. El
    # redondeo mueve el veto en el margen de las plantas chicas; con las plantas
    # de la GEIH (mediana 3) es el caso común, así que se declara en vez de
    # esconderse.
    """
    if estado is None:
        frac_informal = 0.0 if firma.formal else 1.0
        frac_empleada = 1.0
    else:
        frac_informal = estado.fraccion_informal_previa(firma.id)
        frac_empleada = estado.fraccion_empleada_previa(firma.id)
    empleados = int(round(firma.n_trabajadores * frac_empleada))
    en_regla = int(round(empleados * (1.0 - frac_informal)))
    return empleados, en_regla


def vetar(
    decision: dict[str, Any],
    firma: Firma,
    estado: EstadoVivo | None = None,
) -> dict[str, Any]:
    """El veredicto de factibilidad de una propuesta. Función pura.

    Los tres argumentos posicionales son los de `MODELO.md` (`decision`, `firma`)
    más el estado vivo. Con dos argumentos la firma coincide con el `Protocol
    Veto` que consume `behavior/capa.py`, así que se puede pasar tal cual —
    aunque lo que se pasa en una corrida real es el cierre de `veto_del_motor()`,
    que lleva el estado adentro.
    """
    detalle = decision.get("detalle")
    if not isinstance(detalle, dict):
        detalle = {}

    empleados, en_regla = planta_viva(firma, estado)

    # 1. Los porcentajes acotados: reducir más del todo, o menos que nada.
    for campo in _PORCENTAJES_ACOTADOS:
        pct = _real(detalle.get(campo))
        if pct is NotImplemented:
            return _infactible("detalle_ilegible", campo=campo)
        if pct is not None and not (0.0 <= pct <= 100.0):
            return _infactible("porcentaje_fuera_de_rango", campo=campo, valor=_num(pct))

    # 2. Dejar sin empleo: no a más de los que hay, y con qué indemnizar.
    despedidos = _entero(detalle.get("empleados_a_despedir"))
    if despedidos is NotImplemented:
        return _infactible("detalle_ilegible", campo="empleados_a_despedir")
    if despedidos is not None:
        if despedidos < 0:
            return _infactible("conteo_negativo", campo="empleados_a_despedir")
        if despedidos > empleados:
            return _infactible(
                "despido_sobre_planta",
                planta=_num(empleados),
                pedidos=_num(despedidos),
            )
        costo = despedidos * firma.costo_despido
        caja = caja_de_la_ronda(firma)
        if costo > caja:
            return _infactible(
                "despido_sin_caja",
                pedidos=_num(despedidos),
                costo=_plata(costo),
                caja=_plata(caja),
            )

    # 3. Sacar de regla: solo se puede sacar a quien está adentro.
    informalizados = _entero(detalle.get("empleados_a_informalizar"))
    if informalizados is NotImplemented:
        return _infactible("detalle_ilegible", campo="empleados_a_informalizar")
    if informalizados is not None:
        if informalizados < 0:
            return _infactible("conteo_negativo", campo="empleados_a_informalizar")
        if informalizados > en_regla:
            return _infactible(
                "informalizacion_sobre_planta",
                en_regla=_num(en_regla),
                pedidos=_num(informalizados),
            )

    return dict(FACTIBLE)


def veto_del_motor(estado: EstadoVivo) -> Callable[[dict[str, Any], Firma], dict[str, Any]]:
    """El veto con el estado vivo adentro, listo para `behavior/rondas.correr()`.

    Es lo que se le pasa al parámetro `veto=` en lugar de los dobles de prueba.
    """

    def veto(decision: dict[str, Any], firma: Firma) -> dict[str, Any]:
        return vetar(decision, firma, estado)

    return veto


# --- El catálogo, para poder revisar TODAS las razones -----------------------

# Valores adversarios a propósito: cuatro dígitos exactos y montos que sin el
# agrupamiento de miles se leerían como un año.
_VALORES_ADVERSARIOS: dict[str, Any] = {
    "campo": "empleados_a_despedir",
    "planta": _num(2026),
    "pedidos": _num(1990),
    "costo": _plata(1_999_000),
    "caja": _plata(2020),
    "en_regla": _num(0),
    "valor": _num(2000),
}


def razones_posibles() -> list[str]:
    """Todas las razones que este veto puede emitir, rendidas con números duros.

    Es la lista completa por construcción: si alguien agrega una razón a
    `_RAZONES`, aparece acá y el test de higiene la revisa sin tocarlo.
    """
    return [
        plantilla.format(**_VALORES_ADVERSARIOS) for plantilla in _RAZONES.values()
    ]


if __name__ == "__main__":  # pragma: no cover
    import sys

    try:
        from behavior import higiene
    except ImportError:  # pragma: no cover
        print("no se pudo importar behavior.higiene; solo se imprime el catálogo")
        higiene = None

    sucias = 0
    for razon in razones_posibles():
        hallazgos = higiene.revisar(razon) if higiene else []
        if hallazgos:
            sucias += 1
            print(f"SUCIA  {razon}")
            for patron, motivo, frag in hallazgos:
                print(f"       [{patron}] {motivo}\n         {frag}")
        else:
            print(f"limpia {razon}")
    total = len(razones_posibles())
    print(f"\n{total - sucias}/{total} razones del veto pasan la higiene")
    sys.exit(1 if sucias else 0)
