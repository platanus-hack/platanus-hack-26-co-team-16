# Resultado V0 — el backtest, con dos episodios

> **Qué es este archivo.** La medición cruda que alimenta a `VALIDATION.md`. Aquí van los números y
> cómo se obtuvieron; la interpretación y los umbrales viven allá. Dueño: Alejo (R1).
>
> Todo lo de aquí sale de correr `data/construir_poblacion.py` **sin tocar la lógica** sobre tres
> años de GEIH. Que sea literalmente el mismo código en los tres extremos es lo que hace que las
> comparaciones signifiquen algo.

## La serie de tres años

| Año | SMLMV | Alza | Informalidad (proxy, Bogotá, ene–jun) | Pico salarial observado |
|---|---|---|---|---|
| 2024 | 1.300.000 | — | **32,01 %** | **1.300.000** |
| 2025 | 1.423.500 | +9,5 % | **34,64 %** | **1.420.000** |
| 2026 | 1.750.905 | +23,0 % | **30,57 %** | **1.750.000** |

**El pico salarial encuentra el mínimo legal él solo, los tres años.** Nadie se lo dijo al pipeline:
la moda de la distribución de ingresos cae en 1.300.000, 1.420.000 y 1.750.000 contra unos mínimos
legales de 1.300.000, 1.423.500 y 1.750.905. Las diferencias son redondeo del encuestado. Es la
mejor evidencia de que la capa de datos lee la realidad, y sostiene el patrón **P3** en tres años
independientes en vez de uno.

## Los dos episodios

| | Alza | Δ informalidad observado |
|---|---|---|
| **Episodio 1** · 2024 → 2025 | +9,5 % | **+2,63 pp** |
| **Episodio 2** · 2025 → 2026 | +23,0 % | **−4,07 pp** |

**El modelo predice que la informalidad sube con cada alza, y más cuanto mayor sea el alza.** Lo
observado va en direcciones opuestas entre los dos episodios, y la magnitud del movimiento real está
entre 2 y 4 puntos, no entre 28 y 45.

### Qué se puede concluir y qué no

**Sí se puede decir:** el modelo está mal escalado por un orden de magnitud, y eso no depende del
signo ni de qué episodio se mire. Un movimiento real de ±4 pp contra una predicción de +33 pp es un
problema de escala, no de calibración fina. También refuerza el baseline de persistencia: el tamaño
del cambio anual de la informalidad **es** de unos pocos puntos, así que "2026 = 2025" es un rival
difícil de vencer y el modelo ni se acerca.

**NO se puede decir** que el salario mínimo no tenga efecto sobre la informalidad. Son dos episodios,
confundidos con todo lo demás que pasó: la reforma laboral (Ley 2466 de 2025), la jornada de 42 horas
desde julio de 2026, el ciclo, y los cambios de medición. **El proyecto declara desde el principio que
no es un modelo macro** (`docs/PLAN.md` D8): esa limitación es justamente la que impide leer estos
deltas como el efecto causal de la política. Se reportan como lo que son — el resultado observado
contra el que el modelo se puntúa — y nada más.

**Que las direcciones se opongan es informativo en sí:** dice que en esta ventana la informalidad de
Bogotá no está dominada por el salario mínimo. Un modelo que le atribuye ±33 pp de movimiento está
sobreatribuyendo, aunque acertara el signo.

## Cómo se obtuvo

```bash
python data/descargar_geih.py     --anio 2024   # catalogo 819
python data/descargar_geih.py     --anio 2025   # catalogo 853
python data/construir_poblacion.py --anio 2024
python data/construir_poblacion.py --anio 2025
python scripts/validate.py                      # imprime EL numero
```

**Los ids de descarga no se adivinan:** se leen de la página de ANDA en tiempo de ejecución y el
script se niega a correr si no encuentra exactamente uno por mes. Control: redescubre los seis de
2026 y coinciden con los que estaban verificados a mano.

### Tres variantes de empaquetado, y por qué importan

El DANE no empaqueta igual todos los meses, ni siquiera dentro del mismo año. En 2024 conviven las
tres a la vez:

| Variante | Meses | Ruta hasta los módulos |
|---|---|---|
| Carpeta anidada | ene, feb 2024 | `GEIH_2024_enero/Ene_2024/CSV/` |
| Directa | may, jun 2024 · todo 2025 y 2026 | `GEIH_2025_enero/CSV/` |
| **ZIP dentro del ZIP** | mar, abr 2024 | `GEIH_2024_marzo/CSV/CSV/` |

Y los nombres de archivo cambian de año: `Enero 2026.zip`, `Ene_2024.zip`, `Mayo_2024 1.zip`. Sin
manejar esto, 2024 quedaba con cuatro meses de seis y dos carpetas vacías — que es peor que fallar,
porque el promedio semestral se habría calculado sobre cuatro meses sin que nadie lo notara.

`construir_poblacion.py` ya no busca "la carpeta que se llama CSV" sino **la que contiene
`Ocupados.CSV`**, y revienta si encuentra más de una en vez de adivinar: mezclar dos meses en
silencio es exactamente el error que no se puede permitir acá.

## El invariante que protege todo esto

Después de cada cambio de rutas, regenerar 2026 tiene que reproducir `data/poblacion.parquet` **byte
por byte** contra lo que está en `main`, y `data/momentos.json` con contenido idéntico. Verificado.
Si eso se rompe, la comparación entre años deja de ser válida y el backtest no significa nada.
