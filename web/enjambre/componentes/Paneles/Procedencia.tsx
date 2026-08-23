"use client";

// Panel de procedencia (C4/C6, decisión 22:30 del vet): por cada métrica que
// aparece en pantalla, de dónde sale. Es la respuesta a "¿de dónde se
// alimenta esto?" sin que un juez tenga que preguntarla ni ir a leer código.
//
//   DATO      = GEIH/DANE, expandido, sin tocar
//   NORMA     = un valor legal citado (decreto, salario mínimo anterior)
//   CALCULADO = aritmética del motor sobre DATO y/o NORMA, sin números sueltos
//   SUPUESTO  = una elección declarada donde el motor no puede derivar el
//               número — cada una tiene su `# SUPUESTO:` grepeable en el código
//
// Colapsado por defecto para no competir con el enjambre; se abre con el botón.

import { useState } from "react";

type Tipo = "DATO" | "NORMA" | "CALCULADO" | "SUPUESTO";

const COLOR: Record<Tipo, string> = {
  DATO: "var(--verde)",
  NORMA: "var(--azul-vivo)",
  CALCULADO: "var(--tinta)",
  SUPUESTO: "var(--ambar)",
};

interface Fila {
  metrica: string;
  tipo: Tipo;
  fuente: string;
}

const FILAS: Fila[] = [
  { metrica: "Informalidad observada (punto de partida)", tipo: "DATO", fuente: "GEIH-DANE, expandida a celdas" },
  { metrica: "Celdas: sector, tamaño, ingreso, empleo", tipo: "DATO", fuente: "GEIH-DANE, sin tocar" },
  { metrica: "Piso salarial anterior", tipo: "NORMA", fuente: "smlmv_anterior_cop, parametros_legales.json" },
  { metrica: "% de alza simulado (el slider)", tipo: "NORMA", fuente: "lo fija quien mira; 23% es el decreto real de Bogotá" },
  { metrica: "Informalidad, empleo, prob. de sanción por ronda", tipo: "CALCULADO", fuente: "motor de mejor respuesta, sobre DATO + NORMA" },
  { metrica: "Reparto de estrategias", tipo: "CALCULADO", fuente: "propuesta LLM (o reglas), vetada por factibilidad" },
  { metrica: "Fallback / sin salida", tipo: "CALCULADO", fuente: "conteo directo de decisiones del motor" },
  { metrica: "Traslado a precios", tipo: "CALCULADO", fuente: "declarado por la firma, no observado en la GEIH" },
  { metrica: "Masa salarial relativa", tipo: "SUPUESTO", fuente: "el alza se aplica solo al empleo formal — serializar.py" },
  { metrica: "Ocupados bajo el mínimo nuevo", tipo: "SUPUESTO", fuente: "piso nuevo = anterior × (1+alza) — serializar.py" },
  { metrica: "1 ronda = N meses / horizonte", tipo: "SUPUESTO", fuente: "ADR 0005 — el reloj de la simulación" },
  // C2/E4 · decía "Banda de incertidumbre (p10–p90)". Con N=5 el p10/p90 ES el
  // mínimo y el máximo de las cinco paráfrasis, no un percentil calibrado, y
  // "incertidumbre" se lee como intervalo de confianza — que no calculamos.
  { metrica: "Rango entre paráfrasis (mín–máx, N=5)", tipo: "CALCULADO", fuente: "5 paráfrasis del mismo prompt — NO es un intervalo de confianza ni un p10/p90 calibrado" },
];

// `forzarAbierto` lo usa el reporte: ahí la tabla no es un panel flotante que
// tape el enjambre, es una sección más del documento y va siempre desplegada.
export default function Procedencia({ forzarAbierto = false }: { forzarAbierto?: boolean }) {
  const [abierto, setAbierto] = useState(false);
  const visible = abierto || forzarAbierto;

  return (
    <div
      style={
        forzarAbierto
          ? { position: "static" }
          : { position: "absolute", left: "50%", top: 32, transform: "translateX(-50%)", zIndex: 20 }
      }
    >
      {!forzarAbierto && (
      <button
        onClick={() => setAbierto((v) => !v)}
        style={{
          fontFamily: "var(--mono)",
          fontSize: 10,
          letterSpacing: "0.08em",
          padding: "4px 10px",
          borderRadius: 3,
          border: "1px solid var(--linea)",
          background: "var(--panel)",
          backdropFilter: "blur(14px)",
          color: "var(--tinta-suave)",
          cursor: "pointer",
        }}
      >
        {abierto ? "cerrar procedencia ▲" : "¿de dónde sale esto? ▾"}
      </button>
      )}
      {visible && (
        <div
          className={forzarAbierto ? undefined : "vidrio"}
          style={{
            marginTop: forzarAbierto ? 0 : 8,
            width: forzarAbierto ? "100%" : 460,
            maxHeight: forzarAbierto ? "none" : "60vh",
            overflowY: forzarAbierto ? "visible" : "auto",
            border: forzarAbierto ? "none" : "1px solid var(--linea)",
            padding: forzarAbierto ? 0 : "14px 16px",
            display: "flex",
            flexDirection: "column",
            gap: 4,
          }}
        >
          <div className="kicker" style={{ marginBottom: 6 }}>
            procedencia · métrica por métrica
          </div>
          {FILAS.map((f) => (
            <div
              key={f.metrica}
              style={{
                display: "grid",
                gridTemplateColumns: "76px 1fr",
                gap: 10,
                alignItems: "baseline",
                padding: "5px 0",
                borderTop: "1px solid var(--linea)",
              }}
            >
              <span
                style={{
                  fontFamily: "var(--mono)",
                  fontSize: 9.5,
                  letterSpacing: "0.06em",
                  color: COLOR[f.tipo],
                }}
              >
                {f.tipo}
              </span>
              <span style={{ fontSize: 12, color: "var(--tinta-suave)" }}>
                {f.metrica}
                <span style={{ display: "block", fontFamily: "var(--mono)", fontSize: 10, color: "var(--tinta-tenue)" }}>
                  {f.fuente}
                </span>
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
