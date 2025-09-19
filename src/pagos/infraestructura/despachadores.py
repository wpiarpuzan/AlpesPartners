from pagos.infrastructure.publisher import publish_event
from pagos.infrastructure.schema.v1.eventos import PagoConfirmadoV1

def despachar_pago_exitoso(payload):
    publish_event('PagoConfirmado.v1', payload)
