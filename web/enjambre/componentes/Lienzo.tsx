"use client";

// El lienzo WebGL: cámara ortográfica cenital, pan + zoom (sin rotación), y la
// escena del enjambre adentro. El zoom mueve el LOD: acercarse subdivide los
// puntos (cada uno pasa a representar menos personas).

import { Canvas } from "@react-three/fiber";
import { MapControls } from "@react-three/drei";
import Escena from "@/componentes/enjambre/Escena";

export default function Lienzo() {
  return (
    <div style={{ position: "absolute", inset: 0 }}>
      <Canvas
        orthographic
        dpr={[1, 2]}
        camera={{ position: [0, 0, 100], zoom: 9, up: [0, 1, 0], near: 1, far: 1000 }}
        // `preserveDrawingBuffer` deja que el lienzo se pueda capturar
        // (`toDataURL`) para screenshots del pitch y para la verificación
        // automatizada. Con 81 celdas y unos miles de puntos el costo es nulo.
        gl={{ antialias: true, alpha: false, preserveDrawingBuffer: true }}
        onCreated={({ gl, scene }) => {
          gl.setClearColor("#06080c");
          scene.background = null;
        }}
      >
        <MapControls
          enableRotate={false}
          screenSpacePanning
          minZoom={5}
          maxZoom={110}
          dampingFactor={0.12}
          zoomSpeed={1.1}
          panSpeed={0.9}
        />
        <Escena />
      </Canvas>
    </div>
  );
}
