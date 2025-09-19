"""Launcher flexible para el servicio cliente.
"""
import importlib
import sys
import os

MODULE = os.environ.get('SERVICE_MODULE', 'cliente')

def try_create_app(module_name: str):
    try:
        mod = importlib.import_module(f"{module_name}.api")
    except Exception:
        try:
            mod = importlib.import_module(f"{module_name}.application.api")
        except Exception:
            return None
    create_app = getattr(mod, 'create_app', None)
    if callable(create_app):
        return create_app
    bp = getattr(mod, 'bp', None) or getattr(mod, 'blueprint', None)
    if bp is not None:
        from flask import Flask
        def factory():
            app = Flask(__name__)
            app.register_blueprint(bp)
            return app
        return factory
    return None

def try_consumers(module_name: str):
    try:
        mod = importlib.import_module(f"{module_name}.infraestructura.consumidores")
    except Exception:
        try:
            mod = importlib.import_module(f"{module_name}.infrastructure.consumidores")
        except Exception:
            return None
    for name in ('run', 'start', 'main'):
        fn = getattr(mod, name, None)
        if callable(fn):
            return fn
    return None

def main():
    factory = try_create_app(MODULE)
    if factory:
        app = factory()
        app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
        return

    consumer_fn = try_consumers(MODULE)
    if consumer_fn:
        consumer_fn()
        return

    print(f"No entry point encontrado para el módulo '{MODULE}'.", file=sys.stderr)
    sys.exit(1)

if __name__ == '__main__':
    main()
