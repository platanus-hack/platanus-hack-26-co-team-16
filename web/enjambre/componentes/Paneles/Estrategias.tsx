"use client";

// El reparto de estrategias: qué decidieron de verdad los agentes. Es el
// segundo protagonista de la pantalla, después del enjambre.
//
// Se muestran DOS lecturas del mismo dato, y esa es la gracia:
//   · ponderado por población (la barra y la cifra grande) — a cuánta gente
//     le pasa cada cosa
//   · por conteo de celdas (la marca vertical) — a cuántas empresas
// No coinciden, y el desacuerdo es un hallazgo: por conteo suele dominar
// "cumplir" (son muchas celdas chicas) mientras que ponderado domina
// "informalizar" (son pocas celdas, pero enormes). Mostrar solo una de las dos
// deja contar media historia.

import { COLOR_FAMILIA } from "@/componentes/enjambre/motorVisual";
import { nombreEstrategia, pct } from "@/lib/formato";
import { usarAlmacen } from "@/estado/simulacion";

export default function Estrategias() {
  // S2-5: la ronda mostrada, no la última llegada (ver motorVisual.ts).
  const ult = usarAlmacen((s) => s.rondaMostrada);
  if (!ult) return null;

  const entradas = Object.entries(ult.desglose_estrategias)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 6);
  if (!entradas.length) return null;

  const conteo = ult.desglose_estrategias_conteo ?? {};
  const celdasTotal = Object.values(conteo).reduce((s, n) => s + n, 0);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 13 }}>
      <div className="kicker">reparto de estrategias</div>
      {entradas.map(([k, v]) => {
        const n = conteo[k] ?? 0;
        return (
          <div key={k} style={{ display: "flex", alignItems: "center", gap: 14 }}>
            <div style={{ width: 118, flexShrink: 0 }}>
              <div style={{ fontSize: 15, fontWeight: 500, color: "var(--tinta)" }}>
                {nombreEstrategia(k)}
              </div>
              {celdasTotal > 0 && (
                <div style={{ fontFamily: "var(--mono)", fontSize: 10, color: "var(--tinta-tenue)" }}>
                  {n} de {celdasTotal} celdas
                </div>
              )}
            </div>
            <div
              style={{
                flex: 1,
                height: 14,
                background: "rgba(233,236,242,0.07)",
                position: "relative",
              }}
            >
              <div
                style={{
                  position: "absolute",
                  inset: "0 auto 0 0",
                  width: `${Math.min(100, v * 100)}%`,
                  background: COLOR_FAMILIA[k] ?? "var(--tinta-tenue)",
                  opacity: 0.88,
                  transition: "width 1.2s cubic-bezier(.2,.7,.2,1)",
                }}
              />
              {/* dónde caería la barra si contáramos celdas en vez de personas */}
              {celdasTotal > 0 && (
                <div
                  title={`por conteo de celdas: ${pct(n / celdasTotal)}`}
                  style={{
                    position: "absolute",
                    top: -3,
                    bottom: -3,
                    left: `${Math.min(100, (n / celdasTotal) * 100)}%`,
                    width: 2,
                    background: "var(--tinta)",
                    opacity: 0.55,
                    transition: "left 1.2s cubic-bezier(.2,.7,.2,1)",
                  }}
                />
              )}
            </div>
            <div
              className="cifra"
              style={{ width: 86, textAlign: "right", fontSize: 30, lineHeight: 1 }}
            >
              {pct(v)}
            </div>
          </div>
        );
      })}
      <div style={{ fontFamily: "var(--mono)", fontSize: 10, color: "var(--tinta-tenue)" }}>
        barra y cifra = población · marca vertical = conteo de celdas
      </div>
    </div>
  );
}
