from abc import ABC, abstractmethod
from .entidades import ClienteNatural

class IClienteRepositorio(ABC):
    @abstractmethod
    def obtener_por_id(self, cliente_id: str) -> ClienteNatural | None: ...