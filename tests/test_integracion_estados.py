"""La costura entre el bucle conductual y el estado vivo del motor.

Por qué existe: `docs/agents/estado-consolidado-2026-08-22.md` §89 pedía
"un test de integración que corra dos rondas con `EstadoVivo`,
`EstadoFiscalizacion` y `veto_del_motor` reales". No existía, y por eso la
costura #1 era invisible: los tests probaban el veto AISLADO —actualizando el
estado a mano— y nunca la composición. El bucle podía autorizar en la ronda 2
informalizar a quien ya estaba fuera de regla en la ronda 1.

Qué prueba, y por qué así: se corre la RUTA POR DEFECTO (`veto=None`), que es
la que usa el producto. `correr()` construye su propio `EstadoVivo` y el veto
que lo lleva adentro, así que no se le puede pasar uno por fuera y esperar que
lo actualice — el docstring de `behavior/rondas.py` dice literalmente que en
ese caso "el estado que ese veto vea es responsabilidad de quien lo pasó".
Un test que inyecte su propio estado estaría probando un contrato que el motor
no ofrece, y quedaría rojo por diseño del test y no por un defecto real.

La evidencia observable de que la costura está cosida es el VETO: si el estado
viaja entre rondas, el segundo intento de sacar gente de regla se rechaza
porque ya no queda a quién sacar.
"""

from behavior.arquetipos import Arquetipo
from behavior.rondas import correr
from engine.fiscalizacion import EstadoFiscalizacion


class ClienteDosRondas:
    """Primero saca toda la planta; después intenta sacar a uno más."""

    def proponer(self, sistema, usuario, modelo=None, max_tokens=None, contexto=None):
        if contexto["ronda"] == 1:
            return {
                "estrategia_propuesta": "informalizar_total",
                "detalle": {"empleados_a_informalizar": 4},
                "justificacion": "prueba de integracion",
            }
        return {
            "estrategia_propuesta": "informalizar_parcial",
            "detalle": {"empleados_a_informalizar": 1},
            "justificacion": "prueba de integracion",
        }


def _firma() -> Arquetipo:
    return Arquetipo(
        id="integracion-micro-formal",
        sector="comercio",
        tamano="micro",
        formal=True,
        tramo_ingreso="t1",
        n_trabajadores=4,
        ingreso_por_trabajador=1_000_000.0,
        flujo_caja=2_000_000.0,
        costo_despido=1_000_000.0,
        peso=4.0,
    )


def _correr(firma: Arquetipo):
    fiscalizacion = EstadoFiscalizacion(universo=4)
    return correr(
        [firma],
        ClienteDosRondas(),
        aumento_pct=23.0,
        tasa_informalidad_inicial=0.0,
        rondas_totales=3,
        paralelismo=1,
        fiscalizacion=fiscalizacion,
    )


def test_el_estado_viaja_entre_rondas_y_el_veto_lo_ve():
    """Sacar de regla dos veces a la misma gente tiene que rechazarse.

    Es la costura #1. Si el `EstadoVivo` no viajara, la ronda 2 vería la planta
    como si siguiera entera en regla y autorizaría informalizar de nuevo.
    """
    firma = _firma()
    rondas = _correr(firma)

    assert len(rondas) == 3

    # Ronda 1: la planta entera sale de regla.
    assert rondas[1].por_arquetipo[firma.id].distribucion, "la ronda 1 no decidió nada"

    # Ronda 2: ya no queda a quién sacar, así que el veto tiene que pitar.
    vetadas = rondas[2].por_arquetipo[firma.id].vetadas
    assert vetadas, (
        "la ronda 2 volvió a informalizar sobre una planta que ya estaba "
        "fuera de regla: el EstadoVivo no viajó entre rondas (costura #1)"
    )


def test_la_informalidad_no_se_desborda_al_repetir_la_jugada():
    """Informalizar dos veces no puede dar más del 100% de la planta."""
    rondas = _correr(_firma())
    for r in rondas:
        assert 0.0 <= r.tasa_informalidad <= 1.0, (
            f"ronda {r.ronda}: tasa fuera de [0,1] = {r.tasa_informalidad}"
        )
