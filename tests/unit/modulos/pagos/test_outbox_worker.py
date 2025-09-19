import os
import time
from datetime import datetime
import sqlite3
import json

from alpespartners.infra.message_bus.db_outbox import metadata, outbox_table, DbOutboxBus, _get_engine
from alpespartners.infra.message_bus.worker import OutboxWorker
from sqlalchemy import create_engine, select


def test_outbox_worker_marks_sent(tmp_path, monkeypatch):
    # Use a temporary sqlite file so SQLAlchemy can be used across connections
    db_file = tmp_path / "test_db.sqlite"
    db_url = f"sqlite:///{db_file}"

    # Ensure environment uses our tmp sqlite DB
    monkeypatch.setenv('DATABASE_URL', db_url)

    # Create engine and ensure table exists
    engine = create_engine(db_url, future=True)
    metadata.create_all(engine)

    # Insert a pending outbox row using DbOutboxBus
    bus = DbOutboxBus()
    payload = {"sagaId": "test-saga", "type": "ChargePayment", "sagaStepId": "step-1"}
    rowid = bus.publish('payment.charge', payload)

    # Define a handler that simulates successful HTTP call
    def fake_handler(event_row, conn):
        # Do nothing (simulate 200 OK)
        return

    # Create worker and run once
    worker = OutboxWorker(handle_event=fake_handler)
    processed = worker.run_once()
    assert processed >= 1

    # Verify the outbox row was marked SENT
    with engine.connect() as conn:
        stmt = select(outbox_table).where(outbox_table.c.id == rowid)
        row = conn.execute(stmt).fetchone()
        assert row is not None
        assert row.status == 'SENT'
        assert row.updated_at is not None
