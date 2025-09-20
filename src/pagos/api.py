from flask import Flask, jsonify

def create_app():
    app = Flask('pagos')

    @app.route('/')
    def index():
        return jsonify({'service': 'pagos', 'status': 'ok'})

    @app.route('/health')
    def health():
        return jsonify({'status': 'healthy'})

    @app.route('/comandos/crear', methods=['POST'])
    def crear_pago():
        """Endpoint de prueba para crear un pago y publicar PagoConfirmado.v1 en Pulsar.

        Body esperado JSON: { "idPago": "pay-1", "idCampania": "camp-1", "idCliente": "cli-1", "monto": 100 }
        """
        from flask import request
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'JSON body required'}), 400
            # Import the dispatcher from the spanish-named package (present in this repo)
            from pagos.infraestructura.despachadores import despachar_pago_exitoso
            despachar_pago_exitoso(data)
            return jsonify({'status': 'accepted', 'detail': 'Pago publicado'}), 202
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return app
