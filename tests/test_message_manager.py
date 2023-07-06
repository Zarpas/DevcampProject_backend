import pytest

from core.models import Message
from core import db

def test_new_message(auth):
    api_url = '/api/message/v1.0/message'

    response = auth.post(api_url)
    print(response.status_code)
    print(response.json)
    assert response.status_code == 401
    assert "Missing" in response.json["msg"]

    auth.login()

    response = auth.post(api_url, json={})
    print(response.status_code)
    print(response.json)
    assert response.status_code == 400
    assert "Must include" in response.json["message"]

    response = auth.post(api_url, json={'recipient_id': 2})
    print(response.status_code)
    print(response.json)
    assert response.status_code == 400
    assert "Must include" in response.json["message"]

    response = auth.post(api_url, json={'recipient_id': 2, "body":"Hello"})
    print(response.status_code)
    print(response.json)
    assert response.status_code == 201
    # assert "Must include" in response.json["message"]


def test_get_message_list(app, auth):

    with app.app_context():
        message = Message()
        message2 = Message()
        payload = {"sender_id": 2, "recipient_id": 1, "body": "hola"}
        payload2 = {"sender_id": 2, "recipient_id": 3, "body": "hola"}
        message.from_dict(payload)
        message2.from_dict(payload2)
        db.session.add(message)
        db.session.add(message2)
        db.session.commit()

    api_url = '/api/message/v1.0/messages'

    response = auth.get(api_url)
    print(response.status_code)
    print(response.json)
    assert response.status_code == 401
    assert "Missing" in response.json["msg"]

    auth.login()

    response = auth.get(api_url)
    print(response.status_code)
    print(response.json)
    assert response.status_code == 200
    assert response.json["_meta"]["per_page"] == 10
    assert "id=1" in response.json["items"][0]["_links"]["recipient"]

    response = auth.get(api_url + '?per_page=2&sent=True')
    print(response.status_code)
    print(response.json)
    assert response.status_code == 200
    assert response.json["_meta"]["per_page"] == 2
    assert "id=1" in response.json["items"][0]["_links"]["sender"]


def test_get_message(auth):
    api_url = '/api/message/v1.0/message'
    
    response = auth.get(api_url)
    print(response.status_code)
    print(response.json)
    assert response.status_code == 401
    assert "Missing" in response.json["msg"]

    auth.login()

    response = auth.get(api_url)
    print(response.status_code)
    print(response.json)
    assert response.status_code == 400
    assert "identify" in response.json["message"]

    response = auth.get(api_url, json={'od': 1})
    print(response.status_code)
    print(response.json)
    assert response.status_code == 400
    assert "identify" in response.json["message"]

    response = auth.get(api_url + '?id=1')
    print(response.status_code)
    print(response.json)
    assert response.status_code == 200
    
    response = auth.get(api_url, json={'id': 2})
    print(response.status_code)
    print(response.json)
    assert response.status_code == 200

    response = auth.get(api_url, json={'id': 3})
    print(response.status_code)
    print(response.json)
    assert response.status_code == 400


def test_delete_message(auth):
    api_url = '/api/message/v1.0/message'

    response = auth.delete(api_url)
    print(response.status_code)
    print(response.json)
    assert response.status_code == 401
    assert "Missing" in response.json["msg"]

    auth.login()

    response = auth.delete(api_url)
    print(response.status_code)
    print(response.json)
    assert response.status_code == 400
    assert "identify" in response.json["message"]

    response = auth.delete(api_url, json={'od': 1})
    print(response.status_code)
    print(response.json)
    assert response.status_code == 400
    assert "identify" in response.json["message"]

    response = auth.delete(api_url, json={'id': 1})
    print(response.status_code)
    print(response.json)
    assert response.status_code == 400
    assert "isn't yours" in response.json["message"]

    response = auth.delete(api_url + '?id=2')
    print(response.status_code)
    print(response.json)
    assert response.status_code == 200
    assert "deleted" in response.json["message"]

    response = auth.delete(api_url + '?id=2')
    print(response.status_code)
    print(response.json)
    assert response.status_code == 400
    assert "not found" in response.json["message"]
