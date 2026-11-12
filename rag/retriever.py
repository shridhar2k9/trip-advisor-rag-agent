from pathlib import Path

import chromadb


# Keep retrieval pointed at the same persistent store used by ingestion.
CHROMA_DIR = Path(__file__).resolve().parent / "chroma_db"
COLLECTION_NAME = "travel_documents"


def retrieve_documents(query: str, k: int = 5) -> list[dict[str, str | int]]:
    """Return up to ``k`` nearest chunks with their source citation metadata."""
    query = query.strip()
    if not query:
        raise ValueError("query must not be empty")
    if not isinstance(k, int) or isinstance(k, bool) or k <= 0:
        raise ValueError("k must be a positive integer")

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = client.get_or_create_collection(COLLECTION_NAME)
    # Avoid querying an uninitialized or newly created empty knowledge base.
    if collection.count() == 0:
        return []

    # Chroma embeds the query with the collection's embedding function and ranks
    # stored vectors; cap k to the number of indexed chunks.
    results = collection.query(
        query_texts=[query],
        n_results=min(k, collection.count()),
        include=["documents", "metadatas"],
    )
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    # Pair each retrieved passage with its PDF filename and page for citations.
    return [
        {
            "text": text,
            "source": metadata["source"],
            "page": metadata["page"],
        }
        for text, metadata in zip(documents, metadatas)
        if text is not None and metadata is not None
    ]
