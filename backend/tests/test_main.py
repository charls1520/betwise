from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "BetWise API is running"}


def test_real_chat_endpoint(monkeypatch):
    # Mock query_index so it doesn't actually hit Ollama
    monkeypatch.setattr(
        "src.rag.pipeline.query_index", lambda idx, q: "Mocked RAG response"
    )

    response = client.post(
        "/api/chat", json={"message": "Injury update?", "match_id": 1}
    )
    assert response.status_code == 200
    assert "Mocked RAG response" in response.json()["response"]


def test_dashboard_endpoint():
    response = client.get("/api/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "matches" in data
    assert "suggestions" in data


def test_app_startup_initializes_rag(monkeypatch):
    # This is a bit tricky to test directly without starting the server,
    # but we can verify the global_index is not None or dummy.
    from src.main import global_index

    assert global_index is not None


def test_audit_endpoint():
    response = client.get("/api/health/audit")
    assert response.status_code == 200
    data = response.json()
    assert "rag_engine" in data
    assert "ml_engine" in data
    assert "ingestion_engine" in data
