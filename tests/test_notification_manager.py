import pytest

from core import db
from core.models import User


def test_get_notification_list(app, auth):
    with app.app_context():
        user = db.session.get(User, 1)
        user.add_notification("example", data={"status": "complete"})
        db.session.commit()
    
    api_url = '/api/notification/v1.0/notifications'

    response = auth.get(api_url)
    print(response.status_code)
    print(response.json)
    assert response.status_code == 400
    assert "Registered users" in response.json["message"]

    auth.login()

    response = auth.get(api_url)
    print(response.status_code)
    print(response.json)
    assert response.status_code == 200
    assert response.json["items"][0]["id"] == 1
    assert response.json["_meta"]["per_page"] == 10

    response = auth.get(api_url + '?per_page=2')
    print(response.status_code)
    print(response.json)
    assert response.status_code == 200
    assert response.json["items"][0]["id"] == 1
    assert response.json["_meta"]["per_page"] == 2


def test_get_notification(auth):
    api_url = '/api/notification/v1.0/notification'

    response = auth.get(api_url)
    print(response.status_code)
    print(response.json)
    assert response.status_code == 400
    assert "Registered users" in response.json["message"]

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
    assert response.json["id"] == 1

    response = auth.get(api_url, json={'id': 1})
    print(response.status_code)
    print(response.json)
    assert response.status_code == 200
    assert response.json["id"] == 1
