"use client";

// Las noticias de la corrida, como burbujas.
//
// Antes esto era un bloque editorial de 380 px anclado a la derecha que crecía
// con el largo del titular y de la cita del LLM. Ocupaba lienzo, competía con
// las cifras y solo mostraba la última ronda.
//
// Ahora cada ronda cerrada suelta una burbuja cuadrada arriba. Son chicas y se
// leen de un vistazo; si alguien quiere el detalle —la cita textual del motor,
// la celda protagonista— le da clic y la burbuja se abre.
//
// LA FILA VIVE EN UN CORREDOR ACOTADO (review de R2, menor 2). Antes estaba
// centrada en el viewport con `translateX(-50%)`, así que crecía hacia los dos
// lados y se metía debajo de `Titulo` (arriba a la izquierda) y `Hero` (arriba
// a la derecha). Con las 3 rondas y una burbuja abierta llegaba a 732 px y se
// comía el rótulo «MODO REGLAS (ablación)», que es justo el que no puede
// esconderse en una demo.
//
// Dos cambios lo cierran de raíz, y ninguno depende de adivinar el ancho del
// texto de los costados:
//
//   1. `left`/`right` fijos en `CORREDOR` en vez de centrado por transform. La
//      caja de la fila NO PUEDE cruzar esa frontera, mida lo que mida.
//   2. Las burbujas son flexibles (`flex: 1 1 0`, tope `ANCHO_BURBUJA`): si el
//      corredor se angosta, se angostan ellas en vez de desbordar. El titular
//      ya venía con clamp de 3 líneas, así que encoger no rompe nada.
//
// Y al abrirse, la burbuja crece HACIA ABAJO —se suelta el clamp y aparecen
// cita y atribución— en vez de empujar a sus vecinas. Abajo hay enjambre, que
// se puede tapar un momento; a los lados hay cifras que no.

import { useMemo, useState } from "react";
import { titular } from "@/lib/narrativa";
import { rondasVisibles, usarAlmacen } from "@/estado/simulacion";

/** Tope de ancho de cada burbuja, abierta o cerrada. Si el corredor no da,
 *  la burbuja encoge por debajo de esto. */
const ANCHO_BURBUJA = 176;

/** Cuánto se le reserva a CADA costado para los paneles de cifras. Medido en
 *  headless a 1440×900 con la corrida andando: `Titulo` llega a x≈452 en su
 *  fila más larga («RONDA n DECIDIENDO · x/81 CELDAS») y `Hero` empieza en
 *  x≈1038, o sea a 402 px del borde derecho. 470 cubre las dos con margen. */
const CORREDOR = 470;

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
        left: CORREDOR,
        right: CORREDOR,
        top: 26,
        zIndex: 22,
        display: "flex",
        justifyContent: "center",
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
            style={{ flex: "1 1 0", minWidth: 0, maxWidth: ANCHO_BURBUJA }}
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
