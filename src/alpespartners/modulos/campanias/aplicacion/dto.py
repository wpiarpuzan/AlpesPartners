from dataclasses import dataclass
from typing import Any


@dataclass
class CrearCampaniaDTO:
    idCampania: str
    idCliente: str
    itinerario: Any  # Puedes ajustar el tipo según tu dominio
