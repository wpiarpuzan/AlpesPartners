from dataclasses import dataclass
from datetime import datetime

@dataclass
class PagoConfirmado:
    idPago: str
    idCampania: str
    idCliente: str
    monto: float
    fecha: datetime
    schemaVersion: str = 'v1'

@dataclass
class PagoRevertido:
    idPago: str
    idCampania: str
    idCliente: str
    motivo: str
    fecha: datetime
    schemaVersion: str = 'v1'
