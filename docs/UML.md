# UML — Estructura de la idea

> Diagrama de clases del dominio. Renderiza directo en GitHub (Mermaid).
> Corresponde a los contratos de `docs/PLAN.md` §4: `agente.json`, `decision.json`, `ronda.json`.

```mermaid
classDiagram
    direction TB

    class Poblacion {
        +origen: "GEIH microdatos DANE"
        +agentes: List~Agente~
        +momentos_observados: Momentos
        +cargar_desde_parquet(ruta)
        +muestrear(n, seed)
    }

    class Agente {
        <<abstract>>
        +id: str
        +ciudad: str
        +sector: str
        +arquetipo: str
        +factor_expansion: float
        +estado_actual(): Estado
    }

    class Trabajador {
        +ingreso_mensual_cop: int
        +formal: bool
        +educacion: str
        +tamano_empresa: int
    }

    class Empresa {
        +n_empleados: int
        +flujo_caja: float
        +productividad_marginal: float
        %% construida agrupando trabajadores GEIH por sector x tamaño
    }

    class Politica {
        +tipo: "cambio_costo_laboral"
        +aumento_pct: float
        +capacidad_fiscalizacion: float
        %% al LLM NUNCA se le pasa el nombre, solo la mecánica
        +como_mecanica(): str
    }

    class MotorFisico {
        <<determinista, con seed>>
        +seed: int
        +costo_formal(salario, factor_prestacional)
        +costo_informal(salario, riesgo_sancion)
        +prob_fiscalizacion(evasores): float
        +vetar(d: DecisionPropuesta): Veto
        +aplicar(decisiones): EstadoMundo
    }

    class CapaConductual {
        <<LLM por arquetipo, no por agente>>
        +modelo_masa: "haiku"
        +modelo_narrativa: "modelo grande"
        +cache_disco: HashCache
        +presupuesto_tope_usd: float
        +proponer(arquetipo, mecanica, agregado): DecisionPropuesta
        +narrar(agente): Historia
    }

    class DecisionPropuesta {
        +agente_id: str
        +ronda: int
        +estrategia: "cumplir|informalizar|despedir|absorber|renegociar"
        +detalle: dict
        +justificacion: str
        +veto: Veto
    }

    class Veto {
        +factible: bool
        +razon: str
    }

    class MotorEquilibrio {
        <<mejor respuesta, 3-4 rondas — NO convergencia>>
        +max_rondas: int = 4
        +ronda_0_ingenua(): Ronda
        +iterar(agregado_anterior): Ronda
    }

    class Ronda {
        +simulacion_id: str
        +ronda: int
        +tasa_informalidad: float
        +prob_fiscalizacion: float
        +empleo_relativo: float
        +banda: Banda
    }

    class Simulacion {
        +id: str
        +seed: int
        +politica: Politica
        +rondas: List~Ronda~
        +brecha(): float
        %% brecha = ronda 3 - ronda 0: EL producto
    }

    class Validador {
        +calibracion_base(momentos): Error
        +backtest_historico(alzas_2000_2019_2022_2025): Error
        +test_reskinning(): bool
        +ablacion_llm(): Diff
        +make_validate(): "imprime EL número"
    }

    class Interfaz {
        <<Next.js + Supabase Realtime>>
        +slider_politica: [7, 13.6, 23]
        +curva_cascada: Chart
        +mapa_distributivo: Chart
        +feed_decisiones: Realtime
        +historias: List~Historia~
    }

    Poblacion "1" *-- "miles" Agente
    Agente <|-- Trabajador
    Agente <|-- Empresa
    Simulacion --> Politica
    Simulacion --> Poblacion
    Simulacion "1" *-- "4" Ronda
    MotorEquilibrio --> Ronda : produce
    MotorEquilibrio --> CapaConductual : pide propuestas
    CapaConductual --> DecisionPropuesta : genera
    DecisionPropuesta --> Veto
    MotorFisico --> Veto : emite
    MotorFisico ..> DecisionPropuesta : veta o acepta
    MotorFisico --> Politica : lee mecánica
    Validador ..> Simulacion : audita
    Validador ..> Poblacion : compara momentos
    Interfaz ..> Ronda : suscrita via Realtime
    Interfaz ..> Simulacion : dispara POST /simulaciones
```

## Lectura del diagrama en 4 frases

1. **`Poblacion`** no se genera: se **carga** desde la GEIH — por eso `Trabajador` tiene los atributos de la encuesta y `factor_expansion` para escalar a la ciudad.
2. El bucle central es `MotorEquilibrio → CapaConductual → DecisionPropuesta → MotorFisico.vetar()`: el LLM propone, el motor determinista dispone. Ninguna decisión no factible sobrevive.
3. **`Politica.como_mecanica()`** es el control de contaminación hecho código: el LLM solo ve la mecánica ("tu costo laboral sube X%"), nunca el nombre.
4. **`Simulacion.brecha()`** — la distancia entre la ronda 0 (lo que el gobierno proyecta) y la ronda 3 (la cascada) — es el producto entero.
