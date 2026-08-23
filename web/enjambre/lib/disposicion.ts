// La disposición del enjambre: dónde vive cada celda empleadora en el plano.
// Determinista por seed (mismo seed, mismo enjambre), área del nodo ∝ peso
// poblacional, separación mínima para que las órbitas de puntos no se pisen.
// Sin mapa, sin geografía: solo densidad y jerarquía de tamaños.

import { ArquetipoEstatico } from "@/estado/simulacion";

export interface Celda {
  id: string;
  x: number;
  y: number;
  /** radio del disco de la empresa, en unidades de mundo */
  r: number;
  /** radio exterior de la órbita donde viven sus puntos-persona */
  orbita: number;
  peso: number;
  indice: number;
}

// Umbrales del LOD: a cuántas personas equivale un punto según el zoom de la
// cámara ortográfica (zoom = píxeles por unidad de mundo; el enjambre entero
// cabe alrededor de zoom ~9-14 en una pantalla normal).
//
// El piso son **1.000 personas por punto**, que es la unidad visual que declara
// `web/DISENO.md`: la GEIH expande ~630 personas por fila encuestada, así que
// bajar de ahí sería dibujar una resolución que la encuesta no tiene. Con la
// grilla real (3,24 M de trabajadores con empleador) eso da ~3.200 puntos en el
// nivel más cercano y ~1.080 en el más lejano.
//
// Los dos niveles de arriba bajaron de 8.000/3.000 a 3.000/1.500. No es
// estética: con 8.000 personas por punto muchas celdas quedaban en 1-3 puntos,
// y ahí `nExp = round(n·(1−fraccion_empleada))` necesita ~50% de despidos para
// redondear siquiera a UN punto — o sea que los despidos moderados eran
// literalmente invisibles. El piso de 1.000 NO se toca: ese tiene una razón de
// honestidad, no de legibilidad.
export const NIVELES_LOD = [
  { zoomMax: 18, personasPorPunto: 3000 },
  { zoomMax: 45, personasPorPunto: 1500 },
  { zoomMax: Infinity, personasPorPunto: 1000 },
];

export function nivelPorZoom(zoom: number): number {
  for (let i = 0; i < NIVELES_LOD.length; i++) {
    if (zoom < NIVELES_LOD[i].zoomMax) return i;
  }
  return NIVELES_LOD.length - 1;
}

/** RNG determinista (mulberry32). */
export function crearRng(seed: number): () => number {
  let a = seed | 0;
  return () => {
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/**
 * Coloca las celdas en barrios por sector. Las más pesadas primero (consiguen
 * el mejor sitio); rechazo por distancia mínima con relajación gradual para
 * garantizar que todas entren.
 *
 * P4.3 — por qué ya no es una elipse. El muestreo anterior era
 * `u = √rng()` sobre una elipse de 46×29, que es exactamente la fórmula para
 * repartir puntos de forma UNIFORME por área. Sumado al rechazo por distancia
 * mínima, el resultado era un empaquetado de discos casi regular: un óvalo
 * horizontal parejo, sin grumos ni huecos. Se veía diseñado, no vivo.
 *
 * Ahora cada sector tiene su propio núcleo en el plano y las celdas caen
 * alrededor del suyo con dispersión gaussiana. Aparecen barrios densos,
 * corredores vacíos y bordes irregulares — y de paso la posición pasa a
 * significar algo: celdas cercanas comparten sector.
 */
export function disponer(arquetipos: ArquetipoEstatico[], seed = 20260322): Map<string, Celda> {
  const rng = crearRng(seed);
  const pesoMax = Math.max(...arquetipos.map((a) => a.peso));
  const orden = [...arquetipos].sort((a, b) => b.peso - a.peso);

  const A = 46; // extensión x de la nube
  const B = 29; // extensión y
  // Calibrados midiendo la huella resultante: con estos valores las 81
  // celdas ocupan ~90×61 unidades, casi lo mismo que la elipse anterior
  // (92×58), así que la cámara, el zoom inicial y los cortes de LOD siguen
  // sirviendo sin tocarlos. Verificado: 0 celdas caen al escape aleatorio.
  const NUCLEO_FACTOR = 0.52;
  const DISP_BASE = 5.0;
  const DISP_VAR = 8.0;
  const CLAMP_SIGMA = 2.0;

  // un núcleo por sector, repartidos en espiral áurea para que no queden ni
  // alineados ni amontonados
  const sectores = [...new Set(arquetipos.map((a) => a.sector))].sort();
  const AUREO = Math.PI * (3 - Math.sqrt(5));
  const nucleos = new Map<string, { x: number; y: number }>();
  sectores.forEach((s, i) => {
    const rad = Math.sqrt((i + 0.5) / sectores.length);
    const th = i * AUREO;
    nucleos.set(s, { x: Math.cos(th) * rad * A * NUCLEO_FACTOR, y: Math.sin(th) * rad * B * NUCLEO_FACTOR });
  });

  // normal(0,1) por Box-Muller, sobre el mismo rng determinista, recortada a
  // ±2σ: sin el recorte la cola de la gaussiana manda alguna celda muy lejos
  // y la nube pasa de 90×61 a 141×86 unidades, que ya no cabe en la cámara.
  const gauss = () => {
    const u1 = Math.max(1e-9, rng());
    const v = Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * rng());
    return Math.max(-CLAMP_SIGMA, Math.min(CLAMP_SIGMA, v));
  };

  const celdas: Celda[] = [];

  for (const a of orden) {
    const w = a.peso / pesoMax;
    const r = 0.65 + 4.9 * Math.sqrt(w);
    const orbita = r + 1.1 + 2.6 * Math.sqrt(w) + 1.4;
    const nucleo = nucleos.get(a.sector) ?? { x: 0, y: 0 };
    // las celdas pesadas se quedan cerca del corazón de su barrio; las
    // livianas se desparraman hacia las afueras
    const disp = DISP_BASE + DISP_VAR * (1 - w);
    let margen = 1.35;
    let puesto: { x: number; y: number } | null = null;
    for (let intento = 0; intento < 4000 && !puesto; intento++) {
      const x = nucleo.x + gauss() * disp;
      const y = nucleo.y + gauss() * disp * 0.72;
      const choca = celdas.some(
        (c) => Math.hypot(c.x - x, c.y - y) < (c.orbita + orbita) * 0.62 * margen
      );
      if (!choca) puesto = { x, y };
      if (intento % 500 === 499) margen *= 0.92; // relajar antes que fallar
    }
    if (!puesto) puesto = { x: (rng() - 0.5) * 2 * A, y: (rng() - 0.5) * 2 * B };
    celdas.push({ id: a.id, x: puesto.x, y: puesto.y, r, orbita, peso: a.peso, indice: 0 });
  }

  // índice estable por id (para el stagger de nacimiento, independiente del orden de colocación)
  const porId = new Map<string, Celda>();
  const ordenId = [...celdas].sort((a, b) => (a.id < b.id ? -1 : 1));
  ordenId.forEach((c, i) => {
    c.indice = i;
    porId.set(c.id, c);
  });
  return porId;
}
