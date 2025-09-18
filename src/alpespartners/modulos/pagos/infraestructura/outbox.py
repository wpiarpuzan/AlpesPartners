import threading
import threading
import time
import os
from sqlalchemy import create_engine, text
from alpespartners.modulos.pagos.infraestructura.publisher import publish_event
import logging


def outbox_poller(interval_ms=1000):
    db_url = os.getenv('DB_URL') or os.getenv('DATABASE_URL')
    if not db_url:
        raise RuntimeError('DB_URL not set; cannot start outbox poller')
    db_url_sql = db_url.replace('+psycopg2', '')
    engine = create_engine(db_url_sql, pool_pre_ping=True)

    def poll():
        while True:
            try:
                with engine.begin() as conn:
                    # Grab a batch of pending events with row-level locking to avoid
                    # multiple pollers publishing the same outbox rows.
                    sel = text(
                        "SELECT id, event_type, payload FROM outbox "
                        "WHERE status = 'PENDING' ORDER BY id FOR UPDATE SKIP LOCKED LIMIT 10"
                    )
                    rows = conn.execute(sel).fetchall()
                    if rows:
                        print(f"[OUTBOX][POLL] Found {len(rows)} pending rows")
                    for row in rows:
                        id_, event_type, payload = row
                        try:
                            print(f"[OUTBOX][PUBLISH] id={id_} event_type={event_type}")
                            publish_event(event_type, payload)
                            upd = text("UPDATE outbox SET status='SENT', published_at = now() WHERE id = :id")
                            conn.execute(upd, {"id": id_})
                        except Exception:
                            # If publishing fails, we let the transaction roll back so the
                            # row remains PENDING for the next poll.
                            logging.exception("Error publicando evento desde outbox; rollback de transacción")
                            raise
            except Exception:
                # If the DB connection or publishing temporarily fails, wait and retry
                logging.exception('Outbox poller error; retrying after backoff')
            time.sleep(interval_ms / 1000.0)

    thread = threading.Thread(target=poll, daemon=True)
    thread.start()
"""Deprecated: Migrado a `src/pagos`.

Este archivo se deja como marcador temporal y no debe usarse.
"""

raise RuntimeError("Este módulo fue migrado a `pagos` y no debe usarse.")
