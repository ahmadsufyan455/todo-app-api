from fastapi import status

from routers.admin import get_db, get_current_user
from .utils import *

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_get_todos(test_todo):
    response = client.get("/admin/todos")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
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


def test_delete_todo(test_todo):
    response = client.delete("/admin/todos/1/delete")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = TestSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model is None

def test_delete_todo_not_found(test_todo):
    response = client.delete("/admin/todos/999/delete")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Todo not found"}

