from abc import ABC, abstractmethod
from .entidades import Payout, Transaction

class Repositorio(ABC):
    @abstractmethod
    def obtener_por_id(self, id: str) -> any: ...

    @abstractmethod
    def agregar(self, aggregate: any): ...
    
    @abstractmethod
    def actualizar(self, aggregate: any): ...

    @abstractmethod
    def eliminar(self, aggregate_id: str): ...

class IPayoutRepositorio(Repositorio):
    @abstractmethod
    def obtener_por_partner_y_ciclo(self, partner_id: str, cycle_id: str) -> Payout | None: ...

class ITransactionRepositorio(Repositorio):
    @abstractmethod
    def obtener_por_partner_y_ciclo(self, partner_id: str, cycle_id: str) -> list[Transaction]:
        ...