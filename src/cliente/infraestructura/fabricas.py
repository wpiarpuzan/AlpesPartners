from cliente.infraestructura.repositorios import ClienteRepo


class FabricaRepositorio:
    def crear_objeto(self, interface):
        return ClienteRepo()
