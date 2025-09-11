from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

@dataclass
class ReservaCreada:
    idReserva: str
    idCliente: str
    itinerario: List[str]
    fechaCreacion: datetime
    estado: str = "CREADA"
    schemaVersion: str = "v1"

@dataclass
class ReservaAprobada:
    idReserva: str
    fechaAprobacion: datetime
    origen: str = "PAGOS"
    schemaVersion: str = "v1"

@dataclass
class ReservaCancelada:
    idReserva: str
    motivo: Optional[str]
    fechaCancelacion: datetime
    schemaVersion: str = "v1"
