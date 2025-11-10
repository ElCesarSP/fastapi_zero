from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_session
from app.models import User
from app.schemas import FilterPage, Message, UserList, UserPublic, UserSchema
from app.security import get_current_user, get_password_hast

router = APIRouter(prefix='/users', tags=['users'])

Session = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema, session: Session):
    # Verifica se username ou email já existem
    db_user = session.scalar(
        select(User).where(
            or_(User.username == user.username, User.email == user.email)
        )
    )

    if db_user:
        if db_user.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Username already exists',
            )
        elif db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Email already exists',
            )

    # Cria um novo usuário
    db_user = User(
        username=user.username,
        email=user.email,
        password=get_password_hast(user.password),
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@router.get('/', status_code=HTTPStatus.OK, response_model=UserList)
def read_users(
    session: Session,
    current_user: CurrentUser,
    filter_users: Annotated[FilterPage, Query()],
):
    users = session.scalars(
        select(User).limit(filter_users.limit).offset(filter_users.offset)
    ).all()
    return {'users': users}


@router.put('/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic)
def update_user(
    user_id: int,
    user: UserSchema,
    session: Session,
    current_user: CurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions'
        )

    try:
        current_user.email = user.email
        current_user.username = user.username
        current_user.password = get_password_hast(user.password)

        session.add(current_user)
        session.commit()
        session.refresh(current_user)

        return current_user

    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Username or email already exists',
        )

    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail=f'Error updating user: {str(e)}',
        )


@router.delete('/{user_id}', response_model=Message)
def delete_user(
    user_id: int,
    session: Session,
    current_user: CurrentUser,
):
    user_db = session.get(User, user_id)
    if not user_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='User not found',
        )

    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Not enough permissions',
        )

    session.delete(user_db)
    session.commit()

    return {'message': 'User Deleted'}


@router.get('/{user_id}', response_model=UserPublic)
def read_user(
    user_id: int,
    session: Session,
    current_user: CurrentUser,
):
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='User not found',
        )

    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Not enough permissions',
        )

    return db_user
