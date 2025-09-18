
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
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

MODEL_MODULES = [   
    "alpespartners.modulos.cliente.infraestructura.dto",  # idem
    "alpespartners.modulos.pago.infraestructura.dto",     # si aún no existe, se ignora
    "alpespartners.modulos.campanias.infraestructura.repos", # Para event_store
]

def init_db(app: Flask):
    # Prefer Heroku's DATABASE_URL, then DB_URL. If neither exists, keep
    # the previous local default. Also normalize legacy 'postgres://' URLs
    # to the SQLAlchemy-compatible 'postgresql+psycopg2://' scheme.
    db_url = os.getenv('DATABASE_URL') or os.getenv('DB_URL') or (
        'postgresql+psycopg2://partner:partner@postgres:5432/alpespartner'
    )
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql+psycopg2://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
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