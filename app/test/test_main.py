from http import HTTPStatus


def test_read_root_retornar_serve_on(client):
    response = client.get('/')  # Act (ação)
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Hello World'}


def test_create_user(client):
    response = client.post(  # UserSchema
        '/users/',
        json={
            'username': 'test_username',
            'email': 'test_test@test.com',
            'password': 'test_password',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'username': 'test_username',
        'email': 'test_test@test.com',
        'id': 1,
    }


def test_read_users(client):
    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'users': [
            {
                'username': 'test_username',
                'email': 'test_test@test.com',
                'id': 1,
            }
        ]
    }


def test_updade_user(client):
    response = client.put(
        '/users/1',
        json={
            'username': 'test_username2',
            'email': 'test_test@test2.com',
            'password': '',
            'id': 1,
        },
    )

    assert response.json() == {
        'username': 'test_username2',
        'email': 'test_test@test2.com',
        'id': 1,
    }


def test_delete_user(client):
    response = client.delete('/users/1')

    assert response.json() == {'message': 'User Deleted'}


def test_update_user_not_found(client):
    response = client.put(
        '/users/1',
        json={
            'username': 'test_username2',
            'email': 'test_test@test2.com',
            'password': '',
            'id': 1,
        },
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User Not Found'}


def test_delete_user_not_found(client):
    response = client.delete('/users/1')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User Not Found'}


def test_read_get_user_not_found(client):
    response = client.get('/users/1')
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User Not Found'}
