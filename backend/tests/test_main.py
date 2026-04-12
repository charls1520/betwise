from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "BetWise API is running"}


def test_chat_endpoint():
    response = client.post(
        "/api/chat", json={"message": "Is the striker playing?", "match_id": 1}
    )
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "sources" in data
