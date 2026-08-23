"""Humo contra el deploy: ¿la URL pública transmite una corrida de verdad?

    python3 scripts/humo_deploy.py https://enjambre-web-xxxx.onrender.com

Qué prueba, y por qué esto y no un `curl` a la home. La interfaz es 100% cliente
y habla con el motor por `/api/...`, que el servidor de Next reescribe hacia la
API de Python. O sea que hay CUATRO piezas entre el juez y el resultado —
navegador, Next, proxy, FastAPI— y la home puede cargar perfecto con el motor
caído. Esto ejercita la cadena completa: abre el SSE, consume los eventos a
medida que llegan y verifica que la simulación cierra sus rondas.

Corre en `modo=reglas`: la ablación determinista del repo, sin una sola llamada
al LLM. Cuesta $0, tarda ~1 s y sirve de humo cuantas veces haga falta. Con
`--llm` corre el camino del producto — eso SÍ gasta créditos de Anthropic y
tarda minutos; se usa para el calentamiento antes del pitch (deja la caché del
contenedor tibia) y para comprobar que un stream largo no se corta.

Depende solo de la stdlib: se puede correr desde una máquina sin el repo
instalado, que es justo lo que hay que poder hacer si el deploy se cae en vivo.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request

TIEMPO_LIMITE = 600  # s. Una corrida LLM con 5 parafrasis puede tardar minutos.


def _abrir(url: str, tiempo_limite: int = 30):
    pedido = urllib.request.Request(url, headers={"Accept": "*/*"})
    return urllib.request.urlopen(pedido, timeout=tiempo_limite)


def _prefijo(base: str) -> str:
    """`/api` si la URL es la del frontend; vacío si apunta a la API directo.

    Se detecta en vez de pedirse por bandera para que el mismo comando sirva
    para los dos servicios: el que importa es el del frontend (es la cadena
    completa), pero cuando algo falla lo primero es preguntarle a la API sola.
    """
    # Se guarda POR QUÉ falló cada intento en vez de tragárselo. `URLError`
    # cubre desde "el servicio está caído" hasta "tu certificado local está
    # roto", y el mensaje de antes decía lo mismo para los dos: quien corría
    # esto veía «el deploy no responde» cuando el problema era su propia
    # máquina. Un diagnóstico que apunta al lugar equivocado cuesta más que no
    # tener diagnóstico.
    motivos: list[str] = []
    for p in ("/api", ""):
        try:
            with _abrir(f"{base}{p}/poblacion") as r:
                if r.status == 200:
                    return p
                motivos.append(f"{base}{p}/poblacion -> HTTP {r.status}")
        except urllib.error.HTTPError as e:
            motivos.append(f"{base}{p}/poblacion -> HTTP {e.code} {e.reason}")
        except urllib.error.URLError as e:
            motivos.append(f"{base}{p}/poblacion -> {type(e.reason).__name__}: {e.reason}")
        except TimeoutError:
            motivos.append(f"{base}{p}/poblacion -> timeout")
    detalle = "\n  ".join(motivos)
    raise SystemExit(
        f"FALLO · ni {base}/api/poblacion ni {base}/poblacion respondieron 200:\n  {detalle}"
    )


def _eventos(respuesta):
    """Parte el stream SSE en (evento, datos) a medida que llega.

    No se acumula el cuerpo entero a propósito: si esto se leyera de un golpe,
    un stream que se corta a la mitad se vería igual que uno completo, que es
    exactamente el fallo que este script existe para cazar.
    """
    nombre = None
    for cruda in respuesta:
        linea = cruda.decode("utf-8").rstrip("\n")
        if linea.startswith(":"):  # latido del servidor
            continue
        if linea.startswith("event:"):
            nombre = linea[6:].strip()
        elif linea.startswith("data:") and nombre:
            yield nombre, json.loads(linea[5:].strip())
            nombre = None


def main() -> int:
    p = argparse.ArgumentParser(description="Humo de la corrida contra el deploy.")
    p.add_argument("url", help="URL base del servicio (sin barra final)")
    p.add_argument("--aumento", type=float, default=23.0, help="alza en %% (default: 23)")
    p.add_argument("--parafrasis", type=int, default=1)
    p.add_argument(
        "--llm",
        action="store_true",
        help="corre el camino del producto en vez de la ablacion. GASTA creditos de Anthropic.",
    )
    args = p.parse_args()
    base = args.url.rstrip("/")
    modo = "llm" if args.llm else "reglas"

    print(f"\n=== humo contra {base} · modo {modo} · aumento {args.aumento:g}% ===\n")
    pref = _prefijo(base)
    print(f"[1/3] {base}{pref}/poblacion responde · prefijo detectado: {pref or '(ninguno)'}")

    with _abrir(f"{base}{pref}/poblacion") as r:
        pob = json.loads(r.read())
    esperadas = int(pob["rondas_totales"])
    print(
        f"      {len(pob['arquetipos'])} arquetipos · "
        f"{pob['peso_total']:,.0f} trabajadores · "
        f"informalidad observada {pob['tasa_informalidad_observada']:.2%} · "
        f"{esperadas} rondas de {pob['meses_por_ronda']} meses"
    )

    q = (
        f"aumento_pct={args.aumento:g}&seed=42&modo={modo}"
        f"&parafrasis={args.parafrasis}&cobertura=0.8"
    )
    print(f"\n[2/3] abriendo el flujo: {pref}/simulaciones/flujo?{q}")
    t0 = time.time()
    rondas: list[dict] = []
    decisiones = 0
    inicio = fin = None
    error = None

    with _abrir(f"{base}{pref}/simulaciones/flujo?{q}", TIEMPO_LIMITE) as r:
        for nombre, datos in _eventos(r):
            if nombre == "inicio":
                inicio = datos
                print(f"      inicio · {datos['n_arquetipos']} celdas · modo {datos['modo']}")
            elif nombre == "decision":
                decisiones += 1
            elif nombre == "ronda":
                rondas.append(datos)
                c = datos["contrato"]
                print(
                    f"      ronda {c['ronda']} · informalidad {c['tasa_informalidad']:.2%}"
                    f" · empleo {c['empleo_relativo']:.2%}"
                    f" · p(sancion) {c['prob_fiscalizacion']:.2%}"
                    f" · fallback {datos['fraccion_fallback']:.1%}"
                    f"   [{time.time() - t0:5.1f}s]"
                )
            elif nombre == "fin":
                fin = datos
            elif nombre == "error":
                error = datos

    segundos = time.time() - t0
    print(f"\n[3/3] el stream cerro solo, a los {segundos:.1f}s\n")

    fallos = []
    if error:
        fallos.append(f"el motor reporto error: {error.get('mensaje')}")
    if inicio is None:
        fallos.append("nunca llego el evento `inicio`")
    if inicio and inicio.get("modo") != modo:
        fallos.append(f"se pidio modo={modo} y el servidor corrio {inicio.get('modo')}")
    if decisiones == 0:
        fallos.append("ninguna celda emitio `decision`: no hubo progreso intra-ronda")
    if len(rondas) != esperadas:
        fallos.append(f"llegaron {len(rondas)} rondas y /poblacion declara {esperadas}")
    if fin is None:
        fallos.append("el stream termino sin evento `fin`: se corto a la mitad")
    if rondas:
        r0 = rondas[0]["contrato"]["tasa_informalidad"]
        observada = pob["tasa_informalidad_observada"]
        # La ronda 0 es la proyeccion oficial: arranca donde la encuesta dejo la
        # informalidad. Si no coincide, el deploy no esta leyendo los datos reales.
        if abs(r0 - observada) > 5e-4:
            fallos.append(f"la ronda 0 arranca en {r0:.4f} y la GEIH dice {observada:.4f}")

    if fin:
        print(
            f"      {decisiones} decisiones · {len(rondas)} rondas · "
            f"{fin.get('llamadas_api', 0)} llamadas a la API · "
            f"${fin.get('gasto_usd', 0):.4f} · "
            f"cache {fin.get('cache_aciertos', 0)} aciertos / {fin.get('cache_fallos', 0)} fallos"
        )
    if rondas:
        ult = rondas[-1]["contrato"]
        # `banda.tipo` solo existe cuando hubo mas de una parafrasis; con una
        # sola el motor emite {p10, p90, degenerada} y nada mas. Se lee con
        # `.get` para que el humo no reviente justo en la corrida barata.
        banda = ult["banda"]
        etiqueta = banda.get("tipo") or ("degenerada" if banda.get("degenerada") else "con ancho")
        print(
            f"      final: informalidad {ult['tasa_informalidad']:.2%} · "
            f"empleo {ult['empleo_relativo']:.2%} · "
            f"banda {etiqueta} [{banda['p10']:.2%}, {banda['p90']:.2%}] · "
            f"estabilizada={ult['estabilizada']}"
        )

    if fallos:
        print("\nFALLO:")
        for f in fallos:
            print(f"  · {f}")
        return 1
    print(f"\nOK · la cadena completa transmite ({segundos:.1f}s, modo {modo})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
