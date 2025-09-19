import pulsar
import json
import logging
from pulsar import ConsumerType

import os
TOPIC_EVENTOS_PAGOS = 'persistent://public/default/eventos-pagos-json'

class PagosSagaConsumer:
    def __init__(self):
        pulsar_broker_url = os.environ['PULSAR_BROKER_URL']
        self.client = pulsar.Client(pulsar_broker_url)
        self.consumer = self.client.subscribe(TOPIC_EVENTOS_PAGOS, subscription_name='pagos-saga', consumer_type=ConsumerType.Shared)

    def run(self):
        logging.info('[PAGOS] Saga consumer iniciado')
        while True:
            msg = self.consumer.receive()
            raw = msg.data()
            try:
                evento = json.loads(raw)
            except Exception as e:
                logging.error(f"[PAGOS] Error decodificando evento saga. Raw: {raw}. Error: {e}")
                self.consumer.acknowledge(msg)
                continue
            tipo = evento.get('type')
            data = evento.get('data', {})
            if tipo == 'PagoExitoso':
                self.handle_exitoso(data)
            elif tipo == 'PagoFallido':
                self.handle_fallido(data)
            self.consumer.acknowledge(msg)

    def handle_exitoso(self, data):
        logging.info(f"[PAGOS] Pago exitoso: {data}")

    def handle_fallido(self, data):
        logging.info(f"[PAGOS] Pago fallido: {data}")

    def close(self):
        self.client.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    consumer = PagosSagaConsumer()
    consumer.run()
