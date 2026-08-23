// El motor visual: el estado interpolado que la escena dibuja a 60 fps.
// React no re-renderiza por frame; esto se actualiza imperativamente en un
// useFrame y las mallas leen de acá. Todo lo que interpola parte de datos
// reales del flujo (estado_por_arquetipo de cada ronda) — la interpolación es
// puramente estética, entre dos estados que el motor sí calculó.

import { Celda, disponer } from "@/lib/disposicion";
import { EstadoCelda, EventoDecision, Poblacion, usarAlmacen } from "@/estado/simulacion";

export interface Pulso {
  id: string;
  edad: number; // segundos desde la decisión
  familia: string | null;
  vetadas: number;
}

const DURACION_TRANSICION = 2.4; // s por ronda: el enjambre respira, no salta
const DURACION_PULSO = 1.9;
// P4.1: en cuántos segundos se reproduce la ráfaga de decisiones de una
// ronda, y el piso de decisiones por segundo cuando son pocas.
const VENTANA_DECISIONES = 4.0;
const RITMO_MINIMO_DECISIONES = 6;

// --- La intro (ronda 0) -----------------------------------------------------
// La ronda 0 no llama al LLM: es el escenario sin adaptación, el punto de partida.
// En vez de gastarla en una pantalla de "preparando", se usa para MOSTRAR de
// qué está hecha la ciudad: primero brotan las empresas, y alrededor de cada
// una van apareciendo sus personas de a una. Los ~10 s salen de sumar los
// cuatro tramos de abajo.
const INTRO_RETARDO = 0.3; // s antes de que aparezca la primera empresa
const INTRO_EMPRESAS = 5.6; // s repartiendo la aparición de las 81 celdas
const INTRO_POP_EMPRESA = 0.55; // s que tarda UNA empresa en reventar
const INTRO_PERSONAS = 3.4; // s repartiendo las personas dentro de su empresa
const INTRO_POP_PERSONA = 0.45; // s que tarda UNA persona en aparecer
export const DURACION_INTRO =
  INTRO_RETARDO + INTRO_EMPRESAS + INTRO_POP_EMPRESA + INTRO_PERSONAS + INTRO_POP_PERSONA;

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
  /** cuándo empieza a nacer cada celda, en segundos desde el arranque */
  private retardoCelda = new Map<string, number>();
  reloj = 0;

  /** true mientras corre la intro de la ronda 0 */
  get enIntro(): boolean {
    return this.reloj < DURACION_INTRO;
  }
  /** 0..1, cuánto lleva la intro — lo lee la barra de tiempo */
  get progresoIntro(): number {
    return Math.min(1, this.reloj / DURACION_INTRO);
  }

  /**
   * Progreso de aparición de UNA persona (0..1). Las personas de una celda no
   * aparecen todas con su celda: brotan de a una alrededor de ella, en el
   * orden en que se construyeron. `orden` es i/n dentro de la celda.
   */
  nacimientoPersona(celdaId: string, orden: number): number {
    const base = this.retardoCelda.get(celdaId) ?? 0;
    const inicio = base + INTRO_POP_EMPRESA * 0.6 + orden * INTRO_PERSONAS;
    return Math.min(1, Math.max(0, (this.reloj - inicio) / INTRO_POP_PERSONA));
  }

  /**
   * P4.2 · reposo vivo. Desplazamiento continuo y sutil de una celda respecto
   * de su posición nominal, para que nada quede nunca perfectamente quieto.
   *
   * Son dos senos incoherentes por eje (periodos primos entre sí, ~27 s y
   * ~15 s) desfasados por el índice de la celda: no se repite a simple vista,
   * no cuesta nada, y no necesita ninguna librería de ruido. La amplitud
   * (~0,7 unidades de mundo) está muy por debajo del radio de una celda, así
   * que es vida, no movimiento: ninguna celda se va de su barrio ni se puede
   * confundir con un dato.
   */
  derivaX(indice: number): number {
    const t = this.reloj;
    return Math.sin(t * 0.23 + indice * 1.7) * 0.48 + Math.sin(t * 0.41 + indice * 0.9) * 0.22;
  }
  derivaY(indice: number): number {
    const t = this.reloj;
    return Math.cos(t * 0.19 + indice * 2.3) * 0.44 + Math.cos(t * 0.37 + indice * 1.3) * 0.2;
  }

  /** pulsos activos por decisiones recién llegadas */
  pulsos: Pulso[] = [];
  private decisionesVistas = 0;
  /** decisiones que llegaron y todavía no se muestran (P4.1) */
  private colaDecisiones: EventoDecision[] = [];
  private deudaDecisiones = 0;
  private ultimoAvancePublicado = -1;
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
    // El orden de aparición es el de `disponer()`, que ordena por peso
    // descendente: primero brotan las celdas grandes y después las chicas, así
    // que la ciudad se construye de adentro hacia afuera.
    for (const c of this.celdas.values()) {
      this.retardoCelda.set(c.id, INTRO_RETARDO + (c.indice / this.celdas.size) * INTRO_EMPRESAS);
    }
  }

  actualizar(dt: number): void {
    const st = usarAlmacen.getState();
    this.reloj += dt;

    // nacimiento escalonado: cada celda revienta con su propio retardo
    for (const c of this.celdas.values()) {
      const retardo = this.retardoCelda.get(c.id) ?? 0;
      const prog = Math.min(1, Math.max(0, (this.reloj - retardo) / INTRO_POP_EMPRESA));
      this.nacimiento.set(c.id, prog);
    }

    // S2-5: cola de rondas, una a la vez. `st.rondas` puede recibir varias de
    // golpe en la misma ráfaga (caché caliente); antes esto tomaba siempre
    // rondas[length-1] y descartaba las intermedias, así que la pantalla
    // saltaba directo de "preparando" a la última ronda. Ahora solo se saca
    // la siguiente ronda pendiente de la cola, y solo cuando la transición
    // anterior ya terminó (this.t >= 1) — se consume una cada
    // DURACION_TRANSICION, nunca se salta por delante.
    //
    // P1: además, no se toma la ronda siguiente si el usuario no la pidió.
    // La API no sabe pausar — su hilo empuja eventos a una cola sin esperar a
    // nadie — así que la pausa vive acá: el motor ya tiene toda la corrida en
    // memoria y decide a qué ritmo la reproduce. La ronda 0 tampoco se toma
    // hasta que la intro termina de construir la ciudad.
    const listoParaOtra = !st.pausado && (this.rondasVistas > 0 || !this.enIntro);
    if (this.t >= 1 && listoParaOtra && st.rondas.length > this.rondasVistas) {
      const r = st.rondas[this.rondasVistas];
      this.rondasVistas += 1;
      for (const id of this.orden) {
        this.previo.set(id, { ...this.actual.get(id)! });
        const e = r.estado_por_arquetipo[id];
        if (e) this.objetivo.set(id, { ...e });
      }
      this.t = r.contrato.ronda === 0 ? 1 : 0; // la ronda 0 es el punto de partida, sin viaje
      this.rondaEnCurso = r.contrato.ronda + 1;
      this.decididas.clear();
      this.ultimoAvancePublicado = -1;
      st.setDecididasMostradas(0);
      // publica cuál ronda se está mostrando para que los paneles de texto
      // (Titulo, Hero, Metricas, Estrategias, BarraTiempo) avancen en el
      // mismo ritmo que el enjambre, en vez de leer la última llegada.
      st.setRondaMostrada(r);
      // la ronda 0 no viaja, así que su "transición" termina en el acto y hay
      // que marcar la pausa desde acá; las demás la marcan al llegar t=1.
      if (this.t >= 1) this.cerrarRonda(r.contrato.ronda);
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
      if (this.t >= 1) this.cerrarRonda(this.rondaEnCurso - 1);
    }

    // P4.1: las decisiones nuevas entran a una COLA, no a la pantalla.
    //
    // El motor resuelve una ronda entera con un pool de 8 hilos y el servidor
    // las empuja a la cola SSE en cuanto terminan, así que en modo reglas (o
    // con caché caliente) las ~81 decisiones llegan prácticamente juntas.
    // Aplicarlas todas en un frame es lo que hace que la simulación se vea
    // muerta: no hay proceso, hay un salto entre dos estados.
    if (st.decisiones.length > this.decisionesVistas) {
      for (let i = this.decisionesVistas; i < st.decisiones.length; i++) {
        this.colaDecisiones.push(st.decisiones[i]);
      }
      this.decisionesVistas = st.decisiones.length;
    }

    // ...y se van soltando de a poco. El ritmo se adapta al tamaño de la cola
    // para que una ráfaga entera termine de reproducirse en VENTANA_DECISIONES
    // segundos, sin acelerarse tanto que se vuelva un parpadeo.
    if (this.colaDecisiones.length && !st.pausado) {
      const ritmo = Math.max(
        RITMO_MINIMO_DECISIONES,
        this.colaDecisiones.length / VENTANA_DECISIONES
      );
      this.deudaDecisiones += ritmo * dt;
      let cuantas = Math.floor(this.deudaDecisiones);
      this.deudaDecisiones -= cuantas;
      while (cuantas-- > 0 && this.colaDecisiones.length) {
        const d = this.colaDecisiones.shift()!;
        this.pulsos.push({ id: d.arquetipo_id, edad: 0, familia: d.dominante, vetadas: d.vetadas });
        if (d.dominante) this.familias.set(d.arquetipo_id, d.dominante);
        this.decididas.add(d.arquetipo_id);
      }
      if (this.pulsos.length > 60) this.pulsos.splice(0, this.pulsos.length - 60);
      // el contador de la interfaz sigue al reproductor, no al cálculo: se
      // escribe solo cuando cambia el entero, no 60 veces por segundo.
      if (this.decididas.size !== this.ultimoAvancePublicado) {
        this.ultimoAvancePublicado = this.decididas.size;
        st.setDecididasMostradas(this.decididas.size);
      }
    }

    for (const p of this.pulsos) p.edad += dt;
    this.pulsos = this.pulsos.filter((p) => p.edad < DURACION_PULSO);
  }

  /**
   * Terminó de animarse una ronda. Si quedan rondas por delante, se pausa: la
   * simulación no avanza sola, avanza cuando el usuario lo pide. Es el punto
   * donde la corrida deja de ser una caja negra que se reproduce entera.
   */
  private cerrarRonda(ronda: number): void {
    // Se relee el estado en vez de usar el snapshot del inicio del frame: en
    // la ronda 0 `setRondaMostrada` acaba de correr y el snapshot ya está
    // viejo. Y la ronda llega por parámetro, no del store, por lo mismo.
    const st = usarAlmacen.getState();
    const ultima = (st.poblacion?.rondas_totales ?? 4) - 1;
    if (ronda < ultima) st.setPausado(true);
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
