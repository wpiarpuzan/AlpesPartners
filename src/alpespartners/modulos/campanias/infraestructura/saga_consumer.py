import pulsar
import json
import logging
import os
from pulsar import ConsumerType

PULSAR_BROKER_URL = os.environ['PULSAR_BROKER_URL']
TOPIC_EVENTOS_CAMPANIAS = 'persistent://public/default/eventos-campanias'

class CampaniaSagaConsumer:
    def __init__(self):
        self.client = pulsar.Client(PULSAR_BROKER_URL)
        self.consumer = self.client.subscribe(TOPIC_EVENTOS_CAMPANIAS, subscription_name='campanias-saga', consumer_type=ConsumerType.Shared)

    def run(self):
        logging.info('[CAMPANIAS] Saga consumer iniciado')
        while True:
            msg = self.consumer.receive()
            raw = msg.data()
            try:
                evento = json.loads(raw)
            except Exception as e:
                logging.error(f"[CAMPANIAS][SAGA] Error parseando evento. Raw: {raw}. Error: {e}")
                self.consumer.acknowledge(msg)
                continue
            tipo = evento.get('type')
            data = evento.get('data', {})
            if tipo == 'CampaniaAprobada':
                self.handle_aprobada(data)
            elif tipo == 'CampaniaCancelada':
                self.handle_cancelada(data)
            self.consumer.acknowledge(msg)

    def handle_aprobada(self, data):
        logging.info(f"[CAMPANIAS] Campania aprobada: {data}")
        # Aquí puedes actualizar el estado de la campaña en la base de datos

    def handle_cancelada(self, data):
        logging.info(f"[CAMPANIAS] Campania cancelada: {data}")
        # Aquí puedes actualizar el estado de la campaña en la base de datos

    def close(self):
        self.client.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    consumer = CampaniaSagaConsumer()
    consumer.run()
    # consumer.close() # Llamar al finalizar
