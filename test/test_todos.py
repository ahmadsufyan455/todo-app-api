from fastapi import status

from routers.todos import get_db, get_current_user
from .utils import *

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_get_todos(test_todo):
    response = client.get("/todos")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
            "id": test_todo.id,
            "title": test_todo.title,
            "description": test_todo.description,
            "priority": test_todo.priority,
            "completed": test_todo.completed,
            "owner_id": test_todo.owner_id
        }
    ]


def test_get_todo(test_todo):
    response = client.get("/todos/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": test_todo.id,
        "title": test_todo.title,
        "description": test_todo.description,
        "priority": test_todo.priority,
        "completed": test_todo.completed,
        "owner_id": test_todo.owner_id
    }


def test_get_todo_not_found(test_todo):
    response = client.get("/todos/100")
    assert response.status_code == 404
    assert response.json() == {"detail": "Data not found"}


def test_add_todo(test_todo):
    request_body = {
        "title": "Learn PostgreSQL",
        "description": "Because it's best DBMS",
        "priority": 3,
        "completed": False
    }
    response = client.post("/todos/add", json=request_body)
    assert response.status_code == status.HTTP_201_CREATED
    db = TestSessionLocal()
    model = db.query(Todos).filter(Todos.id == 2).first()
    assert model.title == request_body["title"]
    assert model.description == request_body["description"]
    assert model.priority == request_body["priority"]
    assert model.completed == request_body["completed"]
    assert model.owner_id == 1
    db.close()


def test_update_todo(test_todo):
    request_body = {
        "title": "Learn PostgreSQL",
        "description": "Because it's best DBMS",
        "priority": 2,
        "completed": True
    }
    response = client.put("/todos/1/update", json=request_body)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = TestSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model.title == request_body["title"]
    assert model.description == request_body["description"]
    assert model.priority == request_body["priority"]
    assert model.completed == request_body["completed"]
    assert model.owner_id == 1
    db.close()


def test_update_todo_not_found(test_todo):
    request_body = {
        "title": "Learn PostgreSQL",
        "description": "Because it's best DBMS",
        "priority": 2,
        "completed": True
    }
    response = client.put("/todos/999/update", json=request_body)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Todo not found"}


def test_delete_todo(test_todo):
    response = client.delete("/todos/1/delete")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = TestSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model is None


def test_delete_todo_not_found(test_todo):
    response = client.delete("/todos/999/delete")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Todo not found"}
