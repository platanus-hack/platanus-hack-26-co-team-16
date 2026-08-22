"""Caché en disco por hash del prompt. La segunda corrida cuesta ~$0.

Qué modela: nada. Es memoización.
Entradas: (modelo, sistema, usuario, esquema) -> Salidas: la respuesta guardada.
Supuestos: ninguno.

Por qué importa más de lo que parece
------------------------------------
1. **Costo.** Una simulación se corre decenas de veces mientras se ajusta la
   pantalla; no pagamos dos veces el mismo prompt.
2. **Reproducibilidad.** Una llamada a un LLM no es determinista, así que el
   determinismo del proyecto (mismo seed, mismo resultado) se sostiene sobre
   esto: con el caché poblado, la corrida vuelve a leer exactamente las mismas
   respuestas. Es un hecho del diseño y así se reporta en `VALIDATION.md`, no
   una propiedad del modelo.

Verificable a mano:

    python3 -m behavior.cache            # tamaño y contenido del caché
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

DIR_CACHE = Path(__file__).parent / ".cache"


def clave(modelo: str, sistema: str, usuario: str, esquema: Any = None) -> str:
    """Hash estable de todo lo que determina la respuesta."""
    crudo = json.dumps(
        {"modelo": modelo, "sistema": sistema, "usuario": usuario, "esquema": esquema},
        sort_keys=True,  # sin esto el hash cambia entre corridas y el caché no sirve
        ensure_ascii=False,
    ).encode()
    return hashlib.sha256(crudo).hexdigest()[:32]


class Cache:
    def __init__(self, directorio: Path | str = DIR_CACHE, activo: bool = True):
        self.dir = Path(directorio)
        self.activo = activo
        self.aciertos = 0
        self.fallos = 0
        if self.activo:
            self.dir.mkdir(parents=True, exist_ok=True)

    def _ruta(self, k: str) -> Path:
        return self.dir / f"{k}.json"

    def leer(self, k: str) -> dict[str, Any] | None:
        if not self.activo:
            return None
        ruta = self._ruta(k)
        if not ruta.exists():
            self.fallos += 1
            return None
        self.aciertos += 1
        return json.loads(ruta.read_text(encoding="utf-8"))

    def escribir(self, k: str, valor: dict[str, Any]) -> None:
        if self.activo:
            self._ruta(k).write_text(
                json.dumps(valor, ensure_ascii=False, indent=2), encoding="utf-8"
            )

    @property
    def tasa_acierto(self) -> float:
        total = self.aciertos + self.fallos
        return self.aciertos / total if total else 0.0

    def exportar(self, destino: Path | str) -> int:
        """Consolida el caché en un archivo, para versionar los escenarios del demo.

        Un juez sin API key puede reproducir la corrida importando esto.
        """
        todo = {r.stem: json.loads(r.read_text(encoding="utf-8")) for r in self.dir.glob("*.json")}
        Path(destino).write_text(json.dumps(todo, ensure_ascii=False, indent=2), encoding="utf-8")
        return len(todo)

    def importar(self, origen: Path | str) -> int:
        todo = json.loads(Path(origen).read_text(encoding="utf-8"))
        for k, v in todo.items():
            self.escribir(k, v)
        return len(todo)


if __name__ == "__main__":
    c = Cache()
    archivos = sorted(c.dir.glob("*.json"))
    peso = sum(a.stat().st_size for a in archivos)
    print(f"caché: {c.dir}")
    print(f"entradas: {len(archivos)}  ({peso / 1024:.1f} KiB)")
    if not archivos:
        print("vacío — todavía no se ha corrido nada contra la API")
    sys.exit(0)
