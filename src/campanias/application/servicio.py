"""
CampaniasService: Orquesta la lógica de campanias (event sourcing, proyección, integración Pulsar).
"""
import logging
from campanias.domain.entidades import Campania
from campanias.domain.eventos import CampaniaCreada, CampaniaAprobada, CampaniaCancelada
from campanias.infrastructure.repos import CampaniaViewRepo
from campanias.application.dto import CrearCampaniaDTO
from alpespartners.config.db import db
from alpespartners.seedwork.infraestructura import utils
import pulsar
import json
import threading
from datetime import datetime
from campanias.domain.entidades import EstadoCampania
from campanias.infrastructure.event_store import append_event
from campanias.infrastructure.publisher import publish_event

# Pulsar topics (should come from config)
TOPIC_COMANDOS_CAMPANIAS = 'persistent://public/default/comandos.campanias'
TOPIC_EVENTOS_CAMPANIAS = 'persistent://public/default/eventos.campanias'
TOPIC_EVENTOS_PAGOS = 'persistent://public/default/eventos.pagos'

class CampaniasService:
    def __init__(self, db_session=None):
        import os
        self.db_session = db_session or db.session
        self.proy_repo = CampaniaViewRepo(self.db_session)
        PULSAR_BROKER_URL = os.getenv('PULSAR_BROKER_URL', 'pulsar://broker:6650')
        self.pulsar_client = pulsar.Client(PULSAR_BROKER_URL)
        self.eventos_producer = self.pulsar_client.create_producer(TOPIC_EVENTOS_CAMPANIAS)

    def handle_crear_campania(self, cmd: CrearCampaniaDTO):
        """Valida, persiste evento, actualiza proyección y publica evento integración."""
        # 1. Validación y creación de dominio
        campania = Campania.crear(cmd.idCampania, cmd.idCliente, cmd.itinerario)
        evento = CampaniaCreada(cmd.idCampania, cmd.idCliente, cmd.itinerario, datetime.utcnow())
        # 2. Append event sourcing
        self.event_repo.append_event(evento)
        # 3. Upsert proyección
        self.proy_repo.upsert(cmd.idCampania, estado="CREADA")
        # 4. Publicar evento integración
        self.publish_event("CampaniaCreada", evento)
        logging.info(f"Campania creada: {cmd.idCampania}")

    def publish_event(self, tipo, evento):
        envelope = {"type": tipo, "data": evento.to_dict()}
        self.eventos_producer.send(json.dumps(envelope).encode("utf-8"))

    def subscribe_eventos_pagos(self):
        """Suscribe a eventos.pagos y reacciona a PagoConfirmado/PagoRevertido."""
        def _consume():
            consumer = self.pulsar_client.subscribe(
                TOPIC_EVENTOS_PAGOS,
                subscription_name="campanias-sub",
                consumer_type=pulsar.ConsumerType.Shared
            )
            while True:
                msg = consumer.receive()
                try:
                    raw = msg.data()
                    try:
                        payload = json.loads(raw)
                    except Exception as e:
                        logging.error(f"[CAMPANIAS][APLICACION] Error parseando payload. Raw: {raw}. Error: {e}")
                        consumer.acknowledge(msg)
                        continue
                    tipo = payload.get("type")
                    data = payload.get("data")
                    idCampania = data.get("idCampania")
                    if tipo == "PagoConfirmado":
                        evento = CampaniaAprobada(idCampania, datetime.utcnow(), origen="PAGOS")
                        self.event_repo.append_event(evento)
                        self.proy_repo.upsert(idCampania, estado="APROBADA")
                        self.publish_event("CampaniaAprobada", evento)
                        logging.info(f"Campania aprobada: {idCampania}")
                    elif tipo == "PagoRevertido":
                        evento = CampaniaCancelada(idCampania, motivo=data.get("motivo"), fechaCancelacion=datetime.utcnow())
                        self.event_repo.append_event(evento)
                        self.proy_repo.upsert(idCampania, estado="CANCELADA")
                        self.publish_event("CampaniaCancelada", evento)
                        logging.info(f"Campania cancelada: {idCampania}")
                    consumer.acknowledge(msg)
                except Exception as e:
                    logging.error(f"Error procesando evento de pagos: {e}")
                    consumer.negative_acknowledge(msg)
        thread = threading.Thread(target=_consume, daemon=True)
        thread.start()

    def close(self):
        self.pulsar_client.close()


def crear_campania_cmd(data):
    idCampania = data.get('idCampania')
    idCliente = data.get('idCliente')
    itinerario = data.get('itinerario')
    if not idCampania or not idCliente or not isinstance(itinerario, list):
        raise ValueError('idCampania, idCliente y itinerario[] son requeridos')
    event_data = {
        'schemaVersion': '1.0',
        'idCampania': idCampania,
        'idCliente': idCliente,
        'itinerario': itinerario
    }
    append_event(idCampania, 'CampaniaCreada.v1', event_data)
    # Persist event first and update projection. Publishing to Pulsar is best-effort;
    # if Pulsar is temporarily unavailable we should still return success to the API
    # because the local state and event store are already updated.
    try:
        publish_event('CampaniaCreada.v1', event_data)
    except Exception as e:
        # Log and continue; the system's consumers can recover the missing integration
        # publication later or the publisher will retry when available.
        import logging
        logging.warning(f"publish_event failed (continuing): {e}")
    repo = CampaniaViewRepo(db.session)
    repo.upsert(idCampania, idCliente, EstadoCampania.PENDIENTE.value)
    return {'status': 'accepted', 'idCampania': idCampania}


def obtener_campania_qry(id_campania):
    repo = CampaniaViewRepo(db.session)
    return repo.get(id_campania)
