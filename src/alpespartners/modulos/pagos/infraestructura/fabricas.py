"""
Fábricas para la creación de objetos en la capa de infrastructura del dominio de pagos.
"""

from dataclasses import dataclass
from alpespartners.seedwork.dominio.fabricas import Fabrica
from alpespartners.seedwork.dominio.repositorios import Repositorio
from alpespartners.seedwork.dominio.excepciones import ExcepcionFabrica as ExcepcionFabricaDominio

from alpespartners.modulos.pagos.dominio.repositorios import IPayoutRepositorio, ITransactionRepositorio

from .repositorios import PayoutRepositorioSQLAlchemy, TransactionRepositorioSQLAlchemy


class ExcepcionFabrica(ExcepcionFabricaDominio):
    """Excepción específica para errores en la fábrica de la capa de infraestructura."""
    ...

@dataclass
class FabricaRepositorio(Fabrica):
    def crear_objeto(self, obj: type, mapeador: any = None) -> Repositorio:
        if obj == IPayoutRepositorio:
            return PayoutRepositorioSQLAlchemy()
        if obj == ITransactionRepositorio:
            return TransactionRepositorioSQLAlchemy()
        else:
            raise ExcepcionFabrica(f'No existe fábrica para el tipo de repositorio {obj}')