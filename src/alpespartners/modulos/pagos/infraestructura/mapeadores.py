from decimal import Decimal
from alpespartners.modulos.pagos.dominio.entidades import Pago
from alpespartners.modulos.pagos.dominio.objetos_valor import Monto, MedioPago, EstadoPago, TipoMedioPago
from .dto import PagoModel
from alpespartners.seedwork.dominio.repositorios import Mapeador

def pago_a_modelo(p: Pago) -> PagoModel:
    return PagoModel(
        id=p.id,
        reserva_id=p.reserva_id,
        cliente_id=p.cliente_id,
        valor=p.monto.valor,
        moneda=p.monto.moneda,
        medio_tipo=p.medio.tipo,   # Enum -> texto automático
        medio_mask=p.medio.mascara,
        estado=p.estado,           # Enum -> texto automático
        fecha_creacion=p.fecha_creacion,
        fecha_actualizacion=p.fecha_actualizacion,
    )

def modelo_a_pago(m: PagoModel) -> Pago:
    estado = m.estado if isinstance(m.estado, EstadoPago) else EstadoPago(m.estado)
    tipo   = m.medio_tipo if isinstance(m.medio_tipo, TipoMedioPago) else TipoMedioPago(m.medio_tipo)
    return Pago(
        id=m.id,
        reserva_id=m.reserva_id,
        cliente_id=m.cliente_id, 
        monto=Monto(Decimal(m.valor), m.moneda),
        medio=MedioPago(tipo, m.medio_mask),
        estado=estado,
        fecha_creacion=m.fecha_creacion,
        fecha_actualizacion=m.fecha_actualizacion,
    )

