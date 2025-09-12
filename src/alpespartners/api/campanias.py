from flask import Blueprint, request, jsonify

bp = Blueprint('campanias', __name__, url_prefix='/campanias')

@bp.route('/comandos/crear', methods=['POST'])
def crear_campania():
    data = request.get_json()
    # Aquí deberías llamar a tu lógica de aplicación para crear la campania
    # Por ejemplo: result = crear_campania_cmd(data)
    # return jsonify(result), 202
    return jsonify({'message': 'Campania creada (mock)', 'data': data}), 202

@bp.route('/<id_campania>', methods=['GET'])
def obtener_campania(id_campania):
    # Aquí deberías llamar a tu lógica de aplicación para obtener la campania
    # Por ejemplo: result = obtener_campania_qry(id_campania)
    # if not result:
    #     return jsonify({'error': 'Campania no encontrada'}), 404
    # return jsonify(result), 200
    return jsonify({'message': f'Campania {id_campania} (mock)'}), 200
