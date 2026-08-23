"use client";

// Las celdas empleadoras: hexágonos instanciados. El área sigue al empleo vivo
// (una celda que despide se encoge), el color va del hueso al azul según su
// fracción informal REAL, y cada decisión que llega del motor dispara un anillo
// del color de su familia. Nacen con pop escalonado, sin halo.
//
// El halo aditivo se quitó: cada celda salía envuelta en un disco de color 3-4x
// su radio, y con 81 celdas eso es una capa de ruido encima de la única señal
// que importa —QUÉ decidió cada una—, que son los anillos de familia. Los
// anillos se quedan: son información, no adorno.

import { useFrame } from "@react-three/fiber";
import { useMemo, useRef } from "react";
import * as THREE from "three";
import { COLOR_FAMILIA, MotorVisual } from "./motorVisual";
import { protagonista } from "@/lib/narrativa";
import { rondasVisibles, usarAlmacen } from "@/estado/simulacion";

const HUESO = new THREE.Color("#dfe3ea");
const AZUL = new THREE.Color("#5b9dff");
const ROJO = new THREE.Color("#f0544f");
const MAX_PULSOS = 60;
// Un hexágono regular de radio 1 (al vértice) tiene área 3√3/2 ≈ 2,598,
// contra π ≈ 3,1416 del círculo. Para que un hexágono ocupe la misma área
// que el disco que reemplaza hay que escalarlo por √(π / (3√3/2)) ≈ 1,0996.
const COMPENSA_HEX = Math.sqrt(Math.PI / ((3 * Math.sqrt(3)) / 2));

function popNacimiento(t: number): number {
  if (t <= 0) return 0;
  if (t >= 1) return 1;
  const c1 = 1.70158;
  const c3 = c1 + 1;
  const u = t - 1;
  return 1 + c3 * u * u * u + c1 * u * u;
}

export default function Empresas({ motor }: { motor: MotorVisual }) {
  const n = motor.orden.length;
  const discos = useRef<THREE.InstancedMesh>(null);
  const pulsos = useRef<THREE.InstancedMesh>(null);
  const aroFoco = useRef<THREE.Mesh>(null);
  const dummy = useMemo(() => new THREE.Object3D(), []);
  const color = useMemo(() => new THREE.Color(), []);

  const rondas = usarAlmacen((s) => s.rondas);
  const rondaMostrada = usarAlmacen((s) => s.rondaMostrada);
  // S2-5: el aro rojo señala al protagonista de la ronda MOSTRADA. Antes
  // apuntaba al de una ronda futura respecto de lo que el enjambre animaba.
  const foco = useMemo(
    () => protagonista(rondasVisibles({ rondas, rondaMostrada })),
    [rondas, rondaMostrada]
  );

  useFrame((estado) => {
    const t = estado.clock.elapsedTime;
    const st = usarAlmacen.getState();
    const md = discos.current;
    const mp = pulsos.current;
    if (!md || !mp) return;

    motor.orden.forEach((id, i) => {
      const c = motor.celdas.get(id)!;
      const e = motor.actual.get(id)!;
      // P4.2: reposo vivo — la celda nunca queda perfectamente quieta
      const cx = c.x + motor.derivaX(c.indice);
      const cy = c.y + motor.derivaY(c.indice);
      const pop = popNacimiento(motor.nacimiento.get(id) ?? 0);
      // área ∝ peso × empleo vivo → radio ∝ raíz
      const r = c.r * Math.sqrt(Math.max(e.fraccion_empleada, 0.04)) * pop;

      dummy.position.set(cx, cy, 0.5);
      // el radio del hexágono se mide al VÉRTICE; se compensa para que el
      // área dibujada siga siendo ∝ peso × empleo vivo, como el disco.
      dummy.scale.setScalar(Math.max(r * COMPENSA_HEX, 0.0001));
      dummy.rotation.set(0, 0, Math.PI / 6); // lado plano arriba, como un panal
      dummy.updateMatrix();
      md.setMatrixAt(i, dummy.matrix);

      color.copy(HUESO).lerp(AZUL, Math.min(1, e.fraccion_informal * 1.12));
      // la celda que aún no decide en la ronda en curso respira, tenue
      const pendiente =
        st.conexion === "corriendo" && motor.rondaEnCurso > 0 && !motor.decididas.has(id);
      const respiro = pendiente ? 0.86 + 0.14 * Math.sin(t * 2.2 + c.indice * 1.7) : 1;
      const esHover = st.hover === id;
      color.multiplyScalar(respiro * (esHover ? 1.25 : 1));
      md.setColorAt(i, color);
    });

    // anillos de decisión: aditivos, el alfa viaja en el color
    for (let i = 0; i < MAX_PULSOS; i++) {
      const p = motor.pulsos[i];
      if (!p) {
        dummy.scale.setScalar(0.0001);
        dummy.updateMatrix();
        mp.setMatrixAt(i, dummy.matrix);
        continue;
      }
      const c = motor.celdas.get(p.id)!;
      const dur = 1.9;
      const k = Math.min(1, p.edad / dur);
      dummy.position.set(c.x + motor.derivaX(c.indice), c.y + motor.derivaY(c.indice), 0.6);
      dummy.scale.setScalar(c.r * (1.25 + k * 3.4));
      dummy.updateMatrix();
      mp.setMatrixAt(i, dummy.matrix);
      color.set(p.vetadas > 0 && k < 0.35 ? "#f0544f" : COLOR_FAMILIA[p.familia ?? "otra"] ?? "#a7afbe");
      color.multiplyScalar((1 - k) * 0.85);
      mp.setColorAt(i, color);
    }

    md.instanceMatrix.needsUpdate = true;
    mp.instanceMatrix.needsUpdate = true;
    if (md.instanceColor) md.instanceColor.needsUpdate = true;
    if (mp.instanceColor) mp.instanceColor.needsUpdate = true;

    // el aro del testimonio: rojo, giro lento, latido
    if (aroFoco.current) {
      if (foco) {
        const c = motor.celdas.get(foco.id);
        if (c) {
          aroFoco.current.visible = true;
          aroFoco.current.position.set(c.x + motor.derivaX(c.indice), c.y + motor.derivaY(c.indice), 0.7);
          const e = motor.actual.get(foco.id)!;
          const r = c.r * Math.sqrt(Math.max(e.fraccion_empleada, 0.04));
          aroFoco.current.scale.setScalar(r * (1.55 + 0.1 * Math.sin(t * 3)));
          aroFoco.current.rotation.z = t * 0.6;
          (aroFoco.current.material as THREE.MeshBasicMaterial).color
            .copy(ROJO)
            .multiplyScalar(0.75 + 0.25 * Math.sin(t * 3));
        }
      } else {
        aroFoco.current.visible = false;
      }
    }
  });

  return (
    <group>
      {/* P5.2 · HIVE: la empresa es un hexágono. `circleGeometry` con 6
          segmentos ya ES un hexágono regular, así que no hace falta
          construir una THREE.Shape ni cambiar nada del instanciado. El
          pulso y el aro siguen circulares a propósito: no compiten con la
          silueta. */}
      <instancedMesh ref={discos} args={[undefined, undefined, n]} frustumCulled={false}>
        <circleGeometry args={[1, 6]} />
        <meshBasicMaterial />
      </instancedMesh>
      <instancedMesh ref={pulsos} args={[undefined, undefined, MAX_PULSOS]} frustumCulled={false}>
        <ringGeometry args={[0.92, 1, 64]} />
        <meshBasicMaterial transparent depthWrite={false} blending={THREE.AdditiveBlending} />
      </instancedMesh>
      <mesh ref={aroFoco} visible={false}>
        <ringGeometry args={[0.94, 1, 64, 1, 0, Math.PI * 1.55]} />
        <meshBasicMaterial transparent depthWrite={false} blending={THREE.AdditiveBlending} />
      </mesh>
    </group>
  );
}
