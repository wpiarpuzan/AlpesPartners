import logging
import os
import threading
import traceback

from flask import Flask, jsonify
from flask_swagger import swagger
import os
import threading

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

    def run_with_log(name, fn):
        def wrapper():
            logging.info(f"[CONSUMER-START] Lanzando hilo: {name}")
            try:
                fn()
            except Exception as e:
                logging.error(f"[CONSUMER-FAIL] Hilo {name} terminó con error: {e}")
                logging.error(traceback.format_exc())
        t = threading.Thread(target=wrapper, daemon=True)
        t.start()

    run_with_log('cliente.suscribirse_a_pagos', cliente.suscribirse_a_pagos)
    run_with_log('pagos.suscribirse_a_eventos', pagos.suscribirse_a_eventos)
    run_with_log('cliente.suscribirse_a_comandos', cliente.suscribirse_a_comandos)
    run_with_log('pagos.suscribirse_a_comandos', pagos.suscribirse_a_comandos)
    run_with_log('campanias.suscribirse_a_eventos_pagos', campanias.suscribirse_a_eventos_pagos)

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
        # Run lightweight migrations (create outbox and saga_log) when starting
        try:
            from alpespartners.config.migrations import run_startup_migrations
            run_startup_migrations()
        except Exception:
            pass

        # If running in DB_OUTBOX mode, start the Outbox worker in-process
        if os.getenv('MESSAGE_BUS') == 'DB_OUTBOX':
            try:
                from alpespartners.infra.message_bus.worker import OutboxWorker

                def start_worker():
                    worker = OutboxWorker()
                    worker.run()

                t = threading.Thread(target=start_worker, daemon=True)
                t.start()
            except Exception:
                pass
        else:
            if not app.config.get('TESTING'):
                comenzar_consumidor()

    # Importa Blueprints
    from . import cliente
    from . import pagos
    from . import campanias
    from . import saga
    from . import admin

    # Registro de Blueprints
    app.register_blueprint(cliente.bp)
    app.register_blueprint(pagos.bp)
    app.register_blueprint(campanias.bp)
    # register saga endpoints and its mocks
    app.register_blueprint(saga.bp)
    app.register_blueprint(saga.mock_bp)
    app.register_blueprint(admin.bp)

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
