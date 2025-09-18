import os
import time
import json
import traceback
import logging
import sys
from datetime import datetime, timedelta
import requests
from sqlalchemy import create_engine, select, update
from sqlalchemy.exc import SQLAlchemyError
from .db_outbox import outbox_table, _get_engine, RETRY_LIMIT
from alpespartners.config.migrations import saga_log
from sqlalchemy import and_, func

POLL_INTERVAL_S = int(os.getenv('OUTBOX_POLL_INTERVAL_S', '3'))
BATCH_SIZE = int(os.getenv('OUTBOX_BATCH_SIZE', '10'))
RETRY_LIMIT = int(os.getenv('RETRY_LIMIT', '5'))
RETRY_BACKOFF_MS = int(os.getenv('RETRY_BACKOFF_MS', '2000'))


def default_handle_event(event_row, conn):
    # Default behavior for demo: call local BFF mock endpoints according to topic
    try:
        topic = event_row.topic
        payload = event_row.payload
        logging.info(f"[outbox.worker] handling event id={event_row.id} topic={topic} payload={payload}")
        base = os.getenv('BFF_BASE_URL', 'http://127.0.0.1:5000')
        if topic == 'inventory.reserve':
            url = f"{base}/inventory/reserve"
        elif topic == 'payment.charge':
            url = f"{base}/payment/charge"
        elif topic == 'inventory.release':
            url = f"{base}/inventory/release"
        else:
            print(f"[outbox.worker] unknown topic {topic}, skipping HTTP call")
            return
        logging.info(f"[outbox.worker] POST {url} payload={payload}")
        resp = requests.post(url, json=payload, timeout=10)
        # Log response details for easier debugging
        try:
            body = resp.text
        except Exception:
            body = '<unreadable body>'
        logging.info(f"[outbox.worker] HTTP {url} -> {resp.status_code} body={body}")
    except Exception as e:
        logging.exception(f"[outbox.worker] handler exception: {e}")
        raise


class OutboxWorker:
    def __init__(self, handle_event=None):
        self.engine = _get_engine()
        self.handle_event = handle_event or default_handle_event
        self.running = False

    def _fetch_pending(self, conn):
        # Only pick PENDING rows or RETRYING rows whose backoff period passed
        now = func.now()
        stmt = select(outbox_table).where(
            (outbox_table.c.status == 'PENDING') | (outbox_table.c.status == 'RETRYING')
        ).limit(BATCH_SIZE).with_for_update(skip_locked=True)
        res = conn.execute(stmt)
        rows = res.fetchall()
        ready = []
        for r in rows:
            # simple backoff: skip rows whose retry_count implies a backoff not passed
            retry = getattr(r, 'retry_count', 0) or 0
            updated_at = getattr(r, 'updated_at', None)
            if retry > 0 and updated_at is not None:
                # compute backoff in seconds
                backoff_ms = RETRY_BACKOFF_MS * (2 ** (retry - 1))
                backoff_s = backoff_ms / 1000.0
                age = (datetime.utcnow() - updated_at).total_seconds()
                if age < backoff_s:
                    # not ready yet
                    continue
            ready.append(r)
        return ready

    def _mark_as_sent(self, conn, rowid):
        stmt = update(outbox_table).where(outbox_table.c.id == rowid).values(
            status='SENT', updated_at=datetime.utcnow()
        )
        conn.execute(stmt)

    def _mark_failed(self, conn, rowid, error):
        # increment retry_count and set status accordingly
        # fetch current retry_count
        try:
            cur = conn.execute(select(outbox_table.c.retry_count).where(outbox_table.c.id == rowid)).scalar()
            cur = int(cur or 0)
        except Exception:
            cur = 0
        new_retry = cur + 1
        new_status = 'RETRYING' if new_retry < RETRY_LIMIT else 'FAILED'
        stmt = update(outbox_table).where(outbox_table.c.id == rowid).values(
            status=new_status, last_error=str(error), updated_at=datetime.utcnow(), retry_count=new_retry
        )
        conn.execute(stmt)

    def run_once(self):
        with self.engine.begin() as conn:
            rows = self._fetch_pending(conn)
            if not rows:
                return 0
            for r in rows:
                rid = r.id
                # Idempotency: if payload contains sagaStepId or unique dedupe key, ensure the saga_log doesn't already contain this step
                try:
                    payload = r.payload or {}
                    saga_step_id = None
                    if isinstance(payload, dict):
                        saga_step_id = payload.get('sagaStepId') or (payload.get('sagaId') and payload.get('type'))
                    if saga_step_id:
                        # check saga_log for an existing step with this payload
                        q = select(saga_log).where(
                            and_(saga_log.c.saga_id == payload.get('sagaId'), saga_log.c.step == saga_step_id)
                        ).limit(1)
                        existing = conn.execute(q).fetchone()
                        if existing:
                            # already handled — mark as SENT to avoid reprocessing
                            print(f"[outbox.worker] skipping already-applied saga_step_id={saga_step_id} for outbox id={rid}")
                            self._mark_as_sent(conn, rid)
                            continue
                except Exception:
                    # If idempotency check fails, continue to normal processing path
                    pass
                try:
                    # set as IN_PROGRESS to avoid other workers picking it
                    try:
                        conn.execute(update(outbox_table).where(outbox_table.c.id == rid).values(status='IN_PROGRESS', updated_at=datetime.utcnow()))
                    except Exception:
                        pass
                    # call handler
                    self.handle_event(r, conn)
                    self._mark_as_sent(conn, rid)
                    print(f"[outbox.worker] published id={rid}")
                except Exception as e:
                    print(f"[outbox.worker] error id={rid}: {e}")
                    traceback.print_exc()
                    # increment retry_count and optionally set FAILED
                    # simple logic: mark failed and leave for manual retry
                    self._mark_failed(conn, rid, e)
        return len(rows)

    def run(self):
        self.running = True
        logging.info('[outbox.worker] started')
        try:
            while self.running:
                try:
                    processed = self.run_once()
                except Exception as e:
                    logging.exception('[outbox.worker] run_once error')
                time.sleep(POLL_INTERVAL_S)
        except KeyboardInterrupt:
            logging.info('[outbox.worker] stopped by signal')

    def stop(self):
        self.running = False


def _main():
    # Configure logging
    logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    logging.info('Starting OutboxWorker (module runner)')
    worker = OutboxWorker()
    try:
        worker.run()
    except Exception:
        logging.exception('OutboxWorker exited with exception')
        raise


if __name__ == '__main__':
    try:
        _main()
    except Exception:
        # Exit with non-zero code so process manager can detect failure
        sys.exit(1)
