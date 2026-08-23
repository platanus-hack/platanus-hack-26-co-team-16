"use client";

// El bloque editorial: titular armado con cifras reales de la ronda y cita
// textual de la justificación que el motor produjo para la celda protagonista.
// Medio ficticio, siempre rotulado como tal.

import { useMemo } from "react";
import { titular } from "@/lib/narrativa";
import { usarAlmacen } from "@/estado/simulacion";

export default function Noticias() {
  const rondas = usarAlmacen((s) => s.rondas);
  const nota = useMemo(() => titular(rondas), [rondas]);
  if (!nota) return null;

  return (
    <div
      key={nota.titulo}
      className="panel aparecer"
      style={{
        right: 36,
        top: 208,
        width: 380,
        borderLeft: "2px solid var(--rojo)",
        paddingLeft: 18,
        display: "flex",
        flexDirection: "column",
        gap: 10,
      }}
    >
      <div className="kicker" style={{ color: "var(--rojo)" }}>
        {nota.kicker}
      </div>
      <div className="cifra" style={{ fontSize: 24, lineHeight: 1.22, textWrap: "pretty" as never }}>
        {nota.titulo}
      </div>
      {nota.cita && (
        <div
          style={{
            fontFamily: "var(--serif)",
            fontStyle: "italic",
            fontSize: 15.5,
            lineHeight: 1.45,
            color: "var(--tinta-suave)",
          }}
        >
          “{nota.cita}”
        </div>
      )}
      {nota.atribucion && (
        <div style={{ fontFamily: "var(--mono)", fontSize: 10.5, color: "var(--tinta-tenue)", lineHeight: 1.5 }}>
          {nota.atribucion}
        </div>
      )}
    </div>
  );
}
