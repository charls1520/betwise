import os
# Set default embed model for tests before importing main to avoid HF model download errors
os.environ["EMBEDDING_MODEL_NAME"] = "BAAI/bge-small-en-v1.5"

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
    # Mock LLM calls inside normalizer to avoid hanging during tests
    monkeypatch.setattr("src.ingestion.normalizer.TeamNormalizer._ask_llm", lambda self, name: None)
    
    # Mock global_index to not be None
    import src.main
    monkeypatch.setattr(src.main, "global_index", "dummy_index")

    response = client.post(
        "/api/chat", json={"message": "Injury update?", "match_id": 1}
    )
    assert response.status_code == 200
    assert "Mocked RAG response" in response.json()["response"]


def test_dashboard_endpoint(monkeypatch):
    monkeypatch.setattr("src.ingestion.normalizer.TeamNormalizer._ask_llm", lambda self, name: None)
    response = client.get("/api/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "matches" in data
    assert "suggestions" in data


def test_app_startup_initializes_rag(monkeypatch):
    import src.main
    mock_called = False
    
    def mock_build_index_sync():
        nonlocal mock_called
        mock_called = True
        
    monkeypatch.setattr(src.main, "_build_index_sync", mock_build_index_sync)
    
    with TestClient(app) as test_client:
        import time
        time.sleep(0.1)  # allow background executor to run
        
    assert mock_called is True


def test_audit_endpoint():
    response = client.get("/api/health/audit")
    assert response.status_code == 200
    data = response.json()
    assert "rag_engine" in data
    assert "ml_engine" in data
    assert "ingestion_engine" in data
