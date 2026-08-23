"use client";

// El reporte de la corrida: todo lo que se sacó del lienzo para que la
// simulación se pudiera ver, más la procedencia de cada cifra.
//
// SE IMPRIME, NO SE DESCARGA. El botón llama a `window.print()` y el navegador
// genera el PDF. Es a propósito: jsPDF, pdfmake y react-pdf son dependencias
// nuevas, y `AGENTS.md` congela dependencias nuevas en el feature freeze. Una
// hoja de estilo de impresión cuesta cero y además deja el informe como página
// compartible, no solo como archivo.
//
// Lee del almacén, que es un singleton de módulo: sobrevive la navegación de
// cliente desde la simulación. Un refresco directo sobre /reporte lo pierde, y
// entonces la página lo dice en vez de mostrar una hoja vacía.

import Link from "next/link";
import { useMemo } from "react";
import Procedencia from "@/componentes/Paneles/Procedencia";
import { registrarCorrida } from "@/lib/corrida";
import { copMes, miles, nombreEstrategia, nombreSector, pct, pp } from "@/lib/formato";
import { usarAlmacen } from "@/estado/simulacion";

function Seccion({ titulo, children }: { titulo: string; children: React.ReactNode }) {
  return (
    <section style={{ marginTop: 34, breakInside: "avoid" }}>
      <h2
        style={{
          fontFamily: "var(--mono)",
          fontSize: 11,
          letterSpacing: "0.18em",
          textTransform: "uppercase",
          color: "var(--tinta-tenue)",
          borderBottom: "1px solid var(--linea)",
          paddingBottom: 6,
          marginBottom: 14,
        }}
      >
        {titulo}
      </h2>
      {children}
    </section>
  );
}

const TD: React.CSSProperties = {
  padding: "5px 10px 5px 0",
  fontSize: 12.5,
  borderBottom: "1px solid var(--linea)",
  verticalAlign: "top",
};
const TH: React.CSSProperties = {
  ...TD,
  fontFamily: "var(--mono)",
  fontSize: 10,
  letterSpacing: "0.08em",
  textTransform: "uppercase",
  color: "var(--tinta-tenue)",
  textAlign: "left",
};

export default function Reporte() {
  const poblacion = usarAlmacen((s) => s.poblacion);
  const rondas = usarAlmacen((s) => s.rondas);
  const registro = useMemo(() => registrarCorrida(), []);

  if (!registro || !poblacion) {
    return (
      <main style={{ padding: 60, maxWidth: 700, margin: "0 auto" }}>
        <h1 className="cifra" style={{ fontSize: 30 }}>
          No hay una corrida en memoria
        </h1>
        <p style={{ marginTop: 14, color: "var(--tinta-suave)", lineHeight: 1.6 }}>
          El reporte se arma con la corrida que está abierta en la simulación. Si llegaste acá por
          un enlace directo o recargaste la página, corre una simulación y vuelve desde el botón del
          final.
        </p>
        <Link href="/" className="boton" style={{ display: "inline-block", marginTop: 26 }}>
          Ir a la simulación
        </Link>
      </main>
    );
  }

  const r0 = registro.rondas[0];
  const ult = registro.rondas[registro.rondas.length - 1];
  const ultimaRondaCruda = rondas[rondas.length - 1];

  // las celdas ordenadas por cuánta gente movieron: es el orden en que un
  // lector quiere leerlas, no el alfabético
  const celdas = useMemo(() => {
    if (!ultimaRondaCruda) return [];
    return [...poblacion.arquetipos]
      .map((a) => {
        const e = ultimaRondaCruda.estado_por_arquetipo[a.id];
        const res = ultimaRondaCruda.por_arquetipo[a.id];
        const dInf = e ? e.fraccion_informal - a.fraccion_informal_inicial : 0;
        const dEmp = e ? 1 - e.fraccion_empleada : 0;
        return { a, e, res, afectados: a.peso * (Math.max(0, dInf) + Math.max(0, dEmp)) };
      })
      .sort((x, y) => y.afectados - x.afectados);
  }, [poblacion, ultimaRondaCruda]);

  return (
    <main className="reporte">
      <div className="reporte__acciones no-imprimir">
        <Link href="/" className="boton" style={{ padding: "10px 18px", fontSize: 11 }}>
          ← volver
        </Link>
        <button
          className="boton boton--primario"
          style={{ padding: "10px 18px", fontSize: 11 }}
          onClick={() => window.print()}
        >
          Descargar PDF
        </button>
      </div>

      <header>
        <div className="kicker">HIVE · reporte de corrida</div>
        <h1 className="cifra" style={{ fontSize: 34, lineHeight: 1.1, marginTop: 10 }}>
          Alza del salario mínimo de{" "}
          <span style={{ color: "var(--azul-vivo)" }}>
            +{registro.aumento_pct.toFixed(1).replace(".", ",")} %
          </span>
        </h1>
        <p style={{ marginTop: 10, color: "var(--tinta-suave)", fontSize: 13.5, lineHeight: 1.6 }}>
          Simulación de cumplimiento sobre el mercado laboral de Bogotá. La población se instancia
          desde personas reales anonimizadas de la GEIH (DANE); un motor determinista veta las
          reacciones imposibles que propone la capa de decisión.
        </p>
      </header>

      <Seccion titulo="parámetros de la corrida">
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <tbody>
            {[
              ["alza simulada", `${registro.aumento_pct.toFixed(1).replace(".", ",")} %`],
              [
                "modo",
                registro.modo === "reglas"
                  ? "reglas · ablación determinista, sin LLM"
                  : "llm · decisiones del modelo, vetadas por el motor",
              ],
              ["seed", String(registro.seed)],
              ["celdas empleadoras", registro.n_arquetipos ? String(registro.n_arquetipos) : "—"],
              [
                "cobertura del LLM",
                registro.cobertura != null ? pct(registro.cobertura) : "—",
              ],
              ["paráfrasis por celda", registro.parafrasis != null ? String(registro.parafrasis) : "—"],
              ["rondas", `${registro.rondas.length} · 1 ronda = ${poblacion.meses_por_ronda} meses`],
              ["piso salarial anterior", copMes(poblacion.piso_salarial_anterior)],
              ["informalidad observada (GEIH)", pct(poblacion.tasa_informalidad_observada)],
              ["ocupados expandidos", miles(poblacion.ocupados_expandidos)],
              [
                "cuenta propia fuera de la grilla",
                `${miles(poblacion.cuenta_propia.peso_cuenta_propia)} personas · ${pct(
                  poblacion.cuenta_propia.fraccion_cuenta_propia
                )} de los ocupados`,
              ],
              [
                "costo y duración",
                `${registro.segundos?.toFixed(1).replace(".", ",") ?? "—"} s · ${
                  registro.llamadas_api ?? 0
                } llamadas · $${(registro.gasto_usd ?? 0).toFixed(2)} USD`,
              ],
            ].map(([k, v]) => (
              <tr key={k}>
                <th style={{ ...TH, width: 260 }}>{k}</th>
                <td style={TD}>{v}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Seccion>

      <Seccion titulo="el resultado">
        <div style={{ display: "flex", gap: 40, flexWrap: "wrap" }}>
          {[
            ["informalidad final", pct(ult.tasa_informalidad)],
            ["proyección oficial (ronda 0)", pct(r0.tasa_informalidad)],
            ["brecha", pp(registro.brecha_pp)],
            ["empleo relativo", pct(ult.empleo_relativo)],
          ].map(([k, v]) => (
            <div key={k}>
              <div className="kicker" style={{ fontSize: 9.5 }}>
                {k}
              </div>
              <div className="cifra" style={{ fontSize: 30, marginTop: 4 }}>
                {v}
              </div>
            </div>
          ))}
        </div>
        <p style={{ marginTop: 16, fontSize: 12.5, color: "var(--tinta-suave)", lineHeight: 1.6 }}>
          La brecha es la distancia entre la proyección oficial —que asume cumplimiento total— y lo
          que resulta de dejar decidir a los agentes. {ult.estabilizada
            ? "El resultado se estabilizó dentro del horizonte simulado."
            : "El resultado NO se estabilizó dentro del horizonte simulado: la última ronda todavía se movía."}
        </p>
      </Seccion>

      <Seccion titulo="ronda por ronda">
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr>
              {["ronda", "informalidad", "p(sanción)", "empleo", "masa laboral", "fallback", "sin salida", "vetos"].map(
                (h) => (
                  <th key={h} style={TH}>
                    {h}
                  </th>
                )
              )}
            </tr>
          </thead>
          <tbody>
            {registro.rondas.map((r) => (
              <tr key={r.ronda}>
                <td style={TD}>{r.ronda === 0 ? "0 · oficial" : `${r.ronda}`}</td>
                <td style={TD}>
                  {pct(r.tasa_informalidad)}
                  {!r.banda_degenerada && (
                    <span style={{ color: "var(--tinta-tenue)" }}>
                      {" "}
                      [{pct(r.banda_p10)}–{pct(r.banda_p90)}]
                    </span>
                  )}
                </td>
                <td style={TD}>{pct(r.prob_fiscalizacion, 2)}</td>
                <td style={TD}>{pct(r.empleo_relativo)}</td>
                <td style={TD}>{pct(r.ingreso_laboral_relativo)}</td>
                <td style={TD}>{pct(r.fraccion_fallback)}</td>
                <td style={TD}>{pct(r.fraccion_sin_salida)}</td>
                <td style={TD}>{r.vetadas}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <p style={{ marginTop: 12, fontSize: 11.5, color: "var(--tinta-tenue)", lineHeight: 1.6 }}>
          <strong>p(sanción)</strong> es fiscalización endógena: capacidad fija dividida por el
          universo de evasores. Es el mecanismo de la cascada — más evasores bajan el riesgo de cada
          uno. <strong>Fallback</strong> es la fracción de población cuya decisión terminó en la
          salida de emergencia porque ninguna propuesta pasó el veto; el umbral de alarma declarado
          por el proyecto es 5%. <strong>Sin salida</strong> es población para la que NO existía
          ninguna opción factible: es un resultado del modelo, no un error. La banda entre corchetes
          solo aparece cuando hubo más de una paráfrasis.
        </p>
      </Seccion>

      <Seccion titulo="reparto de estrategias · última ronda">
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr>
              {["estrategia", "población", "celdas"].map((h) => (
                <th key={h} style={TH}>
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {Object.entries(ult.desglose_estrategias)
              .sort((a, b) => b[1] - a[1])
              .map(([k, v]) => (
                <tr key={k}>
                  <td style={TD}>{nombreEstrategia(k)}</td>
                  <td style={TD}>{pct(v)}</td>
                  <td style={TD}>{ult.desglose_estrategias_conteo[k] ?? 0}</td>
                </tr>
              ))}
          </tbody>
        </table>
        <p style={{ marginTop: 12, fontSize: 11.5, color: "var(--tinta-tenue)", lineHeight: 1.6 }}>
          Las dos columnas miden lo mismo de dos maneras y no coinciden: por población pesa a cuánta
          gente le pasa cada cosa, por celdas a cuántas empresas. Suelen contar historias distintas.
        </p>
      </Seccion>

      <Seccion titulo="detalle por celda · ordenado por gente afectada">
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr>
              {["celda", "trabajadores", "informalidad", "empleo", "decidió", "vetos"].map((h) => (
                <th key={h} style={TH}>
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {celdas.map(({ a, e, res }) => (
              <tr key={a.id}>
                <td style={TD}>
                  {nombreSector(a.sector)} · {a.tamano}
                  <div style={{ fontSize: 10.5, color: "var(--tinta-tenue)" }}>
                    tramo {a.tramo_ingreso} · mediana {copMes(a.ingreso_por_trabajador)}
                  </div>
                </td>
                <td style={TD}>{miles(a.peso)}</td>
                <td style={TD}>
                  {pct(a.fraccion_informal_inicial)} → {e ? pct(e.fraccion_informal) : "—"}
                </td>
                <td style={TD}>{e ? pct(e.fraccion_empleada) : "—"}</td>
                <td style={TD}>
                  {res?.dominante ? nombreEstrategia(res.dominante) : "—"}
                  {res?.justificacion && (
                    <div
                      style={{
                        fontFamily: "var(--serif)",
                        fontStyle: "italic",
                        fontSize: 11.5,
                        color: "var(--tinta-tenue)",
                        marginTop: 3,
                      }}
                    >
                      “{res.justificacion}”
                    </div>
                  )}
                </td>
                <td style={TD}>
                  {res?.vetadas ?? 0}
                  {res?.razones_veto?.length ? (
                    <div style={{ fontSize: 10.5, color: "var(--rojo)", marginTop: 3 }}>
                      {res.razones_veto.join(" · ")}
                    </div>
                  ) : null}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <p style={{ marginTop: 12, fontSize: 11.5, color: "var(--tinta-tenue)", lineHeight: 1.6 }}>
          Una celda es un grupo sector × tamaño de la GEIH, no una empresa individual. Las razones de
          veto son el texto literal del motor: son la voz de la aritmética rechazando lo que la plata
          no permite. El motor publica como máximo dos por celda.
        </p>
      </Seccion>

      <Seccion titulo="de dónde sale cada cifra">
        <div className="reporte__procedencia">
          <Procedencia forzarAbierto />
        </div>
      </Seccion>

      <Seccion titulo="lo que este modelo no hace">
        <ul style={{ paddingLeft: 18, fontSize: 12.5, lineHeight: 1.8, color: "var(--tinta-suave)" }}>
          <li>No es un modelo macro: inflación, crecimiento y tasa de cambio son datos exógenos.</li>
          <li>
            No prueba convergencia a equilibrio. Son {registro.rondas.length - 1} rondas de dinámica
            de mejor respuesta, y así se reporta.
          </li>
          <li>No optimiza políticas: evalúa la que se le dé, no busca la mejor.</li>
          <li>
            No cubre a los {pct(poblacion.cuenta_propia.fraccion_cuenta_propia)} de ocupados que
            trabajan por cuenta propia: el enjambre son celdas con empleador.
          </li>
          <li>
            El traslado a precios es lo que las firmas <em>declaran</em>, no inflación: no hay
            respuesta de demanda en el modelo.
          </li>
          <li>No entrega el futuro, entrega el rango, con el error del backtest publicado.</li>
        </ul>
      </Seccion>

      <footer
        style={{
          marginTop: 40,
          paddingTop: 14,
          borderTop: "1px solid var(--linea)",
          fontFamily: "var(--mono)",
          fontSize: 10,
          color: "var(--tinta-tenue)",
        }}
      >
        HIVE · generado el {new Date(registro.ts).toLocaleString("es-CO")} · seed {registro.seed} ·
        modo {registro.modo}
      </footer>
    </main>
  );
}
