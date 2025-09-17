import json
from datetime import datetime
from typing import Any, Dict, List
from sqlalchemy import create_engine, text
from alpespartners.config.db import db
from alpespartners.modulos.campanias.infraestructura.repos import EventStoreModel
import os


def append_event(aggregate_id: str, type_: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Append an event to the event_store using a short-lived engine/transaction.
    Returns a lightweight dict with inserted row info. This avoids using the
    Flask-scoped `db.session` from background threads.
    """
    db_url = os.getenv('DB_URL') or os.getenv('DATABASE_URL')
    if not db_url:
        # Fall back to Flask SQLAlchemy engine (will raise if not configured)
        record = EventStoreModel(
            aggregate_id=aggregate_id,
            aggregate_type='Campania',
            type=type_,
            payload=json.dumps(data),
            occurred_on=datetime.utcnow()
        )
        db.session.add(record)
        db.session.commit()
        return {"id": record.id, "aggregate_id": record.aggregate_id, "type": record.type}

    # SQLAlchemy engine expects the psycopg2-less URL for direct connect if present
    # Normalize legacy Heroku URL and create a short-lived engine
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql+psycopg2://', 1)
    db_url_sql = db_url.replace('+psycopg2', '')
    engine = create_engine(db_url_sql, pool_pre_ping=True)
    insert_q = text(
        "INSERT INTO event_store (aggregate_id, aggregate_type, type, payload, occurred_on) "
        "VALUES (:agg, 'Campania', :type, :payload, now()) RETURNING id"
    )
    with engine.begin() as conn:
        res = conn.execute(insert_q, {"agg": aggregate_id, "type": type_, "payload": json.dumps(data)})
        row = res.fetchone()
        inserted_id = row[0] if row is not None else None
    return {"id": inserted_id, "aggregate_id": aggregate_id, "type": type_}


def events_of(aggregate_id: str) -> List[EventStoreModel]:
    return (
        db.session.query(EventStoreModel)
        .filter_by(aggregate_id=aggregate_id)
        .order_by(EventStoreModel.id)
        .all()
    )
