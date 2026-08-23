// El resumen de una corrida terminada: la forma con la que se escribe al
// histórico del laboratorio y con la que se arma el reporte.
//
// Regla de esta capa, igual que en `api/serializar.py`: acá no se calcula nada
// nuevo. Todo sale del contrato que ya viajó por el cable, o es una suma sobre
// campos que ya existen. Si un número no está en el flujo, no está acá.

import { EventoRonda, Poblacion, usarAlmacen } from "@/estado/simulacion";

/** Una ronda, reducida a lo que se puede graficar y comparar entre corridas. */
export interface RondaRegistrada {
  ronda: number;
  tasa_informalidad: number;
  prob_fiscalizacion: number;
  empleo_relativo: number;
  ingreso_laboral_relativo: number;
  movimiento_pp: number;
  estabilizada: boolean;
  banda_p10: number;
  banda_p90: number;
  banda_degenerada: boolean;
  fraccion_fallback: number;
  fraccion_sin_salida: number;
  fraccion_jornada_recortada: number;
  varianza_media: number;
  /** suma de propuestas vetadas en la ronda — el motor solo la publica por celda */
  vetadas: number;
  /** cuántas celdas se quedaron sin ninguna salida factible */
  celdas_sin_salida: number;
  desglose_estrategias: Record<string, number>;
  desglose_estrategias_conteo: Record<string, number>;
}

export interface CorridaRegistrada {
  ts: string;
  aumento_pct: number;
  seed: number;
  modo: string;
  cobertura: number | null;
  parafrasis: number | null;
  n_arquetipos: number | null;
  tasa_informalidad_observada: number;
  rondas: RondaRegistrada[];
  informalidad_final: number;
  empleo_final: number;
  brecha_pp: number;
  segundos: number | null;
  llamadas_api: number | null;
  gasto_usd: number | null;
}

/**
 * Los vetos por ronda no existen como campo: el motor publica `vetadas` por
 * arquetipo y nunca la suma. Se suma acá, que es exactamente lo que pide
 * `docs/VARIABLES-PENDIENTES.md` B3 — evidencia de que el veto de
 * factibilidad hace algo, como serie y no como dato suelto.
 */
export function vetadasDeRonda(r: EventoRonda): number {
  return Object.values(r.por_arquetipo ?? {}).reduce((s, x) => s + (x?.vetadas ?? 0), 0);
}

export function celdasSinSalidaDeRonda(r: EventoRonda): number {
  return Object.values(r.por_arquetipo ?? {}).filter((x) => (x?.sin_salida ?? 0) > 0).length;
}

export function registrarRonda(r: EventoRonda): RondaRegistrada {
  const c = r.contrato;
  return {
    ronda: c.ronda,
    tasa_informalidad: c.tasa_informalidad,
    prob_fiscalizacion: c.prob_fiscalizacion,
    empleo_relativo: c.empleo_relativo,
    ingreso_laboral_relativo: c.ingreso_laboral_relativo,
    movimiento_pp: c.movimiento_pp,
    estabilizada: c.estabilizada,
    banda_p10: c.banda.p10,
    banda_p90: c.banda.p90,
    banda_degenerada: c.banda.degenerada,
    fraccion_fallback: r.fraccion_fallback,
    fraccion_sin_salida: r.fraccion_sin_salida,
    fraccion_jornada_recortada: r.fraccion_jornada_recortada,
    varianza_media: r.varianza_media,
    vetadas: vetadasDeRonda(r),
    celdas_sin_salida: celdasSinSalidaDeRonda(r),
    desglose_estrategias: r.desglose_estrategias,
    desglose_estrategias_conteo: r.desglose_estrategias_conteo ?? {},
  };
}

/** Arma el registro de la corrida que está en el almacén, o null si no hay. */
export function registrarCorrida(): CorridaRegistrada | null {
  const s = usarAlmacen.getState();
  const pob: Poblacion | null = s.poblacion;
  if (!pob || s.rondas.length === 0) return null;

  const rondas = s.rondas.map(registrarRonda);
  const primera = rondas[0];
  const ultima = rondas[rondas.length - 1];

  return {
    ts: new Date().toISOString(),
    aumento_pct: s.inicio?.aumento_pct ?? s.aumentoPct,
    seed: s.inicio?.seed ?? s.rondas[0].contrato.seed,
    modo: s.modo ?? "desconocido",
    cobertura: s.inicio?.cobertura ?? null,
    parafrasis: s.inicio?.parafrasis ?? null,
    n_arquetipos: s.inicio?.n_arquetipos ?? null,
    tasa_informalidad_observada: pob.tasa_informalidad_observada,
    rondas,
    informalidad_final: ultima.tasa_informalidad,
    empleo_final: ultima.empleo_relativo,
    // la brecha es contra la ronda 0, que es la proyección oficial
    brecha_pp: (ultima.tasa_informalidad - primera.tasa_informalidad) * 100,
    segundos: s.fin?.segundos ?? null,
    llamadas_api: s.fin?.llamadas_api ?? null,
    gasto_usd: s.fin?.gasto_usd ?? null,
  };
}
