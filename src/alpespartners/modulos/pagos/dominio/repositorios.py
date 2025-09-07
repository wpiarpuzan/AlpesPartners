from abc import ABC, abstractmethod
from .entidades import Pago

class IPagoRepositorio(ABC):
    @abstractmethod
    def agregar(self, pago: Pago) -> None: ...
    @abstractmethod
    def obtener_por_id(self, pago_id: str) -> Pago | None: ...
