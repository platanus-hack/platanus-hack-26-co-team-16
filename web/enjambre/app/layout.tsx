import type { Metadata } from "next";
import { IBM_Plex_Mono, IBM_Plex_Sans, Newsreader } from "next/font/google";
import "./globals.css";

const serif = Newsreader({
  subsets: ["latin"],
  style: ["normal", "italic"],
  weight: ["400", "500", "600"],
  variable: "--fuente-serif",
});
const sans = IBM_Plex_Sans({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  variable: "--fuente-sans",
});
const mono = IBM_Plex_Mono({
  subsets: ["latin"],
  weight: ["400", "500"],
  variable: "--fuente-mono",
});

export const metadata: Metadata = {
  title: "ENJAMBRE · simulación de política laboral",
  description:
    "La corrida real del simulador de cumplimiento, transmitida en vivo: celdas empleadoras GEIH decidiendo frente a un alza del costo laboral formal.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <head>
        {/* Solo para verificación automatizada (?prueba en la URL): en una
            pestaña oculta Chrome pausa requestAnimationFrame y el enjambre no
            anima; este shim lo reemplaza por un bucle de MessageChannel que no
            se estrangula. Ningún usuario normal pasa por acá. */}
        <script
          dangerouslySetInnerHTML={{
            __html: `if (new URLSearchParams(location.search).has("prueba")) {
  (function () {
    var mc = new MessageChannel();
    var cbs = [];
    var ultima = performance.now();
    mc.port1.onmessage = function () {
      var ahora = performance.now();
      if (ahora - ultima >= 16 && cbs.length) {
        var lista = cbs; cbs = []; ultima = ahora;
        for (var i = 0; i < lista.length; i++) { try { lista[i](ahora); } catch (e) {} }
      }
      mc.port2.postMessage(0);
    };
    window.requestAnimationFrame = function (cb) { cbs.push(cb); return 1; };
    window.cancelAnimationFrame = function () {};
    mc.port2.postMessage(0);
  })();
}`,
          }}
        />
      </head>
      <body className={`${serif.variable} ${sans.variable} ${mono.variable}`}>{children}</body>
    </html>
  );
}
