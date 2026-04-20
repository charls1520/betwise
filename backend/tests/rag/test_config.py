import pytest
import os
from llama_index.core import Settings
from llama_index.llms.ollama import Ollama
from llama_index.llms.openai import OpenAI
from src.rag.config import init_llama_index

class MockEmbedding:
    def __init__(self, model_name):
        self.model_name = model_name

def test_init_llama_index_with_openrouter(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "dummy_key")
    monkeypatch.setenv("LLM_MODEL_NAME", "meta-llama/llama-3-8b-instruct")
    monkeypatch.setattr("src.rag.config.HuggingFaceEmbedding", MockEmbedding)
    
    # Reset Settings to avoid cross-test pollution
    Settings.llm = None
    
    init_llama_index()
    
    assert isinstance(Settings.llm, OpenAI)
    assert Settings.llm.api_base == "https://openrouter.ai/api/v1"
    assert Settings.llm.model == "meta-llama/llama-3-8b-instruct"

def test_init_llama_index_with_ollama(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://localhost:11434")
    monkeypatch.setenv("OLLAMA_MODEL", "gemma:latest")
    monkeypatch.setattr("src.rag.config.HuggingFaceEmbedding", MockEmbedding)
    
    Settings.llm = None
    
    init_llama_index()
    
    assert isinstance(Settings.llm, Ollama)
    assert Settings.llm.base_url == "http://localhost:11434"
    assert Settings.llm.model == "gemma:latest"