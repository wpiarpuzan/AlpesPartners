from pulsar.schema import *
from alpespartners.seedwork.infraestructura.schema.v1.eventos import EventoIntegracion

class PagoExitosoPayload(Record):
    payout_id = String(required=True)
    partner_id = String(required=True)
    cycle_id = String(required=True)
    total_amount = Float(required=True)
    currency = String(required=True)
    completed_at = Long(required=True)
    confirmation_id = String(required=True)
    correlation_id = String(required=True)

class EventoPagoExitoso(EventoIntegracion):
    data = PagoExitosoPayload()

# ======================================================================

class PagoFallidoPayload(Record):
    payout_id = String(required=True)
    partner_id = String(required=True)
    cycle_id = String(required=True)
    total_amount = Float(required=True)
    currency = String(required=True)
    failed_at = Long(required=True)
    reason = String(required=True)
    correlation_id = String(required=True)

class EventoPagoFallido(EventoIntegracion):
    data = PagoFallidoPayload()