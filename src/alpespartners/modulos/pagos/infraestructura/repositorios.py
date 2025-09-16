from alpespartners.config.db import ProcessedEvent
from typing import Optional
from alpespartners.config.db import db
from alpespartners.modulos.pagos.dominio.entidades import Transaction
from alpespartners.modulos.pagos.dominio.entidades import Payout
from alpespartners.modulos.pagos.dominio.repositorios import IPayoutRepositorio, ITransactionRepositorio

from .dto import PayoutModel, TransactionModel, PayoutCycleModel
from .mapeadores import MapeadorPayout, MapeadorTransaction

class PayoutRepositorioSQLAlchemy(IPayoutRepositorio):
    def guardar_evento_outbox(self, event_type, payload):
        from alpespartners.config.db import OutboxEvent
        evt = OutboxEvent(event_type=event_type, payload=payload)
        self._session.add(evt)
        self._session.commit()
        # Debug trace so demos show when an outbox row was created
        try:
            print(f"[OUTBOX][INSERT] id={evt.id} event_type={event_type}")
        except Exception:
            # best-effort logging, don't fail the flow
            print(f"[OUTBOX][INSERT] event_type={event_type} (id unknown)")

    def is_event_processed(self, aggregate_id, event_type, event_id):
        return self._session.query(ProcessedEvent).filter_by(
            aggregate_id=aggregate_id, event_type=event_type, event_id=event_id
        ).first() is not None

    def mark_event_processed(self, aggregate_id, event_type, event_id):
        pe = ProcessedEvent(
            aggregate_id=aggregate_id,
            event_type=event_type,
            event_id=event_id
        )
        self._session.add(pe)
        self._session.commit()

    def __init__(self, session=None):
        self._session = session or db.session
        self._mapeador = MapeadorPayout()

    def agregar(self, payout: Payout):
        payout_dto = self._mapeador.entidad_a_dto(payout)
        print(f"[DEBUG][agregar] PayoutDTO: {payout_dto}")
        self._session.add(payout_dto)
        # El commit se manejará por fuera, en la unidad de trabajo (Unit of Work)

    def obtener_por_id(self, payout_id: str, version_dto: bool = False) -> Optional[Payout]:
        payout_dto = self._session.query(PayoutModel).filter_by(id=payout_id).one_or_none()
        if payout_dto:
            if version_dto:
                return payout_dto
            return self._mapeador.dto_a_entidad(payout_dto)
        return None

    def actualizar(self, payout: Payout):
        """
        Actualiza un payout existente en la base de datos.
        """
        payout_dto = self._session.query(PayoutModel).filter_by(id=payout.id).one_or_none()
        if payout_dto:
            actualizado = self._mapeador.entidad_a_dto(payout)
            for attr, value in actualizado.__dict__.items():
                setattr(payout_dto, attr, value)
            # El commit se maneja por fuera

    def eliminar(self, aggregate_id: str):
        """
        Elimina un payout por su ID.
        """
        payout_dto = self._session.query(PayoutModel).filter_by(id=aggregate_id).one_or_none()
        if payout_dto:
            self._session.delete(payout_dto)

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
        Actualiza una entidad Transaction en la base de datos.
        """
        transaccion_dto = self._session.query(TransactionModel).filter_by(id=transaccion.id).one_or_none()
        if transaccion_dto:
            actualizado = mapeador.entidad_a_dto(transaccion)
            for attr, value in actualizado.__dict__.items():
                setattr(transaccion_dto, attr, value)
            # El commit se maneja por fuera

    def eliminar(self, aggregate_id: str):
        """
        Elimina una transacción por su ID.
        """
        transaccion_dto = self._session.query(TransactionModel).filter_by(id=aggregate_id).one_or_none()
        if transaccion_dto:
            self._session.delete(transaccion_dto)