from alpespartners.modulos.cliente.dominio.repositorios import IClienteRepositorio
from alpespartners.modulos.cliente.infraestructura.repositorios import ClienteRepositorioSQLAlchemy

class FabricaRepositorio():
    def crear_objeto(self, tipo):
        if tipo == IClienteRepositorio:
            return ClienteRepositorioSQLAlchemy()
        raise ValueError(f'Repositorio no implementado para tipo: {tipo}')
