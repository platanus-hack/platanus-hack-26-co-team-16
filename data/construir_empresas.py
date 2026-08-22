"""data/poblacion.parquet -> data/empresas.parquet (el lado empleador).

Por que existe. El veto del motor (`engine/veto.py`, ADR 0003) decide sobre una
FIRMA: "esta propuesta no cabe en la caja de esta empresa". Pero la GEIH es una
encuesta de hogares: cada fila es una persona, no un empleador. Sin esta tabla,
quien escriba el veto se inventa la firma, que es exactamente lo que ya pasa en
`behavior/arquetipos.py` con `flujo_caja = ingreso * n * 0.18`.

Que hace. Agrupa a los trabajadores por sector x tamano de establecimiento
(P3069) y reconstruye el empleador tipico de cada celda: cuanta gente emplea, a
cuanto la paga, que fraccion tiene formal, cuanto le cuesta tenerla formal segun
`parametros_legales.json`, y a cuantas empresas reales representa esa celda.

Que NO hace, y es importante. La GEIH no observa ingresos, activos ni margenes
de las empresas: es una encuesta de HOGARES. El flujo de caja no se puede
derivar de ella. Se emite como un supuesto explicito y parametrizado (un margen
sobre la nomina) para que exista en UN solo lugar, con nombre y con rango de
barrido, en vez de aparecer como un 0.18 suelto dentro de otra carpeta. Es el
parametro numero uno que R5 debe barrer.

Entrada:  data/poblacion.parquet, data/parametros_legales.json
Salida:   data/empresas.parquet

Determinista: transformacion pura sin muestreo. Ordenado por empresa_id.

Uso:  python data/construir_empresas.py
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

AQUI = Path(__file__).parent
POBLACION = AQUI / "poblacion.parquet"
PARAMETROS = AQUI / "parametros_legales.json"
SALIDA = AQUI / "empresas.parquet"

# P3069: codigo ordinal 1-10, NO un numero de empleados. Punto medio de cada
# rango declarado. Identico al EMPLEADOS_POR_CODIGO de behavior/arquetipos.py
# a proposito: dos tablas distintas para el mismo codigo serian una divergencia
# silenciosa entre el motor y la capa conductual.
PERSONAS_POR_CODIGO = {
    1: 1,     # trabaja solo
    2: 2.5,   # 2-3
    3: 4.5,   # 4-5
    4: 8,     # 6-10
    5: 15,    # 11-19
    6: 25,    # 20-30
    7: 40,    # 31-50
    8: 75,    # 51-100
    9: 150,   # 101-200
    10: 300,  # 201+  <- SUPUESTO: el rango es abierto, no tiene punto medio.
              # 300 es conservador (la alternativa seria la media de la
              # distribucion de tamanos, que la GEIH no da). Barrer.
}

TAMANO_GRUPO = {1: "micro", 2: "micro", 3: "micro", 4: "micro",
                5: "pyme", 6: "pyme", 7: "pyme", 8: "pyme",
                9: "grande", 10: "grande"}

# SUPUESTO: margen operacional sobre la nomina, es decir cuanta caja libre
# mensual tiene la firma como multiplo de lo que paga en salarios. La GEIH no
# lo observa y no hay fuente en el repo todavia. 0.18 se hereda del andamio de
# behavior/ para no cambiar el resultado del demo al introducir esta tabla; el
# rango de barrido es lo que importa, no el punto.
MARGEN_SOBRE_NOMINA = 0.18
MARGEN_RANGO_BARRIDO = (0.05, 0.40)


def mediana_ponderada(valores: np.ndarray, pesos: np.ndarray) -> float:
    """Mediana ponderada por factor de expansion. Sin el peso no es la mediana
    de Bogota, es la de la muestra."""
    orden = np.argsort(valores)
    v, w = valores[orden], pesos[orden]
    acum = np.cumsum(w)
    if acum[-1] <= 0:
        return float("nan")
    return float(v[np.searchsorted(acum, 0.5 * acum[-1])])


def construir() -> tuple[pd.DataFrame, dict]:
    df = pd.read_parquet(POBLACION)
    par = json.loads(PARAMETROS.read_text(encoding="utf-8"))

    faltan = {"sector", "tamano_empresa", "ingreso_mensual_cop", "formal",
              "factor_expansion"} - set(df.columns)
    if faltan:
        raise ValueError(f"{POBLACION} no cumple contracts/agente.json; faltan: {sorted(faltan)}")

    malos = sorted(set(df["tamano_empresa"].unique()) - set(PERSONAS_POR_CODIGO))
    if malos:
        raise ValueError(f"codigos de tamano_empresa fuera de 1-10: {malos}")

    # Codigo 1 = "trabaja solo": es un cuenta propia, no un empleador. No tiene
    # nomina que informalizar, asi que no genera una fila de empresa. Se cuenta
    # aparte porque es un tercio de la muestra y el motor debe saber que existe.
    cuenta_propia = df[df["tamano_empresa"] == 1]
    con_empleador = df[df["tamano_empresa"] > 1]

    smlmv = par["salario"]["smlmv_cop"]
    auxilio = par["salario"]["auxilio_transporte_cop"]
    tope_auxilio = par["salario"]["auxilio_transporte_tope_smlmv"] * smlmv
    factores = par["factor_prestacional_por_sector"]
    min_trab_exoneracion = par["exoneracion_114_1"]["min_trabajadores"]

    filas = []
    for (sector, codigo), g in con_empleador.groupby(
        ["sector", "tamano_empresa"], observed=True
    ):
        personas = PERSONAS_POR_CODIGO[int(codigo)]
        # SUPUESTO: uno de los ocupados del establecimiento es el dueno, asi que
        # los EMPLEADOS son las personas menos uno. Importa en el codigo 2
        # (2-3 personas): ahi la firma emplea a 1 o 2, y con 1 solo empleado
        # pierde la exoneracion del Art. 114-1 y paga 13,5 puntos mas.
        empleados = max(1.0, personas - 1)

        peso = g["factor_expansion"].to_numpy()
        ingreso = g["ingreso_mensual_cop"].to_numpy()
        trabajadores_exp = float(peso.sum())

        salario_mediano = mediana_ponderada(ingreso, peso)
        nomina = salario_mediano * empleados

        exonerada = empleados >= min_trab_exoneracion and salario_mediano < 10 * smlmv
        f = factores[sector]["exonerado" if exonerada else "no_exonerado"]

        aux_por_trabajador = auxilio if salario_mediano <= tope_auxilio else 0
        costo_formal = nomina * f["factor"] + aux_por_trabajador * empleados

        filas.append({
            "empresa_id": f"emp-{sector}-t{int(codigo):02d}",
            "sector": sector,
            "tamano_codigo": int(codigo),
            "tamano_grupo": TAMANO_GRUPO[int(codigo)],
            "n_personas": float(personas),
            "n_empleados": float(empleados),
            # A cuantas empresas reales de Bogota representa esta fila.
            "n_empresas_expandidas": round(trabajadores_exp / empleados, 1),
            "trabajadores_expandidos": round(trabajadores_exp, 1),
            "salario_mediano_cop": int(salario_mediano),
            "nomina_mensual_cop": int(round(nomina)),
            "share_formal": round(float((peso * g["formal"].to_numpy()).sum() / trabajadores_exp), 4),
            "clase_riesgo": f["clase_riesgo"],
            "exonerada_114_1": bool(exonerada),
            "factor_prestacional": f["factor"],
            "auxilio_transporte_cop": int(aux_por_trabajador),
            "costo_formal_mensual_cop": int(round(costo_formal)),
            "sobrecosto_formal_pct": round(costo_formal / nomina - 1, 4),
            "flujo_caja_mensual_cop": int(round(nomina * MARGEN_SOBRE_NOMINA)),
            "costo_despido_por_empleado_cop": int(round(
                salario_mediano * par["indemnizacion_despido"]["meses_de_salario_bajo_10_smlmv"])),
            "n_muestra": int(len(g)),
        })

    empresas = pd.DataFrame(filas).sort_values("empresa_id").reset_index(drop=True)

    peso_cp = cuenta_propia["factor_expansion"].to_numpy()
    resumen = {
        "n_celdas_empresa": int(len(empresas)),
        "empresas_expandidas": round(float(empresas["n_empresas_expandidas"].sum()), 1),
        "trabajadores_con_empleador_expandidos": round(
            float(empresas["trabajadores_expandidos"].sum()), 1),
        "cuenta_propia_expandidos": round(float(peso_cp.sum()), 1),
        "cuenta_propia_share": round(
            float(peso_cp.sum()) / float(df["factor_expansion"].sum()), 4),
        "margen_sobre_nomina_supuesto": MARGEN_SOBRE_NOMINA,
        "margen_rango_barrido": list(MARGEN_RANGO_BARRIDO),
        "celdas_sin_exoneracion": int((~empresas["exonerada_114_1"]).sum()),
    }
    return empresas, resumen


def main() -> None:
    empresas, r = construir()
    empresas.to_parquet(SALIDA, index=False)

    print(f"\n  {SALIDA.name}: {len(empresas)} celdas de empresa.\n")
    print(f"  Empresas expandidas de Bogota:        {r['empresas_expandidas']:>14,.0f}")
    print(f"  Trabajadores con empleador:           {r['trabajadores_con_empleador_expandidos']:>14,.0f}")
    print(f"  Cuenta propia (sin nomina):           {r['cuenta_propia_expandidos']:>14,.0f}"
          f"  = {r['cuenta_propia_share']:.1%} de los ocupados")
    print(f"  Celdas SIN exoneracion Art. 114-1:    {r['celdas_sin_exoneracion']:>14}")
    print("\n  Sobrecosto de la formalidad por grupo de tamano:")
    for grupo, g in empresas.groupby("tamano_grupo", observed=True):
        print(f"    {grupo:<8} factor {g['factor_prestacional'].min():.3f}-"
              f"{g['factor_prestacional'].max():.3f}   "
              f"sobrecosto total {g['sobrecosto_formal_pct'].min():.1%}-"
              f"{g['sobrecosto_formal_pct'].max():.1%}")
    print(f"\n  SUPUESTO a barrer: margen sobre nomina = {r['margen_sobre_nomina_supuesto']} "
          f"(rango {r['margen_rango_barrido']}). La GEIH no observa caja.\n")


if __name__ == "__main__":
    main()
