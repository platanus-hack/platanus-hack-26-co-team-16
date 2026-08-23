# Último momento — el reparto de la última hora

> **Escrito:** 23-ago 08:40 · **Ventana:** 60 minutos · **Los tres trabajan en `main`, sin PR.**
>
> Tres personas, tres archivos de prompt, **cero archivos compartidos**. Esa es la única
> protección que queda cuando se trabaja en `main` sin revisión: si nadie toca el archivo de
> otro, no hay conflicto que resolver con sueño.

| Quién | Prompt | Zona exclusiva | Qué entrega |
|---|---|---|---|
| **Manu** | [`manu-backend.md`](manu-backend.md) | `api/`, `behavior/`, `engine/`, `scripts/` | La simulación maqueta que corre en <60 s en vivo + el tope que hoy la cortaría |
| **Dani** | [`dani-lienzo.md`](dani-lienzo.md) | `web/enjambre/componentes/` (menos `reporte/`), `app/page.tsx` | Items 5, 6, 7, 8, 9: animaciones, cifras, ronda, leyenda, pantalla de entrada |
| **Juanda** | [`juanda-reporte.md`](juanda-reporte.md) | `web/enjambre/app/reporte/`, `componentes/reporte/`, `lib/narrativa.ts`, docs raíz | Items 1, 3, 4: lenguaje del reporte, quitar «no hay que creerle», PDF |

## Reglas de `main` — las tres que importan

1. **Nadie toca un archivo que no esté en su fila de la tabla de abajo.** Si lo necesitas,
   avisas en el grupo y esperas; no lo editas «rapidito».
2. **Commit pequeño y frecuente**, y antes de cada push:
   `git pull --rebase origin main && git push`. Si el rebase da conflicto en un archivo
   ajeno, **para y avisa** — significa que alguien salió de su zona.
3. **Verifica antes de decir que está hecho.** `git diff --stat`, y el comando de verificación
   que trae cada prompt. Un reporte sin salida pegada es un reclamo, no evidencia.

## Tabla de archivos — quién toca qué

Si un archivo no está acá, nadie lo toca esta hora.

| Archivo | Dueño |
|---|---|
| `api/servidor.py`, `api/trayectorias.py`, `api/serializar.py` | **Manu** |
| `behavior/rondas.py`, `behavior/capa.py`, `behavior/cliente.py` | **Manu** |
| `scripts/` (todo) | **Manu** |
| `web/enjambre/componentes/enjambre/*` (Empresas, Onda, Escena, Personas, motorVisual) | **Dani** |
| `web/enjambre/componentes/Paneles/*` (Hero, BarraTiempo, Leyenda, Estrategias, ColumnaIzquierda) | **Dani** |
| `web/enjambre/componentes/Menu.tsx`, `Carga.tsx`, `Simulacion.tsx` | **Dani** |
| `web/enjambre/app/page.tsx` | **Dani** |
| `web/enjambre/app/reporte/page.tsx` | **Juanda** |
| `web/enjambre/componentes/reporte/Graficas.tsx` | **Juanda** |
| `web/enjambre/lib/narrativa.ts` | **Juanda** |
| `VALIDATION.md`, `README.md`, `AGENTS.md` | **Juanda** |
| `web/enjambre/estado/*`, `web/enjambre/lib/formato.ts` | **NADIE** — si hace falta, se avisa |

> ⚠️ **La trampa que va a pasar si nadie la nombra:** la frase «dónde no hay que creerle» está
> en **dos** sitios — `componentes/Menu.tsx:74` (pantalla de entrada, **de Dani**) y
> `app/reporte/page.tsx:238` (**de Juanda**). Cada uno borra la suya. No la del otro.

---

## Contexto: qué acaba de arreglar Manuel, y qué sigue abierto

Verificado leyendo el código del merge (PR #38), no el handoff.

### Cerrado ✅

| Qué | Cómo | Commit |
|---|---|---|
| Las 5 trayectorias iban en serie (~23 min) | `decidir_arquetipo()` acepta `parafrasis_fija`; murió el parche al global `behavior.capa.parafrasis`; `ThreadPoolExecutor` en `trayectorias.py:143`. **Medido: 23 min → ~5** | `a4e1429` |
| El candado mataba la URL pública | Clase `GuardianCorrida` con token por turno y reloj monotónico: recupera el huérfano a los 15 min y un `finally` tardío no puede soltar la corrida nueva | `8083ce0` |
| La pantalla enfrentaba 17,99% contra 30,57% | `serializar.py` separa `tasa_informalidad_observada` (empleados de firma) de `tasa_informalidad_total_ciudad` | `7a76410` |
| A1 deploy→main, B1, B2, B3, C1, C3, media C2 | Rótulos y procedencia | `2c051c1` |

### Abierto ❌ — re-verificado hoy, ninguno se movió

| # | Qué | Evidencia (comando corrido hoy) | De quién |
|---|---|---|---|
| **H-7** | El tope de gasto no cuenta los reintentos del veto | `tope_derivado(0.50, 2)` = **$0,60** y el costo real @1,31× es **$0,72**. **CORTA en las 4 configuraciones de la maqueta** | **Manu — paso 0** |
| **O1** | `paralelismo` sigue en `8` (`rondas.py:220`) y **no es perilla de la API** | `grep -n paralelismo api/servidor.py` → 0 resultados | **Manu** |
| **H-2** | `prob_fiscalizacion` publica 62,94%; el riesgo del evasor es **0,99%** | `rondas.py:356` intacto. 18/81 celdas clavadas en p=100% con 51,8% del peso y 0,03% de los evasores | Manu (aditivo) |
| **H-5** | `fallback`/`sin_salida` cuentan decisiones, no población | `rondas.py:546` intacto. Publicado **0,6296** vs ponderado **0,7327** (+10,3 pp) | Manu / Nico |
| **H-1** | `make reproduce` revienta con exit 1 | Corrido hoy: `exit 1`. No pasa `cobertura_llm`, manda 81 celdas a una caché de 31 | Manu (2 líneas) |
| **H-10** | SDK sin `timeout` ni `max_retries` (hereda 600 s) | `cliente.py:105` intacto | Manu |
| **H-4** | `subir_precios` y `renegociar` no mueven ningún número, y son las únicas dos que el veto **nunca** rechaza | 27% de las decisiones. El 81,5% del peso termina en decisiones inertes | **Declarar, no arreglar** |
| **H-3** | `alfa = 1,875` es un parámetro libre ajustado al placebo | Con `alfa=0` el modelo predice 95,67% y el placebo se mueve +77,68 pp | **Juanda — declararlo** |

Detalle completo con evidencia: [`../agents/auditoria-motor/2026-08-23-motor-y-agregacion.md`](../agents/auditoria-motor/2026-08-23-motor-y-agregacion.md)
y [`../agents/hallazgos-dani-cache-decisiones.md`](../agents/hallazgos-dani-cache-decisiones.md).
