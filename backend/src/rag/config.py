from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama


def init_llama_index():
    """Initializes global LlamaIndex settings for embeddings and LLM."""
    # Use a lightweight local embedding model
    Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

    # Use local Ollama instance for the reader/generator
    Settings.llm = Ollama(model="llama3", request_timeout=60.0)
