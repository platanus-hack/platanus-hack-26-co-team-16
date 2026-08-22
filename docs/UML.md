# UML — Estructura de la idea

> Diagrama de clases del dominio. Renderiza directo en GitHub (Mermaid).
> Corresponde a los contratos de `docs/PLAN.md` §4 (`agente.json`, `decision.json`,
> `ronda.json`) y a las decisiones de [`docs/IDEA.md`](IDEA.md).
>
> **Actualizado 2026-08-22 (R2)** con [ADR 0005](adr/0005-el-reloj-de-la-simulacion.md) ·
> [0006](adr/0006-fiscalizacion-es-estado-del-mundo.md) ·
> [0007](adr/0007-forma-funcional-prob-sancion.md) ·
> [0008](adr/0008-asimetria-firma-trabajador.md) 🔶 ·
> [0009](adr/0009-frontera-del-determinismo.md).

```mermaid
classDiagram
    direction TB

    class Poblacion {
        +origen: "GEIH microdatos DANE"
        +agentes: List~Agente~
        +momentos_observados: Momentos
        +cargar_desde_parquet(ruta)
        +muestrear(n, rng)
    }

    class Agente {
        <<abstract>>
        +id: str
        +ciudad: str
        +sector: str
        +arquetipo_id: str
        +factor_expansion: float
    }

    class Trabajador {
        +ingreso_mensual_cop: int
        +formal: bool
        +educacion: str
        +tamano_empresa: int
        %% ADR 0008: el trabajador NO usa LLM. Regla determinista.
        +acepta_informal(neto_f, neto_i, prima): bool
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
        %% ADR 0006: la capacidad de fiscalizacion NO vive aca.
        %% Al LLM jamas se le pasa el nombre, solo la mecanica.
        +como_mecanica(): str
    }

    class EstadoFiscalizacion {
        <<estado del mundo, NO palanca del usuario>>
        +inspectores_efectivos: int
        +inspecciones_por_inspector_trimestre: float
        +fraccion_universo: float
        +capacidad_trimestre(): float
    }

    class EstadoMundo {
        +poblacion: Poblacion
        +fiscalizacion: EstadoFiscalizacion
        +politica: Politica
        +trimestre: int
    }

    class Arquetipo {
        <<unidad de llamada al LLM, de cache y de presupuesto>>
        +id: str
        +sector: str
        +tamano: str
        +formal: bool
        +tramo_ingreso: str
        +n_agentes: int
    }

    class Agregado {
        <<lo unico que los arquetipos VEN>>
        +ronda: int
        +tasa_evasion: float
        +prob_sancion_vigente: float
    }

    class MotorFisico {
        <<determinista, con seed>>
        +rng: Generator
        +costo_formal(salario, factor_prestacional)
        +costo_informal(salario, p, sancion)
        +prob_sancion(C, E): float
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
        +arquetipo_id: str
        +ronda: int
        +estrategia: "cumplir|informalizar|despedir|absorber|renegociar"
        +detalle: dict
        +justificacion: str
        +veto: Veto
    }

    class Veto {
        +factible: bool
        +razon: str
        %% max 3 reintentos; al agotarlos la estrategia terminal es "cumplir"
    }

    class MotorEquilibrio {
        <<mejor respuesta con rezago, 4 rondas — NO convergencia>>
        +max_rondas: int = 4
        +max_reintentos: int = 3
        +ronda_0_ingenua(): Ronda
        +iterar(agregado_anterior): Ronda
    }

    class Ronda {
        +simulacion_id: str
        +ronda: int
        +trimestre: int
        +tasa_informalidad: float
        +prob_fiscalizacion: float
        +empleo_relativo: float
        +n_vetos: int
        +n_fallback: int
        +banda: Banda
    }

    class Simulacion {
        +id: str
        +seed: int
        +hash_cache: str
        +politica: Politica
        +rondas: List~Ronda~
        +brecha(): float
        %% brecha = ronda 3 - ronda 0: EL producto
    }

    class Validador {
        +calibracion_base(momentos): Error
        +backtest_historico(alzas): Error
        +test_reskinning(): bool
        +ablacion_llm(): Diff
        +make_validate(): "imprime EL numero"
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
    Poblacion "1" *-- "40-60" Arquetipo
    Arquetipo "1" o-- "muchos" Agente : agrupa

    EstadoMundo --> Poblacion
    EstadoMundo --> EstadoFiscalizacion
    EstadoMundo --> Politica

    Simulacion --> EstadoMundo
    Simulacion "1" *-- "4" Ronda
    MotorEquilibrio --> Ronda : produce
    MotorEquilibrio --> Agregado : publica por ronda
    Agregado ..> CapaConductual : es lo unico que ve
    MotorEquilibrio --> CapaConductual : pide propuestas por arquetipo
    CapaConductual --> DecisionPropuesta : genera
    DecisionPropuesta --> Veto
    MotorFisico --> Veto : emite
    MotorFisico ..> DecisionPropuesta : veta o acepta
    MotorFisico --> EstadoFiscalizacion : lee capacidad
    MotorFisico --> Politica : lee mecanica
    MotorFisico ..> Trabajador : consulta acepta_informal()
    Validador ..> Simulacion : audita
    Validador ..> Poblacion : compara momentos
    Interfaz ..> Ronda : suscrita via Realtime
    Interfaz ..> Simulacion : dispara POST /simulaciones
```

## Lectura del diagrama en seis frases

1. **`Poblacion`** no se genera: se **carga** desde la GEIH. Por eso `Trabajador` tiene los
   atributos de la encuesta y `factor_expansion` para escalar a la ciudad.
2. El bucle central es `MotorEquilibrio → CapaConductual → DecisionPropuesta →
   MotorFisico.vetar()`: **el LLM propone, el motor determinista dispone.** Ninguna decisión
   no factible sobrevive, y tras tres vetos la estrategia terminal es cumplir.
3. **`Politica.como_mecanica()`** es el control de contaminación hecho código: el LLM solo ve
   la mecánica (*"tu costo laboral sube X%"*), nunca el nombre.
4. **`EstadoFiscalizacion` está separada de `Politica` a propósito**
   ([ADR 0006](adr/0006-fiscalizacion-es-estado-del-mundo.md)). La capacidad de inspección es
   un dato del mundo con fuente, no una perilla del usuario. Si fuera perilla, cualquier
   resultado sería alcanzable y la cascada no probaría nada.
5. **`Arquetipo` y `Agregado` son entidades de primera clase.** El arquetipo es la unidad de
   llamada al LLM, de caché y de presupuesto. El agregado es **lo único que los arquetipos
   ven**, y por eso la interacción es indirecta: ahí nace la cascada sin costo cuadrático.
6. **`Simulacion.brecha()`** — la distancia entre la ronda 0 (lo que el gobierno proyecta) y
   la ronda 3 (la cascada, nueve meses después) — **es el producto entero**.

## Lo que el diagrama declara que NO hay

- **No hay `Aprendizaje`.** Los agentes no acumulan memoria entre rondas más allá del agregado.
- **No hay `Prediccion`.** Nadie anticipa rondas futuras. Es mejor respuesta miope, y es
  exactamente por qué esto no se llama equilibrio.
- **No hay red ni geografía.** La interacción es indirecta vía `Agregado`. El caso no es espacial.
