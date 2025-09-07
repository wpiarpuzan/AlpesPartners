import os

from flask import Flask, render_template, request, url_for, redirect, jsonify, session
from flask_swagger import swagger

# Identifica el directorio base
basedir = os.path.abspath(os.path.dirname(__file__))

def registrar_handlers():
    import alpespartners.modulos.cliente.aplicacion
    import alpespartners.modulos.pagos.aplicacion

def importar_modelos_alchemy():
    import alpespartners.modulos.cliente.infraestructura.dto
    import alpespartners.modulos.pagos.infraestructura.dto

def comenzar_consumidor():
    """
    Este es un código de ejemplo. Aunque esto sea funcional puede ser un poco peligroso tener 
    threads corriendo por si solos. Mi sugerencia es en estos casos usar un verdadero manejador
    de procesos y threads como Celery.
    """

    import threading
    import alpespartners.modulos.cliente.infraestructura.consumidores as cliente
    import alpespartners.modulos.pagos.infraestructura.consumidores as pagos

    # Suscripción a eventos
    threading.Thread(target=cliente.suscribirse_a_pagos).start()
    threading.Thread(target=pagos.suscribirse_a_eventos).start()

    # Suscripción a comandos
    threading.Thread(target=cliente.suscribirse_a_comandos).start()
    threading.Thread(target=pagos.suscribirse_a_comandos).start()

def create_app(configuracion={}):
    # Init la aplicacion de Flask
    app = Flask(__name__, instance_relative_config=True)
    
    app.config['SQLALCHEMY_DATABASE_URI'] =\
            'sqlite:///' + os.path.join(basedir, 'database.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.secret_key = '9d58f98f-3ae8-4149-a09f-3a8c2012e32c'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['TESTING'] = configuracion.get('TESTING')

     # Inicializa la DB
    from alpespartners.config.db import init_db, db
    
    init_db(app)
    importar_modelos_alchemy()
    registrar_handlers()

    with app.app_context():
        db.create_all()
        if not app.config.get('TESTING'):
            comenzar_consumidor()

     # Importa Blueprints
    from . import cliente
    from . import hoteles
    from . import pagos
    from . import precios_dinamicos
    from . import vehiculos
    from . import vuelos

    # Registro de Blueprints
    app.register_blueprint(cliente.bp)
    app.register_blueprint(pagos.bp)

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
