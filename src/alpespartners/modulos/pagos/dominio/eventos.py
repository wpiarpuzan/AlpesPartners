from dataclasses import dataclass

@dataclass
class PagoRegistrado:
    pago_id: str
    reserva_id: str
    cliente_id: str
    valor: float
    moneda: str

@dataclass
class PagoConfirmado:
    pago_id: str
    reserva_id: str
