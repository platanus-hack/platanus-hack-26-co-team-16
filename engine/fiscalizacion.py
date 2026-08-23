"""Fiscalización endógena: capacidad fija repartida entre quienes están fuera de regla.

Qué modela: la probabilidad de que a una unidad fuera de regla le caiga una
  inspección en el trimestre, dada una capacidad de inspección que **no crece
  con el problema** ([ADR 0006](../docs/adr/0006-fiscalizacion-es-estado-del-mundo.md),
  [ADR 0007](../docs/adr/0007-forma-funcional-prob-sancion.md)).
Entradas: `C` (inspecciones esperadas en el trimestre sobre el universo del
  modelo) y `E` (unidades fuera de regla observadas en la ronda **anterior**).
Salidas: `p ∈ [0,1)`, el insumo que ven los agentes de la ronda siguiente.
Supuestos: S2 (inspecciones por inspector), S4 (reparto al azar), S5 (conversión
  anual→trimestral), S10 (fracción del universo). Todos marcados abajo.

**Acá nace la cascada**, y nace de una resta: la capacidad es fija, así que cada
unidad nueva fuera de regla le baja el riesgo a todas las demás. Nadie escribió
"si muchos evaden, evade más".

La forma funcional, y por qué
------------------------------
    p(E) = 1 − exp(−C / max(E, 1))

Sale de repartir `C` inspecciones al azar entre `E` unidades: los golpes que
recibe una unidad dada se aproximan por una Poisson de media `C/E`, y la
probabilidad de recibir **al menos uno** es `1 − e^(−C/E)`. Es bolas en cajas,
no una curva escogida para que la gráfica quede bonita. La derivación completa y
las cuatro alternativas descartadas están en la ADR 0007.

Para `C/E` pequeño —el régimen real: pocas inspecciones, muchos evasores—
`e^(−x) ≈ 1 − x`, o sea `p ≈ C/E`, que es la fórmula abreviada del plan. No
cambiamos el modelo: le damos la forma que se comporta en los bordes donde la
abreviada se rompía (devolvía números mayores que 1).

La decisión del borde: qué es ese `max(E, 1)`
----------------------------------------------
No es un parche contra la división por cero. El `1` **tiene significado**: `p`
es la probabilidad que enfrenta quien está considerando salirse de regla, y al
salirse él mismo es una unidad fuera de regla. El fondo nunca está vacío —
siempre contiene, como mínimo, a quien hace la pregunta. Con esa lectura la
fórmula queda definida para todo `E ≥ 0` sin tocar un solo número de la ADR.

**El estado absorbente es real y se declara, no se parcha.** Con `E → 0`,
`p → 1 − e^(−C)`, que con la capacidad de una ciudad es prácticamente 1: si nadie
está fuera de regla, salirse es suicida. Eso no es un artefacto, es el espejo de
la cascada — el mismo mecanismo que hace que la evasión se retroalimente hace que
el cumplimiento total también sea estable. Un modelo de esta familia produce
**equilibrios múltiples**, y eso está publicado (JPubE 2007, ver
`docs/investigacion/1-teorica.md` §3).

Lo que sí es un problema es que sea **silencioso**. En el barrido del candado 4
la corrida de ablación llegó a `E = 0` —porque compara mal el costo de
formalizarse, no por esta fórmula— y desde ahí quedó clavada en 0% para siempre
sin que nada lo dijera. Por eso `es_degenerado()` existe y por eso el régimen se
reporta junto al número, en vez de arreglar la física para tapar un bug de otra
capa. Corregir la fórmula ahí sería fabricar el resultado.

La trampa de unidades, que es la que rompe modelos en silencio
---------------------------------------------------------------
`C` y `E` cuentan **la misma cosa: unidades del universo del modelo**, no
personas y no fracciones. `behavior/` produce una *fracción* ponderada por factor
de expansión; convertirla es explícito y vive en un solo lugar
(`EstadoFiscalizacion.evasores()`). Mezclar una fracción con un conteo no falla:
da un número plausible y equivocado.

Cómo verificarlo a mano
-----------------------
    python3 -m engine.fiscalizacion       # C, la curva p(E), la cordura y el barrido de S2
    python3 -m engine.test_fiscalizacion  # los tests sin pytest
"""

from __future__ import annotations

import math
from dataclasses import dataclass, replace
from typing import Sequence

# --- Los números, cada uno con su origen -------------------------------------

# Fuente: OIT, "Mayor capacidad de la inspección del trabajo en Colombia"
# (proyecto ago-2023 a ago-2024): 1.300 inspectores en 36 direcciones
# territoriales. Ver `docs/investigacion/1-teorica.md` §3.
INSPECTORES_NACIONALES = 1_300

# SUPUESTO: S2 — el más importante del motor, y no tiene fuente. Es el numerador
# de p, o sea la cascada. Una inspección por día hábil serían ~60 al trimestre;
# el hallazgo de la OCDE de que el número de investigaciones CAYÓ pese a
# triplicar el presupuesto, y que casi la mitad exceden el plazo legal, dice que
# el rendimiento efectivo es una fracción de eso. Se usa 20 como orden de
# magnitud. Barrido de sensibilidad OBLIGATORIO: `python3 -m engine.fiscalizacion`
# lo imprime, y es la respuesta a "¿y si le erraron a la capacidad?".
INSPECCIONES_POR_INSPECTOR_TRIMESTRE = 20.0

# SUPUESTO: S10 — qué parte de la planta nacional actúa sobre el universo del
# modelo (una ciudad × los sectores modelados). Son dos factores multiplicados y
# ninguno está medido todavía: la participación de la ciudad en el empleo
# nacional (~0,20) y la de los sectores modelados dentro de ella (~0,75). Sale de
# la GEIH en cuanto R1 entregue `momentos.json`; hasta entonces es orden de
# magnitud y va al barrido junto con S2.
FRACCION_UNIVERSO = 0.15

TRIMESTRES_POR_ANO = 4

# Chequeo de CORDURA, no de calibración (ADR 0007). La literatura de cumplimiento
# del salario mínimo en EE.UU. reporta ~1,4% de probabilidad anual de
# investigación para una firma infractora (AEA 2025). Si nuestro p anualizado
# sale de un orden de magnitud muy distinto a un dígito porcentual, el error está
# en C y no en el fenómeno. Nunca se ajusta C para pegarle a este número.
PROB_ANUAL_REFERENCIA_EEUU = 0.014

# SUPUESTO: la elasticidad no se escoge para producir una curva conveniente: se
# CALIBRA contra la informalidad observada por tamaño con
# `python scripts/calibrar_visibilidad.py`. `alfa=0` recupera exactamente el
# reparto uniforme anterior y por eso es el contrafactual auditable del cambio.
ELASTICIDAD_VISIBILIDAD = 1.875


# --- La probabilidad ---------------------------------------------------------


def prob_sancion(capacidad: float, evasores: float) -> float:
    """`p(E) = 1 − exp(−C / max(E, 1))`. Estrictamente decreciente en `E`.

    `capacidad` y `evasores` se cuentan en las mismas unidades: unidades del
    universo del modelo por trimestre. Ver la trampa de unidades en el docstring
    del módulo.
    """
    if capacidad < 0:
        raise ValueError(f"la capacidad no puede ser negativa: {capacidad}")
    if evasores < 0:
        raise ValueError(f"no existe un número negativo de evasores: {evasores}")
    # `expm1` y no `1 - exp`: en el régimen real el exponente es diminuto
    # (C/E ~ 0,02) y `1 - exp(-x)` pierde media docena de dígitos justo donde
    # vive la cascada. `-expm1(-x)` es exacto ahí. Ver `satura()` para el otro
    # extremo, donde ninguna de las dos formas alcanza.
    return -math.expm1(-capacidad / max(evasores, 1.0))


def prob_por_celda(
    capacidad: float,
    celdas: Sequence[tuple[str, float, float]],
    alfa: float,
) -> dict[str, float]:
    """Reparte `C` según la visibilidad de cada celda de firmas evasoras.

    La unidad sigue siendo la firma: `n_empleados_por_firma` solo modifica qué
    fracción de la capacidad ve cada una. `expm1` conserva la precisión por la
    misma razón documentada en `prob_sancion()`.
    """
    if capacidad < 0:
        raise ValueError(f"la capacidad no puede ser negativa: {capacidad}")
    filas = list(celdas)
    pesos = {
        identificador: n_empleados**alfa
        for identificador, n_empleados, _ in filas
    }
    denominador = sum(
        evasores * pesos[identificador]
        for identificador, _, evasores in filas
        if evasores > 0
    )
    if denominador <= 0:
        return {identificador: 0.0 for identificador, _, _ in filas}
    return {
        identificador: -math.expm1(
            -capacidad * pesos[identificador] / max(denominador, 1.0)
        )
        for identificador, _, _ in filas
    }


def satura(capacidad: float, evasores: float) -> bool:
    """¿`p` salió exactamente 1,0 porque el double no da para más?

    Con `C/E` por encima de ~36, `exp(−C/E)` cae debajo del epsilon del double y
    `p` se vuelve 1,0 **exacto**. El valor verdadero sigue siendo menor que 1
    —la ADR 0007 tiene razón— pero no es representable, así que en esa banda `p`
    deja de ser estrictamente decreciente y pasa a ser una meseta.

    No se parchea con un tope artificial: eso metería un codo falso justo en la
    zona donde el proyecto dice descubrir **el codo**. Se detecta y se reporta.
    Con la `C` del caso demo la meseta cubre menos del 0,03% del universo, muy
    lejos del régimen donde ocurre la acción.
    """
    return prob_sancion(capacidad, evasores) >= 1.0


def es_degenerado(evasores: float) -> bool:
    """¿El `p` de esta ronda salió del borde en vez del régimen normal?

    Con menos de una unidad fuera de regla, `p` deja de ser una frecuencia
    observada y pasa a ser una **contrafáctica**: lo que le pasaría al primero
    que se salga. Sigue siendo el número correcto para decidir, pero se reporta
    marcado — es lo que faltó cuando la ablación quedó clavada en 0%.
    """
    return evasores < 1.0


def tasa_anual_implicita(p_trimestral: float) -> float:
    """Cuatro trimestres independientes: `1 − (1 − p)^4`.

    # SUPUESTO: S5 — los trimestres son independientes y la capacidad se reparte
    # uniforme en el año. La inspección real es estacional y una unidad ya
    # inspeccionada no es un ensayo idéntico al siguiente. Sirve para el chequeo
    # de cordura contra la cifra de EE.UU., no como resultado del modelo.
    """
    return 1.0 - (1.0 - p_trimestral) ** TRIMESTRES_POR_ANO


# --- El estado del mundo, no una perilla del usuario -------------------------


@dataclass(frozen=True)
class EstadoFiscalizacion:
    """La capacidad de inspección del periodo. **No es parte de la política.**

    Es estado del mundo ([ADR 0006](../docs/adr/0006-fiscalizacion-es-estado-del-mundo.md)):
    la inspección laboral existía antes del decreto y va a seguir existiendo
    después. Si fuera un campo de la política sería una perilla del slider, y
    entonces cualquier resultado sería alcanzable y la cascada no probaría nada.

    Es inmutable a propósito: se construye una vez al inicializar el mundo y
    **no se ajusta entre rondas**. Ese es el compromiso metodológico entero.

    `universo` es el número de unidades del modelo y no tiene default: sale de
    `data/poblacion.parquet` y nadie lo puede adivinar.
    """

    universo: int
    inspectores: int = INSPECTORES_NACIONALES
    inspecciones_por_inspector: float = INSPECCIONES_POR_INSPECTOR_TRIMESTRE
    fraccion_universo: float = FRACCION_UNIVERSO

    def __post_init__(self) -> None:
        if self.universo <= 0:
            raise ValueError(f"el universo tiene que tener unidades: {self.universo}")
        if not 0.0 <= self.fraccion_universo <= 1.0:
            raise ValueError(f"`fraccion_universo` va en [0,1]: {self.fraccion_universo}")

    def capacidad(self) -> float:
        """`C` = inspectores × inspecciones por inspector × fracción del universo.

        Cada factor declara su origen en las constantes de arriba: uno con
        fuente (OIT) y dos con `# SUPUESTO:` y barrido obligatorio.
        """
        return self.inspectores * self.inspecciones_por_inspector * self.fraccion_universo

    def evasores(self, fraccion_fuera_de_regla: float) -> float:
        """De la fracción ponderada que produce `behavior/` al conteo que usa `p`.

        La única conversión de unidades del modelo, en un solo lugar a propósito.
        """
        if not 0.0 <= fraccion_fuera_de_regla <= 1.0:
            raise ValueError(f"una fracción va en [0,1]: {fraccion_fuera_de_regla}")
        return fraccion_fuera_de_regla * self.universo

    def prob(self, fraccion_fuera_de_regla: float) -> float:
        """`p` para la ronda siguiente, a partir de la fracción de la anterior."""
        return prob_sancion(self.capacidad(), self.evasores(fraccion_fuera_de_regla))

    def prob_celdas(
        self,
        celdas: Sequence[tuple[str, float, float]],
        alfa: float | None = None,
    ) -> dict[str, float]:
        """`p` por celda con la misma capacidad fija del estado del mundo."""
        elasticidad = ELASTICIDAD_VISIBILIDAD if alfa is None else alfa
        return prob_por_celda(self.capacidad(), celdas, elasticidad)

    def con(self, **cambios) -> EstadoFiscalizacion:
        """Una copia con un factor cambiado. Es como se hace el barrido."""
        return replace(self, **cambios)


# --- El informe de honestidad ------------------------------------------------


def _miles(x: float) -> str:
    """Miles con punto. Aparte del f-string: un `.replace(",", ".")` sobre la
    línea entera se come también las comas del texto."""
    return f"{x:,.0f}".replace(",", ".")


def _fila(etiqueta: str, p: float) -> str:
    anual = tasa_anual_implicita(p)
    return f"{etiqueta:>28}  p trimestral {p:7.3%}   anualizada {anual:7.2%}"


def informe(estado: EstadoFiscalizacion) -> str:
    """Lo que se imprime para poder discutir el número en vez de creerle."""
    C = estado.capacidad()
    lineas = [
        "Capacidad de inspección del trimestre",
        f"  inspectores (OIT, con fuente) ........ {_miles(estado.inspectores):>12}",
        f"  inspecciones por inspector (S2) ...... {estado.inspecciones_por_inspector:>12.1f}",
        f"  fracción del universo (S10) .......... {estado.fraccion_universo:>12.2f}",
        f"  C = inspecciones en el trimestre ..... {_miles(C):>12}",
        f"  universo (unidades del modelo) ....... {_miles(estado.universo):>12}",
        "",
        "La curva p(E): más unidades fuera de regla, menos riesgo para cada una",
    ]
    for frac in (0.0, 0.01, 0.10, 0.42, 0.632, 0.756, 1.0):
        E = estado.evasores(frac)
        if es_degenerado(E):
            marca = "  <- régimen degenerado"
        elif satura(C, E):
            marca = "  <- meseta del double"
        else:
            marca = ""
        lineas.append(_fila(f"{frac:6.1%} fuera de regla", estado.prob(frac)) + marca)

    p_base = estado.prob(0.42)
    razon = tasa_anual_implicita(p_base) / PROB_ANUAL_REFERENCIA_EEUU
    lineas += [
        "",
        "Cordura (NO calibración): la referencia de EE.UU. para una firma infractora",
        f"  nuestra anualizada a 42% fuera de regla . {tasa_anual_implicita(p_base):7.2%}",
        f"  referencia AEA 2025 .................... {PROB_ANUAL_REFERENCIA_EEUU:7.2%}",
        f"  razón ................................... {razon:7.1f}x"
        + ("  OK: mismo dígito porcentual" if razon < 20 else "  REVISAR C"),
        "",
        "Barrido de S2, que es obligatorio: inspecciones por inspector por trimestre",
    ]
    for s2 in (5.0, 10.0, 20.0, 40.0, 60.0):
        alterno = estado.con(inspecciones_por_inspector=s2)
        lineas.append(_fila(f"S2 = {s2:g}, E a 42%", alterno.prob(0.42)))
    return "\n".join(lineas)


if __name__ == "__main__":  # pragma: no cover
    # SUPUESTO: 400.000 unidades es el orden de magnitud de una ciudad grande en
    # los sectores modelados, y es SOLO para que este informe imprima algo. El
    # universo real sale de `data/poblacion.parquet`; por eso el campo no tiene
    # default en la clase.
    print(informe(EstadoFiscalizacion(universo=400_000)))
