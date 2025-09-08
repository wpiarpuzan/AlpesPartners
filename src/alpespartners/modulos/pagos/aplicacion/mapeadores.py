from alpespartners.modulos.pagos.aplicacion.dto import PagoDTO
from alpespartners.seedwork.aplicacion.dto import Mapeador as AppMap

class MapeadorPagoDTOJson(AppMap):
    """Convierte payloads JSON externos <-> PagoDTO de aplicación."""

    def externo_a_dto(self, externo: dict) -> PagoDTO:
        # Acepta dos formatos: con "monto": {"valor","moneda"} o plano "monto_valor","monto_moneda"
        monto = externo.get("monto") or {}
        monto_valor  = externo.get("monto_valor", monto.get("valor"))
        monto_moneda = externo.get("monto_moneda", monto.get("moneda"))

        return PagoDTO(
            id=externo.get("id"),
            reserva_id=externo.get("reserva_id"),
            monto_valor=float(monto_valor) if monto_valor is not None else None,
            monto_moneda=monto_moneda,
            medio=str(externo.get("medio") or externo.get("medio_pago") or ""),
            estado=externo.get("estado"),
        )

    def dto_a_externo(self, dto: PagoDTO) -> dict:
        return {
            "id": dto.id,
            "reserva_id": dto.reserva_id,
            "monto": {
                "valor": float(dto.monto_valor) if dto.monto_valor is not None else None,
                "moneda": dto.monto_moneda,
            },
            "medio": str(dto.medio) if dto.medio is not None else None,
            "estado": dto.estado,
            "fecha_creacion": dto.fecha_creacion.isoformat() if getattr(dto, "fecha_creacion", None) else None,
            "fecha_actualizacion": dto.fecha_actualizacion.isoformat() if getattr(dto, "fecha_actualizacion", None) else None,
        }