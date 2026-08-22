# ADR 0008 — Asimetría deliberada: la firma propone, el trabajador calcula

**Estado:** 🔶 **propuesta de R2, pendiente de aval de Alejo (R1) y Nico (R3)** · **Fecha:** 2026-08-22 · **Fuente:** hueco H4

> Toca `contracts/` (dueño Alejo) y la interfaz del veto (compartida con Nico). **No se
> implementa hasta que los dos den el visto bueno en el standup.**

## Contexto

Hay una inconsistencia entre los contratos y el modelo:

- `contracts/agente.json` describe **un trabajador** (`tipo: "trabajador"`, ingreso, formalidad, educación).
- `contracts/decision.json` usa **un id de empresa** (`"empresa-com-04-0083"`).
- `docs/UML.md` tiene `Empresa` como subclase de `Agente`, pero una empresa construida
  agrupando trabajadores no tiene `factor_expansion` propio, y no existe contrato para ella.

Y hay un problema de fondo más grave. El insumo de Juan David (§5) identifica el modo de
falla más probable del proyecto: *"si todos los agentes maximizan ganancia, la conclusión ya
está escrita en el supuesto"*. Su antídoto es modelar **el margen formal/informal**, y ese
margen es una decisión de **dos lados**: la firma ofrece informalidad, y el trabajador la
acepta o no. Un empleo formal al mínimo deja **menos plata en el bolsillo hoy** (descuentos
de ley) pero protege; uno informal paga más neto y no protege nada.

Hoy el modelo solo tiene un lado. Con un solo lado, "informalizar" es una decisión unilateral
de la firma, que es justamente la caricatura que el proyecto dice evitar.

## Decisión

**Los dos lados existen, pero con mecanismos deliberadamente distintos:**

| Lado | Mecanismo | Por qué |
|---|---|---|
| **Firma** | **Propone vía la capa LLM**, espacio de estrategias abierto (cumplir, informalizar parcial, despedir, absorber, renegociar), filtrado por el veto de flujo de caja | Es donde vive el aporte: descubrir adaptaciones que un economista no habría enumerado (dato A4 del plan) |
| **Trabajador** | **Regla determinista en el motor.** Acepta la oferta informal si su neto informal supera su neto formal por encima de la prima que le asigna a la protección | El trabajador **no necesita creatividad, necesita aritmética**. Su decisión es una comparación entre dos números observables en la propia GEIH |

**La frase:** *un lado creativo, un lado aritmético.*

La prima de protección (cuánto vale para el trabajador la pensión, la salud y las
cesantías, expresada como fracción del salario) va con `# SUPUESTO:` y sensibilidad. Los
descuentos de ley del lado formal sí son cifra legal y van con fuente.

## Alternativas descartadas

| Alternativa | Por qué no |
|---|---|
| **Solo decide la firma** (el statu quo) | Convierte informalizar en una decisión unilateral. Cae en el modo de falla que el insumo de Juan David identificó como el más probable del proyecto. |
| **Los dos lados con LLM** | Duplica el costo de inferencia sobre un presupuesto de USD 50, y duplica el ruido. Y compra poco: el colapso de varianza documentado ([`1-teorica.md`](../investigacion/1-teorica.md) §5) dice que el LLM aporta **espacio de estrategias**, no heterogeneidad — y el espacio de estrategias del trabajador ante una oferta concreta tiene dos elementos. |
| **Los dos lados deterministas** | Es la ablación (candado 4 de validación), no el diseño. Sin LLM se pierde el dato A4. |
| **Negociación explícita de ida y vuelta** | Es un juego de negociación completo. Fuera de alcance en 36 horas y no responde ninguno de los datos A1-A4. |

## Consecuencias

- **`contracts/` necesita un cuarto ejemplo o una extensión:** la unidad que decide (firma) y
  la unidad que responde (trabajador) son distintas. **Es la conversación con Alejo.**
- El veto sigue siendo la interfaz con Nico y no cambia de forma: Nico manda
  `estrategia_propuesta` + `detalle`, el motor responde `{factible, razon}`. Lo que se agrega
  es que una estrategia factible para la firma **puede aun así no realizarse** si el
  trabajador la rechaza. Eso es un resultado del motor, no un veto. **Es la conversación con Nico.**
- Aparece una métrica nueva y valiosa para el pitch: **cuánta informalización propuesta no
  ocurre porque el trabajador no acepta.** Es distribución, no promedio, y alimenta el mapa (dato A3).
- Si el equipo rechaza la propuesta, el plan B es el statu quo (solo firma) y se declara en
  `VALIDATION.md` como límite: *"el modelo trata la aceptación del trabajador como automática"*.
