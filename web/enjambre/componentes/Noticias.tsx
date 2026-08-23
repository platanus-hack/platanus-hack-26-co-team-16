"use client";

// Las noticias de la corrida, como burbujas.
//
// Antes esto era un bloque editorial de 380 px anclado a la derecha que crecía
// con el largo del titular y de la cita del LLM. Ocupaba lienzo, competía con
// las cifras y solo mostraba la última ronda.
//
// Ahora cada ronda cerrada suelta una burbuja cuadrada arriba, donde no había
// nada que mostrar. Son chicas y se leen de un vistazo; si alguien quiere el
// detalle —la cita textual del motor, la celda protagonista— le da clic y la
// burbuja se abre. Cerradas no estorban; abiertas tampoco tapan el centro del
// enjambre.

import { useMemo, useState } from "react";
import { titular } from "@/lib/narrativa";
import { rondasVisibles, usarAlmacen } from "@/estado/simulacion";

export default function Noticias() {
  const rondas = usarAlmacen((s) => s.rondas);
  const rondaMostrada = usarAlmacen((s) => s.rondaMostrada);
  const [abierta, setAbierta] = useState<number | null>(null);

  // una noticia por ronda cerrada, no solo la última: `titular()` mira el
  // final del arreglo que se le pase, así que se le pasa cada prefijo.
  const notas = useMemo(() => {
    const vis = rondasVisibles({ rondas, rondaMostrada });
    const out: { ronda: number; nota: NonNullable<ReturnType<typeof titular>> }[] = [];
    for (let i = 1; i < vis.length; i++) {
      const nota = titular(vis.slice(0, i + 1));
      if (nota) out.push({ ronda: vis[i].contrato.ronda, nota });
    }
    return out;
  }, [rondas, rondaMostrada]);

  if (!notas.length) return null;

  return (
    <div
      className="panel panel--activo"
      style={{
        left: "50%",
        top: 26,
        transform: "translateX(-50%)",
        zIndex: 22,
        display: "flex",
        gap: 10,
        alignItems: "flex-start",
      }}
    >
      {notas.map(({ ronda, nota }) => {
        const esta = abierta === ronda;
        return (
          <div
            key={ronda}
            className="burbuja"
            onClick={() => setAbierta(esta ? null : ronda)}
            style={{ width: esta ? 340 : 186 }}
          >
            <div className="burbuja__ronda">ronda {ronda}</div>
            <div
              className="burbuja__titulo"
              style={esta ? undefined : { WebkitLineClamp: 3 }}
            >
              {nota.titulo}
            </div>
            {esta && nota.cita && <div className="burbuja__cita">“{nota.cita}”</div>}
            {esta && nota.atribucion && <div className="burbuja__pie">{nota.atribucion}</div>}
            {!esta && <div className="burbuja__mas">leer</div>}
          </div>
        );
      })}
    </div>
  );
}
