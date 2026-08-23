"use client";

// El reporte de la corrida. Es un documento de GRÁFICAS: seis figuras que
// cuentan el resultado, cada una con una línea que dice qué mirar, y arriba
// cuatro cifras y tres hallazgos calculados sobre la corrida real.
//
// La versión anterior era casi todo prosa y tablas largas — informativa en el
// sentido de que los datos estaban, inútil en el sentido de que había que
// leerse mil palabras para sacar una conclusión. Lo que se conserva de texto es
// lo que un número no puede decir: los límites del modelo.
//
// SE IMPRIME, NO SE DESCARGA. `window.print()` y el navegador genera el PDF.
// jsPDF y compañía son dependencias nuevas y `AGENTS.md:111` las congela.

import Link from "next/link";
import { useMemo } from "react";
import {
  GraficaBrecha,
  GraficaCascada,
  GraficaDistributiva,
  GraficaEmpleo,
  GraficaEstrategias,
  GraficaVeto,
} from "@/componentes/reporte/Graficas";
import { registrarCorrida } from "@/lib/corrida";
import { miles, nombreEstrategia, pct, pp } from "@/lib/formato";
import { usarAlmacen } from "@/estado/simulacion";

function Cifra({ valor, etiqueta, color }: { valor: string; etiqueta: string; color?: string }) {
  return (
    <div>
      <div className="cifra" style={{ fontSize: 34, lineHeight: 1, color: color ?? "var(--tinta)" }}>
        {valor}
      </div>
      <div
        style={{
          fontFamily: "var(--mono)",
          fontSize: 9.5,
          letterSpacing: "0.08em",
          color: "var(--tinta-tenue)",
          marginTop: 6,
          maxWidth: 150,
          lineHeight: 1.45,
        }}
      >
        {etiqueta}
      </div>
    </div>
  );
}

export default function Reporte() {
  const poblacion = usarAlmacen((s) => s.poblacion);
  const rondas = usarAlmacen((s) => s.rondas);
  const registro = useMemo(() => registrarCorrida(), []);

  const hallazgos = useMemo(() => {
    if (!registro || !poblacion) return [];
    const rs = registro.rondas;
    const ult = rs[rs.length - 1];
    const r0 = rs[0];
    const out: string[] = [];

    const gente = Math.round(poblacion.peso_total * (ult.tasa_informalidad - r0.tasa_informalidad));
    if (Math.abs(gente) >= 1000) {
      out.push(
        `La proyección oficial se equivoca por ${miles(Math.abs(gente))} personas: es la gente que ` +
          `${gente > 0 ? "queda fuera de regla" : "vuelve a la regla"} y que un modelo de cumplimiento total no cuenta.`
      );
    }
    const dSan = (ult.prob_fiscalizacion - r0.prob_fiscalizacion) * 100;
    if (dSan < -0.001) {
      out.push(
        `El riesgo de sanción cayó ${Math.abs(dSan).toFixed(3).replace(".", ",")} pp sin que nadie ` +
          `tocara el presupuesto de inspección: más evasores repartidos sobre la misma capacidad. Esa es la cascada.`
      );
    }
    const vetos = rs.reduce((s, r) => s + r.vetadas, 0);
    if (vetos > 0) {
      out.push(
        `El motor rechazó ${vetos} propuestas por impagables. Sin ese filtro el resultado sería lo que ` +
          `el modelo de lenguaje imagine, no lo que la caja de las empresas permite.`
      );
    }
    if (ult.fraccion_sin_salida > 0.001) {
      out.push(
        `Para el ${pct(ult.fraccion_sin_salida)} de la población NO existía ninguna opción factible: ` +
          `ni cumplir, ni recortar, ni informalizar. Es un resultado del modelo, no un error.`
      );
    }
    if (!ult.estabilizada) {
      out.push(
        `El resultado no se estabilizó dentro del horizonte: la última ronda todavía se movía ` +
          `${Math.abs(ult.movimiento_pp).toFixed(2).replace(".", ",")} pp. El número final es una foto, no un punto de reposo.`
      );
    }
    return out;
  }, [registro, poblacion]);

  if (!registro || !poblacion) {
    return (
      <main style={{ padding: 60, maxWidth: 700, margin: "0 auto" }}>
        <h1 className="cifra" style={{ fontSize: 30 }}>
          No hay una corrida en memoria
        </h1>
        <p style={{ marginTop: 14, color: "var(--tinta-suave)", lineHeight: 1.6 }}>
          El reporte se arma con la corrida que está abierta en la simulación. Si llegaste por un
          enlace directo o recargaste la página, corre una simulación y entra desde el botón
          «ver reporte» del final.
        </p>
        <Link href="/" className="boton" style={{ display: "inline-block", marginTop: 26 }}>
          Ir a la simulación
        </Link>
      </main>
    );
  }

  const ult = registro.rondas[registro.rondas.length - 1];
  const ultimaCruda = rondas[rondas.length - 1] ?? null;
  const dominante = Object.entries(ult.desglose_estrategias).sort((a, b) => b[1] - a[1])[0];

  return (
    <main className="reporte">
      <div className="reporte__acciones no-imprimir">
        <Link href="/" className="boton" style={{ padding: "10px 18px", fontSize: 11 }}>
          ← volver
        </Link>
        <Link href="/laboratorio" className="boton" style={{ padding: "10px 18px", fontSize: 11 }}>
          laboratorio
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
        <div className="kicker">HIVE · alza del salario mínimo · Bogotá</div>
        <h1 className="cifra" style={{ fontSize: 38, lineHeight: 1.05, marginTop: 8 }}>
          +{registro.aumento_pct.toFixed(1).replace(".", ",")} %
        </h1>
        <div
          style={{
            fontFamily: "var(--mono)",
            fontSize: 10.5,
            color: "var(--tinta-tenue)",
            marginTop: 8,
            lineHeight: 1.6,
          }}
        >
          {registro.rondas.length - 1} rondas de {poblacion.meses_por_ronda} meses ·{" "}
          {registro.n_arquetipos ?? "—"} celdas empleadoras · {miles(poblacion.peso_total)} trabajadores ·
          seed {registro.seed} · modo {registro.modo}
          {registro.parafrasis != null && ` · ${registro.parafrasis} paráfrasis`}
          {registro.gasto_usd != null && ` · $${registro.gasto_usd.toFixed(2)} USD`}
        </div>
      </header>

      <section
        style={{
          display: "flex",
          gap: 40,
          flexWrap: "wrap",
          marginTop: 30,
          paddingTop: 24,
          borderTop: "1px solid var(--linea)",
        }}
      >
        <Cifra
          valor={pct(ult.tasa_informalidad)}
          etiqueta="informalidad al cierre"
          color="var(--azul-vivo)"
        />
        <Cifra valor={pp(registro.brecha_pp)} etiqueta="brecha contra la proyección oficial" />
        <Cifra
          valor={pct(ult.empleo_relativo)}
          etiqueta="empleo que sobrevive"
          color={ult.empleo_relativo < 0.98 ? "var(--rojo)" : undefined}
        />
        <Cifra
          valor={nombreEstrategia(dominante[0])}
          etiqueta={`salida dominante · ${pct(dominante[1])} de la población`}
        />
      </section>

      {hallazgos.length > 0 && (
        <section style={{ marginTop: 30 }}>
          <ul style={{ listStyle: "none", padding: 0, display: "flex", flexDirection: "column", gap: 10 }}>
            {hallazgos.map((h, i) => (
              <li
                key={i}
                style={{
                  fontSize: 14,
                  lineHeight: 1.55,
                  color: "var(--tinta)",
                  borderLeft: "2px solid var(--azul)",
                  paddingLeft: 14,
                }}
              >
                {h}
              </li>
            ))}
          </ul>
        </section>
      )}

      <section style={{ marginTop: 42 }}>
        <GraficaBrecha rondas={registro.rondas} />
        <GraficaDistributiva arquetipos={poblacion.arquetipos} ultima={ultimaCruda} />
        <GraficaCascada rondas={registro.rondas} />
        <GraficaEstrategias rondas={registro.rondas} />
        <GraficaEmpleo rondas={registro.rondas} />
        <GraficaVeto rondas={registro.rondas} />
      </section>

      <section style={{ marginTop: 10, breakInside: "avoid" }}>
        <h2
          className="kicker"
          style={{ borderBottom: "1px solid var(--linea)", paddingBottom: 6, marginBottom: 12 }}
        >
          dónde no hay que creerle
        </h2>
        <ul style={{ paddingLeft: 18, fontSize: 12.5, lineHeight: 1.75, color: "var(--tinta-suave)" }}>
          <li>
            No es un modelo macro. Inflación, crecimiento y tasa de cambio entran como datos
            observados, nunca como resultado.
          </li>
          <li>
            No prueba convergencia a equilibrio: son {registro.rondas.length - 1} rondas de mejor
            respuesta{ult.estabilizada ? "" : ", y la última todavía se movía"}.
          </li>
          <li>
            El enjambre son celdas con empleador. Los{" "}
            {pct(poblacion.cuenta_propia.fraccion_cuenta_propia)} de ocupados por cuenta propia (
            {miles(poblacion.cuenta_propia.peso_cuenta_propia)} personas) quedan fuera.
          </li>
          <li>
            El traslado a precios es lo que las firmas <em>declaran</em>, no inflación: no hay
            respuesta de demanda en el modelo.
          </li>
          <li>
            Una celda es un grupo sector × tamaño de la GEIH, no una empresa real. La posición en el
            mapa no es geográfica.
          </li>
          {ult.banda_degenerada && (
            <li>
              Esta corrida usó una sola paráfrasis, así que la banda sale degenerada: hay un número,
              no un rango. Con <code>parafrasis ≥ 2</code> el rango aparece.
            </li>
          )}
          <li>No entrega el futuro, entrega el rango, con el error del backtest publicado.</li>
        </ul>
      </section>

      <footer
        style={{
          marginTop: 34,
          paddingTop: 12,
          borderTop: "1px solid var(--linea)",
          fontFamily: "var(--mono)",
          fontSize: 9.5,
          color: "var(--tinta-tenue)",
          lineHeight: 1.6,
        }}
      >
        Población instanciada desde microdatos de la GEIH (DANE); informalidad observada de partida{" "}
        {pct(poblacion.tasa_informalidad_observada)}. Piso salarial anterior{" "}
        {miles(poblacion.piso_salarial_anterior)} COP/mes.
        <br />
        Generado el {new Date(registro.ts).toLocaleString("es-CO")} · HIVE
      </footer>
    </main>
  );
}
