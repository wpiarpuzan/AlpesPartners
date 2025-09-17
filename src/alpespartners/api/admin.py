from flask import Blueprint, jsonify
from alpespartners.config.migrations import run_startup_migrations

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/db/migrate', methods=['POST'])
def migrate():
    try:
        run_startup_migrations()
        return jsonify({'migrated': True}), 200
    except Exception as e:
        return jsonify({'migrated': False, 'error': str(e)}), 500
