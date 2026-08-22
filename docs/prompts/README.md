# Prompts por persona — cómo usar esta carpeta

Cada quien abre **su propia sesión de Claude Code** en la raíz del repo y pega el contenido COMPLETO de su archivo como primer mensaje:

- `alejo.md` → R1 Datos · rama `rol/datos`
- `manuel.md` → R2 Backend · rama `rol/backend`
- `nico.md` → R3 Conductual/equilibrio · rama `rol/conductual`
- `dani.md` → R4 Diseño/interfaz · rama `rol/interfaz`
- `juanda.md` → R5 Integración/validación/pitch · rama `rol/integracion`

## Orden de trabajo global (quién desbloquea a quién)

```
H0 ──► TODOS EN PARALELO desde el minuto 0, PERO con este orden de desbloqueo:

1. Alejo publica contracts/*.json (H+2) ──► desbloquea a Manuel, Nico y Dani
   (hasta entonces, cada uno usa los ejemplos de docs/PLAN.md §4 tal cual)
2. Juanda deja el deploy hola-mundo andando (H+4) ──► desbloquea el flujo de integración
3. Manuel y Nico acuerdan el contrato del VETO (H+4, juntos, 30 min) ──► desbloquea la integración motor↔LLM
4. Manuel entrega motor punta a punta con datos falsos (H+10) ──► desbloquea la corrida completa
5. Alejo entrega poblacion.parquet real (H+8) ──► desbloquea calibración (Juanda) y arquetipos reales (Nico)
6. Calibración base cerrada (H+20) ──► desbloquea backtest (Juanda) y test pico y placa (Nico+Juanda)
```

**Regla clave: nadie ESPERA a nadie.** Todos construyen contra los contratos con datos falsos desde H0. Los desbloqueos de arriba son cuándo se REEMPLAZA lo falso por lo real.

## Flujo de git (las 5 sesiones en paralelo sin pisarse)

1. Cada quien SOLO en su rama (`rol/...`) y SOLO en sus carpetas (ver `docs/ROLES.md`).
2. Commits pequeños y frecuentes. **Todo entra a `main` por Pull Request, mínimo cada 6 horas** (en el standup de pie) — nadie pushea directo a `main`, y ramas largas = infierno de integración en la hora 30. Plantilla en `.github/pull_request_template.md`; lo revisa alguien distinto de quien lo escribió.
3. Orden de merge cuando hay conflicto de dependencia: `contracts` (Alejo) → `engine/api` (Manuel) → `behavior` (Nico) → `web` (Dani). Juanda mergea docs/tests cuando sea.
4. `main` SIEMPRE corre. Si tu merge rompe `main`, lo arreglas tú antes de volver a tu rama.
5. Push va a los dos remotos automáticamente (ya configurado). El deploy sale del repo espejo.
