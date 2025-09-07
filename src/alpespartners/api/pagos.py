# alpespartners/modulos/pago/infraestructura/api.py
from flask import Blueprint, jsonify, request, Response
import json

from alpespartners.modulos.pagos.infraestructura.repositorios import PagoRepositorioSQLAlchemy
from alpespartners.seedwork.dominio.excepciones import ExcepcionDominio
from alpespartners.modulos.pagos.infraestructura.mapeadores import MapeadorPagoDTOJson
from alpespartners.modulos.pagos.aplicacion.comandos.registrar_pago import RegistrarPago, RegistrarPagoHandler
from alpespartners.seedwork.aplicacion.comandos import ejecutar_commando  # mismo patrón que reserva
from alpespartners.modulos.pagos.infraestructura.event_bus import publicar_evento

bp = Blueprint("pagos", __name__, url_prefix="/pagos")

@bp.route('/pago-comando', methods=('POST',))
def registrar_pago_asincrono():
    try:
        pago_dict = request.json

        map_pago = MapeadorPagoDTOJson()
        pago_dto = map_pago.pago_a_modelo(pago_dict)

        # Comando CQS (no ejecutamos servicio sincrónico aquí)
        comando = RegistrarPago(
            reserva_id=pago_dto.reserva_id,
            cliente_id=pago_dto.cliente_id,
            valor=pago_dto.valor,
            moneda=pago_dto.moneda,
            medio_tipo=pago_dto.medio_tipo,
            medio_mask=pago_dto.medio_mask,
        )

        handler = RegistrarPagoHandler(PagoRepositorioSQLAlchemy(), publicar_evento)
        pago_id = handler.handle(comando)

        return Response(jsonify({"pago_id": pago_id}), status=202, mimetype='application/json')
    except ExcepcionDominio as e:
        return Response(json.dumps(dict(error=str(e))), status=400, mimetype='application/json')
