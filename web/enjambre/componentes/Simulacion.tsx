"use client";

// Pantalla 4: el enjambre. El lienzo three.js atrás; los paneles de dato,
// narrativa y tiempo flotando encima. Cada panel es un componente separado.

import dynamic from "next/dynamic";
import Link from "next/link";
import Globo from "@/componentes/Globo";
import BarraTiempo from "@/componentes/Paneles/BarraTiempo";
import ColumnaIzquierda from "@/componentes/Paneles/ColumnaIzquierda";
import Continuar from "@/componentes/Paneles/Continuar";
import Hero from "@/componentes/Paneles/Hero";
import Metricas from "@/componentes/Paneles/Metricas";
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
        // Estaba en `top:150`, pisando la línea de la banda del Hero con
        // z-index 20. Abajo a la derecha no compite con nada: Metricas termina
        // en bottom:96 y la barra de tiempo va centrada.
        <div
          className="aparecer"
          style={{ position: "absolute", right: 36, bottom: 30, zIndex: 20, display: "flex", gap: 10 }}
        >
          {/* P3: al terminar TODAS las rondas aparece el reporte, con todo lo
              que se sacó del lienzo para que la simulación se viera. */}
          <Link
            href="/reporte"
            className="boton boton--primario"
            style={{ padding: "12px 22px", fontSize: 11 }}
          >
            ver reporte
          </Link>
          <button
            className="boton"
            style={{ padding: "12px 22px", fontSize: 11 }}
            onClick={() => setFase("politica")}
          >
            otra política
          </button>
        </div>
      )}
      <Titulo />
      {/* `Procedencia` sale del lienzo: abierto tapaba el centro del enjambre
          con z-index 20, que es justo donde viven las celdas más pesadas. Su
          tabla DATO/NORMA/CALCULADO/SUPUESTO se muda al reporte (P3), donde se
          lee entera en vez de flotando sobre la simulación. El componente se
          conserva para reusarlo allá. */}
      <Hero />
      <Noticias />
      <Relato />
      <ColumnaIzquierda />
      <Metricas />
      <BarraTiempo />
      <Continuar />
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
