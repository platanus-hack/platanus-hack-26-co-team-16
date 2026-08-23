"use client";

// Cómo leer el enjambre, en fichas. Nada de párrafos: las aclaraciones largas
// (qué es una celda, qué queda fuera de la grilla) viven en el reporte, no
// encima del lienzo.
//
// Tamaño: las fichas eran de 8 px con texto de 11,5 y en una demo proyectada no
// se leían. El mapa entero es ilegible sin esta leyenda —el color de cada punto
// ES el dato—, así que ocupa el espacio que necesita para cumplir su función.

import { miles } from "@/lib/formato";
import { usarAlmacen } from "@/estado/simulacion";

function Ficha({ color, hueco, texto }: { color: string; hueco?: boolean; texto: string }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
      <span
        style={{
          width: 12,
          height: 12,
          borderRadius: "50%",
          background: hueco ? "transparent" : color,
          border: hueco ? `2px solid ${color}` : "none",
          display: "inline-block",
          flexShrink: 0,
        }}
      />
      <span style={{ fontSize: 14, color: "var(--tinta)" }}>{texto}</span>
    </div>
  );
}

export default function Leyenda() {
  const ppp = usarAlmacen((s) => s.personasPorPunto);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
      <div style={{ display: "flex", flexWrap: "wrap", gap: "9px 20px" }}>
        <Ficha color="#3ecf8e" texto="formal" />
        <Ficha color="#5b9dff" texto="informal" />
        <Ficha color="#e8a33d" texto="jornada recortada" />
        <Ficha color="#99a2b1" hueco texto="sin empleo" />
      </div>
      <div style={{ fontFamily: "var(--mono)", fontSize: 11.5, color: "var(--tinta-tenue)" }}>
        1 punto ≈ {miles(ppp)} personas · zoom para subdividir
      </div>
    </div>
  );
}
