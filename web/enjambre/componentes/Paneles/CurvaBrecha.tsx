"use client";

// La gráfica imprescindible: la proyección oficial (plana, la ronda 0 asumida
// para siempre) contra la cascada real, ronda a ronda, con la banda cuando
// existe. Es el producto del proyecto en 240×64 píxeles.

import { pct } from "@/lib/formato";
import { usarAlmacen } from "@/estado/simulacion";

const W = 320;
const H = 72;
const M = { l: 6, r: 46, t: 10, b: 14 };

export default function CurvaBrecha() {
  const rondas = usarAlmacen((s) => s.rondas);
  const poblacion = usarAlmacen((s) => s.poblacion);
  if (rondas.length < 2 || !poblacion) return null;

  const total = poblacion.rondas_totales;
  const oficial = rondas[0].contrato.tasa_informalidad;
  const valores = rondas.map((r) => r.contrato.tasa_informalidad);
  const p10s = rondas.map((r) => r.contrato.banda.p10);
  const p90s = rondas.map((r) => r.contrato.banda.p90);

  const maxV = Math.max(...p90s, ...valores, oficial) + 0.01;
  const minV = Math.min(...p10s, ...valores, oficial) - 0.01;
  const x = (i: number) => M.l + (i / (total - 1)) * (W - M.l - M.r);
  const y = (v: number) => M.t + (1 - (v - minV) / (maxV - minV)) * (H - M.t - M.b);

  const linea = valores.map((v, i) => `${i ? "L" : "M"}${x(i)},${y(v)}`).join(" ");
  const banda =
    valores.map((_, i) => `${i ? "L" : "M"}${x(i)},${y(p90s[i])}`).join(" ") +
    [...valores.keys()].reverse().map((i) => `L${x(i)},${y(p10s[i])}`).join("") +
    "Z";

  const ultima = valores.length - 1;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
      <div className="kicker">la brecha · proyección oficial vs corrida real</div>
      <svg width={W} height={H} style={{ overflow: "visible" }}>
        <path d={banda} fill="var(--azul)" opacity={0.1} />
        <line
          x1={x(0)}
          y1={y(oficial)}
          x2={x(total - 1)}
          y2={y(oficial)}
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
          y={y(oficial) + 3}
          fill="var(--tinta-tenue)"
          fontSize={9.5}
          fontFamily="var(--mono)"
        >
          oficial {pct(oficial)}
        </text>
        <text
          x={x(ultima) + 6}
          y={y(valores[ultima]) + 3}
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
