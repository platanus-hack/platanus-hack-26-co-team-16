"use client";

// La barra de tiempo, con la unidad REAL del motor: 1 ronda = 1 trimestre
// (ADR 0005), la ronda 0 es la proyección oficial y el horizonte son 9 meses.
// Durante una ronda LLM el segmento activo se llena con el avance real
// (celdas decididas / total).

import { usarAlmacen } from "@/estado/simulacion";

export default function BarraTiempo() {
  const rondas = usarAlmacen((s) => s.rondas);
  const avance = usarAlmacen((s) => s.avance);
  const conexion = usarAlmacen((s) => s.conexion);
  const fin = usarAlmacen((s) => s.fin);
  const poblacion = usarAlmacen((s) => s.poblacion);

  const total = poblacion?.rondas_totales ?? 4;
  const cerrada = rondas.length ? rondas[rondas.length - 1].contrato.ronda : -1;
  const etiquetas = ["R0 · proyección", "T1", "T2", "T3", "T4", "T5"].slice(0, total);

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
          : "1 ronda = 1 trimestre · horizonte 9 meses · la ronda 0 es la proyección oficial"}
      </div>
    </div>
  );
}
