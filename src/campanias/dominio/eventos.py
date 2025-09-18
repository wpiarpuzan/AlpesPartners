from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class CampaniaCreada:
    idCampania: str
    idCliente: str
    itinerario: List[str]
    fechaCreacion: datetime
    estado: str = "CREADA"
    schemaVersion: str = "v1"
    type: str = 'CampaniaCreada'
    data: dict = None


@dataclass
class CampaniaAprobada:
    idCampania: str
    fechaAprobacion: datetime
    origen: str = "PAGOS"
    schemaVersion: str = "v1"
    type: str = 'CampaniaAprobada'
    data: dict = None


@dataclass
class CampaniaCancelada:
    idCampania: str
    motivo: Optional[str]
    fechaCancelacion: datetime
    schemaVersion: str = "v1"
    type: str = 'CampaniaCancelada'
    data: dict = None
