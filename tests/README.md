# `tests/` — Núcleo verificable

**Dueño: Juanda (R5)**, con Manuel (R2) para el motor · rama `rol/integracion`

Los tests son la prueba más barata de que hay ingeniería real. Prioridad: el núcleo determinista antes que cualquier otra cosa.

## Qué probar primero

1. **Determinismo:** mismo seed, mismo resultado, dos corridas.
2. **El veto:** una propuesta imposible (sin flujo de caja) se rechaza con razón.
3. **Fiscalización endógena:** más evasores baja la probabilidad de sanción.
4. **Contratos:** lo que produce el motor valida contra `contracts/ronda.json`.

Se corren con `make test`, y en cada PR cuando el CI esté cableado (~H+6).
