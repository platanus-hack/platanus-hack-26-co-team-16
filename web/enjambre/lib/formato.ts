// Formatos es-CO: coma decimal, punto de miles. Todo número visible pasa por acá.

export function pct(x: number, decimales = 1): string {
  return `${(x * 100).toFixed(decimales).replace(".", ",")} %`;
}

export function pp(x: number, decimales = 1): string {
  const v = x.toFixed(decimales).replace(".", ",");
  return `${x >= 0 ? "+" : ""}${v} pp`;
}

export function miles(x: number): string {
  return Math.round(x).toLocaleString("es-CO");
}

export function copBillones(x: number): string {
  // billón español = 10^12
  return `$ ${(x / 1e12).toFixed(2).replace(".", ",")} billones`;
}

export function copMes(x: number): string {
  return `$ ${miles(x)}`;
}

export const NOMBRE_ESTRATEGIA: Record<string, string> = {
  informalizar: "informalizar",
  despedir: "despedir",
  bajar_horas: "bajar horas",
  cumplir: "cumplir",
  subir_precios: "subir precios",
  renegociar: "renegociar",
  absorber: "absorber",
  otra: "otra",
};

export function nombreEstrategia(k: string): string {
  return NOMBRE_ESTRATEGIA[k] ?? k.replace(/_/g, " ");
}

// Los 9 sectores reales de data/empresas.parquet
export const NOMBRE_SECTOR: Record<string, string> = {
  adm_publica_edu_salud: "adm. pública, educación y salud",
  agro_mineria: "agro y minería",
  alojamiento_comida: "alojamiento y comida",
  comercio: "comercio",
  construccion_utilities: "construcción y utilities",
  industria: "industria",
  otros_servicios: "otros servicios",
  servicios_empresariales: "servicios empresariales",
  transporte: "transporte",
};

export function nombreSector(k: string): string {
  return NOMBRE_SECTOR[k] ?? k.replace(/_/g, " ");
}
