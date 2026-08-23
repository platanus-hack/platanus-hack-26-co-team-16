"use client";

// El kit de gráficas del reporte. SVG a mano, sin librería: `AGENTS.md:111`
// congela dependencias nuevas y un SVG es texto.
//
// Todo el color sale de tokens CSS, nunca de literales, para que la hoja de
// impresión —que reasigna los tokens a negro sobre blanco— invierta las
// gráficas junto con el resto del documento sin código aparte.

import { ArquetipoEstatico, EventoRonda } from "@/estado/simulacion";
import { RondaRegistrada } from "@/lib/corrida";
import { miles, nombreEstrategia, nombreSector, pct } from "@/lib/formato";

const W = 760;
const M = { l: 62, r: 22, t: 14, b: 34 };

export const COLOR_FAMILIA_CSS: Record<string, string> = {
  informalizar: "var(--azul)",
  despedir: "var(--rojo)",
  bajar_horas: "var(--ambar)",
  subir_precios: "var(--ambar)",
  renegociar: "var(--ambar)",
  cumplir: "var(--verde)",
  absorber: "var(--verde)",
  otra: "var(--tinta-tenue)",
};

type Anclaje = "start" | "middle" | "end";

function Etiqueta({
  x,
  y,
  children,
  anchor = "end",
}: {
  x: number;
  y: number;
  children: React.ReactNode;
  anchor?: Anclaje;
}) {
  return (
    <text x={x} y={y} textAnchor={anchor} fill="var(--tinta-tenue)" fontSize={10} fontFamily="var(--mono)">
      {children}
    </text>
  );
}

export function Figura({
  titulo,
  lee,
  alto = 220,
  children,
}: {
  titulo: string;
  lee: string;
  alto?: number;
  children: React.ReactNode;
}) {
  return (
    <figure style={{ margin: "0 0 30px" }}>
      <figcaption
        style={{
          fontFamily: "var(--mono)",
          fontSize: 10.5,
          letterSpacing: "0.14em",
          textTransform: "uppercase",
          color: "var(--tinta-tenue)",
          marginBottom: 8,
        }}
      >
        {titulo}
      </figcaption>
      <svg viewBox={`0 0 ${W} ${alto}`} width="100%" style={{ display: "block", overflow: "visible" }}>
        {children}
      </svg>
      <div style={{ fontSize: 12, color: "var(--tinta-suave)", lineHeight: 1.55, marginTop: 8 }}>{lee}</div>
    </figure>
  );
}

/* ---------------------------------------------------------------- la brecha */

/**
 * El dato A1 del proyecto: la distancia entre lo que la proyección oficial
 * asume (cumplimiento total, plana) y lo que sale de dejar decidir a los
 * agentes. El área sombreada ENTRE las dos líneas es literalmente la brecha.
 */
export function GraficaBrecha({ rondas }: { rondas: RondaRegistrada[] }) {
  const alto = 240;
  if (rondas.length < 2) return null;
  const oficial = rondas[0].tasa_informalidad;
  const vals = rondas.map((r) => r.tasa_informalidad);
  const hayBanda = rondas.some((r) => !r.banda_degenerada);
  const todos = [...vals, oficial, ...rondas.flatMap((r) => (r.banda_degenerada ? [] : [r.banda_p10, r.banda_p90]))];
  const pad = Math.max(0.01, (Math.max(...todos) - Math.min(...todos)) * 0.35);
  const lo = Math.min(...todos) - pad;
  const hi = Math.max(...todos) + pad;
  const x = (i: number) => M.l + (i / (rondas.length - 1)) * (W - M.l - M.r);
  const y = (v: number) => M.t + (1 - (v - lo) / (hi - lo || 1)) * (alto - M.t - M.b);

  const linea = vals.map((v, i) => `${i ? "L" : "M"}${x(i)},${y(v)}`).join(" ");
  const area =
    vals.map((v, i) => `${i ? "L" : "M"}${x(i)},${y(v)}`).join(" ") +
    ` L${x(vals.length - 1)},${y(oficial)} L${x(0)},${y(oficial)} Z`;
  const banda = hayBanda
    ? rondas.map((r, i) => `${i ? "L" : "M"}${x(i)},${y(r.banda_p90)}`).join(" ") +
      [...rondas.keys()].reverse().map((i) => `L${x(i)},${y(rondas[i].banda_p10)}`).join("") +
      "Z"
    : null;

  const brechaPp = (vals[vals.length - 1] - oficial) * 100;

  return (
    <Figura
      titulo="la brecha · proyección oficial contra lo que pasa"
      alto={alto}
      lee={`La línea punteada es lo que el modelo oficial asume: que todo el mundo cumple, para siempre. La línea llena es lo que resulta de dejar decidir a cada empresa con su propia caja. El área entre las dos es la brecha — ${brechaPp
        .toFixed(2)
        .replace(".", ",")} pp al cierre del horizonte.`}
    >
      {[hi, (hi + lo) / 2, lo].map((v, i) => (
        <g key={i}>
          <line x1={M.l} y1={y(v)} x2={W - M.r} y2={y(v)} stroke="var(--linea)" />
          <Etiqueta x={M.l - 8} y={y(v) + 3}>
            {pct(v)}
          </Etiqueta>
        </g>
      ))}
      <path d={area} fill="var(--azul)" opacity={0.14} />
      {banda && <path d={banda} fill="var(--azul)" opacity={0.12} />}
      <line
        x1={x(0)}
        y1={y(oficial)}
        x2={x(rondas.length - 1)}
        y2={y(oficial)}
        stroke="var(--tinta-tenue)"
        strokeDasharray="4 4"
        strokeWidth={1.2}
      />
      <path d={linea} fill="none" stroke="var(--azul-vivo)" strokeWidth={2.2} />
      {vals.map((v, i) => (
        <circle key={i} cx={x(i)} cy={y(v)} r={3.2} fill="var(--azul-vivo)" />
      ))}
      {rondas.map((r, i) => (
        <Etiqueta key={i} x={x(i)} y={alto - M.b + 16} anchor="middle">
          {r.ronda === 0 ? "decreto" : `T${r.ronda}`}
        </Etiqueta>
      ))}
    </Figura>
  );
}

/* ------------------------------------------------------------- la cascada */

/**
 * El MECANISMO del proyecto, en una figura: la capacidad de fiscalización es
 * fija, así que cuantos más evasores hay, menos probable es que a cada uno le
 * caiga la sanción — y eso induce más evasión. Si la línea de p(sanción) baja
 * mientras la de informalidad sube, la cascada está operando DENTRO del modelo.
 *
 * Ojo con el verbo: la cascada agregada es el mecanismo que el motor simula, no
 * un hallazgo del proyecto. `VALIDATION.md` la declara falsada contra el dato
 * observado (37,37 pp de error, signo contrario). La figura describe cómo se
 * mueve el modelo; no afirma que el mundo se mueva así.
 */
export function GraficaCascada({ rondas }: { rondas: RondaRegistrada[] }) {
  const alto = 220;
  if (rondas.length < 2) return null;
  const inf = rondas.map((r) => r.tasa_informalidad);
  const san = rondas.map((r) => r.prob_fiscalizacion);
  const x = (i: number) => M.l + (i / (rondas.length - 1)) * (W - M.l - M.r);
  const esc = (vs: number[]) => {
    const pad = Math.max(1e-4, (Math.max(...vs) - Math.min(...vs)) * 0.4);
    const lo = Math.min(...vs) - pad;
    const hi = Math.max(...vs) + pad;
    return (v: number) => M.t + (1 - (v - lo) / (hi - lo || 1)) * (alto - M.t - M.b);
  };
  const yI = esc(inf);
  const yS = esc(san);
  const dSan = (san[san.length - 1] - san[0]) * 100;

  return (
    <Figura
      titulo="la cascada · el mecanismo: más evasores, menos riesgo para cada uno"
      alto={alto}
      lee={`La capacidad de inspección es fija, así que la probabilidad de sanción es capacidad ÷ evasores. ${
        dSan < -0.001
          ? `Acá bajó ${Math.abs(dSan).toFixed(3).replace(".", ",")} pp mientras la informalidad subía: es la retroalimentación del modelo operando. Es el mecanismo que el motor simula, no un hallazgo verificado — contra el dato observado el backtest lo falsa (ver «dónde no hay que creerle»).`
          : "En esta corrida no se movió lo suficiente como para hablar de cascada, y así se reporta."
      }`}
    >
      <path
        d={inf.map((v, i) => `${i ? "L" : "M"}${x(i)},${yI(v)}`).join(" ")}
        fill="none"
        stroke="var(--azul-vivo)"
        strokeWidth={2.2}
      />
      <path
        d={san.map((v, i) => `${i ? "L" : "M"}${x(i)},${yS(v)}`).join(" ")}
        fill="none"
        stroke="var(--rojo)"
        strokeWidth={2.2}
        strokeDasharray="5 3"
      />
      {inf.map((v, i) => (
        <g key={i}>
          <circle cx={x(i)} cy={yI(v)} r={3} fill="var(--azul-vivo)" />
          <circle cx={x(i)} cy={yS(san[i])} r={3} fill="var(--rojo)" />
        </g>
      ))}
      <Etiqueta x={x(0) + 6} y={yI(inf[0]) - 10} anchor="start">
        informalidad {pct(inf[0])} → {pct(inf[inf.length - 1])}
      </Etiqueta>
      <Etiqueta x={x(0) + 6} y={yS(san[0]) + 18} anchor="start">
        p(sanción) {pct(san[0], 2)} → {pct(san[san.length - 1], 2)}
      </Etiqueta>
      {rondas.map((r, i) => (
        <Etiqueta key={i} x={x(i)} y={alto - M.b + 16} anchor="middle">
          {r.ronda === 0 ? "decreto" : `T${r.ronda}`}
        </Etiqueta>
      ))}
    </Figura>
  );
}

/* --------------------------------------------------- a quién le cae encima */

/**
 * El dato A3: la política no cae parejo. Barras por sector, ordenadas por
 * cuántos puntos porcentuales se movió su informalidad, con el tamaño de la
 * población afectada al lado. Es la figura que contesta "¿y a quién?".
 */
export function GraficaDistributiva({
  arquetipos,
  ultima,
}: {
  arquetipos: ArquetipoEstatico[];
  ultima: EventoRonda | null;
}) {
  if (!ultima) return null;
  const porSector = new Map<string, { peso: number; ini: number; fin: number }>();
  for (const a of arquetipos) {
    const e = ultima.estado_por_arquetipo[a.id];
    if (!e) continue;
    const g = porSector.get(a.sector) ?? { peso: 0, ini: 0, fin: 0 };
    g.peso += a.peso;
    g.ini += a.peso * a.fraccion_informal_inicial;
    g.fin += a.peso * e.fraccion_informal;
    porSector.set(a.sector, g);
  }
  const filas = [...porSector.entries()]
    .map(([sector, g]) => ({
      sector,
      peso: g.peso,
      ini: g.ini / g.peso,
      fin: g.fin / g.peso,
      delta: (g.fin / g.peso - g.ini / g.peso) * 100,
    }))
    .sort((a, b) => b.delta - a.delta);
  if (!filas.length) return null;

  const alto = 36 + filas.length * 26;
  const maxAbs = Math.max(0.5, ...filas.map((f) => Math.abs(f.delta)));
  const x0 = 210;
  const anchoBarra = W - x0 - 130;
  const ancho = (d: number) => (Math.abs(d) / maxAbs) * anchoBarra;

  const peor = filas[0];

  return (
    <Figura
      titulo="a quién le cae encima · cambio de informalidad por sector"
      alto={alto}
      lee={`El alza no cae parejo. ${nombreSector(peor.sector)} se lleva el golpe más fuerte: ${peor.delta
        .toFixed(2)
        .replace(".", ",")} pp sobre ${miles(peor.peso)} trabajadores. Un promedio de ciudad esconde exactamente esto.`}
    >
      {filas.map((f, i) => {
        const y = 16 + i * 26;
        return (
          <g key={f.sector}>
            <text x={x0 - 12} y={y + 11} textAnchor="end" fill="var(--tinta-suave)" fontSize={12}>
              {nombreSector(f.sector)}
            </text>
            <rect x={x0} y={y} width={Math.max(1.5, ancho(f.delta))} height={15} fill="var(--azul)" opacity={0.75} rx={2} />
            <text
              x={x0 + Math.max(1.5, ancho(f.delta)) + 8}
              y={y + 11}
              fill="var(--tinta)"
              fontSize={11}
              fontFamily="var(--mono)"
            >
              {f.delta >= 0 ? "+" : ""}
              {f.delta.toFixed(2).replace(".", ",")} pp
            </text>
            <text
              x={W}
              y={y + 11}
              textAnchor="end"
              fill="var(--tinta-tenue)"
              fontSize={10}
              fontFamily="var(--mono)"
            >
              {miles(f.peso)}
            </text>
          </g>
        );
      })}
    </Figura>
  );
}

/* --------------------------------------------- cómo se reparten las salidas */

/** Cómo se reparte la población entre estrategias, ronda a ronda. */
export function GraficaEstrategias({ rondas }: { rondas: RondaRegistrada[] }) {
  const conDatos = rondas.filter((r) => Object.keys(r.desglose_estrategias).length > 0);
  if (!conDatos.length) return null;
  const alto = 60 + conDatos.length * 46;
  const familias = [...new Set(conDatos.flatMap((r) => Object.keys(r.desglose_estrategias)))];
  const x0 = 78;
  const anchoBarra = W - x0 - 20;

  const ultima = conDatos[conDatos.length - 1];
  const dom = Object.entries(ultima.desglose_estrategias).sort((a, b) => b[1] - a[1])[0];

  return (
    <Figura
      titulo="cómo reaccionan · reparto de población por estrategia"
      alto={alto}
      lee={`Cada franja es la fracción de trabajadores cuya empresa eligió esa salida. Al cierre domina ${nombreEstrategia(
        dom[0]
      )} con ${pct(dom[1])} de la población. Ojo: por CONTEO de empresas el orden suele ser otro — muchas celdas chicas cumpliendo pesan poco en gente.`}
    >
      {conDatos.map((r, i) => {
        const y = 14 + i * 46;
        let acum = 0;
        return (
          <g key={r.ronda}>
            <text x={x0 - 12} y={y + 15} textAnchor="end" fill="var(--tinta-suave)" fontSize={11.5} fontFamily="var(--mono)">
              {r.ronda === 0 ? "decreto" : `T${r.ronda}`}
            </text>
            {Object.entries(r.desglose_estrategias)
              .sort((a, b) => b[1] - a[1])
              .map(([k, v]) => {
                const w = v * anchoBarra;
                const px = x0 + acum;
                acum += w;
                return (
                  <g key={k}>
                    <rect x={px} y={y} width={Math.max(0, w)} height={22} fill={COLOR_FAMILIA_CSS[k] ?? "var(--tinta-tenue)"} opacity={0.8} />
                    {v > 0.11 && (
                      <text x={px + 6} y={y + 15} fill="var(--fondo)" fontSize={10.5} fontFamily="var(--mono)">
                        {nombreEstrategia(k)} {pct(v)}
                      </text>
                    )}
                  </g>
                );
              })}
          </g>
        );
      })}
      <g>
        {familias.map((k, i) => (
          <g key={k} transform={`translate(${x0 + i * 118}, ${alto - 16})`}>
            <rect width={9} height={9} y={-8} fill={COLOR_FAMILIA_CSS[k] ?? "var(--tinta-tenue)"} opacity={0.8} />
            <text x={14} y={0} fill="var(--tinta-tenue)" fontSize={10} fontFamily="var(--mono)">
              {nombreEstrategia(k)}
            </text>
          </g>
        ))}
      </g>
    </Figura>
  );
}

/* --------------------------------------------------- el veto de factibilidad */

/** Cuántas propuestas rechazó el motor por ronda, y cuántas cayeron al fallback. */
export function GraficaVeto({ rondas }: { rondas: RondaRegistrada[] }) {
  const alto = 200;
  const conDatos = rondas.filter((r) => r.ronda > 0);
  if (!conDatos.length) return null;
  const maxV = Math.max(1, ...conDatos.map((r) => r.vetadas));
  const x0 = M.l;
  const paso = (W - x0 - M.r) / conDatos.length;
  const y = (v: number) => M.t + (1 - v / maxV) * (alto - M.t - M.b);
  const total = conDatos.reduce((s, r) => s + r.vetadas, 0);

  return (
    <Figura
      titulo="el veto de factibilidad · propuestas que la aritmética rechazó"
      alto={alto}
      lee={`${total} propuestas rechazadas en toda la corrida. Es la mitad del argumento del proyecto hecha número: la capa de decisión propone —incluso cosas que un economista no enumeraría— y el motor determinista mata lo que la caja de la empresa no permite. Sin este filtro, el resultado sería lo que el modelo imagine.`}
    >
      {[maxV, maxV / 2, 0].map((v, i) => (
        <g key={i}>
          <line x1={x0} y1={y(v)} x2={W - M.r} y2={y(v)} stroke="var(--linea)" />
          <Etiqueta x={x0 - 8} y={y(v) + 3}>
            {Math.round(v)}
          </Etiqueta>
        </g>
      ))}
      {conDatos.map((r, i) => {
        const cx = x0 + paso * (i + 0.5);
        const w = Math.min(72, paso * 0.42);
        return (
          <g key={r.ronda}>
            <rect x={cx - w / 2} y={y(r.vetadas)} width={w} height={y(0) - y(r.vetadas)} fill="var(--rojo)" opacity={0.72} rx={2} />
            <text x={cx} y={y(r.vetadas) - 7} textAnchor="middle" fill="var(--tinta)" fontSize={12} fontFamily="var(--mono)">
              {r.vetadas}
            </text>
            <Etiqueta x={cx} y={alto - M.b + 16} anchor="middle">
              T{r.ronda}
            </Etiqueta>
          </g>
        );
      })}
    </Figura>
  );
}

/* ------------------------------------------------- lo que pierde el trabajo */

/** Empleo y masa laboral relativa: dos formas de perder, no una. */
export function GraficaEmpleo({ rondas }: { rondas: RondaRegistrada[] }) {
  const alto = 210;
  if (rondas.length < 2) return null;
  const emp = rondas.map((r) => r.empleo_relativo);
  const ing = rondas.map((r) => r.ingreso_laboral_relativo);
  const todos = [...emp, ...ing, 1];
  const lo = Math.min(...todos) - 0.01;
  const hi = Math.max(...todos) + 0.005;
  const x = (i: number) => M.l + (i / (rondas.length - 1)) * (W - M.l - M.r);
  const y = (v: number) => M.t + (1 - (v - lo) / (hi - lo || 1)) * (alto - M.t - M.b);
  const perdidaEmp = (1 - emp[emp.length - 1]) * 100;
  const perdidaIng = (1 - ing[ing.length - 1]) * 100;

  return (
    <Figura
      titulo="lo que se paga en trabajo · empleo y masa laboral"
      alto={alto}
      lee={`Dos formas distintas de perder. El empleo cae ${perdidaEmp
        .toFixed(2)
        .replace(".", ",")}%, pero la masa laboral —empleo × jornada— cae ${perdidaIng
        .toFixed(2)
        .replace(".", ",")}%. La diferencia es gente que conserva el puesto con menos horas: el modelo oficial no ve esa pérdida porque no mira la jornada.`}
    >
      {[hi, (hi + lo) / 2, lo].map((v, i) => (
        <g key={i}>
          <line x1={M.l} y1={y(v)} x2={W - M.r} y2={y(v)} stroke="var(--linea)" />
          <Etiqueta x={M.l - 8} y={y(v) + 3}>
            {pct(v)}
          </Etiqueta>
        </g>
      ))}
      <path d={emp.map((v, i) => `${i ? "L" : "M"}${x(i)},${y(v)}`).join(" ")} fill="none" stroke="var(--tinta)" strokeWidth={2.2} />
      <path d={ing.map((v, i) => `${i ? "L" : "M"}${x(i)},${y(v)}`).join(" ")} fill="none" stroke="var(--ambar)" strokeWidth={2.2} strokeDasharray="5 3" />
      <Etiqueta x={x(rondas.length - 1)} y={y(emp[emp.length - 1]) - 9}>
        empleo
      </Etiqueta>
      <Etiqueta x={x(rondas.length - 1)} y={y(ing[ing.length - 1]) + 17}>
        masa laboral
      </Etiqueta>
      {rondas.map((r, i) => (
        <Etiqueta key={i} x={x(i)} y={alto - M.b + 16} anchor="middle">
          {r.ronda === 0 ? "decreto" : `T${r.ronda}`}
        </Etiqueta>
      ))}
    </Figura>
  );
}
