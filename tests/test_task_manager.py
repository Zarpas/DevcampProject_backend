import pytest
import time

from core.models import Task
from core import db

def test_new_task(auth):
    api_url = '/api/task/v1.0/task'
    response = auth.post(api_url)
    print(response.status_code)
    print(response.json)
    assert response.status_code == 401
    assert "Missing" in response.json["msg"]

    auth.login(id=2)

    response = auth.post(api_url)
    print(response.status_code)
    print(response.json)
    assert response.status_code == 403
    assert "List Operators only" in response.json["message"]

    auth.login()

    response = auth.post(api_url, json={})
    print(response.status_code)
    print(response.json)
    assert response.status_code == 400
    assert "No task especified" in response.json["message"]

    response = auth.post(api_url, json={"task": "example"})
    print(response.status_code)
    print(response.json)
    assert response.status_code == 400
    assert "File not especified" in response.json["message"]

    response = auth.post(api_url, json={"task": "example", "description": "test task", "filename": "6"})
    print(response.status_code)
    print(response.json)
    assert response.status_code == 200
    assert "launched" in response.json["message"]

    response = auth.post(api_url, json={"task": "example", "description": "test task", "filename": "6"})
    print(response.status_code)
    print(response.json)
    assert response.status_code == 400
    assert "currently in progress" in response.json["message"]


def test_get_task_list(app, auth):
    api_url = '/api/task/v1.0/tasks'
    response = auth.get(api_url)
    print(response.status_code)
    print(response.json)
    assert response.status_code == 401
    assert "Missing" in response.json["msg"]

    auth.login(id=2)

    response = auth.get(api_url)
    print(response.status_code)
    print(response.json)
    assert response.status_code == 403
    assert "List Operators only" in response.json["message"]

    auth.login()

    response = auth.get(api_url)
    print(response.status_code)
    print(response.json)
    assert response.status_code == 200
    assert response.json["_meta"]["per_page"] == 10

    response = auth.get(api_url + '?per_page=2')
    print(response.status_code)
    print(response.json)
    assert response.status_code == 200
    assert response.json["_meta"]["per_page"] == 2

    response = auth.get(api_url + "?active=True")
    print(response.status_code)
    print(response.json)
    assert response.status_code == 200
    assert response.json["items"][0]["complete"] == False


    with app.app_context():
        task = Task.query.filter_by(complete=False).first()
        task.complete = True
        db.session.commit()

    response = auth.get(api_url)
    print(response.status_code)
    print(response.json)
    assert response.status_code == 200
    assert response.json["items"][0]["complete"] == True


    
def test_get_task(auth):
    api_url = '/api/task/v1.0/task'
    response = auth.get(api_url)
    print(response.status_code)
    print(response.json)
    assert response.status_code == 401
    assert "Missing" in response.json["msg"]

    auth.login(id=2)

    response = auth.get(api_url)
    print(response.status_code)
    print(response.json)
    assert response.status_code == 403
    assert "List Operators only" in response.json["message"]

    auth.login()
    response = auth.get('/api/task/v1.0/tasks')
    print(response.json)
    id = response.json['items'][0]["id"]

    response = auth.get(api_url)
    print(response.status_code)
    print(response.json)
    assert response.status_code == 400
    assert "need to identify" in response.json["message"]
    
    response = auth.get(api_url, json={'od': id})
    print(response.status_code)
    print(response.json)
    assert response.status_code == 400
    assert "need to identify" in response.json["message"]

    response = auth.get(api_url + '?id={}'.format(id))
    print(response.status_code)
    print(response.json)
    assert response.status_code == 200
    assert id in response.json["id"]

    response = auth.get(api_url, json={'id': id})
    print(response.status_code)
    print(response.json)
    assert response.status_code == 200
    assert id in response.json["id"]


