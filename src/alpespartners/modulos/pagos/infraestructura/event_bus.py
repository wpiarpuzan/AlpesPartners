import os
try:
    import pulsar
except Exception:
    pulsar = None

TOPIC = os.getenv("PAGOS_TOPIC", "persistent://public/default/pagos")

def publicar_evento(evento):
    # Stub si no hay pulsar
    if pulsar is None:
        print(f"[EVENTO] {evento.__class__.__name__}: {evento}")
        return

    client = pulsar.Client(f"pulsar://{os.getenv('PULSAR_ADDRESS','localhost')}:6650")
    producer = client.create_producer(TOPIC)
    producer.send(str(evento).encode("utf-8"))
    producer.close()
    client.close()
