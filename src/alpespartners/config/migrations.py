"""Lightweight startup migrations for demo/Heroku mode.
This is intentionally simple: create tables if they don't exist using SQLAlchemy metadata.
For production, replace with Alembic.
"""
from sqlalchemy import Table, Column, Integer, String, JSON, DateTime, MetaData, create_engine
from datetime import datetime
import os

DB_URL = os.getenv('DATABASE_URL') or os.getenv('DB_URL')
if not DB_URL:
    DB_URL = 'sqlite:///./dev.db'

# SQLAlchemy expects the 'postgresql' dialect name; Heroku provides URLs with
# the legacy 'postgres://' scheme. Normalize to a SQLAlchemy-compatible URL
# using the psycopg2 driver when needed.
if DB_URL.startswith('postgres://'):
    DB_URL = DB_URL.replace('postgres://', 'postgresql+psycopg2://', 1)

metadata = MetaData()

outbox = Table(
    'outbox', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('event_type', String, nullable=True),
    Column('topic', String, nullable=False),
    Column('payload', JSON, nullable=False),
    Column('status', String, nullable=False, default='PENDING'),
    Column('created_at', DateTime, nullable=False),
    Column('updated_at', DateTime, nullable=True),
    Column('last_error', String, nullable=True),
    Column('retry_count', Integer, nullable=False, default=0),
)

saga_log = Table(
    'saga_log', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('saga_id', String, nullable=False),
    Column('step', String, nullable=False),
    Column('step_id', String, nullable=True),
    Column('type', String, nullable=False),
    Column('payload', JSON, nullable=True),
    Column('status', String, nullable=False),
    Column('ts', DateTime, nullable=False, default=datetime.utcnow),
    Column('error', String, nullable=True),
)


def run_startup_migrations():
    engine = create_engine(DB_URL, future=True)
    metadata.create_all(engine)
    print('[migrations] ensured outbox and saga_log tables')
