from sqlalchemy import Column, String, DateTime, Integer, JSON, func, UniqueConstraint
from alpespartners.config.db import db
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime

# SQLAlchemy Base is db.Model (from config/db.py)

class EventStoreModel(db.Model):
    __tablename__ = "event_store"
    id = Column(Integer, primary_key=True, autoincrement=True)
    aggregate_id = Column(String, nullable=False, index=True)
    event_type = Column(String, nullable=False)
    schema_version = Column(String, nullable=False)
    payload = Column(JSONB, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

class ReservasViewModel(db.Model):
    __tablename__ = "reservas_view"
    id_reserva = Column(String, primary_key=True)
    estado = Column(String, nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), server_onupdate=func.now(), nullable=False)
    __table_args__ = (UniqueConstraint('id_reserva', name='uq_reserva_id'),)

class EventStoreRepo:
    def __init__(self, session=None):
        self._session = session or db.session

    def append(self, aggregate_id, event_type, schema_version, payload: dict):
        event = EventStoreModel(
            aggregate_id=aggregate_id,
            event_type=event_type,
            schema_version=schema_version,
            payload=payload
        )
        self._session.add(event)
        self._session.commit()
        return event.id

class ReservaViewRepo:
    def __init__(self, session=None):
        self._session = session or db.session

    def upsert(self, id_reserva, estado):
        obj = self._session.query(ReservasViewModel).filter_by(id_reserva=id_reserva).one_or_none()
        if obj:
            obj.estado = estado
            obj.updated_at = datetime.utcnow()
        else:
            obj = ReservasViewModel(id_reserva=id_reserva, estado=estado)
            self._session.add(obj)
        self._session.commit()
        return obj

    def get(self, id_reserva):
        obj = self._session.query(ReservasViewModel).filter_by(id_reserva=id_reserva).one_or_none()
        if obj:
            return {"idReserva": obj.id_reserva, "estado": obj.estado, "updatedAt": obj.updated_at}
        return None
