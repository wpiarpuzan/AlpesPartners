"""Launcher flexible para el servicio campanias.
Intenta (en este orden):
- importar `create_app` y ejecutar la app Flask
- importar `infraestructura.consumidores` y ejecutar una función `run()`
- imprimir un error explicativo si no hay punto de entrada.
"""
import importlib
import sys
import os

MODULE = os.environ.get('SERVICE_MODULE', 'campanias')

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
    # if module exposes Blueprint named 'bp' or 'blueprint', return a small factory
    bp = getattr(mod, 'bp', None) or getattr(mod, 'blueprint', None)
    if bp is not None:
        from flask import Flask
        import threading
        import logging
        def factory():
            app = Flask(__name__)
            # initialize shared DB (so repositories using alpespartners.config.db.db work)
            try:
                from alpespartners.config.db import init_db
                init_db(app)
            except Exception:
                pass
            # debug: print which blueprint/module file was loaded
            try:
                print('Registering blueprint from module:', getattr(bp, '__module__', None))
                import inspect
                mod = inspect.getmodule(bp)
                if mod is not None and hasattr(mod, '__file__'):
                    print('Blueprint module file:', mod.__file__)
            except Exception:
                pass
            app.register_blueprint(bp)
            # If requested, start local background consumers for this module.
            try:
                if os.environ.get('START_CONSUMERS', '0') == '1':
                    # Try to import the module's consumidores and start known functions
                    try:
                        cons_mod = importlib.import_module(f"{module_name}.infraestructura.consumidores")
                    except Exception:
                        try:
                            cons_mod = importlib.import_module(f"{module_name}.infrastructure.consumidores")
                        except Exception:
                            cons_mod = None
                    if cons_mod is not None:
                        fn = getattr(cons_mod, 'suscribirse_a_eventos_pagos', None) or getattr(cons_mod, 'run', None)
                        if callable(fn):
                            def _run_consumer():
                                try:
                                    logging.info(f"[LOCAL-CONSUMER] Starting consumer for {module_name}")
                                    fn()
                                except Exception:
                                    logging.exception(f"[LOCAL-CONSUMER] Consumer for {module_name} failed")
                            t = threading.Thread(target=_run_consumer, daemon=True)
                            t.start()
            except Exception:
                # Non-fatal: continue serving the Flask app even if consumer thread fails to start
                logging.exception('Failed to start local consumers')
            try:
                print('App url_map:')
                print(app.url_map)
            except Exception:
                pass
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
    # prefer function named 'run' or 'start'
    for name in ('run', 'start', 'main'):
        fn = getattr(mod, name, None)
        if callable(fn):
            return fn
    return None

def main():
    # 1) Flask app
    factory = try_create_app(MODULE)
    if factory:
        app = factory()
        # If run as script, start dev server (only for local/dev use)
        app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
        return

    # 2) Consumers
    consumer_fn = try_consumers(MODULE)
    if consumer_fn:
        consumer_fn()
        return

    print(f"No entry point encontrado para el módulo '{MODULE}'.\nBuscado: {module_name}.api.create_app y {module_name}.infraestructura.consumidores.run/start/main", file=sys.stderr)
    sys.exit(1)

if __name__ == '__main__':
    main()
