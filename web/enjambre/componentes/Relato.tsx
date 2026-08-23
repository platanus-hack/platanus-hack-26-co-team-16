"use client";

// ⚠️ NO SE MONTA. Este componente salió del lienzo en `Simulacion.tsx` (P2) y
// hoy no lo importa nadie: `grep -rn "Relato" web/enjambre` solo devuelve este
// archivo. Se conserva, no se borra, porque el feed de decisiones puede volver
// si aparece una superficie donde quepa leerlo — pero mientras tanto, nada de
// lo que diga acá llega a una pantalla.
//
// Su contenido vive ordenado en `/reporte`, que es donde tiene tamaño para
// leerse. Si vuelve al lienzo, hay que rehacer el reparto de espacio del borde
// izquierdo: hoy esos 330 px son de `ColumnaIzquierda`.

// El reporte que se escribe solo: un feed sobrio con efecto de tecleo que
// narra decisiones (las de más peso) y cierres de ronda, todo desde el flujo
// real. Si las decisiones llegan en ráfaga (modo reglas) la cola se poda para
// no teclear el pasado.

import { useEffect, useRef, useState } from "react";
import { miles, nombreSector, pct } from "@/lib/formato";
import { rondasVisibles, usarAlmacen } from "@/estado/simulacion";

// Qué hizo la celda, en español corriente. `nombreEstrategia` devuelve la
// etiqueta canónica del motor ("informalizar", "bajar_horas"); acá se narra,
// porque el relato lo lee alguien que no conoce el modelo.
const NARRA: Record<string, string> = {
  informalizar: "se pasan a la informalidad",
  despedir: "recortan personal",
  bajar_horas: "recortan la jornada",
  subir_precios: "suben precios",
  renegociar: "renegocian",
  cumplir: "cumplen y pagan el alza",
  absorber: "absorben el costo",
};
const narrar = (k: string) => NARRA[k] ?? k.replace(/_/g, " ");

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
        const veto =
          d.vetadas > 0
            ? ` · el motor les vetó ${d.vetadas} salida${d.vetadas > 1 ? "s" : ""}`
            : "";
        cola.current.push({
          texto: `${nombreSector(a.sector)} ${a.tamano} · ${miles(a.peso)} trabajadores → ${narrar(d.dominante)}${veto}`,
          tono: d.vetadas > 0 ? "veto" : "decision",
        });
      }
      // S2-5: los cierres de ronda salen de las rondas MOSTRADAS. Antes el
      // feed tecleaba "ronda 3 cerrada" mientras el enjambre animaba la 1.
      const vis = rondasVisibles(s);
      while (vistasRondas.current < vis.length) {
        const r = vis[vistasRondas.current++];
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
      {/* S2-6 sigue vigente — que esto es un top-25 podado hay que decirlo —
          pero el sitio donde se dice es el reporte, no un subtítulo de 9,5 px
          encima del lienzo. El kicker lo insinúa; el reporte lo detalla. */}
      <div className="kicker" style={{ marginBottom: 4 }}>
        lo que va pasando · las celdas que más pesan
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
