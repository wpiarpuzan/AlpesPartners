from datetime import datetime
from alpespartners.config.db import db
from alpespartners.modulos.cliente.dominio.repositorios import IClienteRepositorio
from .dto import ClienteModel
from typing import Optional
from alpespartners.modulos.cliente.dominio.entidades import ClienteNatural
from .mapeadores import modelo_a_cliente
from .mapeadores import cliente_a_modelo

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
    
    def agregar(self, cliente: ClienteNatural):
        cliente_dto = cliente_a_modelo(cliente)
        print(f"[DEBUG][agregar] ClienteDTO: {cliente_dto}")
        db.session.add(cliente_dto)
        # El commit se manejará por fuera, en la unidad de trabajo (Unit of Work)