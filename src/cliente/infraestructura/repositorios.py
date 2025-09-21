from datetime import datetime
from alpespartners.config.db import db
from typing import Optional
from sqlalchemy import text


class ClienteRepositorioSQLAlchemy:
    def __init__(self):
        self._session = db.session

    def obtener_por_id(self, cliente_id: str) -> Optional[object]:
        r = self._session.execute(text("SELECT id, nombre, email, cedula, fecha_nacimiento, fecha_registro, total_pagos, ultimo_pago FROM clientes WHERE id = :id"), {"id": cliente_id}).fetchone()
        if not r:
            return None
        class C:
            pass
        c = C()
        c.id = r[0]
        c.nombre = r[1]
        c.email = r[2]
        c.cedula = r[3]
        c.fecha_nacimiento = r[4]
        c.fecha_registro = r[5]
        c.total_pagos = r[6]
        c.ultimo_pago = r[7]
        return c

    def agregar(self, cliente):
        # Implementación mínima: asume que la unidad de trabajo hace commit
        q = text("INSERT INTO clientes (id, nombre, email, cedula, fecha_nacimiento, fecha_registro, total_pagos) VALUES (:id, :nombre, :email, :cedula, :fecha_nacimiento, now(), 0)")

        # Ensure email is a plain string (some domain Email objects are not DB-adaptable)
        email_val = getattr(cliente, 'email', None)
        if email_val is None:
            email_str = None
        else:
            # If it's an object with attribute 'address' prefer that
            email_str = getattr(email_val, 'address', None) or str(email_val)

        # Cedula may be a value object; extract primitive
        cedula_val = getattr(cliente, 'cedula', None)
        if cedula_val is None:
            cedula_str = None
        else:
            cedula_str = getattr(cedula_val, 'numero', None) or str(cedula_val)

        # Fecha de nacimiento: try to pass a datetime (SQLAlchemy will adapt)
        fecha_nac = getattr(cliente, 'fecha_nacimiento', None)

        self._session.execute(q, {
            "id": getattr(cliente, 'id', None),
            "nombre": getattr(cliente, 'nombre', None),
            "email": email_str,
            "cedula": cedula_str,
            "fecha_nacimiento": fecha_nac
        })

    def actualizar_totales_por_pago(self, cliente_id: str, fecha_pago: datetime) -> None:
        q = text("UPDATE clientes SET total_pagos = COALESCE(total_pagos, 0) + 1, ultimo_pago = :fecha WHERE id = :id")
        self._session.execute(q, {"fecha": fecha_pago, "id": cliente_id})

# Alias por compatibilidad con importaciones antiguas
ClienteRepo = ClienteRepositorioSQLAlchemy
