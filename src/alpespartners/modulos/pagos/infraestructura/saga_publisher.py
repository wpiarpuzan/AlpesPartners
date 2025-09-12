import pulsar
import json
import logging
from pulsar import ConsumerType

PULSAR_BROKER_URL = 'pulsar://broker:6650'
TOPIC_COMANDOS_PAGOS = 'persistent://public/default/comandos-pagos'
TOPIC_EVENTOS_PAGOS = 'persistent://public/default/eventos-pagos'

class PagosSagaPublisher:
    def __init__(self):
        self.client = pulsar.Client(PULSAR_BROKER_URL)
        self.consumer = self.client.subscribe(TOPIC_COMANDOS_PAGOS, subscription_name='pagos-saga-pub', consumer_type=ConsumerType.Shared)
        self.producer = self.client.create_producer(TOPIC_EVENTOS_PAGOS)

    def run(self):
        logging.info('[PAGOS] Saga publisher iniciado')
        while True:
            msg = self.consumer.receive()
            comando = json.loads(msg.data())
            tipo = comando.get('type')
            data = comando.get('data', {})
            if tipo == 'ProcesarPago':
                self.publicar_evento_exitoso(data)
            self.consumer.acknowledge(msg)

    def publicar_evento_exitoso(self, data):
        # Simulación: siempre éxito, en la práctica aquí iría la lógica real
        evento = {'type': 'PagoExitoso', 'data': data}
        self.producer.send(json.dumps(evento).encode('utf-8'))
        logging.info(f"[PAGOS] Evento PagoExitoso publicado: {data}")

    def close(self):
        self.client.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    publisher = PagosSagaPublisher()
    publisher.run()
    # publisher.close() # Llamar al finalizar
