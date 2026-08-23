// El cliente del flujo SSE: abre la corrida real contra la API y va vertiendo
// los eventos en el almacén. También imprime el debug por ronda en la consola
// del navegador, espejo de los prints del servidor, para poder verificar que lo
// que se ve es lo que el motor calculó.

import {
  EventoDecision,
  EventoFin,
  EventoRonda,
  Poblacion,
  usarAlmacen,
} from "./simulacion";

export async function cargarPoblacion(): Promise<Poblacion> {
  const r = await fetch("/api/poblacion");
  if (!r.ok) throw new Error(`GET /api/poblacion respondió ${r.status}`);
  const p = (await r.json()) as Poblacion;
  usarAlmacen.getState().setPoblacion(p);
  console.info(
    `[enjambre] grilla: ${p.arquetipos.length} celdas empleadoras · ` +
      `${Math.round(p.peso_total).toLocaleString("es-CO")} trabajadores expandidos · ` +
      `informalidad observada ${(p.tasa_informalidad_observada * 100).toFixed(1)}%`
  );
  return p;
}

let fuente: EventSource | null = null;

export function iniciarCorrida(): void {
  const s = usarAlmacen.getState();
  detenerCorrida();
  s.reiniciarCorrida();
  s.setConexion("conectando");

  const q = new URLSearchParams({ aumento_pct: String(s.aumentoPct), seed: "42" });
  // Escape de desarrollo: abrir la página con ?modo=reglas corre la ablación
  // determinista ($0, sin key). El producto usa el modo LLM por defecto.
  const modo = new URLSearchParams(window.location.search).get("modo");
  if (modo === "reglas") q.set("modo", "reglas");
  fuente = new EventSource(`/api/simulaciones/flujo?${q}`);

  fuente.addEventListener("inicio", (e) => {
    usarAlmacen.getState().setConexion("corriendo");
    console.info("[enjambre] corrida iniciada:", JSON.parse((e as MessageEvent).data));
  });

  fuente.addEventListener("decision", (e) => {
    const d = JSON.parse((e as MessageEvent).data) as EventoDecision;
    usarAlmacen.getState().agregarDecision(d);
  });

  fuente.addEventListener("ronda", (e) => {
    const r = JSON.parse((e as MessageEvent).data) as EventoRonda;
    usarAlmacen.getState().agregarRonda(r);
    const c = r.contrato;
    console.info(
      `[enjambre] ronda ${c.ronda}: informalidad ${(c.tasa_informalidad * 100).toFixed(1)}% · ` +
        `p(sanción) ${(c.prob_fiscalizacion * 100).toFixed(2)}% · ` +
        `empleo ${(c.empleo_relativo * 100).toFixed(1)}% · ` +
        `masa salarial ${r.masa_salarial_relativa}`,
      { estrategias: r.desglose_estrategias, banda: c.banda }
    );
    console.table(
      Object.fromEntries(
        Object.entries(r.estado_por_arquetipo)
          .slice(0, 8)
          .map(([id, e2]) => [id, e2])
      )
    );
  });

  fuente.addEventListener("fin", (e) => {
    const f = JSON.parse((e as MessageEvent).data) as EventoFin;
    usarAlmacen.getState().setFin(f);
    console.info("[enjambre] corrida terminada:", f);
    detenerCorrida();
  });

  fuente.addEventListener("error", (e) => {
    const datos = (e as MessageEvent).data;
    if (datos) {
      const { mensaje } = JSON.parse(datos);
      usarAlmacen.getState().setConexion("error", mensaje);
      console.warn("[enjambre] la corrida murió:", mensaje);
      detenerCorrida();
    } else if (fuente && fuente.readyState === EventSource.CLOSED) {
      const st = usarAlmacen.getState();
      if (st.conexion === "corriendo" || st.conexion === "conectando") {
        st.setConexion("error", "se perdió la conexión con la API (¿uvicorn corriendo en :8000?)");
      }
      detenerCorrida();
    }
    // readyState CONNECTING: EventSource reintenta solo; se deja.
  });
}

export function detenerCorrida(): void {
  if (fuente) {
    fuente.close();
    fuente = null;
  }
}
