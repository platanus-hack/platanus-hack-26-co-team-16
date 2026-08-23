"use client";

// Las tasas generales, pocas y en tiempo real. Solo campos que el motor emite
// o que son aritmética declarada sobre ellos (masa salarial y bajo-el-mínimo
// llegan calculados del servidor, con su # SUPUESTO documentado en api/).

import { useMemo } from "react";
import CurvaBrecha from "./CurvaBrecha";
import { copBillones, pct } from "@/lib/formato";
import { usarAlmacen } from "@/estado/simulacion";

interface Fila {
  nombre: string;
  valor: string;
  color?: string;
}

export default function Metricas() {
  const poblacion = usarAlmacen((s) => s.poblacion);
  // S2-5: la ronda mostrada, no la última llegada (ver motorVisual.ts).
  const ult = usarAlmacen((s) => s.rondaMostrada);

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
  // SUPUESTO: 0,1% es el piso de "vale la pena mostrarlo" para estas filas
  // (aquí y en fallback/sin_salida más abajo) — ruido de redondeo por debajo,
  // elegido para no llenar el panel de ceros. No es un umbral del motor.
  if (ult.fraccion_jornada_recortada > 0.001) {
    filas.push({
      nombre: "Conserva el empleo con jornada recortada",
      valor: pct(ult.fraccion_jornada_recortada),
      color: "var(--ambar)",
    });
  }
  // S2-7: fraccion_fallback y fraccion_sin_salida viajan en el contrato
  // (serializar.py) desde antes, pero ningún panel los leía. Es lo primero
  // que pide un juez técnico: cuánto del modelo terminó en la salida de
  // emergencia en vez de en una decisión real.
  if (ult.fraccion_fallback > 0.001) {
    filas.push({
      nombre: "Decisiones en fallback (LLM sin propuesta viable)",
      valor: pct(ult.fraccion_fallback),
      color: ult.fraccion_fallback > 0.05 ? "var(--rojo)" : "var(--ambar)",
    });
  }
  if (ult.fraccion_sin_salida > 0.001) {
    filas.push({
      nombre: "Sin salida factible · todo vetado",
      valor: pct(ult.fraccion_sin_salida),
      color: "var(--rojo)",
    });
  }
  if (ult.fraccion_bajo_minimo != null) {
    filas.push({
      nombre: "Ocupados que ganan bajo el mínimo nuevo",
      valor: pct(ult.fraccion_bajo_minimo),
    });
  }
  // SUPUESTO: 0,5% de piso para mostrar traslado a precios — mismo criterio
  // de "no llenar el panel con ruido de redondeo" que arriba.
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
