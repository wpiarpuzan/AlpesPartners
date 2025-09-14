import pulsar
import json
import logging
from pulsar import ConsumerType

PULSAR_BROKER_URL = 'pulsar://localhost:6650'
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
            print(f'[PULSAR][CONSUMO][COMANDO] Comando recibido en Pulsar: {msg.data()}')
            comando = json.loads(msg.data())
            tipo = comando.get('type')
            data = comando.get('data', {})
            if tipo == 'ProcesarPago':
                print(f'[PULSAR][CONSUMO][PROCESO] Procesando comando ProcesarPago: {data}')
                self.publicar_evento_exitoso(data)
            else:
                print(f'[PULSAR][CONSUMO] Comando ignorado: {tipo}')
            self.consumer.acknowledge(msg)

    def publicar_evento_exitoso(self, data):
        # Crear y guardar el payout en la base de datos
        from alpespartners.modulos.pagos.dominio.entidades import Payout
        from alpespartners.modulos.pagos.infraestructura.repositorios import PayoutRepositorioSQLAlchemy
        from alpespartners.config.db import db
        payout = Payout.crear(
            partner_id=data.get('partner_id'),
            cycle_id=data.get('cycle_id'),
            payment_method_type=data.get('payment_method_type'),
            payment_method_mask=data.get('payment_method_mask')
        )
        repo = PayoutRepositorioSQLAlchemy(session=db.session)
        repo.agregar(payout)
        db.session.commit()
        print(f"[PULSAR][CONSUMO][DB] Payout guardado en la base de datos: {payout}")
        # Publicar evento de éxito
        evento = {'type': 'PagoExitoso', 'data': payout.__dict__}
        self.producer.send(json.dumps(evento).encode('utf-8'))
        print(f"[PULSAR][PUBLICACION] Evento PagoExitoso publicado en Pulsar: {evento}")

    def close(self):
        self.client.close()

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO, force=True)
    publisher = PagosSagaPublisher()
    publisher.run()
    # publisher.close() # Llamar al finalizar
