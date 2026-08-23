"use client";

// Cómo leer el enjambre, en una línea de fichas. Nada de párrafos: las
// aclaraciones largas (qué es una celda, qué queda fuera de la grilla, qué
// mide la onda) viven en el reporte, no encima del lienzo.

import { miles } from "@/lib/formato";
import { usarAlmacen } from "@/estado/simulacion";

function Ficha({ color, hueco, texto }: { color: string; hueco?: boolean; texto: string }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
      <span
        style={{
          width: 8,
          height: 8,
          borderRadius: "50%",
          background: hueco ? "transparent" : color,
          border: hueco ? `1.5px solid ${color}` : "none",
          display: "inline-block",
          flexShrink: 0,
        }}
      />
      <span style={{ fontSize: 11.5, color: "var(--tinta-suave)" }}>{texto}</span>
    </div>
  );
}

export default function Leyenda() {
  const ppp = usarAlmacen((s) => s.personasPorPunto);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 7 }}>
      <div style={{ display: "flex", flexWrap: "wrap", gap: "5px 16px" }}>
        <Ficha color="#3ecf8e" texto="formal" />
        <Ficha color="#5b9dff" texto="informal" />
        <Ficha color="#e8a33d" texto="jornada recortada" />
        <Ficha color="#99a2b1" hueco texto="sin empleo" />
      </div>
      <div style={{ fontFamily: "var(--mono)", fontSize: 10, color: "var(--tinta-tenue)" }}>
        1 punto ≈ {miles(ppp)} personas · zoom para subdividir
      </div>
    </div>
  );
}
