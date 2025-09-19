from dataclasses import dataclass
from typing import List


@dataclass
class CrearCampaniaDTO:
    idCampania: str
    idCliente: str
    itinerario: List[str]
