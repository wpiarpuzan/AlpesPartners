from alpespartners.seedwork.dominio.repositorios import Mapeador
from alpespartners.modulos.pagos.dominio.entidades import Payout, Transaction
from alpespartners.modulos.pagos.dominio.objetos_valor import Monto
from .dto import PayoutModel, TransactionModel

class MapeadorPayout(Mapeador):

    def obtener_tipo(self) -> type:
        return Payout.__class__

    def entidad_a_dto(self, entidad: Payout) -> PayoutModel:
        """Convierte una entidad de dominio Payout a un DTO de persistencia."""
        from alpespartners.modulos.pagos.dominio.objetos_valor import TipoMedioPago
        from datetime import datetime
        # medio_pago
        tipo_medio_pago = None
        mask_medio_pago = None
        if hasattr(entidad, 'medio_pago') and entidad.medio_pago:
            tipo_medio_pago = getattr(entidad.medio_pago, 'tipo', None)
            mask_medio_pago = getattr(entidad.medio_pago, 'mascara', None)
        if tipo_medio_pago and hasattr(tipo_medio_pago, 'value'):
            tipo_medio_pago = tipo_medio_pago.value
        else:
            tipo_medio_pago = tipo_medio_pago or TipoMedioPago.TRANSFERENCIA.value
        mask_medio_pago = mask_medio_pago or 'XXXXXXXXXXXX'
        # monto
        total_amount = float(entidad.monto_total.valor) if entidad.monto_total and hasattr(entidad.monto_total, 'valor') else 0.0
        # fechas
        updated_at = entidad.fecha_creacion if hasattr(entidad, 'fecha_creacion') and entidad.fecha_creacion else datetime.utcnow()
        payout_dto = PayoutModel(
            id=entidad.id,
            partner_id=entidad.partner_id,
            cycle_id=entidad.cycle_id,
            _total_amount=getattr(entidad, 'monto_total_valor', total_amount),
            _currency=getattr(entidad, 'monto_total_moneda', str(entidad.monto_total.moneda) if entidad.monto_total else 'USD'),
            _payment_method_type=getattr(entidad, 'payment_method_type', tipo_medio_pago),
            _payment_method_mask=getattr(entidad, 'payment_method_mask', mask_medio_pago),
            status=getattr(entidad, 'estado', entidad.estado.value if hasattr(entidad.estado, 'value') else entidad.estado),
            confirmation_id=getattr(entidad, 'confirmation_id', None),
            failure_reason=getattr(entidad, 'failure_reason', None),
            created_at=getattr(entidad, 'fecha_creacion', entidad.fecha_creacion),
            updated_at=getattr(entidad, 'fecha_actualizacion', updated_at),
            processed_at=getattr(entidad, 'processed_at', None),
            completed_at=getattr(entidad, 'completed_at', None)
        )
        return payout_dto

    def dto_a_entidad(self, dto: PayoutModel) -> Payout:
        """Convierte un DTO de persistencia a una entidad de dominio Payout."""
        
        payout = Payout(
            id=dto.id,
            partner_id=dto.partner_id,
            cycle_id=dto.cycle_id,
            estado=dto.status,
            fecha_creacion=dto.created_at,
            monto_total=dto.monto
        )
        payout.eventos = []
        
        return payout
    
class MapeadorTransaction(Mapeador):
    def obtener_tipo(self) -> type:
        return Transaction.__class__
    
    def entidad_a_dto(self, entidad: Transaction) -> TransactionModel:
        transaccion_dto = TransactionModel()

        transaccion_dto.id = str(entidad.id)
        transaccion_dto.partner_id = str(entidad.partner_id)
        transaccion_dto.brand_id = str(entidad.brand_id)
        transaccion_dto.payout_id = str(entidad.payout_id) if entidad.payout_id else None
        transaccion_dto.event_type = entidad.event_type
        transaccion_dto.event_timestamp = entidad.event_timestamp
        transaccion_dto.comision = entidad.comision
        
        return transaccion_dto

    def dto_a_entidad(self, dto: TransactionModel) -> Transaction:
        if dto is None:
            return None
        
        comision = Monto(valor=dto.comision.valor, moneda=dto.comision.moneda)

        return Transaction(
            id=dto.id,
            partner_id=dto.partner_id,
            brand_id=dto.brand_id,
            payout_id=dto.payout_id,
            comision=comision,
            event_type=dto.event_type,
            event_timestamp=dto.event_timestamp
        )
