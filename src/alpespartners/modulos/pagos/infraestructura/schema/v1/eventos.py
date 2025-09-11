from pulsar.schema import *

class EventoPagoExitoso(Record):
    payout_id = String()
    partner_id = String()
    cycle_id = String()
    total_amount = Float()
    currency = String()
    completed_at = Long()
    confirmation_id = String()
    correlation_id = String()

class EventoPagoFallido(Record):
    payout_id = String()
    partner_id = String()
    cycle_id = String()
    total_amount = Float()
    currency = String()
    failed_at = Long()
    reason = String()
    correlation_id = String()