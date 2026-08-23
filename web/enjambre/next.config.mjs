/** @type {import('next').NextConfig} */
const config = {
  // La API Python corre aparte (uvicorn :8000). El navegador habla solo con
  // Next; esto evita CORS en dev y en el deploy detrás del mismo dominio.
  async rewrites() {
    const api = process.env.ENJAMBRE_API ?? "http://localhost:8000";
    return [{ source: "/api/:path*", destination: `${api}/:path*` }];
  },
};

export default config;
