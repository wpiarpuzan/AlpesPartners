
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
import os, importlib

db = SQLAlchemy()

class ProcessedEvent(db.Model):
    __tablename__ = "processed_events"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    aggregate_id = db.Column(db.String, nullable=False)
    event_type = db.Column(db.String, nullable=False)
    event_id = db.Column(db.String, nullable=False)
    processed_at = db.Column(db.DateTime, server_default=db.func.now())
    __table_args__ = (db.UniqueConstraint('aggregate_id', 'event_type', 'event_id', name='_uq_processed_event'),)

class OutboxEvent(db.Model):
    __tablename__ = "outbox"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_type = db.Column(db.String, nullable=False)
    payload = db.Column(db.JSON, nullable=False)
    status = db.Column(db.String, default='PENDING')
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    published_at = db.Column(db.DateTime)

MODEL_MODULES = [   
    "cliente.infraestructura.dto",  # idem
    "pagos.infraestructura.dto",     # si aún no existe, se ignora
    "campanias.infrastructure.repos", # Para event_store
]

def init_db(app: Flask):
    # Use SQLite in-memory for tests to avoid external Postgres dependency
    if app.config.get('TESTING'):
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DB_URL', 'sqlite:///:memory:')
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
            'DB_URL',
            'postgresql+psycopg2://partner:partner@postgres:5432/alpespartner'
        )
    # Opcional: evita warnings y corta conexiones zombie
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_pre_ping': True}
    db.init_app(app)

    with app.app_context():
        # importa los modelos para que SQLAlchemy 
        for m in MODEL_MODULES:
            try:
                importlib.import_module(m)   # importa modelos para que create_all los “vea”
            except ModuleNotFoundError:
                pass 
        db.create_all()