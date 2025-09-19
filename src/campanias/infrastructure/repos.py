from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy import text
from alpespartners.config.db import db
from datetime import datetime


class EventStoreModel(db.Model):
    __tablename__ = 'event_store'
    id = Column(Integer, primary_key=True)
    aggregate_id = Column(String(255), index=True)
    aggregate_type = Column(String(255))
    type = Column(String(255))
    payload = Column(Text)
    occurred_on = Column(DateTime, default=datetime.utcnow)


class CampaniaViewRepo:
    def __init__(self, session):
        self.session = session

    def upsert(self, id_campania, id_cliente=None, estado=None):
        q = text(
            "INSERT INTO campanias_view (id, id_cliente, estado, updated_at) VALUES (:idc, :idcli, :est, now()) "
            "ON CONFLICT (id) DO UPDATE SET id_cliente = EXCLUDED.id_cliente, estado = EXCLUDED.estado, updated_at = now()"
        )
        self.session.execute(q, {"idc": id_campania, "idcli": id_cliente, "est": estado})
        self.session.commit()

    def get(self, id_campania):
        r = self.session.execute(text("SELECT id, id_cliente, estado FROM campanias_view WHERE id = :id"), {"id": id_campania}).fetchone()
        if not r:
            return None
        return {"id": r[0], "idCliente": r[1], "estado": r[2]}
