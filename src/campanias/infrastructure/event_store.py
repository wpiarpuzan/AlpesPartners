import json
from datetime import datetime
from typing import Any, Dict, List
from sqlalchemy import create_engine, text
from alpespartners.config.db import db
from campanias.infrastructure.repos import EventStoreModel
import os


def append_event(aggregate_id: str, type_: str, data: Dict[str, Any]) -> Dict[str, Any]:
    db_url = os.getenv('DB_URL') or os.getenv('DATABASE_URL')
    if not db_url:
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


def events_of(aggregate_id: str):
    return (
        db.session.query(EventStoreModel)
        .filter_by(aggregate_id=aggregate_id)
        .order_by(EventStoreModel.id)
        .all()
    )
