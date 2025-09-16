"""
Aplicación Flask para el BFF Web UI

Configura y expone la aplicación Flask con todos los endpoints
del Backend For Frontend optimizado para interfaces web.
"""

from flask import Flask
from flask_cors import CORS
from marshmallow import ValidationError
import os

from bff.infrastructure.web.controllers import bff_bp
from bff.infrastructure.config import container


def create_bff_app():
    """Factory function para crear la aplicación BFF"""
    app = Flask(__name__)
    
    # Configuración básica
    app.config['SECRET_KEY'] = os.getenv('BFF_SECRET_KEY', 'dev-secret-key-bff')
    app.config['DEBUG'] = os.getenv('BFF_DEBUG', 'False').lower() == 'true'
    
    # Configurar CORS para permitir requests desde frontend
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000", "http://localhost:8080"],  # React, Vue, etc.
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Registrar blueprints
    app.register_blueprint(bff_bp)
    
    # Configurar logging
    if not app.debug:
        import logging
        from logging.handlers import RotatingFileHandler
        
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = RotatingFileHandler('logs/bff.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('BFF Web UI startup')
    
    # Middleware para logging de requests
    @app.before_request
    def log_request_info():
        if app.debug:
            container.logger_service.debug(f"Request: {request.method} {request.url}")
    
    @app.after_request
    def log_response_info(response):
        if app.debug:
            container.logger_service.debug(f"Response: {response.status_code}")
        return response
    
    # Handler global para errores no manejados
    @app.errorhandler(500)
    def internal_error(error):
        container.logger_service.error(f"Internal Server Error: {str(error)}")
        return {'error': 'Internal Server Error', 'message': 'Ha ocurrido un error interno'}, 500
    
    # Endpoint raíz de información
    @app.route('/')
    def info():
        return {
            'service': 'Alpes Partners BFF - Web UI',
            'version': '1.0.0',
            'description': 'Backend For Frontend optimizado para interfaces web',
            'endpoints': {
                'dashboard': '/api/v1/dashboard',
                'clientes': '/api/v1/clientes',
                'pagos': '/api/v1/pagos',
                'campanias': '/api/v1/campanias',
                'search': '/api/v1/search',
                'health': '/api/v1/health'
            },
            'docs': 'https://github.com/wpiarpuzan/AlpesPartners/blob/main/API_DOCUMENTATION.md'
        }
    
    return app


# Instancia de la aplicación para desarrollo
app = create_bff_app()


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('BFF_PORT', 5001)),
        debug=os.getenv('BFF_DEBUG', 'False').lower() == 'true'
    )