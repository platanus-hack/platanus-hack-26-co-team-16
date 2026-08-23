"use client";

// Las cifras de la corrida, mudas.
//
// La pantalla es del mapa: el lienzo tiene que ser casi todo enjambre. Así que
// acá van los NÚMEROS y nada más — sin rótulos permanentes robando espacio y
// atención. Qué significa cada uno aparece al pasar el mouse por encima, o al
// hacer clic si alguien quiere fijarlo mientras explica.
//
// Este panel absorbió lo que antes estaba repartido entre el hero y el panel de
// métricas (que ya no se monta). Las cifras de abajo incluyen fallback y
// sin-salida: son las primeras que pide un juez técnico y no pueden
// desaparecer del lienzo solo porque estorbaban.

import { useState } from "react";
import { pct, pp } from "@/lib/formato";
import { usarAlmacen } from "@/estado/simulacion";

interface Cifra {
  clave: string;
  valor: string;
  etiqueta: string;
  color?: string;
}

function Muda({ c, tam, fija, onClick }: { c: Cifra; tam: number; fija: boolean; onClick: () => void }) {
  return (
    <div
      className={`cifra-muda${fija ? " cifra-muda--fija" : ""}`}
      onClick={onClick}
      style={{ pointerEvents: "auto" }}
    >
      <div
        className="cifra"
        style={{ fontSize: tam, lineHeight: 1, color: c.color ?? "var(--tinta)", textAlign: "right" }}
      >
        {c.valor}
      </div>
      <span className="cifra-muda__etiqueta">{c.etiqueta}</span>
    </div>
  );
}

export default function Hero() {
  const rondas = usarAlmacen((s) => s.rondas);
  // S2-5: la ronda mostrada, no la última llegada (ver motorVisual.ts).
  const ult = usarAlmacen((s) => s.rondaMostrada);
  const [fija, setFija] = useState<string | null>(null);

  if (!ult || !rondas.length) return null;

  const c = ult.contrato;
  const inicial = rondas[0].contrato.tasa_informalidad;
  // SUPUESTO: 0,05pp es el piso para considerar que la tasa "se movió" y
  // colorear la cifra — ruido de redondeo por debajo, no un umbral del motor.
  const delta = (c.tasa_informalidad - inicial) * 100;
  const movida = delta > 0.05;

  const principal: Cifra = {
    clave: "informalidad",
    valor: pct(c.tasa_informalidad),
    etiqueta: "informalidad · cuánta gente queda fuera de regla",
    color: movida ? "var(--azul-vivo)" : "var(--tinta)",
  };

  const secundarias: Cifra[] = [
    {
      clave: "brecha",
      valor: pp(delta),
      etiqueta: "brecha contra el escenario sin adaptación",
      color: movida ? "var(--azul-vivo)" : undefined,
    },
    {
      clave: "empleo",
      valor: pct(c.empleo_relativo),
      etiqueta: "empleo que sobrevive",
      color: c.empleo_relativo < 0.98 ? "var(--rojo)" : undefined,
    },
    {
      clave: "sancion",
      valor: pct(c.prob_fiscalizacion, 2),
      etiqueta: "probabilidad de sanción por trimestre",
    },
  ];

  if (ult.fraccion_fallback > 0.001) {
    secundarias.push({
      clave: "fallback",
      valor: pct(ult.fraccion_fallback),
      etiqueta: "sin propuesta viable: cayó al fallback",
      color: ult.fraccion_fallback > 0.05 ? "var(--rojo)" : "var(--ambar)",
    });
  }
  if (ult.fraccion_sin_salida > 0.001) {
    secundarias.push({
      clave: "sin_salida",
      valor: pct(ult.fraccion_sin_salida),
      etiqueta: "sin ninguna salida factible",
      color: "var(--rojo)",
    });
  }

  const alternar = (k: string) => setFija((v) => (v === k ? null : k));

  return (
    <div
      className="panel"
      style={{ right: 36, top: 30, display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 24 }}
    >
      <Muda c={principal} tam={58} fija={fija === principal.clave} onClick={() => alternar(principal.clave)} />
      <div style={{ display: "flex", gap: 20, alignItems: "flex-start" }}>
        {secundarias.map((s) => (
          <Muda key={s.clave} c={s} tam={19} fija={fija === s.clave} onClick={() => alternar(s.clave)} />
        ))}
      </div>
      {!c.estabilizada && c.ronda > 0 && (
        <div style={{ fontFamily: "var(--mono)", fontSize: 10, color: "var(--ambar)" }}>no estabilizada</div>
      )}
    </div>
  );
}
