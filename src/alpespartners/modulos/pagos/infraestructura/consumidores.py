import pulsar, _pulsar
from pulsar.schema import *
import logging
import traceback

from alpespartners.modulos.pagos.infraestructura.schema.v1.comandos import ComandoProcesarPago
from alpespartners.modulos.pagos.infraestructura.schema.v1.eventos import EventoPagoExitoso, EventoPagoFallido

from alpespartners.seedwork.infraestructura import utils

def suscribirse_a_comandos(app=None):
    """
    Suscribe el servicio al tópico de comandos de pagos en Pulsar.
    """
    cliente = None
    try:
        cliente = pulsar.Client(f'pulsar://{utils.broker_host()}:6650')
        consumidor = cliente.subscribe(
            'comandos-pagos', 
            consumer_type=_pulsar.ConsumerType.Shared,
            subscription_name='alpespartners-sub-comandos-pagos', 
            schema=AvroSchema(ComandoProcesarPago)
        )

        logging.info("========= Suscripción a comandos de pagos iniciada =========")

        while True:
            mensaje = consumidor.receive()
            data = mensaje.value().data
            correlation_id = mensaje.value().correlation_id
            
            logging.info(f"Comando de pago recibido: {data} con correlation_id: {correlation_id}")
            
            # TODO: Aquí va la lógica para despachar el comando a un manejador en la capa de aplicación.
            # Este es el punto de entrada para ejecutar tu caso de uso.
            # Ejemplo:
            # with app.app_context():
            #     comando_dominio = ProcesarPago(correlation_id=correlation_id, partner_id=data.partner_id, ...)
            #     manejador_comandos.handle(comando_dominio)

            consumidor.acknowledge(mensaje)     

        cliente.close()
    except Exception:
        logging.error('ERROR: Suscribiéndose al tópico de comandos de pagos!')
        traceback.print_exc()
        if cliente:
            cliente.close()

def suscribirse_a_eventos(app=None):
    """
    Suscribe el servicio al tópico de eventos de pagos en Pulsar.
    Esto permite que el propio servicio u otros interesados reaccionen a los
    resultados del procesamiento de pagos.
    """
    cliente = None
    try:
        # Se suscribe a múltiples eventos usando una lista de esquemas
        # En un escenario real, podrías tener tópicos separados para éxito y fallo.
        cliente = pulsar.Client(f'pulsar://{utils.broker_host()}:6650')
        consumidor = cliente.subscribe(
            'eventos-pagos', 
            consumer_type=_pulsar.ConsumerType.Shared,
            subscription_name='alpespartners-sub-eventos-pagos',
            schema=AvroSchema(EventoPagoExitoso) # Pulsar puede manejar múltiples esquemas si el tópico está bien configurado
        )

        logging.info("========= Suscripción a eventos de pagos iniciada =========")

        while True:
            mensaje = consumidor.receive()
            valor = mensaje.value()
            
            # Determina el tipo de evento recibido y procesa
            if isinstance(valor, EventoPagoExitoso):
                logging.info(f"Evento de PAGO EXITOSO recibido: {valor.data}")
                # TODO: Lógica para reaccionar a un pago exitoso (ej. actualizar un dashboard)
            
            elif isinstance(valor, EventoPagoFallido):
                logging.info(f"Evento de PAGO FALLIDO recibido: {valor.data}")
                # TODO: Lógica para reaccionar a un pago fallido (ej. enviar alerta a operaciones)
            
            else:
                logging.warning(f"Evento de tipo desconocido recibido: {type(valor)}")

            consumidor.acknowledge(mensaje)     

        cliente.close()
    except Exception:
        logging.error('ERROR: Suscribiéndose al tópico de eventos de pagos!')
        traceback.print_exc()
        if cliente:
            cliente.close()

