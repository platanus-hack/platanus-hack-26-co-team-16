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
          let mejorD = Infinity;
          for (const c of motor.celdas.values()) {
            const d = Math.hypot(c.x - x, c.y - y);
            if (d < Math.max(c.r * 1.6, 1.6) && d < mejorD) {
              mejor = c.id;
              mejorD = d;
            }
          }
          const st = usarAlmacen.getState();
          if (st.hover !== mejor) st.setHover(mejor);
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
