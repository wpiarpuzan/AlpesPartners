from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from enum import Enum


@dataclass
class Campania:
    idCampania: str
    idCliente: str
    itinerario: List[str]
    estado: str = "CREADA"
    fechaCreacion: datetime = field(default_factory=datetime.utcnow)

    @staticmethod
    def crear(idCampania: str, idCliente: str, itinerario: List[str]):
        return Campania(idCampania=idCampania, idCliente=idCliente, itinerario=itinerario)


@dataclass
class CampaniaCreada:
    idCampania: str
    idCliente: str
    itinerario: List[str]
    fechaCreacion: datetime
    estado: str = "CREADA"
    schemaVersion: str = "v1"

    def to_dict(self):
        return {
            "schemaVersion": self.schemaVersion,
            "idCampania": self.idCampania,
            "idCliente": self.idCliente,
            "itinerario": self.itinerario,
            "fechaCreacion": int(self.fechaCreacion.timestamp() * 1000),
            "estado": self.estado
        }


@dataclass
class CampaniaAprobada:
    idCampania: str
    fechaAprobacion: datetime
    origen: str = "PAGOS"
    schemaVersion: str = "v1"

    def to_dict(self):
        return {
            "schemaVersion": self.schemaVersion,
            "idCampania": self.idCampania,
            "fechaAprobacion": int(self.fechaAprobacion.timestamp() * 1000),
            "origen": self.origen
        }


@dataclass
class CampaniaCancelada:
    idCampania: str
    motivo: Optional[str]
    fechaCancelacion: datetime
    schemaVersion: str = "v1"

    def to_dict(self):
        return {
            "schemaVersion": self.schemaVersion,
            "idCampania": self.idCampania,
            "motivo": self.motivo,
            "fechaCancelacion": int(self.fechaCancelacion.timestamp() * 1000)
        }

class EstadoCampania(str, Enum):
    PENDIENTE = 'PENDIENTE'
    APROBADA = 'APROBADA'
    CANCELADA = 'CANCELADA'
