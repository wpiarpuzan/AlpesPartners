from alpespartners.seedwork.aplicacion.queries import Query, QueryHandler, QueryResultado
from alpespartners.seedwork.aplicacion.queries import ejecutar_query as query
from dataclasses import dataclass


@dataclass
class ObtenerPayout(Query):
    id: str


class ObtenerPayoutHandler(QueryHandler):
    def handle(self, query: ObtenerPayout) -> QueryResultado:
        # implementación mínima: delegar a repositorio simple
        from pagos.infraestructura.repositorios import PayoutRepositorioSQLAlchemy
        repo = PayoutRepositorioSQLAlchemy()
        pago = repo.obtener_por_id(query.id)
        return QueryResultado(resultado=pago)


@query.register(ObtenerPayout)
def ejecutar_query_obtener_payout(query: ObtenerPayout):
    handler = ObtenerPayoutHandler()
    return handler.handle(query)
