from dataclasses import dataclass
from cliente.dominio.repositorios import IClienteRepositorio
from alpespartners.seedwork.aplicacion.queries import Query, QueryHandler, QueryResultado
from alpespartners.seedwork.aplicacion.queries import ejecutar_query as query


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
            "id": getattr(cliente, 'id', None),
            "nombre": getattr(cliente, 'nombre', None),
            "email": getattr(cliente, 'email', None),
            "fecha_registro": getattr(cliente, 'fecha_registro', None),
            "total_pagos": getattr(cliente, 'total_pagos', 0),
            "ultimo_pago": getattr(cliente, 'ultimo_pago', None),
        }
        return QueryResultado(resultado=data)
    
@query.register(ObtenerClientePorId)
def ejecutar_Obtener_Cliente_Por_Id(query: ObtenerClientePorId):
    from cliente.infraestructura.repositorios import (
        ClienteRepositorioSQLAlchemy,
    )
    handler = ObtenerClientePorIdHandler(ClienteRepositorioSQLAlchemy())
    return handler.handle(query)
from cliente.dominio.repositorios import IClienteRepositorio
from cliente.infraestructura.repositorios import ClienteRepo

def ObtenerClientePorId(id_cliente):
    repo = ClienteRepo()
    return repo.get(id_cliente)
