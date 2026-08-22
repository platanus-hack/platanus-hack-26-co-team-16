# `api/` — FastAPI

**Dueño: Manuel (R2)** · rama `rol/backend`

## Qué va aquí

- `POST /simulaciones`: recibe política + seed, corre el motor, persiste cada ronda en Supabase.
- El esquema de Supabase (se acuerda con Dani, que consume por Realtime).

## Qué NO va aquí

- Lógica de simulación (importa de `engine/`, no la reimplementa).
- Auth, cuentas ni multi-tenant: un extraño debe poder usar el demo sin registrarse.
