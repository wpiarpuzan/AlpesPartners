"""
ReservasService: Orquesta la lógica de reservas (event sourcing, proyección, integración Pulsar).
"""
import logging
from alpespartners.modulos.reservas.dominio.entidades import Reserva
from alpespartners.modulos.reservas.dominio.eventos import ReservaCreada, ReservaAprobada, ReservaCancelada
from alpespartners.modulos.reservas.infraestructura.repos import ReservaViewRepo
from alpespartners.modulos.reservas.aplicacion.dto import CrearReservaDTO
from alpespartners.config.db import db
from alpespartners.seedwork.infraestructura import utils
import pulsar
import json
import threading
from datetime import datetime
from alpespartners.modulos.reservas.dominio.entidades import EstadoReserva
from alpespartners.modulos.reservas.infraestructura.event_store import append_event
from alpespartners.modulos.reservas.infraestructura.publisher import publish_event

# Pulsar topics (should come from config)
TOPIC_COMANDOS_RESERVAS = 'persistent://public/default/comandos.reservas'
TOPIC_EVENTOS_RESERVAS = 'persistent://public/default/eventos.reservas'
TOPIC_EVENTOS_PAGOS = 'persistent://public/default/eventos.pagos'

class ReservasService:
    def __init__(self, db_session=None):
        import os
        self.db_session = db_session or db.session
        self.proy_repo = ReservaViewRepo(self.db_session)
        PULSAR_BROKER_URL = os.getenv('PULSAR_BROKER_URL', 'pulsar://broker:6650')
        self.pulsar_client = pulsar.Client(PULSAR_BROKER_URL)
        self.eventos_producer = self.pulsar_client.create_producer(TOPIC_EVENTOS_RESERVAS)

    def handle_crear_reserva(self, cmd: CrearReservaDTO):
        """Valida, persiste evento, actualiza proyección y publica evento integración."""
        # 1. Validación y creación de dominio
        reserva = Reserva.crear(cmd.idReserva, cmd.idCliente, cmd.itinerario)
        evento = ReservaCreada(cmd.idReserva, cmd.idCliente, cmd.itinerario, datetime.utcnow())
        # 2. Append event sourcing
        self.event_repo.append_event(evento)
        # 3. Upsert proyección
        self.proy_repo.upsert(cmd.idReserva, estado="CREADA")
        # 4. Publicar evento integración
        self.publish_event("ReservaCreada", evento)
        logging.info(f"Reserva creada: {cmd.idReserva}")

    def publish_event(self, tipo, evento):
        envelope = {"type": tipo, "data": evento.to_dict()}
        self.eventos_producer.send(json.dumps(envelope).encode("utf-8"))

    def subscribe_eventos_pagos(self):
        """Suscribe a eventos.pagos y reacciona a PagoConfirmado/PagoRevertido."""
        def _consume():
            consumer = self.pulsar_client.subscribe(
                TOPIC_EVENTOS_PAGOS,
                subscription_name="reservas-sub",
                consumer_type=pulsar.ConsumerType.Shared
            )
            while True:
                msg = consumer.receive()
                try:
                    payload = json.loads(msg.data())
                    tipo = payload.get("type")
                    data = payload.get("data")
                    idReserva = data.get("idReserva")
                    if tipo == "PagoConfirmado":
                        evento = ReservaAprobada(idReserva, datetime.utcnow(), origen="PAGOS")
                        self.event_repo.append_event(evento)
                        self.proy_repo.upsert(idReserva, estado="APROBADA")
                        self.publish_event("ReservaAprobada", evento)
                        logging.info(f"Reserva aprobada: {idReserva}")
                    elif tipo == "PagoRevertido":
                        evento = ReservaCancelada(idReserva, motivo=data.get("motivo"), fechaCancelacion=datetime.utcnow())
                        self.event_repo.append_event(evento)
                        self.proy_repo.upsert(idReserva, estado="CANCELADA")
                        self.publish_event("ReservaCancelada", evento)
                        logging.info(f"Reserva cancelada: {idReserva}")
                    consumer.acknowledge(msg)
                except Exception as e:
                    logging.error(f"Error procesando evento de pagos: {e}")
                    consumer.negative_acknowledge(msg)
        thread = threading.Thread(target=_consume, daemon=True)
        thread.start()

    def close(self):
        self.pulsar_client.close()

def crear_reserva_cmd(data):
    idReserva = data.get('idReserva')
    idCliente = data.get('idCliente')
    itinerario = data.get('itinerario')
    if not idReserva or not idCliente or not isinstance(itinerario, list):
        raise ValueError('idReserva, idCliente y itinerario[] son requeridos')
    event_data = {
        'schemaVersion': '1.0',
        'idReserva': idReserva,
        'idCliente': idCliente,
        'itinerario': itinerario
    }
    append_event(idReserva, 'ReservaCreada.v1', event_data)
    publish_event('ReservaCreada.v1', event_data)
    repo = ReservaViewRepo(db.session)
    repo.upsert(idReserva, idCliente, EstadoReserva.PENDIENTE.value)
    return {'status': 'accepted', 'idReserva': idReserva}

def obtener_reserva_qry(id_reserva):
    repo = ReservaViewRepo(db.session)
    return repo.get(id_reserva)

# TODO: Inyectar ReservasService en handlers y API vía DI, siguiendo patrón de pagos.
# TODO: Unificar logging y manejo de errores con seedwork.
