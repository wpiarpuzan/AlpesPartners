from flask import Blueprint, request, jsonify

from campanias.aplicacion.servicio import crear_campania_cmd, obtener_campania_qry

bp = Blueprint('campanias', __name__, url_prefix='/campanias')


@bp.route('/comandos/crear', methods=['POST'])
def crear_campania():
    # Debug: print headers and raw body to help diagnose JSON parsing issues
    try:
        print('---- CAMPANIAS incoming Headers (top-level api) ----')
        print(dict(request.headers))
        print('---- CAMPANIAS raw body (top-level api) ----')
        print(request.get_data(as_text=True))
    except Exception as e:
        print('Error logging request data (top-level api):', e)

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
