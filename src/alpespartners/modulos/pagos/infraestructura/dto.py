from alpespartners.config.db import db
from sqlalchemy.orm import composite
from datetime import datetime
from alpespartners.modulos.pagos.dominio.objetos_valor import EstadoPago, TipoMedioPago, Monto, MedioPago
import uuid

class PayoutCycleModel(db.Model):
    __tablename__ = "payout_cycles"
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(50), nullable=False, default="IN_PROGRESS")
    
class PayoutModel(db.Model):
    __tablename__ = "payouts"
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    partner_id = db.Column(db.String, nullable=False, index=True) 
    cycle_id = db.Column(db.String, db.ForeignKey('payout_cycles.id'), nullable=False)
    
    _total_amount = db.Column("total_amount", db.Numeric(10, 2), nullable=False)
    _currency = db.Column("currency", db.String(3), nullable=False)
    _payment_method_type = db.Column("payment_method_type", db.Enum(TipoMedioPago, name="tipo_medio_pago", native_enum=False), nullable=False)
    _payment_method_mask = db.Column("payment_method_mask", db.String(32), nullable=False)

    monto = composite(Monto, _total_amount, _currency)
    medio_pago = composite(MedioPago, _payment_method_type, _payment_method_mask)

    status = db.Column(db.Enum(EstadoPago, name="estado_pago", native_enum=False), nullable=False, default=EstadoPago.PENDIENTE)
    confirmation_id = db.Column(db.String, nullable=True)
    failure_reason = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    processed_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)

class TransactionModel(db.Model):
    __tablename__ = "transactions"
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    partner_id = db.Column(db.String, nullable=False, index=True)
    brand_id = db.Column(db.String, nullable=False, index=True)
    payout_id = db.Column(db.String, db.ForeignKey('payouts.id'), nullable=True, index=True)
    
    _commission_value = db.Column("commission_value", db.Numeric(10, 2), nullable=False)
    _currency = db.Column("currency", db.String(3), nullable=False)
    
    comision = composite(Monto, _commission_value, _currency)
    
    event_type = db.Column(db.String(50), nullable=False)
    event_timestamp = db.Column(db.DateTime, nullable=False)