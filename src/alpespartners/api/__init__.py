import logging
import os
import threading
import traceback

from flask import Flask, jsonify
from flask_swagger import swagger

logging.basicConfig(level=logging.DEBUG)

# Handlers de dominio (registran comandos/eventos)
def registrar_handlers():
    import alpespartners.modulos.cliente.aplicacion
    import alpespartners.modulos.pagos.aplicacion

# Modelos SQLAlchemy
def importar_modelos_alchemy():
    import alpespartners.modulos.cliente.infraestructura.dto
    import alpespartners.modulos.pagos.infraestructura.dto

# Consumidores de eventos (ejemplo, pagos/cliente)
def comenzar_consumidor():
    import alpespartners.modulos.cliente.infraestructura.consumidores as cliente
    import alpespartners.modulos.pagos.infraestructura.consumidores as pagos
    import alpespartners.modulos.campanias.infraestructura.consumidores as campanias

    threading.Thread(target=cliente.suscribirse_a_pagos).start()
    threading.Thread(target=pagos.suscribirse_a_eventos).start()
    threading.Thread(target=cliente.suscribirse_a_comandos).start()
    threading.Thread(target=pagos.suscribirse_a_comandos).start()
    threading.Thread(target=campanias.suscribirse_a_eventos_pagos, daemon=True).start()

def create_app(configuracion: dict = {}):
    app = Flask(__name__, instance_relative_config=True)

    app.secret_key = '9d58f98f-3ae8-4149-a09f-3a8c2012e32c'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['TESTING'] = configuracion.get('TESTING')

    # Inicializa DB
    from alpespartners.config.db import init_db, db
    init_db(app)
    importar_modelos_alchemy()
    registrar_handlers()

    with app.app_context():
        db.create_all()
        if not app.config.get('TESTING'):
            comenzar_consumidor()

    # Importa y registra Blueprints de negocio
    from . import cliente
    from . import pagos
    app.register_blueprint(cliente.bp)
    app.register_blueprint(pagos.bp)
    from alpespartners.modulos.campanias.api import bp as campanias_bp
    app.register_blueprint(campanias_bp)

    # ---- Observabilidad: métricas ----
    from alpespartners.seedwork.observabilidad.metrics import (
        metrics_bp, register_metrics
    )
    register_metrics(app)
    app.register_blueprint(metrics_bp)

    # ---- Rutas auxiliares ----
    @app.errorhandler(Exception)
    def handle_exception(e):
        logging.error("\n" + traceback.format_exc())
        return jsonify({
            "error": str(e),
            "trace": traceback.format_exc()
        }), 500

    @app.route("/spec")
    def spec():
        swag = swagger(app)
        swag['info']['version'] = "1.0"
        swag['info']['title'] = "MediSupply"
        return jsonify(swag)

    @app.route("/health")
    def health():
        return {"status": "up"}

    return app
