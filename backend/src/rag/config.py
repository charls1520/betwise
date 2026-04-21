import os
from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.llms.openai_like import OpenAILike

def init_llama_index():
    """Initializes global LlamaIndex settings for embeddings and LLM."""
    # Use a lightweight local embedding model
    embed_model_name = os.getenv("EMBEDDING_MODEL_NAME", "BAAI/bge-small-en-v1.5")
    Settings.embed_model = HuggingFaceEmbedding(model_name=embed_model_name)

    # Determine LLM Provider (OpenRouter vs Local Ollama)
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    model_name = os.getenv("LLM_MODEL_NAME")
    if not model_name:
        model_name = "gemma4:26b"

    if openrouter_key and openrouter_key.strip():
        # Use OpenRouter via OpenAILike compatibility
        Settings.llm = OpenAILike(
            model=model_name,
            api_key=openrouter_key,
            api_base="https://openrouter.ai/api/v1",
            max_tokens=1024,
            timeout=120.0,
            is_chat_model=True
        )
        print(f"LlamaIndex initialized using OpenRouter (Model: {model_name})")
    else:
        # Fallback to local Ollama
        base_url = os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
        # Legacy fallback if they still have OLLAMA_MODEL set
        fallback_model = os.getenv("OLLAMA_MODEL")
        if not fallback_model:
            fallback_model = model_name
            
        Settings.llm = Ollama(
            model=fallback_model, 
            base_url=base_url, 
            request_timeout=600.0
        )
        print(f"LlamaIndex initialized using Local Ollama (Model: {fallback_model})")
