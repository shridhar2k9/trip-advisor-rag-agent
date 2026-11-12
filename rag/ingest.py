import argparse
import hashlib
from pathlib import Path

import chromadb
from pypdf import PdfReader

from rag.retriever import CHROMA_DIR, COLLECTION_NAME


# Resolve the default PDF folder from this file so the CLI works from any cwd.
DEFAULT_PDF_DIR = Path(__file__).resolve().parents[1] / "data"


def chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 150) -> list[str]:
    """Split extracted text into bounded, overlapping chunks for embedding."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")
    if chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be non-negative and smaller than chunk_size")

    # PDF extraction often adds irregular whitespace; normalize it before splitting.
    text = " ".join(text.split())
    chunks: list[str] = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))
        if end < len(text):
            # Prefer a word boundary when possible so chunks remain readable.
            boundary = text.rfind(" ", start, end)
            if boundary > start:
                end = boundary

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break
        # Carry part of the previous chunk forward to retain context at boundaries.
        start = max(start + 1, end - chunk_overlap)

    return chunks


def read_pdf_chunks(
    pdf_path: Path,
    chunk_size: int = 1000,
    chunk_overlap: int = 150,
) -> tuple[list[str], list[dict[str, str | int]], list[str]]:
    """Extract page-wise chunks and source metadata from one PDF."""
    documents: list[str] = []
    metadatas: list[dict[str, str | int]] = []
    ids: list[str] = []
    reader = PdfReader(str(pdf_path))

    for page_number, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text() or ""
        for chunk_number, chunk in enumerate(
            chunk_text(page_text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        ):
            chunk_id = hashlib.sha256(
                f"{pdf_path.name}:{page_number}:{chunk_number}".encode("utf-8")
            ).hexdigest()
            documents.append(chunk)
                # Preserve page references so retrieved text can be cited to its PDF.
            metadatas.append(
                {"source": pdf_path.name, "page": page_number, "chunk": chunk_number}
            )
            ids.append(chunk_id)

    return documents, metadatas, ids


def ingest_pdfs(
    pdf_dir: Path = DEFAULT_PDF_DIR,
    chunk_size: int = 1000,
    chunk_overlap: int = 150,
) -> int:
    """Rebuild the persistent Chroma collection from PDFs in ``pdf_dir``."""
    if not pdf_dir.is_dir():
        raise FileNotFoundError(f"PDF directory does not exist: {pdf_dir}")

    pdf_files = sorted(pdf_dir.glob("*.pdf"))
    if not pdf_files:
        raise FileNotFoundError(f"No PDF files found in: {pdf_dir}")

    documents: list[str] = []
    metadatas: list[dict[str, str | int]] = []
    ids: list[str] = []
    for pdf_path in pdf_files:
        pdf_documents, pdf_metadatas, pdf_ids = read_pdf_chunks(
            pdf_path, chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )
        documents.extend(pdf_documents)
        metadatas.extend(pdf_metadatas)
        ids.extend(pdf_ids)

    if not documents:
        raise ValueError(f"No extractable text found in PDFs under: {pdf_dir}")

    # Chroma persists its SQLite metadata and vector indexes under this directory.
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    try:
        # Rebuilding removes stale chunks when PDFs are changed or removed.
        client.delete_collection(COLLECTION_NAME)
    except chromadb.errors.NotFoundError:
        pass

    collection = client.create_collection(COLLECTION_NAME)
    batch_size = 200
    for start in range(0, len(documents), batch_size):
        end = start + batch_size
        # Supplying documents lets the collection's embedding function vectorize them.
        collection.add(
            ids=ids[start:end],
            documents=documents[start:end],
            metadatas=metadatas[start:end],
        )

    return len(documents)


def main() -> None:
    """Parse ingestion options and index the requested PDF folder."""
    parser = argparse.ArgumentParser(description="Index travel PDFs into ChromaDB.")
    parser.add_argument("--pdf-dir", type=Path, default=DEFAULT_PDF_DIR)
    parser.add_argument("--chunk-size", type=int, default=1000)
    parser.add_argument("--chunk-overlap", type=int, default=150)
    args = parser.parse_args()

    count = ingest_pdfs(
        pdf_dir=args.pdf_dir,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
    )
    print(f"Indexed {count} chunks from {args.pdf_dir} into {CHROMA_DIR}.")


if __name__ == "__main__":
    main()
