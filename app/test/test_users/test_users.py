from http import HTTPStatus
from unittest.mock import patch

from app.schemas import UserPublic


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


def test_create_user_duplicate_username(client):
    # Cria o primeiro usuário
    client.post(
        '/users/',
        json={
            'username': 'duplicate_user',
            'email': 'unique_email@test.com',
            'password': 'password1',
        },
    )

    # Tenta criar outro usuário com o mesmo username
    response = client.post(
        '/users/',
        json={
            'username': 'duplicate_user',
            'email': 'another_email@test.com',
            'password': 'password2',
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Username already exists'}


def test_create_user_duplicate_email(client):
    # Cria o primeiro usuário
    client.post(
        '/users/',
        json={
            'username': 'unique_user',
            'email': 'duplicate_email@test.com',
            'password': 'password1',
        },
    )

    # Tenta criar outro usuário com o mesmo email
    response = client.post(
        '/users/',
        json={
            'username': 'another_user',
            'email': 'duplicate_email@test.com',
            'password': 'password2',
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Email already exists'}


def test_read_users(client, user, token):
    user_schema = UserPublic.model_validate(user).model_dump()

    response = client.get(
        '/users/?limit=10&offset=0',
        headers={'Authorization': f'Bearer {token}'},
    )

    data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert data == {'users': [user_schema]}


def test_updade_user(client, token):
    response = client.put(
        '/users/1',
        headers={'Authorization': f'Bearer {token}'},
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


def test_delete_user(client, user, token):
    response = client.delete(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User Deleted'}


def test_update_integrity_error(client, user, token):
    client.post(
        '/users',
        json={
            'username': 'fausto',
            'email': 'fausto@exemple.com',
            'password': 'secrurytePass',
        },
    )

    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'fausto',
            'email': 'Bob@example.com',
            'password': 'myPassErro',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username or email already exists'}


def test_delete_user_not_found(client, token):
    non_existent_id = 999
    response = client.delete(
        f'/users/{non_existent_id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_read_get_user_not_found(client, token):
    non_existent_id = 999
    response = client.get(
        f'/users/{non_existent_id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_read_get_user(client, token, user):
    response = client.get(
        f'/users/{user.id}',  # ID real do usuário
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': user.id,
        'username': user.username,
        'email': user.email,
    }


def test_get_token(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )

    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert token['token_type'] == 'bearer'
    assert 'access_token' in token


def test_update_user_forbidden(client, token):
    # Tenta atualizar outro usuário
    response = client.put(
        '/users/999',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'hacker',
            'email': 'hack@test.com',
            'password': '123',
        },
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}


def test_update_user_generic_exception(client, token):
    with patch(
        'app.routers.users.users.get_password_hast',
        side_effect=Exception('hash error'),
    ):
        response = client.put(
            '/users/1',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'username': 'test',
                'email': 'test@test.com',
                'password': '123',
            },
        )
    assert response.status_code == HTTPStatus.CONFLICT
    assert 'Error updating user' in response.json()['detail']


def test_get_token_user_not_found(client):
    response = client.post(
        '/auth/token',
        data={'username': 'notfound@example.com', 'password': '123'},
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect email or password'}


def test_read_user_forbidden(client, token):
    client.post(
        '/users/',
        json={
            'username': 'other_user',
            'email': 'other@example.com',
            'password': 'otherpass',
        },
    )

    response = client.get(
        '/users/2',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}


def test_delete_user_forbidden(client, token):
    # Cria outro usuário real
    response_create = client.post(
        '/users/',
        json={
            'username': 'other_user',
            'email': 'other@example.com',
            'password': 'otherpass',
        },
    )

    other_user = response_create.json()

    # Tenta deletar o outro usuário com o token do primeiro
    response = client.delete(
        f'/users/{other_user["id"]}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}
