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
import math
import queue
import threading
import time
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable, Iterator

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from api import serializar
from behavior.ablacion import ClienteReglas
from behavior.arquetipos import (
    desde_empresas,
    informalidad_observada,
    particionar_por_peso,
    poblacion_cuenta_propia,
)
from behavior.cache import Cache
from behavior.cliente import ClienteConductual, SinCredenciales
from behavior.presupuesto import USD_POR_LLAMADA_MEDIDO, Presupuesto
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

# Qué gobierna la perilla `seed` de esta API.
#
# Hasta el 23-ago era "etiqueta", y estaba medido: `modo=reglas`, seed 42 contra
# seed 99, las 4 rondas comparadas campo por campo -> trayectorias IDÉNTICAS
# (informalidad final 31,01% en ambas). En el camino del LLM no podía ser de
# otra forma: `capa.renderizar()` no recibía seed, así que el prompt no lo
# llevaba, y como `cache.clave()` hashea el prompt, dos semillas eran dos
# aciertos del mismo caché.
#
# Eso cambió: `behavior/contexto.py` sortea con el seed el contexto
# idiosincrático de cada firma —quién le compra, cómo viene la venta, contra
# quién compite— y ese texto entra al prompt. Dos semillas son ahora dos
# poblaciones de firmas distintas sobre los mismos arquetipos, que es lo que la
# perilla siempre dijo que hacía. `engine/seed.py` sigue teniendo los streams
# buenos y sigue sin importarlo nadie fuera de su propio test.
#
# ⚠️ En el camino de REGLAS FIJAS (`behavior/ablacion.py`) la perilla sigue
# siendo una etiqueta, y a propósito: la ablación no lee el prompt. Esa es
# justamente la comparación que la hace útil.
SEED_EFECTO = "trayectoria"  # "etiqueta" | "trayectoria"

# La otra perilla que hoy no hace nada, y esta la rompí yo en este mismo PR.
# `api/trayectorias.py` fija en qué paráfrasis corre cada trayectoria
# reemplazando `behavior.capa.parafrasis` por una lambda que devuelve UNA, y esa
# lambda ignora el `n` que le pasan. Río abajo, `behavior/capa.py:250` hace
# `for instruccion in parafrasis(n_parafrasis)`, o sea una sola vuelta pase lo
# que pase: `parafrasis` queda neutralizado en el camino de trayectorias.
# No es un bug que se arregle: es una incoherencia de diseño. Una trayectoria
# ESTÁ DEFINIDA por su paráfrasis, así que pedir N paráfrasis adentro de una
# trayectoria no quiere decir nada. La banda que se publica es la de entre
# trayectorias justamente porque reemplazó a la intra-ronda, que era la angosta.
# Se declara en vez de disimularse, igual que `SEED_EFECTO`, y se saca de la
# cuenta del presupuesto: una perilla que no multiplica llamadas no puede
# multiplicar el tope.
PARAFRASIS_EFECTO = "ninguno"  # "ninguno" | "intra_ronda"

# El tope de gasto de UNA corrida, derivado de la corrida QUE SE PIDIÓ. V-1.
#
# Lo medido (R3, 23-08-2026, `behavior/README.md` §Costo): una corrida en frío
# con `claude-sonnet-5` sobre la grilla real y cobertura 0,80 son **94 llamadas
# y USD 1,26**, o sea USD 0,0134 por llamada.
#
# Por qué el tope no puede ser UN número. El tope que había era 3,00 —el mismo
# literal que `behavior.presupuesto`, dos fuentes cuadrando por casualidad
# (S2-9)— y venía de cuando una corrida era UNA trayectoria. Con 5 se agotaba
# cerca de la segunda. Pero subirlo a un número más grande solo mueve el
# problema: un número fijo o corta una corrida legítima (y entonces miente) o
# deja pasar una corrida desbocada (y entonces cuesta). Los dos modos de falla
# existen porque el costo de la corrida NO es constante: depende de la cobertura
# top-K, de cuántas trayectorias se pidieron y de cuántas paráfrasis por ronda.
#
# Lo grave del tope corto no era que la corrida se parara. `correr_consolidada()`
# consolida con las trayectorias que alcanzaron, así que la corrida TERMINABA
# bien y publicaba una banda sobre 2 donde el contrato promete la de 5. Un tope
# mal puesto no se ve como un error, se ve como un resultado.
#
# Entonces el tope se calcula por request, con la cuenta EXACTA de llamadas que
# esa corrida va a hacer: `particionar_por_peso()` dice cuántas celdas entran al
# LLM con esa cobertura (no es una estimación, es la misma función que usa el
# motor). Así el corte no salta nunca en una corrida legítima —o sea que si
# salta, algo se desbocó— y una corrida barata no queda autorizada a gastar como
# la cara.
#
# SUPUESTO: el costo por llamada es el de la medición y se supone estable entre
# celdas. El margen cubre que la medición es UNA corrida (el largo de la
# respuesta varía).
#
# El número viejo era `1.26 / 94 = 0,0134` y salía de una medición que no es la
# del modelo que hoy corre. Se corrigió a `7,8731 / 518 = 0,0152` con la corrida
# pagada del 23-ago, Y ESO TAMBIÉN QUEDÓ CORTO: la corrida de verificación de la
# maqueta (23-ago, aumento 17%, cobertura 0,50, 2 trayectorias) gastó USD 0,9742
# en 50 llamadas, o sea USD 0,0195 — 28% por encima. El tope derivado de USD 0,96
# la cortó y publicó `trayectorias_efectivas: 1` sobre 2 pedidas, con
# `banda_tipo: "degenerada"`. Exactamente la falla que este bloque existe para
# evitar, ocurrida DESPUÉS del primer arreglo.
#
# POR QUÉ NO ES RUIDO, y esto es lo que importa: el costo por llamada NO es
# constante entre configuraciones, porque `cobertura` no elige un número de
# celdas, elige CUÁLES.
#
#   | corrida                        | USD/llamada | factor de reintento |
#   |--------------------------------|-------------|---------------------|
#   | cobertura 0,80 x 5 (completa)  |     0,01520 |               1,11x |
#   | cobertura 0,50 x 2 (cortada)   |     0,01948 |        >= 1,58x     |
#
# Con cobertura 0,50 el top-K se queda con las 9 celdas MÁS GRANDES: prompts más
# largos y más vetos, o sea más caro por llamada Y más reintentos. Con cobertura
# 1,00 entran también las celdas chicas, que son baratas. Bajar la cobertura
# encarece cada llamada.
#
# Entonces el tope se calibra sobre el PEOR caso medido y no sobre el promedio.
# Un tope es un colchón, no un pronóstico: equivocarse hacia arriba cuesta
# headroom que no se gasta, y equivocarse hacia abajo publica una banda que no
# se pagó. Consecuencia declarada: para las corridas de cobertura alta este tope
# sobreestima (la completa deriva USD 18,14 y costó USD 7,87 reales). No se
# interpola entre las dos mediciones porque dos puntos no son una curva, y el
# repo no inventa números.
# El número vive en `behavior/presupuesto.py`, que es donde se lleva la
# contabilidad, y acá se IMPORTA. Tener dos copias del costo por llamada en dos
# archivos es exactamente el defecto S2-9 que el repo ya sufrió con el literal
# 3,00: cuadran hasta el día que alguien actualiza una sola.
USD_POR_LLAMADA_EN_FRIO = USD_POR_LLAMADA_MEDIDO
MARGEN_TOPE = 1.25

# SUPUESTO: cada corrida hace ~1,4 veces las llamadas que estaban previstas.
#
# `llamadas_de_la_corrida()` cuenta UNA llamada por celda-ronda, y eso es cierto
# solo si ninguna decisión se reintenta. Pero `behavior.capa.MAX_REINTENTOS = 3`
# y cada veto de factibilidad dispara una llamada nueva, así que el gasto real
# vive por encima del conteo. Medido, tres corridas distintas:
#
#   | corrida                              | previstas | reales | factor |
#   |--------------------------------------|-----------|--------|--------|
#   | pagada (cobertura 0,80, 5 tray.)     |       465 |    518 |  1,11x |
#   | camino LLM desde caché               |        93 |    122 |  1,31x |
#   | maqueta 17% (cobertura 0,50, 2 tray.)|        36 |  57 (*)| 1,58x (*)|
#   | ablación al 23%                      |        93 |    219 |  2,35x |
#
# (*) COTA INFERIOR: esa corrida se cortó por presupuesto antes de terminar la
# segunda trayectoria, así que 57 prompts únicos sobre 36 previstas es lo que
# alcanzó a intentar, no lo que necesitaba. El factor verdadero de esa
# configuración es MAYOR que 1,58.
#
# 1,6 se pone justo encima de esa cota inferior y por debajo del 2,35x de la
# ablación, que no gasta. Empezó en 1,4 —encima del 1,31x del camino de caché— y
# la corrida de verificación demostró que no alcanzaba: con 1,4 el tope de la
# maqueta quedó en USD 0,96 y la corrida gastó USD 0,9742. Sin este factor
# quedaba peor todavía: `tope_derivado(0,50, 2)` daba USD 0,60 contra USD 0,72.
# La corrida pagada del 23-ago costó USD 7,87 contra un tope de USD 7,79: se
# habría cortado a sí misma.
#
# Y cortarse no se ve como un error. `correr_consolidada()` consolida con las
# trayectorias que alcanzaron, así que la corrida TERMINA bien y publica una
# banda sobre menos trayectorias de las que prometió. Un tope mal puesto no se
# ve como falla: se ve como resultado.
FACTOR_REINTENTO = 1.6

# El techo absoluto, y la única cifra de acá que es un juicio y no una cuenta.
# El equipo tiene ~USD 230 vivos entre los 5 (2026-08-23).
#
# Sube de 25 a 35 al corregir el costo por llamada, y sube para NO romper el
# invariante que el equipo ya había escrito en
# `api/test_trayectorias.py::test_el_tope_paga_la_corrida_que_promete`: el techo
# no puede prohibir la mejor corrida. La corrida de máxima calidad —cobertura
# 1,00, las 81 celdas, 5 trayectorias, 1215 llamadas— derivaba USD 20,36 con los
# números viejos y deriva USD 32,32 con los buenos; con el techo en 25 quedaba
# imposible de pedir incluso pasando `tope_usd` a mano, porque el mismo techo
# acota ese parámetro.
#
# Subir el techo NO autoriza gasto nuevo en el camino normal: el techo no
# gasta, solo deja de rechazar. Lo que se gasta lo fija la corrida que se pide,
# y la que se pide es cobertura 0,80 x 5 trayectorias — USD 12,37 derivados,
# USD 7,87 REALES medidos el 23-ago. La de 1,00 nunca se ha corrido y además es
# la más lenta (81 celdas = 21 olas, ~8 min), así que no es la corrida de la
# demo ni de la validación: es el máximo que el presupuesto debe poder cubrir
# sin clipar, que es exactamente lo que un techo describe.
#
# 35 es el 15% de la bolsa del equipo, contra el 11% de antes: sigue siendo el
# peor caso individual que el proyecto puede absorber sin que una sola corrida
# se coma la tarde de otro.
TOPE_USD_MAXIMO = 35.0


def celdas_al_llm(cobertura: float) -> int:
    """Cuántas celdas de la grilla entran al LLM con esa cobertura top-K.

    No es una estimación: es la misma `particionar_por_peso()` que usa el motor.
    La usan el conteo de llamadas y el paralelismo, que TIENEN que estar de
    acuerdo — el tiempo de una corrida no lo fija cuántas celdas hay, lo fija
    cuántas OLAS de llamadas ocurren, y una ola es `celdas / paralelismo`.
    """
    celdas, _cola = particionar_por_peso(_grilla(), cobertura)
    return len(celdas)


def llamadas_de_la_corrida(
    cobertura: float, trayectorias: int, rondas: int = RONDAS_TOTALES
) -> int:
    """Cuántas llamadas al LLM tiene PREVISTAS esta corrida. Exacto, no estimado.

    La ronda 0 es la reacción ingenua y no llama al LLM (ADR 0005), así que las
    rondas que cuestan son `rondas - 1`. `parafrasis` NO entra: ver
    `PARAFRASIS_EFECTO`.

    A propósito NO lleva `FACTOR_REINTENTO`: esta cifra es el PISO exacto y se
    publica como tal en el evento `inicio`. Lo que el veto reintenta se paga
    pero no estaba previsto; meterle el factor acá convertiría un conteo en una
    estimación y la pantalla dejaría de tener un número que pueda defender.
    El factor vive donde corresponde, en `tope_derivado()`.
    """
    return celdas_al_llm(cobertura) * (rondas - 1) * trayectorias


def reserva_en_vuelo(cobertura: float, trayectorias: int) -> float:
    """Lo que `Presupuesto.reservar()` tiene apartado en el pico. En USD.

    Desde que el corte de presupuesto es atómico (DEFECTOS.md §3.7), cada
    llamada en vuelo tiene plata APARTADA que todavía no se gastó. En el pico
    hay `paralelismo x trayectorias` llamadas volando a la vez, así que ese
    monto no está disponible para autorizar la siguiente.

    Si no se sumara al tope, la garantía de no-sobregiro se pagaría cortando
    corridas legítimas: la maqueta necesita ~USD 1,21 y con 18 llamadas en vuelo
    tendría USD 0,35 congelados, o sea que se cortaría a sí misma otra vez. Va
    como término APARTE y no dentro de `MARGEN_TOPE` porque mide otra cosa: el
    margen cubre que el costo por llamada varía, esto cubre que hay llamadas sin
    liquidar. Cada término, un trabajo.
    """
    concurrencia = paralelismo_de_la_corrida(cobertura, trayectorias) * trayectorias
    return concurrencia * USD_POR_LLAMADA_EN_FRIO


def tope_derivado(
    cobertura: float, trayectorias: int, rondas: int = RONDAS_TOTALES
) -> float:
    """Lo que esta corrida va a costar en frío de verdad, con margen. En USD.

    `piso exacto × reintentos medidos × margen + reserva en vuelo`. Los cuatro
    términos están separados porque miden cosas distintas: el primero se cuenta,
    el segundo se midió en tres corridas, el tercero es el colchón declarado y
    el cuarto es la plata que la atomicidad del corte mantiene apartada.
    """
    n = llamadas_de_la_corrida(cobertura, trayectorias, rondas)
    esperado = n * USD_POR_LLAMADA_EN_FRIO * FACTOR_REINTENTO
    return round(
        esperado * MARGEN_TOPE + reserva_en_vuelo(cobertura, trayectorias), 2
    )


# Cuántas celdas resuelve a la vez CADA trayectoria, y el techo total de
# conexiones simultáneas contra el proveedor.
#
# Por qué esto existe: hasta hoy `paralelismo` no era perilla de la API — se
# quedaba en el default 8 de `behavior.rondas.correr()` y `grep -n paralelismo
# api/servidor.py` daba cero. Eso hacía que bajar la cobertura NO bajara el
# tiempo, que es justo lo que la demo necesita. La aritmética que manda no es
# cuántos agentes hay, es cuántas OLAS de llamadas ocurren:
#
#     olas   = ceil(celdas / paralelismo) x (rondas - 1)
#     tiempo ~ olas x 23,3 s        (23,3 s/llamada: medido, 1398 s / 60 olas)
#
# Con 9 celdas y el default 8 son 2 olas por ronda, no 1, y la maqueta no cabe
# en la demo. Con `paralelismo = celdas` es 1 ola por ronda: 3 rondas totales
# (2 con LLM) = 2 olas ~ 47 s.
#
# Los dos techos son distintos y los dos hacen falta:
#   - `TECHO_PARALELISMO` acota UNA trayectoria. 31 conexiones simultáneas no
#     están probadas contra este proveedor y el rate limit de la cuenta se
#     desconoce.
#   - `TECHO_CONEXIONES` acota el producto, que es lo que de verdad llega a la
#     red: las N trayectorias corren en paralelo entre sí desde a4e1429, así que
#     las conexiones vivas son `paralelismo x trayectorias`. 40 no es un número
#     de gusto: es el punto que YA se corrió sano (8 x 5 en la corrida pagada del
#     23-ago, ~5 min sin errores de rate limit). No se autoriza más de lo medido.
TECHO_PARALELISMO = 12
TECHO_CONEXIONES = 40


def paralelismo_de_la_corrida(cobertura: float, trayectorias: int) -> int:
    """Cuántas celdas en vuelo por trayectoria, sin pasarse de lo ya probado.

    Con la cobertura por defecto (0,80 -> 31 celdas, 5 trayectorias) devuelve 8,
    o sea exactamente el default de antes: esto no cambia la corrida completa,
    solo deja de desperdiciar paralelismo cuando hay pocas celdas.
    """
    return max(
        1,
        min(
            celdas_al_llm(cobertura),
            TECHO_PARALELISMO,
            TECHO_CONEXIONES // max(1, trayectorias),
        ),
    )


def perfil_de_la_corrida(cobertura: float, trayectorias: int, rondas: int) -> str:
    """`"completo"` o `"maqueta"`. Va en el evento `inicio` para que se pueda decir.

    No es cosmético y no es "el simulador más pequeño": es OTRA corrida. La
    respuesta del modelo a la política es escalonada (medido: +3,25 pp idéntico
    en 5/10/12%, +6,07 pp idéntico en 23/30%), así que cambiar QUÉ celdas deciden
    puede saltar de escalón entero. Un resultado de maqueta que se muestre sin
    rótulo es un resultado distinto presentado como el mismo.
    """
    completo = (
        rondas == RONDAS_TOTALES
        and cobertura >= 0.8
        and trayectorias >= N_TRAYECTORIAS
    )
    return "completo" if completo else "maqueta"


app = FastAPI(title="enjambre-api", docs_url=None, redoc_url=None)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # sin auth ni registro: regla no-negociable del repo
    allow_methods=["GET"],
    allow_headers=["*"],
)

# SUPUESTO: una toma de más de 15 minutos ya no representa una corrida sana. Desde
# a4e1429 las 5 trayectorias corren en paralelo y una corrida LLM completa tarda
# ~5 minutos (antes eran ~23), así que el margen es 3x sin condenar el proceso:
# el 23-ago un stream abandonado dejó la URL pública bloqueada durante ~2 horas.
UMBRAL_CANDADO_HUERFANO_SEGUNDOS = 15 * 60


class GuardianCorrida:
    """Excluye corridas concurrentes sin convertir un stream muerto en un bloqueo eterno.

    Cada toma recibe un token. Recuperar un huérfano reemplaza ese token dentro
    del mismo tramo protegido que comprueba su edad; por eso dos peticiones no
    pueden heredar el mismo turno. El token también evita que el `finally` tardío
    del stream viejo suelte la corrida nueva que lo reemplazó.
    """

    def __init__(
        self,
        umbral_segundos: float = UMBRAL_CANDADO_HUERFANO_SEGUNDOS,
        reloj: Callable[[], float] = time.monotonic,
    ) -> None:
        self._umbral_segundos = umbral_segundos
        self._reloj = reloj
        self._candado = threading.Lock()
        self._estado = threading.Lock()
        self._turno: object | None = None
        self._tomado_en: float | None = None

    def adquirir(self) -> tuple[object | None, float]:
        """Toma o recupera el turno; devuelve token y antigüedad previa en segundos."""
        with self._estado:
            ahora = self._reloj()
            if self._candado.acquire(blocking=False):
                self._turno = object()
                self._tomado_en = ahora
                return self._turno, 0.0

            # El reloj monotónico no retrocede por ajustes de hora del sistema;
            # `max` deja el guardián seguro también ante un reloj falso defectuoso.
            tomado_en = ahora if self._tomado_en is None else self._tomado_en
            antiguedad = max(0.0, ahora - tomado_en)
            if antiguedad <= self._umbral_segundos:
                return None, antiguedad

            # Nadie puede observar el candado libre entre estas dos operaciones:
            # ambas ocurren bajo `_estado`, que gobierna todas sus transiciones.
            self._candado.release()
            self._candado.acquire()
            self._turno = object()
            self._tomado_en = ahora
            print(
                "[candado] recuperado candado huérfano tras "
                f"{antiguedad:.1f} segundos tomado"
            )
            return self._turno, antiguedad

    def soltar(self, turno: object | None) -> None:
        """Suelta solo el turno propio; un `finally` obsoleto es inocuo."""
        with self._estado:
            if turno is None or turno is not self._turno:
                return
            self._turno = None
            self._tomado_en = None
            self._candado.release()


# Una corrida a la vez: el motor satura los hilos y el presupuesto es uno solo.
_ocupado = GuardianCorrida()


@lru_cache(maxsize=1)
def _grilla():
    return desde_empresas(_RAIZ / "data" / "empresas.parquet", _RAIZ / "data" / "momentos.json")


@lru_cache(maxsize=1)
def _cuenta_propia():
    return poblacion_cuenta_propia(_RAIZ / "data" / "poblacion.parquet")


# La caché versionada del escenario del demo, si alguien la dejó en el repo.
#
# Por qué acá y no en un script: la caché en disco vive en la MÁQUINA que corre
# el motor, y quien corre el motor es este proceso. Warmear la caché en un
# portátil no calienta el deploy; `behavior/cache-demo.json` es la única forma
# de que una corrida ya pagada viaje con el repositorio. Hoy solo la importaba
# `scripts/reproduce.py`, o sea que el deploy arrancaba siempre en frío.
#
# El archivo NO existe todavía (`DEFECTOS.md` 3.6 lo tiene abierto). Cuando
# exista, esto lo levanta solo y el demo deja de depender de que nadie mueva el
# slider a una posición nueva. Si no existe, no pasa nada y la corrida es en
# frío, que es exactamente lo de hoy.
_CACHE_DEMO = _RAIZ / "behavior" / "cache-demo.json"


def _precargar_cache_demo() -> int:
    """Mete la caché versionada en la caché de disco. Devuelve cuántas entradas.

    El origen es un archivo del propio repositorio, no entrada de usuario: no
    hay ruta pública que llame a `Cache.importar()` con algo de afuera, y esto
    no abre una.
    """
    if not _CACHE_DEMO.is_file():
        return 0
    n = Cache().importar(_CACHE_DEMO)
    print(f"[caché] {n} entradas precargadas desde {_CACHE_DEMO.name}")
    return n


_precargar_cache_demo()


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
            "Elige el contexto idiosincrático de cada firma (quién le compra, "
            "cómo viene la venta, contra quién compite) y por lo tanto la "
            "trayectoria. En el camino de reglas fijas sigue siendo solo un "
            "rótulo, porque la ablación no lee el prompt. Ver `SEED_EFECTO`."
        ),
    ),
    cobertura: float = Query(
        0.8,
        gt=0.0,
        le=1.0,
        description=(
            "Fracción de la POBLACIÓN cuyas celdas deciden con el LLM (top-K por "
            "peso); el resto se resuelve con las reglas fijas de la ablación. "
            "SUPUESTO: el 0,8 es un CORTE DE PRESUPUESTO, no una propiedad del "
            "modelo. Con 0,80 son 31 celdas de 81 y la corrida cuesta USD 7,87 "
            "medidos; con 1,00 son las 81 y ~USD 20. No hay ningún hallazgo que "
            "diga que el 80% de la población basta para representar al 100%: se "
            "eligió para que una corrida quepa en la bolsa del equipo, y la "
            "pantalla lo muestra como «población decidida por LLM» justamente "
            "para que la cifra viaje con esa procedencia. El supuesto sobre "
            "cómo se resuelve la cola sí está marcado aparte, en "
            "`behavior/arquetipos.py`."
        ),
    ),
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
            "HOY NO HACE NADA en este endpoint, y se declara en vez de "
            "quitarse: ver `PARAFRASIS_EFECTO`. Fijar la paráfrasis de cada "
            "trayectoria neutraliza este parámetro río abajo, así que ni "
            "multiplica el costo ni llena `banda_intra_ronda`. La banda que se "
            "publica es la de ENTRE trayectorias, que es la que reemplazó a esta."
        ),
    ),
    rondas: int = Query(
        RONDAS_TOTALES,
        ge=2,
        le=RONDAS_TOTALES,
        description=(
            "Cuántas rondas corre el motor, contando la 0. La ronda 0 es la "
            "reacción ingenua y no llama al LLM (ADR 0005), así que las rondas "
            "que cuestan son `rondas - 1`. Bajarla a 3 es la mitad de la "
            "maqueta de demo: 2 rondas con LLM en vez de 3. La elección viaja "
            "en el evento `inicio` (`rondas` y `perfil`) para que la pantalla "
            "pueda decir cuántas dibuja en vez de suponerlo."
        ),
    ),
    tope_usd: float | None = Query(
        None,
        gt=0.0,
        le=TOPE_USD_MAXIMO,
        description=(
            "Corte DURO de gasto para la corrida ENTERA, no por trayectoria. "
            "Vacío = se deriva de la corrida que se pidió (celdas × rondas con "
            "LLM × trayectorias × USD 0,0195 medidos × 1,6 de reintentos del "
            "veto × 1,25 de margen), que es lo que se quiere casi siempre: así "
            "el corte no "
            "salta nunca en una corrida legítima y saltar significa que algo se "
            "desbocó. Si salta, la corrida se consolida con las trayectorias "
            "que alcanzaron y `trayectorias_efectivas` lo declara en `fin`."
        ),
    ),
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
            aumento_pct,
            seed,
            cobertura,
            trayectorias,
            parafrasis,
            rondas,
            tope_usd,
            modo,
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
    rondas: int,
    tope_usd: float | None,
    modo: str,
) -> Iterator[str]:
    # El tope, antes del candado y antes de gastar un peso. Si la corrida que
    # pidieron no cabe en el techo, se dice CUÁNTO cuesta y QUÉ bajar, en vez de
    # correrla a medias y publicar una banda sobre menos trayectorias de las
    # prometidas.
    llamadas_previstas = llamadas_de_la_corrida(cobertura, trayectorias, rondas)
    derivado = tope_derivado(cobertura, trayectorias, rondas)
    paralelismo = paralelismo_de_la_corrida(cobertura, trayectorias)
    perfil = perfil_de_la_corrida(cobertura, trayectorias, rondas)
    if tope_usd is None:
        if derivado > TOPE_USD_MAXIMO:
            yield _sse(
                "error",
                {
                    "mensaje": (
                        f"esta corrida cuesta ~${derivado:.2f} en frío "
                        f"({llamadas_previstas} llamadas) y el techo es "
                        f"${TOPE_USD_MAXIMO:.2f}. Baja `cobertura`, `trayectorias` "
                        f"o `rondas`, o pasa `tope_usd` a mano."
                    )
                },
            )
            return
        tope_usd = derivado

    turno, antiguedad = _ocupado.adquirir()
    if turno is None:
        restante = max(0.0, UMBRAL_CANDADO_HUERFANO_SEGUNDOS - antiguedad)
        yield _sse(
            "error",
            {
                "mensaje": (
                    "ya hay una corrida en curso desde hace "
                    f"{antiguedad / 60:.1f} min; se liberará automáticamente "
                    f"en {restante / 60:.1f} min"
                )
            },
        )
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
            mediana, n_efectivas = correr_consolidada(
                arquetipos,
                cliente,
                n_trayectorias=trayectorias,
                aumento_pct=aumento_pct,
                rondas_totales=rondas,
                seed=seed,
                simulacion_id=f"enjambre-{seed}-{aumento_pct:g}",
                cobertura_llm=cobertura if modo == "llm" else None,
                tasa_informalidad_inicial=informalidad_observada(_RAIZ / "data" / "momentos.json"),
                n_parafrasis=parafrasis,
                paralelismo=paralelismo,
                al_decidir_arquetipo=al_decidir,
                al_terminar_ronda=al_terminar,
                al_empezar_trayectoria=al_empezar_trayectoria,
            )
            if not mediana:
                eventos.put(
                    ("error", {"mensaje": "ninguna trayectoria alcanzó a terminar"})
                )
                return
            # Acá salen las rondas al cable, todas juntas y no mientras se
            # calculaban: son las de la trayectoria MEDIANA, con la banda entre
            # las N puesta encima por `consolidar_trayectorias()`. La mediana y
            # no la media, porque la mediana es una trayectoria que de verdad
            # ocurrió y la media no corresponde a ninguna.
            for r in mediana:
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
            gasto["banda_tipo"] = mediana[-1].banda.get("tipo", "degenerada")
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
    # Cuántas tandas de llamadas concurrentes va a hacer CADA trayectoria. Es la
    # cifra que predice el tiempo de pared (~23,3 s por ola, medido), y no
    # `llamadas_previstas`: las N trayectorias corren en paralelo entre sí.
    olas = math.ceil(celdas_al_llm(cobertura) / paralelismo) * (rondas - 1)
    print(
        f"\n=== corrida: aumento {aumento_pct:g}% · seed {seed} ({SEED_EFECTO}) · "
        f"modo {modo} · "
        f"cobertura {cobertura:g} · {trayectorias} trayectorias × {parafrasis} "
        f"paráfrasis · {total} arquetipos · {rondas} rondas ({perfil}) · "
        f"paralelismo {paralelismo} · {olas} olas · "
        f"~{llamadas_previstas} llamadas · tope ${tope_usd:.2f} ==="
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
                "parafrasis_efecto": PARAFRASIS_EFECTO,
                "n_arquetipos": total,
                # Cuántas rondas dibujar. Antes la pantalla lo sacaba de
                # `/poblacion`, que responde con la constante del módulo: el día
                # que una corrida pidiera menos, la barra de tiempo mentía.
                "rondas": rondas,
                # "completo" | "maqueta". Una corrida de maqueta NO es la misma
                # corrida más pequeña, es otra: ver `perfil_de_la_corrida()`.
                "perfil": perfil,
                # Lo que fija el tiempo de pared, para que se pueda prometer sin
                # adivinar: ~23,3 s por ola, medido.
                "paralelismo": paralelismo,
                "olas_previstas": olas,
                # Lo que esta corrida va a costar y dónde está su corte duro. La
                # pantalla puede decirlo antes de que el usuario espere 15
                # minutos, y el juez que pregunta "¿cuánto les cuesta mover el
                # slider?" tiene el número en el primer evento.
                "llamadas_previstas": llamadas_previstas,
                "tope_usd": tope_usd,
                "tope_derivado_usd": derivado,
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
        _ocupado.soltar(turno)
