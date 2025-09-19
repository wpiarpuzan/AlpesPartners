import os
import json
import pulsar
from threading import Lock

_pulsar_client = None
_producer = None
_lock = Lock()


PULSAR_BROKER_URL = os.getenv('PULSAR_BROKER_URL', 'pulsar://broker:6650')
TOPIC_EVENTOS_CAMPANIAS = os.getenv('TOPIC_EVENTOS_CAMPANIAS', 'persistent://public/default/eventos.campanias')


def get_producer():
    global _pulsar_client, _producer
    with _lock:
        # Try to create a Pulsar client and producer with retries to tolerate broker startup delays
        if _pulsar_client is None:
            attempts = int(os.getenv('PULSAR_CONNECT_ATTEMPTS', '5'))
            delay = float(os.getenv('PULSAR_CONNECT_DELAY', '1'))
            last_exc = None
            for i in range(1, attempts + 1):
                try:
                    _pulsar_client = pulsar.Client(PULSAR_BROKER_URL)
                    break
                except Exception as e:
                    last_exc = e
                    # backoff
                    time_to_sleep = delay * i
                    print(f"[PUBLISHER] Pulsar client connect attempt {i}/{attempts} failed: {e}. Retrying in {time_to_sleep}s")
                    import time
                    time.sleep(time_to_sleep)
            else:
                raise RuntimeError(f"Pulsar client connection failed after {attempts} attempts: {last_exc}")

        if _producer is None:
            attempts = int(os.getenv('PULSAR_PRODUCER_ATTEMPTS', '3'))
            delay = float(os.getenv('PULSAR_PRODUCER_DELAY', '1'))
            last_exc = None
            for i in range(1, attempts + 1):
                try:
                    _producer = _pulsar_client.create_producer(TOPIC_EVENTOS_CAMPANIAS)
                    break
                except Exception as e:
                    last_exc = e
                    time_to_sleep = delay * i
                    print(f"[PUBLISHER] create_producer attempt {i}/{attempts} failed: {e}. Retrying in {time_to_sleep}s")
                    import time
                    time.sleep(time_to_sleep)
            else:
                raise RuntimeError(f"Pulsar create_producer failed after {attempts} attempts: {last_exc}")
    return _producer

def publish_event(type_: str, data: dict):
    envelope = {"type": type_, "data": data}
    producer = get_producer()
    # Try sending with a small retry loop to handle transient broker hiccups
    attempts = int(os.getenv('PULSAR_SEND_ATTEMPTS', '3'))
    delay = float(os.getenv('PULSAR_SEND_DELAY', '0.5'))
    last_exc = None
    for i in range(1, attempts + 1):
        try:
            producer.send(json.dumps(envelope).encode('utf-8'))
            return
        except Exception as e:
            last_exc = e
            time_to_sleep = delay * i
            print(f"[PUBLISHER] send attempt {i}/{attempts} failed: {e}. Retrying in {time_to_sleep}s")
            import time
            time.sleep(time_to_sleep)
    # If we reach here, all attempts failed
    raise RuntimeError(f"Pulsar publish failed after {attempts} attempts: {last_exc}")