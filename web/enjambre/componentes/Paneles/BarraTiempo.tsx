"use client";

// La línea de tiempo explícita (ADR 0005 — "el reloj de la simulación"): sin
// reloj, empleo_relativo es "un número sin unidades". Las etiquetas NO son
// texto fijo: salen de `poblacion.meses_por_ronda`, el mismo campo que viaja
// en el contrato y que antes nadie leía. Si el motor cambia el largo de la
// ronda, esta barra cambia con él, no hay que tocar el front.
// Durante una ronda LLM el segmento activo se llena con el avance real
// (celdas decididas / total).

import { usarAlmacen } from "@/estado/simulacion";

export default function BarraTiempo() {
  // S2-5: la ronda mostrada, no la última llegada — si no, esta barra salta
  // directo a "Ronda 3/3" mientras el enjambre todavía anima la 1 (ver
  // motorVisual.ts).
  const rondaMostrada = usarAlmacen((s) => s.rondaMostrada);
  const avance = usarAlmacen((s) => s.avance);
  const conexion = usarAlmacen((s) => s.conexion);
  const fin = usarAlmacen((s) => s.fin);
  const poblacion = usarAlmacen((s) => s.poblacion);

  const total = poblacion?.rondas_totales ?? 4;
  const mpr = poblacion?.meses_por_ronda ?? 3;
  const horizonteMeses = (total - 1) * mpr;
  const cerrada = rondaMostrada?.contrato.ronda ?? -1;
  const etiquetas = Array.from({ length: total }, (_, i) =>
    i === 0 ? "R0 · decreto" : `T${i} · mes +${i * mpr}`
  );

  return (
    <div
      className="panel"
      style={{
        left: "50%",
        bottom: 30,
        transform: "translateX(-50%)",
        width: 460,
        display: "flex",
        flexDirection: "column",
        gap: 8,
      }}
    >
      <div style={{ display: "flex", gap: 6 }}>
        {etiquetas.map((et, i) => {
          let lleno = 0;
          if (i <= cerrada) lleno = 1;
          else if (i === cerrada + 1 && conexion === "corriendo" && avance.total > 0)
            lleno = avance.decididos / avance.total;
          return (
            <div key={i} style={{ flex: 1, display: "flex", flexDirection: "column", gap: 5 }}>
              <div style={{ height: 4, background: "rgba(233,236,242,0.1)", position: "relative" }}>
                <div
                  style={{
                    position: "absolute",
                    inset: "0 auto 0 0",
                    width: `${lleno * 100}%`,
                    background: i <= cerrada ? "var(--tinta)" : "var(--azul)",
                    transition: "width 0.5s",
                  }}
                />
              </div>
              <div
                style={{
                  fontFamily: "var(--mono)",
                  fontSize: 10,
                  letterSpacing: "0.08em",
                  color: i <= cerrada ? "var(--tinta-suave)" : "var(--tinta-tenue)",
                }}
              >
                {et}
              </div>
            </div>
          );
        })}
      </div>
      <div style={{ fontFamily: "var(--mono)", fontSize: 10.5, color: "var(--tinta-tenue)", textAlign: "center" }}>
        {conexion === "terminada" && fin
          ? `corrida terminada · ${fin.segundos.toFixed(1).replace(".", ",")} s · ${fin.llamadas_api ?? 0} llamadas API · $${(fin.gasto_usd ?? 0).toFixed(2)} USD`
          : `1 ronda = ${mpr} meses · horizonte ${horizonteMeses} meses desde el decreto · la ronda 0 es la proyección oficial`}
      </div>
    </div>
  );
}
