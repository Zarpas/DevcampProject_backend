import pytest


def test_new_codelist(auth):
    api_url = '/api/codelist/v1.0/codelist'

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
    assert "List Operators" in response.json["message"]

    auth.login()

    response = auth.post(api_url, json={})
    print(response.status_code)
    print(response.json)
    assert response.status_code == 400
    assert "Must include" in response.json["message"]

    response = auth.post(api_url, json={'list_code': 'CA.1.00.000'})
    print(response.status_code)
    print(response.json)
    assert response.status_code == 400
    assert "Must include" in response.json["message"]

    response = auth.post(api_url, json={'list_code': 'CA.1.00.000', 'description': 'test code'})
    print(response.status_code)
    print(response.json)
    assert response.status_code == 400
    assert "Must include" in response.json["message"]

    response = auth.post(api_url, json={'list_code': 'CA.1.00.000', 'description': 'test code', 'edition': '-'})
    print(response.status_code)
    print(response.json)
    assert response.status_code == 400
    assert "Must include" in response.json["message"]

    response = auth.post(api_url, json={'list_code': 'CA.1.00.000', 'description': 'test code', 'edition': '-', 'revision': '0'})
    print(response.status_code)
    print(response.json)
    assert response.status_code == 400
    assert "Must include" in response.json["message"]

    response = auth.post(api_url, json={'list_code': 'CA.1.00.000', 'description': 'test code', 'edition': '-', 'revision': '0', 'project': '2825'})
    print(response.status_code)
    print(response.json)
    assert response.status_code == 201
    # assert "Must include" in response.json["message"]
    

def test_get_codelist_list(auth):
    api_url = '/api/codelist/v1.0/codelists'

    response = auth.get(api_url)
    print(response.status_code)
    print(response.json)
    assert response.status_code == 200
    assert response.json["_meta"]["per_page"] == 10

    response = auth.get(api_url + '?per_page=2&sent=True')
    print(response.status_code)
    print(response.json)
    assert response.status_code == 200
    assert response.json["_meta"]["per_page"] == 2

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


def test_get_codelist(auth):
    api_url = '/api/codelist/v1.0/codelist'

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
    
    response = auth.get(api_url, json={'id': 1})
    print(response.status_code)
    print(response.json)
    assert response.status_code == 200

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
    
    response = auth.get(api_url, json={'id': 1})
    print(response.status_code)
    print(response.json)
    assert response.status_code == 200


def test_delete_codelist(auth):
    api_url = '/api/codelist/v1.0/codelist'

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
    assert response.status_code == 200
    assert "deleted" in response.json["message"]

    response = auth.delete(api_url + '?id=2')
    print(response.status_code)
    print(response.json)
    assert response.status_code == 400
    assert "not found" in response.json["message"]

    response = auth.post(api_url, json={'list_code': 'CA.1.00.000', 'description': 'test code', 'edition': '-', 'revision': '0', 'project': '2825'})

