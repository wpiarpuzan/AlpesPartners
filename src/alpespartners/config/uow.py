from alpespartners.config.db import db
from alpespartners.seedwork.infraestructura.uow import UnidadTrabajo, Batch

class UnidadTrabajoSQLAlchemy(UnidadTrabajo):

    def __init__(self):
        self._batches: list[Batch] = list()

    def __enter__(self) -> UnidadTrabajo:
        return super().__enter__()

    def __exit__(self, *args):
        self.rollback()

    def _limpiar_batches(self):
        self._batches = list()

    @property
    def savepoints(self) -> list:
        return list[db.session.get_nested_transaction()]

    @property
    def batches(self) -> list[Batch]:
        return self._batches             

    def commit(self):
        import logging
        logger = logging.getLogger("batch_logger")
        logger.setLevel(logging.DEBUG)
        logger.debug("[UnidadTrabajoSQLAlchemy.commit] INICIO batches")
        for idx, batch in enumerate(self.batches):
            logger.debug(f"[UnidadTrabajoSQLAlchemy.commit] Batch {idx}: operacion={batch.operacion}, args={batch.args}, kwargs={batch.kwargs}")
        logger.debug("[UnidadTrabajoSQLAlchemy.commit] FIN batches")
        for idx, batch in enumerate(self.batches):
            print(f"[DEBUG][commit] Ejecutando batch {idx}: operacion={batch.operacion}, args={batch.args}, kwargs={batch.kwargs}")
            lock = batch.lock
            batch.operacion(*batch.args, **batch.kwargs)
            print(f"[DEBUG][commit] Batch {idx} ejecutado")
        db.session.commit()
        super().commit()

    def rollback(self, savepoint=None):
        if savepoint:
            savepoint.rollback()
        else:
            db.session.rollback()
        
        super().rollback()
    
    def savepoint(self):
        db.session.begin_nested()