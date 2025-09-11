from sqlalchemy import func
"""DTOs para la capa de infrastructura del dominio de clientes

En este archivo usted encontrará los DTOs (modelos anémicos) de
la infraestructura del dominio del cliente

"""

# ... imports existentes
from alpespartners.config.db import db
from datetime import datetime

class ClienteModel(db.Model):
    __tablename__ = "clientes"

    # === ya existentes ===
    id             = db.Column(db.String, primary_key=True)
    nombre         = db.Column(db.String(120), nullable=False)
    email          = db.Column(db.String(120), nullable=False, unique=True)
    cedula         = db.Column(db.String(120), nullable=False, unique=True)    
    fecha_registro = db.Column(db.DateTime, server_default=func.now(), nullable=False)

    # === NUEVO: proyección alimentada por eventos de pago ===
    total_pagos = db.Column(db.Integer, nullable=False, default=0)
    ultimo_pago = db.Column(db.DateTime, nullable=True)

    __table_args__ = (
        db.Index("ix_clientes_email", "email"),
    )