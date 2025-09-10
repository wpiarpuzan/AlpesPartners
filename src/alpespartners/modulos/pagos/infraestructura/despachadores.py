import pulsar
from pulsar.schema import *
import datetime
import logging

from alpespartners.modulos.pagos.infraestructura.schema.v1.eventos import EventoPagoExitoso, PagoExitosoPayload, EventoPagoFallido, PagoFallidoPayload
from alpespartners.modulos.pagos.infraestructura.schema.v1.comandos import ComandoProcesarPago, ComandoProcesarPagoPayload
from alpespartners.seedwork.infraestructura import utils
epoch = datetime.datetime.utcfromtimestamp(0)

def unix_time_millis(dt):
    return (dt - epoch).total_seconds() * 1000.0

class Despachador:
    def _publicar_mensaje(self, mensaje, topico, schema):
        try:
            cliente = pulsar.Client(f'pulsar://{utils.broker_host()}:6650')
            publicador = cliente.create_producer(topico, schema=schema)
            publicador.send(mensaje)
            logging.info(f"======== Mensaje publicado en el tópico {topico} ========")
            cliente.close()
        except Exception as e:
            logging.error(f"[Pagos] ERROR: Publicando en Pulsar: {e}")

    def publicar_evento(self, evento_dominio, topico):
        if isinstance(evento_dominio, EventoPagoExitoso):
            payload = PagoExitosoPayload(
                payout_id=str(evento_dominio.payout_id),
                partner_id=str(evento_dominio.partner_id),
                cycle_id=str(evento_dominio.cycle_id),
                total_amount=float(evento_dominio.total_amount),
                currency=str(evento_dominio.currency),
                completed_at=int(unix_time_millis(evento_dominio.completed_at)),
                confirmation_id=str(evento_dominio.confirmation_id),
                correlation_id=str(evento_dominio.correlation_id)
            )
            evento_integracion = EventoPagoExitoso(data=payload)
            self._publicar_mensaje(evento_integracion, topico, AvroSchema(EventoPagoExitoso))
        
        elif isinstance(evento_dominio, EventoPagoFallido):
            payload = PagoFallidoPayload(
                payout_id=str(evento_dominio.payout_id),
                partner_id=str(evento_dominio.partner_id),
                cycle_id=str(evento_dominio.cycle_id),
                total_amount=float(evento_dominio.total_amount),
                currency=str(evento_dominio.currency),
                failed_at=int(unix_time_millis(evento_dominio.failed_at)),
                reason=str(evento_dominio.reason),
                correlation_id=str(evento_dominio.correlation_id)
            )
            evento_integracion = EventoPagoFallido(data=payload)
            self._publicar_mensaje(evento_integracion, topico, AvroSchema(EventoPagoFallido))
        
        else:
            logging.warning(f"[Pagos] Evento de dominio de tipo {type(evento_dominio).__name__} no tiene un mapeo de integración.")


    def publicar_comando(self, comando_app, topico):
        if isinstance(comando_app, ComandoProcesarPago):
             payload = ComandoProcesarPagoPayload(
                 partner_id=str(comando_app.partner_id),
                 cycle_id=str(comando_app.cycle_id),
                 correlation_id=str(comando_app.correlation_id)
             )
             comando_integracion = ComandoProcesarPago(data=payload)
             self._publicar_mensaje(comando_integracion, topico, AvroSchema(ComandoProcesarPago))
        else:
            logging.warning(f"[Pagos] Comando de tipo {type(comando_app).__name__} no tiene un mapeo de integración.")
