from flask import Blueprint, jsonify, request, Response
import json

from alpespartners.seedwork.dominio.excepciones import ExcepcionDominio
from alpespartners.modulos.pagos.aplicacion.mapeadores import MapeadorPayoutDTOJson
from alpespartners.modulos.pagos.aplicacion.comandos.registrar_pago import ProcesarPago
from alpespartners.modulos.pagos.aplicacion.queries.obtener_pago import ObtenerPayout
from alpespartners.seedwork.aplicacion.comandos import ejecutar_commando
from alpespartners.seedwork.aplicacion.queries import ejecutar_query

bp = Blueprint("pagos", __name__, url_prefix="/pagos")
mapeador_payout = MapeadorPayoutDTOJson()

@bp.route('/pagar', methods=('POST',))
def procesar_payout_asincrono():
    try:
        payout_dict = request.json
        payout_dto_in = mapeador_payout.externo_a_dto(payout_dict)
        comando = ProcesarPago(
            partner_id=payout_dto_in.partner_id,
            cycle_id=payout_dto_in.cycle_id
        )
        payout = ejecutar_commando(comando)
        payout_id = payout.id if payout else None
        return Response(json.dumps({'id': payout_id}), status=202, mimetype='application/json')

    except ExcepcionDominio as e:
        return Response(json.dumps({'error': str(e)}), status=400, mimetype='application/json')
    except Exception as e:
        return Response(json.dumps({'error': str(e)}), status=500, mimetype='application/json')

@bp.route('/<id>', methods=('GET',))
def obtener_payout_por_id(id):
    try:
        query_resultado = ejecutar_query(ObtenerPayout(id=id))
        
        if query_resultado.resultado:
            payout_dto_out = mapeador_payout.dto_a_externo(query_resultado.resultado)
            return jsonify(payout_dto_out)
        else:
            return Response(json.dumps({'error': 'Payout no encontrado'}), status=404, mimetype='application/json')
            
    except Exception as e:
        return Response(json.dumps({'error': str(e)}), status=500, mimetype='application/json')
