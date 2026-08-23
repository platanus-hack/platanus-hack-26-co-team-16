"use client";

// Pantalla 2: dos caminos, uno solo abierto. El bloqueado se ve bloqueado a
// propósito — es una promesa de producto, no un enlace roto.

import { usarAlmacen } from "@/estado/simulacion";

export default function Menu() {
  const setFase = usarAlmacen((s) => s.setFase);
  const poblacion = usarAlmacen((s) => s.poblacion);

  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        gap: 46,
      }}
    >
      <div className="aparecer" style={{ textAlign: "center", display: "flex", flexDirection: "column", gap: 14 }}>
        <div className="kicker">mercado laboral de Bogotá · GEIH-DANE 2026</div>
        <h1 className="cifra" style={{ fontSize: 44, color: "var(--tinta)" }}>
          ¿Qué política quieres estresar?
        </h1>
        {poblacion && (
          <div style={{ fontFamily: "var(--mono)", fontSize: 12, color: "var(--tinta-tenue)" }}>
            {poblacion.arquetipos.length} celdas empleadoras ·{" "}
            {Math.round(poblacion.peso_total / 1e6).toLocaleString("es-CO")}
            {","}
            {Math.round((poblacion.peso_total % 1e6) / 1e5)} millones de trabajadores representados
          </div>
        )}
      </div>

      <div className="aparecer" style={{ display: "flex", flexDirection: "column", gap: 16, width: 460 }}>
        <button className="boton boton--primario" onClick={() => setFase("politica")}>
          Simular incremento del salario mínimo
        </button>
        <button className="boton" disabled title="próximamente">
          Simular política personalizada
          <span style={{ display: "block", fontSize: 10, letterSpacing: "0.2em", marginTop: 6, color: "var(--tinta-tenue)" }}>
            bloqueado · próxima iteración
          </span>
        </button>
      </div>
    </div>
  );
}
