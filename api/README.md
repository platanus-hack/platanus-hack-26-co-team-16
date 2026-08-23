# `api/` — FastAPI

**Dueño: Manuel (R2)** · rama `rol/backend`

## Qué hay hoy

`servidor.py` — la API del enjambre. Levanta con:

```bash
make servidor          # equivale a: uvicorn api.servidor:app --port 8000
```

| Ruta | Qué hace |
|---|---|
| `GET /poblacion` | La grilla estática de celdas empleadoras (81 celdas de `data/empresas.parquet`) + los momentos observados. Es lo que el frontend precarga para dibujar el enjambre. |
| `GET /simulaciones/flujo` | **Corre el motor de verdad y transmite por SSE.** Parámetros: `aumento_pct` (0-50), `seed`, `cobertura` (top-K), `parafrasis`, `tope_usd`, `modo` (`llm` \| `reglas`). |

Eventos del flujo, en orden: `inicio` → (`decision`\*, `ronda`)\* → `fin` \| `error`.

- `decision` sale de la costura `al_decidir_arquetipo` de `behavior/rondas.py`: una celda acaba de decidir, en orden de terminación real. Trae su familia canónica, su `justificacion` y las razones de veto.
- `ronda` sale de `al_terminar_ronda`. Lleva `contracts/ronda.json` **intacto** bajo la llave `contrato`, y aparte el desglose de estrategias ponderado, el estado vivo por arquetipo y dos cifras derivadas (`masa_salarial_relativa`, `fraccion_bajo_minimo`) que `serializar.py` documenta con su `# SUPUESTO:`.

Cada ronda imprime en la terminal las cifras que el motor calculó, para poder
contrastar contra lo que muestra la pantalla.

`serializar.py` traduce los objetos de `behavior/` a esos eventos. Regla: cero
números inventados — lo que el motor no produce (contrataciones, productividad,
utilidad) no se serializa, y la interfaz no lo muestra.

## Decisiones tomadas

- **SSE en vez de Supabase Realtime.** La spec original de este archivo era `POST /simulaciones` + persistencia en Supabase; Supabase nunca entró al repo y a esta altura sumar un servicio externo cuesta más de lo que da. SSE entrega el mismo "en vivo" contra el mismo motor. Si Supabase entra después, `al_terminar_ronda` es la misma costura.
- **Una corrida a la vez** (candado global): el motor satura el pool de hilos y el presupuesto de LLM es uno solo.

## Qué NO va aquí

- Lógica de simulación (importa de `engine/` y `behavior/`, no la reimplementa).
- Auth, cuentas ni multi-tenant: un extraño debe poder usar el demo sin registrarse.
