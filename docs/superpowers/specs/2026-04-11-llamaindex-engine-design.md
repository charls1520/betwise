# LlamaIndex RAG Engine Design

## 1. Overview
This spec covers the **Retrieval-Augmented Generation (RAG) Engine** using LlamaIndex for BetWise.
The goal is to index unstructured text (news, injury reports, manager quotes) so the AI can provide context-aware answers to user queries regarding Premier League matches.

## 2. Architecture & Components
We will use a completely local and free stack for the initial version to minimize costs and simplify the setup.

### 2.1 Embedding Model (Local)
* **Model:** `BAAI/bge-small-en-v1.5` (or similar lightweight open-source model via HuggingFace).
* **Execution:** Runs locally within the FastAPI backend using the `llama-index-embeddings-huggingface` integration. This avoids API costs for indexing.

### 2.2 Vector Database (Local)
* **Database:** **ChromaDB** running in embedded/ephemeral mode.
* **Storage:** Vectors and metadata will be saved locally to disk (e.g., `data/chromadb/`).
* **Integration:** Handled via the `llama-index-vector-stores-chroma` plugin.

### 2.3 Document Ingestion Pipeline
* Documents (e.g., scraped news JSONs from the Data Lake) will be loaded using LlamaIndex `SimpleDirectoryReader` or custom Document loaders.
* Nodes/Chunks will be tagged with rich metadata (e.g., `team_canonical: Arsenal`, `date: 2026-04-11`, `topic: injury`) to allow for hybrid search (Vector + Metadata filtering) in the future.

### 2.4 Query Engine & LLM (Local)
* The actual LLM (the "Reader") that synthesizes the retrieved chunks into a human-readable answer will run locally via **Ollama**.
* This enables self-hosting of models like `Llama 3`, `Mistral`, or `Phi-3` completely free and privately.
* The architecture uses `llama-index-llms-ollama` to connect LlamaIndex with the local Ollama instance.
* For the initial implementation plan, we will focus on building the **Indexing and Retrieval** pipeline connected to a local Ollama model to generate real context-aware answers.

## 3. Tech Stack Requirements
* `llama-index-core`
* `llama-index-embeddings-huggingface` (for BAAI models)
* `llama-index-vector-stores-chroma`
* `llama-index-llms-ollama` (for local LLM synthesis)
* `chromadb`
* `transformers` and `torch` (required by HuggingFace embeddings)