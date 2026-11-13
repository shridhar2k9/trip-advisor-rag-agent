import sys
from pathlib import Path

from mcp.client.stdio import StdioServerParameters, stdio_client
from strands.tools.mcp import MCPClient


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SERVER_SCRIPT = PROJECT_ROOT / "trip_mcp" / "servers" / "travel_knowledge_server.py"


def create_mcp_client() -> MCPClient:
    if not SERVER_SCRIPT.is_file():
        raise FileNotFoundError(f"MCP server script not found: {SERVER_SCRIPT}")

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[str(SERVER_SCRIPT)],
        cwd=str(PROJECT_ROOT),
    )
    return MCPClient(lambda: stdio_client(server_params))