"use client";

// Pantalla 1: el logo (placeholder tipográfico — el logo aún no existe) y una
// barra de carga. La barra avanza de verdad: espera el GET /poblacion, que es
// lo único que la simulación necesita precargar.

import { useEffect, useRef, useState } from "react";
import { cargarPoblacion } from "@/estado/flujo";
import { usarAlmacen } from "@/estado/simulacion";

export default function Carga() {
  const setFase = usarAlmacen((s) => s.setFase);
  const [progreso, setProgreso] = useState(0);
  const [falla, setFalla] = useState<string | null>(null);
  const listo = useRef(false);

  useEffect(() => {
    let vivo = true;
    // La barra sube sola hasta 82% mientras llega la red; el tramo final es real.
    const timer = setInterval(() => {
      setProgreso((p) => (listo.current ? Math.min(1, p + 0.1) : Math.min(0.82, p + 0.02)));
    }, 50);
    cargarPoblacion()
      .then(() => {
        if (!vivo) return;
        listo.current = true;
        setTimeout(() => vivo && setFase("menu"), 650);
      })
      .catch((e) => vivo && setFalla(String(e?.message ?? e)));
    return () => {
      vivo = false;
      clearInterval(timer);
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
        <div style={{ height: 1, background: "rgba(233,236,242,0.12)" }}>
          <div
            style={{
              height: 1,
              width: `${progreso * 100}%`,
              background: "var(--tinta)",
              transition: "width 0.2s linear",
            }}
          />
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
