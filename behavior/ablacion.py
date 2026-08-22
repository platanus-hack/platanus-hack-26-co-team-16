"""Ablación: la misma corrida con reglas fijas en vez de LLM (candado 4).

Qué modela: un maximizador simple de costo esperado, del tipo que un economista
  escribiría a mano. Es la hipótesis nula de la capa conductual.
Entradas: las mismas que la capa LLM, vía `contexto`.
Salidas: el mismo JSON crudo que produciría el modelo.
Supuestos: ver `# SUPUESTO:` en `proponer()`. El más importante es el costo de
  formalizarse, que decide el signo del candado 4 — ver `--barrido-factor`.

Por qué existe (plan §5.4): si la corrida con reglas fijas da el mismo resultado
que la corrida con LLM, el LLM no se está ganando el puesto — y preferimos
saberlo nosotros a la H+24 que el juez en el Q&A. Si da distinto, esa diferencia
ES el argumento de por qué la capa conductual existe: el espacio de estrategias
abierto encuentra salidas que la regla no enumera.

Es un reemplazo directo de `ClienteConductual`: misma firma de `proponer()`, así
que `capa.py` y `rondas.py` no cambian una línea entre las dos corridas.
"""

from __future__ import annotations

from typing import Any

from pathlib import Path

from behavior.presupuesto import Presupuesto
from engine.veto import MESES_POR_RONDA


# SUPUESTO (S1 de `engine/MODELO.md`): el costo formal por trabajador es el
# salario por un factor prestacional de ~1,4-1,5, sin cifra exacta verificada.
# Acá se toma el extremo bajo del rango. Es un parámetro, no una constante
# enterrada: el valor que manda es el del motor de Manuel, y el barrido de
# `python3 -m behavior.ablacion --barrido-factor` muestra qué tanto depende de él
# la conclusión del candado 4 (spoiler: mucho — el signo se voltea en 1,43).
FACTOR_PRESTACIONAL = 1.40


class ClienteReglas:
    """Cliente falso: decide por regla fija, no llama a ninguna API, cuesta $0."""

    def __init__(self, factor_prestacional: float | None = None) -> None:
        self.presupuesto = Presupuesto(tope_usd=0.0)  # no gasta nada, y se nota
        self.llamadas = 0
        # C1: `None` significa "el factor de CADA arquetipo" (1,3835-1,5829 según
        # sector y exoneración del Art. 114-1), que es lo que trae
        # `data/empresas.parquet`. Un float fuerza el mismo valor para todos, que
        # es lo que necesita `--barrido-factor` y lo único para lo que sirve
        # promediar. El default era 1,40 para toda la población, y ese promedio
        # borraba justo la diferencia que decide el signo del candado 4.
        self.factor_prestacional = factor_prestacional

    def _factor(self, arq) -> float:
        """El factor de la celda, con el override del barrido por encima."""
        if self.factor_prestacional is not None:
            return self.factor_prestacional
        return float(getattr(arq, "factor_prestacional", FACTOR_PRESTACIONAL))

    def proponer(
        self,
        sistema: str,
        usuario: str,
        modelo: str = "reglas-fijas",
        max_tokens: int = 0,
        contexto: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if contexto is None:
            raise ValueError("la ablación necesita `contexto`; `capa.py` lo pasa siempre")
        self.llamadas += 1

        arq = contexto["arquetipo"]
        aumento = float(contexto["aumento_pct"]) / 100.0
        prob = float(contexto["prob_fiscalizacion"])
        multa = float(contexto["multa"])
        vetadas = contexto.get("estrategias_vetadas", ())
        # El estado VIVO, no el del dataclass: una unidad que informalizó en la
        # ronda anterior tiene que decidir como informal en ésta.
        frac_previa = float(
            contexto.get("fraccion_informal_previa", 0.0 if arq.formal else 1.0)
        )

        # SUPUESTO: formalizarse cuesta el costo formal COMPLETO —el salario por
        # el factor prestacional, ya con el aumento encima—, no solo el
        # sobrecosto que el aumento agrega. Comparar solo el sobrecosto contra la
        # sanción esperada era comparar un delta contra un nivel, y tenía una
        # consecuencia medible: el umbral quedaba en p > 1,92%, así que cualquier
        # probabilidad de fiscalización realista formalizaba a TODAS las unidades
        # informales en la ronda 1, la informalidad caía a 0, `p(E)` saltaba a
        # 100% y el sistema se clavaba ahí para siempre. El hallazgo "con reglas
        # fijas no hay cascada" era en buena parte artefacto de esa comparación.
        #
        # SUPUESTO: el salario bruto NO cambia al formalizarse; solo se agregan
        # las cargas. Es la especificación que no exige inventar una brecha
        # salarial informal/formal (el 0,85x del andamio no es un dato). Sesga a
        # favor de formalizar —o sea, A FAVOR de nuestro propio candado 4— y por
        # eso va acompañada del barrido de sensibilidad del factor prestacional.
        factor = self._factor(arq)
        costo_formal = arq.ingreso_por_trabajador * factor * (1 + aumento)
        costo_informal = arq.ingreso_por_trabajador + prob * multa
        # El sobrecosto que hay que financiar es el incremento sobre lo que ya se
        # pagaba (salario x factor), no sobre el salario pelado.
        sobrecosto = arq.ingreso_por_trabajador * factor * aumento
        # A3: la regla fija compara contra la caja del PERIODO, igual que el veto
        # y que el prompt. Comparaba contra el flujo mensual, así que la
        # ablación despedía en casos en los que el veto decía que sí se podía
        # pagar: tres lugares y dos unidades para la misma billetera.
        caja_periodo = arq.flujo_caja * MESES_POR_RONDA

        # SUPUESTO: la regla fija decide para la planta entera. Una unidad con la
        # mayoría de su planta fuera de regla se comporta como informal.
        if frac_previa >= 0.5:
            # Ya está fuera de regla: se formaliza solo si sale más barato que
            # seguir informal cargando la sanción esperada.
            eleccion = "cumplir" if costo_formal < costo_informal else "absorber"
        elif costo_informal < costo_formal:
            eleccion = "informalizar_total"
        elif sobrecosto * arq.n_trabajadores > caja_periodo:
            eleccion = "despedir"
        else:
            eleccion = "cumplir"

        # Único reintento posible de una regla fija: caer al siguiente escalón.
        escalera = ["informalizar_total", "despedir", "absorber", "cumplir"]
        while eleccion in vetadas and eleccion in escalera:
            idx = escalera.index(eleccion)
            if idx + 1 >= len(escalera):
                break
            eleccion = escalera[idx + 1]

        detalle: dict[str, Any] = {}
        if eleccion == "despedir":
            # SUPUESTO: despide lo mínimo para que el sobrecosto quepa en la caja.
            faltante = sobrecosto * arq.n_trabajadores - caja_periodo
            detalle = {
                "empleados_a_despedir": max(1, min(arq.n_trabajadores - 1,
                                                   int(faltante // max(sobrecosto, 1)) + 1))
            }
        elif eleccion == "informalizar_total":
            detalle = {"empleados_a_informalizar": arq.n_trabajadores}

        return {
            "estrategia_propuesta": eleccion,
            "detalle": detalle,
            "justificacion": (
                f"regla fija: costo formal {costo_formal:,.0f} u vs costo informal "
                f"{costo_informal:,.0f} u"
            ),
        }


# --- El barrido del factor prestacional: la sensibilidad del candado 4 --------


def barrer_factor(
    factores: list[float] | None = None,
    *,
    aumento_pct: float = 23.0,
    real: bool = False,
) -> list[tuple[float, float, float]]:
    """Corre la ablación completa para varios factores prestacionales.

    Existe porque el resultado del candado 4 **no es robusto al valor de S1**, y
    esconderlo detrás de un solo número sería exactamente lo que el plan §5.4
    quiere evitar. `engine/MODELO.md` declara el factor prestacional como
    "≈1,4-1,5, sin cifra exacta verificada": este barrido dice qué conclusión
    sale de cada punto de ese rango declarado.

    Cuesta $0 — la ablación no llama a ninguna API.

    Devuelve `[(factor, informalidad_final, prob_sancion_final)]`.
    """
    # Importación local: `rondas` importa `ClienteReglas` de este módulo.
    from behavior.arquetipos import (
        arquetipos_falsos,
        desde_empresas,
        informalidad_observada,
    )
    from behavior.rondas import correr

    if factores is None:
        factores = [1.40, 1.4125, 1.425, 1.43, 1.4375, 1.45, 1.475, 1.50]
    # C1/C2 — el barrido corre sobre la grilla REAL de empleadores si existe.
    # Con la grilla de andamio los pesos son 1,0 por celda, así que el universo
    # de firmas que sale de ahí son ~5 unidades contra una capacidad de 3.900
    # inspecciones: la p(sanción) satura en 100% y el barrido deja de decir
    # nada. No es un defecto de la fiscalización, es que el andamio nunca fue
    # un universo poblacional.
    ruta = Path("data/empresas.parquet")
    if real or ruta.exists():
        arquetipos = desde_empresas(ruta)
    else:
        arquetipos = arquetipos_falsos()
    tasa_inicial = informalidad_observada()

    fuera = []
    for f in factores:
        rondas = correr(
            arquetipos,
            ClienteReglas(factor_prestacional=f),
            aumento_pct=aumento_pct,
            paralelismo=1,
            tasa_informalidad_inicial=tasa_inicial,
        )
        fuera.append((f, rondas[-1].tasa_informalidad, rondas[-1].prob_fiscalizacion))
    return fuera


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="Sensibilidad del candado 4 al supuesto S1.")
    ap.add_argument("--barrido-factor", action="store_true", default=True)
    ap.add_argument("--aumento", type=float, default=23.0)
    ap.add_argument("--real", action="store_true", help="usar data/poblacion.parquet")
    args = ap.parse_args()

    print(
        f"ABLACIÓN (reglas fijas, $0) · aumento {args.aumento:g}% · "
        f"{'población real' if args.real else 'andamio'}\n"
        "Barrido del factor prestacional — supuesto S1 de engine/MODELO.md,\n"
        "declarado como «≈1,4-1,5, sin cifra exacta verificada».\n"
    )
    print(f"{'factor':>8} {'informalidad final':>19} {'p. sanción':>11}   conclusión")
    print("-" * 70)
    previo = None
    for f, tasa, prob in barrer_factor(aumento_pct=args.aumento, real=args.real):
        hay_cascada = tasa > 0.01
        marca = ""
        if previo is not None and previo != hay_cascada:
            marca = "  <-- AQUÍ SE VOLTEA EL CANDADO 4"
        previo = hay_cascada
        print(
            f"{f:>8.4f} {tasa:>18.1%} {prob:>11.1%}   "
            f"{'CASCADA con reglas fijas' if hay_cascada else 'sin cascada'}{marca}"
        )
    print(
        "\nLeer así: el candado 4 sostiene «la diferencia ES el LLM» solo en las\n"
        "filas sin cascada. Que el signo cambie DENTRO del rango que el propio\n"
        "modelo declaró incierto es el resultado, no un defecto de la medición."
    )
