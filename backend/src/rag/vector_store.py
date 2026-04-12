import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore


def get_vector_store(
    persist_dir: str = "./data/chromadb", collection_name: str = "betwise_news"
):
    """Initializes and returns a ChromaVectorStore and the underlying client."""
    db = chromadb.PersistentClient(path=persist_dir)
    chroma_collection = db.get_or_create_collection(collection_name)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    return vector_store, db
