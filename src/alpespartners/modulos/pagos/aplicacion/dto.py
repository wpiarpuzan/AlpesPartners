# alpespartners/modulos/pagos/aplicacion/dto.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class PagoDTO:
    # Identificadores
    id: Optional[str] = None
    reserva_id: str = ""

    # Monto (plano para el DTO; el mapeador lo convertirá al VO Monto)
    monto_valor: float = 0.0
    monto_moneda: str = "USD"

    # Enums en dominio; en DTO viajan como string (nombre del Enum)
    medio: str = ""          # p.ej. "TARJETA", "PSE", "EFECTIVO"
    estado: Optional[str] = None  # p.ej. "PENDIENTE", "CONFIRMADO", "RECHAZADO"

    # Timestamps (opcionales; si no vienen, los setea dominio/infra)
    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None
