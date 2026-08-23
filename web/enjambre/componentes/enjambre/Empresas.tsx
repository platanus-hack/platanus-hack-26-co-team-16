"use client";

// Las celdas empleadoras: discos instanciados con halo aditivo. El área sigue
// al empleo vivo (una celda que despide se encoge), el color va del hueso al
// azul según su fracción informal REAL, y cada decisión que llega del motor
// dispara un anillo del color de su familia. Nacen con pop escalonado.

import { useFrame } from "@react-three/fiber";
import { useMemo, useRef } from "react";
import * as THREE from "three";
import { COLOR_FAMILIA, MotorVisual } from "./motorVisual";
import { protagonista } from "@/lib/narrativa";
import { usarAlmacen } from "@/estado/simulacion";

const HUESO = new THREE.Color("#dfe3ea");
const AZUL = new THREE.Color("#5b9dff");
const ROJO = new THREE.Color("#f0544f");
const MAX_PULSOS = 60;

function popNacimiento(t: number): number {
  if (t <= 0) return 0;
  if (t >= 1) return 1;
  const c1 = 1.70158;
  const c3 = c1 + 1;
  const u = t - 1;
  return 1 + c3 * u * u * u + c1 * u * u;
}

function texturaHalo(): THREE.CanvasTexture {
  const c = document.createElement("canvas");
  c.width = c.height = 128;
  const g = c.getContext("2d")!;
  const grad = g.createRadialGradient(64, 64, 0, 64, 64, 64);
  grad.addColorStop(0, "rgba(255,255,255,0.85)");
  grad.addColorStop(0.35, "rgba(255,255,255,0.25)");
  grad.addColorStop(1, "rgba(255,255,255,0)");
  g.fillStyle = grad;
  g.fillRect(0, 0, 128, 128);
  return new THREE.CanvasTexture(c);
}

export default function Empresas({ motor }: { motor: MotorVisual }) {
  const n = motor.orden.length;
  const discos = useRef<THREE.InstancedMesh>(null);
  const halos = useRef<THREE.InstancedMesh>(null);
  const pulsos = useRef<THREE.InstancedMesh>(null);
  const aroFoco = useRef<THREE.Mesh>(null);
  const halo = useMemo(texturaHalo, []);
  const dummy = useMemo(() => new THREE.Object3D(), []);
  const color = useMemo(() => new THREE.Color(), []);

  const rondas = usarAlmacen((s) => s.rondas);
  const foco = useMemo(() => protagonista(rondas), [rondas]);

  useFrame((estado) => {
    const t = estado.clock.elapsedTime;
    const st = usarAlmacen.getState();
    const md = discos.current;
    const mh = halos.current;
    const mp = pulsos.current;
    if (!md || !mh || !mp) return;

    motor.orden.forEach((id, i) => {
      const c = motor.celdas.get(id)!;
      const e = motor.actual.get(id)!;
      const pop = popNacimiento(motor.nacimiento.get(id) ?? 0);
      // área ∝ peso × empleo vivo → radio ∝ raíz
      const r = c.r * Math.sqrt(Math.max(e.fraccion_empleada, 0.04)) * pop;

      dummy.position.set(c.x, c.y, 0.5);
      dummy.scale.setScalar(Math.max(r, 0.0001));
      dummy.rotation.set(0, 0, 0);
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

      // halo aditivo, más ancho y más azul cuanto más informal
      dummy.position.set(c.x, c.y, 0.2);
      dummy.scale.setScalar(Math.max(r * (3.0 + 0.9 * e.fraccion_informal), 0.0001));
      dummy.updateMatrix();
      mh.setMatrixAt(i, dummy.matrix);
      color.copy(HUESO).lerp(AZUL, Math.min(1, e.fraccion_informal * 1.2));
      const brillo = (esHover ? 0.3 : 0.11) * respiro * pop;
      color.multiplyScalar(brillo);
      mh.setColorAt(i, color);
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
      dummy.position.set(c.x, c.y, 0.6);
      dummy.scale.setScalar(c.r * (1.25 + k * 3.4));
      dummy.updateMatrix();
      mp.setMatrixAt(i, dummy.matrix);
      color.set(p.vetadas > 0 && k < 0.35 ? "#f0544f" : COLOR_FAMILIA[p.familia ?? "otra"] ?? "#a7afbe");
      color.multiplyScalar((1 - k) * 0.85);
      mp.setColorAt(i, color);
    }

    md.instanceMatrix.needsUpdate = true;
    mh.instanceMatrix.needsUpdate = true;
    mp.instanceMatrix.needsUpdate = true;
    if (md.instanceColor) md.instanceColor.needsUpdate = true;
    if (mh.instanceColor) mh.instanceColor.needsUpdate = true;
    if (mp.instanceColor) mp.instanceColor.needsUpdate = true;

    // el aro del testimonio: rojo, giro lento, latido
    if (aroFoco.current) {
      if (foco) {
        const c = motor.celdas.get(foco.id);
        if (c) {
          aroFoco.current.visible = true;
          aroFoco.current.position.set(c.x, c.y, 0.7);
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
      <instancedMesh ref={halos} args={[undefined, undefined, n]} frustumCulled={false}>
        <planeGeometry args={[2, 2]} />
        <meshBasicMaterial
          map={halo}
          transparent
          depthWrite={false}
          blending={THREE.AdditiveBlending}
        />
      </instancedMesh>
      <instancedMesh ref={discos} args={[undefined, undefined, n]} frustumCulled={false}>
        <circleGeometry args={[1, 48]} />
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
