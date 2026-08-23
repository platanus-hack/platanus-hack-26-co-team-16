"use client";

// El reporte de la corrida. Es un documento de GRÁFICAS: seis figuras que
// cuentan el resultado, cada una con una línea que dice qué mirar, y arriba
// cuatro cifras y los hallazgos calculados sobre la corrida real.
//
// REGISTRO DEL TEXTO — la regla que ordena este archivo. El lector es alguien a
// quien le interesa qué pasa con el empleo en Bogotá, no cómo está construida
// la simulación. Entonces:
//   · se queda el vocabulario del tema (informalidad, formal/informal, sector,
//     indemnización, inspección, salario mínimo). El lector ya lo sabe y es lo
//     importante; traducirlo a «trabajadores sin contrato formal» pierde
//     precisión sin ganar nada.
//   · se va el vocabulario de la implementación (seed, paráfrasis, banda
//     degenerada, p10/p90, arquetipo, el veto, la capa LLM, rutas de archivo).
//     Lo que de eso hace falta para auditar vive al final, en el anexo.
// Los límites declarados NO se quitan: se dicen una vez, en limpio, en «Alcance
// del modelo», en vez de repetirse entre paréntesis dentro de cada figura.
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
import Procedencia from "@/componentes/Paneles/Procedencia";
import { registrarCorrida } from "@/lib/corrida";
import { miles, nombreEstrategia, pct, pp } from "@/lib/formato";
import { usarAlmacen } from "@/estado/simulacion";

// La app fija `overflow: hidden` en html/body para que el lienzo 3D ocupe la
// ventana. Al imprimir, esa caja raíz de alto fijo hace que Chrome pagine solo
// el primer viewport: medido, `documentElement.scrollHeight` = 720 contra
// `body.scrollHeight` = 3584, o sea el PDF salía cortado en la primera página.
// Va acá y no en `globals.css` porque el reporte es la única página que monta
// este componente: mismo efecto, sin tocar un archivo que usa toda la app.
const ESTILO_IMPRESION = `
@media print {
  html, body { height: auto !important; overflow: visible !important; }
  figure, .reporte section { break-inside: avoid; }
}
`;

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

/** Título de sección, con la misma regla tipográfica en todo el documento. */
function Titulo({ children }: { children: React.ReactNode }) {
  return (
    <h2
      className="kicker"
      style={{ borderBottom: "1px solid var(--linea)", paddingBottom: 6, marginBottom: 12 }}
    >
      {children}
    </h2>
  );
}

export default function Reporte() {
  const poblacion = usarAlmacen((s) => s.poblacion);
  const rondas = usarAlmacen((s) => s.rondas);
  const decisiones = usarAlmacen((s) => s.decisiones);
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
        gente > 0
          ? `El alza empuja a ${miles(gente)} personas a la informalidad. Es gente que hoy tiene ` +
              `contrato formal y termina sin él, y una proyección que da por hecho que todo el mundo ` +
              `cumple no la cuenta en ninguna parte.`
          : `El alza devuelve a ${miles(Math.abs(gente))} personas a un contrato formal.`
      );
    }
    const dSan = (ult.prob_fiscalizacion - r0.prob_fiscalizacion) * 100;
    if (dSan < -0.001) {
      out.push(
        `El riesgo de que la inspección le caiga a una empresa bajó ${Math.abs(dSan)
          .toFixed(3)
          .replace(".", ",")} pp sin que nadie recortara el presupuesto de inspección: hay más ` +
          `empresas informales repartiéndose la misma capacidad de vigilancia. Por eso la ` +
          `informalidad se alimenta a sí misma: cada empresa que se sale hace que salirse le ` +
          `cueste un poco menos a la siguiente.`
      );
    }
    const vetos = rs.reduce((s, r) => s + r.vetadas, 0);
    if (vetos > 0) {
      out.push(
        `${vetos} veces una empresa quiso hacer algo que no podía pagar y la simulación se lo ` +
          `impidió. Esa es la diferencia entre una simulación y una historia: la decisión tiene ` +
          `que caber en la caja de la empresa que la toma.`
      );
    }
    if (ult.fraccion_sin_salida > 0.001) {
      out.push(
        `Para el ${pct(ult.fraccion_sin_salida)} de la población ninguna salida alcanzaba: ni ` +
          `cumplir con el alza, ni recortar la jornada, ni informalizar. Son empresas a las que la ` +
          `aritmética no les deja ninguna opción, y la simulación lo reporta en vez de escoger una ` +
          `por ellas.`
      );
    }
    if (!ult.estabilizada) {
      out.push(
        `El resultado todavía se movía en la última ronda —${Math.abs(ult.movimiento_pp)
          .toFixed(2)
          .replace(".", ",")} pp—, así que la cifra final es una foto a mitad de camino, no un ` +
          `punto de llegada.`
      );
    }
    return out;
  }, [registro, poblacion]);

  // Lo que decidió cada empresa en ESTA corrida. El almacén ya lo trae entero;
  // acá solo se cuenta.
  //
  // El filtro de abajo no es cosmético. `justificacion` trae DOS cosas
  // distintas por el mismo campo: la razón que escribió la empresa, y el
  // diagnóstico que arma el motor cuando ninguna propuesta pasó («sin ninguna
  // opción factible tras 3 propuestas vetadas: el sobrecosto del periodo es …»,
  // con la misma cláusula repetida una vez por intento). Lo segundo no es una
  // razón: es la máquina hablando de sí misma, y citarlo era exactamente el
  // defecto que este reporte vino a corregir. Se descarta por prefijo conocido
  // y por repetición literal — un blob repetido contiene su propio arranque más
  // de una vez, y ninguna frase escrita por alguien hace eso.
  const queDecidieron = useMemo(() => {
    if (!decisiones.length) return null;
    const porFamilia = new Map<string, number>();
    for (const d of decisiones) {
      const k = d.dominante ?? "otra";
      porFamilia.set(k, (porFamilia.get(k) ?? 0) + 1);
    }
    // Los prefijos son literales de `behavior/contrato.py:196-205` y
    // `behavior/ablacion.py:155`, no heurística: es exactamente el texto que
    // arma el motor cuando la empresa no escribió nada.
    const MAQUINA =
      /^(regla fija:|tentativa de fallback|fallback tras \d+ propuestas vetadas|sin ninguna opción factible|sin razones registradas)/i;
    const esProsa = (j: string) => {
      if (j.length < 90 || j.length > 700 || MAQUINA.test(j)) return false;
      // El motor pega hasta 3 razones de veto con «; », y suelen ser la misma
      // frase repetida. Nadie escribe así.
      const partes = j.split("; ");
      return new Set(partes).size === partes.length;
    };
    const prosa = decisiones.map((d) => d.justificacion?.trim() ?? "").filter(esProsa);
    const mencionan = (re: RegExp) => prosa.filter((j) => re.test(j)).length;
    return {
      total: decisiones.length,
      reparto: [...porFamilia.entries()].sort((a, b) => b[1] - a[1]),
      citas: [...new Set(prosa)].sort((a, b) => b.length - a.length).slice(0, 2),
      nCitables: prosa.length,
      caja: mencionan(/caja|liquidez|flujo/i),
      despido: mencionan(/despid|indemniz/i),
    };
  }, [decisiones]);

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
  // Cuánta gente perdió el empleo. `empleo_relativo` puede pasarse de 1 por
  // redondeo, y un «-0» en portada se lee como un error.
  const despedidos = Math.max(0, Math.round(poblacion.peso_total * (1 - ult.empleo_relativo)));
  const nCorridas = registro.parafrasis;

  return (
    <main className="reporte">
      <style dangerouslySetInnerHTML={{ __html: ESTILO_IMPRESION }} />

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
          sobre el costo de tener un trabajador formal · {registro.rondas.length - 1} rondas de{" "}
          {poblacion.meses_por_ronda} meses · {miles(poblacion.peso_total)} trabajadores de Bogotá
          con empleador
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
        <Cifra valor={pp(registro.brecha_pp)} etiqueta="brecha contra el escenario sin adaptación" />
        {/* Decía «empleo que sobrevive · 100,0 %», y obligaba al lector a
            invertir la cifra para entender que nadie fue despedido. La cuenta
            de despidos lo dice directo, y engancha con «Alcance del modelo»,
            que explica por qué la simulación casi no despide. */}
        <Cifra
          valor={miles(despedidos)}
          etiqueta="despidos en toda la simulación"
          color={despedidos > 0 ? "var(--rojo)" : undefined}
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

      {/* Lo que decide cada empresa, y por qué, es lo más valioso que produce
          esta simulación y hasta ahora no aparecía en el reporte. Son dos
          bloques y están separados a propósito: arriba lo que hizo la corrida
          que el lector acaba de ver, abajo el análisis de las 518 decisiones
          del modelo de lenguaje, que es material de otra corrida y se rotula
          como tal. Mezclarlos sería atribuirle a esta corrida cifras que no
          produjo. */}
      <section style={{ marginTop: 40, breakInside: "avoid" }}>
        <Titulo>qué decidieron las empresas, y por qué</Titulo>

        {queDecidieron && (
          <>
            <p style={{ fontSize: 13, lineHeight: 1.7, color: "var(--tinta-suave)" }}>
              Se tomaron <strong>{miles(queDecidieron.total)} decisiones</strong> en total
              {nCorridas != null && nCorridas > 1 && ` — la ciudad se corrió ${nCorridas} veces`}. Cada
              una es un grupo de empresas del mismo sector y tamaño escogiendo qué hacer con el alza:
            </p>
            <ul
              style={{
                listStyle: "none",
                padding: 0,
                margin: "12px 0 0",
                display: "flex",
                flexWrap: "wrap",
                gap: "6px 22px",
                fontSize: 13,
              }}
            >
              {queDecidieron.reparto.map(([k, n]) => (
                <li key={k} style={{ fontFamily: "var(--mono)", color: "var(--tinta-suave)" }}>
                  <strong style={{ color: "var(--tinta)" }}>{nombreEstrategia(k)}</strong> {n} (
                  {pct(n / queDecidieron.total)})
                </li>
              ))}
            </ul>

            {queDecidieron.citas.length > 0 ? (
              <>
                <p style={{ fontSize: 13, lineHeight: 1.7, color: "var(--tinta-suave)", marginTop: 16 }}>
                  Y estas son razones que escribieron, textuales:
                </p>
                <ul style={{ listStyle: "none", padding: 0, margin: "10px 0 0" }}>
                  {queDecidieron.citas.map((c, i) => (
                    <li
                      key={i}
                      style={{
                        fontFamily: "var(--serif)",
                        fontSize: 14,
                        lineHeight: 1.6,
                        color: "var(--tinta)",
                        borderLeft: "2px solid var(--linea)",
                        paddingLeft: 14,
                        marginBottom: 10,
                      }}
                    >
                      «{c}»
                    </li>
                  ))}
                </ul>
                {queDecidieron.caja > 0 && (
                  <p style={{ fontSize: 13, lineHeight: 1.7, color: "var(--tinta-suave)", marginTop: 10 }}>
                    De las {miles(queDecidieron.nCitables)} razones escritas en esta corrida,{" "}
                    <strong style={{ color: "var(--tinta)" }}>{queDecidieron.caja}</strong> deciden
                    mirando la caja disponible
                    {queDecidieron.despido > 0 && (
                      <>
                        {" "}y <strong style={{ color: "var(--tinta)" }}>{queDecidieron.despido}</strong>{" "}
                        mencionan el despido o la indemnización
                      </>
                    )}
                    .
                  </p>
                )}
              </>
            ) : (
              <p style={{ fontSize: 13, lineHeight: 1.7, color: "var(--tinta-tenue)", marginTop: 14 }}>
                Esta corrida usó reglas fijas en vez del modelo de lenguaje, así que las empresas no
                escribieron una razón: compararon el costo formal contra el informal y escogieron el
                menor. Las razones escritas del bloque de abajo salen de la corrida completa.
              </p>
            )}
          </>
        )}

        <div
          style={{
            marginTop: 22,
            paddingTop: 16,
            borderTop: "1px solid var(--linea)",
            fontSize: 13,
            lineHeight: 1.7,
            color: "var(--tinta-suave)",
          }}
        >
          <div className="kicker" style={{ marginBottom: 8 }}>
            las 518 decisiones de la corrida completa · 23-ago-2026
          </div>
          <p>
            Sobre la corrida grande, en la que cada empresa razonó por escrito, se leyeron las 518
            decisiones una por una. Lo que salió es lo más contundente que produce este proyecto:
          </p>
          <ul style={{ paddingLeft: 18, marginTop: 10 }}>
            <li>
              <strong style={{ color: "var(--tinta)" }}>211 de 518 (40,7 %)</strong> pasaron parte de
              su planta a la informalidad. <strong style={{ color: "var(--tinta)" }}>Solo 1 despidió.</strong>
            </li>
            <li>
              <strong style={{ color: "var(--tinta)" }}>242 (47 %)</strong> consideraron despedir y lo
              descartaron: no tenían con qué pagar la indemnización. No lo ignoraron, lo evaluaron y
              no les alcanzó.
            </li>
            <li>
              <strong style={{ color: "var(--tinta)" }}>361 (70 %)</strong> deciden mirando cuánta
              plata tienen disponible. La única que sí despidió botó exactamente a los 17
              trabajadores que su caja alcanzaba a indemnizar, ni uno más.
            </li>
          </ul>
          <p style={{ marginTop: 10 }}>
            Dicho corto: <strong style={{ color: "var(--tinta)" }}>el alza no se paga con despidos
            porque despedir cuesta plata por adelantado e informalizar no cuesta nada hoy</strong>.
            Lo que decide no es el criterio del empresario, es su caja.
          </p>
        </div>
      </section>

      <section style={{ marginTop: 42 }}>
        <GraficaBrecha rondas={registro.rondas} />
        <GraficaDistributiva arquetipos={poblacion.arquetipos} ultima={ultimaCruda} />
        <GraficaCascada rondas={registro.rondas} />
        <GraficaEstrategias rondas={registro.rondas} />
        <GraficaEmpleo rondas={registro.rondas} />
        <GraficaVeto rondas={registro.rondas} />
      </section>

      {/* El rótulo anterior invitaba al lector a desconfiar del reporte. El
          contenido es el mejor activo del proyecto —límites escritos antes de
          que los pregunten— pero ese nombre sonaba a confesión y hacía que la
          sección se leyera como una disculpa en vez de como rigor. Cambia el
          nombre; los límites se quedan enteros, y ahora en el mismo idioma que
          el resto del documento. */}
      <section style={{ marginTop: 34, breakInside: "avoid" }}>
        <Titulo>alcance del modelo · qué mide y qué no</Titulo>
        <ul style={{ paddingLeft: 18, fontSize: 12.5, lineHeight: 1.75, color: "var(--tinta-suave)" }}>
          <li>
            <strong>Esto no es un pronóstico.</strong> Corrimos la simulación sobre un año que ya
            había pasado, para ver si le atinaba, y se equivocó por 37,37 pp <em>y en la dirección
            contraria</em>: dijo que la informalidad en Bogotá subiría 33,3 pp entre 2025 y 2026, y
            en realidad bajó 4,07. Apostar a que un año se parece al anterior le gana ocho veces.
            Lo publicamos porque lo que este proyecto muestra es <em>cómo</em> reaccionan las
            empresas y cómo esa reacción se retroalimenta; la cifra agregada de informalidad no
            está validada y no hay que usarla como predicción.
          </li>
          <li>
            <strong>Por qué casi no hay despidos.</strong> No es un error del resultado, es lo que
            se le pidió simular: a cada empresa se le dice que sus ventas y su producción no
            cambian, y que despedir exige pagar la indemnización de inmediato mientras informalizar
            no cuesta nada hoy. Con la demanda fija, despedir solo destruye producción y encima
            cuesta caja, así que casi nunca es la mejor jugada. Que un alza del mínimo se pague en
            informalidad y no en despidos <strong>es coherente con lo que se observa en Colombia</strong>;
            lo que no sería honesto es presentarlo como un descubrimiento de la simulación, porque
            estaba decidido por esas dos condiciones antes de empezar.
          </li>
          <li>
            <strong>Subir precios no mueve el resultado.</strong> Es una de las salidas más elegidas,
            pero en esta simulación los clientes no se van cuando suben los precios, porque no hay
            respuesta de la demanda. Es lo que la empresa <em>dice</em> que haría, no inflación
            medida, y no cambia ninguna de las cifras de portada.
          </li>
          <li>
            <strong>No es un modelo de toda la economía.</strong> La inflación, el crecimiento y la
            tasa de cambio entran como datos del mundo real. La simulación no los predice ni los
            mueve.
          </li>
          <li>
            <strong>Son {registro.rondas.length - 1} rondas de decisiones, no un punto de equilibrio.</strong>{" "}
            En cada ronda las empresas ven qué hicieron las demás y vuelven a decidir
            {ult.estabilizada
              ? ". El resultado dejó de moverse antes de terminar"
              : ", y en la última ronda el resultado todavía se movía"}
            .
          </li>
          <li>
            <strong>Cubre a quien tiene empleador.</strong> El {pct(poblacion.cuenta_propia.fraccion_cuenta_propia)}{" "}
            de los ocupados de Bogotá que trabaja por cuenta propia ({miles(poblacion.cuenta_propia.peso_cuenta_propia)}{" "}
            personas) queda fuera: no tiene a quién despedir ni a quién informalizar.
          </li>
          <li>
            <strong>Cada punto del mapa es un grupo de empresas</strong> del mismo sector y tamaño,
            no una empresa concreta, y dónde está en la pantalla no significa nada geográfico.
          </li>
          <li>
            <strong>De dónde sale el rango.</strong>{" "}
            {ult.banda_degenerada
              ? `Esta corrida se hizo una sola vez, así que hay un número y no un rango. ` +
                `Cuando la ciudad se corre varias veces, publicamos el valor de en medio y la ` +
                `distancia entre la corrida más baja y la más alta.`
              : `Corremos la misma ciudad ${nCorridas ?? "varias"} veces y publicamos el valor de en ` +
                `medio. La franja alrededor de la línea es la distancia entre la corrida más baja y ` +
                `la más alta — con tan pocas corridas es literalmente el mínimo y el máximo, no un ` +
                `intervalo de confianza estadístico.`}
          </li>
        </ul>
      </section>

      {/* P9 · procedencia. Estaba antes de los límites, y es el bloque más
          técnico del documento: nombra archivos y decisiones de arquitectura.
          Baja al final, de anexo: quien quiera auditar de dónde sale cada cifra
          lo encuentra, y quien solo quiere leer el reporte ya lo leyó entero.
          El componente es de otra zona y no se toca — solo se mueve. */}
      <section style={{ marginTop: 40, breakInside: "avoid" }}>
        <Titulo>anexo · de dónde sale cada cifra</Titulo>
        <Procedencia forzarAbierto />
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
        La población sale de los microdatos de la Gran Encuesta Integrada de Hogares del DANE: son
        personas reales anonimizadas, no perfiles inventados. La informalidad de partida de esta
        población —{miles(poblacion.peso_total)} empleados de firma, que son los que el modelo mueve—
        es {pct(poblacion.tasa_informalidad_observada)}, y es de donde arranca la ronda 0.
        {poblacion.tasa_informalidad_total_ciudad !== undefined && (
          <>
            {" "}La de Bogotá entera es {pct(poblacion.tasa_informalidad_total_ciudad)}, más alta porque
            incluye al cuenta propia, que esta grilla no cubre. Son dos denominadores distintos y no
            se comparan entre sí.
          </>
        )}{" "}
        Piso salarial anterior {miles(poblacion.piso_salarial_anterior)} COP/mes.
        <br />
        Ficha técnica: {registro.n_arquetipos ?? "—"} celdas empleadoras · seed {registro.seed} ·
        modo {registro.modo}
        {registro.parafrasis != null && ` · ${registro.parafrasis} paráfrasis`}
        {registro.gasto_usd != null && ` · $${registro.gasto_usd.toFixed(2)} USD`}
        <br />
        Generado el {new Date(registro.ts).toLocaleString("es-CO")} · HIVE
      </footer>
    </main>
  );
}
