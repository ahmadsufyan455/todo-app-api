import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base
from api.main import app
from models import Todos, User
from routers.user import bcrypt_context

engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)

TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestSessionLocal()
        yield db
    finally:
        db.close()


def override_get_current_user():
    return {"email": "fyan@gmail.com", "user_id": 1, "role": "admin"}


client = TestClient(app)


@pytest.fixture
def test_todo():
    db = TestSessionLocal()
    db.query(Todos).delete()

    todo = Todos(
        title="Learn fastAPI",
        description="Because it's awesome",
        priority=5,
        completed=False,
        owner_id=1
    )
    db.add(todo)
    db.commit()
    db.refresh(todo)
    yield todo

    db.query(Todos).delete()
    db.commit()
    db.close()


@pytest.fixture
def test_user():
    db = TestSessionLocal()
    db.query(User).delete()

    user = User(
        email="fyan@gmail.com",
        username="fyan514",
        first_name="Ahmad",
        last_name="Sufyan",
        phone_number="087763324456",
        hashed_password=bcrypt_context.hash("admin123"),
        role="admin",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    yield user

    db.query(User).delete()
    db.commit()
    db.close()
