from datetime import timedelta, datetime

from fastapi import HTTPException
from jose import jwt
from starlette import status

from routers.auth import get_db, authenticate_user, create_access_token, ALGORITHM, SECRET_KEY, get_current_user
from .utils import *

app.dependency_overrides[get_db] = override_get_db


def test_authenticate_user(test_user):
    db = TestSessionLocal()
    authenticated_user = authenticate_user(test_user.email, "admin123", db)
    assert authenticated_user is not None
    assert authenticated_user.email == test_user.email

    not_authenticated_email = authenticate_user("fyantest@gmail.com", "admin123", db)
    assert not_authenticated_email is False

    not_authenticated_password = authenticate_user(test_user.email, "test123", db)
    assert not_authenticated_password is False

    db.close()


def test_create_access_token(test_user):
    token = create_access_token(test_user.email, test_user.id, test_user.role, timedelta(minutes=10))
    assert token is not None

    decode_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert decode_token["email"] == test_user.email
    assert decode_token["user_id"] == test_user.id
    assert decode_token["role"] == test_user.role
    assert decode_token["exp"] > datetime.now().timestamp()


@pytest.mark.asyncio
async def test_get_current_user(test_user):
    token = create_access_token(test_user.email, test_user.id, test_user.role, timedelta(minutes=10))
    current_user = await get_current_user(token=token)
    assert current_user is not None
    decode_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert current_user == {
        "email": decode_token["email"],
        "user_id": decode_token["user_id"],
        "role": decode_token["role"],
    }


@pytest.mark.asyncio
async def test_get_current_user_no_token(test_user):
    token = jwt.encode({"email": test_user.email}, SECRET_KEY, algorithm=ALGORITHM)

    with pytest.raises(HTTPException) as e:
        await get_current_user(token=token)

    assert e.value.status_code == 401
    assert e.value.detail == "Invalid credentials"


def test_create_user(test_user):
    request_body = {
        "email": "newfyan@gmail.com",
        "username": "newfyan",
        "first_name": test_user.first_name,
        "last_name": test_user.last_name,
        "phone_number": test_user.phone_number,
        "role": test_user.role,
        "password": "test123"
    }
    response = client.post("/auth/register", json=request_body)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {"message": "user successfully created"}
    db = TestSessionLocal()
    model = db.query(User).filter(User.email == request_body["email"]).first()
    assert model.email == request_body["email"]
    assert model.username == request_body["username"]
    assert model.first_name == request_body["first_name"]
    assert model.last_name == request_body["last_name"]
    assert model.phone_number == request_body["phone_number"]
    assert model.role == request_body["role"]
    assert bcrypt_context.verify("test123", model.hashed_password)
    db.close()


def test_create_user_already_exist(test_user):
    request_body = {
        "email": test_user.email,
        "username": test_user.username,
        "first_name": test_user.first_name,
        "last_name": test_user.last_name,
        "phone_number": test_user.phone_number,
        "role": test_user.role,
        "password": "test123"
    }
    response = client.post("/auth/register", json=request_body)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "User already exists"}


def test_login(test_user):
    request_body = {
        "username": test_user.email,
        "password": "admin123"
    }
    response = client.post("/auth/login", data=request_body,
                           headers={"Content-Type": "application/x-www-form-urlencoded"})
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert response.json()["access_token"] is not None
    assert response.json()["token_type"] == "bearer"


def test_login_failed(test_user):
    request_body = {
        "username": test_user.email,
        "password": "test123"
    }
    response = client.post("/auth/login", data=request_body,
                           headers={"Content-Type": "application/x-www-form-urlencoded"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Invalid credentials"}
