from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Cliente:
    idCliente: str
    nombre: str
    email: Optional[str]
    fecha_creacion: datetime
