"use client";

// Las tasas generales, pocas y en tiempo real. Solo campos que el motor emite
// o que son aritmética declarada sobre ellos (masa salarial y bajo-el-mínimo
// llegan calculados del servidor, con su # SUPUESTO documentado en api/).

import { useMemo } from "react";
import CurvaBrecha from "./CurvaBrecha";
import { copBillones, pct } from "@/lib/formato";
import { ultimaRonda, usarAlmacen } from "@/estado/simulacion";

interface Fila {
  nombre: string;
  valor: string;
  color?: string;
}

export default function Metricas() {
  const rondas = usarAlmacen((s) => s.rondas);
  const poblacion = usarAlmacen((s) => s.poblacion);
  const ult = ultimaRonda({ rondas });

  // masa salarial base (COP/mes) para traducir el índice relativo a plata
  const masaBase = useMemo(
    () =>
      poblacion
        ? poblacion.arquetipos.reduce((s, a) => s + a.peso * a.ingreso_por_trabajador, 0)
        : 0,
    [poblacion]
  );

  if (!ult) return null;
  const c = ult.contrato;

  const filas: Fila[] = [
    {
      nombre: "Empleo relativo al reposo",
      valor: pct(c.empleo_relativo),
      color: c.empleo_relativo < 0.98 ? "var(--rojo)" : undefined,
    },
  ];
  if (ult.masa_salarial_relativa != null) {
    filas.push({
      nombre: "Masa salarial · proxy de PIB laboral",
      valor: `${pct(ult.masa_salarial_relativa)} · ${copBillones(masaBase * ult.masa_salarial_relativa)}/mes`,
      color: ult.masa_salarial_relativa < 1 ? "var(--rojo)" : "var(--verde)",
    });
  }
  filas.push({
    nombre: "Prob. de sanción · fiscalización endógena",
    valor: pct(c.prob_fiscalizacion, 2),
  });
  if (ult.fraccion_jornada_recortada > 0.001) {
    filas.push({
      nombre: "Conserva el empleo con jornada recortada",
      valor: pct(ult.fraccion_jornada_recortada),
      color: "var(--ambar)",
    });
  }
  if (ult.fraccion_bajo_minimo != null) {
    filas.push({
      nombre: "Ocupados que ganan bajo el mínimo nuevo",
      valor: pct(ult.fraccion_bajo_minimo),
    });
  }
  if (c.traslado_precios_pct > 0.005) {
    filas.push({
      nombre: "Traslado a precios declarado por firmas",
      valor: `${c.traslado_precios_pct.toFixed(2).replace(".", ",")} %`,
    });
  }
  if (ult.fraccion_poblacion_llm > 0 && ult.fraccion_poblacion_llm < 1) {
    filas.push({
      nombre: "Población decidida por LLM (top-K)",
      valor: pct(ult.fraccion_poblacion_llm),
    });
  }

  return (
    <div
      className="panel"
      style={{ right: 36, bottom: 96, width: 380, display: "flex", flexDirection: "column", gap: 8 }}
    >
      <CurvaBrecha />
      <div>
        {filas.map((f) => (
          <div
            key={f.nombre}
            style={{
              display: "flex",
              alignItems: "baseline",
              justifyContent: "space-between",
              gap: 18,
              padding: "8px 0",
              borderTop: "1px solid var(--linea)",
            }}
          >
            <div style={{ fontSize: 13, color: "var(--tinta-suave)" }}>{f.nombre}</div>
            <div className="cifra" style={{ fontSize: 21, color: f.color ?? "var(--tinta)", whiteSpace: "nowrap" }}>
              {f.valor}
            </div>
          </div>
        ))}
      </div>
      <div style={{ fontFamily: "var(--mono)", fontSize: 10.5, color: "var(--tinta-tenue)", textAlign: "right" }}>
        celdas empleadoras GEIH-DANE · cifras de esta corrida · masa salarial y bajo-mínimo con supuesto declarado
      </div>
    </div>
  );
}
