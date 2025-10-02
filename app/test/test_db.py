from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.models import User, table_registry


def test_create_user():
    engine = create_engine('sqlite:///database.db')
    table_registry.metadata.create_all(engine)

    with Session(engine) as session:
        user = User(
            username='cesar',
            password='testpassword',
            email='email@email.com',
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        assert user.id == 1
        assert user.username == 'cesar'
