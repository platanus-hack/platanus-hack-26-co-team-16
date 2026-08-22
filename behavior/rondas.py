"""El bucle de mejor respuesta: 4 rondas, no una prueba de convergencia.

Qué modela: la dinámica de mejor respuesta entre arquetipos. Cada ronda, cada
  arquetipo ve el agregado de la ronda anterior y decide de nuevo.
Entradas: los arquetipos, la política (aumento_pct), y el motor de Manuel.
Salidas: una lista de `ronda.json` (`docs/PLAN.md` §4) + el desglose por arquetipo.
Supuestos: el agregado que ve un arquetipo es el de la ronda anterior completa
  (mejor respuesta simultánea, no secuencial). Declarado en `VALIDATION.md`.

Honestidad de vocabulario (decisión D5 del plan)
------------------------------------------------
Esto es **dinámica de mejor respuesta a 3-4 rondas**. NO es una prueba de
existencia ni de convergencia a un equilibrio de Nash. Puede no converger, y si
no converge lo reportamos: `converge()` mira si la última ronda movió la tasa de
informalidad menos que un umbral, y esa respuesta va al pitch tal como salga.

La cascada sale de acá: la capacidad de fiscalización es fija, así que cuando
más arquetipos se salen de regla, la probabilidad de sanción de cada uno baja, y
eso vuelve a entrar como insumo de la siguiente ronda.
"""

from __future__ import annotations

from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Any, Callable

from behavior import contrato
from behavior.ablacion import ClienteReglas
from behavior.arquetipos import (
    Arquetipo,
    particionar_por_peso,
    reparto_de_parafrasis,
    universo_de_firmas,
)
from behavior.capa import (
    Reskin,
    ResultadoArquetipo,
    Veto,
    decidir_arquetipo,
    veto_permisivo,
)

# C2 — esta capa deja de tener su propia copia del motor. Antes vivían acá una
# fórmula de sanción duplicada y una capacidad de fiscalización de 0,02 sin
# fuente, que equivalía a 83.993 inspecciones por trimestre contra las 3.900 que
# el motor deriva de la cifra de la OIT. Además la capa contaba PERSONAS fuera
# de regla y el motor cuenta EMPRESAS: dos universos distintos para la misma
# probabilidad. Ahora hay una sola implementación y es la del motor.
from engine.fiscalizacion import EstadoFiscalizacion
from engine.veto import EstadoVivo, veto_del_motor

# Quién queda fuera de regla lo decide `contrato.fraccion_fuera_de_regla()`,
# que trabaja sobre la FAMILIA canónica de la estrategia y sobre el estado del
# que viene el agente. El motor tiene la última palabra sobre el estado del
# mundo; esto es solo el agregado que vuelve a los agentes la ronda siguiente.


@dataclass
class Ronda:
    """Un `contracts/ronda.json` más el desglose por arquetipo (dato A4)."""

    simulacion_id: str
    seed: int
    ronda: int
    politica: dict[str, Any]
    tasa_informalidad: float
    prob_fiscalizacion: float
    empleo_relativo: float
    banda: dict[str, float]
    por_arquetipo: dict[str, ResultadoArquetipo] = field(default_factory=dict)
    # Qué fracción de la población expandida fue decidida por LLM (el resto salió
    # de reglas fijas por el modo top-K). NO va en `a_contrato()`: `ronda.json`
    # está congelado desde H+4 y agregarle un campo exige avisar en el grupo ANTES.
    fraccion_poblacion_llm: float = 1.0
    # Peso poblacional de cada arquetipo (suma de factores de expansión). Sin
    # esto el dato A4 no se puede ponderar, y sin ponderar dice lo contrario.
    pesos: dict[str, float] = field(default_factory=dict)

    # --- Las cifras nuevas del plan de correcciones -------------------------
    # A4: masa salarial que sobrevive (empleo × jornada) y qué parte de la
    # población conserva el puesto con la jornada recortada.
    ingreso_laboral_relativo: float = 1.0
    fraccion_jornada_recortada: float = 0.0
    # C3: traslado a precios DECLARADO por las firmas. No es un pronóstico de
    # inflación: no hay respuesta de demanda en el modelo (ver Bloque D).
    traslado_precios_pct: float = 0.0
    # A2: qué fracción de las decisiones cayó al fallback, y de esas cuántas no
    # tuvieron ninguna opción factible. El plan fija el umbral de alarma en 5%
    # ANTES de correr; si se supera, se publica.
    fraccion_fallback: float = 0.0
    fraccion_sin_salida: float = 0.0
    # A5: cuánto se movió la informalidad respecto de la ronda anterior, y si
    # eso cae bajo el umbral declarado. Los llena `etiquetar_estabilidad()`.
    movimiento_pp: float = 0.0
    estabilizada: bool = False
    # B2: la dispersión de las paráfrasis DENTRO de esta ronda, partiendo todas
    # del mismo estado. Es diagnóstico interno, no la banda que se publica: por
    # construcción es más angosta que la dispersión entre trayectorias completas.
    banda_intra_ronda: dict[str, Any] = field(default_factory=dict)

    def a_contrato(self) -> dict[str, Any]:
        """Solo los campos de `contracts/ronda.json`, para la API y el frontend."""
        return {
            "simulacion_id": self.simulacion_id,
            "seed": self.seed,
            "ronda": self.ronda,
            "politica": self.politica,
            "tasa_informalidad": round(self.tasa_informalidad, 4),
            "prob_fiscalizacion": round(self.prob_fiscalizacion, 4),
            "empleo_relativo": round(self.empleo_relativo, 4),
            "banda": {
                k: (v if isinstance(v, bool) else round(v, 4))
                for k, v in self.banda.items()
            },
            # C3 + A4 + A5 — campos NUEVOS respecto de `contracts/ronda.json`
            # congelado en H+4. Se avisó al grupo junto con `banda.degenerada`,
            # que ya se emitía sin estar declarado (§4.4), y el contrato del repo
            # se actualizó en el mismo movimiento. Un campo que se emite y no se
            # declara es peor que un campo nuevo: nadie lo ve venir.
            "traslado_precios_pct": round(self.traslado_precios_pct, 4),
            "ingreso_laboral_relativo": round(self.ingreso_laboral_relativo, 4),
            "movimiento_pp": round(self.movimiento_pp, 4),
            "estabilizada": self.estabilizada,
        }

    def desglose_estrategias(self) -> dict[str, float]:
        """Dato A4: qué estrategia domina, **ponderado por factor de expansión**.

        Devuelve fracciones de la población, no conteos de arquetipos. Es la
        misma regla que `MODELO.md` le impone a `tasa_informalidad` —*"siempre
        ponderada; sin el factor no es la informalidad de la GEIH, es la de la
        muestra"*— y aplica igual acá: sin ponderar, este desglose dice lo
        CONTRARIO de lo que dice ponderado. Medido en la corrida del 23%:
        por conteo domina `cumplir` (44 de 101 arquetipos), ponderado domina
        `informalizar` (51,0% de la población) y `cumplir` cae a 18,1%.

        Un arquetipo de microempresa informal representa a muchísima más gente
        que uno de empresa mediana formal, y contar arquetipos los iguala.
        """
        total: Counter[str] = Counter()
        peso_total = sum(self.pesos.values())
        if not peso_total:
            return {}
        for aid, r in self.por_arquetipo.items():
            peso = self.pesos.get(aid, 0.0)
            votos = sum(r.distribucion.values()) or 1
            for estrategia, n in r.distribucion.items():
                total[estrategia] += peso * n / votos
        return {k: v / peso_total for k, v in total.most_common()}

    def desglose_estrategias_conteo(self) -> dict[str, int]:
        """El conteo crudo de arquetipos. Para el feed y el diagnóstico, NO para
        el dato A4: para eso hay que ponderar (ver `desglose_estrategias`)."""
        total: Counter[str] = Counter()
        for r in self.por_arquetipo.values():
            total.update(r.distribucion)
        return dict(total.most_common())

    @property
    def varianza_media(self) -> float:
        """¿Colapsó la varianza? 0 = todos los arquetipos hicieron una sola cosa."""
        vs = [r.varianza for r in self.por_arquetipo.values()]
        return sum(vs) / len(vs) if vs else 0.0


def correr(
    arquetipos: list[Arquetipo],
    cliente,
    *,
    aumento_pct: float,
    seed: int = 42,
    simulacion_id: str = "sim-local",
    rondas_totales: int = 4,
    veto: Veto | None = None,
    multa_factor: float = 12.0,
    tasa_informalidad_inicial: float,
    n_parafrasis: int = 1,
    parafrasis_por_peso: bool = False,
    paralelismo: int = 8,
    cobertura_llm: float | None = None,
    al_terminar_ronda: Callable[[Ronda], None] | None = None,
    fiscalizacion: EstadoFiscalizacion | None = None,
    congelar_prob_fiscalizacion: bool = False,
    reskin: Reskin | None = None,
) -> list[Ronda]:
    """Corre las rondas de mejor respuesta y devuelve el agregado de cada una.

    La fiscalización sale de `engine.fiscalizacion.EstadoFiscalizacion`, que
    deriva su capacidad de la cifra de inspectores de la OIT. Es FIJA: no se
    ajusta a mano entre rondas, y ese es el compromiso metodológico que hace de
    la cascada un resultado y no un supuesto. Esta capa tenía su propia copia de
    la fórmula y una capacidad de 0,02 sin fuente —83.993 inspecciones por
    trimestre contra las 3.900 del motor—; se borró (C2).

    `veto=None` es el caso normal: `correr()` construye el `EstadoVivo` del motor
    y el veto que lo lleva adentro, y lo cierra al final de cada ronda. Pasar un
    veto por fuera queda para los dobles de prueba, y en ese caso el estado que
    ese veto vea es responsabilidad de quien lo pasó.

    `parafrasis_por_peso=True` reparte las preguntas según cuánta gente
    representa cada arquetipo (B1) en vez de darle la misma cantidad a todos.

    `congelar_prob_fiscalizacion=True` corre el experimento de cascada apagada
    (B4): la sanción se queda en su valor de la ronda 0 y la diferencia contra
    la corrida normal es, en pp, cuánto de la brecha pone la cascada.

    El calendario es el de la [ADR 0005](../docs/adr/0005-el-reloj-de-la-simulacion.md):
    una ronda es un trimestre, la **ronda 0 es la reacción ingenua** —la
    proyección oficial, que asume cumplimiento total y no gasta LLM— y las
    rondas 1..`rondas_totales`-1 son mejor respuesta. Con el valor por defecto
    son 3 rondas de LLM, no 4.

    `cobertura_llm` activa el modo top-K: si se le da (p. ej. `0.80`), solo los
    arquetipos que suman esa fracción de la población van al LLM y el resto se
    resuelve con las reglas fijas de `ablacion.ClienteReglas`. `None` = todos al
    LLM. Cada `Ronda` reporta `fraccion_poblacion_llm`.

    `tasa_informalidad_inicial` es obligatoria a propósito: es el punto de
    partida de la ronda 0 y sale de `data/momentos.json` (30,57% observado en la
    GEIH). Tenía un default de andamio de 0,42 que el propio repo contradice, y
    no era inocuo — `p(E)` sube de 4,65% a 6,33% al corregirlo, que es suficiente
    para voltear la decisión de la ablación con reglas fijas.

    El ESTADO de cada arquetipo persiste entre rondas: qué fracción de su planta
    quedó fuera de regla y cuánto de su empleo original sobrevive. Sin eso, la
    ronda n+1 contradice a la ronda n y las dos métricas del pitch mienten en
    direcciones opuestas.
    """
    peso_total = sum(a.peso for a in arquetipos) or 1.0
    tasa = tasa_informalidad_inicial
    historial: dict[str, list[str]] = {a.id: [] for a in arquetipos}
    salida: list[Ronda] = []

    # EL ESTADO VIVO entre rondas — AHORA ES EL DEL MOTOR (C2 + costura §3.1).
    #
    # Antes esta capa llevaba dos diccionarios propios y el veto del motor
    # capturaba un `EstadoVivo` que nadie actualizaba: el veto veía el estado
    # inicial para siempre y en la ronda 2 podía autorizar despedir a quien ya
    # había sido despedido. Los 44 tests no lo detectaban porque probaban el
    # veto aislado —actualizando el estado a mano— y nunca la composición.
    #
    # Ahora hay UN solo estado y lo lleva `engine/`. Esta capa lo lee al empezar
    # cada ronda y lo cierra al terminarla con `registrar()`; el veto que juzga
    # es un cierre sobre ESE mismo objeto, así que no pueden divergir.
    estado = EstadoVivo.inicial(arquetipos)
    if veto is None:
        # El caso normal: el veto sale del motor y lleva adentro el estado vivo
        # y la política. Pasar un veto por fuera queda para los dobles de prueba.
        veto = veto_del_motor(estado, aumento_pct)

    # A4 — la jornada que sobrevive, acumulativa como el empleo. No la lleva
    # `EstadoVivo` porque el veto no la necesita: él lee el recorte de la
    # decisión en curso, no el acumulado. Es una métrica de esta capa.
    horas: dict[str, float] = {a.id: 1.0 for a in arquetipos}

    # B1 — cuántas veces se le pregunta a cada quien. Con el reparto por peso,
    # el presupuesto se gasta donde de verdad mueve el agregado en vez de
    # repartirse parejo entre celdas que pesan 15% y celdas que pesan 0,02%.
    reparto = (
        reparto_de_parafrasis(arquetipos)
        if parafrasis_por_peso
        else {a.id: n_parafrasis for a in arquetipos}
    )

    # Ruteo del top-K. `ClienteReglas` es un reemplazo directo de la firma de
    # `proponer()`, así que el resto del bucle no distingue entre los dos.
    if cobertura_llm is None:
        cabeza_ids = {a.id for a in arquetipos}
        cliente_cola = None
    else:
        cabeza, _cola = particionar_por_peso(arquetipos, cobertura_llm)
        cabeza_ids = {a.id for a in cabeza}
        cliente_cola = ClienteReglas()
    fraccion_llm = (
        sum(a.peso for a in arquetipos if a.id in cabeza_ids) / peso_total
    )

    # C2 — la fiscalización sale del motor, con el universo de FIRMAS que trae
    # `data/empresas.parquet`. Si la grilla no lo trae (arquetipos de andamio),
    # `EstadoFiscalizacion` se queda con su universo por defecto y lo declara.
    if fiscalizacion is None:
        fiscalizacion = EstadoFiscalizacion(
            universo=max(1.0, universo_de_firmas(arquetipos))
        )

    def _fraccion_firmas_fuera_de_regla() -> float:
        """Qué fracción del universo de FIRMAS está fuera de regla.

        La sanción se le aplica a unidades productivas, no a trabajadores: es la
        divergencia del defecto §3.5, donde esta capa contaba personas y el motor
        contaba empresas para la misma probabilidad. Con la grilla real se
        pondera por `n_empresas`; sin ella se cae al peso poblacional, que es lo
        único disponible en el andamio.
        """
        pesos_firma = sum(a.n_empresas for a in arquetipos)
        if pesos_firma <= 0:
            return min(1.0, sum(a.peso * estado.fraccion_informal[a.id] for a in arquetipos) / peso_total)
        return min(
            1.0,
            sum(a.n_empresas * estado.fraccion_informal[a.id] for a in arquetipos) / pesos_firma,
        )

    # La p(sanción) de la ronda 0, que es también la que se congela cuando se
    # corre el experimento de cascada apagada (B4).
    prob_inicial = fiscalizacion.prob(_fraccion_firmas_fuera_de_regla())

    # RONDA 0 — la proyección oficial (ADR 0005). No se llama al LLM: por
    # definición asume cumplimiento total, así que la informalidad se queda en la
    # observada y nadie pierde el empleo. Es el punto contra el que se mide
    # `brecha = ronda 3 − ronda 0`, que es el producto entero (dato A1).
    r0 = Ronda(
        simulacion_id=simulacion_id,
        seed=seed,
        ronda=0,
        politica={"tipo": "cambio_costo_laboral", "aumento_pct": aumento_pct},
        tasa_informalidad=tasa,
        prob_fiscalizacion=prob_inicial,
        empleo_relativo=1.0,
        # La proyección oficial es un punto, no una distribución: no tiene banda
        # porque no hay nada estocástico que la genere. Se marca degenerada en
        # vez de inventarle un intervalo.
        banda={"p10": tasa, "p90": tasa, "degenerada": True},
        por_arquetipo={},
        fraccion_poblacion_llm=0.0,
    )
    salida.append(r0)
    if al_terminar_ronda:
        al_terminar_ronda(r0)

    for n in range(1, rondas_totales):
        # B4 — con `congelar_prob_fiscalizacion` la sanción se queda en su valor
        # de la ronda 0 en vez de responder a la evasión acumulada. Es el
        # experimento que CUANTIFICA la cascada: la diferencia entre esta corrida
        # y la normal es, en puntos porcentuales, cuánto de la brecha pone el
        # hecho de que la capacidad de fiscalización no crece.
        prob = (
            prob_inicial
            if congelar_prob_fiscalizacion
            else fiscalizacion.prob(_fraccion_firmas_fuera_de_regla())
        )

        # Las RONDAS son secuenciales por definición (cada una responde al
        # agregado de la anterior), pero los ARQUETIPOS dentro de una ronda son
        # independientes: se resuelven en paralelo. Con 48 arquetipos eso baja
        # una corrida en frío de ~10 min a ~1,5 min sin cambiar el resultado —
        # el orden de recorrido no entra en ninguna semilla (ver
        # `arquetipos._semilla`), así que sigue siendo determinista.
        def _uno(a: Arquetipo) -> tuple[str, ResultadoArquetipo]:
            # Top-K: la cabeza al LLM, la cola a reglas fijas. Misma firma.
            cli = cliente if (cliente_cola is None or a.id in cabeza_ids) else cliente_cola
            previo = historial[a.id]
            texto_historial = (
                "\n- Lo que hiciste en periodos anteriores: " + ", ".join(previo)
                if previo
                else ""
            )
            return a.id, decidir_arquetipo(
                a,
                cli,
                veto,
                aumento_pct=aumento_pct,
                ronda=n,
                # El agente decide en los periodos 1..rondas_totales-1: la ronda
                # 0 es la proyección oficial y él no participa en ella. Se le
                # dice "periodo 1 de 3", no "de 4".
                rondas_totales=rondas_totales - 1,
                tasa_informalidad=tasa,
                prob_fiscalizacion=prob,
                # SUPUESTO: la sanción equivale a `multa_factor` meses de
                # ingreso por trabajador (por defecto 12). Es el parámetro que
                # decide si evadir paga, así que es de los primeros que R5 debe
                # someter a análisis de sensibilidad. El valor que manda es el
                # del motor de Manuel; acá entra como dato.
                multa=a.ingreso_por_trabajador * multa_factor,
                historial=texto_historial,
                n_parafrasis=reparto[a.id],
                # El estado que dejó la ronda anterior, leído del motor.
                fraccion_informal_previa=estado.fraccion_informal_previa(a.id),
                # C6 — el candado 3(b): mismos incentivos, otras etiquetas y
                # otra escala de montos. El agregado no debería moverse.
                reskin=reskin,
            )

        if paralelismo > 1:
            with ThreadPoolExecutor(max_workers=paralelismo) as pool:
                pares = list(pool.map(_uno, arquetipos))
        else:
            pares = [_uno(a) for a in arquetipos]

        # Se reconstruye en el orden de `arquetipos`, no en el de terminación:
        # el paralelismo no puede filtrarse al resultado.
        resultados: dict[str, ResultadoArquetipo] = dict(pares)
        for a in arquetipos:
            historial[a.id].append(resultados[a.id].estrategia_dominante)

        # El estado con el que los arquetipos ENTRARON a esta ronda. Se guarda
        # antes de pisarlo porque la banda lo necesita: cada paráfrasis parte del
        # mismo punto de partida.
        frac_previa = {a.id: estado.fraccion_informal_previa(a.id) for a in arquetipos}

        # Nuevo agregado: para cada arquetipo, qué fracción de SU planta queda
        # fuera de regla ACUMULANDO sobre lo que ya estaba; después se pondera
        # por cuánta gente representa. Se promedia primero entre paráfrasis,
        # después entre arquetipos. El resultado se CIERRA en el estado del
        # motor, que es la única fuente: el veto de la ronda siguiente lo lee de
        # ahí y por eso no puede autorizar lo que ya ocurrió.
        for a in arquetipos:
            ds = resultados[a.id].decisiones
            nueva_frac = sum(
                contrato.fraccion_fuera_de_regla(d, a.n_trabajadores, frac_previa[a.id])
                for d in ds
            ) / max(1, len(ds))

            # El empleo se ARRASTRA: lo que se despidió en una ronda no vuelve
            # porque la siguiente absorba. Se descuenta sobre la planta original,
            # que es la unidad en la que está medida la línea base.
            despidos_ronda = sum(
                min(1.0, d["detalle"].get("empleados_a_despedir", 0) / max(1, a.n_trabajadores))
                for d in ds
            ) / max(1, len(ds))
            nuevo_empleo = max(0.0, estado.fraccion_empleada_previa(a.id) - despidos_ronda)

            estado.registrar(
                a.id, fraccion_informal=nueva_frac, fraccion_empleada=nuevo_empleo
            )

            # A4 — la jornada, acumulativa y promediada entre paráfrasis.
            horas[a.id] = sum(
                contrato.jornada_resultante(d, horas[a.id]) for d in ds
            ) / max(1, len(ds))

        tasa = min(
            1.0,
            sum(a.peso * estado.fraccion_informal[a.id] for a in arquetipos) / peso_total,
        )
        empleo_relativo = (
            sum(a.peso * estado.fraccion_empleada[a.id] for a in arquetipos) / peso_total
        )
        # A4 — la masa salarial que sobrevive: empleo × jornada. Un trabajador
        # que conserva el puesto con media jornada cuenta como medio. Es la
        # CUARTA cifra del plan y es material nuevo para el mapa distributivo:
        # el modelo oficial no ve esta pérdida porque no ve la jornada.
        ingreso_laboral_relativo = (
            sum(
                a.peso * estado.fraccion_empleada[a.id] * horas[a.id]
                for a in arquetipos
            )
            / peso_total
        )
        # Qué parte de la población conserva el empleo pero con jornada recortada.
        peso_recortado = sum(
            a.peso * estado.fraccion_empleada[a.id]
            for a in arquetipos
            if horas[a.id] < 0.999
        )
        fraccion_jornada_recortada = peso_recortado / peso_total

        # C3 — el traslado a precios que las firmas DECLARAN. `subir_precios` era
        # el único canal por el que un alza salarial llegaba a los precios: los
        # agentes lo elegían y el agregado lo botaba. No es un pronóstico de
        # inflación —no hay respuesta de demanda— y por eso viaja con su nombre
        # honesto.
        traslado_precios = _traslado_precios(resultados, arquetipos, peso_total)

        # A2 — cuántas decisiones no tuvieron ninguna opción factible.
        total_decisiones = sum(len(r.decisiones) for r in resultados.values()) or 1
        fraccion_sin_salida = (
            sum(r.sin_salida for r in resultados.values()) / total_decisiones
        )
        fraccion_fallback = (
            sum(r.fallbacks for r in resultados.values()) / total_decisiones
        )

        r = Ronda(
            simulacion_id=simulacion_id,
            seed=seed,
            ronda=n,
            politica={"tipo": "cambio_costo_laboral", "aumento_pct": aumento_pct},
            tasa_informalidad=tasa,
            prob_fiscalizacion=prob,
            empleo_relativo=empleo_relativo,
            # SUPUESTO: sin N paráfrasis la banda es degenerada (p10 = p90 = media).
            # Con n_parafrasis>=5 se llena de verdad; hasta entonces se reporta
            # como banda vacía en vez de inventar una.
            banda=_banda(resultados, tasa, arquetipos, peso_total, frac_previa),
            por_arquetipo=resultados,
            fraccion_poblacion_llm=fraccion_llm,
            pesos={a.id: a.peso for a in arquetipos},
            ingreso_laboral_relativo=ingreso_laboral_relativo,
            fraccion_jornada_recortada=fraccion_jornada_recortada,
            traslado_precios_pct=traslado_precios,
            fraccion_fallback=fraccion_fallback,
            fraccion_sin_salida=fraccion_sin_salida,
        )
        # A5 — la etiqueta se pone ANTES de entregar la ronda, para que quien
        # escucha `al_terminar_ronda` (el terminal, la API, el frontend) la vea
        # ya puesta y no tenga que recalcularla por su cuenta.
        etiquetar_estabilidad(salida[-1] if salida else None, r)
        salida.append(r)
        if al_terminar_ronda:
            al_terminar_ronda(r)

    return salida


def _banda(
    resultados, tasa: float, arquetipos, peso_total: float, frac_previa: dict[str, float]
) -> dict[str, float]:
    """p10/p90 de la tasa entre paráfrasis. Degenerada si solo hubo una.

    SUPUESTO: las N paráfrasis parten todas del MISMO estado previo (el promedio
    que dejó la ronda anterior), no de N trayectorias separadas. Seguir un árbol
    de estados por paráfrasis multiplicaría las llamadas por N en cada ronda y es
    otro proyecto; acá la banda mide dispersión de la decisión de ESTA ronda, no
    de la historia completa. Se declara porque estrecha la banda respecto de la
    que daría el árbol.
    """
    n_votos = max(len(r.decisiones) for r in resultados.values())
    if n_votos < 2:
        return {"p10": tasa, "p90": tasa, "degenerada": True}
    tasas = []
    for i in range(n_votos):
        fuera = sum(
            a.peso
            * contrato.fraccion_fuera_de_regla(
                resultados[a.id].decisiones[i], a.n_trabajadores, frac_previa[a.id]
            )
            for a in arquetipos
        )
        tasas.append(min(1.0, fuera / peso_total))
    return _percentiles(tasas, tipo="intra_ronda")


def _percentiles(valores: list[float], *, tipo: str) -> dict[str, Any]:
    """p10/p90 de una lista, con la etiqueta de QUÉ dispersión se está midiendo.

    `tipo` no es decorativo: `intra_ronda` y `entre_trayectorias` miden cosas
    distintas y dan números muy distintos (0,0 pp contra 22,5 pp en la corrida
    medida). Publicar una donde se espera la otra es la forma más rápida de
    perder credibilidad en el Q&A, así que la etiqueta viaja con el número.
    """
    if not valores:
        return {"p10": 0.0, "p90": 0.0, "degenerada": True, "tipo": tipo}
    if len(valores) < 2:
        return {
            "p10": valores[0], "p90": valores[0], "degenerada": True, "tipo": tipo
        }
    vs = sorted(valores)
    k10 = max(0, int(0.10 * (len(vs) - 1)))
    k90 = min(len(vs) - 1, int(round(0.90 * (len(vs) - 1))))
    return {"p10": vs[k10], "p90": vs[k90], "degenerada": False, "tipo": tipo}


# --- B2: la banda que se PUBLICA es la de trayectorias completas -------------


def banda_entre_trayectorias(corridas: list[list[Ronda]], ronda: int = -1) -> dict[str, Any]:
    """p10/p90 de la tasa final entre N corridas completas e independientes.

    Esta es la banda honesta y es la que va a la pantalla. La otra —la que
    calcula `_banda()`— mide la dispersión de las paráfrasis DENTRO de una ronda
    partiendo todas del mismo estado, y por construcción es más angosta: en la
    corrida medida daba 0,0 pp mientras la dispersión real entre trayectorias
    independientes era de 22,5 pp.

    Publicar la angosta no era una decisión, era un accidente del código; pero
    el efecto habría sido presentar una precisión que el modelo no tiene. La
    banda se ENSANCHA con esta corrección, y ese ensanchamiento es el arreglo.
    """
    finales = [c[ronda].tasa_informalidad for c in corridas if c]
    return _percentiles(finales, tipo="entre_trayectorias")


def consolidar_trayectorias(corridas: list[list[Ronda]]) -> list[Ronda]:
    """Toma N corridas y devuelve la MEDIANA con la banda real puesta.

    La corrida que se publica es la de la mediana de la tasa final —no la media,
    que no corresponde a ninguna trayectoria que haya ocurrido— y su banda es la
    dispersión entre las N. La banda intra-ronda de cada una se conserva en
    `banda_intra_ronda` para el diagnóstico.
    """
    if not corridas:
        return []
    validas = [c for c in corridas if c]
    if len(validas) == 1:
        return validas[0]
    orden = sorted(validas, key=lambda c: c[-1].tasa_informalidad)
    mediana = orden[len(orden) // 2]
    for n, r in enumerate(mediana):
        r.banda_intra_ronda = dict(r.banda)
        r.banda = banda_entre_trayectorias(validas, ronda=min(n, len(validas[0]) - 1))
    return mediana


def _traslado_precios(
    resultados: dict[str, ResultadoArquetipo], arquetipos, peso_total: float
) -> float:
    """Promedio ponderado del alza de precios que las firmas DECLARARON (C3).

    Solo cuentan las decisiones de familia `subir_precios`; el resto aporta 0.
    Es un promedio sobre TODA la población, no sobre quienes suben precios: la
    cifra responde "¿cuánto sube el nivel de precios que fijan estas firmas?",
    no "¿cuánto suben los que suben?".

    Su nombre honesto es *traslado declarado por las firmas*. NO es inflación:
    no hay respuesta de demanda, no hay elasticidad, y una firma que declara que
    subirá 10% puede no poder hacerlo. Se publica con esa etiqueta pegada
    (Bloque D) porque la alternativa —no publicar nada— deja sin respuesta la
    pregunta obvia del Q&A.
    """
    por_id = {a.id: a for a in arquetipos}
    total = 0.0
    for aid, r in resultados.items():
        a = por_id.get(aid)
        if a is None or not r.decisiones:
            continue
        suma = 0.0
        for d in r.decisiones:
            if d.get("familia") != "subir_precios":
                continue
            pct = d.get("detalle", {}).get("aumento_precios_pct")
            try:
                suma += max(0.0, float(pct))
            except (TypeError, ValueError):
                continue
        total += a.peso * suma / len(r.decisiones)
    return total / peso_total if peso_total else 0.0


# A5 — LA REGLA DE CORTE, DECLARADA ANTES DE CORRER.
#
# Se reporta la ronda 3. Si el movimiento de la última ronda supera este umbral,
# la corrida sale marcada "no estabilizada" y el número viaja con esa etiqueta
# pegada hasta la pantalla. El umbral se fija acá, en el código, y no en el
# análisis posterior: elegir dónde cortar después de ver el resultado es
# exactamente lo que esta constante existe para impedir.
UMBRAL_ESTABILIDAD_PP = 2.0


def etiquetar_estabilidad(anterior: Ronda | None, actual: Ronda) -> Ronda:
    """Llena `movimiento_pp` y `estabilizada` de una ronda contra la previa."""
    if anterior is None:
        actual.movimiento_pp = 0.0
        actual.estabilizada = True
        return actual
    actual.movimiento_pp = (
        actual.tasa_informalidad - anterior.tasa_informalidad
    ) * 100.0
    actual.estabilizada = abs(actual.movimiento_pp) <= UMBRAL_ESTABILIDAD_PP
    return actual


def converge(rondas: list[Ronda], umbral: float = 0.01) -> bool:
    """¿La última ronda movió la informalidad menos que `umbral`?

    NO es una prueba de equilibrio. Es una observación sobre esta corrida, y se
    reporta como tal: "en esta corrida el movimiento de la última ronda fue de
    X pp". Si alguien la cita como convergencia a Nash, está mintiendo.
    """
    if len(rondas) < 2:
        return False
    return abs(rondas[-1].tasa_informalidad - rondas[-2].tasa_informalidad) < umbral
