import os
import json
import pulsar
from threading import Lock

_pulsar_client = None
_producer = None
_lock = Lock()

PULSAR_BROKER_URL = os.getenv('PULSAR_BROKER_URL', 'pulsar://broker:6650')
# Use the JSON-only pagos topic by default so JSON producers hit consumers subscribed to the JSON topic
TOPIC_EVENTOS_PAGOS = os.getenv('TOPIC_EVENTOS_PAGOS', 'persistent://public/default/eventos-pagos-json')

def get_producer():
    global _pulsar_client, _producer
    with _lock:
        if _pulsar_client is None:
            _pulsar_client = pulsar.Client(PULSAR_BROKER_URL)
        if _producer is None:
            _producer = _pulsar_client.create_producer(TOPIC_EVENTOS_PAGOS)
    return _producer

def publish_event(type_: str, data: dict):
    envelope = {"type": type_, "data": data}
    producer = get_producer()
    producer.send(json.dumps(envelope).encode('utf-8'))
