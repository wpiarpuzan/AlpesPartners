from dataclasses import dataclass
from typing import Optional


@dataclass
class PayoutDTO:
    # Minimal identifiers
    id: Optional[str] = None
    partner_id: Optional[str] = None
    cycle_id: Optional[str] = None

    # Monetary fields
    monto_total: Optional[float] = None
    # Some modules expect a richer money representation; keep optional placeholders
    monto_total_valor: Optional[float] = None
    monto_total_moneda: Optional[str] = None

    # Optional metadata used by the pago processing flow
    confirmation_id: Optional[str] = None
    failure_reason: Optional[str] = None
    payment_method_type: Optional[str] = None
    payment_method_mask: Optional[str] = None
    processed_at: Optional[str] = None
    completed_at: Optional[str] = None
