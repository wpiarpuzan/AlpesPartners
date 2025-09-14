"""
CampaniasService: Orquesta la lógica de campanias (event sourcing, proyección, integración Pulsar).
"""
import logging
from alpespartners.modulos.campanias.dominio.entidades import Campania
from alpespartners.modulos.campanias.dominio.eventos import CampaniaCreada, CampaniaAprobada, CampaniaCancelada
from alpespartners.modulos.campanias.infraestructura.repos import CampaniaViewRepo
from alpespartners.modulos.campanias.aplicacion.dto import CrearCampaniaDTO
from alpespartners.config.db import db
from alpespartners.seedwork.infraestructura import utils
import pulsar
import json
import threading
from datetime import datetime
from alpespartners.modulos.campanias.dominio.entidades import EstadoCampania
from alpespartners.modulos.campanias.infraestructura.event_store import append_event
from alpespartners.modulos.campanias.infraestructura.publisher import publish_event

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
                    payload = json.loads(msg.data())
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
    publish_event('CampaniaCreada.v1', event_data)
    repo = CampaniaViewRepo(db.session)
    repo.upsert(idCampania, idCliente, EstadoCampania.PENDIENTE.value)
    return {'status': 'accepted', 'idCampania': idCampania}


def obtener_campania_qry(id_campania):
    repo = CampaniaViewRepo(db.session)
    return repo.get(id_campania)

# TODO: Inyectar ReservasService en handlers y API vía DI, siguiendo patrón de pagos.
# TODO: Unificar logging y manejo de errores con seedwork.