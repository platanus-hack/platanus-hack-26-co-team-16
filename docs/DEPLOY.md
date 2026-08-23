# El deploy — runbook

> **Dueño:** Juanda (R5 · integración). **Configuración:** [`render.yaml`](../render.yaml) en la raíz.
> **Humo:** `make humo URL=<la url>`.
>
> Este archivo es para las 4am: qué está corriendo, cómo se arregla y qué hacer si se cae en vivo.

## Qué está desplegado

```
  navegador
     │  https
     ▼
  [enjambre-web]  Next.js · sirve la interfaz y hace de PROXY de /api/*
     │  https (ENJAMBRE_API)
     ▼
  [enjambre-api]  FastAPI · uvicorn · corre behavior/ + engine/ y transmite SSE
```

| Servicio | URL | Qué es |
|---|---|---|
| `enjambre-web` | **https://enjambre-web.onrender.com** | **La URL de la entrega.** Es la que va en `platanus-hack-project.jsonc` |
| `enjambre-api` | https://enjambre-api.onrender.com | El motor. Útil para depurar: `GET /poblacion` y `GET /simulaciones/flujo` |

La interfaz es 100% cliente y pide `/api/...` **relativo**, así que el navegador nunca habla directo
con la API: el servidor de Next hace de proxy. Por eso son dos servicios y no uno, y por eso el
frontend **no** puede ser un sitio estático.

## Por qué Render y no Vercel

Porque el proxy tiene que sostener un stream largo. Una corrida LLM medida tarda **166 s** con una
paráfrasis, y más con cinco.

| | Límite del proxy | Resultado |
|---|---|---|
| Vercel (rewrite a destino externo) | **120 s** → `ROUTER_EXTERNAL_TARGET_ERROR` | la corrida muere a mitad, siempre |
| Render (web service) | **100 minutos** | alcanza de sobra |

Ventaja lateral: con los dos servicios en Render **no hubo que tocar un solo archivo de `web/`**, que
es de otro dueño (R4). Con Vercel habría tocado cambiar `estado/flujo.ts` para que el navegador
hablara directo con la API.

## Los créditos: qué pagan y qué no

Los $50 de Render pagan **el servidor**. El "cooldown" —Render apaga un servicio *Free* que pasa 15
minutos sin tráfico y tarda ~1 minuto en volver— **no se quita con créditos, se quita eligiendo un
plan de pago**, que es lo que los créditos cubren. Por eso `render.yaml` dice `plan: standard` en los
dos servicios y no `free`.

```
  standard × 2  =  $50/mes  ≈  $1,67/día   →  el hackathon completo cuesta ~$3
```

Se cobra prorrateado por segundo, y el crédito se descuenta solo de la factura del **workspace**. La
única forma de perderlo es crear los servicios en un workspace distinto al que tiene el saldo.

> **Acordarse de apagarlo.** $50 de crédito ÷ $50/mes ≈ **30 días de autonomía**: a partir de
> ~23-sep-2026 la factura le empieza a caer a la tarjeta. Cuando pase la votación, en cada servicio
> *Settings → Suspend* (o bajarlos a `free`, que los deja en línea pero con spin-down). No depende de
> que alguien se acuerde en el momento: está escrito acá.

**Anthropic es otra factura.** Cada clic en "Simular" son llamadas reales al modelo (~$1,26 medidos
con Sonnet 5 y una paráfrasis), y las paga la cuenta de la llave que esté en `ANTHROPIC_API_KEY`. Los
créditos de Render no tienen nada que ver con eso.

## Crear los servicios (una sola vez)

1. Render → **New → Blueprint** → repo **espejo** `vibe-coders-team/platanus-hack-26-T16-simulations`,
   rama `rol/integracion-deploy`. Render lee `render.yaml` y propone los dos servicios.
   *(La plataforma no puede conectarse al repo de la organización, solo a uno propio. Ver la sección
   de deploy del `README.md`.)*
2. Confirmá que el workspace sea el que tiene los $50 y que los dos servicios digan **Standard**, no
   Free.
3. Render pide los dos valores marcados `sync: false`:
   - `ANTHROPIC_API_KEY` → la llave (empieza con `sk-ant-`). **Nunca se commitea.**
   - `ENJAMBRE_API` → todavía no existe la URL de la API: poné cualquier cosa y seguí al paso 4.
4. Cuando `enjambre-api` termine de desplegar, copiá su URL pública y pegala en `ENJAMBRE_API` de
   `enjambre-web`, **sin barra final**. Guardar dispara un redeploy, y ese redeploy es el que
   importa (ver abajo).
5. `make humo URL=<url de enjambre-web>` → tiene que decir `OK`.

### ⚠️ La trampa cara: `ENJAMBRE_API` se lee en el BUILD

`next build` evalúa `rewrites()` y **congela el destino** dentro de `.next/routes-manifest.json`.
Verificado a mano en este repo: un servidor arrancado con otro `ENJAMBRE_API` siguió proxyando al
destino que quedó horneado.

```json
{ "source": "/api/:path*", "destination": "http://localhost:8000/:path*" }
```

O sea: si el build corre sin la variable, el frontend queda apuntando a `localhost:8000` **dentro de
su propio contenedor**. La página carga perfecta, el enjambre se dibuja y **ninguna simulación
arranca nunca**. Falla en silencio, que es la peor forma de fallar.

- Cambiar la variable **no basta con reiniciar**: hay que volver a buildear. Editarla en el dashboard
  ya dispara un deploy completo, así que alcanza con guardarla.
- Síntoma en producción: la home carga y `make humo` falla en el paso 1 (`/api/poblacion` no
  responde 200).

## Verificar que sirve

```bash
make humo URL=https://enjambre-web.onrender.com          # $0, ~2 s
make humo URL=https://enjambre-web.onrender.com LLM=1    # el camino real, gasta créditos
```

El humo abre el SSE y consume los eventos a medida que llegan: comprueba que llegan las 4 rondas y el
evento `fin`, y que la ronda 0 arranca en la informalidad que declara la GEIH. **Un stream que se
corta a la mitad se ve igual que uno completo si uno lee el cuerpo de un golpe** — por eso el script
existe y por eso no es un `curl` a la home.

Además, en los logs de `enjambre-api` tienen que aparecer los `[ronda N]` con las mismas cifras que
muestra la pantalla. Es la verificación de que la interfaz no está inventando nada.

## Calentamiento antes del pitch

La caché en disco del contenedor (`behavior/.cache/`) **no sobrevive a un redeploy**. Después del
último deploy, y antes de presentar:

```bash
make humo URL=<url> LLM=1        # ~3 min, paga una corrida
```

Eso deja la corrida canónica cacheada: el juez que mueva el slider a 23% la ve al instante en vez de
esperar tres minutos. Con otros parámetros vuelve a costar y a tardar, que es lo honesto.

## Si se cae en vivo

1. **Mirá los logs** del servicio en el dashboard (pestaña *Logs*). Un fallo del motor sale ahí como
   evento `error` con su mensaje.
2. **Rollback**: pestaña *Deploys* → el último deploy verde → **Rollback**. Es instantáneo y no
   depende de git.
3. **Respaldo local**: `make servidor` + `make enjambre` corren lo mismo en el portátil. La demo se
   hace desde `localhost` y se dice que el deploy se cayó. Requiere la llave en el entorno.
4. **Respaldo sin llave y sin red**: hoy **no existe**. `behavior/cache-demo.json` (nivel 2 de la
   ADR 0009) todavía no está en el repo; sin él, `?modo=reglas` es lo único que corre a $0, y la
   interfaz no lo expone.

## Límites conocidos de este deploy

Se declaran acá porque un juez los va a encontrar:

- **Una corrida a la vez.** `api/servidor.py` tiene un candado global (`_ocupado`); el segundo
  visitante que llegue mientras otro simula recibe *"ya hay una corrida en curso"*. Por eso el
  servicio corre con **una sola instancia** y sin autoscaling: el candado vive en memoria del
  proceso y con dos instancias dejaría de existir.
- **Sin auth y sin registro**, que es una regla del repo, no un descuido: *"un extraño con el link
  tiene que poder usarlo"*. La contracara es que cualquiera puede disparar corridas que se pagan.
- **El tope de gasto es por corrida, no por día** (`tope_usd`, hoy 3.0). Con varias paráfrasis una
  sola corrida puede no caber en él y cortarse a mitad.
- **La caché no persiste entre deploys** (no hay disco montado). Primera corrida después de cada
  deploy: minutos y dólares.
