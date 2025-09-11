from sqlalchemy import Column, String, DateTime, Integer, JSON, func, UniqueConstraint
from alpespartners.config.db import db
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from alpespartners.modulos.campanias.infraestructura.mapeos import CampaniasView

# SQLAlchemy Base is db.Model (from config/db.py)

class EventStoreModel(db.Model):
    __tablename__ = "event_store"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    aggregate_id = db.Column(db.String, nullable=False, index=True)
    aggregate_type = db.Column(db.String, nullable=False, default='Campania')
    type = db.Column(db.String, nullable=False)
    payload = db.Column(db.Text, nullable=False)  # JSON as text
    occurred_on = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

# class CampaniasViewModel(db.Model):
#     __tablename__ = "campanias_view"
#     id = db.Column(db.String, primary_key=True)
#     id_cliente = db.Column(db.String, nullable=False)
#     estado = db.Column(db.String, nullable=False)
#     __table_args__ = (
#         db.Index("ix_campanias_view_id", "id"),
#     )

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

class CampaniaViewRepo:
    def __init__(self, session=None):
        self._session = session or db.session

    def upsert(self, id_campania, id_cliente, estado):
        obj = self._session.query(CampaniasView).filter_by(id=id_campania).one_or_none()
        if obj:
            obj.estado = estado
        else:
            obj = CampaniasView(id=id_campania, id_cliente=id_cliente, estado=estado)
            self._session.add(obj)
        self._session.commit()
        return obj

    def get(self, id_campania):
        obj = self._session.query(CampaniasView).filter_by(id=id_campania).one_or_none()
        if obj:
            return {'idCampania': obj.id, 'idCliente': obj.id_cliente, 'estado': obj.estado}
        return None
