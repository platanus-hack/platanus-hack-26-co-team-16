"use client";

// Pantalla 4: el enjambre. El lienzo three.js atrás; los paneles de dato,
// narrativa y tiempo flotando encima. Cada panel es un componente separado.

import dynamic from "next/dynamic";
import Globo from "@/componentes/Globo";
import BarraTiempo from "@/componentes/Paneles/BarraTiempo";
import Estrategias from "@/componentes/Paneles/Estrategias";
import Hero from "@/componentes/Paneles/Hero";
import Leyenda from "@/componentes/Paneles/Leyenda";
import Metricas from "@/componentes/Paneles/Metricas";
import Procedencia from "@/componentes/Paneles/Procedencia";
import Titulo from "@/componentes/Paneles/Titulo";
import Noticias from "@/componentes/Noticias";
import Relato from "@/componentes/Relato";
import { usarAlmacen } from "@/estado/simulacion";

// three.js solo vive en el cliente
const Lienzo = dynamic(() => import("@/componentes/Lienzo"), { ssr: false });

export default function Simulacion() {
  const error = usarAlmacen((s) => s.error);
  const conexion = usarAlmacen((s) => s.conexion);
  const setFase = usarAlmacen((s) => s.setFase);

  return (
    <div style={{ position: "absolute", inset: 0 }}>
      <Lienzo />
      {conexion === "terminada" && (
        <button
          className="boton aparecer"
          style={{ position: "absolute", right: 36, top: 150, zIndex: 20, padding: "12px 22px", fontSize: 11 }}
          onClick={() => setFase("politica")}
        >
          otra política
        </button>
      )}
      <Titulo />
      <Procedencia />
      <Hero />
      <Noticias />
      <Relato />
      <Estrategias />
      <Metricas />
      <BarraTiempo />
      <Leyenda />
      <Globo />
      {error && (
        <div
          className="panel panel--activo vidrio"
          style={{
            left: "50%",
            top: "50%",
            transform: "translate(-50%,-50%)",
            padding: "26px 34px",
            maxWidth: 520,
            textAlign: "center",
            display: "flex",
            flexDirection: "column",
            gap: 14,
          }}
        >
          <div className="kicker" style={{ color: "var(--rojo)" }}>
            la corrida murió
          </div>
          <div style={{ fontFamily: "var(--mono)", fontSize: 13, lineHeight: 1.6, color: "var(--tinta-suave)" }}>
            {error}
          </div>
          <button
            className="boton"
            style={{ alignSelf: "center", padding: "12px 26px" }}
            onClick={() => usarAlmacen.getState().setFase("politica")}
          >
            volver al control
          </button>
        </div>
      )}
    </div>
  );
}
