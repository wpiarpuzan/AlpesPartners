from alpespartners.modulos.cliente.dominio.entidades import ClienteNatural
from alpespartners.modulos.cliente.dominio.objetos_valor import Email
from .dto import ClienteModel

def modelo_a_cliente(m: ClienteModel) -> ClienteNatural:
    if m is None:
        return None

    email=Email(
            address=m.email,
            dominio=m.email.split('@')[1] if '@' in m.email else '',
            es_empresarial=True  # o False, según tu lógica
        )
    
    return ClienteNatural(
        id=m.id,
        nombre=m.nombre,
        email=email,
        cedula=m.cedula,                           # si tienes VO Cedula, cámbialo por Cedula(m.cedula)
        fecha_registro=m.fecha_registro,
        total_pagos=m.total_pagos or 0,
        ultimo_pago=m.ultimo_pago
    )