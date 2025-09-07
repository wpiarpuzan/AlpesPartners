from dataclasses import dataclass
from alpespartners.modulos.pagos.dominio.repositorios import IPagoRepositorio

@dataclass
class ObtenerPagoPorId:
    pago_id: str

class ObtenerPagoPorIdHandler:
    def __init__(self, repo: IPagoRepositorio):
        self.repo = repo
    def handle(self, q: ObtenerPagoPorId):
        pago = self.repo.obtener_por_id(q.pago_id)
        if not pago: return None
        return {
            "id": pago.id,
            "reserva_id": pago.reserva_id,
            "cliente_id": pago.cliente_id, 
            "valor": float(pago.monto.valor),
            "moneda": pago.monto.moneda,
            "medio_tipo": pago.medio.tipo.value,  # <---
            "medio_mask": pago.medio.mascara,
            "estado": pago.estado.value,          # <---
            "fecha_creacion": pago.fecha_creacion.isoformat(),
        }
