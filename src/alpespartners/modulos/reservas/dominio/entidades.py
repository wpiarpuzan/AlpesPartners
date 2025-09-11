from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

@dataclass
class Reserva:
    idReserva: str
    idCliente: str
    itinerario: List[str]
    estado: str = "CREADA"
    fechaCreacion: datetime = field(default_factory=datetime.utcnow)

    @staticmethod
    def crear(idReserva: str, idCliente: str, itinerario: List[str]):
        return Reserva(idReserva=idReserva, idCliente=idCliente, itinerario=itinerario)

@dataclass
class ReservaCreada:
    idReserva: str
    idCliente: str
    itinerario: List[str]
    fechaCreacion: datetime
    estado: str = "CREADA"
    schemaVersion: str = "v1"

    def to_dict(self):
        return {
            "schemaVersion": self.schemaVersion,
            "idReserva": self.idReserva,
            "idCliente": self.idCliente,
            "itinerario": self.itinerario,
            "fechaCreacion": int(self.fechaCreacion.timestamp() * 1000),
            "estado": self.estado
        }

@dataclass
class ReservaAprobada:
    idReserva: str
    fechaAprobacion: datetime
    origen: str = "PAGOS"
    schemaVersion: str = "v1"

    def to_dict(self):
        return {
            "schemaVersion": self.schemaVersion,
            "idReserva": self.idReserva,
            "fechaAprobacion": int(self.fechaAprobacion.timestamp() * 1000),
            "origen": self.origen
        }

@dataclass
class ReservaCancelada:
    idReserva: str
    motivo: Optional[str]
    fechaCancelacion: datetime
    schemaVersion: str = "v1"

    def to_dict(self):
        return {
            "schemaVersion": self.schemaVersion,
            "idReserva": self.idReserva,
            "motivo": self.motivo,
            "fechaCancelacion": int(self.fechaCancelacion.timestamp() * 1000)
        }
