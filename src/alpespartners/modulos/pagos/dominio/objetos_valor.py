from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

class EstadoPago(str, Enum):
    PENDIENTE  = "PENDIENTE"
    CONFIRMADO = "CONFIRMADO"
    RECHAZADO  = "RECHAZADO"

class TipoMedioPago(str, Enum):
    TARJETA        = "TARJETA"
    PSE            = "PSE"
    TRANSFERENCIA  = "TRANSFERENCIA"
    EFECTIVO       = "EFECTIVO"

@dataclass(frozen=True)
class Monto:
    valor: Decimal
    moneda: str

@dataclass(frozen=True)
class MedioPago:
    tipo: TipoMedioPago
    mascara: str
