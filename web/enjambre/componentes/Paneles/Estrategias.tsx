"use client";

// Reparto de estrategias de la última ronda, PONDERADO por población (dato A4
// del plan: sin ponderar dice lo contrario). Barras sobrias, color por familia.

import { COLOR_FAMILIA } from "@/componentes/enjambre/motorVisual";
import { nombreEstrategia, pct } from "@/lib/formato";
import { ultimaRonda, usarAlmacen } from "@/estado/simulacion";

export default function Estrategias() {
  const rondas = usarAlmacen((s) => s.rondas);
  const ult = ultimaRonda({ rondas });
  const entradas = ult ? Object.entries(ult.desglose_estrategias).slice(0, 4) : [];
  if (!entradas.length) return null;

  return (
    <div className="panel" style={{ left: 36, bottom: 128, width: 360, display: "flex", flexDirection: "column", gap: 10 }}>
      <div className="kicker">reparto de estrategias · ponderado por población</div>
      {entradas.map(([k, v]) => (
        <div key={k} style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <div style={{ width: 104, fontSize: 13.5, fontWeight: 500, color: "var(--tinta-suave)" }}>
            {nombreEstrategia(k)}
          </div>
          <div style={{ flex: 1, height: 8, background: "rgba(233,236,242,0.07)", position: "relative" }}>
            <div
              style={{
                position: "absolute",
                inset: "0 auto 0 0",
                width: `${Math.min(100, v * 100)}%`,
                background: COLOR_FAMILIA[k] ?? "var(--tinta-tenue)",
                opacity: 0.85,
                transition: "width 1.2s cubic-bezier(.2,.7,.2,1)",
              }}
            />
          </div>
          <div className="cifra" style={{ width: 72, textAlign: "right", fontSize: 20 }}>
            {pct(v)}
          </div>
        </div>
      ))}
    </div>
  );
}
