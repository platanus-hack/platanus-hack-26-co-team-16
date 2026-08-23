"use client";

// Las gráficas del laboratorio, en SVG a mano.
//
// Sin librería de charts a propósito: `AGENTS.md` congela dependencias nuevas
// en el feature freeze, y la única gráfica que ya existía en el proyecto
// (`CurvaBrecha`) también es SVG construido a mano. Se sigue el mismo patrón.
//
// Todas leen del histórico acumulado. Ninguna calcula nada que el motor no
// haya publicado: son proyecciones de campos del contrato.

import { CorridaRegistrada } from "@/lib/corrida";
import { pct } from "@/lib/formato";

const W = 460;
const H = 240;
const M = { l: 52, r: 18, t: 16, b: 38 };

const COLOR_MODO: Record<string, string> = {
  llm: "var(--azul-vivo)",
  reglas: "var(--ambar)",
};

function Marco({
  titulo,
  ejeX,
  ejeY,
  nota,
  children,
}: {
  titulo: string;
  ejeX: string;
  ejeY: string;
  nota?: string;
  children: React.ReactNode;
}) {
  return (
    <figure style={{ margin: 0 }}>
      <figcaption className="kicker" style={{ marginBottom: 8 }}>
        {titulo}
      </figcaption>
      <svg width={W} height={H} style={{ maxWidth: "100%", height: "auto", overflow: "visible" }}>
        {children}
        <text
          x={M.l + (W - M.l - M.r) / 2}
          y={H - 6}
          textAnchor="middle"
          fill="var(--tinta-tenue)"
          fontSize={9.5}
          fontFamily="var(--mono)"
        >
          {ejeX}
        </text>
        <text
          x={-(M.t + (H - M.t - M.b) / 2)}
          y={11}
          transform="rotate(-90)"
          textAnchor="middle"
          fill="var(--tinta-tenue)"
          fontSize={9.5}
          fontFamily="var(--mono)"
        >
          {ejeY}
        </text>
      </svg>
      {nota && (
        <div style={{ fontSize: 11, color: "var(--tinta-tenue)", lineHeight: 1.5, marginTop: 6 }}>
          {nota}
        </div>
      )}
    </figure>
  );
}

function Ejes({
  xs,
  ys,
  fmtY,
}: {
  xs: number[];
  ys: number[];
  fmtY: (v: number) => string;
}) {
  const minX = Math.min(...xs);
  const maxX = Math.max(...xs);
  const minY = Math.min(...ys);
  const maxY = Math.max(...ys);
  const ticks = [maxY, (maxY + minY) / 2, minY];
  const y = (v: number) =>
    M.t + (1 - (v - minY) / (maxY - minY || 1)) * (H - M.t - M.b);
  const x = (v: number) => M.l + ((v - minX) / (maxX - minX || 1)) * (W - M.l - M.r);
  return (
    <>
      {ticks.map((v, i) => (
        <g key={i}>
          <line x1={M.l} y1={y(v)} x2={W - M.r} y2={y(v)} stroke="var(--linea)" />
          <text
            x={M.l - 6}
            y={y(v) + 3}
            textAnchor="end"
            fill="var(--tinta-tenue)"
            fontSize={9}
            fontFamily="var(--mono)"
          >
            {fmtY(v)}
          </text>
        </g>
      ))}
      <text x={M.l} y={H - M.b + 14} fill="var(--tinta-tenue)" fontSize={9} fontFamily="var(--mono)">
        {minX.toFixed(1).replace(".", ",")}
      </text>
      <text
        x={W - M.r}
        y={H - M.b + 14}
        textAnchor="end"
        fill="var(--tinta-tenue)"
        fontSize={9}
        fontFamily="var(--mono)"
      >
        {maxX.toFixed(1).replace(".", ",")}
      </text>
    </>
  );
}

/** Informalidad final contra el alza simulada: el barrido que se construye solo. */
export function BarridoPolitica({ corridas }: { corridas: CorridaRegistrada[] }) {
  if (corridas.length < 1) return null;
  const xs = corridas.map((c) => c.aumento_pct);
  const ys = corridas.map((c) => c.informalidad_final);
  const minX = Math.min(...xs);
  const maxX = Math.max(...xs);
  const minY = Math.min(...ys);
  const maxY = Math.max(...ys);
  const x = (v: number) => M.l + ((v - minX) / (maxX - minX || 1)) * (W - M.l - M.r);
  const y = (v: number) => M.t + (1 - (v - minY) / (maxY - minY || 1)) * (H - M.t - M.b);

  return (
    <Marco
      titulo="informalidad final vs alza simulada"
      ejeX="% de alza del salario mínimo"
      ejeY="informalidad final"
      nota={`Un punto por corrida acumulada (${corridas.length}). Si aparece un codo, ahí es donde el sistema se quiebra — pero hacen falta corridas en todo el rango para verlo, y esta curva se construye usando el simulador.`}
    >
      <Ejes xs={xs} ys={ys} fmtY={(v) => pct(v)} />
      {corridas.map((c, i) => (
        <circle
          key={i}
          cx={x(c.aumento_pct)}
          cy={y(c.informalidad_final)}
          r={4}
          fill={COLOR_MODO[c.modo] ?? "var(--tinta-tenue)"}
          opacity={0.85}
        />
      ))}
    </Marco>
  );
}

/** Dispersión entre corridas con los MISMOS parámetros: ¿da lo mismo si corre otra vez? */
export function Dispersion({ corridas }: { corridas: CorridaRegistrada[] }) {
  const grupos = new Map<string, CorridaRegistrada[]>();
  for (const c of corridas) {
    const k = `${c.aumento_pct}·${c.modo}·${c.parafrasis ?? "?"}`;
    grupos.set(k, [...(grupos.get(k) ?? []), c]);
  }
  const repetidos = [...grupos.entries()].filter(([, v]) => v.length > 1);
  if (!repetidos.length) {
    return (
      <Marco titulo="dispersión con los mismos parámetros" ejeX="" ejeY="">
        <text x={M.l} y={H / 2} fill="var(--tinta-tenue)" fontSize={11.5}>
          Todavía no hay dos corridas con parámetros idénticos.
        </text>
      </Marco>
    );
  }
  const xs = repetidos.map((_, i) => i);
  const ys = repetidos.flatMap(([, v]) => v.map((c) => c.informalidad_final));
  const minY = Math.min(...ys);
  const maxY = Math.max(...ys);
  const y = (v: number) => M.t + (1 - (v - minY) / (maxY - minY || 1)) * (H - M.t - M.b);
  const x = (i: number) => M.l + ((i + 0.5) / repetidos.length) * (W - M.l - M.r);

  return (
    <Marco
      titulo="dispersión con los mismos parámetros"
      ejeX="configuración repetida"
      ejeY="informalidad final"
      nota="Cada columna es una configuración corrida más de una vez. Si los puntos de una columna se separan, el resultado no es una línea sino un rango, y así hay que reportarlo."
    >
      <Ejes xs={xs} ys={ys} fmtY={(v) => pct(v)} />
      {repetidos.map(([k, v], i) => (
        <g key={k}>
          <line
            x1={x(i)}
            y1={y(Math.min(...v.map((c) => c.informalidad_final)))}
            x2={x(i)}
            y2={y(Math.max(...v.map((c) => c.informalidad_final)))}
            stroke="var(--linea)"
            strokeWidth={2}
          />
          {v.map((c, j) => (
            <circle
              key={j}
              cx={x(i)}
              cy={y(c.informalidad_final)}
              r={3.5}
              fill={COLOR_MODO[c.modo] ?? "var(--tinta-tenue)"}
              opacity={0.85}
            />
          ))}
        </g>
      ))}
    </Marco>
  );
}

/** Propuestas vetadas por ronda: evidencia de que el veto de factibilidad hace algo. */
export function VetosPorRonda({ corridas }: { corridas: CorridaRegistrada[] }) {
  const puntos = corridas.flatMap((c) => c.rondas.map((r) => ({ ronda: r.ronda, v: r.vetadas, modo: c.modo })));
  if (!puntos.length) return null;
  const xs = puntos.map((p) => p.ronda);
  const ys = puntos.map((p) => p.v);
  const maxY = Math.max(...ys, 1);
  const maxX = Math.max(...xs, 1);
  const x = (v: number) => M.l + (v / (maxX || 1)) * (W - M.l - M.r);
  const y = (v: number) => M.t + (1 - v / maxY) * (H - M.t - M.b);

  return (
    <Marco
      titulo="propuestas vetadas por ronda"
      ejeX="ronda"
      ejeY="propuestas rechazadas"
      nota="El motor rechaza lo que la plata no permite. Esta serie es la evidencia directa de que el veto de factibilidad no es decorativo — y hasta ahora solo existía por celda, nunca como serie."
    >
      <Ejes xs={xs} ys={ys} fmtY={(v) => String(Math.round(v))} />
      {corridas.map((c, i) => (
        <polyline
          key={i}
          points={c.rondas.map((r) => `${x(r.ronda)},${y(r.vetadas)}`).join(" ")}
          fill="none"
          stroke={COLOR_MODO[c.modo] ?? "var(--tinta-tenue)"}
          strokeWidth={1.4}
          opacity={0.55}
        />
      ))}
    </Marco>
  );
}

/** p(sanción) por ronda: el mecanismo de la cascada, hecho visible. */
export function CascadaPorRonda({ corridas }: { corridas: CorridaRegistrada[] }) {
  const puntos = corridas.flatMap((c) => c.rondas.map((r) => ({ x: r.ronda, y: r.prob_fiscalizacion })));
  if (!puntos.length) return null;
  const xs = puntos.map((p) => p.x);
  const ys = puntos.map((p) => p.y);
  const maxX = Math.max(...xs, 1);
  const minY = Math.min(...ys);
  const maxY = Math.max(...ys);
  const x = (v: number) => M.l + (v / (maxX || 1)) * (W - M.l - M.r);
  const y = (v: number) => M.t + (1 - (v - minY) / (maxY - minY || 1)) * (H - M.t - M.b);

  return (
    <Marco
      titulo="probabilidad de sanción por ronda"
      ejeX="ronda"
      ejeY="p(sanción) por trimestre"
      nota="Es EL mecanismo: la capacidad de fiscalización es fija, así que más evasores bajan el riesgo de cada uno y eso induce más evasión. Si estas líneas bajan, la cascada está operando."
    >
      <Ejes xs={xs} ys={ys} fmtY={(v) => pct(v, 2)} />
      {corridas.map((c, i) => (
        <polyline
          key={i}
          points={c.rondas.map((r) => `${x(r.ronda)},${y(r.prob_fiscalizacion)}`).join(" ")}
          fill="none"
          stroke={COLOR_MODO[c.modo] ?? "var(--tinta-tenue)"}
          strokeWidth={1.4}
          opacity={0.55}
        />
      ))}
    </Marco>
  );
}
