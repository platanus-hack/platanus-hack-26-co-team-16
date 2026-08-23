"use client";

// El laboratorio: la evidencia que se acumula entre corridas en vez de
// perderse al cerrar la pestaña.
//
// Cada corrida terminada agrega una línea a `web/laboratorio/historico.jsonl`,
// que se commitea como cualquier otro artefacto del repo. Esta página lo lee y
// lo grafica. La curva del barrido de política no se calcula de una vez: se
// construye usando el simulador, una corrida a la vez.

import Link from "next/link";
import { useEffect, useState } from "react";
import {
  BarridoPolitica,
  CascadaPorRonda,
  Dispersion,
  VetosPorRonda,
} from "@/componentes/laboratorio/Graficas";
import { CorridaRegistrada } from "@/lib/corrida";
import { pct, pp } from "@/lib/formato";

export default function Laboratorio() {
  const [corridas, setCorridas] = useState<CorridaRegistrada[] | null>(null);
  const [falla, setFalla] = useState<string | null>(null);

  useEffect(() => {
    fetch("/laboratorio/registro")
      .then((r) => r.json())
      .then((j) => setCorridas(j.corridas ?? []))
      .catch((e) => setFalla(String(e?.message ?? e)));
  }, []);

  return (
    <main className="reporte">
      <div className="reporte__acciones no-imprimir">
        <Link href="/" className="boton" style={{ padding: "10px 18px", fontSize: 11 }}>
          ← volver a la simulación
        </Link>
      </div>

      <header>
        <div className="kicker">HIVE · laboratorio</div>
        <h1 className="cifra" style={{ fontSize: 34, lineHeight: 1.1, marginTop: 10 }}>
          Lo que sabemos después de {corridas?.length ?? "…"} corridas
        </h1>
        <p style={{ marginTop: 10, color: "var(--tinta-suave)", fontSize: 13.5, lineHeight: 1.6 }}>
          Cada corrida terminada se archiva en un histórico versionado del repo. Estas gráficas se
          arman con ese histórico: no son un resultado calculado de una vez, son evidencia que se
          acumula con el uso del simulador.
        </p>
      </header>

      {falla && (
        <p style={{ marginTop: 24, color: "var(--rojo)", fontFamily: "var(--mono)", fontSize: 12 }}>
          no se pudo leer el histórico: {falla}
        </p>
      )}

      {corridas !== null && corridas.length === 0 && (
        <section style={{ marginTop: 40 }}>
          <p style={{ color: "var(--tinta-suave)", fontSize: 13.5, lineHeight: 1.7 }}>
            El histórico está vacío. Corre una simulación completa y vuelve: al terminar la última
            ronda la corrida se archiva sola.
          </p>
          <p style={{ color: "var(--tinta-tenue)", fontSize: 12, lineHeight: 1.7, marginTop: 12 }}>
            Si estás viendo esto en el sitio desplegado y sigue vacío, es lo esperado: el sistema de
            archivos de un host serverless es de solo lectura, así que el histórico se llena
            corriendo el simulador en local y se publica por git.
          </p>
        </section>
      )}

      {corridas !== null && corridas.length > 0 && (
        <>
          <section
            style={{
              marginTop: 34,
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(420px, 1fr))",
              gap: 40,
            }}
          >
            <BarridoPolitica corridas={corridas} />
            <CascadaPorRonda corridas={corridas} />
            <VetosPorRonda corridas={corridas} />
            <Dispersion corridas={corridas} />
          </section>

          <section style={{ marginTop: 44 }}>
            <h2
              className="kicker"
              style={{ borderBottom: "1px solid var(--linea)", paddingBottom: 6, marginBottom: 12 }}
            >
              las corridas, una por una
            </h2>
            <div style={{ overflowX: "auto" }}>
              <table style={{ width: "100%", borderCollapse: "collapse", minWidth: 640 }}>
                <thead>
                  <tr>
                    {["cuándo", "alza", "modo", "paráf.", "informalidad", "brecha", "empleo", "vetos", "costo"].map(
                      (h) => (
                        <th
                          key={h}
                          style={{
                            fontFamily: "var(--mono)",
                            fontSize: 10,
                            letterSpacing: "0.08em",
                            textTransform: "uppercase",
                            color: "var(--tinta-tenue)",
                            textAlign: "left",
                            padding: "5px 10px 5px 0",
                            borderBottom: "1px solid var(--linea)",
                          }}
                        >
                          {h}
                        </th>
                      )
                    )}
                  </tr>
                </thead>
                <tbody>
                  {[...corridas].reverse().map((c, i) => (
                    <tr key={i}>
                      {[
                        new Date(c.ts).toLocaleString("es-CO", {
                          day: "2-digit",
                          month: "short",
                          hour: "2-digit",
                          minute: "2-digit",
                        }),
                        `${c.aumento_pct.toFixed(1).replace(".", ",")} %`,
                        c.modo,
                        c.parafrasis ?? "—",
                        pct(c.informalidad_final),
                        pp(c.brecha_pp),
                        pct(c.empleo_final),
                        c.rondas.reduce((s, r) => s + r.vetadas, 0),
                        c.gasto_usd != null ? `$${c.gasto_usd.toFixed(2)}` : "—",
                      ].map((v, j) => (
                        <td
                          key={j}
                          style={{
                            padding: "5px 10px 5px 0",
                            fontSize: 12.5,
                            borderBottom: "1px solid var(--linea)",
                            whiteSpace: "nowrap",
                          }}
                        >
                          {v}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          <section style={{ marginTop: 40 }}>
            <h2
              className="kicker"
              style={{ borderBottom: "1px solid var(--linea)", paddingBottom: 6, marginBottom: 12 }}
            >
              lo que este histórico todavía no puede responder
            </h2>
            <p style={{ fontSize: 12.5, color: "var(--tinta-suave)", lineHeight: 1.8 }}>
              Falta el <strong>histograma de tamaños de cascada</strong> — cuántos trabajadores
              arrastra cada evento de informalización. No es solo que no se registre: en este modelo
              la informalización ocurre a nivel de celda, promediada entre paráfrasis, y la cascada
              es indirecta (más evasores bajan p(sanción) para todos), no un contagio de celda a
              celda. Para poder medirla el motor tendría que guardar el delta por celda y por ronda,
              y sobre todo la <strong>fracción de firmas fuera de regla</strong>, que hoy se calcula
              y se descarta. Está pedido en <code>docs/VARIABLES-PENDIENTES.md</code> (B1 y B3).
            </p>
          </section>
        </>
      )}
    </main>
  );
}
