"""Las N trayectorias completas de las que sale la banda que se PUBLICA.

Qué modela: nada. Orquesta N corridas independientes de `behavior.rondas.correr()`
  y las consolida con `behavior.rondas.consolidar_trayectorias()`.
Entradas: la grilla de arquetipos y los parámetros de la corrida.
Salidas: la trayectoria MEDIANA, con su `banda` = dispersión entre las N.

Por qué existe
--------------
`contracts/ronda.json` declara `banda.tipo = "entre_trayectorias"` y la API
entregaba otra cosa: la dispersión de las paráfrasis DENTRO de una ronda,
partiendo todas del mismo estado. No es un matiz. Las dos miden cosas distintas
y dan números distintos —0,0 pp contra 22,5 pp en la corrida que midió el
equipo, según el docstring de `banda_entre_trayectorias()`—, así que la API
estaba fuera de su propio contrato y afirmando una precisión que el modelo no
tiene. Esta capa la pone dentro.

Lo que hace divergir dos trayectorias es la PARÁFRASIS del prompt, no el seed:
la caché se indexa por el prompt y el prompt no lleva seed (ver `SEED_EFECTO` en
`api/servidor.py`, medido). Es el mismo mecanismo con el que
`scripts/barrido_politicas.py` mide la banda del barrido; acá entra al camino
del producto, que es donde faltaba.

Qué cuesta
----------
N veces una corrida. Con la grilla real y cobertura 0,8 son 31 celdas de 81 ×
3 rondas con LLM = 93 llamadas por trayectoria, o sea 465 con N=5. Es
exactamente lo mismo que costaría pedir `n_parafrasis=5` en una sola
trayectoria, que compra la banda angosta: mismo dinero, una es honesta y la otra
no.

El tope de gasto es UNO para toda la corrida y no uno por trayectoria. Si se
agota a mitad de camino se consolida con las que alcanzaron a terminar y se
declara cuántas fueron: con menos de 2 la banda ya no es la de entre
trayectorias, y `banda.tipo` lo dice sin que nadie tenga que preguntarlo.
"""

from __future__ import annotations

import contextlib
from typing import Any, Callable, Iterator

import behavior.capa as _capa
from behavior.arquetipos import Arquetipo
from behavior.cliente import parafrasis as _parafrasis
from behavior.presupuesto import PresupuestoAgotado
from behavior.rondas import Ronda, consolidar_trayectorias, correr

# Cuántas trayectorias hacen una banda publicable. No es una perilla de gusto:
# `AGENTS.md` fija que la barra de error sale de N>=5 paráfrasis del prompt y
# JAMÁS de temperatura. Y sólo hay 5 archivos en `behavior/prompts/parafrasis/`,
# así que 5 es también el techo real de hoy.
N_TRAYECTORIAS = 5


@contextlib.contextmanager
def _parafrasis_fijada(indice: int, disponibles: list[str]) -> Iterator[None]:
    """Fija en QUÉ paráfrasis corre esta trayectoria, y la restaura al salir.

    Acá está la deuda, y es la razón de que las N vayan EN SERIE: hoy la única
    forma de elegir cuál paráfrasis usa una corrida es reemplazar
    `behavior.capa.parafrasis`, que es un global del módulo. Es lo mismo que hace
    `scripts/barrido_politicas.py`, así que el truco no es nuevo ni es mío; lo
    que sí es nuevo es que acá corre en el camino del producto.

    Dos hilos con parches distintos se pisarían, así que no se puede
    paralelizar. Y duele, porque estas llamadas son I/O contra la API: el día que
    `behavior/` acepte el índice de paráfrasis por parámetro, este bloque se
    borra, las N corren a la vez y el tiempo total vuelve a ser el de UNA
    corrida. Es un pedido chico y abierto a R3, no un rediseño.

    Y hay un efecto de borde que se declara acá porque no se ve en ningún otro
    lado: la lambda **ignora el `n` que le pasan**, así que río abajo
    `behavior/capa.py` da una sola vuelta pase lo que pase y el parámetro
    `n_parafrasis` queda NEUTRALIZADO mientras este contexto esté activo. No es
    un descuido que haya que arreglar: una trayectoria está DEFINIDA por su
    paráfrasis, así que pedir N paráfrasis adentro de una trayectoria no quiere
    decir nada. Se declara en `api.servidor.PARAFRASIS_EFECTO` y viaja en el
    evento `inicio`, para que nadie mueva esa perilla, no vea nada y saque una
    conclusión sobre el modelo.
    """
    original = _capa.parafrasis
    elegida = disponibles[indice % len(disponibles)]
    _capa.parafrasis = lambda n=1, _p=elegida: [_p]
    try:
        yield
    finally:
        _capa.parafrasis = original


def correr_consolidada(
    arquetipos: list[Arquetipo],
    cliente: Any,
    *,
    n_trayectorias: int,
    aumento_pct: float,
    rondas_totales: int,
    seed: int,
    simulacion_id: str,
    cobertura_llm: float | None,
    tasa_informalidad_inicial: float,
    n_parafrasis: int = 1,
    al_decidir_arquetipo: Callable[[int, int, str, Any], None] | None = None,
    al_terminar_ronda: Callable[[int, Ronda], None] | None = None,
    al_empezar_trayectoria: Callable[[int, int], None] | None = None,
) -> tuple[list[Ronda], int]:
    """Corre N trayectorias completas y devuelve (la mediana, cuántas corrieron).

    Cada trayectoria es independiente y arranca fijada a una paráfrasis distinta,
    así que divergen desde la ronda 1 y cada una arrastra su propia historia. Eso
    es lo que la hace más fuerte que `n_parafrasis=N`, donde las N variantes
    parten todas del mismo estado previo y por construcción se parecen más.

    `n_parafrasis` no hace nada acá y se recibe solo por compatibilidad de firma
    con `correr()`: `_parafrasis_fijada()` lo neutraliza, y eso es coherente y no
    un bug (ver su docstring y `api.servidor.PARAFRASIS_EFECTO`). La banda que se
    publica es la de entre trayectorias, que es la que reemplazó a la
    intra-ronda.

    Las tres costuras (`al_*`) llevan el índice de trayectoria adelante para que
    quien las escuche pueda decir en cuál va sin adivinarlo por el orden.

    El mismo `cliente` se reusa en las N: no guarda estado por corrida, y así el
    presupuesto y la caché se acumulan solos sobre el total, que es lo que hace
    que el tope duro sea de la corrida entera.
    """
    # Si faltan archivos de paráfrasis esto revienta acá, antes de gastar un
    # dólar, y con el mensaje de `parafrasis()` que dice cuántas hay.
    disponibles = _parafrasis(n_trayectorias)

    corridas: list[list[Ronda]] = []
    for i in range(n_trayectorias):
        if al_empezar_trayectoria is not None:
            al_empezar_trayectoria(i, n_trayectorias)
        try:
            with _parafrasis_fijada(i, disponibles):
                corridas.append(
                    correr(
                        arquetipos,
                        cliente,
                        aumento_pct=aumento_pct,
                        rondas_totales=rondas_totales,
                        seed=seed,
                        simulacion_id=f"{simulacion_id}-t{i}",
                        veto=None,
                        n_parafrasis=n_parafrasis,
                        cobertura_llm=cobertura_llm,
                        tasa_informalidad_inicial=tasa_informalidad_inicial,
                        al_decidir_arquetipo=(
                            None
                            if al_decidir_arquetipo is None
                            else lambda r, aid, res, _i=i: al_decidir_arquetipo(
                                _i, r, aid, res
                            )
                        ),
                        al_terminar_ronda=(
                            None
                            if al_terminar_ronda is None
                            else lambda ronda, _i=i: al_terminar_ronda(_i, ronda)
                        ),
                    )
                )
        except PresupuestoAgotado:
            # Corte duro a mitad de camino. Se publica lo que alcanzó a correr y
            # `n_efectivas` lo declara: preferimos una banda sobre 3 trayectorias
            # dicha en voz alta que una sobre 5 que no se pagó.
            break

    return consolidar_trayectorias(corridas), len(corridas)
