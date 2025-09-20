"""
Archivo principal para ejecutar el BFF Web UI

Punto de entrada para la aplicación BFF que puede ser usado
tanto para desarrollo como para producción.
"""

import os
import sys

# Agregar el path del proyecto al sys.path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from bff.infrastructure.web.app import create_bff_app

def main():
    """Función principal para ejecutar el BFF"""
    app = create_bff_app()
    
    # Configuración desde variables de entorno
    host = os.getenv('BFF_HOST', '0.0.0.0')
    port = int(os.getenv('BFF_PORT', 5001))
    debug = os.getenv('BFF_DEBUG', 'False').lower() == 'true'
    
    # Configuración de servicios backend
    alpespartners_cliente_url = os.environ['ALPESPARTNERS_CLIENTE_SERVICE_URL']
    alpespartners_pago_url = os.environ['ALPESPARTNERS_PAGO_SERVICE_URL']
    alpespartners_campania_url = os.environ['ALPESPARTNERS_CAMPANIA_SERVICE_URL']
    http_timeout = os.getenv('BFF_HTTP_TIMEOUT', '30')
    
    print(f"""
    🚀 Iniciando Alpes Partners BFF - Web UI
    
    📍 BFF URL: http://{host}:{port}
    🔧 Modo Debug: {debug}
    🌐 Backend URL: {
        "Cliente": alpespartners_cliente_url,
        "Pago": alpespartners_pago_url,
        "Campaña": alpespartners_campania_url
    }
    ⏱️ Timeout HTTP: {http_timeout} segundos
    
    Endpoints principales:
    • Health: http://{host}:{port}/api/v1/health
    • Dashboard: http://{host}:{port}/api/v1/dashboard
    • Clientes: http://{host}:{port}/api/v1/clientes
    • Pagos: http://{host}:{port}/api/v1/pagos
    • Campañas: http://{host}:{port}/api/v1/campanias
    • Búsqueda: http://{host}:{port}/api/v1/search?q=termino
    
    🔗 Comunicación: BFF → HTTP REST → AlpesPartners Services
    """)
    
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    main()