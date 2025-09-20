from flask import Blueprint, request, jsonify
import json
import datetime

from campanias.application.servicio import crear_campania_cmd, obtener_campania_qry

bp = Blueprint('campanias', __name__, url_prefix='/campanias')


@bp.route('/comandos/crear', methods=['POST'])
def crear_campania():
    # write raw headers and body to stdout for quick debugging
    try:
        print('---- CAMPANIAS incoming Headers ----')
        print(dict(request.headers))
        print('---- CAMPANIAS raw body ----')
        print(request.get_data(as_text=True))
    except Exception as e:
        print('Error logging request data:', e)

    # Robust JSON parsing: try Flask helper first, then fallback to raw body parsing
    data = request.get_json(silent=True)
    raw = None
    if data is None:
        raw = request.get_data(as_text=True)
        try:
            data = json.loads(raw) if raw else None
        except Exception as e:
            # Save raw request and headers to a persistent debug file for inspection
            try:
                log_path = '/tmp/campanias_debug.log'
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write('\n---- DEBUG api.raw_invalid_json ----\n')
                    f.write(f'timestamp: {datetime.datetime.utcnow().isoformat()}Z\n')
                    f.write('headers:\n')
                    for k, v in request.headers.items():
                        f.write(f'  {k}: {v}\n')
                    f.write('raw_body:\n')
                    f.write((raw or '') + '\n')
            except Exception:
                pass
            return jsonify({'error': f'Invalid JSON body: {e}'}), 400

    # Debug: show parsed data structure
    try:
        print('---- CAMPANIAS parsed body ----')
        print(data)
    except Exception:
        pass

    if not data:
        return jsonify({'error': 'JSON body required'}), 400

    # Save parsed request to debug file for reliable retrieval
    try:
        log_path = '/tmp/campanias_debug.log'
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write('\n---- DEBUG api.parsed_request ----\n')
            f.write(f'timestamp: {datetime.datetime.utcnow().isoformat()}Z\n')
            f.write('headers:\n')
            for k, v in request.headers.items():
                f.write(f'  {k}: {v}\n')
            f.write('parsed_body:\n')
            try:
                f.write(json.dumps(data, ensure_ascii=False) + '\n')
            except Exception:
                f.write(repr(data) + '\n')
    except Exception:
        pass

    try:
        result = crear_campania_cmd(data)
        return jsonify(result), 202
    except Exception as e:
        # write validation error to debug file as well
        try:
            with open('/tmp/campanias_debug.log', 'a', encoding='utf-8') as f:
                f.write('\n---- DEBUG api.validation_error ----\n')
                f.write(f'timestamp: {datetime.datetime.utcnow().isoformat()}Z\n')
                f.write('error: ' + str(e) + '\n')
        except Exception:
            pass
        return jsonify({'error': str(e)}), 400


@bp.route('/<id_campania>', methods=['GET'])
def obtener_campania(id_campania):
    result = obtener_campania_qry(id_campania)
    if not result:
        return jsonify({'error': 'Campania no encontrada'}), 404
    return jsonify(result), 200
