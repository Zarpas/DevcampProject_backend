from core import create_app
import config


def test_config():
    assert not create_app().testing
    assert create_app(config.TestConfiguration).testing


def test_hello(client):
    response = client.get('/hello')
    assert response.data == b'Hello, World!'