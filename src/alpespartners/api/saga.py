from flask import Blueprint, request, jsonify, current_app
import uuid
import os
from datetime import datetime
from alpespartners.infra.message_bus.db_outbox import DbOutboxBus, ensure_outbox_table
from alpespartners.config.migrations import saga_log
from sqlalchemy import create_engine, insert, select
from alpespartners.saga.orchestrator import Orchestrator
from datetime import datetime as _dt

bp = Blueprint('saga', __name__, url_prefix='/saga')

# Lazy engine creation to avoid import-time DB connections and to normalize
# legacy Heroku `postgres://` URLs which SQLAlchemy no longer accepts.
DB_URL = os.getenv('DATABASE_URL') or os.getenv('DB_URL')
_engine = None

def _get_engine():
    global _engine
    if _engine is None:
        db_url = os.getenv('DATABASE_URL') or os.getenv('DB_URL') or DB_URL
        if db_url and db_url.startswith('postgres://'):
            db_url = db_url.replace('postgres://', 'postgresql+psycopg2://', 1)
        if not db_url:
            raise RuntimeError('DATABASE_URL or DB_URL must be set for saga API')
        _engine = create_engine(db_url, future=True)
    return _engine


def write_saga_log(saga_id, step, type_, payload, status, error=None):
    engine = _get_engine()
    with engine.begin() as conn:
        stmt = insert(saga_log).values(
            saga_id=saga_id,
            step=step,
            step_id=payload.get('sagaStepId') if isinstance(payload, dict) else None,
            type=type_,
            payload=payload,
            status=status,
            ts=datetime.utcnow(),
            error=error
        )
        conn.execute(stmt)


@bp.route('/orders', methods=['POST'])
def start_order_saga():
    data = request.get_json() or {}
    # Create a saga id
    saga_id = data.get('sagaId') or str(uuid.uuid4())
    # Simplified payload: items and amount
    items = data.get('items', [])
    amount = data.get('amount', 0)
    # initial saga log entry
    write_saga_log(saga_id, step='start', type_='COMMAND', payload={'items': items, 'amount': amount}, status='PENDING')

    orch = Orchestrator(saga_id)
    # start and enqueue reserve with sagaStepId
    step_id = orch.reserve_inventory(items)
    # orchestration already wrote the reserve_inventory command log

    return jsonify({'orderId': saga_id, 'status': 'PENDING'}), 202


@bp.route('/orders/<saga_id>', methods=['GET'])
def get_order_saga(saga_id):
    # Return saga log entries
    engine = _get_engine()
    with engine.connect() as conn:
        stmt = select(saga_log).where(saga_log.c.saga_id == saga_id).order_by(saga_log.c.id)
        res = conn.execute(stmt)
        # Use mappings() so each row is a mapping compatible with dict()
        rows = [dict(r) for r in res.mappings().all()]
        # Convert datetime objects to isoformat for JSON serialization
        for row in rows:
            if row.get('ts') and isinstance(row.get('ts'), _dt):
                row['ts'] = row['ts'].isoformat()
    return jsonify({'sagaId': saga_id, 'log': rows}), 200


# Mock endpoints for inventory and payment (these would normally be separate services)
mock_bp = Blueprint('mocks', __name__)

@mock_bp.route('/inventory/reserve', methods=['POST'])
def inventory_reserve():
    data = request.get_json() or {}
    # Allow forcing failure via payload
    fail = data.get('forceFail', False)
    saga_id = data.get('sagaId')
    step_id = data.get('sagaStepId')
    if fail:
        # write saga log entry for failed reservation
        orch = Orchestrator(saga_id)
        orch.record_event('reserve_inventory', step_id, {'success': False}, 'FAILED', error='forced')
        return jsonify({'success': False}), 400
    # success
    orch = Orchestrator(saga_id)
    orch.record_event('reserve_inventory', step_id, {'success': True}, 'CONFIRMED')
    # enqueue payment charge with sagaStepId
    orch.charge_payment(data.get('amount', 0))
    return jsonify({'success': True}), 200


@mock_bp.route('/inventory/release', methods=['POST'])
def inventory_release():
    data = request.get_json() or {}
    saga_id = data.get('sagaId')
    orch = Orchestrator(saga_id)
    orch.record_event('release_inventory', data.get('sagaStepId'), data, 'PENDING')
    # perform release (idempotent in mock)
    orch.record_event('release_inventory', data.get('sagaStepId'), {'released': True}, 'COMPENSATED')
    return jsonify({'released': True}), 200


@mock_bp.route('/payment/charge', methods=['POST'])
def payment_charge():
    data = request.get_json() or {}
    fail = data.get('forceFail', False)
    saga_id = data.get('sagaId')
    step_id = data.get('sagaStepId')
    if fail:
        orch = Orchestrator(saga_id)
        orch.record_event('charge_payment', step_id, {'success': False}, 'FAILED', error='forced')
        # enqueue compensation: release inventory
        orch.release_inventory()
        return jsonify({'success': False}), 400
    orch = Orchestrator(saga_id)
    orch.record_event('charge_payment', step_id, {'success': True}, 'CONFIRMED')
    # finalize saga
    orch.record_event('complete', None, {'status': 'CONFIRMED'}, 'CONFIRMED')
    return jsonify({'success': True}), 200


@bp.route('/health', methods=['GET'])
def health():
    return jsonify({'uptime': 'unknown', 'version': '1.0', 'env': os.getenv('MESSAGE_BUS', 'pulsar')}), 200
