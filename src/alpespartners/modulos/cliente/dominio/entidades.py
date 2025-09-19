"""Entidades del dominio de cliente

En este archivo usted encontrará las entidades del dominio de cliente

"""

from datetime import datetime
from alpespartners.seedwork.dominio.entidades import Entidad
from dataclasses import dataclass, field

from .objetos_valor import Nombre, Email, Cedula, Rut
import uuid

@dataclass
class Usuario(Entidad):
    id: uuid.UUID
    nombre: Nombre = field(default_factory=Nombre)
    email: Email = field(default_factory=Email)

@dataclass
class ClienteNatural(Usuario):
    cedula: Cedula = field(default_factory=Cedula)
    fecha_nacimiento: datetime = field(default_factory=datetime.now)
    fecha_registro: datetime = field(default_factory=datetime.now)
    total_pagos: int = 0
    ultimo_pago: datetime = None

@dataclass
class ClienteEmpresa(Usuario):
    rut: Rut = field(default_factory=Rut)
    fecha_constitucion: datetime = field(default_factory=datetime)

"""Deprecated: Migrado a `src/cliente`.

Este archivo se deja como marcador temporal.
"""

raise RuntimeError("Este módulo fue migrado a `cliente` y no debe usarse.")
