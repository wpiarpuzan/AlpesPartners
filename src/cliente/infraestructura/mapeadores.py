def map_to_dto(cliente):
    return {
        'id': getattr(cliente, 'id', None),
        'nombre': getattr(cliente, 'nombre', None),
        'email': getattr(cliente, 'email', None),
    }
from cliente.dominio.entidades import Cliente

def map_to_domain(dto):
    return Cliente(idCliente=dto.get('id'), nombre=dto.get('nombre'), email=dto.get('email'), fecha_creacion=None)
