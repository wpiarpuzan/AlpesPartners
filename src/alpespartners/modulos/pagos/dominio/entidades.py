from dataclasses import dataclass, field
from datetime import datetime
from .objetos_valor import Monto, MedioPago, nuevo_id, EstadoPago
from .eventos import PagoRegistrado

@dataclass
class Pago:
    reserva_id: str
    cliente_id: str
    monto: Monto
    medio: MedioPago
    id: str = field(default_factory=nuevo_id)
    estado: EstadoPago = EstadoPago.PENDIENTE
    fecha_creacion: datetime = field(default_factory=datetime.utcnow)
    fecha_actualizacion: datetime = field(default_factory=datetime.utcnow)

    # dominio expone eventos recién ocurridos
    eventos: list = field(default_factory=list, repr=False)

    @classmethod
    def registrar(cls, reserva_id: str, cliente_id: str, monto: Monto, medio: MedioPago) -> "Pago":
        pago = cls(reserva_id=reserva_id, monto=monto, medio=medio, estado= EstadoPago.CONFIRMADO)
        pago.eventos.append(PagoRegistrado(
            pago_id=pago.id,
            reserva_id=reserva_id,
            cliente_id=cliente_id, 
            valor=float(monto.valor),
            moneda=monto.moneda,
        ))
        return pago
