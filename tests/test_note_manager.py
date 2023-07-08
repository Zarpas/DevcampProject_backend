import pytest

from core import db
from core.models import Note

def test_new_note(app, auth):
    api_url = '/api/note/v1.0/note'

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
    assert "Note writers" in response.json["message"]

    auth.login()
    response = auth.post('/api/codelist/v1.0/codelist', json={'list_code': 'CA.1.00.000', 'description': 'test code', 'edition': '-', 'revision': '0', 'project': '2825'})
    print("codelist ",response.json)
    response = auth.post('/api/wirelist/v1.0/wire', json={
        "owner_id": 2, "orden": "1456", "edicion": "A",
        "zona1": "TL", "zona2": "TM", "zona3": "TN",
        "zona4": "TP", "zona5": "AC", "zona6": "59",
        "zona7": "72", "zona8": "F3", "zona9": "C9",
        "zona10": "C6", "zona11": "C2", "zona12": "B8",
        "cable_num": "33231.02", "clase": "LV",
        "lugarpro": "54", "aparatopro": "XC54.121/F", 
        "bornapro": "18", "esquemapro": "332C3", "lugardes": "73",
        "aparatodes": "30A01-PL2", "bornades": "E",
        "esquemades": "332C3", "seccion": "1", "longitud": "28366",
        "codigocabl": "X.64.00113.03", "terminalor": "X.79.00239.26",
        "terminalde": "C.K9.21.002.07", "num_mazo": "751",
        "codigo": "C.K8.77.145.01", "potencial": "33231", "peso": "0.018",
        "codreftori": "X.79.00239.26", "codreftdes": "C.K8.21.002.07"
        })
    print("codelist ",response.json)
    
    response = auth.post(api_url, json={})
    print(response.status_code)
    print(response.json)
    assert response.status_code == 400
    assert "Must include" in response.json["message"]

    response = auth.post(api_url, json={"note": "hola"})
    print(response.status_code)
    print(response.json)
    assert response.status_code == 400
    assert "Must include" in response.json["message"]

    response = auth.get('/api/wirelist/v1.0/wires')
    reference_id = response.json["items"][0]["id"]
    print(response.json)

    response = auth.post(api_url, json={"note": "hola", "reference_id": reference_id})
    print(response.status_code)
    print(response.json)
    assert response.status_code == 400
    assert "Must include" in response.json["message"]

    response = auth.post(api_url, json={"note": "hola", "reference_id": reference_id, "private": True})
    print(response.status_code)
    print(response.json)
    assert response.status_code == 201
    # assert "Must include" in response.json["message"]

    response = auth.post(api_url, json={"note": "hola", "reference_id": reference_id, "private": True})
    with app.app_context():
        note = db.session.get(Note, 2)
        note.sender_id = 2
        db.session.commit()


def test_get_note_list(auth):
    api_url = '/api/note/v1.0/notes'

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
    assert "Note writers" in response.json["message"]

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


def test_get_note(auth):
    api_url = '/api/note/v1.0/note'

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


def test_update_note(auth):
    api_url = '/api/note/v1.0/note'

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
    assert "Note writers" in response.json["message"]

    auth.login()

    response = auth.patch(api_url, json={})
    print(response.status_code)
    print(response.json)
    assert response.status_code == 400
    assert "identify" in response.json["message"]

    response = auth.patch(api_url, json={'id': 1})
    print(response.status_code)
    print(response.json)
    assert response.status_code == 400

    response = auth.patch(api_url, json={'id': 1, 'note': 'IGOR'})
    print(response.status_code)
    print(response.json)
    assert response.status_code == 200

    response = auth.patch(api_url, json={'id': 1, 'private': False})
    print(response.status_code)
    print(response.json)
    assert response.status_code == 200

    response = auth.patch(api_url, json={'id': 3, 'private': False})
    print(response.status_code)
    print(response.json)
    assert response.status_code == 400
    assert "not found" in response.json["message"]

    response = auth.patch(api_url, json={'id': 2, 'private': False})
    print(response.status_code)
    print(response.json)
    assert response.status_code == 400
    assert "isn't yours" in response.json["message"]
    

def test_delete_note(auth):
    api_url = '/api/note/v1.0/note'

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

    response = auth.delete(api_url + '?id=1')
    print(response.status_code)
    print(response.json)
    assert response.status_code == 400
    assert "not found" in response.json["message"]

    response = auth.delete(api_url + '?id=2')
    print(response.status_code)
    print(response.json)
    assert response.status_code == 400
    assert "isn't yours" in response.json["message"]
    