"use client";

// Pantalla 3: el porcentaje. Un solo número gigante y un slider de 0 a 25.
// Al simular se abre el flujo SSE (la corrida REAL) y se pasa al lienzo.

import { iniciarCorrida } from "@/estado/flujo";
import { usarAlmacen } from "@/estado/simulacion";
import { copMes } from "@/lib/formato";

const MARCAS = [0, 7, 13.6, 23, 25];

export default function ControlPolitica() {
  const aumento = usarAlmacen((s) => s.aumentoPct);
  const setAumento = usarAlmacen((s) => s.setAumentoPct);
  const setFase = usarAlmacen((s) => s.setFase);
  const poblacion = usarAlmacen((s) => s.poblacion);

  const simular = () => {
    iniciarCorrida();
    setFase("simulacion");
  };

  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        gap: 40,
      }}
    >
      <div className="aparecer" style={{ textAlign: "center", display: "flex", flexDirection: "column", gap: 10 }}>
        <div className="kicker">incremento del salario mínimo</div>
        <div className="cifra" style={{ fontSize: 132, color: "var(--azul-vivo)" }}>
          +{aumento.toFixed(1).replace(".", ",")}
          <span style={{ fontSize: 64, color: "var(--tinta-suave)" }}> %</span>
        </div>
        <div style={{ fontFamily: "var(--mono)", fontSize: 12, color: "var(--tinta-tenue)" }}>
          {/* S2-12: antes decía "el decreto de 2026 fue +23,0 %" fijo en el
              texto, sin fuente, mientras `piso_salarial_anterior` ya viaja en
              /api/poblacion y se descartaba. Ahora sale del dato real. */}
          sobre el costo laboral formal por empleado
          {poblacion && ` · piso vigente ${copMes(poblacion.piso_salarial_anterior)}/mes antes del alza`}
        </div>
      </div>

      <div className="aparecer" style={{ width: 480, display: "flex", flexDirection: "column", gap: 14 }}>
        <input
          type="range"
          className="deslizador"
          min={0}
          max={25}
          step={0.5}
          value={aumento}
          style={{ "--progreso": `${(aumento / 25) * 100}%` } as React.CSSProperties}
          onChange={(e) => setAumento(Number(e.target.value))}
        />
        <div style={{ position: "relative", height: 16 }}>
          {MARCAS.map((m) => (
            <button
              key={m}
              onClick={() => setAumento(m)}
              style={{
                position: "absolute",
                left: `${(m / 25) * 100}%`,
                transform: "translateX(-50%)",
                background: "none",
                border: "none",
                cursor: "pointer",
                fontFamily: "var(--mono)",
                fontSize: 11,
                color: Math.abs(m - aumento) < 0.25 ? "var(--azul-vivo)" : "var(--tinta-tenue)",
              }}
            >
              {String(m).replace(".", ",")}
            </button>
          ))}
        </div>
      </div>

      <button className="boton boton--primario aparecer" style={{ padding: "20px 60px" }} onClick={simular}>
        Simular
      </button>
      <button
        onClick={() => setFase("menu")}
        style={{
          background: "none",
          border: "none",
          cursor: "pointer",
          fontFamily: "var(--mono)",
          fontSize: 11,
          letterSpacing: "0.15em",
          color: "var(--tinta-tenue)",
        }}
      >
        ← volver
      </button>
    </div>
  );
}
