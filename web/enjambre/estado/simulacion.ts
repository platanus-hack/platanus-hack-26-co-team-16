// El almacén central del enjambre (zustand). Los componentes React leen de acá
// con selectores; la escena three.js lee por frame con `getState()` para no
// re-renderizar React a 60 fps.

import { create } from "zustand";

// ---- Tipos de los eventos que emite api/servidor.py -------------------------

export interface ArquetipoEstatico {
  id: string;
  sector: string;
  tamano: string;
  tramo_ingreso: string;
  n_trabajadores: number;
  ingreso_por_trabajador: number;
  flujo_caja_mensual: number;
  peso: number;
  n_empresas: number;
  factor_prestacional: number;
  fraccion_informal_inicial: number;
}

export interface Poblacion {
  arquetipos: ArquetipoEstatico[];
  peso_total: number;
  tasa_informalidad_observada: number;
  ocupados_expandidos: number;
  cuenta_propia: { peso_cuenta_propia: number; fraccion_cuenta_propia: number };
  piso_salarial_anterior: number;
  rondas_totales: number;
  meses_por_ronda: number;
}

export interface EstadoCelda {
  fraccion_informal: number;
  fraccion_empleada: number;
  horas: number;
}

export interface ContratoRonda {
  simulacion_id: string;
  seed: number;
  ronda: number;
  politica: { tipo: string; aumento_pct: number };
  tasa_informalidad: number;
  prob_fiscalizacion: number;
  empleo_relativo: number;
  banda: { p10: number; p90: number; degenerada: boolean; tipo?: string };
  traslado_precios_pct: number;
  ingreso_laboral_relativo: number;
  movimiento_pp: number;
  estabilizada: boolean;
}

export interface ResumenArquetipo {
  dominante: string | null;
  estrategia_cruda: string | null;
  distribucion: Record<string, number>;
  justificacion: string | null;
  detalle: Record<string, unknown> | null;
  vetadas: number;
  razones_veto: string[];
  fallbacks: number;
  sin_salida: number;
}

export interface EventoRonda {
  contrato: ContratoRonda;
  desglose_estrategias: Record<string, number>;
  desglose_estrategias_conteo: Record<string, number>;
  fraccion_jornada_recortada: number;
  fraccion_fallback: number;
  fraccion_sin_salida: number;
  fraccion_poblacion_llm: number;
  varianza_media: number;
  estado_por_arquetipo: Record<string, EstadoCelda>;
  por_arquetipo: Record<string, ResumenArquetipo>;
  masa_salarial_relativa: number | null;
  fraccion_bajo_minimo: number | null;
}

export interface EventoDecision extends ResumenArquetipo {
  ronda: number;
  arquetipo_id: string;
  avance: { decididos: number; total: number };
}

export interface EventoFin {
  segundos: number;
  modo: string;
  llamadas_api?: number;
  gasto_usd?: number;
  cache_aciertos?: number;
  cache_fallos?: number;
}

export type Fase = "carga" | "menu" | "politica" | "simulacion";
export type Conexion = "inactiva" | "conectando" | "corriendo" | "terminada" | "error";

interface Almacen {
  fase: Fase;
  aumentoPct: number;
  poblacion: Poblacion | null;
  conexion: Conexion;
  error: string | null;
  rondas: EventoRonda[];
  decisiones: EventoDecision[];
  // contador monotónico para que la escena detecte decisiones nuevas sin
  // recorrer el arreglo entero cada frame
  nDecisiones: number;
  avance: { ronda: number; decididos: number; total: number };
  fin: EventoFin | null;
  hover: string | null;
  // personas por punto del nivel de zoom actual (LOD)
  personasPorPunto: number;

  setFase: (f: Fase) => void;
  setAumentoPct: (v: number) => void;
  setPoblacion: (p: Poblacion) => void;
  setConexion: (c: Conexion, error?: string | null) => void;
  agregarRonda: (r: EventoRonda) => void;
  agregarDecision: (d: EventoDecision) => void;
  setFin: (f: EventoFin) => void;
  setHover: (id: string | null) => void;
  setPersonasPorPunto: (n: number) => void;
  reiniciarCorrida: () => void;
}

export const usarAlmacen = create<Almacen>((set) => ({
  fase: "carga",
  aumentoPct: 23,
  poblacion: null,
  conexion: "inactiva",
  error: null,
  rondas: [],
  decisiones: [],
  nDecisiones: 0,
  avance: { ronda: 0, decididos: 0, total: 0 },
  fin: null,
  hover: null,
  personasPorPunto: 8000,

  setFase: (fase) => set({ fase }),
  setAumentoPct: (aumentoPct) => set({ aumentoPct }),
  setPoblacion: (poblacion) => set({ poblacion }),
  setConexion: (conexion, error = null) => set({ conexion, error }),
  agregarRonda: (r) => set((s) => ({ rondas: [...s.rondas, r] })),
  agregarDecision: (d) =>
    set((s) => ({
      decisiones: [...s.decisiones, d],
      nDecisiones: s.nDecisiones + 1,
      avance: { ronda: d.ronda, decididos: d.avance.decididos, total: d.avance.total },
    })),
  setFin: (fin) => set({ fin, conexion: "terminada" }),
  setHover: (hover) => set({ hover }),
  setPersonasPorPunto: (personasPorPunto) => set({ personasPorPunto }),
  reiniciarCorrida: () =>
    set({
      conexion: "inactiva",
      error: null,
      rondas: [],
      decisiones: [],
      nDecisiones: 0,
      avance: { ronda: 0, decididos: 0, total: 0 },
      fin: null,
      hover: null,
    }),
}));

// La última ronda cerrada (o null antes de la ronda 0).
export function ultimaRonda(s: { rondas: EventoRonda[] }): EventoRonda | null {
  return s.rondas.length ? s.rondas[s.rondas.length - 1] : null;
}

// Depuración desde la consola del navegador (y verificación automatizada).
if (typeof window !== "undefined") {
  (window as unknown as { __almacen?: typeof usarAlmacen }).__almacen = usarAlmacen;
}
