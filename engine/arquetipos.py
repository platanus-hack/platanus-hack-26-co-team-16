"""Muestreo de estrategias desde arquetipos hacia agentes individuales.

Qué modela: el último paso de la ADR 0002. La capa conductual decide una
  distribución de estrategias por arquetipo y el motor la reparte entre los
  agentes que ese arquetipo representa.
Entradas: un objeto con ``arquetipo_id`` y ``distribucion``, el tamaño de muestra
  y un ``numpy.random.Generator`` derivado por ``engine.seed.stream_nombrado``.
Salidas: una estrategia por agente, en una lista de longitud ``n``.
Supuestos: ver ``# SUPUESTO:`` junto al punto donde se aplica.

El motor no importa ``behavior``: ``ResultadoArquetipo`` satisface el protocolo
estructuralmente, pero cualquier doble con los mismos dos atributos sirve para
probar y reutilizar esta pieza.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Protocol

import numpy as np


class ArquetipoMuestreable(Protocol):
    """La superficie mínima que necesita el motor para repartir estrategias."""

    arquetipo_id: str
    distribucion: Mapping[str, float]


def muestrear(
    arq: ArquetipoMuestreable,
    n: int,
    rng: np.random.Generator,
) -> list[str]:
    """Sortea ``n`` estrategias según la distribución de ``arq``.

    Los pesos pueden ser conteos o probabilidades: se normalizan aquí. Las
    estrategias se ordenan antes del sorteo para que dos diccionarios con el
    mismo contenido produzcan lo mismo aunque hayan sido construidos en orden
    distinto.

    ``n`` es el número de agentes concretos que el llamador quiere asignar
    (por ejemplo, filas GEIH), no el factor de expansión poblacional. Esta
    función asigna estrategias; no replica ni inventa atributos individuales.

    El generador se recibe, no se crea. Quien llama debe derivarlo con una clave
    estable, por ejemplo ``stream_nombrado(seed, ronda, arq.arquetipo_id)``; así
    resolver arquetipos en paralelo no cambia qué stream consume cada uno.
    """
    if isinstance(n, bool) or not isinstance(n, (int, np.integer)):
        raise TypeError(f"n debe ser un entero; llegó {type(n).__name__}")
    if n < 0:
        raise ValueError(f"n debe ser no negativo; llegó {n}")
    if n == 0:
        return []
    if not isinstance(rng, np.random.Generator):
        raise TypeError("rng debe ser numpy.random.Generator")

    distribucion = arq.distribucion
    if not distribucion:
        raise ValueError(
            f"distribución vacía para el arquetipo {arq.arquetipo_id!r}: "
            "no hay estrategias que muestrear"
        )

    nombres = sorted(distribucion)
    try:
        pesos = np.asarray([distribucion[nombre] for nombre in nombres], dtype=float)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"la distribución del arquetipo {arq.arquetipo_id!r} contiene pesos ilegibles"
        ) from exc

    if not np.all(np.isfinite(pesos)):
        raise ValueError(
            f"la distribución del arquetipo {arq.arquetipo_id!r} contiene pesos no finitos"
        )
    if np.any(pesos < 0):
        raise ValueError(
            f"la distribución del arquetipo {arq.arquetipo_id!r} contiene pesos negativos"
        )
    peso_maximo = float(pesos.max())
    if peso_maximo <= 0:
        raise ValueError(
            f"la distribución del arquetipo {arq.arquetipo_id!r} no tiene peso positivo"
        )

    # Dividir primero por el máximo conserva las proporciones y evita que pesos
    # finitos grandes desborden al sumarse.
    pesos_escalados = pesos / peso_maximo
    probabilidades = pesos_escalados / float(pesos_escalados.sum())

    # SUPUESTO: la frecuencia relativa de las decisiones aceptadas del
    # arquetipo se interpreta como probabilidad conductual individual. Con
    # pocas paráfrasis esa probabilidad conserva incertidumbre lingüística:
    # aumentar `n` no la elimina ni autoriza a estrechar la banda.
    #
    # SUPUESTO: condicional a esa distribución, los agentes son sorteos iid.
    # Es más fuerte que intercambiabilidad: no modela un choque común ni
    # correlación residual dentro del arquetipo. Sus atributos GEIH siguen
    # siendo individuales y no se inventan aquí.
    indices = rng.choice(len(nombres), size=int(n), p=probabilidades)
    return [nombres[int(indice)] for indice in indices]
