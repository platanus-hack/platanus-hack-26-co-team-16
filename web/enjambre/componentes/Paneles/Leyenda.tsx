"use client";

// Cómo leer el enjambre. Incluye el nivel de LOD vivo: cuántas personas
// representa un punto en el zoom actual.

import { miles } from "@/lib/formato";
import { usarAlmacen } from "@/estado/simulacion";

function Ficha({ color, hueco, texto }: { color: string; hueco?: boolean; texto: string }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 7 }}>
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
      <span style={{ fontSize: 12, color: "var(--tinta-suave)" }}>{texto}</span>
    </div>
  );
}

export default function Leyenda() {
  const ppp = usarAlmacen((s) => s.personasPorPunto);

  return (
    <div className="panel" style={{ left: 36, bottom: 30, width: 360, display: "flex", flexDirection: "column", gap: 8 }}>
      <div className="kicker">cómo leer el enjambre</div>
      <div style={{ display: "flex", flexWrap: "wrap", gap: "6px 18px" }}>
        <Ficha color="#dfe3ea" texto="celda empleadora · área = empleo vivo" />
        <Ficha color="#5b9dff" texto="informal (celda o persona)" />
        <Ficha color="#3ecf8e" texto="empleo formal" />
        <Ficha color="#e8a33d" texto="jornada recortada" />
        <Ficha color="#99a2b1" hueco texto="expulsado del empleo" />
        {/* S2-4: la onda (Onda.tsx) es el elemento más grande de la pantalla
            y no traía leyenda — el radio salta de 0 a ~5 apenas la brecha
            cruza 0,04pp, así que se aclara qué mide y por qué aparece de golpe. */}
        <Ficha color="#5b9dff" texto="halo que late = onda de informalización nueva, radio ∝ √brecha ponderada" />
      </div>
      <div style={{ fontFamily: "var(--mono)", fontSize: 10.5, color: "var(--tinta-tenue)" }}>
        1 punto ≈ {miles(ppp)} personas (zoom para subdividir) · celda = grupo sector×tamaño GEIH, no una
        empresa individual · cuenta propia fuera de la grilla
      </div>
    </div>
  );
}
