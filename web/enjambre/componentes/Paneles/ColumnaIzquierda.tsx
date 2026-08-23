"use client";

// La columna izquierda inferior: reparto de estrategias arriba, leyenda abajo.
//
// Existe por una razón geométrica concreta. Antes `Estrategias` vivía anclada a
// `bottom:128` y `Leyenda` a `bottom:30`, cada una con su alto variable, así
// que se pisaban ~31 px — y como las dos estaban ancladas al borde inferior, se
// pisaban en TODA resolución, no solo en pantallas bajas. Un solo contenedor en
// flujo normal hace que el solapamiento sea imposible por construcción en vez
// de depender de que los altos declarados sigan siendo ciertos.

import Estrategias from "./Estrategias";
import Leyenda from "./Leyenda";

export default function ColumnaIzquierda() {
  return (
    <div
      className="panel"
      style={{
        left: 36,
        bottom: 30,
        width: 330,
        display: "flex",
        flexDirection: "column",
        gap: 13,
      }}
    >
      <Estrategias />
      <Leyenda />
    </div>
  );
}
