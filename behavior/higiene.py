"""Guardia de contaminación: al LLM jamás se le nombra la política.

Qué modela: nada. Es un filtro de texto.
Entradas: cualquier cadena que vaya a salir hacia el modelo (sistema, usuario).
Salidas: nada si está limpia; `ContaminacionError` si no.
Supuestos: la lista negra es de mantenimiento manual (ver `TERMINOS_PROHIBIDOS`).

Por qué existe
--------------
El candado 3 de validación (`docs/PLAN.md` §5) dice que al modelo solo se le da
la mecánica, nunca el nombre de la política. Un acuerdo verbal no es
verificable; esto sí. Todo prompt pasa por `verificar()` antes de salir, y la
corrida se cae si algo se filtró — preferimos una corrida rota a un número
contaminado.

Verificable a mano:

    python3 -m behavior.higiene          # escanea behavior/prompts/ y sale != 0 si hay contaminación
"""

from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path

# SUPUESTO: esta lista es la definición operativa de "nombrar la política".
# Cubre el caso demo (costo laboral) y el test de §5.5 (restricción vehicular).
# Si alguien agrega un caso nuevo, agrega aquí sus términos en el mismo PR.
TERMINOS_PROHIBIDOS: dict[str, str] = {
    # --- la política del caso demo, por todos sus nombres ---
    r"salario\s+minimo": "nombra la política",
    r"\bsmmlv\b": "nombra la política",
    r"\bsmlv\b": "nombra la política",
    r"minimo\s+legal": "nombra la política",
    r"remuneracion\s+minima": "nombra la política",
    r"piso\s+salarial": "nombra la política",
    # --- el instrumento jurídico ---
    r"\bdecreto\b": "nombra el instrumento jurídico",
    r"\breforma\b": "nombra el instrumento jurídico",
    r"\bley\b": "nombra el instrumento jurídico",
    r"\bnormativa\b": "nombra el instrumento jurídico",
    r"\bpolitica\s+publica\b": "nombra que esto es una política",
    # --- lugar y tiempo: anclan el recuerdo del modelo a un evento real ---
    r"\bcolombia\b": "ancla geográfico",
    r"\bcolombian[oa]s?\b": "ancla geográfico",
    r"\bbogota\b": "ancla geográfico",
    r"\bpesos?\b": "ancla de moneda",
    r"\bcop\b": "ancla de moneda",
    r"\$": "ancla de moneda",
    r"\b(19|20)\d{2}\b(?!\s*(u\b|%))": "ancla temporal (año)",
    # --- actores del debate real ---
    r"\bgobierno\b": "actor del debate real",
    r"\bministerio\b": "actor del debate real",
    r"\bmintrabajo\b": "actor del debate real",
    r"\bsindicato": "actor del debate real",
    r"\bgremio": "actor del debate real",
    r"mesa\s+de\s+concertacion": "actor del debate real",
    r"\bdane\b": "nombra la fuente de datos",
    r"\bgeih\b": "nombra la fuente de datos",
    r"\bfedesarrollo\b": "actor del debate real",
    # --- el test de §5.5 tiene la misma regla ---
    r"pico\s+y\s+placa": "nombra la política del test",
    r"restriccion\s+vehicular": "nombra la política del test",
    # --- meta-fugas: decirle al modelo que está en una simulación de política ---
    r"\bsimulaci[oó]n\b": "meta-fuga: el agente no sabe que es una simulación",
    r"\bhistoric[oa]": "meta-fuga: invita a recordar en vez de decidir",
}

_PROMPTS = Path(__file__).parent / "prompts"


class ContaminacionError(RuntimeError):
    """Un prompt nombró la política. La corrida no vale; se para acá."""


def _normalizar(texto: str) -> str:
    """Minúsculas y sin tildes: 'Bogotá' y 'BOGOTA' son el mismo término."""
    descompuesto = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in descompuesto if unicodedata.category(c) != "Mn")


def revisar(texto: str) -> list[tuple[str, str, str]]:
    """Devuelve los hallazgos: [(patrón, razón, fragmento)]. Vacío = limpio."""
    plano = _normalizar(texto)
    hallazgos = []
    for patron, razon in TERMINOS_PROHIBIDOS.items():
        for m in re.finditer(patron, plano):
            ini, fin = max(0, m.start() - 30), min(len(plano), m.end() + 30)
            hallazgos.append((patron, razon, "..." + plano[ini:fin].strip() + "..."))
    return hallazgos


def verificar(texto: str, origen: str = "prompt") -> str:
    """Deja pasar el texto si está limpio; revienta si no. Devuelve el texto."""
    hallazgos = revisar(texto)
    if hallazgos:
        detalle = "\n".join(f"  [{p}] {r}\n    {frag}" for p, r, frag in hallazgos)
        raise ContaminacionError(
            f"{origen} nombra la política — la corrida queda invalidada:\n{detalle}"
        )
    return texto


def escanear_prompts() -> int:
    """Escanea los .md de behavior/prompts/. Devuelve el número de archivos sucios."""
    archivos = sorted(_PROMPTS.rglob("*.md"))
    if not archivos:
        print(f"no hay prompts en {_PROMPTS}", file=sys.stderr)
        return 1
    sucios = 0
    for ruta in archivos:
        hallazgos = revisar(ruta.read_text(encoding="utf-8"))
        rel = ruta.relative_to(_PROMPTS.parent)
        if hallazgos:
            sucios += 1
            print(f"SUCIO  {rel}")
            for patron, razon, frag in hallazgos:
                print(f"       [{patron}] {razon}\n         {frag}")
        else:
            print(f"limpio {rel}")
    print(f"\n{len(archivos) - sucios}/{len(archivos)} prompts limpios")
    return sucios


if __name__ == "__main__":
    sys.exit(1 if escanear_prompts() else 0)
