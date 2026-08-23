"use client";

// El bloque editorial: titular armado con cifras reales de la ronda y cita
// textual de la justificación que el motor produjo para la celda protagonista.
// Medio ficticio, siempre rotulado como tal.

import { useMemo } from "react";
import { titular } from "@/lib/narrativa";
import { rondasVisibles, usarAlmacen } from "@/estado/simulacion";

export default function Noticias() {
  const rondas = usarAlmacen((s) => s.rondas);
  const rondaMostrada = usarAlmacen((s) => s.rondaMostrada);
  // S2-5: el titular es de la ronda que se está viendo, no de la última que
  // llegó por el cable.
  const vis = useMemo(() => rondasVisibles({ rondas, rondaMostrada }), [rondas, rondaMostrada]);
  const nota = useMemo(() => titular(vis), [vis]);
  if (!nota) return null;

  return (
    <div
      key={nota.titulo}
      className="panel aparecer"
      // Contenida a la fuerza: antes crecía con el largo del titular y de la
      // cita del LLM, y a 1440×900 se comía el panel de métricas de abajo. El
      // alto máximo la vuelve predecible; el texto completo va al reporte.
      style={{
        right: 36,
        top: 196,
        width: 360,
        maxHeight: 190,
        overflow: "hidden",
        borderLeft: "2px solid var(--rojo)",
        paddingLeft: 14,
        display: "flex",
        flexDirection: "column",
        gap: 7,
      }}
    >
      <div className="kicker" style={{ color: "var(--rojo)", fontSize: 10 }}>
        {nota.kicker}
      </div>
      <div
        className="cifra"
        style={{
          fontSize: 19,
          lineHeight: 1.2,
          textWrap: "pretty" as never,
          display: "-webkit-box",
          WebkitLineClamp: 3,
          WebkitBoxOrient: "vertical" as never,
          overflow: "hidden",
        }}
      >
        {nota.titulo}
      </div>
      {nota.cita && (
        <div
          style={{
            fontFamily: "var(--serif)",
            fontStyle: "italic",
            fontSize: 13.5,
            lineHeight: 1.4,
            color: "var(--tinta-suave)",
            display: "-webkit-box",
            WebkitLineClamp: 3,
            WebkitBoxOrient: "vertical" as never,
            overflow: "hidden",
          }}
        >
          “{nota.cita}”
        </div>
      )}
    </div>
  );
}
