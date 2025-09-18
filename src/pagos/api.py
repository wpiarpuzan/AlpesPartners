from flask import Flask, jsonify

def create_app():
    app = Flask('pagos')

    @app.route('/')
    def index():
        return jsonify({'service': 'pagos', 'status': 'ok'})

    @app.route('/health')
    def health():
        return jsonify({'status': 'healthy'})

    return app
