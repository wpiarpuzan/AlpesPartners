import threading
import threading
import time
import os
from sqlalchemy import create_engine, text
from alpespartners.modulos.pagos.infraestructura.publisher import publish_event
import logging


def _get_engine_from_env():
    db_url = os.getenv('DB_URL') or os.getenv('DATABASE_URL')
    if not db_url:
        raise RuntimeError('DB_URL not set; cannot start outbox poller')
    # Normalize legacy Heroku URL if present and remove +psycopg2 for direct engine
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql+psycopg2://', 1)
    db_url_sql = db_url.replace('+psycopg2', '')
    return create_engine(db_url_sql, pool_pre_ping=True)


def outbox_poller(interval_ms=1000):
    engine = _get_engine_from_env()

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
