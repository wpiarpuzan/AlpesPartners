import json
import os
import logging

TOPIC_EVENTOS_PAGOS = os.getenv('TOPIC_EVENTOS_PAGOS', 'persistent://public/default/eventos.pagos')


def publish_event(event_type, data):
    """Publish an event to Pulsar if configured. In demo/DB_OUTBOX mode (no PULSAR_BROKER_URL)
    we log the event and return silently so the outbox poller can mark rows SENT.
    """
    pulsar_broker_url = os.environ.get('PULSAR_BROKER_URL')
    envelope = {"type": event_type, "data": data}
    if not pulsar_broker_url:
        logging.info(f"[publisher] Pulsar not configured, skipping publish for event: {event_type} payload={data}")
        return

    try:
        # import lazily to avoid import-time failure when pulsar client isn't installed
        import pulsar
        client = pulsar.Client(pulsar_broker_url)
        producer = client.create_producer(TOPIC_EVENTOS_PAGOS)
        producer.send(json.dumps(envelope).encode("utf-8"))
        client.close()
        logging.info(f"[publisher] published event {event_type} to Pulsar at {pulsar_broker_url}")
    except Exception:
        logging.exception("[publisher] failed to publish event to Pulsar")
        # Propagate exception so caller can decide (outbox poller may retry)
        raise
