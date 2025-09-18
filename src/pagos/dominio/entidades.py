from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
import uuid

from pagos.dominio.objetos_valor import Monto, EstadoPago
from pagos.dominio.eventos import PayoutCreado, ComisionesCalculadas, PayoutProcesado, PayoutExitoso, PayoutFallido

@dataclass
class Transaction:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    partner_id: str = field(default_factory=str)
    brand_id: str = field(default_factory=str)
    payout_id: str = field(default=None)
    comision: Monto = field(default_factory=Monto)
    event_type: str = field(default_factory=str)
    event_timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Payout:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    partner_id: str = field(default_factory=str)
    cycle_id: str = field(default_factory=str)
    monto_total: Monto = field(default_factory=lambda: Monto(valor=0, moneda="USD"))
    medio_pago: object = field(default_factory=lambda: None)
    transaction_ids: list[str] = field(default_factory=list)
    estado: EstadoPago = field(default=EstadoPago.PENDIENTE)
    fecha_creacion: datetime = field(default_factory=datetime.utcnow)
    eventos: list = field(default_factory=list, repr=False)

    @classmethod
    def crear(cls, partner_id: str, cycle_id: str, payment_method_type=None, payment_method_mask=None):
        from pagos.dominio.objetos_valor import MedioPago, TipoMedioPago
        medio_pago = None
        if payment_method_type and payment_method_mask:
            medio_pago = MedioPago(tipo=payment_method_type, mascara=payment_method_mask)
        payout = cls(partner_id=partner_id, cycle_id=cycle_id, estado=EstadoPago.PENDIENTE, medio_pago=medio_pago)
        payout.eventos.append(PayoutCreado(
            payout_id=payout.id,
            partner_id=payout.partner_id,
            cycle_id=payout.cycle_id,
            fecha_creacion=payout.fecha_creacion,
            timestamp=payout.fecha_creacion
        ))
        return payout

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
            transaction_count=len(self.transaction_ids),
            timestamp=datetime.utcnow()
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
