import uuid
import uuid
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
import os

from sqlalchemy import create_engine, insert

from alpespartners.config.migrations import saga_log
from alpespartners.infra.message_bus.db_outbox import DbOutboxBus

DB_URL = os.getenv('DATABASE_URL') or os.getenv('DB_URL')
# Normalize if needed
if DB_URL and DB_URL.startswith('postgres://'):
    DB_URL = DB_URL.replace('postgres://', 'postgresql+psycopg2://', 1)

_engine = None

def _get_engine():
    global _engine
    if _engine is None:
        db_url = os.getenv('DATABASE_URL') or os.getenv('DB_URL') or DB_URL
        if db_url and db_url.startswith('postgres://'):
            db_url = db_url.replace('postgres://', 'postgresql+psycopg2://', 1)
        if not db_url:
            raise RuntimeError('DATABASE_URL or DB_URL must be set for orchestrator')
        _engine = create_engine(db_url, future=True)
    return _engine


class Orchestrator:
    """Simple saga orchestrator which writes saga_log rows and publishes
    commands to the DbOutboxBus. Each command includes a generated
    `sagaStepId` to allow idempotent handling by downstream services.
    """

    def __init__(self, saga_id: Optional[str] = None):
        self.saga_id = saga_id or str(uuid.uuid4())
        self.bus = DbOutboxBus()

    def _write_log(
        self,
        step: str,
        step_id: Optional[str],
        type_: str,
        payload: Dict[str, Any],
        status: str,
        error: Optional[str] = None,
    ):
        engine = _get_engine()
        with engine.begin() as conn:
            stmt = insert(saga_log).values(
                saga_id=self.saga_id,
                step=step,
                step_id=step_id,
                type=type_,
                payload=payload,
                status=status,
                ts=datetime.utcnow(),
                error=error,
            )
            conn.execute(stmt)

    def start(self, items, amount) -> str:
        """Start a new saga and record the start command in saga_log."""
        self._write_log('start', None, 'COMMAND', {'items': items, 'amount': amount}, 'PENDING')
        return self.saga_id

    def reserve_inventory(self, items, step_id: Optional[str] = None) -> str:
        sid = step_id or str(uuid.uuid4())
        payload = {'sagaId': self.saga_id, 'type': 'ReserveInventory', 'items': items, 'sagaStepId': sid}
        # publish command to inventory.reserve topic
        self.bus.publish('inventory.reserve', payload)
        self._write_log('reserve_inventory', sid, 'COMMAND', payload, 'PENDING')
        return sid

    def charge_payment(self, amount, step_id: Optional[str] = None) -> str:
        sid = step_id or str(uuid.uuid4())
        payload = {'sagaId': self.saga_id, 'type': 'ChargePayment', 'amount': amount, 'sagaStepId': sid}
        self.bus.publish('payment.charge', payload)
        self._write_log('charge_payment', sid, 'COMMAND', payload, 'PENDING')
        return sid

    def release_inventory(self, step_id: Optional[str] = None) -> str:
        sid = step_id or str(uuid.uuid4())
        payload = {'sagaId': self.saga_id, 'type': 'ReleaseInventory', 'sagaStepId': sid}
        self.bus.publish('inventory.release', payload)
        self._write_log('release_inventory', sid, 'COMMAND', payload, 'PENDING')
        return sid

    def record_event(self, step: str, step_id: Optional[str], payload: Dict[str, Any], status: str, error: Optional[str] = None):
        """Record an EVENT in saga_log (used by external services to persist events)."""
        self._write_log(step, step_id, 'EVENT', payload, status, error)
