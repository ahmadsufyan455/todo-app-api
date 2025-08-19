from fastapi import status

from routers.user import get_current_user, get_db
from .utils import *

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_get_user(test_user):
    response = client.get("/user")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["email"] == "fyan@gmail.com"
    assert response.json()["first_name"] == test_user.first_name
    assert response.json()["last_name"] == test_user.last_name
    assert response.json()["phone_number"] == test_user.phone_number
    assert response.json()["role"] == test_user.role
    assert response.json()["user_id"] == 1


def test_change_password(test_user):
    response = client.put("/user/change-password", json={"current_password": "admin123", "new_password": "test123"})
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = TestSessionLocal()
    model = db.query(User).filter(User.id == 1).first()
    assert bcrypt_context.verify("test123", model.hashed_password)
    db.close()


def test_change_password_incorrect_password(test_user):
    response = client.put("/user/change-password", json={"current_password": "test123", "new_password": "test123"})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Confirm password is incorrect"}


def test_change_profile(test_user):
    request_body = {
        "email": "fyan514@gmail.com",
        "first_name": "Fyan",
        "last_name": "Liu",
        "phone_number": "1234567890",
    }
    response = client.put("/user/change-profile", json=request_body)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = TestSessionLocal()
    model = db.query(User).filter(User.id == 1).first()
    assert model.email == request_body["email"]
    assert model.first_name == request_body["first_name"]
    assert model.last_name == request_body["last_name"]
    assert model.phone_number == request_body["phone_number"]
    db.close()
