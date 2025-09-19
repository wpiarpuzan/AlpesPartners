from alpespartners.config.db import db
from datetime import datetime


class EventStoreModel(db.Model):
    __tablename__ = "event_store"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    aggregate_id = db.Column(db.String, nullable=False, index=True)
    aggregate_type = db.Column(db.String, nullable=False, default='Campania')
    type = db.Column(db.String, nullable=False)
    payload = db.Column(db.Text, nullable=False)
    occurred_on = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class EventStoreRepo:
    def __init__(self, session=None):
        self._session = session or db.session

    def append(self, aggregate_id, event_type, schema_version, payload: dict):
        event = EventStoreModel(
            aggregate_id=aggregate_id,
            type=event_type,
            payload=str(payload)
        )
        self._session.add(event)
        self._session.commit()
        return event.id
