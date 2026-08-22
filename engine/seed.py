"""El determinismo del motor: un seed, y sub-streams que no dependen del orden.

Qué modela: nada. Es la plomería que hace que dos corridas con el mismo seed den
  el mismo resultado ([ADR 0009](../docs/adr/0009-frontera-del-determinismo.md)).
Entradas: un entero.
Salidas: `numpy.random.Generator` independientes, uno por ronda y, si hace falta,
  uno por (ronda, nombre).
Supuestos: ninguno sobre el mundo. Los límites del determinismo están declarados
  abajo y son de máquina, no de modelo.

Por qué existe, medido y no supuesto
------------------------------------
Hoy el `seed` de `behavior/` es **decorativo**: seed 42 y seed 99 producen la
misma salida salvo la etiqueta, porque nada en el bucle de rondas es estocástico
y el único punto que sí lo es (`muestrear()`) no lo llama nadie todavía. El
determinismo que se observa hoy no lo da una semilla: lo da la caché en disco.
Eso es el nivel 2 de la ADR 0009, no el nivel 1.

Este archivo es el nivel 1: cuando el muestreo hacia agentes individuales entre
—y con él el dato A3, el mapa distributivo—, la aleatoriedad ya tiene por dónde
pasar y tiene cómo verificarse.

La decisión: derivar por clave, no por `spawn()` secuencial
------------------------------------------------------------
`SeedSequence.spawn(n)` es la forma que sugiere numpy, pero **es stateful**: el
padre lleva la cuenta de cuántos hijos entregó, así que el stream que le toca a
la ronda 2 depende de cuántas veces se llamó antes. Con los arquetipos
resolviéndose en paralelo (`ThreadPoolExecutor`, 8 hilos en `behavior/rondas.py`)
eso es una carrera: el resultado dependería del orden de terminación.

Acá cada stream se deriva **directo de su coordenada**, con `spawn_key`:

    SeedSequence(seed, spawn_key=(ronda,))

Es puro: la misma coordenada da el mismo stream, se pida cuando se pida y se
pida desde donde se pida. El orden de recorrido no puede filtrarse al resultado,
que es justo lo que un revisor va a intentar romper corriendo con y sin
paralelismo.

**Nunca `hash()` de Python** para derivar de un nombre: está salado por proceso
(`PYTHONHASHSEED`), así que dos corridas del mismo comando darían streams
distintos. Se usa blake2b, que es estable entre procesos y entre máquinas.

Qué NO garantiza, dicho antes de que lo pregunten
-------------------------------------------------
El determinismo es **misma máquina, mismas versiones** (ADR 0009). Operaciones
vectorizadas en punto flotante pueden diferir en el último bit entre versiones de
BLAS o entre arquitecturas. Prometer "bit a bit en cualquier computador" sería
falso, y es innecesario: ninguna conclusión del proyecto depende del último bit.
`manifiesto()` imprime lo que hace falta para comparar dos corridas de verdad.

Y el nivel 1 es solo el motor: la corrida completa además necesita la misma
caché de decisiones, que es de `behavior/`.

Cómo verificarlo a mano
-----------------------
    python3 -m engine.seed        # el manifiesto y la prueba de independencia
    python3 -m engine.test_seed   # los tests sin pytest
"""

from __future__ import annotations

import hashlib
import platform
import sys
from typing import Any

import numpy as np

# El seed del ejemplo congelado de `contracts/ronda.json`. Es un default, no un
# número mágico: cualquier entero sirve y la corrida lo imprime.
SEED_POR_DEFECTO = 42


def _clave(nombre: object) -> int:
    """Un entero estable a partir de un nombre. Estable ENTRE PROCESOS.

    `hash()` de Python no sirve acá: está salado por proceso, así que la misma
    corrida dos veces daría streams distintos y el bug sería invisible hasta que
    alguien comparara dos ejecuciones completas.
    """
    crudo = str(nombre).encode("utf-8")
    return int.from_bytes(hashlib.blake2b(crudo, digest_size=8).digest(), "big")


def semilla_raiz(seed: int = SEED_POR_DEFECTO) -> np.random.SeedSequence:
    """La raíz de la que cuelga todo el azar de una corrida."""
    return np.random.SeedSequence(int(seed))


def generador_raiz(seed: int = SEED_POR_DEFECTO) -> np.random.Generator:
    """El generador de la corrida. Para lo que no pertenece a ninguna ronda."""
    return np.random.default_rng(semilla_raiz(seed))


def stream_de_ronda(seed: int, ronda: int) -> np.random.Generator:
    """El generador de una ronda, derivado de su número y no de su turno.

    Dos rondas distintas dan streams independientes; la misma ronda pedida dos
    veces da el mismo stream. No hay estado compartido, así que no hay carrera.
    """
    if ronda < 0:
        raise ValueError(f"no existe la ronda {ronda}")
    return np.random.default_rng(
        np.random.SeedSequence(int(seed), spawn_key=(int(ronda),))
    )


def stream_nombrado(seed: int, ronda: int, *nombre: object) -> np.random.Generator:
    """El generador de una coordenada con nombre, por ejemplo un arquetipo.

    Es lo que necesita el muestreo hacia agentes individuales: cada arquetipo
    saca su propio azar sin que importe en qué hilo le tocó correr.
    """
    if ronda < 0:
        raise ValueError(f"no existe la ronda {ronda}")
    if not nombre:
        raise ValueError("`stream_nombrado` sin nombre es `stream_de_ronda`")
    claves = tuple(_clave(parte) for parte in nombre)
    return np.random.default_rng(
        np.random.SeedSequence(int(seed), spawn_key=(int(ronda), *claves))
    )


def manifiesto(seed: int = SEED_POR_DEFECTO) -> dict[str, Any]:
    """Todo lo que hay que igualar para que dos corridas sean comparables.

    Es la mitad del contrato de la ADR 0009 que le toca al motor: el seed y las
    versiones. La otra mitad —el hash de la caché de decisiones— es de
    `behavior/`, y `make run` imprime las dos juntas.
    """
    return {
        "seed": int(seed),
        "python": platform.python_version(),
        "numpy": np.__version__,
        "plataforma": f"{platform.system()}-{platform.machine()}",
        "implementacion": platform.python_implementation(),
    }


if __name__ == "__main__":  # pragma: no cover
    print("Manifiesto de la corrida (ADR 0009, la mitad que es del motor)")
    for clave, valor in manifiesto().items():
        print(f"  {clave:>16} : {valor}")

    print("\nLos streams no dependen del orden en que se pidan")
    directo = [int(stream_de_ronda(SEED_POR_DEFECTO, k).integers(0, 10**9)) for k in range(4)]
    alreves = [int(stream_de_ronda(SEED_POR_DEFECTO, k).integers(0, 10**9)) for k in (3, 2, 1, 0)]
    print(f"  rondas 0..3 en orden  : {directo}")
    print(f"  rondas 3..0 al revés  : {list(reversed(alreves))}")
    print(f"  ¿iguales?             : {directo == list(reversed(alreves))}")

    print("\nY el seed sí siembra: 42 contra 99")
    for s in (42, 99):
        print(f"  seed {s:>3} -> {[int(stream_de_ronda(s, k).integers(0, 10**9)) for k in range(4)]}")
    sys.exit(0)
