from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from uuid import uuid4

def nuevo_id() -> str:
    return str(uuid4())

class EstadoPago(str, Enum):
    PENDIENTE  = "PENDIENTE"
    CALCULADO  = "CALCULADO"
    CONFIRMADO = "CONFIRMADO"
    RECHAZADO  = "RECHAZADO"
    
class TipoMedioPago(str, Enum):
    TARJETA        = "TARJETA"
    PSE            = "PSE"
    TRANSFERENCIA  = "TRANSFERENCIA"
    EFECTIVO       = "EFECTIVO"

class Monto:
    def __init__(self, valor: Decimal, moneda: str):
        self.valor = valor
        self.moneda = moneda
    
    def __composite_values__(self):
        return self.valor, self.moneda
    
    def __eq__(self, other):
        return isinstance(other, Monto) and \
                other.valor == self.valor and \
                other.moneda == self.moneda

class MedioPago:
    def __init__(self, tipo: TipoMedioPago, mascara: str):
        self.tipo = tipo
        self.mascara = mascara
        
    def __composite_values__(self):
        return self.tipo, self.mascara
        
    def __eq__(self, other):
        return isinstance(other, MedioPago) and \
                other.tipo == self.tipo and \
                other.mascara == self.mascara
    