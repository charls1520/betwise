import os
from llama_index.core import Document
from src.rag.config import init_llama_index
from src.rag.pipeline import build_index, query_index


def test_build_and_query_index(tmp_path):
    init_llama_index()

    # 1. Create dummy documents
    doc1 = Document(
        text="Arsenal's star striker suffered a knee injury today.",
        metadata={"team": "Arsenal"},
    )
    doc2 = Document(
        text="Chelsea won their last match 3-0.", metadata={"team": "Chelsea"}
    )

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
