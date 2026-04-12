# LlamaIndex RAG Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Set up a fully local RAG engine using LlamaIndex, HuggingFace embeddings, ChromaDB, and an Ollama-based local LLM for context-aware answers.

**Architecture:** A set of Python modules within the FastAPI backend to initialize the LlamaIndex settings, load local data into ChromaDB, and provide a basic query interface.

**Tech Stack:** Python 3.10+, `llama-index-core`, `llama-index-embeddings-huggingface`, `llama-index-vector-stores-chroma`, `llama-index-llms-ollama`, `chromadb`.

---

### Task 1: Setup Dependencies and LlamaIndex Initialization

**Files:**
- Modify: `backend/requirements.txt`
- Create: `backend/src/rag/__init__.py`
- Create: `backend/src/rag/config.py`
- Create: `backend/tests/rag/__init__.py`
- Create: `backend/tests/rag/test_config.py`

- [ ] **Step 1: Write the failing test**

```python
# backend/tests/rag/test_config.py
from src.rag.config import init_llama_index
from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama

def test_init_llama_index():
    # Calling the init function should configure the global Settings
    init_llama_index()
    
    assert isinstance(Settings.embed_model, HuggingFaceEmbedding)
    assert Settings.embed_model.model_name == "BAAI/bge-small-en-v1.5"
    
    assert isinstance(Settings.llm, Ollama)
    assert Settings.llm.model == "llama3"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && .\venv\Scripts\activate && set PYTHONPATH=. && pytest tests/rag/test_config.py -v`
Expected: FAIL (ModuleNotFoundError)

- [ ] **Step 3: Update dependencies and write minimal implementation**

Modify `backend/requirements.txt`:
Append to the end of the file:
```text
llama-index-core
llama-index-embeddings-huggingface
llama-index-vector-stores-chroma
llama-index-llms-ollama
chromadb
```

```python
# backend/src/rag/config.py
from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama

def init_llama_index():
    """Initializes global LlamaIndex settings for embeddings and LLM."""
    # Use a lightweight local embedding model
    Settings.embed_model = HuggingFaceEmbedding(
        model_name="BAAI/bge-small-en-v1.5"
    )
    
    # Use local Ollama instance for the reader/generator
    Settings.llm = Ollama(model="llama3", request_timeout=60.0)
```

- [ ] **Step 4: Install dependencies and run test to verify it passes**

Run: `cd backend && .\venv\Scripts\activate && pip install -r requirements.txt && set PYTHONPATH=. && pytest tests/rag/test_config.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/requirements.txt backend/src/rag/ backend/tests/rag/
git commit -m "feat(rag): setup dependencies and llamaindex global config"
```

### Task 2: Implement Vector Store Setup (ChromaDB)

**Files:**
- Create: `backend/src/rag/vector_store.py`
- Create: `backend/tests/rag/test_vector_store.py`

- [ ] **Step 1: Write the failing test**

```python
# backend/tests/rag/test_vector_store.py
import os
import chromadb
from src.rag.vector_store import get_vector_store

def test_get_vector_store(tmp_path):
    db_path = os.path.join(tmp_path, "chroma")
    vector_store, chroma_client = get_vector_store(db_path, "test_collection")
    
    assert os.path.exists(db_path)
    assert chroma_client is not None
    # We test that it successfully creates/gets the collection
    collection = chroma_client.get_collection("test_collection")
    assert collection.name == "test_collection"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && .\venv\Scripts\activate && set PYTHONPATH=. && pytest tests/rag/test_vector_store.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# backend/src/rag/vector_store.py
import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore

def get_vector_store(persist_dir: str = "./data/chromadb", collection_name: str = "betwise_news"):
    """Initializes and returns a ChromaVectorStore and the underlying client."""
    db = chromadb.PersistentClient(path=persist_dir)
    chroma_collection = db.get_or_create_collection(collection_name)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    return vector_store, db
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && .\venv\Scripts\activate && set PYTHONPATH=. && pytest tests/rag/test_vector_store.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/src/rag/vector_store.py backend/tests/rag/test_vector_store.py
git commit -m "feat(rag): add local chromadb vector store setup"
```

### Task 3: Build the Indexing and Retrieval Pipeline

**Files:**
- Create: `backend/src/rag/pipeline.py`
- Create: `backend/tests/rag/test_pipeline.py`

- [ ] **Step 1: Write the failing test**

```python
# backend/tests/rag/test_pipeline.py
import os
from llama_index.core import Document
from src.rag.config import init_llama_index
from src.rag.pipeline import build_index, query_index

def test_build_and_query_index(tmp_path):
    init_llama_index()
    
    # 1. Create dummy documents
    doc1 = Document(text="Arsenal's star striker suffered a knee injury today.", metadata={"team": "Arsenal"})
    doc2 = Document(text="Chelsea won their last match 3-0.", metadata={"team": "Chelsea"})
    
    # 2. Build index in a temporary chromadb
    db_path = os.path.join(tmp_path, "chroma")
    index = build_index([doc1, doc2], persist_dir=db_path, collection_name="test_coll")
    
    assert index is not None
    
    # 3. Query the index (Using the retriever part only to avoid relying on Ollama running for unit tests)
    retriever = index.as_retriever(similarity_top_k=1)
    nodes = retriever.retrieve("Who got injured?")
    
    assert len(nodes) == 1
    assert "knee injury" in nodes[0].text
    assert nodes[0].metadata["team"] == "Arsenal"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && .\venv\Scripts\activate && set PYTHONPATH=. && pytest tests/rag/test_pipeline.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# backend/src/rag/pipeline.py
from typing import List
from llama_index.core import Document, VectorStoreIndex, StorageContext
from src.rag.vector_store import get_vector_store

def build_index(documents: List[Document], persist_dir: str = "./data/chromadb", collection_name: str = "betwise_news") -> VectorStoreIndex:
    """Builds a VectorStoreIndex from documents and stores it in ChromaDB."""
    vector_store, _ = get_vector_store(persist_dir, collection_name)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    # Create the index over the documents
    index = VectorStoreIndex.from_documents(
        documents, storage_context=storage_context
    )
    return index

def query_index(index: VectorStoreIndex, query_text: str) -> str:
    """Queries the index using the globally configured LLM (Ollama)."""
    query_engine = index.as_query_engine()
    response = query_engine.query(query_text)
    return str(response)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && .\venv\Scripts\activate && set PYTHONPATH=. && pytest tests/rag/test_pipeline.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/src/rag/pipeline.py backend/tests/rag/test_pipeline.py
git commit -m "feat(rag): implement indexing and querying pipeline using llamaindex"
```