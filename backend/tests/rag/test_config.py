from src.rag.config import init_llama_index
from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama


def test_init_llama_index(monkeypatch):
    monkeypatch.setenv("OLLAMA_MODEL", "gemma4:26b")
    # Calling the init function should configure the global Settings
    init_llama_index()

    assert isinstance(Settings.embed_model, HuggingFaceEmbedding)
    assert Settings.embed_model.model_name == "BAAI/bge-small-en-v1.5"

    assert isinstance(Settings.llm, Ollama)
    assert Settings.llm.model == "gemma4:26b"
