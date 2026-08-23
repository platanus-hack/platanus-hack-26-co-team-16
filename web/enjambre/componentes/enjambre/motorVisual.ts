// El motor visual: el estado interpolado que la escena dibuja a 60 fps.
// React no re-renderiza por frame; esto se actualiza imperativamente en un
// useFrame y las mallas leen de acá. Todo lo que interpola parte de datos
// reales del flujo (estado_por_arquetipo de cada ronda) — la interpolación es
// puramente estética, entre dos estados que el motor sí calculó.

import { Celda, disponer } from "@/lib/disposicion";
import { EstadoCelda, Poblacion, usarAlmacen } from "@/estado/simulacion";

export interface Pulso {
  id: string;
  edad: number; // segundos desde la decisión
  familia: string | null;
  vetadas: number;
}

const DURACION_TRANSICION = 2.4; // s por ronda: el enjambre respira, no salta
const DURACION_PULSO = 1.9;

function atenuar(t: number): number {
  // easeInOutCubic
  return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
}

export class MotorVisual {
  celdas: Map<string, Celda>;
  orden: string[];
  poblacion: Poblacion;

  /** estado interpolado que dibuja la escena */
  actual = new Map<string, EstadoCelda>();
  private previo = new Map<string, EstadoCelda>();
  private objetivo = new Map<string, EstadoCelda>();
  private t = 1;
  private rondasVistas = 0;

  /** progreso de nacimiento 0..1 por celda (pop escalonado tipo palomitas) */
  nacimiento = new Map<string, number>();
  private reloj = 0;

  /** pulsos activos por decisiones recién llegadas */
  pulsos: Pulso[] = [];
  private decisionesVistas = 0;
  /** última familia decidida por celda (colorea el pulso y el hover) */
  familias = new Map<string, string>();
  /** celdas que ya decidieron en la ronda en curso */
  decididas = new Set<string>();
  rondaEnCurso = 0;

  constructor(poblacion: Poblacion, seed = 20260322) {
    this.poblacion = poblacion;
    this.celdas = disponer(poblacion.arquetipos, seed);
    this.orden = [...this.celdas.keys()];
    for (const a of poblacion.arquetipos) {
      const e: EstadoCelda = {
        fraccion_informal: a.fraccion_informal_inicial,
        fraccion_empleada: 1,
        horas: 1,
      };
      this.actual.set(a.id, { ...e });
      this.previo.set(a.id, { ...e });
      this.objetivo.set(a.id, { ...e });
      this.nacimiento.set(a.id, 0);
    }
  }

  actualizar(dt: number): void {
    const st = usarAlmacen.getState();
    this.reloj += dt;

    // nacimiento escalonado: cada celda revienta con su propio retardo
    for (const c of this.celdas.values()) {
      const retardo = 0.15 + (c.indice / this.celdas.size) * 2.2;
      const prog = Math.min(1, Math.max(0, (this.reloj - retardo) / 0.55));
      this.nacimiento.set(c.id, prog);
    }

    // ¿llegó una ronda nueva? → nuevo objetivo, transición desde el estado visible
    if (st.rondas.length > this.rondasVistas) {
      const r = st.rondas[st.rondas.length - 1];
      this.rondasVistas = st.rondas.length;
      for (const id of this.orden) {
        this.previo.set(id, { ...this.actual.get(id)! });
        const e = r.estado_por_arquetipo[id];
        if (e) this.objetivo.set(id, { ...e });
      }
      this.t = r.contrato.ronda === 0 ? 1 : 0; // la ronda 0 es el punto de partida, sin viaje
      this.rondaEnCurso = r.contrato.ronda + 1;
      this.decididas.clear();
    }

    if (this.t < 1) {
      this.t = Math.min(1, this.t + dt / DURACION_TRANSICION);
      const k = atenuar(this.t);
      for (const id of this.orden) {
        const p = this.previo.get(id)!;
        const o = this.objetivo.get(id)!;
        this.actual.set(id, {
          fraccion_informal: p.fraccion_informal + (o.fraccion_informal - p.fraccion_informal) * k,
          fraccion_empleada: p.fraccion_empleada + (o.fraccion_empleada - p.fraccion_empleada) * k,
          horas: p.horas + (o.horas - p.horas) * k,
        });
      }
    }

    // decisiones nuevas → pulso + registro
    if (st.decisiones.length > this.decisionesVistas) {
      for (let i = this.decisionesVistas; i < st.decisiones.length; i++) {
        const d = st.decisiones[i];
        this.pulsos.push({ id: d.arquetipo_id, edad: 0, familia: d.dominante, vetadas: d.vetadas });
        if (d.dominante) this.familias.set(d.arquetipo_id, d.dominante);
        this.decididas.add(d.arquetipo_id);
      }
      this.decisionesVistas = st.decisiones.length;
      if (this.pulsos.length > 60) this.pulsos.splice(0, this.pulsos.length - 60);
    }
    for (const p of this.pulsos) p.edad += dt;
    this.pulsos = this.pulsos.filter((p) => p.edad < DURACION_PULSO);
  }
}

export const COLOR_FAMILIA: Record<string, string> = {
  informalizar: "#5b9dff",
  despedir: "#f0544f",
  bajar_horas: "#e8a33d",
  subir_precios: "#e8a33d",
  renegociar: "#e8a33d",
  cumplir: "#3ecf8e",
  absorber: "#3ecf8e",
  otra: "#a7afbe",
};
