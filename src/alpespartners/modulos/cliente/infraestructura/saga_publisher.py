"""Deprecated: Migrado a `src/cliente`.

Este archivo se deja como marcador temporal.
"""

raise RuntimeError("Este módulo fue migrado a `cliente` y no debe usarse.")
import pulsar
import json
import logging
from pulsar import ConsumerType

import os
TOPIC_COMANDOS_CLIENTES = 'persistent://public/default/comandos-clientes'
TOPIC_EVENTOS_CLIENTES = 'persistent://public/default/eventos-clientes'

class ClienteSagaPublisher:
    def __init__(self):
        pulsar_broker_url = os.environ['PULSAR_BROKER_URL']
        self.client = pulsar.Client(pulsar_broker_url)
        self.consumer = self.client.subscribe(TOPIC_COMANDOS_CLIENTES, subscription_name='clientes-saga-pub', consumer_type=ConsumerType.Shared)
        self.producer = self.client.create_producer(TOPIC_EVENTOS_CLIENTES)

    def run(self):
        logging.info('[CLIENTES] Saga publisher iniciado')
        while True:
            msg = self.consumer.receive()
            raw = msg.data()
            try:
                comando = json.loads(raw)
            except Exception as e:
                logging.error(f"[CLIENTE][SAGA_PUBLISHER] Error parseando comando. Raw: {raw}. Error: {e}")
                self.consumer.acknowledge(msg)
                continue
            tipo = comando.get('type')
            data = comando.get('data', {})
            if tipo == 'ActualizarCliente':
                self.publicar_evento(data)
            self.consumer.acknowledge(msg)

    def publicar_evento(self, data):
        evento = {'type': 'ActualizarCliente', 'data': data}
        self.producer.send(json.dumps(evento).encode('utf-8'))
        logging.info(f"[CLIENTES] Evento ActualizarCliente publicado: {data}")

    def close(self):
        self.client.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    publisher = ClienteSagaPublisher()
    publisher.run()
    # publisher.close() # Llamar al finalizar
