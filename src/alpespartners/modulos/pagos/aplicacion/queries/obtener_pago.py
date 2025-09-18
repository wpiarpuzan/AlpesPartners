from alpespartners.seedwork.aplicacion.queries import Query, QueryHandler, QueryResultado
from alpespartners.seedwork.aplicacion.queries import ejecutar_query as query
from alpespartners.modulos.pagos.dominio.repositorios import IPayoutRepositorio
from alpespartners.modulos.pagos.infraestructura.fabricas import FabricaRepositorio
from alpespartners.modulos.pagos.aplicacion.mapeadores import MapeadorPayoutDTOJson
from dataclasses import dataclass

class PagoQueryBaseHandler(QueryHandler):
    def __init__(self):
        self._fabrica_repositorio: FabricaRepositorio = FabricaRepositorio()

    @property
    def fabrica_repositorio(self) -> FabricaRepositorio:
        return self._fabrica_repositorio

@dataclass
class ObtenerPayout(Query):
    id: str
    """Deprecated: Migrado a `src/pagos`.

    Este archivo se deja como marcador temporal y no debe usarse.
    """

    raise RuntimeError("Este módulo fue migrado a `pagos` y no debe usarse.")

class ObtenerPayoutHandler(PagoQueryBaseHandler):
    def handle(self, query: ObtenerPayout) -> QueryResultado:
        repositorio = self.fabrica_repositorio.crear_objeto(IPayoutRepositorio)
        payout_dto_infra = repositorio.obtener_por_id(query.id, version_dto=True)
        
        mapeador = MapeadorPayoutDTOJson()
        payout_dto_app = mapeador.dto_a_dto(payout_dto_infra)
        
        return QueryResultado(resultado=payout_dto_app)

@query.register(ObtenerPayout)
def ejecutar_query_obtener_payout(query: ObtenerPayout):
    handler = ObtenerPayoutHandler()
    return handler.handle(query)
