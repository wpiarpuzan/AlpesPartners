import os
import tempfile

import pytest
import json

from alpespartners.api import create_app, importar_modelos_alchemy
from alpespartners.config.db import init_db
from alpespartners.config.db import db

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # create a temporary file to isolate the database for each test
    db_fd, db_path = tempfile.mkstemp()
    # create the app with common test config
    app = create_app({"TESTING": True, "DATABASE": db_path})

    # create the database and load test data
    with app.app_context():
        from alpespartners.config.db import db

        importar_modelos_alchemy()
        db.create_all()

    yield app

    # close and remove the temporary database
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()

def test_servidor_levanta(client):

    # Dado un cliente a endpoint health
    rv = client.get('/health')

    # Devuelve estados the UP el servidor
    assert rv.data is not None
    assert rv.status_code == 200

    response = json.loads(rv.data)

    assert response['status'] == 'up'
