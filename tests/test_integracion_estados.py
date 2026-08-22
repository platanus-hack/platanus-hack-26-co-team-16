"""Costura real entre el bucle conductual y los estados del motor."""

from behavior.arquetipos import Arquetipo
from behavior.rondas import correr
from engine.fiscalizacion import EstadoFiscalizacion
from engine.veto import EstadoVivo, veto_del_motor


class ClienteDosRondas:
    """Primero saca toda la planta; después intenta sacar a uno otra vez."""

    def proponer(self, sistema, usuario, modelo=None, max_tokens=None, contexto=None):
        ronda = contexto["ronda"]
        if ronda == 1:
            return {
                "estrategia_propuesta": "informalizar_total",
                "detalle": {"empleados_a_informalizar": 4},
                "justificacion": "prueba de integración",
            }
        return {
            "estrategia_propuesta": "informalizar_parcial",
            "detalle": {"empleados_a_informalizar": 1},
            "justificacion": "prueba de integración",
        }


def test_dos_rondas_actualizan_estado_vivo_y_usan_fiscalizacion_real():
    firma = Arquetipo(
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
    estado_vivo = EstadoVivo.inicial([firma])
    fiscalizacion = EstadoFiscalizacion(universo=4)

    rondas = correr(
        [firma],
        ClienteDosRondas(),
        aumento_pct=23.0,
        tasa_informalidad_inicial=0.0,
        rondas_totales=3,
        paralelismo=1,
        capacidad_fiscalizacion=fiscalizacion.capacidad() / fiscalizacion.universo,
        veto=veto_del_motor(estado_vivo),
    )

    assert len(rondas) == 3
    assert estado_vivo.fraccion_informal_previa(firma.id) == 1.0
    assert rondas[2].por_arquetipo[firma.id].vetadas
