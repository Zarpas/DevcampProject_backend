import pytest

from core import db
from core.models import User


def test_register(client, app):
    assert client.post('/api/user/v1.0/user').status_code == 415
    headers = {"content-type": "application/json"}
    assert client.post('/api/user/v1.0/user', json={'id': '1'}, headers=headers)
    response = client.post(
        '/api/user/v1.0/user', json={'id': '1', 'username': 'Test', 'surnames': 'Test Test', 'email': 'igor@example.com', 'password': 'test'}, headers=headers,
    )
    print(response.json)
    assert response.status_code == 201

    with app.app_context():
        assert User.query.filter_by(username='Test').first() is not None


@pytest.mark.parametrize(('id', 'username', 'surnames', 'email', 'password', 'message'), (
    ('', '', '', '', '', b'Must include ID, username, surnames, email and password'),
    ('1', 'a', 'a', 'a', 'a', b'Please use a different ID' ),
    ('2', 'Test', 'Test Test', 'igor@example.com', 'test', b'Please use a different email address'),
))
def test_register_validate_input(client, id, username, surnames, email, password, message):
    headers = {"content-type": "application/json"}
    response = client.post(
        '/api/user/v1.0/user', json={'id': id, 'username': username, 'surnames': surnames, 'email': email, 'password': password}, headers=headers,
    )
    assert message in response.data


def test_login(client, auth):
    headers = {"content-type": "application/json"}
    assert client.post('/api/user/v1.0/login', json={'id': '1'}, headers=headers,).status_code == 400 
    assert client.post('/api/user/v1.0/login', json={'id': '1', 'password': 'test'}, headers=headers,).status_code == 200
    response = auth.login()
    assert response.json["status"] == 'created'
    auth.set_access_token(response.json["access_token"])
    auth.set_refresh_token(response.json["refresh_token"])


@pytest.mark.parametrize(('id', 'password', 'message'), (
    ('3', 'test', "Wrong username or password"),
    ('1', 'a', "Wrong username or password"),
))
def test_login_validate_input(auth, id, password, message):
    response = auth.login(id, password)
    assert message in response.json['message']


def test_logout(client, auth):
    response = auth.login()
    auth.set_access_token(response.json["access_token"])

    assert auth.logout(auth.get_access_token).status_code == 200 