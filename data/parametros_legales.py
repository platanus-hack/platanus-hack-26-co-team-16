"""Parametros legales del costo laboral colombiano -> data/parametros_legales.json.

Por que existe este archivo. El motor (`engine/costos.py`) necesita el costo de
tener a alguien formal. Hoy ese numero es el supuesto S1 de `engine/MODELO.md`
("factor prestacional ~1,4-1,5, sin cifra exacta verificada") y en `behavior/`
aparece como coeficientes de andamio (`ingreso * 1.5` para el despido). Ninguno
de los dos es un dato. Este modulo los reemplaza por las tasas de la norma, cada
una con su articulo y su URL, igual que se hizo con la GEIH en DESCARGA.json.

Hallazgo principal: el factor prestacional NO es un numero con incertidumbre.
Son DOS numeros, y cual aplica depende del tamano del empleador. El articulo
114-1 del Estatuto Tributario exonera de salud patronal (8,5%), SENA (2%) e
ICBF (3%) a las personas juridicas y a las personas naturales con 2 o mas
trabajadores, sobre cada trabajador que gane menos de 10 SMLMV. Un empleador
con UN solo trabajador no esta exonerado y paga 13,5 puntos mas. La frontera
cae exactamente donde el modelo mira: el micro-empleador.

Segundo hallazgo: el auxilio de transporte (249.095 COP en 2026) es un costo
fijo, no un porcentaje. Sobre el salario minimo pesa 14,2%; sobre un salario
de 4 millones no se paga. Encarece la formalidad justo en el tramo bajo, que
es donde vive la informalidad que el modelo intenta explicar.

Entrada:  ninguna. Son constantes normativas, verificadas contra fuente.
Salida:   data/parametros_legales.json

Determinista por construccion: no lee datos ni muestrea.

Uso:  python data/parametros_legales.py
"""

from __future__ import annotations

import json
from pathlib import Path

SALIDA = Path(__file__).parent / "parametros_legales.json"

VIGENCIA = 2026

# --- Salario y auxilio de transporte -----------------------------------------
# Decreto 1469 del 29 de diciembre de 2025. El decreto estuvo suspendido y el
# Consejo de Estado revoco la suspension en julio de 2026: la cifra quedo firme.
SMLMV = {2025: 1_423_500, 2026: 1_750_905}
AUXILIO_TRANSPORTE = {2025: 200_000, 2026: 249_095}
AUXILIO_TOPE_SMLMV = 2  # se paga a quien gane hasta 2 SMLMV (Ley 15 de 1959)

# --- Seguridad social a cargo del empleador ----------------------------------
# Ley 100 de 1993. La reforma pensional (Ley 2381 de 2024) esta SUSPENDIDA
# desde junio de 2025 por el Auto 841/2025 de la Corte Constitucional, asi que
# en 2026 rige la Ley 100 sin cambios en la cotizacion.
PENSION_TOTAL = 0.16          # 16% del IBC
PENSION_EMPLEADOR = 0.12      # 75% del total (el 4% restante lo paga el trabajador)
SALUD_TOTAL = 0.125           # 12,5% del IBC
SALUD_EMPLEADOR = 0.085       # 8,5% (exonerable, ver EXONERACION_114_1)

# Decreto 1772 de 1994 (tarifas) y Decreto 1607 de 2002 (tabla de actividades).
# 100% a cargo del empleador. Iguales para todas las ARL del pais.
ARL_POR_CLASE = {"I": 0.00522, "II": 0.01044, "III": 0.02436, "IV": 0.04350, "V": 0.06960}

# SUPUESTO: la clase de riesgo por sector. El Decreto 1607 clasifica por
# actividad economica a 4 digitos; nuestros 9 sectores son agregados de la CIIU
# a 2 digitos, asi que cada sector mezcla varias clases. Se asigna la clase
# modal del sector. Es el parametro menos solido de este archivo y el de menor
# impacto (mueve el factor entre 0,5 y 7 puntos); R5 puede barrerlo.
CLASE_RIESGO_POR_SECTOR = {
    "agro_mineria": "V",
    "industria": "III",
    "construccion_utilities": "V",
    "comercio": "I",
    "transporte": "IV",
    "alojamiento_comida": "II",
    "servicios_empresariales": "I",
    "adm_publica_edu_salud": "III",
    "otros_servicios": "I",
    "no_informa": "III",
}

# --- Parafiscales -------------------------------------------------------------
CAJA_COMPENSACION = 0.04  # Ley 21 de 1982. NO exonerable: la paga todo empleador.
SENA = 0.02               # Ley 21 de 1982. Exonerable.
ICBF = 0.03               # Ley 89 de 1988. Exonerable.

# --- Exoneracion del articulo 114-1 del Estatuto Tributario -------------------
# Introducido por la Ley 1607 de 2012, modificado por la Ley 1819 de 2016.
# Exonera de salud patronal, SENA e ICBF a las personas juridicas y a las
# personas naturales que empleen DOS O MAS trabajadores, sobre cada trabajador
# que devengue MENOS de 10 SMLMV. El empleador con un solo trabajador no aplica.
EXONERACION_MIN_TRABAJADORES = 2
EXONERACION_TOPE_SMLMV = 10

# --- Prestaciones sociales ----------------------------------------------------
# Provisiones mensuales sobre el salario, convencion estandar de nomina.
PRIMA_SERVICIOS = 0.0833      # 30 dias de salario al ano (Art. 306 CST) = 30/360
CESANTIAS = 0.0833            # 30 dias de salario al ano (Art. 249 CST) = 30/360
INTERESES_CESANTIAS = 0.01    # 12% anual sobre las cesantias (Ley 52 de 1975) = 1% del salario
VACACIONES = 0.0417           # 15 dias de salario al ano (Art. 186 CST) = 15/360

# --- Indemnizacion por despido sin justa causa --------------------------------
# Art. 64 CST, contrato a termino indefinido. Reemplaza el `ingreso * 1.5` de
# `behavior/arquetipos.py`, que era un coeficiente de andamio sin fuente.
# Para salarios < 10 SMLMV: 30 dias por el primer ano + 20 dias por cada ano
# adicional. Para salarios >= 10 SMLMV: 20 dias + 15 dias por ano adicional.
INDEMNIZACION = {
    "bajo_10_smlmv": {"dias_primer_ano": 30, "dias_ano_adicional": 20},
    "desde_10_smlmv": {"dias_primer_ano": 20, "dias_ano_adicional": 15},
}

# SUPUESTO: antiguedad promedio de 3 anos para convertir la formula del Art. 64
# en un costo por trabajador. La GEIH publica no trae antiguedad en el modulo
# que usamos, asi que no se puede observar. Con 3 anos y salario < 10 SMLMV:
# 30 + 20*2 = 70 dias = 2,33 meses de salario. Es el parametro a barrer si el
# veto por caja resulta apretado.
ANTIGUEDAD_ANOS_SUPUESTA = 3

FUENTES = {
    "smlmv_2026": "Decreto 1469 de 2025 (29-dic-2025); suspension revocada por el Consejo de Estado en julio de 2026. https://www.hklaw.com/en/insights/publications/2025/12/colombia-decreta-aumento-del-salario-minimo-y-auxilio-de-transporte",
    "pension_salud": "Ley 100 de 1993. Reforma pensional (Ley 2381 de 2024) suspendida por Auto 841/2025 de la Corte Constitucional; en 2026 rige la Ley 100. https://actualicese.com/aportes-a-pension-2026/",
    "arl": "Decreto 1772 de 1994 (tarifas) y Decreto 1607 de 2002 (clasificacion). https://sgsst.com.co/decretos/decreto-1607-de-2002/",
    "parafiscales": "Ley 21 de 1982 (caja 4%, SENA 2%) y Ley 89 de 1988 (ICBF 3%).",
    "exoneracion": "Art. 114-1 del Estatuto Tributario, adicionado por la Ley 1607 de 2012 y modificado por la Ley 1819 de 2016.",
    "prestaciones": "Codigo Sustantivo del Trabajo, Arts. 306 (prima), 249 (cesantias), 186 (vacaciones) y Ley 52 de 1975 (intereses).",
    "indemnizacion": "Art. 64 del Codigo Sustantivo del Trabajo. https://leyes.co/codigo_sustantivo_del_trabajo/64.htm",
}


def factor_prestacional(clase_riesgo: str, exonerado: bool) -> dict:
    """El multiplicador del salario que cuesta un trabajador formal.

    Devuelve el desglose ademas del total: el motor necesita el numero, pero un
    revisor necesita ver de donde sale cada punto porcentual.
    """
    if clase_riesgo not in ARL_POR_CLASE:
        raise ValueError(f"clase de riesgo desconocida: {clase_riesgo!r}")

    desglose = {
        "pension_empleador": PENSION_EMPLEADOR,
        "salud_empleador": 0.0 if exonerado else SALUD_EMPLEADOR,
        "arl": ARL_POR_CLASE[clase_riesgo],
        "caja_compensacion": CAJA_COMPENSACION,
        "sena": 0.0 if exonerado else SENA,
        "icbf": 0.0 if exonerado else ICBF,
        "prima_servicios": PRIMA_SERVICIOS,
        "cesantias": CESANTIAS,
        "intereses_cesantias": INTERESES_CESANTIAS,
        "vacaciones": VACACIONES,
    }
    sobrecosto = sum(desglose.values())
    return {
        "clase_riesgo": clase_riesgo,
        "exonerado": exonerado,
        "desglose": {k: round(v, 5) for k, v in desglose.items()},
        "sobrecosto_pct": round(sobrecosto, 5),
        "factor": round(1.0 + sobrecosto, 5),
    }


def costo_despido_meses(antiguedad_anos: int = ANTIGUEDAD_ANOS_SUPUESTA,
                        salario_cop: float | None = None) -> float:
    """Indemnizacion del Art. 64 CST expresada en MESES de salario.

    El motor la multiplica por el salario del trabajador. Se devuelve en meses
    y no en pesos para que sirva a cualquier nivel salarial.
    """
    alto = salario_cop is not None and salario_cop >= 10 * SMLMV[VIGENCIA]
    tabla = INDEMNIZACION["desde_10_smlmv" if alto else "bajo_10_smlmv"]
    dias = tabla["dias_primer_ano"] + tabla["dias_ano_adicional"] * max(0, antiguedad_anos - 1)
    return round(dias / 30.0, 4)


def auxilio_transporte_cop(salario_cop: float) -> int:
    """Auxilio de transporte: costo FIJO, solo hasta 2 SMLMV. No entra al IBC de
    seguridad social, pero si a la base de prima y cesantias."""
    if salario_cop > AUXILIO_TOPE_SMLMV * SMLMV[VIGENCIA]:
        return 0
    return AUXILIO_TRANSPORTE[VIGENCIA]


def construir() -> dict:
    factores = {}
    for sector, clase in CLASE_RIESGO_POR_SECTOR.items():
        factores[sector] = {
            "exonerado": factor_prestacional(clase, exonerado=True),
            "no_exonerado": factor_prestacional(clase, exonerado=False),
        }

    todos = [f[k]["factor"] for f in factores.values() for k in ("exonerado", "no_exonerado")]

    return {
        "fuente": "Normativa laboral y tributaria colombiana vigente en 2026 - "
                  "recopilada y verificada por data/parametros_legales.py",
        "vigencia": VIGENCIA,
        "salario": {
            "smlmv_cop": SMLMV[VIGENCIA],
            "smlmv_anterior_cop": SMLMV[VIGENCIA - 1],
            "aumento_pct": round(SMLMV[VIGENCIA] / SMLMV[VIGENCIA - 1] - 1, 4),
            "auxilio_transporte_cop": AUXILIO_TRANSPORTE[VIGENCIA],
            "auxilio_transporte_tope_smlmv": AUXILIO_TOPE_SMLMV,
            "auxilio_como_pct_del_smlmv": round(
                AUXILIO_TRANSPORTE[VIGENCIA] / SMLMV[VIGENCIA], 4),
        },
        "tasas_empleador": {
            "pension": PENSION_EMPLEADOR,
            "salud": SALUD_EMPLEADOR,
            "caja_compensacion": CAJA_COMPENSACION,
            "sena": SENA,
            "icbf": ICBF,
            "arl_por_clase": ARL_POR_CLASE,
            "prima_servicios": PRIMA_SERVICIOS,
            "cesantias": CESANTIAS,
            "intereses_cesantias": INTERESES_CESANTIAS,
            "vacaciones": VACACIONES,
        },
        "exoneracion_114_1": {
            "min_trabajadores": EXONERACION_MIN_TRABAJADORES,
            "tope_salario_smlmv": EXONERACION_TOPE_SMLMV,
            "conceptos_exonerados": ["salud_empleador", "sena", "icbf"],
            "puntos_porcentuales": round(SALUD_EMPLEADOR + SENA + ICBF, 5),
            "nota": "El empleador con UN solo trabajador no esta exonerado y paga "
                    "13,5 puntos mas. La frontera cae en el micro-empleador, que es "
                    "donde vive el 66,7% de la informalidad de Bogota (momentos.json).",
        },
        "clase_riesgo_por_sector": CLASE_RIESGO_POR_SECTOR,
        "factor_prestacional_por_sector": factores,
        "factor_prestacional_rango": {
            "min": min(todos),
            "max": max(todos),
            "nota": "El rango NO es incertidumbre: es estructura. El extremo bajo es "
                    "un empleador exonerado en un sector de riesgo I; el alto, un "
                    "empleador de un solo trabajador en riesgo V. El motor debe "
                    "asignar el factor que corresponde a cada firma, no promediar.",
        },
        "indemnizacion_despido": {
            "articulo": "Art. 64 CST, contrato a termino indefinido",
            "dias": INDEMNIZACION,
            "antiguedad_anos_supuesta": ANTIGUEDAD_ANOS_SUPUESTA,
            "meses_de_salario_bajo_10_smlmv": costo_despido_meses(),
            "nota": "Reemplaza el coeficiente de andamio `ingreso * 1.5` de "
                    "behavior/arquetipos.py, que no tenia fuente.",
        },
        "fuentes": FUENTES,
    }


def main() -> None:
    datos = construir()
    SALIDA.write_text(json.dumps(datos, indent=2, ensure_ascii=False), encoding="utf-8")

    rango = datos["factor_prestacional_rango"]
    sal = datos["salario"]
    print(f"\n  {SALIDA.name} escrito.\n")
    print(f"  SMLMV {VIGENCIA}: {sal['smlmv_cop']:,} COP  "
          f"(+{sal['aumento_pct']:.1%} sobre {sal['smlmv_anterior_cop']:,})")
    print(f"  Auxilio de transporte: {sal['auxilio_transporte_cop']:,} COP  "
          f"= {sal['auxilio_como_pct_del_smlmv']:.1%} del SMLMV")
    print(f"\n  Factor prestacional: {rango['min']:.3f} a {rango['max']:.3f}")
    for caso, etiqueta in (("exonerado", "exonerado (2+ trabajadores)"),
                           ("no_exonerado", "NO exonerado (1 trabajador)")):
        f = datos["factor_prestacional_por_sector"]["comercio"][caso]
        print(f"    comercio, {etiqueta:<30} {f['factor']:.3f}")
    print(f"\n  Despido (Art. 64, {ANTIGUEDAD_ANOS_SUPUESTA} anos de antiguedad): "
          f"{costo_despido_meses():.2f} meses de salario\n")


if __name__ == "__main__":
    main()
