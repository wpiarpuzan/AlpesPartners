
from flask import Blueprint, request, jsonify
from alpespartners.modulos.campanias.aplicacion.servicio import crear_campania_cmd
from alpespartners.modulos.campanias.infraestructura.repos import CampaniaViewRepo
from alpespartners.config.db import db

bp = Blueprint('campanias', __name__, url_prefix='/campanias')

@bp.route('/comandos/crear', methods=['POST'])
def crear_campania():
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
    repo = CampaniaViewRepo(db.session)
    result = repo.get(id_campania)
    if not result:
        return jsonify({'error': 'Campania no encontrada'}), 404
    return jsonify(result), 200

