// El histórico del laboratorio: un JSONL versionado con una línea por corrida
// terminada.
//
// POR QUÉ ACÁ Y NO EN api/. El histórico es un artefacto de la interfaz, no del
// motor: se llena con lo que el frontend ya recibió por el flujo SSE y no le
// pide nada nuevo al modelo. Ponerlo en `api/` (de R2) o en `scripts/` (de R5)
// cruzaría carpetas de otros dueños para no ganar nada. Vive entero en `web/`.
//
// POR QUÉ NO CUELGA DE /api. `next.config.mjs` reescribe `/api/:path*` al
// backend de Python, así que cualquier ruta bajo ese prefijo se la comería el
// proxy antes de llegar acá. Por eso vive en `/laboratorio/registro`.
//
// CÓMO SE COMPORTA DESPLEGADO, QUE ES DISTINTO. En local el POST agrega una
// línea al archivo y el histórico crece con el uso; se commitea como cualquier
// otro artefacto. En un host serverless el sistema de archivos es de solo
// lectura, así que el POST falla en silencio y el GET sirve lo que esté
// commiteado. Es deliberado: la evidencia se acumula corriendo el simulador en
// local y se publica por git, no por escrituras en producción.

import { promises as fs } from "fs";
import path from "path";
import { NextResponse } from "next/server";

// el histórico vive fuera de la app de Next, en `web/laboratorio/`, para que
// no lo barra un `rm` de `.next` ni lo sirva el bundle estático
const ARCHIVO = path.join(process.cwd(), "..", "laboratorio", "historico.jsonl");

export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const texto = await fs.readFile(ARCHIVO, "utf8");
    const filas = texto
      .split("\n")
      .filter((l) => l.trim().length > 0)
      .map((l) => {
        try {
          return JSON.parse(l);
        } catch {
          // una línea corrupta no puede tumbar el laboratorio entero
          return null;
        }
      })
      .filter(Boolean);
    return NextResponse.json({ corridas: filas });
  } catch {
    // todavía no hay histórico: no es un error, es una página vacía
    return NextResponse.json({ corridas: [] });
  }
}

export async function POST(req: Request) {
  let cuerpo: unknown;
  try {
    cuerpo = await req.json();
  } catch {
    return NextResponse.json({ ok: false, razon: "json inválido" }, { status: 400 });
  }
  try {
    await fs.mkdir(path.dirname(ARCHIVO), { recursive: true });
    await fs.appendFile(ARCHIVO, JSON.stringify(cuerpo) + "\n", "utf8");
    return NextResponse.json({ ok: true });
  } catch (e) {
    // sistema de archivos de solo lectura (deploy): se reporta y ya. La corrida
    // que el usuario está viendo no depende de que esto funcione.
    return NextResponse.json(
      { ok: false, razon: e instanceof Error ? e.message : "no se pudo escribir" },
      { status: 200 }
    );
  }
}
