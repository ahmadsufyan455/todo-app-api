from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status

from database import SessionLocal
from models import User
from .auth import get_current_user

router = APIRouter(
    prefix="/user",
    tags=["user"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class UserResponse(BaseModel):
    user_id: int
    email: str
    first_name: str
    last_name: str
    role: str
    phone_number: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=6, max_length=255)

class UserProfileRequest(BaseModel):
    first_name: str
    last_name: str
    phone_number: str
    email: str


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.get("/", status_code=status.HTTP_200_OK)
async def get_user(db: db_dependency, user: user_dependency):
    validate_current_user(user)
    current_user = db.query(User).filter(User.id == user.get('user_id')).first()
    return UserResponse(
        user_id=current_user.id,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        phone_number=current_user.phone_number,
        role=current_user.role
    )


@router.put("/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(db: db_dependency, user: user_dependency, password: ChangePasswordRequest):
    validate_current_user(user)
    current_user = db.query(User).filter(User.id == user.get('user_id')).first()
    validate_current_password(password.current_password, current_user.hashed_password)
    current_user.hashed_password = bcrypt_context.hash(password.new_password)
    db.add(current_user)
    db.commit()

def validate_current_user(user: user_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")


def validate_current_password(current_password: str, hashed_password: str):
    if not bcrypt_context.verify(current_password, hashed_password):
        raise HTTPException(status_code=400, detail="Confirm password is incorrect")

@router.put("/change-profile", status_code=status.HTTP_204_NO_CONTENT)
async def change_profile(db: db_dependency, user: user_dependency, profile: UserProfileRequest):
    validate_current_user(user)
    current_user = db.query(User).filter(User.id == user.get('user_id')).first()
    current_user.first_name = profile.first_name
    current_user.last_name = profile.last_name
    current_user.phone_number = profile.phone_number
    current_user.email = profile.email
    db.add(current_user)
    db.commit()

