from alpespartners.modulos.pagos.dominio.repositorios import IPagoRepositorio
from alpespartners.modulos.pagos.dominio.entidades import Pago
from alpespartners.config.db import db
from .dto import PagoModel
from .mapeadores import pago_a_modelo, modelo_a_pago

class PagoRepositorioSQLAlchemy(IPagoRepositorio):
    def __init__(self, session=None):
        self.session = session or db.session

    def agregar(self, pago: Pago) -> None:
        self.session.add(pago_a_modelo(pago))
        self.session.commit()

    def obtener_por_id(self, pago_id: str) -> Pago | None:
        m = self.session.get(PagoModel, pago_id)
        return modelo_a_pago(m) if m else None
