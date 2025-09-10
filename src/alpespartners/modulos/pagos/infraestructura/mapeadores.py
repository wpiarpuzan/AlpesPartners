from alpespartners.seedwork.dominio.repositorios import Mapeador
from alpespartners.modulos.pagos.dominio.entidades import Payout, Transaction
from alpespartners.modulos.pagos.dominio.objetos_valor import Monto
from .dto import PayoutModel, TransactionModel

class MapeadorPayout(Mapeador):

    def obtener_tipo(self) -> type:
        return Payout.__class__

    def entidad_a_dto(self, entidad: Payout) -> PayoutModel:
        """Convierte una entidad de dominio Payout a un DTO de persistencia."""
        
        payout_dto = PayoutModel(
            id=entidad.id,
            partner_id=entidad.partner_id,
            cycle_id=entidad.cycle_id,
            status=entidad.estado,
            monto=entidad.monto_total,
            created_at=entidad.fecha_creacion
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
