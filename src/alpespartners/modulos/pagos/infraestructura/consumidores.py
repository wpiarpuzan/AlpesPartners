import pulsar, _pulsar
from pulsar.schema import *
import logging
import traceback
import json

from alpespartners.modulos.pagos.infraestructura.schema.v1.comandos import ComandoProcesarPago
from alpespartners.modulos.pagos.infraestructura.schema.v1.eventos import EventoPagoExitoso, EventoPagoFallido

from alpespartners.seedwork.infraestructura import utils

def suscribirse_a_comandos(app=None):
    """
    Suscribe el servicio al tópico de comandos de pagos en Pulsar.
    """
    cliente = None
    try:
        import os
        PULSAR_BROKER_URL = os.environ['PULSAR_BROKER_URL']
        cliente = pulsar.Client(PULSAR_BROKER_URL)
        consumidor = cliente.subscribe(
            'comandos-pagos', 
            consumer_type=_pulsar.ConsumerType.Shared,
            subscription_name='alpespartners-sub-comandos-pagos', 
            schema=AvroSchema(ComandoProcesarPago)
        )

        logging.info("========= Suscripción a comandos de pagos iniciada =========")

        # Productor para eventos de pagos (Avro canonical)
        producer_avro = cliente.create_producer(
            'persistent://public/default/eventos-pagos',
            schema=AvroSchema(EventoPagoExitoso)
        )
        # Producer para eventos JSON (compatibilidad - new JSON topic)
        producer_json = cliente.create_producer('persistent://public/default/eventos-pagos-json')
        from alpespartners.modulos.pagos.infraestructura.repositorios import PayoutRepositorioSQLAlchemy
        repo = PayoutRepositorioSQLAlchemy()
        while True:
            mensaje = consumidor.receive()
            data = mensaje.value().data
            correlation_id = mensaje.value().correlation_id
            logging.info(f"Comando de pago recibido: {data} con correlation_id: {correlation_id}")

            # Simulación de procesamiento de pago
            try:
                from datetime import datetime
                evento = EventoPagoExitoso(
                    payout_id="payout-" + data.partner_id + "-" + data.cycle_id,
                    partner_id=data.partner_id,
                    cycle_id=data.cycle_id,
                    total_amount=100.0,
                    currency="USD",
                    completed_at=int(datetime.utcnow().timestamp()),
                    confirmation_id="conf-" + data.partner_id + "-" + data.cycle_id,
                    correlation_id=correlation_id
                )
                # Publicar en Avro (para otros consumers)
                producer_avro.send(evento)
                logging.info(f"[PAGOS] EventoPagoExitoso publicado (Avro): {evento}")

                # Publicar en JSON (para campanias)
                evento_json = {
                    "type": "PagoConfirmado.v1",
                    "data": {
                        "idCampania": data.cycle_id,
                        "idCliente": data.partner_id,
                        "monto": 100.0,
                        "moneda": "USD",
                        "fecha": datetime.utcnow().isoformat(),
                        "confirmation_id": "conf-" + data.partner_id + "-" + data.cycle_id
                    },
                    "event_id": correlation_id
                }
                # Serializar y enviar el JSON como un solo mensaje
                # Refuerzo: solo enviar UN mensaje por evento, nunca fragmentos ni partes
                evento_json_str = json.dumps(evento_json, ensure_ascii=False)
                evento_json_bytes = evento_json_str.encode('utf-8')
                logging.info(f"[PAGOS] Enviando evento JSON a topic eventos-pagos-json: {evento_json_str}")
                producer_json.send(evento_json_bytes)
                logging.info(f"[PAGOS] EventoPagoExitoso publicado (JSON, bytes={len(evento_json_bytes)}): {evento_json}")

                # Persistir en outbox (ambos formatos)
                try:
                    logging.info(f"[PAGOS] Guardando en outbox (Avro): {evento.to_dict()}")
                    repo.guardar_evento_outbox("PagoConfirmado.v1", evento.to_dict())
                    logging.info(f"[PAGOS] Guardado en outbox (Avro) OK")
                except Exception as e:
                    logging.error(f"[PAGOS] Error guardando en outbox (Avro): {e}")
                try:
                    logging.info(f"[PAGOS] Guardando en outbox (JSON): {evento_json}")
                    logging.info(f"[PAGOS] Guardando en outbox (JSON): {evento_json}")
                    # store json copy as well for traceability
                    repo.guardar_evento_outbox("PagoConfirmado.v1", evento_json)
                    logging.info(f"[PAGOS] Guardado en outbox (JSON) OK")
                except Exception as e:
                    logging.error(f"[PAGOS] Error guardando en outbox (JSON): {e}")
            except Exception as e:
                logging.error(f"Error procesando pago: {e}")
                # Si falla, podrías publicar EventoPagoFallido aquí
            consumidor.acknowledge(mensaje)
        cliente.close()
    except Exception:
        logging.error('ERROR: Suscribiéndose al tópico de comandos de pagos!')
        traceback.print_exc()
        if cliente:
            cliente.close()

def suscribirse_a_eventos(app=None):
    """
    Suscribe el servicio al tópico de eventos de pagos en Pulsar.
    Esto permite que el propio servicio u otros interesados reaccionen a los
    resultados del procesamiento de pagos.
    """
    cliente = None
    try:
        # Se suscribe a múltiples eventos usando una lista de esquemas
        # En un escenario real, podrías tener tópicos separados para éxito y fallo.

        import os
        PULSAR_BROKER_URL = os.environ['PULSAR_BROKER_URL']
        cliente = pulsar.Client(PULSAR_BROKER_URL)

        # Try Avro subscription first; if that fails, subscribe without schema and
        # decode raw bytes as JSON (compat mode for campanias compatibility)
        try:
            consumidor = cliente.subscribe(
                'persistent://public/default/eventos-pagos',
                consumer_type=_pulsar.ConsumerType.Shared,
                subscription_name='alpespartners-sub-eventos-pagos',
                schema=AvroSchema(EventoPagoExitoso)
            )
            using_avro = True
        except Exception:
            logging.warning('[PAGOS] Avro subscribe failed, subscribing without schema (bytes)')
            consumidor = cliente.subscribe(
                'persistent://public/default/eventos-pagos',
                consumer_type=_pulsar.ConsumerType.Shared,
                subscription_name='alpespartners-sub-eventos-pagos'
            )
            using_avro = False

        logging.info("========= Suscripción a eventos de pagos iniciada =========")

        while True:
            mensaje = consumidor.receive()
            try:
                if using_avro:
                    # Try decoding as Avro first. If decoding fails (e.g. message is
                    # plain JSON bytes or otherwise not written with the Avro schema),
                    # fall back to raw bytes -> JSON decoding to avoid noise and to
                    # allow graceful handling of mixed-format topics.
                    try:
                        valor = mensaje.value()
                    except Exception as decode_err:
                        logging.warning(f"Failed to decode message as Avro: {decode_err}")
                        # Fallback: try to parse raw bytes as JSON
                        try:
                            raw = mensaje.data()
                            decoded = raw.decode('utf-8') if isinstance(raw, (bytes, bytearray)) else raw
                            parsed = json.loads(decoded)
                            logging.info(f"Evento (fallback JSON) recibido: {parsed}")
                        except Exception as json_err:
                            logging.warning(f"Fallback JSON decode also failed: {json_err}; raw={mensaje.data()}")
                        # Acknowledge the message to avoid retry storms; we don't want
                        # the Avro consumer to keep failing on the same message.
                        try:
                            consumidor.acknowledge(mensaje)
                        except Exception:
                            pass
                        # move to next message
                        continue

                    # If Avro decode succeeded, handle known Avro event types
                    if isinstance(valor, EventoPagoExitoso):
                        logging.info(f"Evento de PAGO EXITOSO recibido (Avro): {valor}")
                    elif isinstance(valor, EventoPagoFallido):
                        logging.info(f"Evento de PAGO FALLIDO recibido (Avro): {valor}")
                    else:
                        logging.warning(f"Evento Avro desconocido: {type(valor)}")
                else:
                    raw = mensaje.data()
                    try:
                        decoded = raw.decode('utf-8') if isinstance(raw, (bytes, bytearray)) else raw
                        parsed = json.loads(decoded)
                        logging.info(f"Evento (JSON bytes) recibido: {parsed}")
                    except Exception:
                        logging.warning(f"No se pudo decodificar mensaje como JSON: {raw}")

                consumidor.acknowledge(mensaje)
            except Exception:
                logging.exception('Error procesando mensaje de eventos-pagos')
                try:
                    consumidor.negative_acknowledge(mensaje)
                except Exception:
                    pass

        cliente.close()
    except Exception:
        logging.error('ERROR: Suscribiéndose al tópico de eventos de pagos!')
        traceback.print_exc()
        if cliente:
            cliente.close()

