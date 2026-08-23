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

Lo que hace divergir dos trayectorias dentro de UNA corrida es la PARÁFRASIS del
prompt: esta capa fija una paráfrasis por trayectoria y deja el resto igual.
(Desde el 23-ago el seed TAMBIÉN entra al prompt —elige el contexto de cada
firma en `behavior/contexto.py`, ver `SEED_EFECTO`—, pero es constante dentro de
una corrida, así que no es lo que separa a estas N.) Es el mismo mecanismo con el que
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

import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable

from behavior.arquetipos import Arquetipo
from behavior.cliente import parafrasis as _parafrasis
from behavior.presupuesto import PresupuestoAgotado
from behavior.rondas import Ronda, consolidar_trayectorias, correr

# Cuántas trayectorias hacen una banda publicable. No es una perilla de gusto:
# `AGENTS.md` fija que la barra de error sale de N>=5 paráfrasis del prompt y
# JAMÁS de temperatura. Y sólo hay 5 archivos en `behavior/prompts/parafrasis/`,
# así que 5 es también el techo real de hoy.
N_TRAYECTORIAS = 5


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
    con `correr()`: cada llamada baja su redacción por `parafrasis_fija`, que la
    neutraliza de manera local y sin tocar globales. Una trayectoria está
    DEFINIDA por una sola paráfrasis, así que pedir N adentro no tiene sentido
    (ver `api.servidor.PARAFRASIS_EFECTO`). La banda que se publica es la de
    entre trayectorias, que reemplazó a la intra-ronda.

    Las tres costuras (`al_*`) llevan el índice de trayectoria adelante para que
    quien las escuche pueda decir en cuál va sin adivinarlo por el orden. Como
    ahora se disparan desde varios hilos, comparten un lock: el consumidor puede
    reordenar por índice, pero nunca recibe dos escrituras SSE entrelazadas.

    El mismo `cliente` se reusa en las N: no guarda estado por corrida, y así el
    presupuesto y la caché se acumulan solos sobre el total, que es lo que hace
    que el tope duro sea de la corrida entera.
    """
    # Si faltan archivos de paráfrasis esto revienta acá, antes de gastar un
    # dólar, y con el mensaje de `parafrasis()` que dice cuántas hay.
    disponibles = _parafrasis(n_trayectorias)

    lock_callbacks = threading.Lock()

    def _publicar(callback: Callable[..., None] | None, *args: Any) -> None:
        if callback is None:
            return
        with lock_callbacks:
            callback(*args)

    def _correr_trayectoria(i: int) -> list[Ronda] | None:
        _publicar(al_empezar_trayectoria, i, n_trayectorias)
        try:
            return correr(
                arquetipos,
                cliente,
                aumento_pct=aumento_pct,
                rondas_totales=rondas_totales,
                seed=seed,
                simulacion_id=f"{simulacion_id}-t{i}",
                veto=None,
                n_parafrasis=n_parafrasis,
                parafrasis_fija=disponibles[i % len(disponibles)],
                cobertura_llm=cobertura_llm,
                tasa_informalidad_inicial=tasa_informalidad_inicial,
                al_decidir_arquetipo=(
                    None
                    if al_decidir_arquetipo is None
                    else lambda r, aid, res, _i=i: _publicar(
                        al_decidir_arquetipo, _i, r, aid, res
                    )
                ),
                al_terminar_ronda=(
                    None
                    if al_terminar_ronda is None
                    else lambda ronda, _i=i: _publicar(
                        al_terminar_ronda, _i, ronda
                    )
                ),
            )
        except PresupuestoAgotado:
            # El corte es por trayectoria: varias pueden encontrar el mismo tope
            # mientras están en vuelo. Cada una declara su fracaso con `None` y
            # las demás terminan; solo las corridas completas entran a la banda.
            return None

    with ThreadPoolExecutor(max_workers=n_trayectorias) as pool:
        # `pool.map` devuelve en orden de ENTRADA aunque las llamadas terminen en
        # otro orden. Esa propiedad es parte del determinismo: consolidar jamás
        # puede ver el orden del scheduler ni el de llegada de la red.
        corridas_por_indice = list(
            pool.map(_correr_trayectoria, range(n_trayectorias))
        )

    corridas = [corrida for corrida in corridas_por_indice if corrida is not None]

    return consolidar_trayectorias(corridas), len(corridas)
