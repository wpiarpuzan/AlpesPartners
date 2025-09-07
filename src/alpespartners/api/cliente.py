import json
from flask import jsonify, Response
import alpespartners.seedwork.presentacion.api as api
from alpespartners.seedwork.dominio.excepciones import ExcepcionDominio
from alpespartners.seedwork.aplicacion.queries import ejecutar_query
from alpespartners.modulos.cliente.aplicacion.queries.obtener_cliente import ObtenerClientePorId

bp = api.crear_blueprint('cliente', '/cliente')

@bp.route('/<cliente_id>', methods=('GET',))
def obtener_cliente(cliente_id: str):
    try:
        qres = ejecutar_query(ObtenerClientePorId(cliente_id))
        data = qres.resultado
        if data is None:
            return jsonify({"message": "No encontrado"}), 404
        return jsonify(data), 200
    except ExcepcionDominio as e:
        return Response(json.dumps(dict(error=str(e))), status=400, mimetype='application/json')
