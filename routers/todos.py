from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status

from database import SessionLocal
from models import Todos
from .auth import get_current_user

router = APIRouter(
    prefix="/todos",
    tags=["todos"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class TodoRequest(BaseModel):
    title: str = Field(min_length=3, max_length=50)
    description: str = Field(min_length=3, max_length=255)
    priority: int = Field(gt=0, lt=6)
    completed: bool


@router.get("/", status_code=status.HTTP_200_OK)
async def get_todos(db: db_dependency, user: user_dependency):
    get_user_validation(user)
    return db.query(Todos).filter(Todos.owner_id == user.get('user_id')).all()


@router.get("/{todo_id}", status_code=status.HTTP_200_OK)
async def get_todo(db: db_dependency, user: user_dependency, todo_id: int = Path(gt=0)):
    get_user_validation(user)
    todo = db.query(Todos).filter(Todos.id == todo_id).where(Todos.owner_id == user.get('user_id')).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Data not found")
    return todo


@router.post("/add", status_code=status.HTTP_201_CREATED)
async def add_todo(request: TodoRequest, db: db_dependency, user: user_dependency):
    get_user_validation(user)
    new_todo = Todos(**request.model_dump(), owner_id=user.get('user_id'))
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return {
        "message": "Success add todo",
        "data": new_todo
    }


@router.put("/{todo_id}/update", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(request: TodoRequest, db: db_dependency, user: user_dependency, todo_id: int = Path(gt=0)):
    get_user_validation(user)
    todo_model = db.query(Todos).filter(Todos.id == todo_id).where(Todos.owner_id == user.get('user_id')).first()
    if not todo_model:
        raise HTTPException(status_code=404, detail="Todo not found")
    todo_model.title = request.title
    todo_model.description = request.description
    todo_model.priority = request.priority
    todo_model.completed = request.completed

    db.add(todo_model)
    db.commit()


@router.delete("/{todo_id}/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db: db_dependency, user: user_dependency, todo_id: int = Path(gt=0)):
    get_user_validation(user)
    todo_model = db.query(Todos).filter(Todos.id == todo_id).where(Todos.owner_id == user.get('user_id')).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(todo_model)
    db.commit()

def get_user_validation(user: user_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
