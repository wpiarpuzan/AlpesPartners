import os
import json
import pulsar
from threading import Lock

_pulsar_client = None
_producer = None
_lock = Lock()

# Allow overriding broker url and topic via env (compose already sets these)
PULSAR_BROKER_URL = os.getenv('PULSAR_BROKER_URL', 'pulsar://broker:6650')
TOPIC_EVENTOS_PAGOS = os.getenv('TOPIC_EVENTOS_PAGOS', 'persistent://public/default/eventos-pagos-json')

# Operation timeout (seconds) for client operations like producer creation/send.
# Increase from defaults to tolerate broker startup delays in CI/local compose.
OPERATION_TIMEOUT = int(os.getenv('PULSAR_OPERATION_TIMEOUT', '120'))

def get_producer():
    """Lazily create a Pulsar client and producer with a moderate operation timeout.

    This function is thread-safe and will reuse the same client/producer once created.
    It will raise a RuntimeError with a clear message if Pulsar operations time out.
    """
    global _pulsar_client, _producer
    with _lock:
        try:
            if _pulsar_client is None:
                _pulsar_client = pulsar.Client(PULSAR_BROKER_URL, operation_timeout_seconds=OPERATION_TIMEOUT)
            if _producer is None:
                # create_producer may block until broker acknowledges; rely on client's operation timeout
                _producer = _pulsar_client.create_producer(TOPIC_EVENTOS_PAGOS)
        except Exception as exc:
            # Normalize errors so the API can return a friendly JSON message
            raise RuntimeError(f"Pulsar error during producer creation: {exc}")
    return _producer

def publish_event(type_: str, data: dict):
    envelope = {"type": type_, "data": data}
    try:
        producer = get_producer()
        producer.send(json.dumps(envelope).encode('utf-8'))
    except Exception as exc:
        # Re-raise as RuntimeError with a short message for the Flask handler to return
        raise RuntimeError(f"Pulsar error: {exc}")
