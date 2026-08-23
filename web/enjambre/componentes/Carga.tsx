"use client";

// Pantalla 1: el logo (placeholder tipográfico — el logo aún no existe) y una
// barra de carga. Espera el GET /poblacion, que es lo único que la
// simulación necesita precargar. Sin porcentaje inventado (S2-11): barrido
// indeterminado mientras espera, 100% real solo cuando la respuesta llegó.

import { useEffect, useState } from "react";
import { cargarPoblacion } from "@/estado/flujo";
import { usarAlmacen } from "@/estado/simulacion";

export default function Carga() {
  const setFase = usarAlmacen((s) => s.setFase);
  // S2-11: nada de porcentaje inventado. GET /api/poblacion es un solo
  // fetch sin eventos de progreso reales, así que mientras espera se muestra
  // un barrido indeterminado (no afirma "vamos en 82%" sin medirlo) y la
  // barra solo llega a 100% cuando la respuesta real llegó.
  const [listo, setListo] = useState(false);
  const [falla, setFalla] = useState<string | null>(null);

  useEffect(() => {
    let vivo = true;
    cargarPoblacion()
      .then(() => {
        if (!vivo) return;
        setListo(true);
        setTimeout(() => vivo && setFase("menu"), 650);
      })
      .catch((e) => vivo && setFalla(String(e?.message ?? e)));
    return () => {
      vivo = false;
    };
  }, [setFase]);

  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        gap: 34,
      }}
    >
      <div className="aparecer" style={{ textAlign: "center" }}>
        <div
          style={{
            fontFamily: "var(--mono)",
            fontSize: 13,
            letterSpacing: "0.55em",
            textTransform: "uppercase",
            color: "var(--tinta)",
            marginLeft: "0.55em",
          }}
        >
          Enjambre
        </div>
        <div className="kicker" style={{ marginTop: 12 }}>
          simulador de cumplimiento · logo pendiente
        </div>
      </div>
      <div style={{ width: 280 }}>
        <div style={{ height: 1, background: "rgba(233,236,242,0.12)", overflow: "hidden" }}>
          {listo ? (
            <div style={{ height: 1, width: "100%", background: "var(--tinta)", transition: "width 0.35s ease-out" }} />
          ) : (
            <div className="barra-indeterminada" style={{ height: 1, width: "26%", background: "var(--tinta)" }} />
          )}
        </div>
      </div>
      {falla && (
        <div
          style={{ fontFamily: "var(--mono)", fontSize: 12, color: "var(--rojo)", maxWidth: 420, textAlign: "center" }}
        >
          no se pudo leer la grilla: {falla}
          <br />
          ¿está corriendo la API? — uvicorn api.servidor:app --port 8000
        </div>
      )}
    </div>
  );
}
