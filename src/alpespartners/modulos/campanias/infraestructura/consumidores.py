import time
def subscribe_with_retry(client, topic, subscription_name, consumer_type=None, max_retries=10):
    for attempt in range(max_retries):
        try:
            kwargs = {"subscription_name": subscription_name}
            if consumer_type is not None:
                kwargs["consumer_type"] = consumer_type
            return client.subscribe(topic, **kwargs)
        except Exception as e:
            logging.warning(f"Intento {attempt+1} fallido al suscribirse a {topic}: {e}")
            time.sleep(2 ** attempt)
    raise Exception(f"No se pudo suscribir a {topic} después de varios intentos")
import os
import json
import logging
import pulsar
from pulsar import ConsumerType
from alpespartners.modulos.campanias.infraestructura.event_store import append_event
from alpespartners.modulos.campanias.infraestructura.publisher import publish_event
from alpespartners.modulos.campanias.infraestructura.repos import CampaniaViewRepo
from alpespartners.config.db import db

PULSAR_BROKER_URL = os.getenv('PULSAR_BROKER_URL', 'pulsar://broker:6650')
TOPIC_EVENTOS_PAGOS = os.getenv('TOPIC_EVENTOS_PAGOS', 'persistent://public/default/eventos.pagos')


def suscribirse_a_eventos_pagos():
    import os
    PULSAR_BROKER_URL = os.getenv('PULSAR_BROKER_URL', 'pulsar://broker:6650')
    client = pulsar.Client(PULSAR_BROKER_URL)
    consumer = subscribe_with_retry(
        client,
        TOPIC_EVENTOS_PAGOS,
        subscription_name="campanias-sub-eventos-pagos",
        consumer_type=ConsumerType.Shared
    )
    logging.info(f"[CAMPANIAS] Suscrito a eventos pagos: {TOPIC_EVENTOS_PAGOS}")
    repo = CampaniaViewRepo(db.session)
    while True:
        msg = consumer.receive()
        try:
            payload = json.loads(msg.data())
            tipo = payload.get("type")
            data = payload.get("data")
            id_campania = data.get("idCampania")
            if tipo == "PagoConfirmado":
                append_event(id_campania, "CampaniaAprobada.v1", data)
                repo.upsert(id_campania, data.get("idCliente"), "APROBADA")
                publish_event("CampaniaAprobada.v1", data)
                logging.info(f"[CAMPANIAS] Campania APROBADA: {id_campania}")
            elif tipo == "PagoRevertido":
                append_event(id_campania, "CampaniaCancelada.v1", data)
                repo.upsert(id_campania, data.get("idCliente"), "CANCELADA")
                publish_event("CampaniaCancelada.v1", data)
                logging.info(f"[CAMPANIAS] Campania CANCELADA: {id_campania}")
            consumer.acknowledge(msg)
        except Exception as e:
            logging.error(f"[CAMPANIAS] Error procesando evento de pagos: {e}")
            consumer.negative_acknowledge(msg)