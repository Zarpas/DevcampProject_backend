import pytest


def test_new_picture(auth):
    api_url = '/api/picture/v1.0/picture'

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
    assert "Picture takers" in response.json["message"]

    auth.login()

    response = auth.post(api_url)
    print(response.status_code)
    print(response.json)
    assert response.status_code == 400
    assert "No file" in response.json["message"]

    headers = {"Authorization": f"Bearer {auth.get_access_token()}", "Content_type": "multipart/form-data"}
    response = auth.post(api_url, data={'reference_id': 1, 'filename':(open('/home/zarpas/proyectos/DevCamp-FinalProject/Docs/DSC02896.jpg','rb')),}, headers=headers)
    print(response.status_code)
    print(response.json)
    assert response.status_code == 400
    assert "Must include" in response.json["message"]

    response = auth.post(api_url + '?description=Hello World!&reference_id=1', data={'filename':(open('/home/zarpas/proyectos/DevCamp-FinalProject/Docs/DSC02896.jpg','rb')),}, headers=headers)
    print(response.status_code)
    print(response.json)
    assert response.status_code == 200
    # assert "Must include" in response.json["message"]

    response = auth.post(api_url + '?description=Helhi World!&reference_id=1', data={'filename':(open('/home/zarpas/proyectos/DevCamp-FinalProject/Docs/DSC02896.jpg','rb')),}, headers=headers)
    print(response.status_code)
    print(response.json)
    assert response.status_code == 200

    response = auth.post(api_url + '?description=Helhi World!&reference_id=1', data={'filename':(open('/home/zarpas/proyectos/DevCamp-FinalProject/Docs/L.C._CK.8.ods','rb')),}, headers=headers)
    print(response.status_code)
    print(response.json)
    assert response.status_code == 400

    
    

def test_get_picture_list(auth):
    api_url = '/api/picture/v1.0/pictures'

    response = auth.get(api_url)
    print(response.status_code)
    print(response.json)
    assert response.status_code == 400
    assert "identify" in response.json["message"]

    response = auth.get(api_url + '?reference_id=codelist')
    print(response.status_code)
    print(response.json)
    assert response.status_code == 200
    assert response.json["_meta"]["per_page"] == 10

    response = auth.get(api_url + '?per_page=2&reference_id=codelist')
    print(response.status_code)
    print(response.json)
    assert response.status_code == 200
    assert response.json["_meta"]["per_page"] == 2

    auth.login()

    response = auth.get(api_url + '?reference_id=1')
    print(response.status_code)
    print(response.json)
    assert response.status_code == 200
    assert response.json["_meta"]["per_page"] == 10

    response = auth.get(api_url + '?per_page=2&reference_id=1')
    print(response.status_code)
    print(response.json)
    assert response.status_code == 200
    assert response.json["_meta"]["per_page"] == 2


def test_get_picture(auth):
    api_url = '/api/picture/v1.0/picture'

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
    

def test_update_picture(auth):
    api_url = '/api/picture/v1.0/picture'

    response = auth.patch(api_url)
    print(response.status_code)
    print(response.json)
    assert response.status_code == 401
    assert "Missing" in response.json["msg"]

    auth.login(id=2)

    response = auth.patch(api_url)
    print(response.status_code)
    print(response.json)
    assert response.status_code == 403
    assert "Picture takers" in response.json["message"]

    auth.login()

    response = auth.patch(api_url, json={})
    print(response.status_code)
    print(response.json)
    assert response.status_code == 400
    assert "identify" in response.json["message"]

    response = auth.patch(api_url, json={"id": 3, "description": "prueba"})
    print(response.status_code)
    print(response.json)
    assert response.status_code == 400
    assert "not found" in response.json["message"]

    response = auth.patch(api_url, json={'id': 1})
    print(response.status_code)
    print(response.json)
    assert response.status_code == 400

    response = auth.patch(api_url, json={'id': 1, 'description': 'IGOR'})
    print(response.status_code)
    print(response.json)
    assert response.status_code == 200
    

def test_delete_picture(auth):
    api_url = '/api/picture/v1.0/picture'

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

    response = auth.delete(api_url + '?id=3')
    print(response.status_code)
    print(response.json)
    assert response.status_code == 400
    assert "not found" in response.json["message"]

    assert True == False