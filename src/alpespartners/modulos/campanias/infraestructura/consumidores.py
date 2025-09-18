# Note: avoid calling the consumer at module import time. If run as a script,
# the entrypoint should import and call suscribirse_a_eventos_pagos explicitly
# after the functions are defined.
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
import time
import pulsar
from pulsar import ConsumerType
from alpespartners.modulos.campanias.infraestructura.event_store import append_event
from alpespartners.modulos.campanias.infraestructura.publisher import publish_event
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError

PULSAR_BROKER_URL = os.environ.get('PULSAR_BROKER_URL')
TOPIC_EVENTOS_PAGOS = 'persistent://public/default/eventos-pagos'  # Solo JSON

TOPIC_EVENTOS_PAGOS = 'persistent://public/default/eventos-pagos-json'  # Solo JSON (new dedicated topic)
# The canonical Avro topic remains 'persistent://public/default/eventos-pagos'.
# Consumers that expect JSON should subscribe to the JSON-only topic below.
def suscribirse_a_eventos_pagos():
    # Create Pulsar client and subscribe
    client = pulsar.Client(PULSAR_BROKER_URL)
    # Subscribe and read backlog for demo: use InitialPosition.Earliest so
    # new subscribers will consume existing messages produced earlier.
    # We implement a small retry loop here so we can pass the initial_position.
    consumer = None
    for attempt in range(10):
        try:
            consumer = client.subscribe(
                TOPIC_EVENTOS_PAGOS,
                subscription_name="campanias-sub-eventos-pagos",
                consumer_type=ConsumerType.Shared,
                initial_position=pulsar.InitialPosition.Earliest,
            )
            break
        except Exception as e:
            logging.warning(f"Intento {attempt+1} fallido al suscribirse a {TOPIC_EVENTOS_PAGOS}: {e}")
            time.sleep(2 ** attempt)
    if consumer is None:
        raise Exception(f"No se pudo suscribir a {TOPIC_EVENTOS_PAGOS} después de varios intentos")
    logging.info(f"[CAMPANIAS] Suscrito a eventos pagos: {TOPIC_EVENTOS_PAGOS}")

    # Create a standalone SQLAlchemy engine for background thread operations
    db_url = os.getenv('DB_URL') or os.getenv('DATABASE_URL')
    if not db_url:
        raise RuntimeError('DB_URL not set; cannot create DB engine')
    db_url_sql = db_url.replace('+psycopg2', '')
    logging.info(f"[CAMPANIAS] DB engine will use: {db_url_sql}")
    engine = create_engine(db_url_sql, pool_pre_ping=True)

    def is_event_processed_raw(aggregate_id, event_type, event_id):
        q = text("SELECT 1 FROM processed_events WHERE aggregate_id = :agg AND event_type = :et AND event_id = :eid LIMIT 1")
        with engine.connect() as c:
            r = c.execute(q, {"agg": aggregate_id, "et": event_type, "eid": event_id})
            return r.first() is not None

    def mark_event_processed_raw(aggregate_id, event_type, event_id):
        q = text("INSERT INTO processed_events (aggregate_id, event_type, event_id) VALUES (:agg, :et, :eid) ON CONFLICT DO NOTHING")
        with engine.begin() as c:
            c.execute(q, {"agg": aggregate_id, "et": event_type, "eid": event_id})

    def check_event_processed_raw(aggregate_id, event_type, event_id):
        try:
            q = text("SELECT 1 FROM processed_events WHERE aggregate_id = :agg AND event_type = :et AND event_id = :eid LIMIT 1")
            with engine.connect() as c:
                r = c.execute(q, {"agg": aggregate_id, "et": event_type, "eid": event_id})
                return r.first() is not None
        except Exception:
            return False

    def upsert_campania_view_raw(id_campania, id_cliente, estado):
        q = text(
            "INSERT INTO campanias_view (id, id_cliente, estado, updated_at) VALUES (:idc, :idcli, :est, now())"
            " ON CONFLICT (id) DO UPDATE SET id_cliente = EXCLUDED.id_cliente, estado = EXCLUDED.estado, updated_at = now()"
        )
        with engine.begin() as c:
            c.execute(q, {"idc": id_campania, "idcli": id_cliente, "est": estado})

    try:
        while True:
            try:
                msg = consumer.receive()
                raw = msg.data()
                try:
                    logging.debug(f"[CAMPANIAS] Mensaje recibido (len={len(raw)}): {raw}")
                    payload = json.loads(raw)
                except Exception as e:
                    logging.warning(f"[CAMPANIAS] Error decodificando JSON. Payload raw: {raw}. Error: {e}")
                    # If we can't parse JSON, ack and continue to avoid blocking the topic
                    consumer.acknowledge(msg)
                    continue

                logging.debug(f"[CAMPANIAS] Payload decodificado: {payload}")
                tipo = payload.get("type")
                data = payload.get("data")
                id_campania = data.get("idCampania") if data else None
                event_id = payload.get("event_id") or msg.message_id().serialize().hex()
                logging.info(f"[CAMPANIAS] Procesando evento: tipo={tipo}, id_campania={id_campania}, event_id={event_id}")

                if id_campania is None or tipo is None:
                    logging.error(f"[CAMPANIAS] Evento sin id_campania o tipo. Payload: {payload}")
                    consumer.acknowledge(msg)
                    continue

                if is_event_processed_raw(id_campania, tipo, event_id):
                    logging.info(f"[CAMPANIAS] Evento ya procesado: {event_id}")
                    consumer.acknowledge(msg)
                    continue

                if tipo == "PagoConfirmado.v1":
                    from alpespartners.modulos.campanias.dominio.entidades import CampaniaAprobada
                    from datetime import datetime
                    evento_aprobada = CampaniaAprobada(
                        idCampania=id_campania,
                        fechaAprobacion=datetime.utcnow()
                    )
                    logging.info(f"[CAMPANIAS] About to append_event for {id_campania} type=CampaniaAprobada.v1")
                    try:
                        append_res = append_event(id_campania, "CampaniaAprobada.v1", evento_aprobada.to_dict())
                        logging.info(f"[CAMPANIAS] append_event result: {append_res}")
                    except Exception:
                        logging.exception(f"[CAMPANIAS] append_event failed for {id_campania}")
                    logging.info(f"[CAMPANIAS] append_event complete for {id_campania} type=CampaniaAprobada.v1")
                    try:
                        upsert_campania_view_raw(id_campania, data.get("idCliente"), "APROBADA")
                        logging.info(f"[CAMPANIAS] Upsert campanias_view successful for {id_campania}")
                    except IntegrityError as ie:
                        logging.error(f"[CAMPANIAS] IntegrityError on upsert APROBADA: {ie}")
                        # Mark processed to avoid retry storm; payload should be fixed upstream.
                        mark_event_processed_raw(id_campania, tipo, event_id)
                        consumer.acknowledge(msg)
                        logging.info(f"[CAMPANIAS] Evento marcado procesado tras IntegrityError: {event_id}")
                        continue
                    publish_event("CampaniaAprobada.v1", evento_aprobada.to_dict())
                    logging.info(f"[CAMPANIAS] Campania APROBADA: {id_campania}")

                elif tipo == "PagoRevertido.v1":
                    from alpespartners.modulos.campanias.dominio.entidades import CampaniaCancelada
                    from datetime import datetime
                    evento_cancelada = CampaniaCancelada(
                        idCampania=id_campania,
                        motivo=data.get('motivo', 'Pago fallido'),
                        fechaCancelacion=datetime.utcnow()
                    )
                    logging.info(f"[CAMPANIAS] About to append_event for {id_campania} type=CampaniaCancelada.v1")
                    try:
                        append_res = append_event(id_campania, "CampaniaCancelada.v1", evento_cancelada.to_dict())
                        logging.info(f"[CAMPANIAS] append_event result: {append_res}")
                    except Exception:
                        logging.exception(f"[CAMPANIAS] append_event failed for {id_campania}")
                    logging.info(f"[CAMPANIAS] append_event complete for {id_campania} type=CampaniaCancelada.v1")
                    try:
                        upsert_campania_view_raw(id_campania, data.get("idCliente"), "CANCELADA")
                    except IntegrityError as ie:
                        logging.error(f"[CAMPANIAS] IntegrityError on upsert CANCELADA: {ie}")
                        mark_event_processed_raw(id_campania, tipo, event_id)
                        consumer.acknowledge(msg)
                        logging.info(f"[CAMPANIAS] Evento marcado procesado tras IntegrityError: {event_id}")
                        continue
                    publish_event("CampaniaCancelada.v1", evento_cancelada.to_dict())
                    logging.info(f"[CAMPANIAS] Campania CANCELADA: {id_campania}")

                # mark as processed (idempotency)
                try:
                    mark_event_processed_raw(id_campania, tipo, event_id)
                    try:
                        exists = check_event_processed_raw(id_campania, tipo, event_id)
                    except NameError:
                        exists = is_event_processed_raw(id_campania, tipo, event_id)
                    logging.info(f"[CAMPANIAS] Evento marcado como procesado: {event_id} (aggregate={id_campania}, type={tipo}) - persisted={exists}")
                except Exception:
                    logging.exception(f"[CAMPANIAS] Error marcando evento como procesado: {event_id}")

                consumer.acknowledge(msg)

            except Exception as e:
                import traceback
                logging.error(f"[CAMPANIAS] Error procesando evento de pagos: {e}\n{traceback.format_exc()}")
                try:
                    consumer.negative_acknowledge(msg)
                except Exception:
                    pass

    finally:
        try:
            consumer.close()
        except Exception:
            pass
        try:
            client.close()
        except Exception:
            pass