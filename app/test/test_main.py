from http import HTTPStatus

from fastapi.testclient import TestClient

from app.main import app

# client = TestClient(app)


def test_read_root_retornar_serve_on():
    client = TestClient(app)  # Arrange (organização)

    response = client.get('/')  # Act (ação)
    assert response.status_code == HTTPStatus.OK
    # assert(Garanta pra mim que a resporta status OK)
    assert response.json() == {'message': 'Hello World'}
