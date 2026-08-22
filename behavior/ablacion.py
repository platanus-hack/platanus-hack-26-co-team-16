"""Ablación: la misma corrida con reglas fijas en vez de LLM (candado 4).

Qué modela: un maximizador simple de costo esperado, del tipo que un economista
  escribiría a mano. Es la hipótesis nula de la capa conductual.
Entradas: las mismas que la capa LLM, vía `contexto`.
Salidas: el mismo JSON crudo que produciría el modelo.
Supuestos: ver `# SUPUESTO:` en `proponer()`.

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

from behavior.presupuesto import Presupuesto


class ClienteReglas:
    """Cliente falso: decide por regla fija, no llama a ninguna API, cuesta $0."""

    def __init__(self) -> None:
        self.presupuesto = Presupuesto(tope_usd=0.0)  # no gasta nada, y se nota
        self.llamadas = 0

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

        # SUPUESTO: el sobrecosto anual por trabajador formal es el ingreso por
        # el aumento. Es la aproximación de primer orden; el motor de Manuel
        # calcula el costo real con factor prestacional.
        sobrecosto = arq.ingreso_por_trabajador * aumento
        sancion_esperada = prob * multa

        if not arq.formal:
            # Ya está fuera de regla: la regla fija nunca vuelve a formalizarse
            # si formalizarse cuesta más que la sanción esperada.
            eleccion = "cumplir" if sobrecosto < sancion_esperada else "absorber"
        elif sobrecosto > sancion_esperada:
            eleccion = "informalizar_total"
        elif sobrecosto * arq.n_trabajadores > arq.flujo_caja:
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
            faltante = sobrecosto * arq.n_trabajadores - arq.flujo_caja
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
                f"regla fija: sobrecosto {sobrecosto:,.0f} u vs sanción esperada "
                f"{sancion_esperada:,.0f} u"
            ),
        }
