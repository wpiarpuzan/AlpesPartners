from flask import Blueprint, request, jsonify

from campanias.application.servicio import crear_campania_cmd, obtener_campania_qry

bp = Blueprint('campanias', __name__, url_prefix='/campanias')


@bp.route('/comandos/crear', methods=['POST'])
def crear_campania():
    # debug: log raw body and headers to diagnose JSON parsing issues
    # Debug: print headers and raw body so Docker/container logs capture them
    try:
        print('---- CAMPANIAS incoming Headers ----')
        print(dict(request.headers))
        print('---- CAMPANIAS raw body ----')
        print(request.get_data(as_text=True))
    except Exception as e:
        print('Error logging request data:', e)
    data = request.get_json()
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
