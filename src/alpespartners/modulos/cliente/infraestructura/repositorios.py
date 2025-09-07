from datetime import datetime
from alpespartners.config.db import db
from alpespartners.modulos.cliente.dominio.repositorios import IClienteRepositorio
from .dto import ClienteModel
from typing import Optional
from alpespartners.modulos.cliente.dominio.entidades import ClienteNatural
from .mapeadores import modelo_a_cliente

class ClienteRepositorioSQLAlchemy(IClienteRepositorio):

    def actualizar_totales_por_pago(self, cliente_id: str, fecha_pago: datetime) -> None:
        m = db.session.get(ClienteModel, cliente_id)
        if not m:
            return  # opcional: crear registro perezoso si hiciera sentido
        m.total_pagos = (m.total_pagos or 0) + 1
        m.ultimo_pago = fecha_pago
        db.session.commit()
    
    def obtener_por_id(self, cliente_id: str) -> Optional[ClienteNatural]:
        m = db.session.get(ClienteModel, cliente_id)
        return modelo_a_cliente(m) if m else None