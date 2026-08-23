"""La API del enjambre: una corrida REAL del motor, transmitida ronda a ronda.

    uvicorn api.servidor:app --port 8000        # desde la raíz del repo, venv activo

Qué hace: expone `behavior.rondas.correr()` por HTTP. Nada precomputado: cada
`GET /simulaciones/flujo` lanza una corrida del motor con la grilla real de
`data/empresas.parquet` y va emitiendo eventos SSE a medida que el motor los
produce, por las dos costuras que `behavior/` expone para eso
(`al_terminar_ronda` y `al_decidir_arquetipo`).

Eventos del flujo, en orden:
  inicio    → parámetros de la corrida (con el rótulo de qué gobierna el seed)
  trayectoria → arrancó una de las N trayectorias de las que sale la banda
  decision  → una celda decidió (progreso intra-ronda, orden de terminación real)
  ronda     → agregado de la ronda cerrada (contracts/ronda.json intacto + extras).
              Salen TODAS al final: son las de la trayectoria mediana, y cuál es
              la mediana no se sabe hasta que las N cierran.
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
from api.trayectorias import N_TRAYECTORIAS, correr_consolidada

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
    trayectorias: int = Query(
        N_TRAYECTORIAS,
        ge=1,
        le=N_TRAYECTORIAS,
        description=(
            "Trayectorias completas e independientes. La banda que se publica "
            "es la dispersión ENTRE ellas. Con 1 no hay banda y `banda.tipo` lo dice."
        ),
    ),
    parafrasis: int = Query(
        1,
        ge=1,
        le=9,
        description=(
            "Paráfrasis por ronda DENTRO de cada trayectoria. Solo llena "
            "`banda_intra_ronda`, que es diagnóstico y no sale a pantalla. "
            "Multiplica el costo por su valor: déjalo en 1."
        ),
    ),
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
        _generar(
            aumento_pct, seed, cobertura, trayectorias, parafrasis, tope_usd, modo
        ),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


def _generar(
    aumento_pct: float,
    seed: int,
    cobertura: float,
    trayectorias: int,
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
    # La cuenta de decisiones es por (trayectoria, ronda): con N trayectorias, una
    # sola cuenta por ronda pasaría de `total` y la barra de progreso mentiría.
    decididos: dict[tuple[int, int], int] = {}
    candado = threading.Lock()

    def al_decidir(trayectoria: int, ronda: int, arquetipo_id: str, resultado) -> None:
        if cancelado.is_set():
            raise RuntimeError("corrida cancelada: el cliente se desconectó")
        with candado:
            clave = (trayectoria, ronda)
            decididos[clave] = decididos.get(clave, 0) + 1
            n = decididos[clave]
        ev = serializar.evento_decision(ronda, arquetipo_id, resultado, n, total)
        # Con esto la pantalla anima el enjambre MIENTRAS se calcula, que es lo
        # único que ocurre en vivo ahora. Va rotulado con la trayectoria: sin eso,
        # N pasadas seguidas por las mismas celdas parecen un bucle roto.
        ev["trayectoria"] = trayectoria
        print(
            f"[t{trayectoria} decisión r{ronda} {n:>3}/{total}] {arquetipo_id:<28} "
            f"{ev['dominante'] or '-':<14} vetadas={ev['vetadas']}"
        )
        eventos.put(("decision", ev))

    def _imprimir_ronda(prefijo: str, ev: dict[str, Any]) -> None:
        """Los prints de verificación: lo que ve la pantalla es lo que dice acá."""
        c = ev["contrato"]
        print(
            f"\n[{prefijo}ronda {c['ronda']}] informalidad={c['tasa_informalidad']:.1%} "
            f"p(sanción)={c['prob_fiscalizacion']:.1%} empleo={c['empleo_relativo']:.1%} "
            f"ingreso_laboral={c['ingreso_laboral_relativo']:.1%} "
            f"masa_salarial={ev['masa_salarial_relativa']} "
            f"bajo_mínimo={ev['fraccion_bajo_minimo']}"
        )
        if ev["desglose_estrategias"]:
            top = ", ".join(f"{k} {v:.1%}" for k, v in list(ev["desglose_estrategias"].items())[:4])
            print(f"[{prefijo}ronda {c['ronda']}] estrategias (ponderadas): {top}")
        print(
            f"[{prefijo}ronda {c['ronda']}] fallbacks={ev['fraccion_fallback']:.1%} "
            f"sin_salida={ev['fraccion_sin_salida']:.1%} "
            f"banda={c['banda']} estabilizada={c['estabilizada']}\n"
        )

    def al_terminar(trayectoria: int, r) -> None:
        """Cierra una ronda DE UNA trayectoria: se imprime, no se transmite.

        Transmitirla sería narrar en pantalla una trayectoria que puede no ser la
        que se publique. La que sale al cable es la mediana de las N, y cuál es la
        mediana no se sabe hasta que las N cierran.
        """
        if cancelado.is_set():
            raise RuntimeError("corrida cancelada: el cliente se desconectó")
        _imprimir_ronda(f"t{trayectoria} ", serializar.evento_ronda(r, arquetipos, aumento_pct))

    def al_empezar_trayectoria(i: int, n: int) -> None:
        print(f"\n=== trayectoria {i + 1}/{n} · paráfrasis {i + 1} ===")
        eventos.put(("trayectoria", {"indice": i, "de": n}))

    def trabajar() -> None:
        t0 = time.time()
        cliente = (
            ClienteConductual(presupuesto=Presupuesto(tope_usd=tope_usd))
            if modo == "llm"
            else ClienteReglas()
        )
        try:
            rondas, n_efectivas = correr_consolidada(
                arquetipos,
                cliente,
                n_trayectorias=trayectorias,
                aumento_pct=aumento_pct,
                rondas_totales=RONDAS_TOTALES,
                seed=seed,
                simulacion_id=f"enjambre-{seed}-{aumento_pct:g}",
                cobertura_llm=cobertura if modo == "llm" else None,
                tasa_informalidad_inicial=informalidad_observada(_RAIZ / "data" / "momentos.json"),
                n_parafrasis=parafrasis,
                al_decidir_arquetipo=al_decidir,
                al_terminar_ronda=al_terminar,
                al_empezar_trayectoria=al_empezar_trayectoria,
            )
            if not rondas:
                eventos.put(
                    ("error", {"mensaje": "ninguna trayectoria alcanzó a terminar"})
                )
                return
            # Acá salen las rondas al cable, todas juntas y no mientras se
            # calculaban: son las de la trayectoria MEDIANA, con la banda entre
            # las N puesta encima por `consolidar_trayectorias()`. La mediana y
            # no la media, porque la mediana es una trayectoria que de verdad
            # ocurrió y la media no corresponde a ninguna.
            for r in rondas:
                ev = serializar.evento_ronda(r, arquetipos, aumento_pct)
                _imprimir_ronda("mediana · ", ev)
                eventos.put(("ronda", ev))
            gasto: dict[str, Any] = {"segundos": round(time.time() - t0, 1), "modo": modo}
            # Con cuántas trayectorias se construyó la banda que acaba de salir.
            # Si el tope duro cortó a mitad, `efectivas` < `pedidas` y con menos
            # de 2 la banda ya no es la de entre trayectorias: `banda.tipo` lo
            # dice en el contrato y esto lo dice en el informe de la corrida.
            gasto["trayectorias_pedidas"] = trayectorias
            gasto["trayectorias_efectivas"] = n_efectivas
            gasto["banda_tipo"] = rondas[-1].banda.get("tipo", "degenerada")
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
        f"cobertura {cobertura:g} · {trayectorias} trayectorias × {parafrasis} "
        f"paráfrasis · {total} arquetipos ==="
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
                # De cuántas trayectorias saldrá la banda. La pantalla lo
                # necesita para no prometer una banda que no se va a pagar.
                "trayectorias": trayectorias,
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
