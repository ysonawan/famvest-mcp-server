from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
import httpx
from fastmcp.server.dependencies import get_http_headers
from fastmcp.server.middleware import MiddlewareContext

from middleware.auth import BearerAuthMiddleware

mcp = FastMCP(
    name="Famvest MCP Server",
    instructions="""
        This server provides portfolio management application tools.
    """,
)

mcp.add_middleware(BearerAuthMiddleware())

@mcp.tool()
async def get_holdings():
    headers = get_http_headers()
    auth = headers.get("authorization")
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(
            "https://famvest.online/rest/v1/holdings",
            headers={
                "Authorization": auth,
                "Accept": "application/json",
            },
        )

    if response.status_code != 200:
        raise ToolError(response.text)

    return response.json()


if __name__ == "__main__":
    mcp.run(transport="http", port=8002)