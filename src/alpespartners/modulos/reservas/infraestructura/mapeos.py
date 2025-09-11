from sqlalchemy import func
from alpespartners.config.db import db
from datetime import datetime

class ReservaViewModel(db.Model):
    __tablename__ = "reservas_view"
    id_reserva = db.Column(db.String, primary_key=True)
    estado = db.Column(db.String(32), nullable=False)
    updated_at = db.Column(db.DateTime, server_default=func.now(), server_onupdate=func.now(), nullable=False)
    __table_args__ = (
        db.Index("ix_reservas_view_id_reserva", "id_reserva"),
    )
