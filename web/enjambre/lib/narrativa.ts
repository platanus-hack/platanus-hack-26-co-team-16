// La narrativa: quién protagoniza la ronda y qué titular sale de ella.
// Regla dura: ningún número inventado. Los titulares se arman con plantillas
// sobre cifras del flujo, y la cita es la `justificacion` REAL que produjo el
// motor (LLM o regla fija) para la celda protagonista. El medio es ficticio.

import {
  ArquetipoEstatico,
  EventoRonda,
  usarAlmacen,
} from "@/estado/simulacion";
import { miles, nombreSector, pct, pp } from "./formato";

export interface Protagonista {
  id: string;
  justificacion: string | null;
  familia: string | null;
  deltaInformal: number;
  arquetipo: ArquetipoEstatico | null;
  ronda: number;
}

/** La celda que más movió la informalidad (ponderada) en la última ronda. */
export function protagonista(rondas: EventoRonda[]): Protagonista | null {
  if (rondas.length < 2) return null;
  const poblacion = usarAlmacen.getState().poblacion;
  if (!poblacion) return null;
  const ult = rondas[rondas.length - 1];
  const prev = rondas[rondas.length - 2];

  let mejor: Protagonista | null = null;
  let mejorPuntaje = 0;
  for (const a of poblacion.arquetipos) {
    const e1 = ult.estado_por_arquetipo[a.id];
    const e0 = prev.estado_por_arquetipo[a.id];
    if (!e1 || !e0) continue;
    const res = ult.por_arquetipo[a.id];
    const dInf = Math.max(0, e1.fraccion_informal - e0.fraccion_informal);
    const dEmp = Math.max(0, e0.fraccion_empleada - e1.fraccion_empleada);
    // se prefiere quien tenga una justificación que citar
    const puntaje = a.peso * (dInf + dEmp * 0.8) * (res?.justificacion ? 1 : 0.25);
    if (puntaje > mejorPuntaje) {
      mejorPuntaje = puntaje;
      mejor = {
        id: a.id,
        justificacion: res?.justificacion ?? null,
        familia: res?.dominante ?? null,
        deltaInformal: dInf,
        arquetipo: a,
        ronda: ult.contrato.ronda,
      };
    }
  }
  return mejorPuntaje > 0 ? mejor : null;
}

export interface Titular {
  kicker: string;
  titulo: string;
  cita: string | null;
  atribucion: string | null;
}

/** El titular de la última ronda, armado solo con cifras del flujo. */
export function titular(rondas: EventoRonda[]): Titular | null {
  if (rondas.length < 2) return null;
  const ult = rondas[rondas.length - 1];
  const r0 = rondas[0];
  const c = ult.contrato;
  const brecha = (c.tasa_informalidad - r0.contrato.tasa_informalidad) * 100;
  const dominante = Object.keys(ult.desglose_estrategias)[0] ?? null;
  const fracDominante = dominante ? ult.desglose_estrategias[dominante] : 0;

  let titulo: string;
  if (dominante === "informalizar" && fracDominante > 0.25) {
    titulo = `La sombra se traga ${pct(fracDominante)} de la nómina: la informalidad toca ${pct(c.tasa_informalidad)}`;
  } else if (dominante === "despedir" && fracDominante > 0.25) {
    titulo = `Despedir gana como estrategia: el empleo cae a ${pct(c.empleo_relativo)} del punto de partida`;
  } else if (ult.fraccion_jornada_recortada > 0.08) {
    titulo = `Menos horas para no cerrar: ${pct(ult.fraccion_jornada_recortada)} conserva el puesto con jornada recortada`;
  } else if (brecha > 1) {
    titulo = `La proyección oficial se queda corta: ${pp(brecha)} de informalidad que el modelo no vio`;
  } else if ((1 - c.empleo_relativo) > 0.02) {
    titulo = `El costo se paga en puestos: ${pct(1 - c.empleo_relativo)} del empleo ya no está`;
  } else {
    titulo = `El mercado aguanta la ronda ${c.ronda}: informalidad en ${pct(c.tasa_informalidad)} y empleo en ${pct(c.empleo_relativo)}`;
  }

  const prota = protagonista(rondas);
  const a = prota?.arquetipo ?? null;
  return {
    kicker: `El Centinela · medio ficticio · ronda ${c.ronda} · trimestre ${c.ronda}`,
    titulo,
    cita: prota?.justificacion ?? null,
    atribucion: a
      ? `célula ${nombreSector(a.sector)} · ${a.tamano} · representa ${miles(a.peso)} trabajadores — justificación generada por la simulación`
      : null,
  };
}
