# Diagrama de flujo — cómo funciona la simulación

> Renderiza directo en GitHub (Mermaid). Dos flujos: el de una **corrida** (lo que ve el
> usuario) y el de **validación** (lo que ve el juez con `make validate`).
>
> **Actualizado 2026-08-22 (R2)** con el reloj de [ADR 0005](adr/0005-el-reloj-de-la-simulacion.md),
> la separación de [ADR 0006](adr/0006-fiscalizacion-es-estado-del-mundo.md), la forma
> funcional de [ADR 0007](adr/0007-forma-funcional-prob-sancion.md) y la asimetría de
> [ADR 0008](adr/0008-asimetria-firma-trabajador.md) 🔶.

## Flujo principal: una corrida

**Una ronda es un trimestre. El horizonte son nueve meses desde el decreto.**

```mermaid
flowchart TD
    subgraph PREP["Preparación (una sola vez)"]
        GEIH["Microdatos GEIH<br/>(DANE, ~240k hogares/año)"] --> ING["Ingesta data/<br/>limpieza + arquetipos"]
        ING --> POB[("poblacion.parquet<br/>agentes REALES anonimizados")]
        ING --> MOM[("momentos.json<br/>informalidad, salarios observados")]
        FUENTE["Fuentes MinTrabajo / OIT<br/>inspectores efectivos"] --> FISC[["EstadoFiscalizacion<br/>capacidad por trimestre<br/>NO es palanca del usuario"]]
    end

    subgraph CAL["Calibración base — candado 1"]
        MOM --> C1{"Mundo SIN política<br/>¿reproduce informalidad por sector,<br/>por tamaño, y el spike salarial?"}
        C1 -- "no" --> STOP["Nada de lo que sigue significa algo.<br/>Se cambia la métrica de validación,<br/>no el proyecto"]
    end

    U["Usuario mueve el slider:<br/>aumento 7% / 13,6% / 23%"] --> POL["Política → mecánica SIN nombre:<br/>'tu costo laboral formal sube X%'"]
    POB --> R0
    C1 -- "sí" --> R0
    POL --> R0["RONDA 0 · t=0, el decreto<br/>reacción ingenua<br/>(la proyección del gobierno: línea recta)"]

    R0 --> LOOP

    subgraph LOOP["Rondas 1 a 3 — un trimestre cada una"]
        AGG["Cada arquetipo VE el Agregado anterior:<br/>'el 30% ya evade, la prob. de sanción bajó a 4%'<br/>NO ve agentes individuales"] --> LLM["Capa LLM (Haiku, por arquetipo, cacheada):<br/>propone estrategia: cumplir / informalizar /<br/>despedir / absorber / renegociar"]
        LLM --> VETO{"Motor físico:<br/>¿es factible?<br/>(flujo de caja, reglas)"}
        VETO -- "NO: veto con razón<br/>(hasta 3 reintentos)" --> LLM
        VETO -- "agotados los 3" --> FALL["Estrategia terminal: cumplir<br/>se cuenta en n_fallback"]
        VETO -- "SÍ" --> TRAB{"¿El trabajador acepta?<br/>regla determinista:<br/>neto informal vs neto formal + prima"}
        TRAB -- "no acepta" --> NOOCURRE["La informalización propuesta<br/>NO ocurre. Es resultado, no veto"]
        TRAB -- "acepta" --> APL
        FALL --> APL
        NOOCURRE --> APL["Motor aplica decisiones<br/>(determinista, con seed por ronda)"]
        APL --> FISC2["Recalcula fiscalización:<br/>p = 1 - exp(-C / E)<br/>capacidad C FIJA, más evasores E<br/>= menos prob. de sanción ⇒ CASCADA"]
        FISC --> FISC2
        FISC2 --> NEXT{"¿ronda < 3?"}
        NEXT -- "sí" --> AGG
    end

    NEXT -- "no" --> DB[("Supabase:<br/>rondas + reacciones")]
    DB -- "Realtime" --> WEB["Next.js en vivo"]

    subgraph WEB_OUT["Lo que se ve"]
        CURVA["📈 Curva de la brecha:<br/>línea del gobierno vs cascada real"]
        MAPA["🗺️ Mapa distributivo:<br/>quién pierde, por sector × ingreso,<br/>CON banda de incertidumbre"]
        FEED["📰 Feed de decisiones en vivo"]
        HIST["👤 3-4 historias con cara<br/>(modelo grande, solo estas)"]
    end
    WEB --> CURVA & MAPA & FEED & HIST
```

## Flujo de validación: `make validate`

```mermaid
flowchart LR
    MV["make validate"] --> C1["1 · Calibración base:<br/>mundo SIN política debe reproducir<br/>la informalidad observada (GEIH)"]
    MV --> C2["2 · Backtest:<br/>predecir alzas históricas ya ocurridas<br/>sin ver el resultado, medido a 9 meses<br/>(se excluye 2020-21 / COVID)"]
    MV --> C3["3 · Contaminación:<br/>corrida re-skinneada (etiquetas inventadas)<br/>debe dar = que la canónica"]
    MV --> C4["4 · Ablación:<br/>corrida sin LLM (reglas fijas)<br/>¿el LLM aporta algo?"]
    MV --> C5["Control: p FIJO<br/>sin fiscalización endógena<br/>NO debe haber cascada"]
    C1 & C2 & C3 & C4 & C5 --> NUM["Imprime EL número<br/>(error + varianza + banda)<br/>→ va a VALIDATION.md<br/>acierte o no"]
```

**La corrida de control con `p` fijo** es nueva y es barata: si la cascada aparece igual sin
fiscalización endógena, entonces viene de otra parte y hay que saberlo antes del pitch, no
durante el Q&A ([ADR 0007](adr/0007-forma-funcional-prob-sancion.md)).

## Los tres momentos clave, en una línea cada uno

**El veto es la interfaz entre la creatividad y la física.** El LLM inventa lo que un
economista no enumeraría; el motor determinista mata lo que la plata no permite. Lo que
sobrevive a ambos filtros es lo que ningún otro método produce.

**El trabajador es el segundo filtro, y es aritmético.** Una firma puede querer informalizar
y no lograrlo. Cuánta informalización propuesta **no ocurre** es un resultado del modelo, no
un veto, y es dato para el mapa distributivo.

**La cascada nace de una división.** La capacidad de inspección `C` es fija; los evasores `E`
crecen. `p = 1 − exp(−C/E)` cae, y cada caída hace que evadir sea más barato para el
siguiente. Nadie programó "si muchos evaden, evade más": sale de repartir un número fijo de
inspecciones entre un número creciente de infractores.
