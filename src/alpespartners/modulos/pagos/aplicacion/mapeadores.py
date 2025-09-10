from alpespartners.modulos.pagos.aplicacion.dto import PayoutDTO
from alpespartners.seedwork.aplicacion.dto import Mapeador as AppMap
from alpespartners.modulos.pagos.infraestructura.dto import PayoutModel

class MapeadorPayoutDTOJson(AppMap):
    def externo_a_dto(self, externo: dict) -> PayoutDTO:
        return PayoutDTO(partner_id=externo.get("partner_id"), cycle_id=externo.get("cycle_id"))

    def dto_a_externo(self, dto: PayoutDTO) -> dict:
        monto_json = None
        if dto.monto_total_valor is not None and dto.monto_total_moneda is not None:
            monto_json = {"valor": float(dto.monto_total_valor), "moneda": dto.monto_total_moneda}
        return {
            "id": dto.id, "partner_id": dto.partner_id, "cycle_id": dto.cycle_id,
            "estado": dto.estado, "monto_total": monto_json,
            "fecha_creacion": dto.fecha_creacion.isoformat(),
            "fecha_actualizacion": dto.fecha_actualizacion.isoformat()
        }
    
    def dto_a_dto(self, dto_infra: PayoutModel) -> PayoutDTO:
        if dto_infra is None:
            return None

        return PayoutDTO(
            id=str(dto_infra.id),
            partner_id=str(dto_infra.partner_id),
            cycle_id=str(dto_infra.cycle_id),
            estado=dto_infra.status.value,
            monto_total_valor=dto_infra.monto.valor,
            monto_total_moneda=dto_infra.monto.moneda,
            fecha_creacion=dto_infra.created_at,
            fecha_actualizacion=dto_infra.updated_at
        )

class MapeadorPayout(MapeadorPayoutDTOJson):
    pass