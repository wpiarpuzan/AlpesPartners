import pulsar
import json
import logging
from pulsar import ConsumerType

import os
import os
TOPIC_COMANDOS_PAGOS = 'persistent://public/default/comandos-pagos'
TOPIC_EVENTOS_PAGOS = 'persistent://public/default/eventos-pagos'
TOPIC_EVENTOS_PAGOS_JSON = 'persistent://public/default/eventos-pagos-json'  # JSON-only mirror topic for consumers that expect JSON

class PagosSagaPublisher:
    def __init__(self):
        pulsar_broker_url = os.environ['PULSAR_BROKER_URL']
        self.client = pulsar.Client(pulsar_broker_url)
        self.consumer = self.client.subscribe(TOPIC_COMANDOS_PAGOS, subscription_name='pagos-saga-pub', consumer_type=ConsumerType.Shared)
        # Avro producer (canonical)
        self.producer = self.client.create_producer(TOPIC_EVENTOS_PAGOS)
        # JSON-only producer (mirror for JSON consumers)
        self.producer_json = self.client.create_producer(TOPIC_EVENTOS_PAGOS_JSON)

    def run(self):
        logging.info('[PAGOS] Saga publisher iniciado')
        while True:
            msg = self.consumer.receive()
            raw = msg.data()
            print(f'[PULSAR][CONSUMO][COMANDO] Comando recibido en Pulsar (len={len(raw)}): {raw}')
            try:
                comando = json.loads(raw)
            except Exception as e:
                logging.error(f"[PAGOS][SAGA_PUBLISHER] Error parseando comando. Raw: {raw}. Error: {e}")
                self.consumer.acknowledge(msg)
                continue
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
        # Guardar evento en outbox
        evento = {'type': 'PagoConfirmado.v1', 'data': payout.__dict__}
        repo.guardar_evento_outbox('PagoConfirmado.v1', payout.__dict__)
        print(f"[OUTBOX][GUARDADO] Evento PagoConfirmado.v1 guardado en outbox: {evento}")
            # publish JSON mirror for compatibility
            try:
                self.producer_json.send(json.dumps(evento).encode('utf-8'))
            except Exception:
                # best-effort mirror; outbox guarantees delivery
                logging.exception('Failed to publish JSON mirror to eventos-pagos-json')

    def close(self):
        self.client.close()

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO, force=True)
    publisher = PagosSagaPublisher()
    publisher.run()
    # publisher.close() # Llamar al finalizar
