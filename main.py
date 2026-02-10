from fastmcp import FastMCP

from middleware.on_call_tool_middleware import OnCallToolMiddleware
from middleware.on_request_middleware import OnRequestMiddleware
from tools.tools import setup_tools

mcp = FastMCP(
    name="Famvest MCP Server",
    instructions="""
        This server provides portfolio management application tools.
    """,
)

mcp.add_middleware(OnRequestMiddleware())
mcp.add_middleware(OnCallToolMiddleware())

setup_tools(mcp)

if __name__ == "__main__":
    mcp.run(transport="http", port=8003)