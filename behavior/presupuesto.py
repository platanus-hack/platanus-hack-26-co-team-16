"""Presupuesto por corrida con corte duro.

Qué modela: nada. Es contabilidad de tokens.
Entradas: el `usage` de cada respuesta de la API.
Salidas: costo acumulado; `PresupuestoAgotado` cuando se pasa del tope.
Supuestos: los precios de `PRECIOS` son de lista y se actualizan a mano.

El tope es DURO: cuando se llega, la corrida se para. Preferimos una corrida
incompleta a una factura sorpresa a las cuatro de la mañana (plan §10).
"""

from __future__ import annotations

from dataclasses import dataclass, field

# USD por millón de tokens. Fuente: tabla de precios de la API de Anthropic.
# SUPUESTO: lectura de caché ~0.1x y escritura ~1.25x del precio de entrada.
PRECIOS: dict[str, tuple[float, float]] = {
    "claude-sonnet-5": (3.00, 15.00),   # la masa
    "claude-haiku-4-5": (1.00, 5.00),   # la masa hasta el 22-08-2026; se conserva
                                        # porque `behavior/README.md` reporta una
                                        # corrida real hecha con él y su costo
                                        # tiene que seguir siendo recalculable.
    "claude-opus-5": (5.00, 25.00),     # solo las 3-4 historias narradas
}
# SUPUESTO: para Sonnet 5 se fija el precio DE LISTA (3,00/15,00) y no el
# promocional vigente hasta el 31-08-2026 (2,00/10,00). Sobreestimar es la
# dirección segura para un tope duro: el corte salta antes, no después.

TOPE_POR_DEFECTO_USD = 3.00  # una corrida completa de 4 rondas cabe de sobra acá


class PresupuestoAgotado(RuntimeError):
    """Se llegó al tope. La corrida se para acá, a propósito."""


@dataclass
class Presupuesto:
    tope_usd: float = TOPE_POR_DEFECTO_USD
    gastado_usd: float = 0.0
    llamadas: int = 0
    tokens_entrada: int = 0
    tokens_salida: int = 0
    tokens_cache_leidos: int = 0
    tokens_cache_escritos: int = 0
    por_modelo: dict[str, float] = field(default_factory=dict)

    def costo(self, modelo: str, usage) -> float:
        """Costo en USD de una respuesta, según su `usage`."""
        if modelo not in PRECIOS:
            raise KeyError(f"modelo sin precio registrado: {modelo}. Agrégalo a PRECIOS.")
        p_in, p_out = PRECIOS[modelo]
        g = lambda campo: int(getattr(usage, campo, 0) or 0)  # noqa: E731
        return (
            g("input_tokens") * p_in
            + g("output_tokens") * p_out
            + g("cache_read_input_tokens") * p_in * 0.10
            + g("cache_creation_input_tokens") * p_in * 1.25
        ) / 1_000_000

    def registrar(self, modelo: str, usage) -> float:
        """Suma una llamada. Revienta si esa llamada pasó el tope."""
        c = self.costo(modelo, usage)
        self.gastado_usd += c
        self.llamadas += 1
        self.por_modelo[modelo] = self.por_modelo.get(modelo, 0.0) + c
        self.tokens_entrada += int(getattr(usage, "input_tokens", 0) or 0)
        self.tokens_salida += int(getattr(usage, "output_tokens", 0) or 0)
        self.tokens_cache_leidos += int(getattr(usage, "cache_read_input_tokens", 0) or 0)
        self.tokens_cache_escritos += int(getattr(usage, "cache_creation_input_tokens", 0) or 0)
        if self.gastado_usd > self.tope_usd:
            raise PresupuestoAgotado(
                f"corte duro: ${self.gastado_usd:.4f} > tope ${self.tope_usd:.2f} "
                f"tras {self.llamadas} llamadas"
            )
        return c

    def comprobar(self) -> None:
        """Antes de una llamada: si ya no hay margen, no la hagas."""
        if self.gastado_usd >= self.tope_usd:
            raise PresupuestoAgotado(
                f"corte duro: ${self.gastado_usd:.4f} >= tope ${self.tope_usd:.2f}"
            )

    def informe(self) -> str:
        lineas = [
            f"gasto:     ${self.gastado_usd:.4f} de ${self.tope_usd:.2f}",
            f"llamadas:  {self.llamadas}",
            f"tokens:    {self.tokens_entrada:,} entrada / {self.tokens_salida:,} salida",
            f"caché API: {self.tokens_cache_leidos:,} leídos / {self.tokens_cache_escritos:,} escritos",
        ]
        for m, c in sorted(self.por_modelo.items()):
            lineas.append(f"  {m}: ${c:.4f}")
        return "\n".join(lineas)
