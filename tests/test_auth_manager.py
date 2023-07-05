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
    print("If you read this text, delete de database.sqlite from tests directory.")
    assert response.status_code == 201

    response = client.post(
        '/api/user/v1.0/user', json={'id': '2', 'username': 'Test2', 'surnames': 'Test2 Test2', 'email': 'igor2@example.com', 'password': 'test'}, headers=headers,
    )

    with app.app_context():
        assert User.query.filter_by(username='Test').first() is not None


@pytest.mark.parametrize(('id', 'username', 'surnames', 'email', 'password', 'message'), (
    ('', '', '', '', '', b'Must include ID, username, surnames, email and password'),
    ('1', 'a', 'a', 'a', 'a', b'Please use a different ID' ),
    ('3', 'Test', 'Test Test', 'igor@example.com', 'test', b'Please use a different email address'),
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
    


@pytest.mark.parametrize(('id', 'password', 'message'), (
    ('3', 'test', "Wrong username or password"),
    ('1', 'a', "Wrong username or password"),
))
def test_login_validate_input(auth, id, password, message):
    response = auth.login(id, password)
    assert message in response.json['message']


def test_logout(client, auth):
    auth.login()

    response = auth.logout(auth.get_access_token())
    assert response.status_code == 200
    assert "revoked" in response.json["message"]
    response = auth.logout(auth.get_refresh_token())
    print(response.json)
    assert response.status_code == 200
    assert "revoked" in response.json["message"]


def test_logged_in(client, auth):
    response = client.get('/api/user/v1.0/logged_in')
    assert response.status_code == 200
    assert response.json["logged_in"] is not True

    auth.login()

    headers = {"Authorization": f"Bearer {auth.get_access_token()}"}
    response = client.get('/api/user/v1.0/logged_in', headers=headers)
    print(response.json)
    assert response.status_code == 200
    assert response.json["logged_in"] is True


def test_admin_required(client, auth):
    auth.login()
    headers = {"Authorization": f"Bearer {auth.get_access_token()}"}
    response = client.get('api/user/v1.0/users', headers=headers)
    assert "Admins" in response.json["message"]
    assert response.status_code == 403


def test_get_users(app, client, auth):
    with app.app_context():
        user = db.session.get(User, 1)
        user.admin = True
        db.session.commit()
    auth.login()

    headers = {"Authorization": f"Bearer {auth.get_access_token()}"}
    response = client.get('api/user/v1.0/users', headers=headers)
    print(response.json)
    assert response.status_code == 200
    assert response.json["_meta"]["per_page"] == 10

    response = client.get('api/user/v1.0/users?per_page=2', headers=headers)
    print(response.json)
    assert response.status_code == 200
    assert response.json["_meta"]["per_page"] == 2


def test_get_user(client, auth):
    auth.login()

    headers = {"Authorization": f"Bearer {auth.get_access_token()}"}
    response = client.get('/api/user/v1.0/user?id=1', headers=headers)
    print(response.json)
    assert response.status_code == 200

    headers = {"Authorization": f"Bearer {auth.get_access_token()}", "content-type": "application/json"}
    response = client.get('/api/user/v1.0/user', json={'id':1}, headers=headers)
    print(response.json)
    assert response.status_code == 200

    headers = {"Authorization": f"Bearer {auth.get_access_token()}"}
    response = client.get('/api/user/v1.0/user', headers=headers)
    print(response.json)
    assert "identify" in response.json['message']


@pytest.mark.parametrize(('id', 'username', 'email', 'fileupload', 'message'),(
    (1, 'Test2', 'igor@example.com', False, 400),
    (1, 'Test', 'igor2@example.com', False, 400),
    (1, 'Test', 'igor@example.com', True, 200)
))
def test_user_admin(client, auth, id, username, email, fileupload, message):
    auth.login()
    headers = {"Authorization": f"Bearer {auth.get_access_token()}", "content-type": "application/json"}
    data = {'id': id, 'username': username, 'email': email, 'fileupload': fileupload}
    response = client.patch('/api/user/v1.0/user', json=data, headers=headers)
    assert response.status_code == message


def test_search_user(client, auth):
    auth.login()
    headers = {"Authorization": f"Bearer {auth.get_access_token()}"}
    api_url = '/api/user/v1.0/search_user?id=1'
    response = client.get(api_url, headers=headers)
    print(response.json)
    print(response.status_code)
    assert response.json['items'][0]['username'] == 'Test'
    
    api_url = '/api/user/v1.0/search_user?username=Te'
    response = client.get(api_url, headers=headers)
    print(response.json)
    print(response.status_code)
    assert response.json['items'][0]['username'] == 'Test'

    api_url = '/api/user/v1.0/search_user?surnames=Te'
    response = client.get(api_url, headers=headers)
    print(response.json)
    print(response.status_code)
    assert response.json['items'][0]['username'] == 'Test'

    api_url = '/api/user/v1.0/search_user'
    response = client.get(api_url, headers=headers)
    print(response.json)
    print(response.status_code)
    assert "no data" in response.json['message']


def test_new_password(client, auth):
    auth.login()
    headers = {"Authorization": f"Bearer {auth.get_access_token()}", "content-type": "application/json"}
    data = {'old_password': "test2", 'new_password': "test"}
    response = client.patch('/api/user/v1.0/new_password', json=data, headers=headers)
    print(response.json)
    assert "Wrong" in response.json["message"]

    data = {'old_password': "test", 'new_password': "test"}
    response = client.patch('/api/user/v1.0/new_password', json=data, headers=headers)
    print(response.json)
    assert response.status_code == 200
    

    