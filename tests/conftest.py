import os
import tempfile

import pytest
import config
from core import create_app
from core import db
from core.models import User
from flask_migrate import init, migrate, upgrade


@pytest.fixture(scope="session")
def app():

    app = create_app(config.TestConfiguration)

    with app.app_context():
        upgrade()

    yield app



@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def set_access_token(self, token):
        self._access_token = token

    def get_access_token(self):
        return "Bearer {}".format(self._access_token)
    
    def set_refresh_token(self, token):
        self._refresh_token = token

    def get_refresh_token(self):
        return "Bearer {}".format(self._refresh_token)

    def login(self, id='1', password='test'):
        headers = {"content-type": "application/json"}
        return self._client.post(
            "/api/user/v1.0/login",
            json={'id': id, 'password': password}, headers=headers,
        )
    
    def logout(self, token):
        headers = {"Authorization": token}
        return self._client.delete('/api/user/v1.0/logout', headers=headers)

@pytest.fixture
def auth(client):
    return AuthActions(client)

