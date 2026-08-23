"use client";

// El reporte que se escribe solo: un feed sobrio con efecto de tecleo que
// narra decisiones (las de más peso) y cierres de ronda, todo desde el flujo
// real. Si las decisiones llegan en ráfaga (modo reglas) la cola se poda para
// no teclear el pasado.

import { useEffect, useRef, useState } from "react";
import { nombreEstrategia, nombreSector, pct } from "@/lib/formato";
import { usarAlmacen } from "@/estado/simulacion";

interface Linea {
  texto: string;
  tono: "decision" | "ronda" | "veto";
}

const MAX_VISIBLES = 9;

export default function Relato() {
  const [visibles, setVisibles] = useState<Linea[]>([]);
  const [parcial, setParcial] = useState("");
  const cola = useRef<Linea[]>([]);
  const escribiendo = useRef<Linea | null>(null);
  const vistasDecisiones = useRef(0);
  const vistasRondas = useRef(0);

  // recolectar líneas nuevas del almacén
  useEffect(() => {
    const anular = usarAlmacen.subscribe((s) => {
      const poblacion = s.poblacion;
      if (!poblacion) return;
      // SUPUESTO: top-25 celdas por peso como corte de "lo que mueve el
      // agregado" — un umbral editorial para que el relato quepa, no un
      // resultado del motor. Ver también el subtítulo en el panel (S2-6).
      const pesoGrande =
        [...poblacion.arquetipos].sort((a, b) => b.peso - a.peso)[Math.min(24, poblacion.arquetipos.length - 1)]
          ?.peso ?? 0;

      while (vistasDecisiones.current < s.decisiones.length) {
        const d = s.decisiones[vistasDecisiones.current++];
        const a = poblacion.arquetipos.find((x) => x.id === d.arquetipo_id);
        if (!a || !d.dominante) continue;
        if (a.peso < pesoGrande) continue; // solo las celdas que mueven el agregado
        const veto = d.vetadas > 0 ? ` · ${d.vetadas} propuesta${d.vetadas > 1 ? "s" : ""} vetada` : "";
        cola.current.push({
          texto: `${nombreSector(a.sector)} ${a.tamano} → ${nombreEstrategia(d.dominante)}${veto}`,
          tono: d.vetadas > 0 ? "veto" : "decision",
        });
      }
      while (vistasRondas.current < s.rondas.length) {
        const r = s.rondas[vistasRondas.current++];
        const c = r.contrato;
        cola.current.push({
          texto:
            c.ronda === 0
              ? `ronda 0 · proyección oficial: informalidad ${pct(c.tasa_informalidad)}, empleo pleno asumido`
              : `— ronda ${c.ronda} cerrada · informalidad ${pct(c.tasa_informalidad)} · empleo ${pct(c.empleo_relativo)} —`,
          tono: "ronda",
        });
      }
      // poda: si el flujo va más rápido que el tecleo, se queda lo último.
      // SUPUESTO: el umbral (7) y cuántas decisiones sobreviven la poda (4)
      // son ritmo de lectura elegido a ojo, no una regla del motor.
      if (cola.current.length > 7) {
        const rondasEnCola = cola.current.filter((l) => l.tono === "ronda");
        cola.current = [...rondasEnCola, ...cola.current.filter((l) => l.tono !== "ronda").slice(-4)];
      }
    });
    return anular;
  }, []);

  // el tecleo — todo el estado mutable vive en refs; los setState solo publican
  const largo = useRef(0);
  useEffect(() => {
    const timer = setInterval(() => {
      if (!escribiendo.current) {
        const sig = cola.current.shift();
        if (!sig) return;
        escribiendo.current = sig;
        largo.current = 0;
        setParcial("");
        return;
      }
      const objetivo = escribiendo.current.texto;
      largo.current += 2;
      if (largo.current >= objetivo.length) {
        const hecha = escribiendo.current;
        escribiendo.current = null;
        largo.current = 0;
        setVisibles((v) => [...v.slice(-(MAX_VISIBLES - 1)), hecha]);
        setParcial("");
      } else {
        setParcial(objetivo.slice(0, largo.current));
      }
    }, 28);
    return () => clearInterval(timer);
  }, []);

  const color = (t: Linea["tono"]) =>
    t === "ronda" ? "var(--tinta-suave)" : t === "veto" ? "var(--rojo)" : "var(--tinta-tenue)";

  const enCurso = escribiendo.current;
  if (!visibles.length && !enCurso) return null;

  return (
    <div
      className="panel"
      style={{
        left: 36,
        top: 220,
        width: 330,
        display: "flex",
        flexDirection: "column",
        gap: 5,
        fontFamily: "var(--mono)",
        fontSize: 11,
        lineHeight: 1.5,
      }}
    >
      <div className="kicker" style={{ marginBottom: 0 }}>
        relato de la corrida
      </div>
      {/* S2-6: es un subconjunto filtrado (top-25 celdas por peso, ver
          `pesoGrande` arriba) y podado si el flujo va más rápido que el
          tecleo — dicho, no implícito. */}
      <div style={{ color: "var(--tinta-tenue)", fontSize: 9.5, marginBottom: 4 }}>
        top-25 celdas por peso · se poda si el flujo va más rápido que el tecleo
      </div>
      {visibles.map((l, i) => (
        <div key={i} style={{ color: color(l.tono), opacity: 0.45 + (i / visibles.length) * 0.55 }}>
          {l.texto}
        </div>
      ))}
      {enCurso && (
        <div style={{ color: color(enCurso.tono) }}>
          {parcial}
          <span style={{ animation: "cursor-tecleo 1s step-end infinite" }}>▌</span>
        </div>
      )}
    </div>
  );
}
