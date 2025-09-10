from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
import uuid

from .objetos_valor import Monto, EstadoPago
from .eventos import PayoutCreado, ComisionesCalculadas, PayoutProcesado, PayoutExitoso, PayoutFallido

@dataclass
class Transaction:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    partner_id: str = field(default_factory=str)
    brand_id: str = field(default_factory=str)
    comision: Monto = field(default_factory=Monto)
    event_type: str = field(default_factory=str)
    event_timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Payout:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    partner_id: str = field(default_factory=str)
    cycle_id: str = field(default_factory=str)
    monto_total: Monto = field(default_factory=Monto)
    transaction_ids: list[str] = field(default_factory=list)
    estado: EstadoPago = field(default=EstadoPago.PENDIENTE)
    fecha_creacion: datetime = field(default_factory=datetime.utcnow)
    eventos: list = field(default_factory=list, repr=False)

    def crear(self, partner_id: str, cycle_id: str):
        self.partner_id = partner_id
        self.cycle_id = cycle_id
        self.estado = EstadoPago.PENDIENTE
        self.eventos.append(PayoutCreado(
            payout_id=self.id,
            partner_id=self.partner_id,
            cycle_id=self.cycle_id,
            fecha_creacion=self.fecha_creacion
        ))

    def calcular_comisiones(self, transactions: list[Transaction]):
        if self.estado != EstadoPago.PENDIENTE:
            print("Error: Solo se pueden calcular comisiones para Payouts pendientes.")
            return

        total = Decimal(0)
        moneda = transactions[0].comision.moneda if transactions else "USD"
        
        self.transaction_ids = []
        for tx in transactions:
            total += tx.comision.valor
            self.transaction_ids.append(tx.id)
            
        self.monto_total = Monto(valor=total, moneda=moneda)
        self.estado = EstadoPago.CALCULADO
        
        self.eventos.append(ComisionesCalculadas(
            payout_id=self.id,
            monto_total=float(self.monto_total.valor),
            moneda=self.monto_total.moneda,
            transaction_count=len(self.transaction_ids)
        ))
    
    def procesar_pago(self):
        if self.estado != EstadoPago.CALCULADO:
            print("Error: Solo se pueden procesar Payouts calculados.")
            return
            
        self.estado = EstadoPago.EN_PROCESO
        self.eventos.append(PayoutProcesado(payout_id=self.id))

    def marcar_como_exitoso(self, confirmation_id: str):
        self.estado = EstadoPago.EXITOSO
        self.eventos.append(PayoutExitoso(payout_id=self.id, confirmation_id=confirmation_id))

    def marcar_como_fallido(self, reason: str):
        self.estado = EstadoPago.FALLIDO
        self.eventos.append(PayoutFallido(payout_id=self.id, reason=reason))
