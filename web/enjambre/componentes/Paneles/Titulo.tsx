"use client";

// Esquina superior izquierda: qué política corre y en qué ronda va.

import { usarAlmacen } from "@/estado/simulacion";

export default function Titulo() {
  const aumento = usarAlmacen((s) => s.aumentoPct);
  // S2-5: la ronda MOSTRADA, no la última llegada — si no, esto salta por
  // delante del enjambre en cuanto llega más de una ronda de golpe.
  const rondaMostrada = usarAlmacen((s) => s.rondaMostrada);
  const avance = usarAlmacen((s) => s.avance);
  const poblacion = usarAlmacen((s) => s.poblacion);
  const conexion = usarAlmacen((s) => s.conexion);
  const modo = usarAlmacen((s) => s.modo);

  const total = poblacion?.rondas_totales ?? 4;
  const cerrada = rondaMostrada?.contrato.ronda ?? -1;
  const enCurso = conexion === "corriendo" && cerrada < total - 1 ? cerrada + 1 : null;

  return (
    <div className="panel" style={{ left: 36, top: 32, display: "flex", flexDirection: "column", gap: 12 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
        <div className="kicker">simulación de política · mercado laboral de Bogotá</div>
        {modo && (
          <div
            title={
              modo === "reglas"
                ? "ablación determinista: sin LLM, sin costo, sin key"
                : "decisiones vía LLM (ClienteConductual), con caché y tope de presupuesto"
            }
            style={{
              fontFamily: "var(--mono)",
              fontSize: 10,
              letterSpacing: "0.08em",
              padding: "2px 7px",
              borderRadius: 3,
              border: `1px solid ${modo === "reglas" ? "var(--ambar)" : "var(--azul-vivo)"}`,
              color: modo === "reglas" ? "var(--ambar)" : "var(--azul-vivo)",
            }}
          >
            MODO {modo === "reglas" ? "REGLAS (ablación)" : "LLM"}
          </div>
        )}
      </div>
      <div className="cifra" style={{ fontSize: 38, lineHeight: 1.05 }}>
        Alza del salario mínimo
        <br />
        <span style={{ color: "var(--azul-vivo)" }}>+{aumento.toFixed(1).replace(".", ",")} %</span>
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginTop: 2 }}>
        <div style={{ display: "flex", gap: 5 }}>
          {Array.from({ length: total }, (_, i) => {
            let fondo = "rgba(233,236,242,0.12)";
            if (i <= cerrada) fondo = "var(--tinta)";
            if (i === enCurso) fondo = "var(--azul)";
            return (
              <div
                key={i}
                className={i === enCurso ? "latido" : undefined}
                style={{ width: 30, height: 6, background: fondo, transition: "background 0.4s" }}
              />
            );
          })}
        </div>
        <div style={{ fontFamily: "var(--mono)", fontSize: 12, letterSpacing: "0.1em", color: "var(--tinta-tenue)" }}>
          {enCurso !== null
            ? `RONDA ${enCurso} DECIDIENDO · ${avance.decididos}/${avance.total || "—"} CELDAS`
            : cerrada >= 0
              ? `RONDA ${cerrada} DE ${total - 1}`
              : "PREPARANDO"}
        </div>
      </div>
    </div>
  );
}
