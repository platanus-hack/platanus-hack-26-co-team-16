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
 * Coloca las celdas en una nube elíptica. Las más pesadas primero (consiguen
 * el centro); rechazo por distancia mínima con relajación gradual para
 * garantizar que todas entren.
 *
 * Se probaron barrios por sector con dispersión gaussiana, buscando que la
 * nube se viera más orgánica. Se revirtió: la elipse deja las empresas más
 * juntas y el enjambre se lee como UN cuerpo, que es lo que la pieza necesita.
 * Los barrios separaban los grupos lo suficiente como para que pareciera un
 * diagrama de sectores, no una ciudad.
 */
export function disponer(arquetipos: ArquetipoEstatico[], seed = 20260322): Map<string, Celda> {
  const rng = crearRng(seed);
  const pesoMax = Math.max(...arquetipos.map((a) => a.peso));
  const orden = [...arquetipos].sort((a, b) => b.peso - a.peso);

  const A = 46; // semieje x de la nube
  const B = 29; // semieje y
  const celdas: Celda[] = [];

  for (const a of orden) {
    const w = a.peso / pesoMax;
    const r = 0.65 + 4.9 * Math.sqrt(w);
    const orbita = r + 1.1 + 2.6 * Math.sqrt(w) + 1.4;
    let margen = 1.35;
    let puesto: { x: number; y: number } | null = null;
    for (let intento = 0; intento < 4000 && !puesto; intento++) {
      // uniforme en la elipse, con un sesgo suave hacia el centro para los pesados
      const u = Math.sqrt(rng());
      const th = rng() * Math.PI * 2;
      const sesgo = 0.35 + 0.65 * (1 - w * 0.55);
      const x = A * u * sesgo * Math.cos(th);
      const y = B * u * sesgo * Math.sin(th);
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
