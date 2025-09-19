from flask import Blueprint, request, jsonify, current_app
from alpespartners.config.db import db, ProcessedEvent, OutboxEvent
from sqlalchemy import text
import json

bp = Blueprint('tests', __name__, url_prefix='/test')

# Reuse existing publishers if available
def _get_publisher(module_names):
    for name in module_names:
        try:
            module = __import__(name, fromlist=['*'])
            if hasattr(module, 'publish_event'):
                return module.publish_event
        except Exception:
            continue
    return None

_publish_campanias = _get_publisher([
    'campanias.infrastructure.publisher',
    'campanias.infraestructura.publisher',
])
_publish_pagos = _get_publisher([
    'pagos.infrastructure.publisher',
    'pagos.infraestructura.publisher',
])


@bp.route('/publish', methods=['POST'])
def publish():
    """Publish an event to Pulsar using the available publisher helper.

    Expected JSON body: {"module": "pagos"|"campanias", "type": "Evento.v1", "data": {...}}
    """
    payload = request.get_json(force=True)
    module = payload.get('module')
    type_ = payload.get('type')
    data = payload.get('data')
    if not all([module, type_, data]):
        return jsonify({'error': 'module, type and data required'}), 400

    if module == 'pagos' and _publish_pagos:
        try:
            _publish_pagos(type_, data)
            return jsonify({'status': 'published'}), 202
        except Exception as e:
            current_app.logger.error('Publish failed: %s', e)
            return jsonify({'error': str(e)}), 500

    if module == 'campanias' and _publish_campanias:
        try:
            _publish_campanias(type_, data)
            return jsonify({'status': 'published'}), 202
        except Exception as e:
            current_app.logger.error('Publish failed: %s', e)
            return jsonify({'error': str(e)}), 500

    return jsonify({'error': 'no publisher available for module'}), 400


@bp.route('/db', methods=['GET'])
def db_summary():
    """Return small summary of useful tables for testing.

    Query params: aggregate_id (optional)
    """
    aggregate_id = request.args.get('aggregate_id')

    def q(sql, params=None):
        try:
            stmt = text(sql)
            res = db.session.execute(stmt, params or {})
            # SQLAlchemy Row objects expose a mapping interface on _mapping
            rows = [dict(r._mapping) for r in res]
            return rows
        except Exception as e:
            # Don't fail the whole endpoint for missing tables or transient DB errors
            current_app.logger.exception('DB helper query failed: %s', e)
            return []

    filters = ''
    params = {}
    if aggregate_id:
        filters = "WHERE aggregate_id = :agg"
        params = {'agg': aggregate_id}

    event_store = q('SELECT id, aggregate_id, type, payload, occurred_on FROM event_store ' + filters + ' ORDER BY id DESC LIMIT 50', params)
    campanias_view = q('SELECT * FROM campanias_view ' + ('WHERE id = :agg' if aggregate_id else '') + ' ORDER BY id', params)
    processed = q('SELECT * FROM processed_events ' + filters + ' ORDER BY id DESC LIMIT 50', params)
    outbox = q('SELECT * FROM outbox ' + ('WHERE payload->>\'aggregate_id\' = :agg' if aggregate_id else '') + ' ORDER BY id DESC LIMIT 50', params)

    return jsonify({
        'event_store': event_store,
        'campanias_view': campanias_view,
        'processed_events': processed,
        'outbox': outbox,
    })
