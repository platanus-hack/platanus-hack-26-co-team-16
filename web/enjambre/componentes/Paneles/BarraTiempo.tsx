"use client";

// La línea de tiempo explícita (ADR 0005 — "el reloj de la simulación"): sin
// reloj, empleo_relativo es "un número sin unidades". Las etiquetas NO son
// texto fijo: salen de `poblacion.meses_por_ronda`, el mismo campo que viaja
// en el contrato y que antes nadie leía. Si el motor cambia el largo de la
// ronda, esta barra cambia con él, no hay que tocar el front.
// Durante una ronda LLM el segmento activo se llena con el avance real
// (celdas decididas / total).
//
// Vive a la derecha, debajo de la cifra de informalidad, y no centrada abajo:
// el reloj y el detalle del periodo son la misma pregunta ("¿en qué momento
// estamos y qué pasó ahí?"), y tenerlos en dos bordes distintos de la pantalla
// obligaba a barrer el lienzo con la vista. Acá abajo también aterrizaron las
// cifras que el hero dejó de mostrar (empleo, sanción, fallback, sin-salida).

import { useEffect, useState } from "react";
import { DURACION_INTRO } from "@/componentes/enjambre/motorVisual";
import { pct } from "@/lib/formato";
import { usarAlmacen } from "@/estado/simulacion";

function Dato({ etiqueta, valor, color }: { etiqueta: string; valor: string; color?: string }) {
  return (
    <div style={{ display: "flex", justifyContent: "space-between", gap: 12 }}>
      <span style={{ fontSize: 12, color: "var(--tinta-suave)" }}>{etiqueta}</span>
      <span style={{ fontFamily: "var(--mono)", fontSize: 12, color: color ?? "var(--tinta)" }}>
        {valor}
      </span>
    </div>
  );
}

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

  const cifras = rondaMostrada?.contrato;

  return (
    <div
      className="panel"
      style={{
        right: 36,
        top: 210,
        width: 340,
        display: "flex",
        flexDirection: "column",
        gap: 10,
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
      {/* El detalle del periodo mostrado. Bajó del hero, donde estas cuatro
          cifras eran números mudos sin rótulo. */}
      {cifras && cifras.ronda >= 0 && (
        <div style={{ display: "flex", flexDirection: "column", gap: 5 }}>
          <Dato etiqueta="empleo que sobrevive" valor={pct(cifras.empleo_relativo)}
                color={cifras.empleo_relativo < 0.98 ? "var(--rojo)" : undefined} />
          <Dato etiqueta="probabilidad de sanción · trimestre"
                valor={pct(cifras.prob_fiscalizacion, 2)} />
          {rondaMostrada!.fraccion_fallback > 0.001 && (
            <Dato etiqueta="sin propuesta viable: cayó al fallback"
                  valor={pct(rondaMostrada!.fraccion_fallback)}
                  color={rondaMostrada!.fraccion_fallback > 0.05 ? "var(--rojo)" : "var(--ambar)"} />
          )}
          {rondaMostrada!.fraccion_sin_salida > 0.001 && (
            <Dato etiqueta="sin ninguna salida factible"
                  valor={pct(rondaMostrada!.fraccion_sin_salida)} color="var(--rojo)" />
          )}
          <div style={{ fontFamily: "var(--mono)", fontSize: 10, color: "var(--tinta-tenue)" }}>
            {`horizonte ${horizonteMeses} meses · 1 periodo = ${mpr} meses`}
          </div>
        </div>
      )}
      {/* Solo el cierre de corrida. La explicación del reloj (1 ronda = N
          meses, horizonte, qué es la ronda 0) ya está en las etiquetas de los
          segmentos y se desarrolla en el reporte. */}
      {conexion === "terminada" && fin && (
        <div style={{ fontFamily: "var(--mono)", fontSize: 10, color: "var(--tinta-tenue)" }}>
          {`corrida terminada · ${fin.segundos.toFixed(1).replace(".", ",")} s · ${fin.llamadas_api ?? 0} llamadas API · $${(fin.gasto_usd ?? 0).toFixed(2)} USD`}
        </div>
      )}
    </div>
  );
}
