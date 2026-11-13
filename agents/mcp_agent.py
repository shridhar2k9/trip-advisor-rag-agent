from strands.types.content import Message

from agents.travel_agent import create_travel_agent
from tools.rag_tool import search_travel_knowledge
from tools.registry import TOOLS
from trip_mcp.client import create_mcp_client


def run_mcp_agent(
    prompt: str,
    messages: list[Message] | None = None,
) -> str:
    with create_mcp_client() as client:
        mcp_tools = client.list_tools_sync()
        if not mcp_tools:
            raise RuntimeError("The travel MCP server did not provide any tools.")

        local_tools = [tool for tool in TOOLS if tool is not search_travel_knowledge]
        agent = create_travel_agent(
            messages=messages,
            tools=[*local_tools, *mcp_tools],
        )
        return str(agent(prompt))