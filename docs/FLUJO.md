# Diagrama de flujo — cómo funciona la simulación

> Renderiza directo en GitHub (Mermaid). Dos flujos: el de una **corrida** (lo que ve el usuario) y el de **validación** (lo que ve el juez con `make validate`).

## Flujo principal: una corrida

```mermaid
flowchart TD
    subgraph PREP["Preparación (una sola vez)"]
        GEIH["Microdatos GEIH<br/>(DANE, ~240k hogares/año)"] --> ING["Ingesta data/<br/>limpieza + arquetipos"]
        ING --> POB[("poblacion.parquet<br/>agentes REALES anonimizados")]
        ING --> MOM[("momentos.json<br/>informalidad, salarios observados")]
    end

    U["Usuario mueve el slider:<br/>aumento 7% / 13,6% / 23%"] --> POL["Política → mecánica SIN nombre:<br/>'tu costo laboral formal sube X%'"]
    POB --> R0
    POL --> R0["RONDA 0 — reacción ingenua<br/>(la proyección del gobierno: línea recta)"]

    R0 --> LOOP

    subgraph LOOP["Rondas 1 a 3 — mejor respuesta"]
        AGG["Cada arquetipo VE el agregado:<br/>'el 30% ya evade, prob. de sanción bajó a 4%'"] --> LLM["Capa LLM (Haiku, por arquetipo, cacheada):<br/>propone estrategia: cumplir / informalizar /<br/>despedir / absorber / renegociar"]
        LLM --> VETO{"Motor físico:<br/>¿es factible?<br/>(plata, reglas, restricciones)"}
        VETO -- "NO: veto con razón" --> LLM
        VETO -- "SÍ" --> APL["Motor aplica decisiones<br/>(determinista, con seed)"]
        APL --> FISC["Recalcula fiscalización:<br/>capacidad FIJA / más evasores<br/>= menos prob. de sanción ⇒ CASCADA"]
        FISC --> NEXT{"¿ronda < 3?"}
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
    MV --> C2["2 · Backtest:<br/>predecir alzas históricas ya ocurridas<br/>sin ver el resultado<br/>(se excluye 2020-21 / COVID)"]
    MV --> C3["3 · Contaminación:<br/>corrida re-skinneada (etiquetas inventadas)<br/>debe dar = que la canónica"]
    MV --> C4["4 · Ablación:<br/>corrida sin LLM (reglas fijas)<br/>¿el LLM aporta algo?"]
    C1 & C2 & C3 & C4 --> NUM["Imprime EL número<br/>(error + varianza + banda)<br/>→ va a VALIDATION.md<br/>acierte o no"]
```

## El momento clave, en una línea

**El veto es la interfaz entre la creatividad y la física:** el LLM inventa lo que un economista no enumeraría; el motor determinista mata lo que la plata no permite. Lo que sobrevive a ambos filtros es lo que ningún otro método produce.
