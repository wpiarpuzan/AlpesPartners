from flask_sqlalchemy import SQLAlchemy
from flask import Flask
import os, importlib


db = SQLAlchemy()

MODEL_MODULES = [   
    "alpespartners.modulos.cliente.infraestructura.dto",  # idem
    "alpespartners.modulos.pago.infraestructura.dto",     # si aún no existe, se ignora
]

def init_db(app: Flask):
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DB_URL',
        'postgresql+psycopg2://partner:partner@127.0.0.1:5432/alpespartner'
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
    