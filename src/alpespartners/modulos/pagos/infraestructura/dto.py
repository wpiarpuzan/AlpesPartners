"""DTOs para la capa de infrastructura del dominio de pagos

En este archivo usted encontrará los DTOs (modelos anémicos) de
la infraestructura del dominio de pagos

"""

from alpespartners.config.db import db
from datetime import datetime
from alpespartners.modulos.pagos.dominio.objetos_valor import EstadoPago, TipoMedioPago

class PagoModel(db.Model):
    __tablename__ = "pagos"
    id            = db.Column(db.String, primary_key=True)
    reserva_id    = db.Column(db.String, nullable=False)
    cliente_id    = db.Column(db.String, nullable=False)
    valor         = db.Column(db.Numeric(10,2), nullable=False)
    moneda        = db.Column(db.String(3), nullable=False)

    # Enum portable (se guarda como texto, funciona en SQLite/Postgres)
    medio_tipo = db.Column(
        db.Enum(TipoMedioPago, name="tipo_medio_pago", native_enum=False),
        nullable=False,
    )
    medio_mask = db.Column(db.String(32), nullable=False)

    estado = db.Column(
        db.Enum(EstadoPago, name="estado_pago", native_enum=False),
        nullable=False,
        default=EstadoPago.PENDIENTE,
    )

    fecha_creacion      = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

