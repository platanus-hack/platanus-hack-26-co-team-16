"use client";

// La composición del enjambre: motor visual compartido, LOD por zoom, hover.

import { useFrame, useThree } from "@react-three/fiber";
import { useMemo, useRef } from "react";
import * as THREE from "three";
import Empresas from "./Empresas";
import Onda from "./Onda";
import Personas from "./Personas";
import { MotorVisual } from "./motorVisual";
import { nivelPorZoom, NIVELES_LOD } from "@/lib/disposicion";
import { usarAlmacen } from "@/estado/simulacion";

export default function Escena() {
  const poblacion = usarAlmacen((s) => s.poblacion);
  const camera = useThree((s) => s.camera);
  const nivelRef = useRef(-1);

  const motor = useMemo(() => (poblacion ? new MotorVisual(poblacion) : null), [poblacion]);

  useFrame((_, dt) => {
    if (!motor) return;
    motor.actualizar(Math.min(dt, 0.1));
    // Cámara accesible para la verificación automatizada (`?prueba`).
    if (typeof window !== "undefined") {
      (window as unknown as { __camara?: unknown }).__camara = camera;
    }
    // LOD: el zoom de la cámara decide cuántas personas representa un punto
    const nivel = nivelPorZoom((camera as THREE.OrthographicCamera).zoom);
    if (nivel !== nivelRef.current) {
      nivelRef.current = nivel;
      usarAlmacen.getState().setPersonasPorPunto(NIVELES_LOD[nivel].personasPorPunto);
    }
  });

  if (!motor) return null;

  return (
    <group>
      {/* plano invisible que captura el puntero para el hover */}
      <mesh
        position={[0, 0, -1]}
        onPointerMove={(e) => {
          const { x, y } = e.point;
          let mejor: string | null = null;
          let mejorTipo: "empresa" | "personas" | null = null;
          let mejorD = Infinity;
          for (const c of motor.celdas.values()) {
            // la celda se mueve con el reposo vivo (P4.2): si el hover usara la
            // posición nominal, apuntaría al lado de lo que se ve.
            const cx = c.x + motor.derivaX(c.indice);
            const cy = c.y + motor.derivaY(c.indice);
            const d = Math.hypot(cx - x, cy - y);
            if (d >= mejorD) continue;
            // P6: adentro es la empresa; el anillo de afuera son sus abejas.
            if (d < Math.max(c.r * 1.25, 1.4)) {
              mejor = c.id;
              mejorTipo = "empresa";
              mejorD = d;
            } else if (d < c.orbita) {
              mejor = c.id;
              mejorTipo = "personas";
              mejorD = d;
            }
          }
          const st = usarAlmacen.getState();
          if (st.hover !== mejor || st.hoverTipo !== mejorTipo) st.setHover(mejor, mejorTipo);
        }}
        onPointerLeave={() => usarAlmacen.getState().setHover(null)}
      >
        <planeGeometry args={[400, 260]} />
        <meshBasicMaterial visible={false} />
      </mesh>

      <Onda motor={motor} />
      <Personas motor={motor} />
      <Empresas motor={motor} />
    </group>
  );
}
