from fastmcp import FastMCP
from fastapi import Request, HTTPException, requests
import httpx

mcp = FastMCP(
    name="Famvest MCP Server",
    instructions="""
        This server provides portfolio management application tools.
    """,
)

def verify_jwt(token):
    response = requests.get(
        "https://famvest.online/rest/v1/users/profile",
        headers={"Authorization": f"Bearer {token}"}
    )
    if response.status_code != 200:
        raise HTTPException(401)

    return response.json()

@mcp.middleware("http")
async def auth_middleware(request: Request, call_next):
    auth = request.headers.get("authorization")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")

    token = auth.replace("Bearer ", "")
    request.state.user = verify_jwt(token)
    return await call_next(request)

@mcp.tool()
async def get_holdings(request: Request):
    """
    Fetch user holdings.
    """
    url = "https://famvest.online/rest/v1/holdings"
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(
            url,
            headers={
                "Authorization": request.state.bearer_token,
                "Accept": "application/json"
            }
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text
        )

    return response.json()


if __name__ == "__main__":
    mcp.run(transport="http", port=8002)