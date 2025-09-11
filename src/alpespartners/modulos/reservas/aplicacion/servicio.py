"""
ReservasService: Orquesta la lógica de reservas (event sourcing, proyección, integración Pulsar).
"""
import logging
from alpespartners.modulos.reservas.dominio.entidades import Reserva
from alpespartners.modulos.reservas.dominio.eventos import ReservaCreada, ReservaAprobada, ReservaCancelada
from alpespartners.modulos.reservas.infraestructura.repos import ReservaEventStoreRepo, ReservaProyeccionRepo, ReservasViewRepo
from alpespartners.modulos.reservas.infraestructura.mapeos import ReservaProyeccion
from alpespartners.modulos.reservas.aplicacion.dto import CrearReservaDTO
from alpespartners.config.db import SessionLocal, db
from alpespartners.seedwork.infraestructura import utils
import pulsar
import json
import threading
from datetime import datetime
from alpespartners.modulos.reservas.dominio.entidades import EstadoReserva

# Pulsar topics (should come from config)
TOPIC_COMANDOS_RESERVAS = 'persistent://public/default/comandos.reservas'
TOPIC_EVENTOS_RESERVAS = 'persistent://public/default/eventos.reservas'
TOPIC_EVENTOS_PAGOS = 'persistent://public/default/eventos.pagos'

class ReservasService:
    def __init__(self, db_session=None):
        self.db_session = db_session or SessionLocal()
        self.event_repo = ReservaEventStoreRepo(self.db_session)
        self.proy_repo = ReservaProyeccionRepo(self.db_session)
        self.pulsar_client = pulsar.Client(f'pulsar://{utils.broker_host()}:6650')
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
    repo = ReservasViewRepo(db.session)
    repo.upsert(idReserva, idCliente, EstadoReserva.PENDIENTE.value)
    return {'status': 'accepted', 'idReserva': idReserva}

def obtener_reserva_qry(id_reserva):
    repo = ReservasViewRepo(db.session)
    return repo.get(id_reserva)

# TODO: Inyectar ReservasService en handlers y API vía DI, siguiendo patrón de pagos.
# TODO: Unificar logging y manejo de errores con seedwork.
