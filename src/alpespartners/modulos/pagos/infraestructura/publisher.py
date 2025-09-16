import json
import pulsar
import os

import os
TOPIC_EVENTOS_PAGOS = os.getenv('TOPIC_EVENTOS_PAGOS', 'persistent://public/default/eventos.pagos')

def publish_event(event_type, data):
    pulsar_broker_url = os.environ['PULSAR_BROKER_URL']
    client = pulsar.Client(pulsar_broker_url)
    producer = client.create_producer(TOPIC_EVENTOS_PAGOS)
    envelope = {"type": event_type, "data": data}
    producer.send(json.dumps(envelope).encode("utf-8"))
    client.close()
