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
