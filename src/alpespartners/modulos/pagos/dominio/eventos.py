"""Deprecated: Migrado a `src/pagos`.

Este archivo se deja como marcador temporal y no debe usarse.
"""

raise RuntimeError("Este módulo fue migrado a `pagos` y no debe usarse.")

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime

@dataclass
class EventoDominio:
    timestamp: datetime

@dataclass
class PayoutCreado(EventoDominio):
    payout_id: str
    partner_id: str
    cycle_id: str
    fecha_creacion: datetime

@dataclass
class ComisionesCalculadas(EventoDominio):
    payout_id: str
    monto_total: float
    moneda: str
    transaction_count: int

@dataclass
class PayoutProcesado(EventoDominio):
    payout_id: str

@dataclass
class PayoutExitoso(EventoDominio):
    payout_id: str
    confirmation_id: str

@dataclass
class PayoutFallido(EventoDominio):
    payout_id: str
    reason: str
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime

@dataclass
class EventoDominio:
    timestamp: datetime

@dataclass
class PayoutCreado(EventoDominio):
    payout_id: str
    partner_id: str
    cycle_id: str
    fecha_creacion: datetime

@dataclass
class ComisionesCalculadas(EventoDominio):
    payout_id: str
    monto_total: float
    moneda: str
    transaction_count: int

@dataclass
class PayoutProcesado(EventoDominio):
    payout_id: str

@dataclass
class PayoutExitoso(EventoDominio):
    payout_id: str
    confirmation_id: str

@dataclass
class PayoutFallido(EventoDominio):
    payout_id: str
    reason: str