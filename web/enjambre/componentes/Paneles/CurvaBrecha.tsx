"use client";

// ⚠️ NO SE MONTA. Su único importador es `Metricas.tsx`, que tampoco se monta:
// las dos salieron del lienzo en `Simulacion.tsx` (P2). La versión que sí se
// ve es `GraficaBrecha` en `componentes/reporte/Graficas.tsx`, que dibuja lo
// mismo con el tamaño del reporte. Esta se conserva como la variante compacta
// para el lienzo, por si la brecha vuelve a pantalla.

// La gráfica imprescindible: la proyección oficial (plana, la ronda 0 asumida
// para siempre) contra la cascada real, ronda a ronda, con la banda cuando
// existe. Es el producto del proyecto en 320×96 píxeles.
//
// Tres cosas que antes la hacían ilegible y ya no:
//   1. El eje Y se recalculaba en cada ronda, así que la línea "oficial" — la
//      referencia que por definición NO se mueve — se movía en pantalla. Ahora
//      el dominio se ancla a la proyección oficial y solo crece.
//   2. No había ejes ni ticks: 20 px de separación no se podían leer como pp.
//   3. Las dos etiquetas caían en la misma x en la última ronda y se pisaban.

import { pct } from "@/lib/formato";
import { rondasVisibles, usarAlmacen } from "@/estado/simulacion";

const W = 320;
const H = 96;
const M = { l: 30, r: 46, t: 10, b: 16 };

export default function CurvaBrecha() {
  const rondas = usarAlmacen((s) => s.rondas);
  const rondaMostrada = usarAlmacen((s) => s.rondaMostrada);
  const poblacion = usarAlmacen((s) => s.poblacion);

  // S2-5: solo las rondas que el enjambre ya mostró. La curva avanza en X al
  // mismo reloj que el enjambre en vez de saltar al final.
  const vis = rondasVisibles({ rondas, rondaMostrada });
  if (vis.length < 2 || !poblacion) return null;

  const total = poblacion.rondas_totales;
  const oficial = vis[0].contrato.tasa_informalidad;
  const valores = vis.map((r) => r.contrato.tasa_informalidad);
  const p10s = vis.map((r) => r.contrato.banda.p10);
  const p90s = vis.map((r) => r.contrato.banda.p90);
  const hayBanda = vis.some((r) => !r.contrato.banda.degenerada);

  // Dominio anclado a la oficial y simétrico como mínimo, para que la línea de
  // referencia se quede quieta. SUPUESTO: el piso de ventana (±3 pp) es
  // legibilidad — con menos, el ruido de redondeo se ve como una cascada.
  const extremos = [...valores, ...p10s, ...p90s, oficial];
  const alcance = Math.max(0.03, ...extremos.map((v) => Math.abs(v - oficial))) * 1.15;
  const minV = oficial - alcance;
  const maxV = oficial + alcance;

  const x = (i: number) => M.l + (i / (total - 1)) * (W - M.l - M.r);
  const y = (v: number) => M.t + (1 - (v - minV) / (maxV - minV)) * (H - M.t - M.b);

  const linea = valores.map((v, i) => `${i ? "L" : "M"}${x(i)},${y(v)}`).join(" ");
  const banda =
    valores.map((_, i) => `${i ? "L" : "M"}${x(i)},${y(p90s[i])}`).join(" ") +
    [...valores.keys()].reverse().map((i) => `L${x(i)},${y(p10s[i])}`).join("") +
    "Z";

  const ultima = valores.length - 1;
  // Si las dos etiquetas caen encima (pasa siempre en la última ronda, donde
  // comparten la misma x), se separan verticalmente.
  const yOficial = y(oficial);
  const yReal = y(valores[ultima]);
  const choque = Math.abs(yOficial - yReal) < 11 && ultima === total - 1;
  const desplazoReal = choque ? (yReal >= yOficial ? 8 : -8) : 0;

  const ticks = [maxV, oficial, minV];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
      <div className="kicker">la brecha · proyección oficial vs corrida real</div>
      <svg width={W} height={H} style={{ overflow: "visible" }}>
        {/* grilla y eje Y: sin esto la distancia vertical no es interpretable */}
        {ticks.map((v, i) => (
          <g key={i}>
            <line
              x1={M.l}
              y1={y(v)}
              x2={W - M.r}
              y2={y(v)}
              stroke="var(--linea)"
              strokeWidth={1}
            />
            <text
              x={M.l - 5}
              y={y(v) + 3}
              textAnchor="end"
              fill="var(--tinta-tenue)"
              fontSize={8.5}
              fontFamily="var(--mono)"
            >
              {pct(v)}
            </text>
          </g>
        ))}

        {hayBanda && <path d={banda} fill="var(--azul)" opacity={0.12} />}

        <line
          x1={x(0)}
          y1={yOficial}
          x2={x(total - 1)}
          y2={yOficial}
          stroke="var(--tinta-tenue)"
          strokeDasharray="3 4"
          strokeWidth={1}
        />
        <path d={linea} fill="none" stroke="var(--azul-vivo)" strokeWidth={1.6} />
        {valores.map((v, i) => (
          <circle key={i} cx={x(i)} cy={y(v)} r={i === ultima ? 3 : 2} fill="var(--azul-vivo)" />
        ))}

        <text
          x={x(total - 1) + 6}
          y={yOficial + 3}
          fill="var(--tinta-tenue)"
          fontSize={9.5}
          fontFamily="var(--mono)"
        >
          oficial
        </text>
        <text
          x={x(ultima) + 6}
          y={yReal + 3 + desplazoReal}
          fill="var(--azul-vivo)"
          fontSize={9.5}
          fontFamily="var(--mono)"
        >
          real {pct(valores[ultima])}
        </text>
      </svg>
    </div>
  );
}
