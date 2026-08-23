"use client";

// La onda de informalización: anillos que se expanden desde el centro de masa
// del incumplimiento NUEVO (ponderado por peso poblacional y por cuánto se
// movió cada celda respecto de su estado inicial). El radio sigue a la brecha
// real acumulada — si la política no mueve nada, la onda casi no existe.

import { useFrame } from "@react-three/fiber";
import { useMemo, useRef } from "react";
import * as THREE from "three";
import { MotorVisual } from "./motorVisual";

const AZUL = new THREE.Color("#5b9dff");

export default function Onda({ motor }: { motor: MotorVisual }) {
  const grupo = useRef<THREE.Group>(null);
  const relleno = useRef<THREE.Mesh>(null);
  const anillos = useRef<THREE.Mesh[]>([]);
  const suave = useRef({ x: 0, y: 0, r: 0 });

  const capas = useMemo(
    () => [
      { k: 1.0, alfa: 0.3, interior: 0.985 },
      { k: 0.85, alfa: 0.13, interior: 0.99 },
      { k: 0.68, alfa: 0.06, interior: 0.99 },
    ],
    []
  );

  useFrame((estado, dtCrudo) => {
    const dt = Math.min(dtCrudo, 0.1);
    const t = estado.clock.elapsedTime;
    if (!grupo.current) return;

    // brecha visual NETA (la misma resta del hero: tasa actual − tasa inicial,
    // ponderada); el centro sí usa solo los movimientos positivos.
    let peso = 0;
    let neto = 0;
    let delta = 0;
    let cx = 0;
    let cy = 0;
    for (const a of motor.poblacion.arquetipos) {
      const e = motor.actual.get(a.id)!;
      peso += a.peso;
      neto += a.peso * (e.fraccion_informal - a.fraccion_informal_inicial);
      const d = Math.max(0, e.fraccion_informal - a.fraccion_informal_inicial);
      const w = a.peso * d;
      delta += w;
      const c = motor.celdas.get(a.id)!;
      cx += c.x * w;
      cy += c.y * w;
    }
    // OJO: esto mide el movimiento DE LA GRILLA (las celdas dibujadas), que es
    // lo que hacen los puntos en pantalla. El hero muestra la tasa del contrato,
    // que parte del universo observado completo — pueden diferir y es sabido.
    const brecha = peso > 0 ? Math.max(0, neto / peso) : 0;
    // SUPUESTO: 0,04pp de piso de visibilidad y el mapeo brecha→radio
    // (4 + 55·√brecha, tope 30) son escala visual arbitraria para que la
    // onda quepa en pantalla — no salen de ningún dato del motor.
    const objetivoR = brecha > 0.0004 ? Math.min(30, 4 + 55 * Math.sqrt(brecha)) : 0;
    const ox = delta > 0 ? cx / delta : 0;
    const oy = delta > 0 ? cy / delta : 0;

    const s = suave.current;
    const k = Math.min(1, dt * 1.6);
    s.x += (ox - s.x) * k;
    s.y += (oy - s.y) * k;
    s.r += (objetivoR - s.r) * Math.min(1, dt * 0.9);

    grupo.current.position.set(s.x, s.y, 0.05);
    const visible = s.r > 0.6;
    grupo.current.visible = visible;
    if (!visible) return;

    anillos.current.forEach((m, i) => {
      if (!m || i >= capas.length) {
        if (m) m.visible = false;
        return;
      }
      const capa = capas[i];
      const lat = 1 + Math.sin(t * 1.4 - i * 0.9) * 0.02;
      m.scale.setScalar(Math.max(s.r * capa.k * lat, 0.001));
      (m.material as THREE.MeshBasicMaterial).color
        .copy(AZUL)
        .multiplyScalar(capa.alfa * Math.min(1, s.r / 8));
      m.rotation.z = t * 0.05 * (i % 2 === 0 ? 1 : -1);
    });
    if (relleno.current) {
      relleno.current.scale.setScalar(Math.max(s.r * 0.92, 0.001));
      (relleno.current.material as THREE.MeshBasicMaterial).color
        .copy(AZUL)
        .multiplyScalar(0.028);
    }
  });

  return (
    <group ref={grupo} visible={false}>
      <mesh ref={relleno}>
        <circleGeometry args={[1, 72]} />
        <meshBasicMaterial transparent depthWrite={false} blending={THREE.AdditiveBlending} />
      </mesh>
      {[0, 1, 2].map((i) => (
        <mesh
          key={i}
          ref={(m) => {
            if (m) anillos.current[i] = m;
          }}
        >
          <ringGeometry args={[i === 0 ? 0.985 : 0.99, 1, 96]} />
          <meshBasicMaterial transparent depthWrite={false} blending={THREE.AdditiveBlending} />
        </mesh>
      ))}
    </group>
  );
}
