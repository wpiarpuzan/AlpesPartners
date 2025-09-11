import json
from datetime import datetime
from typing import Any, Dict, List
from alpespartners.config.db import db
from alpespartners.modulos.reservas.infraestructura.repos import EventStoreModel


def append_event(aggregate_id: str, type_: str, data: Dict[str, Any]) -> EventStoreModel:
    record = EventStoreModel(
        aggregate_id=aggregate_id,
        aggregate_type='Reserva',
        type=type_,
        payload=json.dumps(data),
        occurred_on=datetime.utcnow()
    )
    db.session.add(record)
    db.session.commit()
    return record


def events_of(aggregate_id: str) -> List[EventStoreModel]:
    return (
        db.session.query(EventStoreModel)
        .filter_by(aggregate_id=aggregate_id)
        .order_by(EventStoreModel.id)
        .all()
    )
