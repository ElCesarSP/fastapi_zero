from http import HTTPStatus


def test_read_root_retornar_serve_on(client):
    response = client.get('/')  # Act (ação)
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Service online!'}
