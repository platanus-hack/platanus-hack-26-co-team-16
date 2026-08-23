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
| `GET /simulaciones/flujo` | **Corre el motor de verdad y transmite por SSE.** Parámetros: `aumento_pct` (0-50), `seed`, `cobertura` (top-K), `trayectorias` (1-5, de cuántas sale la banda), `parafrasis`, `tope_usd` (corte duro de la corrida ENTERA; vacío = se deriva de la corrida pedida, ver la tabla de abajo), `modo` (`llm` \| `reglas`). |

Eventos del flujo, en orden: `inicio` → (`decision`\*, `ronda`)\* → `fin` \| `error`.

- `decision` sale de la costura `al_decidir_arquetipo` de `behavior/rondas.py`: una celda acaba de decidir, en orden de terminación real. Trae su familia canónica, su `justificacion` y las razones de veto.
- `ronda` sale de `al_terminar_ronda`. Lleva `contracts/ronda.json` **intacto** bajo la llave `contrato`, y aparte el desglose de estrategias ponderado, el estado vivo por arquetipo y tres cifras derivadas (`masa_salarial_relativa`, `masa_salarial_cop`, `fraccion_bajo_minimo`) que `serializar.py` documenta con su `# SUPUESTO:`. `masa_salarial_cop` son los pesos absolutos (COP/mes): el navegador los rearmaba por su cuenta multiplicando el índice relativo por una base que reconstruía desde `poblacion.arquetipos` (S2-8), o sea que la única cifra en pesos de la pantalla se calculaba fuera de esta capa. Es el mismo número —la diferencia medida es 1,6e-05, el redondeo del alambre— calculado donde se puede auditar.

## Qué cuesta mover el slider

La pregunta del Q&A. La caché en disco se indexa por el prompt y el prompt lleva
la política, así que **cada posición nueva del slider es una corrida en frío**.
Repetir una posición ya corrida cuesta $0 y tarda medio segundo.

Base medida (R3, 23-08-2026, `behavior/README.md` §Costo): `claude-sonnet-5`
sobre la grilla real, **94 llamadas y USD 1,26** por trayectoria a cobertura
0,80, o sea **USD 0,0134 por llamada**. Las 5 trayectorias corren en SERIE
(`api/trayectorias.py` explica por qué), así que el tiempo también se multiplica.

| `cobertura` | Celdas al LLM | Peso cubierto | Llamadas (5 trayectorias) | En frío |
|---|---|---|---|---|
| 0,50 | 9 | 51,2% | 135 | $1,81 |
| 0,70 | 22 | 70,6% | 330 | $4,42 |
| **0,80** (default) | **31** | **80,2%** | **465** | **$6,23** |
| 0,90 | 44 | 90,6% | 660 | $8,85 |
| 1,00 | 81 | 100% | 1.215 | $16,29 |

El `tope_usd` por defecto es esa cifra × 1,25 de margen, calculada por request
con la misma `particionar_por_peso()` que usa el motor: no es una estimación. Por
eso el corte no salta en una corrida legítima, y si salta significa que algo se
desbocó. `TOPE_USD_MAXIMO = 25,00` es el techo absoluto y la única cifra que es
un juicio y no una cuenta (ver el comentario en `servidor.py`).

El evento `inicio` publica `llamadas_previstas` y `tope_usd`, así que la pantalla
puede decir qué va a costar y cuánto va a tardar ANTES de que alguien espere.

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
