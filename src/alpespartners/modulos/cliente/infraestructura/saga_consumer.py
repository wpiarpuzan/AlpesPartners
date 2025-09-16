import pulsar
import json
import logging
from pulsar import ConsumerType

import os
TOPIC_EVENTOS_CLIENTES = 'persistent://public/default/eventos-clientes'

class ClienteSagaConsumer:
    def __init__(self):
        pulsar_broker_url = os.environ['PULSAR_BROKER_URL']
        self.client = pulsar.Client(pulsar_broker_url)
        self.consumer = self.client.subscribe(TOPIC_EVENTOS_CLIENTES, subscription_name='clientes-saga', consumer_type=ConsumerType.Shared)

    def run(self):
        logging.info('[CLIENTES] Saga consumer iniciado')
        while True:
            msg = self.consumer.receive()
            raw = msg.data()
            try:
                evento = json.loads(raw)
            except Exception as e:
                logging.error(f"[CLIENTE][SAGA] Error parseando evento. Raw: {raw}. Error: {e}")
                self.consumer.acknowledge(msg)
                continue
            tipo = evento.get('type')
            data = evento.get('data', {})
            if tipo == 'ActualizarCliente':
                self.handle_actualizar(data)
            self.consumer.acknowledge(msg)

    def handle_actualizar(self, data):
        logging.info(f"[CLIENTES] Actualizar cliente: {data}")
        # Aquí puedes actualizar el estado del cliente según la acción recibida

    def close(self):
        self.client.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    consumer = ClienteSagaConsumer()
    consumer.run()
    # consumer.close() # Llamar al finalizar
