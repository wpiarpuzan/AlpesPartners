from dataclasses import dataclass
from alpespartners.modulos.cliente.dominio.repositorios import IClienteRepositorio
from alpespartners.seedwork.aplicacion.queries import Query, QueryHandler, QueryResultado

@dataclass
class ObtenerClientePorId(Query):
    cliente_id: str

class ObtenerClientePorIdHandler(QueryHandler):
    def __init__(self, repo: IClienteRepositorio):
        self.repo = repo

    def handle(self, q: ObtenerClientePorId) -> QueryResultado:
        cliente = self.repo.obtener_por_id(q.cliente_id)
        if not cliente:
            return QueryResultado(resultado=None)

        data = {
            "id": cliente.id,
            "nombre": cliente.nombre,
            "email": (
                cliente.email.valor
                if hasattr(cliente, "email") and hasattr(cliente.email, "valor")
                else getattr(cliente, "email", None)
            ),
            "fecha_registro": (
                cliente.fecha_registro.isoformat()
                if getattr(cliente, "fecha_registro", None)
                else None
            ),
            # proyección mantenida por eventos de PagoRegistrado (vía Pulsar)
            "total_pagos": getattr(cliente, "total_pagos", 0),
            "ultimo_pago": (
                cliente.ultimo_pago.isoformat()
                if getattr(cliente, "ultimo_pago", None)
                else None
            ),
        }
        return QueryResultado(resultado=data)
