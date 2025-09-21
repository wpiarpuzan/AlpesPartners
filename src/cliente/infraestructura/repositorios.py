from datetime import datetime
from alpespartners.config.db import db
from typing import Optional
from sqlalchemy import text


class ClienteRepositorioSQLAlchemy:
    def __init__(self):
        self._session = db.session

    def obtener_por_id(self, cliente_id: str) -> Optional[object]:
        r = self._session.execute(text("SELECT id, nombre, email, fecha_registro, total_pagos, ultimo_pago FROM clientes WHERE id = :id"), {"id": cliente_id}).fetchone()
        if not r:
            return None
        class C:
            pass
        c = C()
        c.id = r[0]
        c.nombre = r[1]
        c.email = r[2]
        c.fecha_registro = r[3]
        c.total_pagos = r[4]
        c.ultimo_pago = r[5]
        return c

    def agregar(self, cliente):
        # Implementación mínima: asume que la unidad de trabajo hace commit
        q = text("INSERT INTO clientes (id, nombre, email, fecha_registro, total_pagos) VALUES (:id, :nombre, :email, now(), 0)")
        # Ensure email is a plain string (some domain Email objects are not DB-adaptable)
        email_val = getattr(cliente, 'email', None)
        if email_val is None:
            email_str = None
        else:
            # If it's an object with attribute 'address' prefer that
            email_str = getattr(email_val, 'address', None) or str(email_val)

        self._session.execute(q, {"id": getattr(cliente, 'id', None), "nombre": getattr(cliente, 'nombre', None), "email": email_str})

    def actualizar_totales_por_pago(self, cliente_id: str, fecha_pago: datetime) -> None:
        q = text("UPDATE clientes SET total_pagos = COALESCE(total_pagos, 0) + 1, ultimo_pago = :fecha WHERE id = :id")
        self._session.execute(q, {"fecha": fecha_pago, "id": cliente_id})

# Alias por compatibilidad con importaciones antiguas
ClienteRepo = ClienteRepositorioSQLAlchemy
