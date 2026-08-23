"use client";

// El control de avance. La simulación se detiene al cerrar cada ronda y no
// sigue hasta que alguien la empuja: deja de ser una caja negra que se
// reproduce sola y pasa a ser algo que se mira ronda por ronda.
//
// La espera es real pero no es la del servidor: la corrida completa ya está en
// el buffer del cliente (la API no sabe pausar). Lo que se pausa es la
// REPRODUCCIÓN, y eso se dice sin adornos en el subtítulo cuando la corrida ya
// terminó de calcularse.

import { usarAlmacen } from "@/estado/simulacion";

export default function Continuar() {
  const pausado = usarAlmacen((s) => s.pausado);
  const setPausado = usarAlmacen((s) => s.setPausado);
  const rondaMostrada = usarAlmacen((s) => s.rondaMostrada);
  const rondas = usarAlmacen((s) => s.rondas);
  const poblacion = usarAlmacen((s) => s.poblacion);
  const conexion = usarAlmacen((s) => s.conexion);

  if (!pausado || !rondaMostrada) return null;

  const mostrada = rondaMostrada.contrato.ronda;
  const siguiente = mostrada + 1;
  const total = (poblacion?.rondas_totales ?? 4) - 1;
  if (siguiente > total) return null;

  // ¿la ronda siguiente ya llegó por el cable, o todavía la está calculando el
  // motor? Cambia lo que puede hacer el botón, así que cambia lo que dice.
  const yaLlego = rondas.length > rondas.indexOf(rondaMostrada) + 1;
  const murio = conexion === "error";
  if (murio) return null;

  return (
    <div
      className="panel panel--activo"
      style={{
        left: "50%",
        bottom: 108,
        transform: "translateX(-50%)",
        zIndex: 25,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: 8,
      }}
    >
      <button
        className="boton boton--primario aparecer"
        disabled={!yaLlego}
        style={{ padding: "15px 34px", fontSize: 12 }}
        onClick={() => setPausado(false)}
      >
        {yaLlego ? `Continuar con la ronda ${siguiente}` : `Calculando la ronda ${siguiente}…`}
      </button>
      <div style={{ fontFamily: "var(--mono)", fontSize: 10, color: "var(--tinta-tenue)" }}>
        {mostrada < 0
          ? "el punto de partida"
          : `ronda ${mostrada} de ${total} · la simulación no avanza sola`}
      </div>
    </div>
  );
}
