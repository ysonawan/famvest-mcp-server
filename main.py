from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
import httpx
from fastmcp.server.dependencies import get_http_headers
from fastmcp.server.middleware import MiddlewareContext

from middleware.auth import BearerAuthMiddleware
from tools.tools import setup_tools

mcp = FastMCP(
    name="Famvest MCP Server",
    instructions="""
        This server provides portfolio management application tools.
    """,
)

mcp.add_middleware(BearerAuthMiddleware())

setup_tools(mcp)


if __name__ == "__main__":
    mcp.run(transport="http", port=8002)