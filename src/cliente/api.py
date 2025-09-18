from flask import Flask, jsonify

def create_app():
    app = Flask('cliente')

    @app.route('/')
    def index():
        return jsonify({'service': 'cliente', 'status': 'ok'})

    @app.route('/health')
    def health():
        return jsonify({'status': 'healthy'})

    return app
