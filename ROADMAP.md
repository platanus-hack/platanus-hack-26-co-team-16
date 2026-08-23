# Hoja de ruta — de demo a plataforma

> **Qué es este archivo.** Lo que falta para que EL ENJAMBRE deje de ser el simulador de *una*
> política en *una* ciudad y pase a ser un banco de pruebas de políticas públicas. Cada fase trae
> **qué desbloquea**, **qué cuesta** y **el comando que verifica que se cerró**.
>
> No es una lista de deseos: cada línea sale de un defecto medido y anotado en el repo, con su
> archivo y su línea. Lo que ya está cerrado dice cómo comprobarlo; lo que no, dice qué falta.
>
> **Regla que hereda de [`VALIDATION.md`](VALIDATION.md):** una fase se declara cerrada cuando su
> comando lo demuestra, no cuando alguien la da por hecha.

## Dónde estamos hoy

| | Estado | Comprobable con |
|---|---|---|
| Población real de encuesta nacional | ✅ 6.692 personas GEIH → 4,2M expandidos, sha256 trazable | `python data/construir_poblacion.py` |
| Motor determinista con veto | ✅ 1.902 líneas, 70 tests | `make test` |
| Capa LLM con control de contaminación | ✅ fail-closed, 31 patrones | `python -m behavior.higiene` |
| Corrida reproducible sin API key | ✅ | `make run && make run` → *IDÉNTICO* |
| Backtest pre-registrado y publicado | ✅ con su signo, salga como salga | `make validate` |
| Curva política → informalidad, medida | ✅ 16 puntos, monótona, Spearman 0,96 | `python scripts/barrido_politicas.py --desde 0 --hasta 30 --paso 2` |
| **Una segunda política** | ❌ **fase 2** | — |
| **Otra ciudad u otro país** | ❌ **fase 3** | — |
| **Más de un usuario simultáneo** | ❌ **fase 5** | — |

**El resumen honesto:** el aparato de medición está terminado y es mejor que el del promedio de
proyectos comparables. Lo que está a medias es que sirva para *otra cosa* que el caso demo.

---

## Fase 1 · Que todo comando publicado corra `[CERRADA · 23-ago]`

Un repo que publica comandos que no funcionan gasta la credibilidad de los que sí.

| Qué | Estado | Comprobar |
|---|---|---|
| `scripts/run_simulacion.py` con artefacto canónico y manifiesto | ✅ | `make run` |
| Determinismo verificable por un tercero | ✅ | `make run && make run` |
| Candado **G1** medido en vez de bloqueado por construcción | ✅ **PASA** | `make validate` |
| `make test` incluye `api/` (eran 16 tests que el comando oficial no corría) | ✅ 104 tests | `make test` |
| `make reproduce` sale 0 y declara su modo efectivo | ✅ | `make reproduce` |
| Los targets que no pueden correr salen con código ≠ 0 | ✅ | — |

**Lo que sigue abierto de esta fase:**

- 🔴 **`scripts/barrido_politicas.py` revienta en Windows** al imprimir el informe:
  `UnicodeEncodeError` con la `Δ` de `Δprecios`. El JSON se escribe antes, así que falla después de
  trabajar. Se sortea con `PYTHONIOENCODING=utf-8`.
- **`--salida` se trata como directorio** en el mismo script.
- **El `Makefile` es POSIX-only** (`SHELL := /bin/bash`, `.venv/bin/python3`) y el equipo trabaja en
  Windows. Falta un `make.ps1` o declararlo.

---

## Fase 2 · La abstracción `Politica` — *la que cambia la categoría del proyecto*

**El problema, medido.** El motor está parametrizado por **un escalar**. `aumento_pct: float`
atraviesa las cinco capas —`api/servidor.py:292` → `api/trayectorias.py:61` →
`behavior/rondas.py:210` → `engine/veto.py:327` → `behavior/prompts/arquetipo.md:12`— y la
aritmética que lo consume está horneada a *"el costo laboral sube X%"* (`engine/veto.py:444`).

El contrato ya declara `politica: {tipo, aumento_pct}` (`contracts/ronda.json:5`), pero
**`tipo` no lo lee nadie**: `grep` de consumidores da cero. Es metadata muerta.

**Consecuencia:** un impuesto a la nómina, un subsidio a la contratación formal o una cuota no
tienen dónde entrar. Hoy "otra política" significa forkear el repo.

**Qué hay que construir:**

1. `engine/politica.py` — un `Protocol` con tres métodos:
   - `delta_costo(estado) -> np.ndarray` — lo que hoy hace a mano `engine/veto.py:444`
   - `mecanica_para_prompt() -> str` — el texto ya higienizado que hoy vive en
     `behavior/prompts/arquetipo.md:12`. **El control de contaminación se muda acá**, así que la
     abstracción refuerza el candado G2 en vez de debilitarlo.
   - `identidad() -> dict` — lo que llena `politica.tipo`, que por fin se lee.
2. Dos implementaciones, porque una sola no prueba que la abstracción sirva:
   `AlzaCostoLaboral(pct)` —la actual, que debe reproducir el artefacto canónico **bit a bit**, o
   sea que es un test de regresión— y una segunda real (`ImpuestoNomina`, `SubsidioContratacionFormal`).
3. Desbloquear `web/enjambre/componentes/Menu.tsx:44-48`, el botón *"Simular política personalizada ·
   bloqueado · próxima iteración"*.

**Costo:** $0 de LLM. Toca `engine/` (R2) y `behavior/` (R3).
**Cerrada cuando:** `make run` con dos políticas distintas produce dos artefactos distintos, y el de
`AlzaCostoLaboral(23)` es idéntico al de hoy.

---

## Fase 3 · Jurisdicción como dato, no como código

Hoy Colombia está **hardcodeada en 40+ sitios**. El inventario completo, irónicamente, ya existe:
`behavior/higiene.py:31-70` prohíbe exactamente los términos que revelan el país (`colombia`,
`bogota`, `cop`, `geih`, `dane`, años). **La abstracción está lograda en el prompt y en ninguna
otra capa.**

| Qué | Dónde está hoy |
|---|---|
| Régimen legal (SMLMV, parafiscales, ARL por clase de riesgo, art. 114-1, indemnización art. 64 CST) | `data/parametros_legales.py:38-117`, ~20 constantes de módulo |
| Geografía | `AREA_BOGOTA = 11` (`data/construir_poblacion.py:28`), `"ciudad": "Bogotá"` congelado en `contracts/agente.json:4` |
| Fuente demográfica | `descargar_geih.py` + `construir_poblacion.py`, 539 líneas de ETL del ANDA-DANE |
| Capacidad de fiscalización | `engine/fiscalizacion.py:80-118`, 4 constantes de módulo |

**Qué hay que construir:** `data/regimenes/co-2026.json` (el trabajo de citación por artículo ya
está hecho — es el más sólido del repo — solo hay que sacarlo del `.py`) y una interfaz
`FuenteDemografica` que convierta ENOE (México) o PNAD (Brasil) en un adaptador y no en un fork.

**Costo:** $0. **Cerrada cuando:** una segunda jurisdicción corre sin tocar `engine/` ni `behavior/`.

---

## Fase 4 · Higiene de repo que un tercero puede tomar

| Falta | Por qué importa |
|---|---|
| `pyproject.toml` | El proyecto **no es instalable**: todo depende de `sys.path.insert` y de correr desde la raíz |
| `.github/workflows/ci.yml` | **Cero CI hoy.** 104 tests que nadie garantiza que corran en un PR. Debe verificar que `make validate` salga con el código **declarado** (1 mientras haya compuertas bloqueadas), no con 0 |
| `ruff` + typecheck | Hay type hints y `Protocol`; nada los verifica (`AGENTS.md:147` lo tiene como PENDIENTE) |
| `pytest.ini` con `testpaths` | Es la causa raíz de que `api/` se quedara fuera del target oficial |
| `CONTRIBUTING.md` | Las reglas ya están escritas en `AGENTS.md:105-131`; falta el archivo donde la gente las busca |
| `CHANGELOG.md`, `SECURITY.md`, Dockerfile | — |
| Frontend sin lint ni tests | `package.json` solo tiene `dev`/`build`/`start` |

---

## Fase 5 · Operación: lo que hoy impide que lo use gente de verdad

1. 🔴 **El techo de escalabilidad es UNA corrida simultánea.** `GuardianCorrida`
   (`api/servidor.py:173`) vive en memoria del proceso, así que `render.yaml:36-38` **prohíbe
   explícitamente** más de una instancia. Mover el candado a almacenamiento compartido es lo que
   permite el segundo usuario.
2. 🔴 **Sin auth, sin rate limiting, y con `allow_origins=["*"]`** (`api/servidor.py:161`) sobre un
   endpoint que puede gastar hasta `TOPE_USD_MAXIMO = 25.0` por request y **sin tope acumulado entre
   corridas** (decisión consciente, `auditoria-final:105-106`). Un bucle anónimo vacía la bolsa del
   equipo. El acceso sin registro es regla no-negociable del repo; el rate limit no la rompe.
3. **Logging estructurado** — hoy es 100% `print()` (`api/servidor.py:216,421,431,525`).
4. **Persistencia real** — Supabase se decidió (`AGENTS.md:144`) y nunca entró. El histórico son
   5 líneas de JSONL y unos parquets en git.
5. **Versionado de API** — rutas sin `/v1`, OpenAPI deshabilitado.

---

## Deuda de modelo, aparte de la de ingeniería

No es hoja de ruta de producto, pero un revisor la va a buscar y está toda medida:

| # | Qué | Dónde | Costo |
|---|---|---|---|
| 1 | **Regenerar `data/prediccion_modelo.json`** — EL NÚMERO no se reproduce desde `main`: el artefacto tiene ronda 0 = 30,6% y 101 arquetipos; el motor de hoy arranca en 17,99% con 81 | `VALIDATION.md:40-75` | **~USD 8** |
| 2 | **El 81,5% del peso poblacional termina en decisiones inertes**: `subir_precios` y `renegociar` no mueven ningún número y son las únicas que el veto nunca rechaza | [H-4](docs/agents/defectos-motor-abiertos.md) | $0 |
| 3 | **La calibración base falla por tamaño**: el modelo produce **cero** informalidad en pyme y grande; toda la suya vive en micro (+7,5 pp). G3 no cumple el ±2 pp | [evidencia §E3](docs/evidencia/2026-08-23-E1-E2-E3.md) | $0 |
| 4 | **La cascada aporta +0,0 pp** en el camino determinista — medido, publicado, sin explicar | [evidencia §E2](docs/evidencia/2026-08-23-E1-E2-E3.md) | $0 |
| 5 | **El ruido de reformulación del prompt iguala a la señal** en el camino LLM (ruido/señal 0,74–0,92, y dos corridas dan signos opuestos) | `DEFECTOS.md` §2.1 | gasta LLM |
| 6 | **La banda con N=5 es literalmente min–max**, no p10/p90 | `VALIDATION.md` §Método | gasta LLM |
| 7 | **El seed es una etiqueta**, no una perilla | `api/servidor.py:80` | $0 |
| 8 | **El margen libre sobre nómina (0,18) no tiene fuente** y decide dónde cae el codo | `VALIDATION.md` §Dos parámetros | $0 |

---

## Cómo verificar el estado de todo esto, hoy

```bash
make test        # 104 tests, incluyendo api/
make run         # una corrida, con artefacto canónico
make run         # otra vez: debe decir "IDÉNTICO al anterior"
make validate    # G1 PASA · G2 y G3 bloqueadas y declaradas · EL NÚMERO
make supuestos   # los 93 supuestos marcados en el punto donde se toman
python scripts/barrido_politicas.py --desde 0 --hasta 30 --paso 2   # la curva, $0
```
