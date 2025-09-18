from dataclasses import dataclass

@dataclass
class PayoutDTO:
    id: str
    partner_id: str
    cycle_id: str
    monto_total: float
