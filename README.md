# trip-advisor-rag-agent

## Python environment

Use Python 3.14 on Windows for this project. The current dependency set includes
`zstandard` through LangSmith; on Python 3.15, pip may try to build it from
source and require Microsoft C++ Build Tools.

If `.venv` was created with Python 3.15, recreate it with Python 3.14:

```powershell
Remove-Item -Recurse -Force .venv
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

In VS Code, select `.venv\Scripts\python.exe` as the workspace interpreter.
The repository pins the recommended Python version in `.python-version`.

## Travel PDF knowledge base

Install the project dependencies, then index the PDFs in `data`:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m rag.ingest
```

Ingestion extracts text from each PDF, creates overlapping 1,000-character chunks,
and stores them in the `travel_documents` Chroma collection under `rag/chroma_db`.
Chroma uses SQLite for metadata and local files for vector indexes; no separate
SQLite server is needed. Running ingestion again rebuilds the collection from the
PDFs in the selected directory.
The first run downloads Chroma's default embedding model; PDF content and queries
remain in the local Chroma database.

The travel agent's `search_travel_knowledge` tool retrieves relevant chunks and
includes the PDF filename and page number as source information. Its `k` argument
sets the maximum number of matching chunks (default `5`, capped by the collection
size). To index another directory, pass `--pdf-dir "D:\path\to\pdfs"`; chunk sizes
can be changed with `--chunk-size` and `--chunk-overlap`.