from flask import Blueprint, request, jsonify
from alpespartners.modulos.reservas.aplicacion.servicio import crear_reserva_cmd, obtener_reserva_qry

bp = Blueprint('reservas', __name__, url_prefix='/reservas')

@bp.route('/comandos/crear', methods=['POST'])
def crear_reserva():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'JSON body required'}), 400
    try:
        result = crear_reserva_cmd(data)
        return jsonify(result), 202
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/<id_reserva>', methods=['GET'])
def obtener_reserva(id_reserva):
    result = obtener_reserva_qry(id_reserva)
    if not result:
        return jsonify({'error': 'Reserva no encontrada'}), 404
    return jsonify(result), 200
