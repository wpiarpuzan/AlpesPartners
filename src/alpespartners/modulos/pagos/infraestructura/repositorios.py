from typing import Optional
from alpespartners.config.db import db
from alpespartners.modulos.pagos.dominio.entidades import Transaction
from alpespartners.modulos.pagos.dominio.entidades import Payout
from alpespartners.modulos.pagos.dominio.repositorios import IPayoutRepositorio, ITransactionRepositorio

from .dto import PayoutModel, TransactionModel, PayoutCycleModel
from .mapeadores import MapeadorPayout, MapeadorTransaction

class PayoutRepositorioSQLAlchemy(IPayoutRepositorio):

    def __init__(self, session=None):
        self._session = session or db.session
        self._mapeador = MapeadorPayout()

    def agregar(self, payout: Payout):
        payout_dto = self._mapeador.entidad_a_dto(payout)
        self._session.add(payout_dto)
        # El commit se manejará por fuera, en la unidad de trabajo (Unit of Work)

    def obtener_por_id(self, payout_id: str) -> Optional[Payout]:
        payout_dto = self._session.query(PayoutModel).filter_by(id=payout_id).one_or_none()
        if payout_dto:
            return self._mapeador.dto_a_entidad(payout_dto)
        return None

    def actualizar(self, payout: Payout):
        # La sesión de SQLAlchemy rastrea los cambios en los objetos DTO.
        # Al confirmar la Unidad de Trabajo, los cambios se reflejarán en la BD.
        # No se necesita una implementación explícita si el objeto fue cargado
        # previamente en la misma sesión.
        pass

    def obtener_por_partner_y_ciclo(self, partner_id: str, cycle_id: str) -> Optional[Payout]:
        payout_dto = self._session.query(PayoutModel).filter_by(
            partner_id=partner_id, 
            cycle_id=cycle_id
        ).one_or_none()
        
        if payout_dto:
            return self._mapeador.dto_a_entidad(payout_dto)
        return None
    
class TransactionRepositorioSQLAlchemy(ITransactionRepositorio):
    """
    Implementación del repositorio de transacciones que utiliza SQLAlchemy para
    las operaciones de base de datos.
    """

    def __init__(self, session=None):
        """
        Inicializa el repositorio con una sesión de base de datos.
        Si no se proporciona una sesión, utiliza la sesión global de la aplicación.
        """
        self._session = session or db.session

    def agregar(self, transaccion: Transaction, mapeador=MapeadorTransaction()):
        """
        Agrega una entidad Transaction a la base de datos.
        """
        transaccion_dto = mapeador.entidad_a_dto(transaccion)
        self._session.add(transaccion_dto)

    def obtener_por_id(self, id: str, mapeador=MapeadorTransaction()) -> Transaction | None:
        """
        Obtiene una entidad Transaction por su identificador.
        """
        transaccion_dto = self._session.query(TransactionModel).filter_by(id=str(id)).one_or_none()
        return mapeador.dto_a_entidad(transaccion_dto) if transaccion_dto else None
    
    def obtener_por_partner_y_ciclo(self, partner_id: str, cycle_id: str, mapeador=MapeadorTransaction()) -> list[Transaction]:
        """
        Obtiene todas las transacciones comisionables para un socio dentro de un ciclo de pago
        que aún no han sido asignadas a un Payout.
        """
        # Paso 1: Obtener las fechas del ciclo de pago a partir de su ID.
        # Esto es necesario para filtrar las transacciones por el rango de fechas correcto.
        ciclo = self._session.query(PayoutCycleModel).filter_by(id=str(cycle_id)).one_or_none()
        if not ciclo:
            # Si el ciclo de pago no se encuentra en la base de datos, no puede haber
            # transacciones asociadas, por lo que se retorna una lista vacía.
            return []

        # Paso 2: Construir y ejecutar la consulta a la base de datos.
        # Se buscan todas las 'TransactionModel' que cumplan tres condiciones críticas:
        # 1. Pertenecen al 'partner_id' especificado.
        # 2. Aún no han sido liquidadas (el campo 'payout_id' es NULO).
        # 3. La fecha del evento ('event_timestamp') está dentro del rango [inicio, fin] del ciclo.
        transacciones_dto = self._session.query(TransactionModel).filter(
            TransactionModel.partner_id == str(partner_id),
            TransactionModel.payout_id.is_(None),
            TransactionModel.event_timestamp >= ciclo.start_date,
            TransactionModel.event_timestamp <= ciclo.end_date
        ).all()
        
        # Paso 3: Mapear la lista de DTOs (objetos de base de datos) a una lista de
        # entidades de dominio, que es lo que la capa de aplicación espera recibir.
        return [mapeador.dto_a_entidad(dto) for dto in transacciones_dto]

    def actualizar(self, transaccion: Transaction, mapeador=MapeadorTransaction()):
        """
        Actualiza una entidad Transaction. Dado que las transacciones son inmutables
        una vez creadas, este método generalmente no se usa o se usa para asignar un payout_id.
        SQLAlchemy maneja el seguimiento de cambios, por lo que una implementación explícita
        no siempre es necesaria.
        """
        pass

    def eliminar(self, aggregate_id: str):
        """
        Elimina una transacción por su ID. Implementar si es requerido por el negocio.
        """
        pass