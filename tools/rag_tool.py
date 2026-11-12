from rag.retriever import retrieve_documents
from strands import tool


@tool
def search_travel_knowledge(query: str, k: int = 5) -> str:
    """Search the indexed travel PDFs and return up to k chunks with citations."""
    results = retrieve_documents(query, k=k)
    if not results:
        return "The travel PDF knowledge base is empty. Run `python -m rag.ingest` to index the PDFs."

    # Format citations alongside each passage so the agent can ground its answer.
    return "\n\n".join(
        f"Source: {result['source']}, page {result['page']}\n{result['text']}"
        for result in results
    )
