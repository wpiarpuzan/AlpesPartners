import pulsar
import json
import logging
import os
from pulsar import ConsumerType

PULSAR_BROKER_URL = os.environ['PULSAR_BROKER_URL']
TOPIC_COMANDOS_CAMPANIAS = 'persistent://public/default/comandos-campanias'
TOPIC_EVENTOS_CAMPANIAS = 'persistent://public/default/eventos-campanias'

class CampaniasSagaPublisher:
    def __init__(self):
        self.client = pulsar.Client(PULSAR_BROKER_URL)
        self.consumer = self.client.subscribe(TOPIC_COMANDOS_CAMPANIAS, subscription_name='campanias-saga-pub', consumer_type=ConsumerType.Shared)
        self.producer = self.client.create_producer(TOPIC_EVENTOS_CAMPANIAS)

    def run(self):
        logging.info('[CAMPANIAS] Saga publisher iniciado')
        while True:
            msg = self.consumer.receive()
            raw = msg.data()
            try:
                comando = json.loads(raw)
            except Exception as e:
                logging.error(f"[CAMPANIAS][SAGA_PUBLISHER] Error parseando comando. Raw: {raw}. Error: {e}")
                self.consumer.acknowledge(msg)
                continue
            tipo = comando.get('type')
            data = comando.get('data', {})
            if tipo == 'CampaniaCreada':
                self.publicar_evento_creada(data)
            elif tipo == 'CampaniaAprobada':
                self.publicar_evento_aprobada(data)
            elif tipo == 'CampaniaCancelada':
                self.publicar_evento_cancelada(data)
            self.consumer.acknowledge(msg)

    def publicar_evento_creada(self, data):
        evento = {'type': 'CampaniaCreada', 'data': data}
        self.producer.send(json.dumps(evento).encode('utf-8'))
        logging.info(f"[CAMPANIAS] Evento CampaniaCreada publicado: {data}")

    def publicar_evento_aprobada(self, data):
        evento = {'type': 'CampaniaAprobada', 'data': data}
        self.producer.send(json.dumps(evento).encode('utf-8'))
        logging.info(f"[CAMPANIAS] Evento CampaniaAprobada publicado: {data}")

    def publicar_evento_cancelada(self, data):
        evento = {'type': 'CampaniaCancelada', 'data': data}
        self.producer.send(json.dumps(evento).encode('utf-8'))
        logging.info(f"[CAMPANIAS] Evento CampaniaCancelada publicado: {data}")

    def close(self):
        self.client.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    publisher = CampaniasSagaPublisher()
    publisher.run()
    # publisher.close() # Llamar al finalizar
