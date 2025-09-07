from alpespartners.modulos.cliente.dominio.entidades import ClienteNatural
from alpespartners.modulos.cliente.dominio.objetos_valor import Email
from .dto import ClienteModel

def modelo_a_cliente(m: ClienteModel) -> ClienteNatural:
    if m is None:
        return None

    return ClienteNatural(
        id=m.id,
        nombre=m.nombre,
        email=Email(m.email) if isinstance(m.email, str) else m.email,
        cedula=m.cedula,                           # si tienes VO Cedula, cámbialo por Cedula(m.cedula)
        fecha_registro=m.fecha_registro,
        total_pagos=m.total_pagos or 0,
        ultimo_pago=m.ultimo_pago
    )