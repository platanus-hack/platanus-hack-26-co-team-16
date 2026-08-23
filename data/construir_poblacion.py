"""GEIH cruda -> población y momentos del año solicitado.

Entrada:  data/raw/GEIH_2026_<mes>/CSV/  (la deja `python data/descargar_geih.py`)
Salida:   data/poblacion.parquet  — una fila por agente-trabajador de Bogota,
          esquema exacto de contracts/agente.json
          data/momentos.json     — objetivos de calibracion (informalidad por
          sector y tamano, distribucion salarial, spike en la moda salarial)

Determinista: transformacion pura sin muestreo (no requiere seed); el parquet
se escribe ordenado por id, asi dos corridas producen el mismo archivo.

Uso:  python data/construir_poblacion.py [--anio 2026] [--meses abril,mayo,junio]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

RAW = Path(__file__).parent / "raw"
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio"]
NUM_MES = {"enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6}

AREA_BOGOTA = 11  # codigo DANE del area metropolitana de Bogota D.C.

LLAVE = ["PERIODO", "DIRECTORIO", "SECUENCIA_P", "ORDEN"]

# Agrupacion de RAMA2D_R4 (CIIU Rev. 4 A.C., 2 digitos) en sectores.
# Los rangos son las secciones oficiales de la CIIU Rev. 4 A.C. (DANE);
# la agrupacion en 9 sectores es nuestra, para densidad por arquetipo.
SECTORES = [
    ((1, 9), "agro_mineria", "agr"),
    ((10, 33), "industria", "ind"),
    ((35, 43), "construccion_utilities", "con"),
    ((45, 47), "comercio", "com"),
    ((49, 53), "transporte", "tra"),
    ((55, 56), "alojamiento_comida", "alo"),
    ((58, 82), "servicios_empresariales", "emp"),
    ((84, 88), "adm_publica_edu_salud", "pub"),
    ((90, 99), "otros_servicios", "otr"),
]

# P3042 (nivel educativo, diccionario ANDA catalogo 900):
# 1 Ninguno · 2 Preescolar · 3 Basica primaria · 4 Basica secundaria ·
# 5 Media academica · 6 Media tecnica · 7 Normalista · 8 Tecnica profesional ·
# 9 Tecnologica · 10 Universitaria · 11 Especializacion · 12 Maestria ·
# 13 Doctorado · 99 No sabe/no informa
EDUCACION = {
    1: "primaria", 2: "primaria", 3: "primaria",
    4: "secundaria",
    5: "media", 6: "media",
    7: "tecnica", 8: "tecnica", 9: "tecnica",
    10: "universitaria", 11: "universitaria", 12: "universitaria", 13: "universitaria",
    99: "no_informa",
}

# P3069 (tamano de empresa, 1..10) agrupado para el arquetipo:
# 1-4 = hasta 10 personas (micro), 5-8 = 11-100 (pyme), 9-10 = 101+ (grande)
TAMANO_GRUPO = {1: "micro", 2: "micro", 3: "micro", 4: "micro",
                5: "pyme", 6: "pyme", 7: "pyme", 8: "pyme",
                9: "grande", 10: "grande"}


def sector_de(rama2d: float) -> tuple[str, str]:
    if pd.isna(rama2d):
        return "no_informa", "nin"
    r = int(rama2d)
    for (lo, hi), nombre, abrev in SECTORES:
        if lo <= r <= hi:
            return nombre, abrev
    return "no_informa", "nin"


def cuantil_ponderado(valores: np.ndarray, pesos: np.ndarray, q: float) -> float:
    orden = np.argsort(valores)
    v, w = valores[orden], pesos[orden]
    acum = np.cumsum(w) - 0.5 * w
    return float(np.interp(q * w.sum(), acum, v))


def _carpeta_csv(anio: int, mes: str) -> Path:
    """Localiza la carpeta CSV del mes, tolerando el anidamiento del ZIP.

    Los ZIP del DANE no traen la misma estructura todos los años. 2025 y 2026
    descomprimen a `GEIH_<anio>_<mes>/CSV/`; los de 2024 traen una carpeta más
    adentro (`GEIH_2024_enero/Ene_2024/CSV/`), porque ANDA los publica con el
    nombre del mes abreviado. Es una diferencia de empaquetado, no de contenido:
    los ocho módulos y sus nombres son idénticos.

    Se busca a un nivel y luego a dos, y NADA MÁS. Si apareciera un tercer nivel
    hay que mirarlo a mano en vez de barrer el árbol entero: un `rglob` podría
    engancharse con la carpeta de otro mes y mezclar períodos en silencio.
    """
    raiz = RAW / f"GEIH_{anio}_{mes}"
    if not raiz.is_dir():
        raise FileNotFoundError(f"no existe {raiz}; corre data/descargar_geih.py --anio {anio}")

    # La carpeta buena es la que CONTIENE los modulos, no la que se llama "CSV":
    # en marzo y abril de 2024 hay un `CSV/CSV/` porque el ZIP venia doble, y
    # quedarse con el primer `CSV` daba una carpeta sin datos.
    candidatas = sorted(
        {p.parent for p in raiz.rglob("Ocupados.CSV")}
        | {p.parent for p in raiz.rglob("Ocupados.csv")}
    )
    if len(candidatas) == 1:
        return candidatas[0]
    if not candidatas:
        raise FileNotFoundError(f"no encontre Ocupados.CSV bajo {raiz}")
    raise RuntimeError(
        f"{raiz} tiene {len(candidatas)} carpetas con Ocupados.CSV: {[str(c) for c in candidatas]}. "
        "No se adivina cual es el mes; revisalo a mano antes de mezclar periodos."
    )


def cargar_mes(mes: str, anio: int = 2026) -> pd.DataFrame:
    base = _carpeta_csv(anio, mes)
    occ = pd.read_csv(base / "Ocupados.CSV", sep=";", encoding="latin-1", low_memory=False)
    occ = occ[occ["AREA"] == AREA_BOGOTA]
    # El nombre del archivo varia entre meses (p.ej. abril: "Capítulos de
    # características generales..."), se localiza por patron.
    [car_path] = [p for p in base.iterdir() if "sticas generales" in p.name and p.suffix.upper() == ".CSV"]
    car = pd.read_csv(
        car_path,
        sep=";", encoding="latin-1", low_memory=False,
        usecols=LLAVE + ["P3042"],
    )
    df = occ.merge(car, on=LLAVE, how="left", validate="one_to_one")
    df["mes_num"] = NUM_MES[mes]
    return df


def construir(anio: int = 2026, meses: list[str] | None = None) -> tuple[pd.DataFrame, dict]:
    ventana_explicita = meses is not None
    meses = MESES if meses is None else meses
    crudo = pd.concat([cargar_mes(m, anio) for m in meses], ignore_index=True)
    n_crudo = len(crudo)

    # Ingreso: INGLABO es el ingreso laboral mensual total que calcula el DANE.
    # Se excluyen registros sin ingreso reportado (no se imputa nada).
    df = crudo[crudo["INGLABO"].notna()].copy()
    n_sin_ingreso = n_crudo - len(df)

    # SUPUESTO: formal = cotiza a pension (P6920==1); "ya es pensionado" (3)
    # se cuenta como formal. Es un proxy de la definicion OIT de empleo informal
    # que usa el DANE (esa requiere cruzar mas modulos); el sesgo se evalua
    # contra la serie oficial de informalidad en la validacion (candado 1).
    df["formal"] = df["P6920"].isin([1, 3])

    sec = df["RAMA2D_R4"].map(lambda r: sector_de(r))
    df["sector"] = sec.map(lambda t: t[0])
    df["sector_abrev"] = sec.map(lambda t: t[1])

    df["tamano_empresa"] = df["P3069"].fillna(1).astype(int)
    # SUPUESTO: P3069 faltante (independientes sin la pregunta) = "trabaja solo" (1),
    # el caso modal de los independientes.
    df["tamano_grupo"] = df["tamano_empresa"].map(TAMANO_GRUPO)

    df["educacion"] = df["P3042"].map(EDUCACION).fillna("no_informa")

    # Pooling de 6 meses: el factor de expansion mensual se divide entre el
    # numero de meses apilados (practica estandar GEIH para promedios de periodo).
    df["factor_expansion"] = df["FEX_C18"].astype(float) / len(meses)

    df["ingreso_mensual_cop"] = df["INGLABO"].astype(float).round().astype("int64")

    # Terciles de ingreso ponderados (sobre ingresos positivos; ingreso 0 -> t1)
    pos = df["ingreso_mensual_cop"] > 0
    v = df.loc[pos, "ingreso_mensual_cop"].to_numpy(float)
    w = df.loc[pos, "factor_expansion"].to_numpy(float)
    t1 = cuantil_ponderado(v, w, 1 / 3)
    t2 = cuantil_ponderado(v, w, 2 / 3)
    df["tercil"] = np.select(
        [df["ingreso_mensual_cop"] <= t1, df["ingreso_mensual_cop"] <= t2], [1, 2], default=3
    )

    # Arquetipo preliminar: sector x tamano x formal/informal x tercil,
    # con colapso de celdas chicas para quedar en el rango ~40-60 del plan (D4):
    # una celda con menos de MIN_OBS observaciones muestrales pierde primero el
    # tercil y luego el tamano (un arquetipo con 5 encuestados no es una
    # distribucion, es una anecdota). Las celdas sector x estado que aun asi
    # queden bajo el piso se conservan: mezclar sectores romperia el mapa
    # distributivo (dato A3). La definicion FINAL se cierra con Nico (R3)
    # hacia H+14; cambiarla es tocar SOLO esta funcion y regenerar.
    MIN_OBS = 60
    estado = np.where(df["formal"], "formal", "informal")
    fino = (df["sector_abrev"] + "-" + df["tamano_grupo"] + "-" + estado
            + "-t" + df["tercil"].astype(str))
    medio = df["sector_abrev"] + "-" + df["tamano_grupo"] + "-" + estado
    grueso = df["sector_abrev"] + "-" + estado

    arquetipo = fino.copy()
    chicos = arquetipo.map(arquetipo.value_counts()) < MIN_OBS
    arquetipo[chicos] = medio[chicos]
    chicos = arquetipo.map(arquetipo.value_counts()) < MIN_OBS
    arquetipo[chicos] = grueso[chicos]
    df["arquetipo"] = arquetipo

    df["id"] = (
        f"geih-{anio}-m" + df["mes_num"].astype(str).str.zfill(2) + "-"
        + df["DIRECTORIO"].astype(str) + "-" + df["SECUENCIA_P"].astype(str)
        + "-" + df["ORDEN"].astype(str)
    )
    df["tipo"] = "trabajador"
    df["ciudad"] = "Bogotá"

    poblacion = df[[
        "id", "tipo", "ciudad", "sector", "tamano_empresa", "ingreso_mensual_cop",
        "formal", "educacion", "factor_expansion", "arquetipo",
    ]].sort_values("id", kind="mergesort").reset_index(drop=True)

    # --- momentos.json: los objetivos de calibracion ---
    wtot = df["factor_expansion"].sum()

    def tasa_informalidad(sub: pd.DataFrame) -> float:
        return float(sub.loc[~sub["formal"], "factor_expansion"].sum() / sub["factor_expansion"].sum())

    percentiles = {f"p{int(q*100)}": round(cuantil_ponderado(v, w, q))
                   for q in [0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95]}

    # Spike salarial: la moda del ingreso (redondeado a 10.000 COP) y su masa.
    # SUPUESTO: se reporta la moda observada; que coincida con el SMLMV 2026
    # lo confirma R5 con la serie de decretos (V4) — aqui no se fija el valor.
    redondeado = (df.loc[pos, "ingreso_mensual_cop"] / 10_000).round() * 10_000
    masa = df.loc[pos].groupby(redondeado)["factor_expansion"].sum()
    moda = int(masa.idxmax())
    spike = float(masa.max() / masa.sum())

    periodo = "enero-junio" if meses == MESES else f"{meses[0]}-{meses[-1]}"
    momentos = {
        "fuente": f"GEIH {anio} {periodo}, Bogota (AREA=11), modulo Ocupados - calculado por data/construir_poblacion.py",
        "n_muestra": int(len(df)),
        "n_descartados_sin_ingreso": int(n_sin_ingreso),
        "ocupados_expandidos": round(float(wtot)),
        "tasa_informalidad_total": round(tasa_informalidad(df), 4),
        "tasa_informalidad_por_sector": {
            s: round(tasa_informalidad(g), 4) for s, g in df.groupby("sector")
        },
        "tasa_informalidad_por_tamano": {
            t: round(tasa_informalidad(g), 4) for t, g in df.groupby("tamano_grupo")
        },
        "distribucion_salarial_cop": percentiles,
        "spike_salarial": {
            "moda_ingreso_cop": moda,
            "masa_en_moda": round(spike, 4),
            "nota": f"verificar contra SMLMV {anio} (V4, R5)",
        },
        "terciles_ingreso_cop": {"t1_max": round(t1), "t2_max": round(t2)},
        "n_arquetipos": int(poblacion["arquetipo"].nunique()),
    }
    if ventana_explicita:
        momentos["meses"] = meses
    return poblacion, momentos


def _parsear_meses(valor: str) -> list[str]:
    meses = [mes.strip().lower() for mes in valor.split(",") if mes.strip()]
    if not meses:
        raise argparse.ArgumentTypeError("--meses requiere al menos un mes")
    invalidos = [mes for mes in meses if mes not in MESES]
    if invalidos:
        validos = ", ".join(MESES)
        raise argparse.ArgumentTypeError(
            f"mes(es) no válido(s): {', '.join(invalidos)}; opciones: {validos}"
        )
    return meses


def main() -> None:
    parser = argparse.ArgumentParser(description="Construye la población GEIH de Bogotá.")
    parser.add_argument("--anio", type=int, choices=(2024, 2025, 2026), default=2026)
    parser.add_argument(
        "--meses",
        type=_parsear_meses,
        help="meses separados por comas; por ejemplo: abril,mayo,junio",
    )
    args = parser.parse_args()

    poblacion, momentos = construir(args.anio, args.meses)
    out = Path(__file__).parent
    sufijo_anio = "" if args.anio == 2026 else f"_{args.anio}"
    if args.meses:
        # Una ventana parcial escribe SOLO los momentos. El parquet de la ventana
        # completa es el entregable de R1 y todo el equipo construye contra el;
        # versionar ademas un parquet por corte duplicaria microdatos para
        # responder una sola pregunta: como se ve la ventana que publica el DANE.
        ventana = f"{args.meses[0][:3]}_{args.meses[-1][:3]}"
        momentos_path = out / f"momentos_{ventana}{sufijo_anio}.json"
        salida_principal = momentos_path.name
    else:
        poblacion_path = out / f"poblacion{sufijo_anio}.parquet"
        momentos_path = out / f"momentos{sufijo_anio}.json"
        poblacion.to_parquet(poblacion_path, index=False)
        salida_principal = poblacion_path.name

    with open(momentos_path, "w", encoding="utf-8") as f:
        json.dump(momentos, f, ensure_ascii=False, indent=2)
    print(f"{salida_principal}: {len(poblacion)} agentes, "
          f"{momentos['ocupados_expandidos']:,} ocupados expandidos, "
          f"{momentos['n_arquetipos']} arquetipos")
    print(f"informalidad total: {momentos['tasa_informalidad_total']:.1%}")
    print(f"spike: {momentos['spike_salarial']['masa_en_moda']:.1%} de la masa "
          f"en {momentos['spike_salarial']['moda_ingreso_cop']:,} COP")


if __name__ == "__main__":
    main()
