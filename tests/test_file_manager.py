import pytest


from core import db
from core.models import User, File


def test_post_file(client, auth):
    api_url = '/api/file/v1.0/file'

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
    assert "File Uploaders" in response.json["message"]

    auth.login()

    response = auth.post(api_url)
    print(response.status_code)
    print(response.json)
    assert response.status_code == 400
    assert "No file" in response.json["message"]

    headers = {"Authorization": f"Bearer {auth.get_access_token()}", "Content_type": "multipart/form-data"}
    response = auth.post(api_url, data={'filename':(open('/home/zarpas/proyectos/DevCamp-FinalProject/Docs/L.C._CK.8.ods','rb')),}, headers=headers)
    print(response.status_code)
    print(response.json)
    assert response.status_code == 200

    headers = {"Authorization": f"Bearer {auth.get_access_token()}", "Content_type": "multipart/form-data"}
    response = auth.post(api_url, data={'filename':(open('/home/zarpas/proyectos/DevCamp-FinalProject/Docs/L.C._CK.8.ods','rb')),}, headers=headers)
    print(response.status_code)
    print(response.json)
    assert response.status_code == 200

    headers = {"Authorization": f"Bearer {auth.get_access_token()}", "Content_type": "multipart/form-data"}
    response = auth.post(api_url, data={'filename':(open('/home/zarpas/proyectos/DevCamp-FinalProject/Docs/backend class diagram.odg','rb')),}, headers=headers)
    print(response.status_code)
    print(response.json)
    assert response.status_code == 400
    assert "allowed" in response.json["message"]
    


def test_get_file_list(auth):
    api_url = '/api/file/v1.0/files'

    response = auth.get(api_url)
    print(response.json)
    print(response.status_code)
    assert response.status_code == 401
    assert "Missing" in response.json["msg"]

    auth.login(id='2')

    response = auth.get(api_url)
    print(response.json)
    print(response.status_code)
    assert response.status_code == 403
    assert "File Uploaders" in response.json["message"]

    auth.login()

    response = auth.get(api_url)
    print(response.json)
    print(response.status_code)
    assert response.status_code == 200
    assert response.json["_meta"]["per_page"] == 10

    response = auth.get(api_url + "?per_page=2")
    print(response.json)
    print(response.status_code)
    assert response.status_code == 200
    assert response.json["_meta"]["per_page"] == 2


def test_get_file(auth):
    api_url = '/api/file/v1.0/file'

    response = auth.get(api_url)
    print(response.json)
    print(response.status_code)
    assert response.status_code == 401
    assert "Missing" in response.json["msg"]

    auth.login(id='2')

    response = auth.get(api_url)
    print(response.json)
    print(response.status_code)
    assert response.status_code == 403
    assert "File Uploaders" in response.json["message"]

    auth.login()

    response = auth.get(api_url)
    print(response.json)
    print(response.status_code)
    assert response.status_code == 400
    assert "identify the file" in response.json["message"]

    response = auth.get(api_url, json={'od': 1})
    print(response.json)
    print(response.status_code)
    assert response.status_code == 400
    assert "identify the file" in response.json["message"]

    response = auth.get(api_url, json={'id': 1})
    print(response.json)
    print(response.status_code)
    assert response.status_code == 200
    assert response.json["id"] == 1

    response = auth.get(api_url + "?id=1")
    print(response.json)
    print(response.status_code)
    assert response.status_code == 200
    assert response.json["id"] == 1


def test_delete_file(auth):
    api_url = '/api/file/v1.0/file'

    response = auth.delete(api_url)
    print(response.json)
    print(response.status_code)
    assert response.status_code == 401
    assert "Missing" in response.json["msg"]

    auth.login(id='2')

    response = auth.delete(api_url)
    print(response.json)
    print(response.status_code)
    assert response.status_code == 403
    assert "File Uploaders" in response.json["message"]

    auth.login()

    response = auth.delete(api_url)
    print(response.json)
    print(response.status_code)
    assert response.status_code == 400
    assert "identify the file" in response.json["message"]

    response = auth.delete(api_url, json={'od': 1})
    print(response.json)
    print(response.status_code)
    assert response.status_code == 400
    assert "identify the file" in response.json["message"]

    response = auth.delete(api_url, json={'id': 1})
    print(response.json)
    print(response.status_code)
    assert response.status_code == 200
    assert "file deleted" in response.json["message"]

    response = auth.delete(api_url + "?id=1")
    print(response.json)
    print(response.status_code)
    assert response.status_code == 400
    assert "file not found" in response.json["message"]

    # assert True == False