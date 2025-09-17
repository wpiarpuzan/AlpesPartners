import os
import json
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import create_engine, Table, Column, Integer, String, JSON, DateTime, MetaData, select, update, insert
from sqlalchemy.exc import SQLAlchemyError

DB_URL = os.getenv('DATABASE_URL') or os.getenv('DB_URL')
# Normalize legacy Heroku scheme if present
if DB_URL and DB_URL.startswith('postgres://'):
    DB_URL = DB_URL.replace('postgres://', 'postgresql+psycopg2://', 1)
RETRY_LIMIT = int(os.getenv('RETRY_LIMIT', '5'))
RETRY_BACKOFF_MS = int(os.getenv('RETRY_BACKOFF_MS', '2000'))

metadata = MetaData()

outbox_table = Table(
    'outbox', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('event_type', String, nullable=True),
    Column('topic', String, nullable=False),
    Column('payload', JSON, nullable=False),
    Column('status', String, nullable=False, default='PENDING'),
    Column('created_at', DateTime, nullable=False, default=datetime.utcnow),
    Column('updated_at', DateTime, nullable=True),
    Column('last_error', String, nullable=True),
    Column('retry_count', Integer, nullable=False, default=0),
)

_engine = None

def _get_engine():
    global _engine
    if _engine is None:
        # Read env again (in case it changed) and normalize
        db_url = os.getenv('DATABASE_URL') or os.getenv('DB_URL') or DB_URL
        if db_url and db_url.startswith('postgres://'):
            db_url = db_url.replace('postgres://', 'postgresql+psycopg2://', 1)
        if not db_url:
            raise RuntimeError('DATABASE_URL or DB_URL must be set')
        _engine = create_engine(db_url, future=True)
    return _engine


class DbOutboxBus:
    """Simple DB Outbox publisher. Inserts into outbox table."""

    def __init__(self, topic_prefix: str = "default"):
        self.topic_prefix = topic_prefix
        self.engine = _get_engine()
        # ensure table exists
        metadata.create_all(self.engine)

    def publish(self, topic: str, payload: Dict[str, Any]):
        """Insert single event into outbox."""
        with self.engine.begin() as conn:
            stmt = insert(outbox_table).values(
                topic=topic,
                payload=payload,
                status='PENDING',
                created_at=datetime.utcnow(),
                retry_count=0
            ).returning(outbox_table.c.id)
            res = conn.execute(stmt)
            rowid = res.scalar()
            print(f"[DbOutboxBus] enqueued id={rowid} topic={topic}")
            return rowid

    def publish_batch(self, topic: str, events: List[Dict[str, Any]]):
        ids = []
        with self.engine.begin() as conn:
            for ev in events:
                stmt = insert(outbox_table).values(
                    topic=topic,
                    payload=ev,
                    status='PENDING',
                    created_at=datetime.utcnow(),
                    retry_count=0
                ).returning(outbox_table.c.id)
                res = conn.execute(stmt)
                ids.append(res.scalar())
        print(f"[DbOutboxBus] enqueued batch {len(ids)} events for topic={topic}")
        return ids


# Helper for on-startup migrations (very small)
def ensure_outbox_table():
    engine = _get_engine()
    metadata.create_all(engine)
    print('[DbOutboxBus] ensured outbox table')
