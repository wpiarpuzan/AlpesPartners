import uuid
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
        id=uuid.UUID(m.id),
        nombre=m.nombre,
        email=email,
        cedula=m.cedula,                          
        fecha_registro=m.fecha_registro,
        total_pagos=m.total_pagos or 0,
        ultimo_pago=m.ultimo_pago
    )

def cliente_a_modelo(entidad: ClienteNatural) -> ClienteModel:
    if entidad is None:
        return None

    return ClienteModel(
        id=str(entidad.id),
        nombre=entidad.nombre,
        email=entidad.email.address,  # extraído del VO Email
        cedula=entidad.cedula.numero,   # extraído del VO Cedula
        fecha_nacimiento=entidad.fecha_nacimiento,
        fecha_registro=entidad.fecha_registro,
        total_pagos=entidad.total_pagos,
        ultimo_pago=entidad.ultimo_pago
    )