"""Entidades del dominio de cliente"""

from datetime import datetime
from dataclasses import dataclass, field
import uuid

@dataclass
class Usuario:
    id: uuid.UUID
    nombre: str = field(default_factory=str)
    email: str = field(default_factory=str)


@dataclass
class ClienteNatural(Usuario):
    cedula: str = field(default_factory=str)
    fecha_nacimiento: datetime = field(default_factory=datetime.now)
    fecha_registro: datetime = field(default_factory=datetime.now)
    total_pagos: int = 0
    ultimo_pago: datetime = None


@dataclass
class ClienteEmpresa(Usuario):
    rut: str = field(default_factory=str)
    fecha_constitucion: datetime = field(default_factory=datetime)
