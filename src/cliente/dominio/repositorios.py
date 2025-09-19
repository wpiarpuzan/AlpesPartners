from abc import ABC, abstractmethod


class IClienteRepositorio(ABC):
    @abstractmethod
    def obtener_por_id(self, cliente_id: str):
        raise NotImplementedError()
