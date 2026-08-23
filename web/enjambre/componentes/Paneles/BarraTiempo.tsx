"use client";

// La línea de tiempo explícita (ADR 0005 — "el reloj de la simulación"): sin
// reloj, empleo_relativo es "un número sin unidades". Las etiquetas NO son
// texto fijo: salen de `poblacion.meses_por_ronda`, el mismo campo que viaja
// en el contrato y que antes nadie leía. Si el motor cambia el largo de la
// ronda, esta barra cambia con él, no hay que tocar el front.
// Durante una ronda LLM el segmento activo se llena con el avance real
// (celdas decididas / total).

import { useEffect, useState } from "react";
import { DURACION_INTRO } from "@/componentes/enjambre/motorVisual";
import { usarAlmacen } from "@/estado/simulacion";

export default function BarraTiempo() {
  // S2-5: la ronda mostrada, no la última llegada — si no, esta barra salta
  // directo a "Ronda 3/3" mientras el enjambre todavía anima la 1 (ver
  // motorVisual.ts).
  const rondaMostrada = usarAlmacen((s) => s.rondaMostrada);
  const avance = usarAlmacen((s) => s.avance);
  const decididasMostradas = usarAlmacen((s) => s.decididasMostradas);
  const conexion = usarAlmacen((s) => s.conexion);
  const fin = usarAlmacen((s) => s.fin);
  const poblacion = usarAlmacen((s) => s.poblacion);

  const total = poblacion?.rondas_totales ?? 4;
  const mpr = poblacion?.meses_por_ronda ?? 3;
  const horizonteMeses = (total - 1) * mpr;
  const cerrada = rondaMostrada?.contrato.ronda ?? -1;

  // P2.2: durante la intro no hay "preparando" — este segmento avanza de R0 a
  // T1 mientras la ciudad se construye, y ESA es la pantalla de carga. El
  // reloj es local (no toca el store) para no re-renderizar React a 60 fps.
  const [progresoIntro, setProgresoIntro] = useState(0);
  useEffect(() => {
    if (cerrada >= 0) return;
    const t0 = performance.now();
    const id = setInterval(() => {
      setProgresoIntro(Math.min(1, (performance.now() - t0) / 1000 / DURACION_INTRO));
    }, 100);
    return () => clearInterval(id);
  }, [cerrada]);
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
          else if (i === 0 && cerrada < 0) lleno = progresoIntro;
          else if (i === cerrada + 1 && conexion === "corriendo" && avance.total > 0)
            lleno = decididasMostradas / avance.total;
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
      {/* Solo el cierre de corrida. La explicación del reloj (1 ronda = N
          meses, horizonte, qué es la ronda 0) ya está en las etiquetas de los
          segmentos y se desarrolla en el reporte. */}
      {conexion === "terminada" && fin && (
        <div style={{ fontFamily: "var(--mono)", fontSize: 10, color: "var(--tinta-tenue)", textAlign: "center" }}>
          {`corrida terminada · ${fin.segundos.toFixed(1).replace(".", ",")} s · ${fin.llamadas_api ?? 0} llamadas API · $${(fin.gasto_usd ?? 0).toFixed(2)} USD`}
        </div>
      )}
    </div>
  );
}
