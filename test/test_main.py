from fastapi.testclient import TestClient
from api.main import app

def test_healthy():
    client = TestClient(app)
    response = client.get("/healthy")
    assert response.status_code == 200
    assert response.json() == {"message": "healthy"}