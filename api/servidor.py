"""La API del enjambre: una corrida REAL del motor, transmitida ronda a ronda.

    uvicorn api.servidor:app --port 8000        # desde la raíz del repo, venv activo

Qué hace: expone `behavior.rondas.correr()` por HTTP. Nada precomputado: cada
`GET /simulaciones/flujo` lanza una corrida del motor con la grilla real de
`data/empresas.parquet` y va emitiendo eventos SSE a medida que el motor los
produce, por las dos costuras que `behavior/` expone para eso
(`al_terminar_ronda` y `al_decidir_arquetipo`).

Eventos del flujo, en orden:
  inicio    → parámetros de la corrida (con el rótulo de qué gobierna el seed)
  decision  → una celda decidió (progreso intra-ronda, orden de terminación real)
  ronda     → agregado de la ronda cerrada (contracts/ronda.json intacto + extras)
  fin       → la corrida terminó (con el informe de gasto si hubo LLM)
  error     → la corrida murió (sin credenciales, presupuesto, etc.)

La spec original de `api/README.md` (POST + Supabase Realtime) nunca se
construyó y Supabase no existe en el repo; SSE da el mismo "en vivo" sin sumar
un servicio externo a horas del cierre. Sin auth (regla del repo): un extraño
con el link puede usarlo.
"""

from __future__ import annotations

import json
import queue
import threading
import time
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterator

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from api import serializar
from behavior.ablacion import ClienteReglas
from behavior.arquetipos import (
    desde_empresas,
    informalidad_observada,
    poblacion_cuenta_propia,
)
from behavior.cliente import ClienteConductual, SinCredenciales
from behavior.presupuesto import Presupuesto
from behavior.rondas import correr

_RAIZ = Path(__file__).resolve().parent.parent

# El calendario de la corrida, declarado UNA vez y en un solo lado. Alimenta los
# dos puntos que TIENEN que coincidir: `correr()`, que decide cuántas rondas
# ejecuta el motor, y el evento `poblacion`, que le dice a la pantalla cuántas
# dibujar. Antes eran dos literales sueltos —el default de `behavior.rondas.correr`
# y un `4` a mano en `serializar.evento_poblacion`— que cuadraban por casualidad;
# el día que uno cambiara, la barra de tiempo mentía sin que nada fallara.
# Ronda 0 = la reacción ingenua, sin LLM; las rondas 1..3 son mejor respuesta.
# O sea 3 rondas de LLM, no 4 (ADR 0005, y el docstring de `correr()`).
RONDAS_TOTALES = 4

# Qué gobierna la perilla `seed` de esta API. Hoy: nada más que su propia
# etiqueta, y eso se declara en vez de disimularse.
# Medido, no supuesto: `modo=reglas`, seed 42 contra seed 99, las 4 rondas
# comparadas campo por campo quitando la etiqueta -> trayectorias IDÉNTICAS
# (informalidad final 31,01% en ambas). En el camino del LLM no puede ser de
# otra forma: `capa.renderizar()` no recibe seed, así que el prompt no lo lleva,
# y `cache.clave()` hashea el prompt, así que dos semillas son dos aciertos de
# caché iguales. `engine/seed.py` tiene los streams buenos y hoy no lo importa
# nadie fuera de su propio test; él mismo lo dice en su encabezado.
# No se quita la perilla: el front ya la manda y `web/` no es de este rol. Se
# rotula, que es lo que evita que alguien la mueva, no vea nada, y concluya que
# el modelo es sordo a su propia semilla.
# El día que el seed elija las N paráfrasis de `banda_entre_trayectorias()`,
# esto pasa a "trayectoria" y es la única línea que cambia.
SEED_EFECTO = "etiqueta"  # "etiqueta" | "trayectoria"

app = FastAPI(title="enjambre-api", docs_url=None, redoc_url=None)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # sin auth ni registro: regla no-negociable del repo
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Una corrida a la vez: el motor satura los hilos y el presupuesto es uno solo.
_ocupado = threading.Lock()


@lru_cache(maxsize=1)
def _grilla():
    return desde_empresas(_RAIZ / "data" / "empresas.parquet", _RAIZ / "data" / "momentos.json")


@lru_cache(maxsize=1)
def _cuenta_propia():
    return poblacion_cuenta_propia(_RAIZ / "data" / "poblacion.parquet")


@app.get("/poblacion")
def poblacion() -> dict[str, Any]:
    """La grilla estática de celdas empleadoras GEIH, para dibujar el enjambre."""
    return serializar.evento_poblacion(
        _grilla(), _cuenta_propia(), rondas_totales=RONDAS_TOTALES
    )


def _sse(evento: str, datos: dict[str, Any]) -> str:
    return f"event: {evento}\ndata: {json.dumps(datos, ensure_ascii=False)}\n\n"


@app.get("/simulaciones/flujo")
def flujo(
    aumento_pct: float = Query(23.0, ge=0.0, le=50.0),
    seed: int = Query(
        42,
        description=(
            "Rotula la corrida y viaja en el contrato. HOY NO CAMBIA NINGUNA "
            "DECISIÓN: nada del bucle de rondas sortea. Ver `SEED_EFECTO`."
        ),
    ),
    cobertura: float = Query(0.8, gt=0.0, le=1.0),
    parafrasis: int = Query(1, ge=1, le=9),
    tope_usd: float = Query(3.0, gt=0.0, le=10.0),
    modo: str = Query("llm", pattern="^(llm|reglas)$"),
) -> StreamingResponse:
    """Corre el motor de verdad y transmite cada evento a medida que ocurre.

    `modo=llm` es el del producto (decisiones de `ClienteConductual`, con caché
    de disco y tope de presupuesto). `modo=reglas` corre la ablación
    determinista — existe para el smoke test y para demos sin credenciales; la
    interfaz no lo expone.
    """
    return StreamingResponse(
        _generar(aumento_pct, seed, cobertura, parafrasis, tope_usd, modo),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


def _generar(
    aumento_pct: float,
    seed: int,
    cobertura: float,
    parafrasis: int,
    tope_usd: float,
    modo: str,
) -> Iterator[str]:
    if not _ocupado.acquire(blocking=False):
        yield _sse("error", {"mensaje": "ya hay una corrida en curso; espera a que termine"})
        return

    eventos: queue.Queue[tuple[str, dict[str, Any]] | None] = queue.Queue()
    cancelado = threading.Event()
    arquetipos = _grilla()
    total = len(arquetipos)
    decididos: dict[int, int] = {}
    candado = threading.Lock()

    def al_decidir(ronda: int, arquetipo_id: str, resultado) -> None:
        if cancelado.is_set():
            raise RuntimeError("corrida cancelada: el cliente se desconectó")
        with candado:
            decididos[ronda] = decididos.get(ronda, 0) + 1
            n = decididos[ronda]
        ev = serializar.evento_decision(ronda, arquetipo_id, resultado, n, total)
        print(
            f"[decisión r{ronda} {n:>3}/{total}] {arquetipo_id:<28} "
            f"{ev['dominante'] or '-':<14} vetadas={ev['vetadas']}"
        )
        eventos.put(("decision", ev))

    def al_terminar(r) -> None:
        if cancelado.is_set():
            raise RuntimeError("corrida cancelada: el cliente se desconectó")
        ev = serializar.evento_ronda(r, arquetipos, aumento_pct)
        c = ev["contrato"]
        # Los prints de verificación: lo que ve la pantalla es lo que dice acá.
        print(
            f"\n[ronda {c['ronda']}] informalidad={c['tasa_informalidad']:.1%} "
            f"p(sanción)={c['prob_fiscalizacion']:.1%} empleo={c['empleo_relativo']:.1%} "
            f"ingreso_laboral={c['ingreso_laboral_relativo']:.1%} "
            f"masa_salarial={ev['masa_salarial_relativa']} "
            f"bajo_mínimo={ev['fraccion_bajo_minimo']}"
        )
        if ev["desglose_estrategias"]:
            top = ", ".join(f"{k} {v:.1%}" for k, v in list(ev["desglose_estrategias"].items())[:4])
            print(f"[ronda {c['ronda']}] estrategias (ponderadas): {top}")
        print(
            f"[ronda {c['ronda']}] fallbacks={ev['fraccion_fallback']:.1%} "
            f"sin_salida={ev['fraccion_sin_salida']:.1%} "
            f"banda={c['banda']} estabilizada={c['estabilizada']}\n"
        )
        eventos.put(("ronda", ev))

    def trabajar() -> None:
        t0 = time.time()
        cliente = (
            ClienteConductual(presupuesto=Presupuesto(tope_usd=tope_usd))
            if modo == "llm"
            else ClienteReglas()
        )
        try:
            correr(
                arquetipos,
                cliente,
                aumento_pct=aumento_pct,
                rondas_totales=RONDAS_TOTALES,
                seed=seed,
                simulacion_id=f"enjambre-{seed}-{aumento_pct:g}",
                veto=None,
                n_parafrasis=parafrasis,
                cobertura_llm=cobertura if modo == "llm" else None,
                tasa_informalidad_inicial=informalidad_observada(_RAIZ / "data" / "momentos.json"),
                al_terminar_ronda=al_terminar,
                al_decidir_arquetipo=al_decidir,
            )
            gasto: dict[str, Any] = {"segundos": round(time.time() - t0, 1), "modo": modo}
            presupuesto = getattr(cliente, "presupuesto", None)
            if presupuesto is not None:
                gasto["llamadas_api"] = presupuesto.llamadas
                gasto["gasto_usd"] = round(getattr(presupuesto, "gastado_usd", 0.0), 4)
            cache = getattr(cliente, "cache", None)
            if cache is not None:
                gasto["cache_aciertos"] = cache.aciertos
                gasto["cache_fallos"] = cache.fallos
            eventos.put(("fin", gasto))
        except SinCredenciales as e:
            eventos.put(("error", {"mensaje": str(e)}))
        except Exception as e:  # noqa: BLE001 — el flujo reporta y muere limpio
            if not cancelado.is_set():
                eventos.put(("error", {"mensaje": f"{type(e).__name__}: {e}"}))
        finally:
            eventos.put(None)

    hilo = threading.Thread(target=trabajar, daemon=True)
    hilo.start()
    print(
        f"\n=== corrida: aumento {aumento_pct:g}% · seed {seed} ({SEED_EFECTO}) · "
        f"modo {modo} · "
        f"cobertura {cobertura:g} · {parafrasis} paráfrasis · {total} arquetipos ==="
    )
    try:
        yield _sse(
            "inicio",
            {
                "aumento_pct": aumento_pct,
                "seed": seed,
                # El rótulo viaja con la corrida: la pantalla tiene con qué
                # decir qué hace la perilla sin que nadie lo adivine.
                "seed_efecto": SEED_EFECTO,
                "modo": modo,
                "cobertura": cobertura,
                "parafrasis": parafrasis,
                "n_arquetipos": total,
            },
        )
        while True:
            try:
                item = eventos.get(timeout=15.0)
            except queue.Empty:
                # Latido: una ronda LLM puede tardar minutos sin cerrar ninguna
                # celda visible (reintentos); el comentario mantiene viva la
                # conexión sin ensuciar los eventos.
                yield ": latido\n\n"
                continue
            if item is None:
                break
            yield _sse(*item)
    finally:
        cancelado.set()
        _ocupado.release()
