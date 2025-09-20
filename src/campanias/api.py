
from flask import Blueprint, request, jsonify
import json

from campanias.aplicacion.servicio import crear_campania_cmd, obtener_campania_qry

bp = Blueprint('campanias', __name__, url_prefix='/campanias')

# Optionally start local consumer thread when running inside Docker with START_CONSUMERS=1
try:
    import os
    if os.environ.get('START_CONSUMERS', '0') == '1':
        import threading
        try:
            from campanias.infrastructure import consumidores as _cons_mod
        except Exception:
            try:
                from campanias.infraestructura import consumidores as _cons_mod
            except Exception:
                _cons_mod = None
        if _cons_mod is not None and hasattr(_cons_mod, 'suscribirse_a_eventos_pagos'):
            def _start_cons():
                try:
                    _cons_mod.suscribirse_a_eventos_pagos()
                except Exception:
                    import logging; logging.exception('Local consumer failed')
            t = threading.Thread(target=_start_cons, daemon=True)
            t.start()
except Exception:
    pass

@bp.route('/comandos/crear', methods=['POST'])
def crear_campania():
    # Debug: print headers and raw body to help diagnose JSON parsing issues
    try:
        print('---- CAMPANIAS incoming Headers (top-level api) ----')
        print(dict(request.headers))
        print('---- CAMPANIAS raw body (top-level api) ----')
        raw = request.get_data(as_text=True)
        print(raw)
    except Exception as e:
        print('Error logging request data (top-level api):', e)

    # Robust JSON parsing: try Flask helper first, then fallback to raw body parsing
    data = request.get_json(silent=True)
    if data is None:
        try:
            data = json.loads(raw) if raw else None
        except Exception as e:
            return jsonify({'error': f'Invalid JSON body: {e}'}), 400

    # Debug: show parsed data structure
    try:
        print('---- CAMPANIAS parsed body (top-level api) ----')
        print(data)
    except Exception:
        pass

    if not data:
        return jsonify({'error': 'JSON body required'}), 400
    try:
        result = crear_campania_cmd(data)
        return jsonify(result), 202
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/<id_campania>', methods=['GET'])
def obtener_campania(id_campania):
    result = obtener_campania_qry(id_campania)
    if not result:
        return jsonify({'error': 'Campania no encontrada'}), 404
    return jsonify(result), 200
