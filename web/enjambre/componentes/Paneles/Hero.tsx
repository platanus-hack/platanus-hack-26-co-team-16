"use client";

// LA cifra de la corrida: la informalidad, y de dónde salió.
//
// Este panel mostraba cinco números mudos y había que pasar el mouse para saber
// cuál era cuál. Con una sola pasada de demo eso no alcanza: quien mira tiene
// que saber en el primer segundo QUÉ está viendo. Ahora hay una cifra, dice su
// nombre, y trae al lado el punto de partida y el movimiento — un número solo
// no significa nada sin el de antes.
//
// Las otras cuatro no se borraron: empleo, sanción, fallback y sin-salida
// bajaron a la carta de ronda (`BarraTiempo.tsx`), que es donde vive el detalle
// del periodo. Son las primeras que pide un juez técnico y no pueden
// desaparecer del lienzo solo porque estorbaban.

import { pct, pp } from "@/lib/formato";
import { usarAlmacen } from "@/estado/simulacion";

export default function Hero() {
  const rondas = usarAlmacen((s) => s.rondas);
  // S2-5: la ronda mostrada, no la última llegada (ver motorVisual.ts).
  const ult = usarAlmacen((s) => s.rondaMostrada);

  if (!ult || !rondas.length) return null;

  const c = ult.contrato;
  const inicial = rondas[0].contrato.tasa_informalidad;
  // SUPUESTO: 0,05pp es el piso para considerar que la tasa "se movió" y
  // colorear la cifra — ruido de redondeo por debajo, no un umbral del motor.
  const delta = (c.tasa_informalidad - inicial) * 100;
  const movida = delta > 0.05;

  return (
    <div
      className="panel"
      style={{ right: 36, top: 30, display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 6 }}
    >
      <div
        style={{
          fontFamily: "var(--mono)",
          fontSize: 11,
          letterSpacing: "0.14em",
          textTransform: "uppercase",
          color: "var(--tinta-suave)",
        }}
      >
        informalidad
      </div>
      <div
        className="cifra"
        style={{
          fontSize: 62,
          lineHeight: 1,
          color: movida ? "var(--azul-vivo)" : "var(--tinta)",
          textAlign: "right",
        }}
      >
        {pct(c.tasa_informalidad)}
      </div>
      <div style={{ fontSize: 12.5, color: "var(--tinta-suave)", textAlign: "right" }}>
        cuánta gente queda fuera de regla
      </div>
      {/* El punto de partida al lado del resultado: sin él, la cifra de arriba
          no dice si la política movió algo o no. */}
      <div
        style={{
          fontFamily: "var(--mono)",
          fontSize: 12,
          color: "var(--tinta-tenue)",
          textAlign: "right",
        }}
      >
        desde {pct(inicial)}{" "}
        <span style={{ color: movida ? "var(--azul-vivo)" : "var(--tinta-tenue)" }}>
          ({pp(delta)})
        </span>
      </div>
      {!c.estabilizada && c.ronda > 0 && (
        <div style={{ fontFamily: "var(--mono)", fontSize: 10, color: "var(--ambar)" }}>no estabilizada</div>
      )}
    </div>
  );
}
