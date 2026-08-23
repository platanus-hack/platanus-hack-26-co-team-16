"use client";

// Los puntos-persona. Cada punto representa N personas expandidas (N cambia
// con el zoom: LOD). Su estado sale del estado REAL de su celda en la ronda:
//   verde  = empleo formal cumpliendo
//   ámbar  = conserva el empleo con jornada recortada
//   azul   = empleo informal (fuera de regla)
//   aro    = expulsado del empleo (despedido), deriva fuera de su celda
// El reparto por punto usa un rango fijo de vulnerabilidad por celda, así los
// mismos puntos que se informalizaron siguen azules la ronda siguiente (los
// flujos del motor son acumulativos y la visual lo respeta).

import { useFrame, useThree } from "@react-three/fiber";
import { useEffect, useMemo, useRef } from "react";
import * as THREE from "three";
import { MotorVisual } from "./motorVisual";
import { crearRng } from "@/lib/disposicion";
import { usarAlmacen } from "@/estado/simulacion";

const COLORES = [
  new THREE.Color("#3ecf8e"), // 0 verde
  new THREE.Color("#e8a33d"), // 1 ámbar
  new THREE.Color("#5b9dff"), // 2 azul
  new THREE.Color("#99a2b1"), // 3 expulsado
];

interface Punto {
  celda: string;
  rango: number;
  /** posición 0..1 dentro de su celda: fija el turno de aparición en la intro */
  orden: number;
  ang: number;
  vel: number;
  /** radio de órbita ACTUAL (se anima al cambiar de anillo) */
  rad: number;
  /** anillo interior: en regla, pegada a su empresa */
  radFormal: number;
  /** anillo exterior: fuera de regla, en la periferia de su empresa */
  radInformal: number;
  /** empuje angular temporal mientras dura el viaje entre anillos */
  impulso: number;
  fase: number;
  estado: number;
  color: THREE.Color;
  x: number;
  y: number;
  exDX: number;
  exDY: number;
  exEdad: number;
  desdeX: number;
  desdeY: number;
  tEntrada: number;
  brillo: number; // destello al cambiar de estado
}

const VERTICES = /* glsl */ `
  attribute float tamano;
  attribute float hueco;
  attribute float alfa;
  attribute vec3 tinte;
  varying vec3 vTinte;
  varying float vHueco;
  varying float vAlfa;
  varying float vPx;
  uniform float uZoom;
  void main() {
    vTinte = tinte;
    vHueco = hueco;
    vAlfa = alfa;
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    float px = max(tamano * uZoom, 1.5);
    // el fragmento necesita saber a cuántos píxeles se está dibujando para
    // decidir si dibuja la abeja o cae al punto liso (P5.4)
    vPx = px;
    gl_PointSize = px;
  }
`;

// P5.3 · HIVE: la persona es una abeja. La silueta se dibuja en el shader
// (nada de texturas ni sprites: son decenas de miles de puntos) con tres
// elipses — cuerpo vertical y dos alas — más una cintura que insinúa las
// franjas sin dibujarlas.
//
// P5.4 · legibilidad primero. Por debajo de PX_ABEJA píxeles la abeja se
// vuelve una mancha ilegible, así que ahí se dibuja el punto liso de siempre.
// La transición es un mix suave para que no se vea el salto al hacer zoom.
const FRAGMENTOS = /* glsl */ `
  varying vec3 vTinte;
  varying float vHueco;
  varying float vAlfa;
  varying float vPx;

  // <=0 dentro de la elipse
  float elipse(vec2 p, vec2 centro, vec2 radios) {
    vec2 q = (p - centro) / radios;
    return dot(q, q) - 1.0;
  }

  float abeja(vec2 p) {
    // cuerpo: óvalo vertical, ligeramente bajo el centro
    float cuerpo = elipse(p, vec2(0.0, -0.04), vec2(0.30, 0.44));
    // alas: dos óvalos inclinados hacia arriba y afuera
    float alaI = elipse(p, vec2(-0.30, 0.22), vec2(0.24, 0.15));
    float alaD = elipse(p, vec2( 0.30, 0.22), vec2(0.24, 0.15));
    float alas = min(alaI, alaD);
    float f = min(cuerpo, alas);
    // borde suave dependiente del tamaño: nítida en grande, blanda en chico
    float suave = clamp(2.2 / vPx, 0.06, 0.34);
    return smoothstep(suave, -suave, f);
  }

  void main() {
    vec2 c = gl_PointCoord - 0.5;
    vec2 p = c * 2.0;          // -1..1
    float d = length(c) * 2.0;

    float disco = smoothstep(1.0, 0.7, d);
    float aro = smoothstep(1.0, 0.84, d) * smoothstep(0.5, 0.68, d);
    float liso = mix(disco, aro, vHueco);

    // la abeja solo se dibuja si hay píxeles para que se lea
    float silueta = abeja(p);
    float esAbeja = smoothstep(6.0, 11.0, vPx) * (1.0 - vHueco);
    float forma = mix(liso, silueta, esAbeja);

    float a = forma * vAlfa;
    if (a < 0.012) discard;
    gl_FragColor = vec4(vTinte, a);
  }
`;

function construirPuntos(
  motor: MotorVisual,
  ppp: number,
  previos: Punto[] | null
): { puntos: Punto[]; porCelda: Map<string, number> } {
  const puntos: Punto[] = [];
  const porCelda = new Map<string, number>();
  const previosPorCelda = new Map<string, Punto[]>();
  if (previos) {
    for (const p of previos) {
      let l = previosPorCelda.get(p.celda);
      if (!l) previosPorCelda.set(p.celda, (l = []));
      l.push(p);
    }
  }

  for (const a of motor.poblacion.arquetipos) {
    const c = motor.celdas.get(a.id)!;
    const n = Math.max(1, Math.round(a.peso / ppp));
    porCelda.set(a.id, n);
    const rng = crearRng(c.indice * 7919 + n * 131);
    // permutación del rango de vulnerabilidad: los estados quedan mezclados
    // espacialmente, no en cuñas
    const rangos = Array.from({ length: n }, (_, i) => i);
    for (let i = n - 1; i > 0; i--) {
      const j = Math.floor(rng() * (i + 1));
      [rangos[i], rangos[j]] = [rangos[j], rangos[i]];
    }
    const rInt = c.r * 1.18 + 0.3;
    const rExt = Math.max(c.orbita - 0.15, rInt + 0.5);
    const padres = previosPorCelda.get(a.id);

    const medio = rInt + (rExt - rInt) * 0.45;
    for (let i = 0; i < n; i++) {
      const ang = rng() * Math.PI * 2;
      // P0.7: cada persona tiene DOS órbitas en su propia empresa — una
      // interior (en regla) y una exterior (fuera de regla). Informalizarse es
      // viajar de una a la otra, no cambiar de color en el sitio. El modelo no
      // mueve gente entre empresas, así que la visual tampoco.
      const radFormal = rInt + (medio - rInt) * Math.sqrt(rng());
      const radInformal = medio + (rExt - medio) * Math.sqrt(rng());
      const rad = radFormal;
      const padre = padres?.length ? padres[Math.floor((i / n) * padres.length)] : null;
      puntos.push({
        celda: a.id,
        rango: rangos[i],
        orden: n > 1 ? i / (n - 1) : 0,
        ang,
        vel: (0.05 + rng() * 0.09) * (rng() < 0.5 ? 1 : -1),
        rad,
        radFormal,
        radInformal,
        impulso: 0,
        fase: rng() * Math.PI * 2,
        estado: -1 as unknown as number, // se asigna en el primer frame
        color: new THREE.Color("#3ecf8e"),
        x: c.x + Math.cos(ang) * rad,
        y: c.y + Math.sin(ang) * rad,
        exDX: 0,
        exDY: 0,
        exEdad: 0,
        desdeX: padre ? padre.x : c.x,
        desdeY: padre ? padre.y : c.y,
        tEntrada: padre ? 0 : 1,
        brillo: 0,
      });
    }
  }
  return { puntos, porCelda };
}

export default function Personas({ motor }: { motor: MotorVisual }) {
  const ppp = usarAlmacen((s) => s.personasPorPunto);
  const camera = useThree((s) => s.camera);
  const previosRef = useRef<Punto[] | null>(null);
  const puntosRef = useRef<THREE.Points>(null);

  const { puntos, porCelda } = useMemo(
    () => construirPuntos(motor, ppp, previosRef.current),
    [motor, ppp]
  );
  useEffect(() => {
    previosRef.current = puntos;
  }, [puntos]);

  const geometria = useMemo(() => {
    const g = new THREE.BufferGeometry();
    const n = puntos.length;
    g.setAttribute("position", new THREE.BufferAttribute(new Float32Array(n * 3), 3));
    g.setAttribute("tinte", new THREE.BufferAttribute(new Float32Array(n * 3), 3));
    g.setAttribute("tamano", new THREE.BufferAttribute(new Float32Array(n), 1));
    g.setAttribute("hueco", new THREE.BufferAttribute(new Float32Array(n), 1));
    g.setAttribute("alfa", new THREE.BufferAttribute(new Float32Array(n), 1));
    g.boundingSphere = new THREE.Sphere(new THREE.Vector3(), 500);
    return g;
  }, [puntos]);

  const material = useMemo(
    () =>
      new THREE.ShaderMaterial({
        vertexShader: VERTICES,
        fragmentShader: FRAGMENTOS,
        uniforms: { uZoom: { value: 10 } },
        transparent: true,
        depthWrite: false,
      }),
    []
  );

  // tamaño del punto en unidades de mundo, según cuánta gente representa
  // SUPUESTO: los tres tamaños de punto (0,86 / 0,58 / 0,42) y sus cortes de
  // LOD (3.000 / 1.500 personas por punto) son estética de legibilidad al
  // hacer zoom, no un cálculo del motor. Subidos desde 0,5/0,34/0,22: a los
  // valores viejos las personas no se distinguían sin acercarse.
  const tamanoBase = ppp >= 3000 ? 0.86 : ppp >= 1500 ? 0.58 : 0.42;

  useFrame((estado, dtCrudo) => {
    const dt = Math.min(dtCrudo, 0.1);
    const t = estado.clock.elapsedTime;
    material.uniforms.uZoom.value = (camera as THREE.OrthographicCamera).zoom;

    // umbrales por celda, una vez por frame
    const umbrales = new Map<string, { nExp: number; nInf: number; nJor: number; n: number }>();
    for (const [id, n] of porCelda) {
      const e = motor.actual.get(id)!;
      const nExp = Math.round(n * (1 - e.fraccion_empleada));
      const nEmpleado = n - nExp;
      const nInf = Math.round(nEmpleado * e.fraccion_informal);
      // S2-3: nada de `+0.15` inventado — la fracción de puntos ámbar sale
      // directo de `e.horas`, el estado real de la celda que emite el motor.
      // El `+0.15` anterior inflaba el conteo de puntos por encima de la
      // cifra real (`fraccion_jornada_recortada` en Metricas.tsx).
      const nJor = e.horas < 0.999 ? Math.round((nEmpleado - nInf) * (1 - e.horas)) : 0;
      umbrales.set(id, { nExp, nInf, nJor, n });
    }

    const pos = geometria.getAttribute("position") as THREE.BufferAttribute;
    const tinte = geometria.getAttribute("tinte") as THREE.BufferAttribute;
    const tam = geometria.getAttribute("tamano") as THREE.BufferAttribute;
    const hueco = geometria.getAttribute("hueco") as THREE.BufferAttribute;
    const alfa = geometria.getAttribute("alfa") as THREE.BufferAttribute;

    for (let i = 0; i < puntos.length; i++) {
      const p = puntos[i];
      const c = motor.celdas.get(p.celda)!;
      const u = umbrales.get(p.celda)!;

      // estado según el rango de vulnerabilidad (acumulativo entre rondas)
      let objetivo: number;
      if (p.rango >= u.n - u.nExp) objetivo = 3;
      else if (p.rango < u.nInf) objetivo = 2;
      else if (p.rango < u.nInf + u.nJor) objetivo = 1;
      else objetivo = 0;

      if (objetivo !== p.estado) {
        if (objetivo === 3 && p.estado !== 3) {
          // recién expulsado: sale disparado desde donde orbitaba
          const dx = p.x - c.x;
          const dy = p.y - c.y;
          const d = Math.hypot(dx, dy) || 1;
          p.exDX = dx / d + (Math.sin(p.fase) * 0.5);
          p.exDY = dy / d + (Math.cos(p.fase * 1.3) * 0.5);
          const dn = Math.hypot(p.exDX, p.exDY) || 1;
          p.exDX /= dn;
          p.exDY /= dn;
          p.exEdad = 0;
        }
        // P0.7 / P4.4: entrar o salir de la informalidad es un VIAJE entre
        // los dos anillos de su empresa. Como el ángulo sigue avanzando
        // mientras el radio cambia, la trayectoria es una espiral: se ve el
        // recorrido, no un salto.
        if (objetivo !== 3) p.impulso = 1;
        p.estado = objetivo;
        p.brillo = 1;
      }
      p.brillo = Math.max(0, p.brillo - dt * 1.4);

      // posición
      if (p.estado === 3) {
        p.exEdad += dt;
        const v = 3.1 * Math.exp(-p.exEdad * 0.7) + 0.14;
        p.x += p.exDX * v * dt + Math.sin(t * 0.7 + p.fase) * 0.12 * dt;
        p.y += p.exDY * v * dt + Math.cos(t * 0.6 + p.fase * 1.7) * 0.12 * dt;
      } else {
        // el radio persigue al anillo que le toca por su estado
        const destino = p.estado === 2 ? p.radInformal : p.radFormal;
        p.rad += (destino - p.rad) * Math.min(1, dt / 0.45);
        // mientras viaja, gira más rápido: la espiral se nota
        p.impulso = Math.max(0, p.impulso - dt / 1.1);
        p.ang += p.vel * (1 + p.impulso * 2.4) * dt;
        const respiro = 1 + Math.sin(t * 0.9 + p.fase) * 0.025;
        // P4.2: la persona orbita su empresa Y acompaña la deriva de esta
        p.x = c.x + motor.derivaX(c.indice) + Math.cos(p.ang) * p.rad * respiro;
        p.y = c.y + motor.derivaY(c.indice) + Math.sin(p.ang) * p.rad * respiro;
      }

      // entrada (nacimiento o cambio de LOD): vuela desde el padre
      let px = p.x;
      let py = p.y;
      if (p.tEntrada < 1) {
        p.tEntrada = Math.min(1, p.tEntrada + dt / 0.85);
        const k = 1 - Math.pow(1 - p.tEntrada, 3);
        px = p.desdeX + (p.x - p.desdeX) * k;
        py = p.desdeY + (p.y - p.desdeY) * k;
      }
      pos.setXYZ(i, px, py, 0.35);

      // color con destello en el cambio
      p.color.lerp(COLORES[p.estado], Math.min(1, dt * 2.4));
      const b = 1 + p.brillo * 1.6;
      tinte.setXYZ(i, p.color.r * b, p.color.g * b, p.color.b * b);

      // P2: durante la intro cada persona aparece en su turno alrededor de su
      // empresa, no todas de golpe con ella.
      const nac = motor.nacimientoPersona(p.celda, p.orden);
      const popN = nac < 1 ? nac * (1.6 - 0.6 * nac) : 1; // leve sobreimpulso
      tam.setX(i, tamanoBase * (p.estado === 3 ? 0.92 : 1) * popN * (1 + p.brillo * 0.7));
      hueco.setX(i, p.estado === 3 ? 1 : 0);
      alfa.setX(i, (p.estado === 3 ? 0.7 : 0.95) * popN);
    }

    pos.needsUpdate = true;
    tinte.needsUpdate = true;
    tam.needsUpdate = true;
    hueco.needsUpdate = true;
    alfa.needsUpdate = true;
  });

  return <points ref={puntosRef} geometry={geometria} material={material} frustumCulled={false} />;
}
