from dataclasses import dataclass
from typing import Any

@dataclass
class CrearReservaDTO:
    idReserva: str
    idCliente: str
    itinerario: Any  # Puedes ajustar el tipo según tu dominio
