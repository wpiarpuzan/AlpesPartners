# Definición de eventos para la SAGA
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any

@dataclass
class CampaniaCreada:
    idCampania: str
    idCliente: str
    itinerario: list
    monto: float
    fechaCreacion: datetime

@dataclass
class ProcesarPago:
    idCampania: str
    idCliente: str
    monto: float

@dataclass
class PagoExitoso:
    idCampania: str
    idCliente: str
    monto: float
    confirmation_id: str
    fecha: datetime

@dataclass
class PagoFallido:
    idCampania: str
    idCliente: str
    monto: float
    reason: str
    fecha: datetime

@dataclass
class CampaniaAprobada:
    idCampania: str
    idCliente: str
    fechaAprobacion: datetime

@dataclass
class CampaniaCancelada:
    idCampania: str
    idCliente: str
    motivo: str
    fechaCancelacion: datetime

@dataclass
class ActualizarCliente:
    idCliente: str
    accion: str
    detalles: Dict[str, Any]
