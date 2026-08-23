"""Ejecuta las compuertas y mediciones pre-registradas en VALIDATION.md.

No completa ni modifica el pre-registro. Un candado imposible de ejecutar se
reporta como BLOQUEADO y hace que el proceso termine con código distinto de 0.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from enum import Enum
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
DATA = RAIZ / "data"
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

def _prediccion() -> dict:
    """La prediccion del modelo, desde el artefacto versionado.

    Estaba como tres constantes sueltas aqui adentro. Un numero magico en el
    validador es exactamente lo que el repo prohibe: nadie podia rastrear de
    que corrida salio ni notar si quedaba viejo.
    """
    ruta = DATA / "prediccion_modelo.json"
    if not ruta.exists():
        raise FileNotFoundError("falta data/prediccion_modelo.json")
    return json.loads(ruta.read_text(encoding="utf-8"))["resultado"]


class Estado(str, Enum):
    """PASA/FALLA/BLOQUEADO son de COMPUERTAS. MEDIDO es de MEDICIONES.

    `VALIDATION.md` define la medicion como "se publica el numero que salga, sin
    pasa/falla". Imprimir [PASA] sobre una medicion contradecia el contrato del
    propio documento y, peor, metia el resultado en el exit code: una medicion
    no puede reprobar.
    """
    PASA = "PASA"
    FALLA = "FALLA"
    BLOQUEADO = "BLOQUEADO"
    MEDIDO = "MEDIDO"


# Solo las COMPUERTAS deciden el codigo de salida. Una medicion que sale mal no
# reprueba nada: publicar un numero feo es el resultado, no un fallo.
COMPUERTAS = (Estado.PASA, Estado.FALLA, Estado.BLOQUEADO)


Resultado = tuple[Estado, str]


def _ejecutar(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args], cwd=RAIZ, capture_output=True, text=True, check=False
    )


PRODUCTOR = RAIZ / "scripts" / "run_simulacion.py"
ARTEFACTOS = RAIZ / "artefactos"
MANIFIESTO_PUBLICADO = ARTEFACTOS / "corrida.manifiesto.json"


def candado_g1(seco: bool = False) -> Resultado:
    """Determinismo punta a punta: seed + manifiesto de caché + versiones.

    Acumula TODOS los motivos en vez de devolver el primero. Con retorno
    temprano, arreglar `anthropic` destapaba el siguiente bloqueo y daba la
    impresión de que la compuerta estaba a un paso de cerrar cuando le faltaban
    tres. Un estado que oculta lo que viene después no sirve para planear.

    Este candado EJECUTA, no inspecciona. Antes terminaba con un
    `faltan.append("falta el artefacto canónico...")` incondicional: devolvía
    `BLOQUEADO` aunque todo lo demás estuviera, así que ningún trabajo podía
    cerrarlo nunca. Ahora corre `scripts/run_simulacion.py --solo-hash` dos
    veces y compara los SHA-256, que es literalmente lo que el candado promete
    en `VALIDATION.md`: *"dos corridas con el mismo (seed, manifiesto de caché,
    versiones) dan salida idéntica"*.

    Corre por la ablación determinista: $0, sin API key y sin red.
    """
    faltan = []
    requisitos = RAIZ / "requirements.txt"
    if not requisitos.exists():
        faltan.append("falta requirements.txt")
    elif "anthropic==" not in requisitos.read_text(encoding="utf-8").lower():
        faltan.append("anthropic sin fijar (no está instalado)")
    if not PRODUCTOR.exists():
        faltan.append("falta scripts/run_simulacion.py para comparar dos corridas completas")
    if faltan:
        return Estado.BLOQUEADO, f"{len(faltan)} bloqueos: " + "; ".join(faltan)

    if seco:
        return (
            Estado.BLOQUEADO,
            "--dry: los requisitos están, pero no se corrieron las dos corridas "
            "que deciden el candado (quita --dry para ejecutarlo)",
        )

    corridas = [_ejecutar(str(PRODUCTOR), "--solo-hash") for _ in range(2)]
    for i, c in enumerate(corridas, 1):
        if c.returncode != 0:
            detalle = (c.stderr + c.stdout).strip().splitlines()
            ultima = detalle[-1] if detalle else "sin salida"
            return Estado.FALLA, f"la corrida {i} salió {c.returncode}: {ultima}"
    hashes = [c.stdout.strip() for c in corridas]
    if hashes[0] != hashes[1]:
        return (
            Estado.FALLA,
            f"dos corridas con el mismo seed dieron artefactos distintos: "
            f"{hashes[0][:12]}… contra {hashes[1][:12]}…",
        )

    # Y contra lo PUBLICADO. Que dos corridas de hoy coincidan prueba que el
    # motor es determinista; no prueba que el artefacto versionado siga
    # describiendo este motor. El repo ya tiene esa herida abierta con
    # `data/prediccion_modelo.json` (ver el recuadro de VALIDATION.md), así que
    # acá se mira explícitamente en vez de confiar.
    #
    # Sólo cuenta como FALLA si el entorno es el MISMO: el candado compara
    # "(seed, manifiesto, versiones)", así que un artefacto producido con otras
    # versiones no es comparable y decirlo es más honesto que reprobarlo.
    nota = "artefacto publicado: no hay (correr `make run` para escribirlo)"
    if MANIFIESTO_PUBLICADO.exists():
        pub = json.loads(MANIFIESTO_PUBLICADO.read_text(encoding="utf-8"))
        if pub.get("sha256_artefacto") == hashes[0]:
            nota = "coincide con el artefacto publicado"
        elif pub.get("versiones") != _versiones_de_esta_maquina():
            nota = (
                "el artefacto publicado se produjo con OTRAS versiones, así que "
                "no es comparable (regenerar con `make run`)"
            )
        else:
            return (
                Estado.FALLA,
                "mismo entorno y mismo seed, pero el artefacto publicado no "
                f"coincide: {pub.get('sha256_artefacto', '?')[:12]}… contra "
                f"{hashes[0][:12]}… — está podrido, regenerar con `make run`",
            )
    return Estado.PASA, f"dos corridas → {hashes[0][:12]}… idéntico; {nota}"


def _versiones_de_esta_maquina() -> dict[str, str]:
    """Las mismas versiones que estampa `scripts/run_simulacion.py`.

    Se importa del productor en vez de reimplementarse: dos listas de paquetes
    que tienen que coincidir y viven en archivos distintos divergen, y cuando
    divergen este candado empieza a comparar peras con manzanas en silencio.
    """
    import importlib.util

    spec = importlib.util.spec_from_file_location("_run_simulacion", PRODUCTOR)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo._versiones()


def candado_g2() -> Resultado:
    """Higiene de prompts + corrida re-skinneada."""
    higiene = _ejecutar("-m", "behavior.higiene")
    if higiene.returncode != 0:
        detalle = (higiene.stdout + higiene.stderr).strip().splitlines()[-1]
        return Estado.FALLA, f"behavior.higiene salió {higiene.returncode}: {detalle}"
    # El re-skinning NO vive en un archivo propio: es `behavior.capa.Reskin`, y
    # se activa con `demo.py --reskin`. Buscarlo como `behavior/reskin.py`
    # reportaba "no implementado" sobre una pieza que sí existe.
    try:
        from behavior.capa import Reskin  # noqa: F401
    except ImportError:
        return Estado.BLOQUEADO, "higiene PASA; behavior.capa.Reskin no existe"
    # Por qué esto sigue BLOQUEADO y NO se cierra con la ablación.
    #
    # Se midió (23-ago): correr el par canónica/re-skinneada con `ClienteReglas`
    # —el camino determinista, gratis, sin API key— da **+0,000000 pp** de
    # diferencia en la informalidad final, con un factor de re-skin de 0,4844.
    # Ese cero no es evidencia de no-contaminación: `Reskin` reescribe el TEXTO
    # del prompt (`capa.renderizar()`), y las reglas fijas de la ablación no leen
    # texto, deciden sobre los números del arquetipo. O sea que el candado
    # pasaría midiendo un canal por el que la contaminación no puede viajar.
    #
    # G2 pregunta si el MODELO reconoce el escenario por sus magnitudes. Sólo el
    # camino LLM puede responder eso, y cuesta créditos. Se deja BLOQUEADO a
    # propósito: un PASA vacío en la compuerta de no-contaminación es peor que
    # un bloqueo declarado, porque es exactamente la mitad del argumento de
    # validación del proyecto.
    return (
        Estado.BLOQUEADO,
        "higiene PASA; Reskin implementado (behavior/capa.py) pero el par "
        "canónica/re-skinneada exige el camino LLM: por la ablación mueve "
        "0,000000 pp porque las reglas fijas no leen el texto del prompt, "
        "y ese PASA no mediría nada",
    )


def candado_g3() -> Resultado:
    """Corrida sin política contra proxy y orden micro > pyme > grande.

    El productor ya existe: `scripts/run_simulacion.py --aumento 0` escribe
    `artefactos/calibracion_base.json`. Se sigue aceptando el archivo en
    `data/` por si el equipo decide versionarlo ahí (esa carpeta es de R1).

    **El objetivo cambió de denominador, y era un defecto.** Este candado
    comparaba contra `tasa_informalidad_total` (30,57%: TODOS los ocupados de
    Bogotá) una corrida que sólo simula empleados de firma. `data/empresas.parquet`
    excluye a propósito a los 964.004 cuenta propia —una unidad sin empleados no
    puede despedir ni informalizar a nadie—, y `arquetipos.informalidad_observada()`
    ya lo documenta al devolver 17,99%. Con el objetivo equivocado el candado
    medía 12,58 pp de error puramente contable y habría reprobado el modelo por
    un cambio de universo. El objetivo correcto es
    `tasa_informalidad_empleados_de_firma`.
    """
    salida = next(
        (r for r in (ARTEFACTOS / "calibracion_base.json", DATA / "calibracion_base.json")
         if r.exists()),
        None,
    )
    if salida is None:
        return (
            Estado.BLOQUEADO,
            "falta la corrida sin política: producirla con "
            "`python3 scripts/run_simulacion.py --aumento 0`",
        )
    observado = json.loads((DATA / "momentos.json").read_text(encoding="utf-8"))
    calibrado = json.loads(salida.read_text(encoding="utf-8"))
    tasa = float(calibrado["tasa_informalidad_total"])
    objetivo = float(observado["tasa_informalidad_empleados_de_firma"])
    tamanos = calibrado["tasa_informalidad_por_tamano"]
    objetivo_tamanos = observado["tasa_informalidad_por_tamano_empleados_de_firma"]
    orden = tamanos["micro"] > tamanos["pyme"] > tamanos["grande"]
    error_pp = abs(tasa - objetivo) * 100
    estado = Estado.PASA if error_pp <= 2.0 and orden else Estado.FALLA
    desglose = " · ".join(
        f"{k} {tamanos[k] * 100:.2f}% vs {objetivo_tamanos[k] * 100:.2f}% obs"
        for k in ("micro", "pyme", "grande")
    )
    return estado, (
        f"error={error_pp:.2f} pp sobre empleados de firma (umbral 2 pp); "
        f"orden micro>pyme>grande={orden}; {desglose}"
    )


def _tasa_periodo(anio: int, meses: list[str]) -> float:
    # Importación local: V0 solo intenta leer crudos cuando los seis meses están.
    from data.construir_poblacion import construir

    _, momentos = construir(anio, meses=meses)
    return float(momentos["tasa_informalidad_total"])


def medicion_v0() -> tuple[Estado, str, dict[str, float] | None]:
    # V0 se computa desde los momentos VERSIONADOS. Antes exigia los seis
    # directorios crudos de GEIH 2025, que estan gitignorados: en un clon limpio
    # EL NUMERO quedaba bloqueado y la promesa de "lo reproduce un extrano con un
    # comando" era falsa. Los crudos solo hacen falta para el corte abr-jun, que
    # es un extra.
    momentos_2025 = DATA / "momentos_2025.json"
    if not momentos_2025.exists():
        return Estado.BLOQUEADO, "faltan data/momentos_2025.json y data/poblacion_2025.parquet", None

    pre_ene_jun = float(json.loads(momentos_2025.read_text(encoding="utf-8"))["tasa_informalidad_total"])
    post_ene_jun = float(json.loads((DATA / "momentos.json").read_text(encoding="utf-8"))["tasa_informalidad_total"])
    # El corte abr-jun es OPCIONAL: solo sirve para contrastar contra el
    # trimestre que publica el DANE, y necesita los crudos. Si no estan, V0
    # igual sale completo con la ventana ene-jun.
    crudos = all(
        (DATA / "raw" / f"GEIH_{anio}_{mes}" / "CSV").is_dir()
        for anio in (2025, 2026)
        for mes in ("abril", "mayo", "junio")
    )
    pre_abr_jun = _tasa_periodo(2025, ["abril", "mayo", "junio"]) if crudos else None
    post_abr_jun = _tasa_periodo(2026, ["abril", "mayo", "junio"]) if crudos else None

    pred = _prediccion()
    delta = (post_ene_jun - pre_ene_jun) * 100
    error_firmado = pred["brecha_pp"] - delta
    error_modelo = abs(error_firmado)
    error_baseline = abs(delta)
    skill = 1.0 - error_modelo / error_baseline if error_baseline else float("-inf")
    numeros = {
        "pre_ene_jun_pct": pre_ene_jun * 100,
        "post_ene_jun_pct": post_ene_jun * 100,
        "delta_ene_jun_pp": delta,
        "pre_abr_jun_pct": pre_abr_jun * 100 if crudos else None,
        "post_abr_jun_pct": post_abr_jun * 100 if crudos else None,
        "delta_abr_jun_pp": (post_abr_jun - pre_abr_jun) * 100 if crudos else None,
        "error_firmado_pp": error_firmado,
        "error_absoluto_pp": error_modelo,
        "error_baseline_pp": error_baseline,
        "skill_b1": skill,
        # B3: se llamaba "cobertura", y esa palabra invita a la pregunta que
        # hunde el numero: "¿cobertura de que nivel?". No hay nivel: es un
        # min-max sobre N=5 parafrasis, no un intervalo calibrado. El nombre
        # nuevo dice literalmente lo que se midio.
        "observado_en_rango": float(
            pred["rango_entre_parafrasis_pct"][0]
            <= post_ene_jun * 100
            <= pred["rango_entre_parafrasis_pct"][1]
        ),
        "ancho_banda_pp": pred["ancho_rango_pp"],
    }
    # SEGUNDO EPISODIO, si esta el momento de 2024: el alza de 2025 fue +9,5%,
    # otra magnitud de shock. Sirve para saber si el error del modelo es
    # sistematico o casualidad de un solo anio.
    momentos_2024 = DATA / "momentos_2024.json"
    if momentos_2024.exists():
        pre_2024 = float(json.loads(momentos_2024.read_text(encoding="utf-8"))["tasa_informalidad_total"])
        numeros["pre_2024_pct"] = pre_2024 * 100
        numeros["delta_2024_2025_pp"] = (pre_ene_jun - pre_2024) * 100

    sufijo = "" if crudos else " (sin crudos: sin el corte abr-jun, que es opcional)"
    return Estado.MEDIDO, f"proxy contra proxy desde momentos versionados{sufijo}", numeros


def medicion_m3(seco: bool = False) -> Resultado:
    if seco:
        # `barrer_factor(real=True)` corre la ablación ocho veces. Es gratis pero
        # no es instantáneo, y `--dry` promete no correr simulaciones.
        return Estado.BLOQUEADO, "--dry: no se corrió el barrido de 8 factores"
    try:
        from behavior.ablacion import barrer_factor

        filas = barrer_factor(real=True)
    except Exception as exc:  # pragma: no cover - evidencia operativa en CLI
        return Estado.BLOQUEADO, f"la ablación no pudo correr: {type(exc).__name__}: {exc}"
    hay_cascada = [factor for factor, tasa, _ in filas if tasa > 0.01]
    sin_cascada = [factor for factor, tasa, _ in filas if tasa <= 0.01]
    return Estado.MEDIDO, f"8 factores; cascada={hay_cascada}; sin cascada={sin_cascada}"


def _imprimir_v0(n: dict[str, float]) -> None:
    skill = n["skill_b1"]
    skill_txt = "-inf" if skill == float("-inf") else f"{skill:.3f}"
    print("\nEL NÚMERO · V0")
    print(f"  Error del backtest:          {n['error_absoluto_pp']:.2f} pp (firmado modelo-observado: {n['error_firmado_pp']:+.2f} pp)")
    print(f"  Skill vs persistencia (B1):  {skill_txt}")
    # "banda" NO: con N=5 el p10/p90 es el minimo y el maximo de las cinco
    # parafrasis (en esperanza, los percentiles 16,7 y 83,3). Llamarlo banda
    # sugiere un intervalo calibrado que no es. Ver VALIDATION.md, "Método".
    print(f"  ¿El observado cae en el rango? {'sí' if n['observado_en_rango'] else 'NO'}"
          "   (rango entre paráfrasis, N=5, min–max; no es un intervalo de confianza)")
    print(f"  Ancho del rango:             {n['ancho_banda_pp']:.1f} pp  (entre paráfrasis, no calibrado)")
    print("  Corridas:                    BLOQUEADO: el repo no registra N>=5 trayectorias comparables")
    print(f"  Proxy 2025 ene-jun:          {n['pre_ene_jun_pct']:.2f}%")
    print(f"  Proxy 2026 ene-jun:          {n['post_ene_jun_pct']:.2f}%")
    print(f"  Delta observado:             {n['delta_ene_jun_pp']:+.2f} pp")
    if "delta_2024_2025_pp" in n:
        print()
        print("  Serie de dos episodios (el modelo predice que SUBE en los dos, y mas en el grande):")
        print(f"    2024 -> 2025, alza  +9,5%:   {n['delta_2024_2025_pp']:+.2f} pp observado")
        print(f"    2025 -> 2026, alza +23,0%:   {n['delta_ene_jun_pp']:+.2f} pp observado")
        print("    Las direcciones se OPONEN, y el movimiento real es de unos pocos puntos.")


def medicion_m4(numeros: dict[str, float] | None) -> Resultado:
    """El rango entre paráfrasis: si el observado cae dentro, Y qué tan ancho es.

    Es una MEDICIÓN, así que devuelve MEDIDO: el resultado se publica, no se
    aprueba, y no entra al código de salida. Que el observado quede FUERA no es
    un fallo del
    candado, es el dato. Existe como fila propia porque `VALIDATION.md` la
    declara en la tabla, y un documento que anuncia una fila que el ejecutor no
    imprime es exactamente la deriva que este trabajo existe para evitar.
    """
    if numeros is None:
        return Estado.BLOQUEADO, "sin V0 no hay contra qué medir el rango"
    dentro = "SÍ" if numeros["observado_en_rango"] else "NO"
    return (
        Estado.MEDIDO,
        f"el observado {dentro} cae dentro del rango entre paráfrasis "
        f"({numeros['ancho_banda_pp']:.1f} pp de ancho, N=5, min–max; "
        "no es un p10/p90 calibrado ni un intervalo de confianza)",
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Sale con código 1 mientras haya compuertas que no estén en PASA. "
               "Las MEDICIONES no entran al código de salida: publicar un número "
               "feo es el resultado, no un fallo.",
    )
    # `--dry` estaba citado en el informe del juez científico y NO existía: este
    # archivo no tenía `argparse`, así que cualquier bandera se ignoraba en
    # silencio y el comando del informe corría la validación completa mientras
    # su autor creía estar haciendo una pasada seca.
    ap.add_argument(
        "--dry", action="store_true",
        help="pasada seca: verifica que los productores de cada candado existan, "
             "pero no corre las simulaciones que deciden G1. No cambia el "
             "veredicto de nada que ya esté medido.",
    )
    ap.add_argument(
        "--json", action="store_true",
        help="emite el resultado como JSON en vez del informe legible",
    )
    args = ap.parse_args(argv)

    resultados = [
        ("G1 reproducibilidad", candado_g1(seco=args.dry)),
        ("G2 no contaminación", candado_g2()),
        ("G3 calibración base", candado_g3()),
    ]
    estado_v0, detalle_v0, numeros = medicion_v0()
    # M1 y M2 van SEPARADAS: `VALIDATION.md` declara siete filas y el ejecutor
    # imprimía seis porque las agrupaba. Un documento que anuncia una fila que el
    # ejecutor no tiene es la deriva que este trabajo existe para evitar.
    if numeros is None:
        resultados.extend([
            ("M1 backtest", (estado_v0, detalle_v0)),
            ("M2 habilidad vs baseline", (estado_v0, detalle_v0)),
        ])
    else:
        skill = numeros["skill_b1"]
        skill_txt = "-inf" if skill == float("-inf") else f"{skill:.3f}"
        resultados.extend([
            ("M1 backtest", (estado_v0, f"error {numeros['error_absoluto_pp']:.2f} pp "
                                        f"(firmado {numeros['error_firmado_pp']:+.2f}); {detalle_v0}")),
            ("M2 habilidad vs baseline", (estado_v0, f"skill B1 = {skill_txt}; "
                                                     f"persistencia erra {numeros['error_baseline_pp']:.2f} pp")),
        ])
    resultados.extend([
        ("M3 ablación", medicion_m3(seco=args.dry)),
        ("M4 rango entre paráfrasis", medicion_m4(numeros)),
    ])

    # Solo las compuertas deciden. Una medición no reprueba: publicar un número
    # feo ES el resultado.
    #
    # Se eligen por NOMBRE, no por estado. Se filtraban por `estado in
    # COMPUERTAS`, y `BLOQUEADO` está ahí: una medición que no podía correr
    # —M3 cuando la ablación revienta, o bajo `--dry`— se colaba al código de
    # salida y hacía reprobar la validación por algo que el propio
    # `VALIDATION.md` declara que no puede reprobar. Qué es compuerta lo dice el
    # pre-registro, no el estado que le tocó hoy.
    compuertas = [(n, e) for n, (e, _) in resultados if n.startswith("G")]
    codigo = 0 if all(e is Estado.PASA for _, e in compuertas) else 1

    if args.json:
        print(json.dumps({
            "compuertas": {n: e.value for n, e in compuertas},
            "filas": [
                {"nombre": n, "estado": e.value, "detalle": d}
                for n, (e, d) in resultados
            ],
            "numero": numeros,
            "dry": args.dry,
            "codigo_de_salida": codigo,
        }, ensure_ascii=False, indent=2, sort_keys=True))
        return codigo

    print("VALIDACIÓN PRE-REGISTRADA" + ("  ·  --dry (pasada seca)" if args.dry else ""))
    for nombre, (estado, detalle) in resultados:
        print(f"  [{estado.value:9}] {nombre}: {detalle}")
    if numeros is None:
        print("\nEL NÚMERO · BLOQUEADO")
        print(f"  {detalle_v0}")
    else:
        _imprimir_v0(numeros)

    return codigo


if __name__ == "__main__":
    raise SystemExit(main())
