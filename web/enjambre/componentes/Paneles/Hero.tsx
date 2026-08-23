"use client";

// Esquina superior derecha: LA cifra — informalidad, de la observada a la de
// la corrida, con su banda y su etiqueta de tipo (regla del repo: ningún
// número sin banda).

import { pct, pp } from "@/lib/formato";
import { ultimaRonda, usarAlmacen } from "@/estado/simulacion";

export default function Hero() {
  const rondas = usarAlmacen((s) => s.rondas);
  const ult = ultimaRonda({ rondas });
  if (!ult) return null;

  const inicial = rondas[0].contrato.tasa_informalidad;
  const actual = ult.contrato.tasa_informalidad;
  const banda = ult.contrato.banda;
  const delta = (actual - inicial) * 100;
  const movida = delta > 0.05;

  return (
    <div className="panel" style={{ right: 36, top: 32, textAlign: "right", display: "flex", flexDirection: "column", gap: 6 }}>
      <div className="kicker">informalidad</div>
      <div style={{ display: "flex", alignItems: "baseline", gap: 14, justifyContent: "flex-end" }}>
        {movida && (
          <>
            <span
              className="cifra"
              style={{ fontSize: 34, color: "var(--tinta-tenue)", textDecoration: "line-through", textDecorationThickness: 1 }}
            >
              {pct(inicial)}
            </span>
            <span style={{ fontSize: 24, color: "var(--tinta-tenue)" }}>→</span>
          </>
        )}
        <span
          className="cifra"
          style={{
            fontSize: 64,
            color: movida ? "var(--azul-vivo)" : "var(--tinta)",
            transition: "color 0.6s",
          }}
        >
          {pct(actual)}
        </span>
      </div>
      <div style={{ fontFamily: "var(--mono)", fontSize: 12, color: "var(--tinta-tenue)" }}>
        {pp(delta)} sobre la proyección oficial
        {!ult.contrato.estabilizada && ult.contrato.ronda > 0 && (
          <span style={{ color: "var(--ambar)" }}> · no estabilizada</span>
        )}
      </div>
      <div style={{ fontFamily: "var(--mono)", fontSize: 11, color: "var(--tinta-tenue)" }}>
        {banda.degenerada
          ? "banda degenerada: una sola trayectoria"
          : `banda ${pct(banda.p10)} – ${pct(banda.p90)} · ${banda.tipo ?? "intra_ronda"}`}
      </div>
    </div>
  );
}
