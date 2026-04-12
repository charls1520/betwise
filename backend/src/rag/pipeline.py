from typing import List
from llama_index.core import Document, VectorStoreIndex, StorageContext
from src.rag.vector_store import get_vector_store


def build_index(
    documents: List[Document],
    persist_dir: str = "./data/chromadb",
    collection_name: str = "betwise_news",
) -> VectorStoreIndex:
    """Builds a VectorStoreIndex from documents and stores it in ChromaDB."""
    vector_store, _ = get_vector_store(persist_dir, collection_name)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    # Create the index over the documents
    index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)
    return index


def query_index(index: VectorStoreIndex, query_text: str) -> str:
    """Queries the index using the globally configured LLM (Ollama)."""
    query_engine = index.as_query_engine()
    response = query_engine.query(query_text)
    return str(response)
