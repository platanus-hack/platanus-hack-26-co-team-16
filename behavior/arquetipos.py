"""Arquetipos: la unidad a la que se le llama al LLM, y el muestreo hacia agentes.

Qué modela: el agrupamiento sector × tamaño × formalidad × tramo de ingreso
  ([ADR 0002](../docs/adr/0002-llm-por-arquetipo.md)) y el muestreo determinista
  de miles de agentes desde la distribución de estrategias de su arquetipo.
Entradas: `data/poblacion.parquet` (esquema `contracts/agente.json`), o el grid
  falso de `arquetipos_falsos()` mientras ese archivo no exista.
Salidas: lista de `Arquetipo`. El muestreo hacia agentes individuales es de
  `engine/arquetipos.py` (ver `_muestrear_local` al final de este archivo).
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

    # --- Lo que aporta `data/empresas.parquet` (C1) --------------------------
    # Estos tres campos existen porque el andamio los inventaba y el dato real
    # los tiene celda por celda. Conservan un default para que `arquetipos_falsos()`
    # y cualquier doble de prueba sigan construyendo sin pasarlos.

    # Factor prestacional de ESTA celda (sector × exoneración del Art. 114-1),
    # entre 1,3835 y 1,5829. El promedio 1,40 que usaba `ablacion.py` para toda
    # la población borraba justo la diferencia que decide el signo del candado 4:
    # el micro-empleador no exonerado paga ~13,5 puntos más que el exonerado.
    factor_prestacional: float = 1.40
    # Fracción de la planta FUERA de regla al empezar (1 − share_formal). Es
    # continua: el corte binario `formal` metía a una celda con 55% de formalidad
    # entera de un lado. `None` = derivar de `formal`, que es lo que hace el andamio.
    fraccion_informal_inicial: float | None = None
    # A cuántas FIRMAS representa esta celda (no a cuántos trabajadores: eso es
    # `peso`). Es el universo que `engine/fiscalizacion.py` reparte entre evasores,
    # y sin él la capa tenía que inventarse una capacidad (el 0,02 de C2).
    n_empresas: float = 0.0

    @property
    def fraccion_informal_inicio(self) -> float:
        """El estado inicial de la planta, continuo, con el binario de respaldo."""
        if self.fraccion_informal_inicial is None:
            return 0.0 if self.formal else 1.0
        return max(0.0, min(1.0, float(self.fraccion_informal_inicial)))

    # `formal` es el estado INICIAL del arquetipo, el que trae la encuesta. No es
    # su estado durante la corrida: eso lo lleva `rondas.correr()` y lo traduce a
    # texto `capa.situacion_planta()`. Acá había una property que devolvía
    # "toda formal"/"toda informal" desde este campo, y era justo la que hacía
    # que la ronda 2 le dijera "toda formal" a quien ya se había informalizado.


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
    # El `id` se arma con `sector[:3]`, y hoy los 9 sectores reales dan prefijos
    # únicos (verificado: 101 ids, 0 colisiones). Pero una colisión futura sería
    # silenciosa y cara: dos arquetipos con el mismo id comparten `historial` y
    # uno pisa al otro en el dict de resultados de `rondas.correr()`. Dos líneas
    # de seguro valen más que ese rato de depuración.
    ids = [a.id for a in fuera]
    if len(ids) != len(set(ids)):
        repetidos = sorted({i for i in ids if ids.count(i) > 1})
        raise ValueError(
            f"ids de arquetipo repetidos en {ruta}: {repetidos}. "
            "El prefijo `sector[:3]` colisiona; hay que alargarlo."
        )
    return fuera


# --- La grilla real de empleadores (C1) --------------------------------------


def desde_empresas(
    ruta: str | Path = "data/empresas.parquet",
    momentos: str | Path = "data/momentos.json",
) -> list[Arquetipo]:
    """Construye los arquetipos desde `data/empresas.parquet` (R1, Alejo).

    Reemplaza a `desde_poblacion()`, que re-derivaba el lado empleador con tres
    coeficientes de andamio sin fuente —caja = 0,18 × nómina, indemnización =
    1,5 salarios, factor prestacional = 1,40 para todo el mundo—. El parquet
    trae las tres cosas calculadas celda por celda contra el CST y el Art. 114-1,
    y `data/parametros_legales.json` lo dice explícitamente en su nota sobre la
    indemnización: ese archivo existe para reemplazar el `ingreso * 1.5` de acá.

    Diferencias que importan y que no son cosméticas:

    - **`n_empleados` excluye al dueño**; `EMPLEADOS_POR_CODIGO` lo incluía. Una
      celda de "2-3 personas" son 1,5 empleados, no 3, y esa diferencia entra
      derecho al veto por la vía del costo de nómina.
    - **Cuenta propia (código 1) no está en el parquet**: `construir_empresas.py`
      ya los excluye porque no tienen a quién despedir ni a quién informalizar.
      Un tercio de los ocupados de Bogotá son cuenta propia y el simulador les
      estaba preguntando a cuántos empleados despedían. Se reportan aparte con
      `poblacion_cuenta_propia()`.
    - **`share_formal` es continuo**: la celda entra con su fracción real fuera
      de regla en vez del corte binario que partía la grilla en dos.

    `peso` son trabajadores expandidos (a cuánta GENTE representa la celda) y
    `n_empresas` son firmas expandidas (a cuántas UNIDADES). Son universos
    distintos y se usan para cosas distintas: el primero pondera el agregado, el
    segundo alimenta la fiscalización. Confundirlos es el defecto §3.5.
    """
    import json

    import pandas as pd

    df = pd.read_parquet(ruta)
    exigidas = {
        "empresa_id", "sector", "tamano_grupo", "n_empleados", "salario_mediano_cop",
        "flujo_caja_mensual_cop", "costo_despido_por_empleado_cop",
        "factor_prestacional", "share_formal", "trabajadores_expandidos",
        "n_empresas_expandidas",
    }
    faltan = exigidas - set(df.columns)
    if faltan:
        raise ValueError(f"{ruta} no trae las columnas que C1 necesita: {sorted(faltan)}")

    # Los cortes de tramo salen de `momentos.json` (R1), no de la mediana de esta
    # tabla: son la misma partición que usa el resto del proyecto y recalcularla
    # acá abriría dos definiciones de "t1" para el mismo dato.
    try:
        terciles = json.loads(Path(momentos).read_text(encoding="utf-8"))["terciles_ingreso_cop"]
        t1_max, t2_max = float(terciles["t1_max"]), float(terciles["t2_max"])
    except (OSError, KeyError, ValueError):
        # SUPUESTO: sin `momentos.json` se cae a los cortes publicados en él a
        # H+15. Se declara porque cambia la etiqueta del tramo, no los números.
        t1_max, t2_max = 1_750_000.0, 3_000_000.0

    fuera: list[Arquetipo] = []
    for fila in df.itertuples(index=False):
        salario = float(fila.salario_mediano_cop)
        tramo = "t1" if salario <= t1_max else ("t2" if salario <= t2_max else "t3")
        # SUPUESTO: la planta se redondea al entero más cercano, con piso 1. Es
        # el mismo S9 que aplica `engine.veto.planta_viva`, y acá hace falta
        # porque `n_empleados` viene fraccionario (1,5 = punto medio del rango).
        n = max(1, int(round(float(fila.n_empleados))))
        share_formal = float(fila.share_formal)
        fuera.append(
            Arquetipo(
                id=str(fila.empresa_id),
                sector=str(fila.sector),
                tamano=str(fila.tamano_grupo),
                # Se conserva por compatibilidad con el Protocol `Firma` y con
                # `arquetipos_falsos()`; el estado que manda es el continuo.
                formal=bool(share_formal >= 0.5),
                tramo_ingreso=tramo,
                n_trabajadores=n,
                ingreso_por_trabajador=salario,
                flujo_caja=float(fila.flujo_caja_mensual_cop),
                costo_despido=float(fila.costo_despido_por_empleado_cop),
                peso=float(fila.trabajadores_expandidos),
                factor_prestacional=float(fila.factor_prestacional),
                fraccion_informal_inicial=max(0.0, min(1.0, 1.0 - share_formal)),
                n_empresas=float(fila.n_empresas_expandidas),
            )
        )

    ids = [a.id for a in fuera]
    if len(ids) != len(set(ids)):
        repetidos = sorted({i for i in ids if ids.count(i) > 1})
        raise ValueError(f"ids de arquetipo repetidos en {ruta}: {repetidos}")
    return fuera


def universo_de_firmas(arquetipos: list[Arquetipo]) -> float:
    """Cuántas unidades productivas representa la grilla. Alimenta a `engine/`.

    Es el denominador de la fiscalización: las inspecciones se reparten entre
    FIRMAS fuera de regla, no entre trabajadores. La capa contaba personas y el
    motor contaba empresas, y esa es exactamente la divergencia del defecto §3.5.

    # SUPUESTO: se suma `n_empresas_expandidas` tal como lo publica
    # `data/construir_empresas.py`. La review del PR #5 le anotó a esa columna
    # que mezcla personas y empleados en su derivación (368.491 publicado contra
    # 254.307 consistente). Es un dato de `data/` y se consume como está: si R1
    # lo corrige, este número se mueve solo y la dirección es conocida —un
    # universo más chico sube p(sanción) y por lo tanto ATENÚA la cascada—.
    """
    directo = sum(a.n_empresas for a in arquetipos)
    if directo > 0:
        return directo
    # SUPUESTO: sin la columna del parquet (grilla de andamio), el universo de
    # firmas se deriva del de trabajadores dividiendo el peso de cada celda
    # entre su planta. Es aritmética, no un dato: una celda que representa a
    # 1.000 trabajadores en plantas de 5 son 200 firmas. Se declara porque
    # alimenta la p(sanción), y con la grilla real esta rama no se usa.
    return sum(a.peso / max(1, a.n_trabajadores) for a in arquetipos)


def poblacion_cuenta_propia(
    ruta_poblacion: str | Path = "data/poblacion.parquet",
) -> dict[str, float]:
    """Los ocupados que la grilla de empleadores NO cubre, con su peso.

    `data/empresas.parquet` excluye el código 1 (trabaja solo) porque una unidad
    sin empleados no puede despedir ni informalizar a nadie. Eso es correcto y
    deja fuera a un tercio de los ocupados de Bogotá, así que el número se
    reporta en vez de desaparecer: sin esta línea, el agregado se leería como si
    fuera toda la ciudad.
    """
    import pandas as pd

    df = pd.read_parquet(ruta_poblacion)
    peso = df.get("factor_expansion")
    if peso is None:
        peso = pd.Series(1.0, index=df.index)
    solos = df["tamano_empresa"] == 1
    total = float(peso.sum())
    cubierto = float(peso[~solos].sum())
    return {
        "peso_cuenta_propia": float(peso[solos].sum()),
        "peso_con_empleador": cubierto,
        "fraccion_cuenta_propia": (float(peso[solos].sum()) / total) if total else 0.0,
    }


# --- El muestreo: lo que AgentTorch habría dado, en 20 líneas -----------------


def _semilla(seed: int, *partes: object) -> int:
    """Semilla estable derivada de (seed, arquetipo, ronda). Mismo seed, mismo
    resultado — no depende del orden en que se recorran los arquetipos."""
    crudo = "|".join(str(p) for p in (seed, *partes)).encode()
    return int.from_bytes(hashlib.blake2b(crudo, digest_size=8).digest(), "big")


def _muestrear_local(
    distribucion: dict[str, float],
    n: int,
    seed: int,
    *partes_semilla: object,
) -> list[str]:
    """Reparte `n` agentes entre las estrategias de su arquetipo, determinista.

    ⚠️ **Este NO es el muestreo del proyecto.** El canónico vive en
    `engine/arquetipos.py` con la firma que le asigna `engine/MODELO.md`
    —`muestrear(arq, n, rng)`— y es el que consume el pipeline. Éste se conserva
    con nombre privado como la evidencia de la verificación V10 (lo que
    AgentTorch habría dado, en 20 líneas; ver `behavior/README.md`), no como
    una segunda implementación en uso: dos funciones con el mismo nombre y
    semillas distintas es un camino directo a dos resultados "deterministas"
    que no coinciden.

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


# --- Modo top-K: a quién se le paga LLM y a quién no ------------------------


def particionar_por_peso(
    arquetipos: list[Arquetipo], cobertura: float = 0.80
) -> tuple[list[Arquetipo], list[Arquetipo]]:
    """Parte la grilla en (cabeza, cola) por peso poblacional acumulado.

    La `cabeza` es el prefijo más corto —ordenando por peso decreciente— que
    alcanza `cobertura` de la población expandida; la `cola` es el resto.

    Por qué existe: con la grilla real (101 arquetipos) una corrida en frío son
    ~404 llamadas y el barrido con banda se sale del presupuesto. La
    distribución de peso lo hace evitable: 51 de los 101 arquetipos pesan menos
    del 0,5% cada uno, y los 30 más grandes cubren ~80% de la población. La
    cabeza va al LLM y la cola a reglas fijas.

    Es un compromiso de costo, no de modelo, y se reporta como tal: cada ronda
    publica qué fracción de la población fue decidida por LLM.

    SUPUESTO: los arquetipos de la cola se comportan como el maximizador de
    `ablacion.ClienteReglas`. Es un sesgo de dirección CONOCIDA: la regla fija
    no descubre estrategias, así que la cola SUBESTIMA la evasión. Nuestra
    cascada con top-K es una cota inferior por este canal.
    """
    if not 0 < cobertura <= 1:
        raise ValueError(f"cobertura debe estar en (0, 1]; llegó {cobertura}")

    ordenados = sorted(arquetipos, key=lambda a: -a.peso)
    total = sum(a.peso for a in ordenados)
    if total <= 0:
        return ordenados, []

    acumulado = 0.0
    for i, a in enumerate(ordenados):
        acumulado += a.peso
        if acumulado / total >= cobertura:
            return ordenados[: i + 1], ordenados[i + 1 :]
    return ordenados, []


# --- B1: el presupuesto de preguntas se reparte por peso ---------------------

# El número que se publica sale de promediar >=5 paráfrasis dentro de cada
# ronda. Promediar 5 sorteos en vez de 1 baja el temblor por un factor de ~raiz(5),
# y ese temblor era el problema: reformular la MISMA pregunta movía el resultado
# 22,5 pp mientras cambiar la política solo lo movía 31,9 pp.
N_PARAFRASIS_MIN = 3
N_PARAFRASIS_MAX = 9


def parafrasis_por_peso(
    arquetipo: Arquetipo,
    peso_maximo: float,
    *,
    minimo: int = N_PARAFRASIS_MIN,
    maximo: int = N_PARAFRASIS_MAX,
) -> int:
    """Cuántas veces se le pregunta a este arquetipo, según cuánta gente pesa.

    Con la población concentrada como está —unos pocos arquetipos cargan casi
    todo el peso— el número final lo decide un puñado de lanzamientos de moneda
    en las celdas grandes. Preguntarle lo mismo a todos reparte mal el
    presupuesto: gasta en celdas que no mueven el agregado y deja sin muestrear
    las que sí.

    Con este reparto, misma plata y mucho menos temblor.

    # SUPUESTO: la asignación va con la RAÍZ de la participación relativa, no
    # con la participación misma. La raíz es lo que reparte cuando el error del
    # estimador escala como 1/raiz(n) —duplicar la muestra no duplica la precisión—
    # y además evita que una sola celda se coma todo el presupuesto. Es un
    # parámetro de costo, no de modelo: cambia cuánto tiembla el número, no su
    # valor esperado. Los extremos (3 y 9) salen del plan de correcciones.
    """
    if peso_maximo <= 0:
        return minimo
    razon = max(0.0, min(1.0, arquetipo.peso / peso_maximo)) ** 0.5
    return int(max(minimo, min(maximo, round(minimo + (maximo - minimo) * razon))))


def reparto_de_parafrasis(
    arquetipos: list[Arquetipo], **kw
) -> dict[str, int]:
    """El reparto completo, para poder auditarlo y sumarlo antes de gastar."""
    peso_maximo = max((a.peso for a in arquetipos), default=0.0)
    return {a.id: parafrasis_por_peso(a, peso_maximo, **kw) for a in arquetipos}


def cobertura_de(cabeza: list[Arquetipo], todos: list[Arquetipo]) -> float:
    """Qué fracción de la población expandida representa `cabeza`."""
    total = sum(a.peso for a in todos)
    return sum(a.peso for a in cabeza) / total if total else 0.0


def informalidad_observada(ruta: str | Path = "data/momentos.json") -> float:
    """La tasa de informalidad observada en la GEIH, ponderada por expansión.

    Se LEE de `data/momentos.json` (R1, Alejo) en vez de recalcularla desde el
    parquet: ese archivo es el objetivo de calibración publicado, y recalcularla
    por nuestra cuenta abriría la puerta a dos números distintos para la misma
    cosa. Si el archivo no está, quien llame decide el respaldo.

    Es el punto de partida de la ronda 0 — la proyección oficial de la ADR 0005
    asume cumplimiento total, o sea que la informalidad se queda donde la
    encuesta la encontró.

    Devuelve la tasa de los EMPLEADOS DE FIRMA, no la de todos los ocupados.
    ------------------------------------------------------------------------
    Esta función devolvía `tasa_informalidad_total` (30,57%), que cubre a todos
    los ocupados de Bogotá. Pero el motor solo simula decisiones de EMPLEADOR, y
    `data/empresas.parquet` excluye a propósito al cuenta propia —964.004
    personas, el 23% de los ocupados, 72,79% informales— porque una unidad sin
    empleados no puede despedir ni informalizar a nadie
    (ver `poblacion_cuenta_propia()`, que ya lo documentaba).

    La consecuencia estaba medida: la ronda 0 DECLARABA 30,57% y la ronda 1
    CALCULABA 17,99% desde la propia grilla, así que el simulador parecía
    formalizar 13,5 pp de la ciudad en la primera ronda incluso con alza 0%. Ese
    salto se leía como conducta del modelo y era un cambio de denominador.
    Contra el objetivo correcto el error a política cero es −0,92 pp, no −13,50.

    El total sigue publicado en `momentos.json` y `poblacion_cuenta_propia()`
    sigue reportando la parte que el motor no cubre: acá no se esconde nada, se
    compara contra la población que el motor efectivamente simula.
    """
    import json

    momentos = json.loads(Path(ruta).read_text(encoding="utf-8"))
    # SUPUESTO: un `momentos.json` viejo (anterior a la descomposición) no trae
    # la clave. Se cae al total para no reventar, que es el comportamiento de
    # antes, y así los artefactos de 2024/2025 se siguen leyendo.
    return float(
        momentos.get("tasa_informalidad_empleados_de_firma")
        or momentos["tasa_informalidad_total"]
    )
