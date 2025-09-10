from pulsar.schema import *
from alpespartners.seedwork.infraestructura.schema.v1.comandos import (ComandoIntegracion)

class ComandoProcesarPagoPayload(ComandoIntegracion):
    partner_id = String(required=True)
    cycle_id = String(required=True)
    correlation_id = String(required=True)

class ComandoProcesarPago(ComandoIntegracion):
    data = ComandoProcesarPagoPayload()
