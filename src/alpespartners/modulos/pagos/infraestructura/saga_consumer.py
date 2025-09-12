import pulsar
import json
import logging
from pulsar import ConsumerType

PULSAR_BROKER_URL = 'pulsar://broker:6650'
TOPIC_EVENTOS_PAGOS = 'persistent://public/default/eventos-pagos'

class PagosSagaConsumer:
    def __init__(self):
        self.client = pulsar.Client(PULSAR_BROKER_URL)
        self.consumer = self.client.subscribe(TOPIC_EVENTOS_PAGOS, subscription_name='pagos-saga', consumer_type=ConsumerType.Shared)

    def run(self):
        logging.info('[PAGOS] Saga consumer iniciado')
        while True:
            msg = self.consumer.receive()
            evento = json.loads(msg.data())
            tipo = evento.get('type')
            data = evento.get('data', {})
            if tipo == 'PagoExitoso':
                self.handle_exitoso(data)
            elif tipo == 'PagoFallido':
                self.handle_fallido(data)
            self.consumer.acknowledge(msg)

    def handle_exitoso(self, data):
        logging.info(f"[PAGOS] Pago exitoso: {data}")
        # Aquí puedes actualizar el estado del pago y disparar eventos de éxito

    def handle_fallido(self, data):
        logging.info(f"[PAGOS] Pago fallido: {data}")
        # Aquí puedes actualizar el estado del pago y disparar eventos de compensación

    def close(self):
        self.client.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    consumer = PagosSagaConsumer()
    consumer.run()
    # consumer.close() # Llamar al finalizar
