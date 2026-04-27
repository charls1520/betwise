# OpenRouter Dynamic Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Integrate OpenRouter as a dynamic fallback or replacement for local Ollama models in LlamaIndex and the auto-healing normalizer, configured via environment variables.

**Architecture:** Modify `src/rag/config.py` to check for `OPENROUTER_API_KEY`. If present, instantiate the OpenAI class from LlamaIndex pointing to the OpenRouter API base. If absent, fallback to Ollama. The model name will be driven by `LLM_MODEL_NAME`. Update requirements and Docker config to support `llama-index-llms-openai`.

**Tech Stack:** Python, LlamaIndex, OpenAI API spec.

---

### Task 1: Update Environment and Dependencies

**Files:**
- Modify: `backend/requirements.txt`
- Modify: `.env.example`
- Modify: `docker-compose.yml`

- [ ] **Step 1: Add dependency to requirements**

Update `backend/requirements.txt` to add `llama-index-llms-openai`.

```text
# At the end of requirements.txt
llama-index-llms-openai
```

- [ ] **Step 2: Install the dependency**

Run:
```bash
docker exec betwise_backend pip install llama-index-llms-openai
```

- [ ] **Step 3: Update `.env.example`**

Modify `.env.example` to reflect the new variables:

```env
# Configuración de Modelos de IA
# Si OPENROUTER_API_KEY está configurada, se usa OpenRouter. Si está vacía o no existe, se usa Ollama local.
OPENROUTER_API_KEY=
LLM_MODEL_NAME=meta-llama/llama-3-8b-instruct

# Configuración Ollama (Fallback)
OLLAMA_BASE_URL=http://host.docker.internal:11434
```

- [ ] **Step 4: Update `docker-compose.yml`**

Modify `docker-compose.yml` to pass `OPENROUTER_API_KEY` to the backend container.
In the `backend` service `environment:` block, add:

```yaml
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
```

- [ ] **Step 5: Commit**

```bash
git add backend/requirements.txt .env.example docker-compose.yml
git commit -m "chore: add openrouter dependencies and environment variables"
```

---

### Task 2: Implement Dynamic LLM Loader in Config

**Files:**
- Modify: `backend/src/rag/config.py`

- [ ] **Step 1: Refactor `init_llama_index`**

Update `backend/src/rag/config.py` to conditionally load OpenRouter or Ollama.

```python
import os
from llama_index.core import Settings
from llama_index.llms.ollama import Ollama
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

def init_llama_index():
    # Use HuggingFace local embeddings to save costs (BGE small)
    embed_model_name = os.getenv("EMBEDDING_MODEL_NAME", "BAAI/bge-small-en-v1.5")
    Settings.embed_model = HuggingFaceEmbedding(model_name=embed_model_name)

    # Determine LLM Provider (OpenRouter vs Local Ollama)
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    model_name = os.getenv("LLM_MODEL_NAME", "gemma4:26b")

    if openrouter_key and openrouter_key.strip():
        # Use OpenRouter via OpenAI compatibility
        Settings.llm = OpenAI(
            model=model_name,
            api_key=openrouter_key,
            api_base="https://openrouter.ai/api/v1",
            max_tokens=1024,
            timeout=120.0
        )
        print(f"LlamaIndex initialized using OpenRouter (Model: {model_name})")
    else:
        # Fallback to local Ollama
        base_url = os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
        # Legacy fallback if they still have OLLAMA_MODEL set
        fallback_model = os.getenv("OLLAMA_MODEL", model_name)
        Settings.llm = Ollama(
            model=fallback_model, 
            base_url=base_url, 
            request_timeout=600.0
        )
        print(f"LlamaIndex initialized using Local Ollama (Model: {fallback_model})")
```

- [ ] **Step 2: Commit**

```bash
git add backend/src/rag/config.py
git commit -m "feat(rag): add dynamic selection between openrouter and ollama in llamaindex config"
```

---

### Task 3: Update Tests for Config Logic

**Files:**
- Modify: `backend/tests/rag/test_config.py`

- [ ] **Step 1: Write test for dynamic loading**

Create or update `backend/tests/rag/test_config.py` to verify the logic.

```python
import pytest
import os
from llama_index.core import Settings
from llama_index.llms.ollama import Ollama
from llama_index.llms.openai import OpenAI
from src.rag.config import init_llama_index

def test_init_llama_index_with_openrouter(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "dummy_key")
    monkeypatch.setenv("LLM_MODEL_NAME", "meta-llama/llama-3-8b-instruct")
    
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
    
    Settings.llm = None
    
    init_llama_index()
    
    assert isinstance(Settings.llm, Ollama)
    assert Settings.llm.base_url == "http://localhost:11434"
```

- [ ] **Step 2: Commit**

```bash
git add backend/tests/rag/test_config.py
git commit -m "test: add tests for dynamic openrouter vs ollama configuration"
```
