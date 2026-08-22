"""Arquetipos: la unidad a la que se le llama al LLM, y el muestreo hacia agentes.

Qué modela: el agrupamiento sector × tamaño × formalidad × tramo de ingreso
  ([ADR 0002](../docs/adr/0002-llm-por-arquetipo.md)) y el muestreo determinista
  de miles de agentes desde la distribución de estrategias de su arquetipo.
Entradas: `data/poblacion.parquet` (esquema `contracts/agente.json`), o el grid
  falso de `arquetipos_falsos()` mientras ese archivo no exista.
Salidas: lista de `Arquetipo`; y estrategias por agente vía `muestrear()`.
Supuestos: ver `# SUPUESTO:` en el cuerpo.

Esta es la pieza de la verificación V10 (`docs/PLAN.md` §6). Ver el veredicto en
`behavior/README.md`: se adoptó la idea de AgentTorch, no la dependencia.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

# SUPUESTO: cuatro sectores y tres tramos de tamaño. Son los cortes con los que
# la GEIH tiene celdas pobladas; Alejo confirma o corrige contra el parquet real
# en H+8. Cambiar esto cambia el número de llamadas al LLM, no el motor.
SECTORES = ("comercio", "servicios", "industria", "construccion")
TAMANOS = {"micro": 3, "pequena": 10, "mediana": 45}

# `tamano_empresa` en `contracts/agente.json` es el código 1-10 de la variable
# P3069 de la GEIH, NO un número de empleados. La equivalencia la documenta
# Alejo en `contracts/README.md`; acá se traduce al punto medio de cada rango
# porque el motor necesita un headcount para calcular caja e indemnizaciones.
# SUPUESTO: el código 10 es "201 o más" — rango abierto, sin punto medio. Se usa
# 300 y es el primer parámetro de esta capa que R5 debe someter a sensibilidad.
EMPLEADOS_POR_CODIGO = {
    1: 1,    # trabaja solo
    2: 3,    # 2-3
    3: 5,    # 4-5
    4: 8,    # 6-10
    5: 15,   # 11-19
    6: 25,   # 20-30
    7: 40,   # 31-50
    8: 75,   # 51-100
    9: 150,  # 101-200
    10: 300,  # 201+  <- SUPUESTO, ver arriba
}
TRAMOS_INGRESO = ("t1", "t2")  # t1 = pegado al piso salarial, t2 = por encima


@dataclass(frozen=True)
class Arquetipo:
    """Un grupo de agentes intercambiables en su conducta (no en sus números)."""

    id: str
    sector: str
    tamano: str
    formal: bool
    tramo_ingreso: str
    n_trabajadores: int
    ingreso_por_trabajador: float
    flujo_caja: float
    costo_despido: float
    peso: float = 1.0  # suma de factores de expansión: a cuánta gente representa

    @property
    def situacion_planta(self) -> str:
        return "toda formal" if self.formal else "toda informal"


def arquetipos_falsos() -> list[Arquetipo]:
    """El grid completo con números inventados, para construir antes de H+8.

    Los números NO son datos: son un andamio para que el motor de Manuel y esta
    capa se puedan enchufar antes de que exista `data/poblacion.parquet`. Se
    reemplazan por `desde_poblacion()` en cuanto Alejo entregue.
    """
    fuera = []
    for sector in SECTORES:
        for tamano, n in TAMANOS.items():
            for formal in (True, False):
                for tramo in TRAMOS_INGRESO:
                    # SUPUESTO: números de andamio, no observados. t1 = 1.0x el
                    # piso, t2 = 1.6x; el informal paga 0.85x de lo que paga el
                    # formal; el flujo de caja libre es 0.18x la nómina.
                    base = 1_000_000.0 * (1.0 if tramo == "t1" else 1.6)
                    ingreso = base * (0.85 if not formal else 1.0)
                    nomina = ingreso * n
                    fuera.append(
                        Arquetipo(
                            id=f"{sector[:3]}-{tamano[:4]}-{'for' if formal else 'inf'}-{tramo}",
                            sector=sector,
                            tamano=tamano,
                            formal=formal,
                            tramo_ingreso=tramo,
                            n_trabajadores=n,
                            ingreso_por_trabajador=ingreso,
                            flujo_caja=nomina * 0.18,
                            costo_despido=ingreso * 1.5,
                            peso=1.0,
                        )
                    )
    return fuera


def desde_poblacion(ruta: str | Path) -> list[Arquetipo]:
    """Construye los arquetipos reales agrupando `data/poblacion.parquet`.

    Espera el esquema de `contracts/agente.json`. Cada arquetipo toma la
    **mediana** de sus miembros (no la media: la cola alta de ingresos de la
    GEIH arrastra la media) y su peso es la suma de factores de expansión.
    """
    import pandas as pd  # local: solo se necesita cuando ya hay datos reales

    df = pd.read_parquet(ruta)
    faltan = {"sector", "tamano_empresa", "ingreso_mensual_cop", "formal"} - set(df.columns)
    if faltan:
        raise ValueError(f"{ruta} no cumple contracts/agente.json; faltan: {sorted(faltan)}")

    # `tamano_empresa` es un CÓDIGO ORDINAL 1-10 del DANE (P3069), no un número
    # de empleados. Está documentado en `contracts/README.md`. Tratarlo como
    # headcount metía a una firma de "201+ personas" con 10 trabajadores, y de
    # ahí al flujo de caja que el veto usa como techo duro.
    n_trab = df["tamano_empresa"].map(EMPLEADOS_POR_CODIGO)
    if n_trab.isna().any():
        malos = sorted(df.loc[n_trab.isna(), "tamano_empresa"].unique())
        raise ValueError(f"{ruta}: códigos de tamano_empresa fuera de 1-10: {malos}")

    df = df.assign(
        _n_trab=n_trab,
        _tamano=pd.cut(
            n_trab, bins=[0, 10, 50, 10**9], labels=list(TAMANOS)
        ).astype(str),
        # SUPUESTO: el corte t1/t2 es la mediana de ingreso de la muestra. Se
        # reemplaza por el piso salarial observado cuando R5 entregue la serie (V4).
        _tramo=np.where(df["ingreso_mensual_cop"] <= df["ingreso_mensual_cop"].median(), "t1", "t2"),
        _peso=df.get("factor_expansion", 1.0),
    )

    fuera = []
    for (sector, tamano, formal, tramo), g in df.groupby(
        ["sector", "_tamano", "formal", "_tramo"], observed=True
    ):
        ingreso = float(g["ingreso_mensual_cop"].median())
        n = int(round(float(g["_n_trab"].median()))) or 1
        fuera.append(
            Arquetipo(
                id=f"{str(sector)[:3]}-{tamano[:4]}-{'for' if formal else 'inf'}-{tramo}",
                sector=str(sector),
                tamano=tamano,
                formal=bool(formal),
                tramo_ingreso=tramo,
                n_trabajadores=n,
                ingreso_por_trabajador=ingreso,
                # SUPUESTO: mismos coeficientes de andamio (0.18 y 1.5) hasta que
                # exista una fuente. Son los dos parámetros a los que R5 debe
                # correrle análisis de sensibilidad.
                flujo_caja=ingreso * n * 0.18,
                costo_despido=ingreso * 1.5,
                peso=float(g["_peso"].sum()),
            )
        )
    return fuera


# --- El muestreo: lo que AgentTorch habría dado, en 20 líneas -----------------


def _semilla(seed: int, *partes: object) -> int:
    """Semilla estable derivada de (seed, arquetipo, ronda). Mismo seed, mismo
    resultado — no depende del orden en que se recorran los arquetipos."""
    crudo = "|".join(str(p) for p in (seed, *partes)).encode()
    return int.from_bytes(hashlib.blake2b(crudo, digest_size=8).digest(), "big")


def muestrear(
    distribucion: dict[str, float],
    n: int,
    seed: int,
    *partes_semilla: object,
) -> list[str]:
    """Reparte `n` agentes entre las estrategias de su arquetipo, determinista.

    `distribucion` es {estrategia: peso}; los pesos se normalizan. Con un solo
    voto del LLM la distribución es degenerada (todos hacen lo mismo dentro del
    arquetipo) y la heterogeneidad viene de los atributos GEIH; con N paráfrasis
    la distribución tiene masa en varias estrategias y los agentes se reparten.
    Ese es exactamente el riesgo de "colapso de varianza" del plan (§10): se
    mide con `varianza_estrategias()` y se reporta, no se esconde.
    """
    if n <= 0:
        return []
    if not distribucion:
        raise ValueError("distribución vacía: el arquetipo no produjo ninguna estrategia")
    nombres = sorted(distribucion)  # orden estable => muestreo reproducible
    pesos = np.array([distribucion[k] for k in nombres], dtype=float)
    if pesos.sum() <= 0:
        raise ValueError(f"pesos no positivos en la distribución: {distribucion}")
    rng = np.random.default_rng(_semilla(seed, *partes_semilla))
    return [nombres[i] for i in rng.choice(len(nombres), size=n, p=pesos / pesos.sum())]


def varianza_estrategias(distribucion: dict[str, float]) -> float:
    """Entropía normalizada (0 = todos iguales, 1 = repartido parejo).

    Es el número que responde "¿el LLM colapsó la varianza?". Va a
    `VALIDATION.md` junto a la media, por la regla del plan §5.
    """
    pesos = np.array(list(distribucion.values()), dtype=float)
    pesos = pesos[pesos > 0]
    if len(pesos) <= 1:
        return 0.0
    p = pesos / pesos.sum()
    return float(-(p * np.log(p)).sum() / np.log(len(p)))
