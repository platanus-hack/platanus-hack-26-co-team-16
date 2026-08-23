#!/usr/bin/env python3
"""Quien decidio que, y por que — con atribucion por empresa, y a costo cero.

    python3 scripts/informe_decisiones.py

Por que existe
--------------
La cache no sabe quien pregunto. Su clave es un `sha256` de
`{modelo, sistema, usuario, esquema}` (`behavior/cache.py:40`) y el archivo guarda
solo `{modelo, salida, usage}`. Por eso se podian CONTAR las 518 decisiones ya
pagadas pero no ATRIBUIRLAS: no se podia decir "los restaurantes hicieron X"
(limite declarado en `docs/agents/hallazgos-dani-cache-decisiones.md` §5).

Este script cierra ese hueco sin pagar nada. `behavior.rondas.correr()` ya expone
`al_decidir_arquetipo(ronda, arquetipo_id, ResultadoArquetipo)`; ese callback SI
sabe quien pregunto. Corriendo la simulacion con la cache caliente, cada acierto
entrega la atribucion que a la cache le falta.

La cache versionada NO cubre la corrida entera hoy
--------------------------------------------------
MEDIDO al escribir esto: con `cobertura_llm=0.80` y la primera redaccion, una
corrida sobre `main` encuentra la respuesta de ALGUNAS celdas y no de otras. La
cache se pago antes de un cambio que movio la probabilidad de inspeccion por
celda, y esa probabilidad entra al texto del prompt, o sea a la clave. Es el
mismo defecto ya declarado en AGENTS.md para `data/prediccion_modelo.json`.

Consecuencia practica, y esta escrita a proposito en vez de escondida:
`scripts/reproduce.py` **no reproduce sobre `main` hoy** — revienta con
`SinCredenciales` en la primera celda cuya respuesta no esta cacheada.

Como responde este script: cada llamada que la cache NO cubre cae a la ablacion
de reglas fijas (`behavior/ablacion.py`), la fila queda MARCADA con su origen, y
el informe dice cuantas decisiones son del modelo y cuantas de la regla. Un
informe honesto y parcial vale mas que uno completo y falso.

Que NO hace
-----------
No cambia como se calcula nada: es un observador. Y no puede gastar plata: el
cliente se construye con `Presupuesto(tope_usd=0.0)`, asi que una llamada que no
este en cache muere en `comprobar()` ANTES de salir a la red (`cliente.py:149`),
no despues de pagarla.

Salidas en `informes/`:
  decisiones-seed<seed>-<aumento>.json   la tabla completa, una fila por decision
  decisiones-seed<seed>-<aumento>.md     el informe legible
"""

from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path
from typing import Any

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from behavior.ablacion import ClienteReglas  # noqa: E402
from behavior.arquetipos import (  # noqa: E402
    desde_empresas,
    informalidad_observada,
    particionar_por_peso,
)
from behavior.cache import Cache  # noqa: E402
from behavior.cliente import SinCredenciales  # noqa: E402
from behavior.presupuesto import Presupuesto, PresupuestoAgotado  # noqa: E402
from behavior.rondas import correr  # noqa: E402

CACHE_DEMO = RAIZ / "behavior" / "cache-demo.json"
EMPRESAS = RAIZ / "data" / "empresas.parquet"
MOMENTOS = RAIZ / "data" / "momentos.json"
INFORMES = RAIZ / "informes"

# El mismo escenario de `scripts/reproduce.py`. No es una eleccion de este
# script: si se desvia de ahi, la cache falla y la corrida empieza a cobrar.
AUMENTO_DEMO = 23.0
SEED_DEMO = 42
# Los de `api/servidor.py`: la corrida que se pago —y que la gente ve en el
# deploy— manda 4 rondas y solo la CABEZA del 80% del peso al LLM. Correr con
# `cobertura_llm=None`, como hace `scripts/reproduce.py`, pide 81 celdas cuando
# solo se pagaron 31: por ahi tambien se le escapa la cache.
RONDAS_DEMO = 4
COBERTURA_DEMO = 0.80

# Que mueve cada familia, segun el `SUPUESTO:` explicito de
# `behavior/contrato.py:337` ("ninguna otra estrategia cambia el estatus de regla
# de la planta") y `jornada_resultante()` (`contrato.py:269`). Es la columna que
# separa una adaptacion que la pantalla puede mostrar de una que no.
EFECTO: dict[str, str] = {
    "informalizar": "informalidad ↑",
    "cumplir": "informalidad → 0",
    "despedir": "empleo ↓",
    "bajar_horas": "jornada ↓",
    "subir_precios": "NADA en el agregado",
    "absorber": "NADA en el agregado",
    "renegociar": "NADA en el agregado",
    "otra": "sin clasificar",
}
INERTES = {"subir_precios", "absorber", "renegociar"}


class ClienteSoloCache:
    """Sirve de la cache; lo que no este en cache lo resuelve la regla fija.

    Existe por una razon y se dice entera: la cache versionada no cubre la
    corrida completa sobre `main` (ver el docstring del modulo). Sin esto el
    informe seria imposible de generar; con esto es posible y PARCIAL, y cada
    fila dice de cual de las dos fuentes salio.

    No puede gastar: el cliente real lleva `tope_usd=0.0`, asi que una llamada
    fuera de cache muere en `comprobar()` antes de tocar la red. Los dos caminos
    que la sacan de ahi —`SinCredenciales` (no hay key) y `PresupuestoAgotado`
    (si la hay)— terminan en el mismo sitio: la regla fija.
    """

    def __init__(self, llm, reglas: ClienteReglas) -> None:
        self._llm = llm
        self._reglas = reglas
        self.presupuesto = llm.presupuesto
        # (agente_id, ronda) -> "llm-cache" | "reglas"
        self.origen: dict[tuple[str, int], str] = {}
        self.aciertos = 0
        self.caidas = 0

    def proponer(self, sistema: str, usuario: str, *a, **kw):
        ctx = kw.get("contexto") or {}
        arq = ctx.get("arquetipo")
        clave = (getattr(arq, "id", "?"), int(ctx.get("ronda", -1)))
        try:
            salida = self._llm.proponer(sistema, usuario, *a, **kw)
        except (SinCredenciales, PresupuestoAgotado):
            self.caidas += 1
            self.origen[clave] = "reglas"
            return self._reglas.proponer(sistema, usuario, *a, **kw)
        self.aciertos += 1
        # Una celda con varios votos puede mezclar; si alguno cayo a reglas, la
        # celda queda marcada como mezclada y no se presenta como del modelo.
        if self.origen.get(clave) == "reglas":
            self.origen[clave] = "mezcla"
        else:
            self.origen.setdefault(clave, "llm-cache")
        return salida


def _pct(parte: float, total: float) -> float:
    return 100.0 * parte / total if total else 0.0


def _tabla(filas: list[list[str]], encabezado: list[str]) -> str:
    out = ["| " + " | ".join(encabezado) + " |",
           "|" + "|".join("---" for _ in encabezado) + "|"]
    out += ["| " + " | ".join(f) + " |" for f in filas]
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--aumento", type=float, default=AUMENTO_DEMO)
    ap.add_argument("--seed", type=int, default=SEED_DEMO)
    ap.add_argument("--rondas", type=int, default=RONDAS_DEMO)
    ap.add_argument("--cobertura", type=float, default=COBERTURA_DEMO)
    ap.add_argument("--max-justificaciones", type=int, default=6,
                    help="cuantas justificaciones textuales se citan por familia")
    args = ap.parse_args(argv)

    if not EMPRESAS.exists():
        print(f"falta {EMPRESAS.relative_to(RAIZ)} — es un entregable de R1 (data/).")
        return 2
    if not CACHE_DEMO.exists():
        print(f"falta {CACHE_DEMO.relative_to(RAIZ)}: sin cache versionada esta corrida")
        print("  costaria dinero, y este script existe justamente para no gastarlo.")
        return 2

    n_cache = Cache().importar(CACHE_DEMO)
    print(f"cache del escenario demo importada: {n_cache} respuestas ya pagadas")

    try:
        from behavior.cliente import ClienteConductual
        from behavior.cliente import parafrasis as _parafrasis
        # tope 0: estructuralmente incapaz de gastar (ver ClienteSoloCache).
        llm = ClienteConductual(presupuesto=Presupuesto(tope_usd=0.0))
    except Exception as e:  # noqa: BLE001
        print(f"no se pudo construir la capa LLM ({type(e).__name__}): {e}")
        print("  este informe necesita el MISMO cliente que produjo la cache.")
        return 2
    cliente = ClienteSoloCache(llm, ClienteReglas())

    arquetipos = desde_empresas(EMPRESAS, MOMENTOS)
    por_id = {a.id: a for a in arquetipos}
    cabeza, _cola = particionar_por_peso(arquetipos, args.cobertura)
    cabeza_ids = {a.id for a in cabeza}
    tasa = informalidad_observada(MOMENTOS)
    print(f"{len(arquetipos)} arquetipos ({len(cabeza)} al LLM con cobertura "
          f"{args.cobertura:g}) · seed {args.seed} · alza {args.aumento:g}%")

    filas: list[dict[str, Any]] = []

    def recolectar(ronda: int, agente_id: str, resultado) -> None:
        a = por_id[agente_id]
        # `peso` y `n_empresas` son universos DISTINTOS: uno cuenta personas y el
        # otro firmas. Se guardan los dos y el informe reporta los dos, porque
        # mezclarlos es exactamente el defecto que se corrigio en pantalla.
        base = {
            "ronda": ronda,
            "agente_id": agente_id,
            "sector": a.sector,
            "tamano": a.tamano,
            "formal_de_origen": a.formal,
            "n_trabajadores": a.n_trabajadores,
            "peso_personas": a.peso,
            "n_empresas": a.n_empresas,
            "ingreso_por_trabajador": a.ingreso_por_trabajador,
            "flujo_caja": a.flujo_caja,
            "costo_despido": a.costo_despido,
            # Cuantas indemnizaciones alcanza a pagar: es LA variable que decide
            # el despido segun las 518 justificaciones ya leidas.
            "indemnizaciones_que_alcanza": (
                a.flujo_caja / a.costo_despido if a.costo_despido else None
            ),
            "va_al_llm": agente_id in cabeza_ids,
            "fuente": cliente.origen.get((agente_id, ronda),
                                         "reglas" if agente_id not in cabeza_ids else "?"),
            "fallbacks_de_la_celda": resultado.fallbacks,
            "sin_salida_de_la_celda": resultado.sin_salida,
            "vetadas_de_la_celda": len(resultado.vetadas),
        }
        # Una celda puede producir varias decisiones (una por parafrasis).
        for i, d in enumerate(resultado.decisiones):
            veto = d.get("veto") or {}
            filas.append({
                **base,
                "voto": i,
                "estrategia_propuesta": d.get("estrategia_propuesta", ""),
                "familia": d.get("familia", "otra"),
                "efecto_en_el_agregado": EFECTO.get(d.get("familia", "otra"), "?"),
                "detalle": d.get("detalle") or {},
                "justificacion": d.get("justificacion", ""),
                "veto_factible": veto.get("factible"),
                "veto_razon": veto.get("razon"),
                "intento": d.get("intento"),
                # `fue_fallback` lo pone `contrato.decision_fallback()`; es el
                # marcador real, no `fallback` (esa clave no existe).
                "es_fallback": bool(d.get("fue_fallback")),
                "sin_salida": bool(d.get("sin_salida")),
            })

    gasto_antes = cliente.presupuesto.gastado_usd
    llamadas_antes = cliente.presupuesto.llamadas

    rondas = correr(
        arquetipos,
        cliente,
        aumento_pct=args.aumento,
        seed=args.seed,
        tasa_informalidad_inicial=tasa,
        rondas_totales=args.rondas,
        cobertura_llm=args.cobertura,
        # Una trayectoria esta DEFINIDA por su redaccion. Se toma la primera, la
        # misma con la que la API arma la trayectoria 0 (`api/trayectorias.py:119`).
        parafrasis_fija=_parafrasis(5)[0],
        al_decidir_arquetipo=recolectar,
    )

    gasto = cliente.presupuesto.gastado_usd - gasto_antes
    llamadas = cliente.presupuesto.llamadas - llamadas_antes

    # GUARDARRAIL. Este informe se publicita como gratis; si dejo de serlo,
    # quiero enterarme por un error y no por la factura. Una sola llamada nueva
    # significa que la cache no cubrio, y entonces las decisiones que estoy
    # atribuyendo YA NO son las 518 que se analizaron.
    if llamadas > 0:
        print(f"\nABORTA: la corrida hizo {llamadas} llamada(s) nueva(s) "
              f"(USD {gasto:.4f}). Este informe se publicita como gratis y el tope")
        print("  de USD 0 deberia haberlo impedido: hay algo roto en el guardarrail.")
        return 1

    if not filas:
        print("\nABORTA: no se recolecto ninguna decision. ¿rondas_totales=1?")
        return 1

    INFORMES.mkdir(exist_ok=True)
    nombre = f"decisiones-seed{args.seed}-{args.aumento:g}"
    ruta_json = INFORMES / f"{nombre}.json"
    ruta_md = INFORMES / f"{nombre}.md"

    ruta_json.write_text(json.dumps({
        "escenario": {"aumento_pct": args.aumento, "seed": args.seed,
                      "rondas": len(rondas), "arquetipos": len(arquetipos),
                      "informalidad_observada": tasa},
        "costo_usd": gasto,
        "llamadas_nuevas": llamadas,
        "decisiones": filas,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    # ---- el informe legible -------------------------------------------------
    n = len(filas)
    peso_total = sum(f["peso_personas"] for f in filas) or 1.0
    emp_total = sum(f["n_empresas"] for f in filas) or 1.0

    cuenta = collections.Counter(f["familia"] for f in filas)
    peso_fam: dict[str, float] = collections.defaultdict(float)
    emp_fam: dict[str, float] = collections.defaultdict(float)
    for f in filas:
        peso_fam[f["familia"]] += f["peso_personas"]
        emp_fam[f["familia"]] += f["n_empresas"]

    n_llm = sum(1 for f in filas if f["fuente"] == "llm-cache")
    n_cola = sum(1 for f in filas if not f["va_al_llm"])
    n_miss = sum(1 for f in filas if f["va_al_llm"] and f["fuente"] != "llm-cache")

    md = [f"# Decisiones de la corrida — alza {args.aumento:g}%, seed {args.seed}",
          "",
          "> Generado por `scripts/informe_decisiones.py` sobre la cache ya pagada.",
          f"> **Costo de este informe: USD {gasto:.2f} · {llamadas} llamadas nuevas.**",
          f"> {len(arquetipos)} celdas · {len(rondas)} rondas · {n} decisiones con nombre y apellido.",
          "",
          "## 0 · De donde sale cada decision",
          "",
          "Tres origenes distintos, y confundirlos cambia todas las cifras de abajo:",
          "",
          f"- **{n_llm} decisiones del modelo**, resueltas con una respuesta ya pagada de",
          "  `behavior/cache-demo.json`. Son las unicas que un LLM escribio.",
          f"- **{n_cola} decisiones de la cola**, que van a la **regla fija** de",
          "  `behavior/ablacion.py` **por diseno**: el ruteo top-K manda al modelo solo la",
          f"  cabeza que concentra el {args.cobertura:.0%} del peso ({len(cabeza)} de "
          f"{len(arquetipos)} celdas). Esto no es un defecto.",
          f"- **{n_miss} decisiones que SI debian ir al modelo y cayeron a la regla** porque su",
          "  respuesta no estaba en la cache. Esto **si** es un defecto, y es de esta corrida.",
          "",
          "La cache se pago antes de un cambio que movio la probabilidad de inspeccion por",
          "celda, y esa probabilidad va dentro del texto del prompt, o sea dentro de la clave",
          "de cache. Es el mismo defecto que AGENTS.md ya declara para",
          "`data/prediccion_modelo.json`. Consecuencia medida: `scripts/reproduce.py` no",
          "reproduce sobre `main` hoy — se cae en la primera celda sin cachear.",
          "",
          "**Lee las secciones 1 a 6 sabiendo eso.** La seccion 7 cita solo justificaciones",
          "de origen `llm-cache`, que son las unicas escritas por el modelo.",
          "",
          "## 1 · Que se decidio, en los tres denominadores",
          "",
          "La misma decision pesa distinto segun que se cuente. `decisiones` es una fila por",
          "voto; `personas` usa el factor de expansion de la GEIH; `firmas` cuenta unidades",
          "productivas. Son universos distintos y enfrentarlos es un error, por eso van los tres.",
          ""]

    filas_md = []
    for fam, c in cuenta.most_common():
        filas_md.append([
            f"`{fam}`", str(c), f"{_pct(c, n):.1f}%",
            f"{_pct(peso_fam[fam], peso_total):.1f}%",
            f"{_pct(emp_fam[fam], emp_total):.1f}%",
            EFECTO.get(fam, "?"),
        ])
    md.append(_tabla(filas_md, ["familia", "n", "% decisiones", "% personas",
                                "% firmas", "que mueve"]))

    solo_llm = [f for f in filas if f["fuente"] == "llm-cache"]
    if solo_llm:
        c_llm = collections.Counter(f["familia"] for f in solo_llm)
        peso_llm = sum(f["peso_personas"] for f in solo_llm) or 1.0
        pf_llm: dict[str, float] = collections.defaultdict(float)
        for f in solo_llm:
            pf_llm[f["familia"]] += f["peso_personas"]
        md += ["",
               f"**Y solo las {len(solo_llm)} que decidio el modelo** — la tabla de arriba las",
               "mezcla con las que resolvio la regla fija, y las dos poblaciones no se parecen:",
               ""]
        md.append(_tabla(
            [[f"`{fam}`", str(c), f"{_pct(c, len(solo_llm)):.1f}%",
              f"{_pct(pf_llm[fam], peso_llm):.1f}%", EFECTO.get(fam, "?")]
             for fam, c in c_llm.most_common()],
            ["familia", "n", "% decisiones", "% personas", "que mueve"]))
        md.append("")

    inerte_n = sum(cuenta[f] for f in INERTES)
    inerte_peso = sum(peso_fam[f] for f in INERTES)
    md += ["",
           f"**Decisiones que no mueven ninguna cifra de portada:** {inerte_n} de {n} "
           f"({_pct(inerte_n, n):.1f}% de las decisiones, {_pct(inerte_peso, peso_total):.1f}% "
           "de las personas).",
           "Son `subir_precios`, `absorber` y `renegociar`: la planta queda donde estaba y el",
           "empleo tambien. La pantalla las lee como adaptacion; el motor las lee como nada.",
           ""]

    # ---- reparto por sector -------------------------------------------------
    md += ["## 2 · Quien decidio que — reparto por sector", ""]
    sectores = sorted({f["sector"] for f in filas})
    fams = [f for f, _ in cuenta.most_common()]
    filas_md = []
    for s in sectores:
        de_s = [f for f in filas if f["sector"] == s]
        c = collections.Counter(f["familia"] for f in de_s)
        filas_md.append([s, str(len(de_s))] +
                        [f"{_pct(c[fa], len(de_s)):.0f}%" for fa in fams])
    md.append(_tabla(filas_md, ["sector", "n"] + [f"`{f}`" for f in fams]))

    md += ["", "## 3 · Reparto por tamano", ""]
    filas_md = []
    for t in sorted({f["tamano"] for f in filas}):
        de_t = [f for f in filas if f["tamano"] == t]
        c = collections.Counter(f["familia"] for f in de_t)
        filas_md.append([t, str(len(de_t))] +
                        [f"{_pct(c[fa], len(de_t)):.0f}%" for fa in fams])
    md.append(_tabla(filas_md, ["tamano", "n"] + [f"`{f}`" for f in fams]))

    # ---- la restriccion de caja --------------------------------------------
    md += ["", "## 4 · La restriccion que decide: la caja", "",
           "Cuantas indemnizaciones alcanza a pagar cada celda con su flujo de caja libre.",
           "Es la variable que las justificaciones invocan mas que ninguna otra.", ""]
    puede = [f for f in filas if (f["indemnizaciones_que_alcanza"] or 0) >= 1]
    despidieron = [f for f in filas if f["familia"] == "despedir"]
    md += [f"- Decisiones tomadas por una celda que **alcanza a indemnizar al menos a un "
           f"trabajador**: {len(puede)} de {n} ({_pct(len(puede), n):.1f}%).",
           f"- Decisiones que efectivamente fueron `despedir`: **{len(despidieron)}**.",
           ""]
    if despidieron:
        md.append("Las que si despidieron:")
        md.append("")
        for f in despidieron[:10]:
            md.append(f"- **{f['sector']} · {f['tamano']}** ({f['n_trabajadores']} trabajadores, "
                      f"alcanza para {f['indemnizaciones_que_alcanza']:.1f} indemnizaciones) — "
                      f"despide {f['detalle'].get('empleados_a_despedir')}: "
                      f"«{f['justificacion']}»")
        md.append("")

    # ---- magnitudes declaradas ---------------------------------------------
    md += ["## 5 · Magnitudes declaradas", "",
           "Lo que el agente DIJO que haria, cuando el campo trae numero. `aumento_precios_pct`",
           "es traslado declarado, no inflacion: no hay respuesta de demanda en este modelo",
           "(`behavior/rondas.py:779`).", ""]
    campos = ("empleados_a_informalizar", "empleados_a_despedir", "reduccion_horas_pct",
              "reduccion_margen_pct", "aumento_precios_pct")
    filas_md = []
    for campo in campos:
        vals = sorted(float(f["detalle"][campo]) for f in filas
                      if f["detalle"].get(campo) is not None)
        if not vals:
            continue
        med = vals[len(vals) // 2]
        filas_md.append([f"`{campo}`", str(len(vals)), f"{vals[0]:.1f}",
                         f"{med:.1f}", f"{vals[-1]:.1f}"])
    md.append(_tabla(filas_md, ["campo", "n con valor", "min", "mediana", "max"]))

    # ---- salud de la capa ---------------------------------------------------
    fb = [f for f in filas if f["es_fallback"]]
    ss = [f for f in filas if f["sin_salida"]]
    peso_fb = sum(f["peso_personas"] for f in fb)
    md += ["", "## 6 · Salud de la capa", "",
           f"- **Fallback** (el veto tumbo todo lo que propuso y cayo a la opcion terminal): "
           f"{len(fb)} de {n} decisiones ({_pct(len(fb), n):.1f}%), que son "
           f"{_pct(peso_fb, peso_total):.1f}% de las personas.",
           f"- **Sin ninguna opcion factible** (ni siquiera la terminal era pagable): "
           f"{len(ss)} ({_pct(len(ss), n):.1f}%).",
           f"- De esos fallbacks, **{sum(1 for f in fb if f['va_al_llm'])}** son de celdas que "
           "van al modelo; el resto son de la cola resuelta por regla fija.",
           "",
           "Los dos denominadores no coinciden y esa diferencia importa: la pantalla publica el",
           "de decisiones, y el que describe a cuanta gente le paso es el de personas.",
           ""]

    # ---- justificaciones ----------------------------------------------------
    md += ["## 7 · Por que — en palabras del agente", "",
           "Textual, sin editar. Es la materia prima de todo lo anterior.", ""]
    for fam, _ in cuenta.most_common():
        de_f = [f for f in filas if f["familia"] == fam and f["justificacion"]
                and f["fuente"] == "llm-cache"]
        if not de_f:
            continue
        md.append(f"### `{fam}` · {len(de_f)} decisiones — {EFECTO.get(fam, '?')}")
        md.append("")
        # Las mas pesadas primero: las que representan a mas gente.
        de_f.sort(key=lambda f: -f["peso_personas"])
        for f in de_f[:args.max_justificaciones]:
            md.append(f"- **{f['sector']} · {f['tamano']} · ronda {f['ronda']}** "
                      f"({f['n_trabajadores']} trab., representa "
                      f"{f['peso_personas']:,.0f} personas) — «{f['justificacion']}»")
        md.append("")

    md += ["---", "",
           "## Como se reproduce", "",
           "```bash", "python3 scripts/informe_decisiones.py", "```", "",
           "Lee `behavior/cache-demo.json` y no toca la red. Si alguna llamada saliera a la API,",
           "el script aborta con codigo distinto de cero antes de escribir nada.", ""]

    ruta_md.write_text("\n".join(md) + "\n", encoding="utf-8")

    print(f"\ngasto: ${gasto:.2f} · llamadas nuevas: {llamadas}")
    print(f"{n} decisiones atribuidas · {len(sectores)} sectores")
    print(f"  {ruta_md.relative_to(RAIZ)}")
    print(f"  {ruta_json.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
