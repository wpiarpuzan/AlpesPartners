from abc import ABC, abstractmethod
from .entidades import ClienteNatural

class IClienteRepositorio(ABC):
    @abstractmethod
    def agregar(self, cliente: ClienteNatural) -> None: ...
    @abstractmethod
    def obtener_por_id(self, cliente_id: str) -> ClienteNatural | None: ...