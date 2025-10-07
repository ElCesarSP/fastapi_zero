from sqlalchemy import select

from app.models import User


def test_create_user(session):
    user = User(
        username='cesar',
        password='testpassword',
        email='email@email.com',
    )
    session.add(user)
    session.commit()

    result = session.scalar(
        select(User).where(User.email == 'email@email.com')
    )

    assert result.id == 1
