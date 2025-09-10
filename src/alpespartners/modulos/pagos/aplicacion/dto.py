from dataclasses import dataclass, field
from alpespartners.seedwork.aplicacion.dto import DTO
from datetime import datetime
from decimal import Decimal

@dataclass(frozen=True)
class PayoutDTO(DTO):
    id: str = field(default_factory=str)
    partner_id: str = field(default_factory=str)
    cycle_id: str = field(default_factory=str)
    estado: str = field(default_factory=str)
    
    monto_total_valor: Decimal | None = field(default=None)
    monto_total_moneda: str | None = field(default=None)
    
    fecha_creacion: datetime = field(default_factory=datetime.now)
    fecha_actualizacion: datetime = field(default_factory=datetime.now)