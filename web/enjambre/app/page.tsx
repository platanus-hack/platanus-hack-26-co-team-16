"use client";

// La máquina de pantallas: carga → menú → política → simulación.
// Cada fase es un componente separado; el estado vive en estado/simulacion.ts.

import Carga from "@/componentes/Carga";
import ControlPolitica from "@/componentes/ControlPolitica";
import Menu from "@/componentes/Menu";
import Simulacion from "@/componentes/Simulacion";
import { usarAlmacen } from "@/estado/simulacion";

export default function Pagina() {
  const fase = usarAlmacen((s) => s.fase);
  return (
    <main style={{ position: "fixed", inset: 0 }}>
      {fase === "carga" && <Carga />}
      {fase === "menu" && <Menu />}
      {fase === "politica" && <ControlPolitica />}
      {fase === "simulacion" && <Simulacion />}
    </main>
  );
}
