import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from mcp.server.mcpserver import MCPServer

from tools.rag_tool import search_travel_knowledge as search_rag


server = MCPServer("Trip Advisor Travel Knowledge")


@server.tool(
    name="search_travel_knowledge",
    description="Search the indexed travel PDFs and return relevant passages with citations.",
)
def search_travel_knowledge(query: str, k: int = 5) -> str:
    return search_rag(query, k)


if __name__ == "__main__":
    server.run(transport="stdio")
