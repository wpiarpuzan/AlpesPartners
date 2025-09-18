from dataclasses import dataclass


@dataclass
class ClienteDTO:
    id: str
    nombre: str
    email: str
