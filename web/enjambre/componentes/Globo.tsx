"use client";

// El globo de hover: datos REALES de la celda bajo el cursor. Solo campos que
// existen — sin contratados (el motor no contrata), sin utilidad ni
// productividad (no se modelan). Los flujos de la ronda salen de comparar los
// dos últimos estados emitidos.

import { useEffect, useState } from "react";
import { copMes, miles, nombreEstrategia, nombreSector, pct } from "@/lib/formato";
import { rondasVisibles, usarAlmacen } from "@/estado/simulacion";

export default function Globo() {
  const hover = usarAlmacen((s) => s.hover);
  const poblacion = usarAlmacen((s) => s.poblacion);
  const rondas = usarAlmacen((s) => s.rondas);
  const rondaMostrada = usarAlmacen((s) => s.rondaMostrada);
  const hoverTipo = usarAlmacen((s) => s.hoverTipo);
  const ppp = usarAlmacen((s) => s.personasPorPunto);
  const [xy, setXy] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const mover = (e: PointerEvent) => setXy({ x: e.clientX, y: e.clientY });
    window.addEventListener("pointermove", mover);
    return () => window.removeEventListener("pointermove", mover);
  }, []);

  if (!hover || !poblacion) return null;
  const a = poblacion.arquetipos.find((x) => x.id === hover);
  if (!a) return null;

  // S2-5: las rondas MOSTRADAS, no las que llegaron por el cable.
  const vis = rondasVisibles({ rondas, rondaMostrada });
  const ult = vis.length ? vis[vis.length - 1] : null;
  const prev = vis.length > 1 ? vis[vis.length - 2] : null;
  // Sin corrida solo existe el dato estático de la GEIH. `fraccion_empleada`
  // y `horas` en 1 NO son un resultado: son el punto de partida asumido, y hay
  // que decirlo — si no, el globo afirma "empleados hoy: 412.303" con la misma
  // tipografía que usa para las cifras que el motor sí calculó.
  const simulado = ult !== null;
  const e = ult?.estado_por_arquetipo[a.id] ?? {
    fraccion_informal: a.fraccion_informal_inicial,
    fraccion_empleada: 1,
    horas: 1,
  };
  const e0 = prev?.estado_por_arquetipo[a.id] ?? null;
  const res = ult?.por_arquetipo[a.id] ?? null;

  const empleados = a.peso * e.fraccion_empleada;
  const despedidosRonda = e0 ? Math.max(0, a.peso * (e0.fraccion_empleada - e.fraccion_empleada)) : 0;
  const informalizadosRonda = e0
    ? Math.max(0, a.peso * (e.fraccion_informal - e0.fraccion_informal))
    : 0;

  // P6: la nube que orbita la empresa son sus abejas, y responde otra
  // pregunta que el disco: no "cómo le va a esta empresa" sino "qué es cada
  // una de estas figuritas y qué le está pasando".
  const esPersonas = hoverTipo === "personas";
  const porAbeja = Math.max(1, Math.round(ppp));
  const nAbejas = Math.max(1, Math.round(a.peso / porAbeja));
  const nSinEmpleo = Math.round(nAbejas * (1 - e.fraccion_empleada));
  const nEmpleadas = nAbejas - nSinEmpleo;
  const nInformal = Math.round(nEmpleadas * e.fraccion_informal);
  const nJornada = e.horas < 0.999 ? Math.round((nEmpleadas - nInformal) * (1 - e.horas)) : 0;
  const nFormal = Math.max(0, nEmpleadas - nInformal - nJornada);

  const filas: [string, string, string?][] = esPersonas
    ? [
        ["cada abeja representa", `${miles(porAbeja)} personas`],
        ["abejas en esta empresa", `${nAbejas}`],
        ["· en regla", `${nFormal}`, "var(--verde)"],
        ...(nInformal > 0
          ? ([["· fuera de regla", `${nInformal}`, "var(--azul-vivo)"]] as [string, string, string?][])
          : []),
        ...(nJornada > 0
          ? ([["· con jornada recortada", `${nJornada}`, "var(--ambar)"]] as [string, string, string?][])
          : []),
        ...(nSinEmpleo > 0
          ? ([["· sin empleo", `${nSinEmpleo}`, "var(--rojo)"]] as [string, string, string?][])
          : []),
      ]
    : [
        ["trabajadores representados", miles(a.peso)],
        [
          simulado ? "empleados hoy" : "empleados (sin simular)",
          miles(empleados),
          despedidosRonda > 0 ? "var(--rojo)" : simulado ? undefined : "var(--tinta-tenue)",
        ],
      ];

  if (!esPersonas) {
    if (despedidosRonda >= 1) filas.push(["despedidos esta ronda", `−${miles(despedidosRonda)}`, "var(--rojo)"]);
    if (informalizadosRonda >= 1)
      filas.push(["informalizados esta ronda", `+${miles(informalizadosRonda)}`, "var(--azul-vivo)"]);
    filas.push(["informalidad interna", pct(e.fraccion_informal)]);
    if (e.horas < 0.999) filas.push(["jornada viva", pct(e.horas), "var(--ambar)"]);
    filas.push(
      ["salario mediano", copMes(a.ingreso_por_trabajador)],
      ["caja mensual de la celda", copMes(a.flujo_caja_mensual)],
      ["firmas representadas", miles(a.n_empresas)]
    );
  }

  const izquierda = xy.x > (typeof window !== "undefined" ? window.innerWidth : 1600) - 360;

  return (
    <div
      className="panel vidrio"
      style={{
        left: izquierda ? undefined : xy.x + 18,
        right: izquierda ? window.innerWidth - xy.x + 18 : undefined,
        top: Math.min(xy.y + 14, (typeof window !== "undefined" ? window.innerHeight : 900) - 340),
        width: 300,
        padding: "14px 16px",
        display: "flex",
        flexDirection: "column",
        gap: 8,
        zIndex: 40,
      }}
    >
      <div>
        <div className="kicker" style={{ fontSize: 10 }}>
          {esPersonas
            ? `sus trabajadores · ${a.tamano}`
            : `celda empleadora · ${a.tamano} · tramo ${a.tramo_ingreso}`}
        </div>
        <div className="cifra" style={{ fontSize: 19, marginTop: 3 }}>
          {nombreSector(a.sector)}
        </div>
      </div>
      <div>
        {filas.map(([k, v, color]) => (
          <div
            key={k}
            style={{
              display: "flex",
              justifyContent: "space-between",
              gap: 12,
              fontSize: 12,
              padding: "3px 0",
              color: "var(--tinta-suave)",
            }}
          >
            <span>{k}</span>
            <span style={{ fontFamily: "var(--mono)", color: color ?? "var(--tinta)" }}>{v}</span>
          </div>
        ))}
      </div>
      {res?.dominante && (
        <div style={{ borderTop: "1px solid var(--linea)", paddingTop: 8, display: "flex", flexDirection: "column", gap: 5 }}>
          <div style={{ fontFamily: "var(--mono)", fontSize: 11 }}>
            <span style={{ color: "var(--tinta-tenue)" }}>decidió · </span>
            <span style={{ color: "var(--tinta)" }}>{nombreEstrategia(res.dominante)}</span>
            {res.vetadas > 0 && <span style={{ color: "var(--rojo)" }}> · {res.vetadas} veto(s)</span>}
            {res.fallbacks > 0 && <span style={{ color: "var(--ambar)" }}> · fallback</span>}
          </div>
          {res.justificacion && (
            <div style={{ fontFamily: "var(--serif)", fontStyle: "italic", fontSize: 12.5, lineHeight: 1.4, color: "var(--tinta-suave)" }}>
              “{res.justificacion}”
            </div>
          )}
        </div>
      )}
      <div style={{ fontFamily: "var(--mono)", fontSize: 9.5, color: "var(--tinta-tenue)" }}>
        {!simulado
          ? "todavía sin simular: empleo y jornada son el punto de partida asumido, no un resultado"
          : esPersonas
            ? "el reparto sale de la tasa de la celda; qué abeja concreta cae en cuál es visual"
            : "sin contrataciones, utilidad ni productividad: el motor no las modela"}
      </div>
    </div>
  );
}
