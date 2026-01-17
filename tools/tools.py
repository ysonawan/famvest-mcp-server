import httpx
from fastmcp.exceptions import ToolError
from fastmcp.server.dependencies import get_http_headers

# -------------------------
# MCP TOOLS SETUP
# -------------------------
def setup_tools(mcp):
    """Register all tools with the MCP server"""

    @mcp.tool()
    async def login():
        """
        Login to Famvest and obtain JWT token for API access.
        Returns instructions for the user to complete the login process.
        """
        warning_message = """
⚠️ WARNING: AI systems are unpredictable and non-deterministic. By continuing, you agree to interact with your Zerodha account via AI at your own risk.
        """

        login_instructions = """
Login to Famvest

Please follow these steps:
1. Open this URL in your browser: https://famvest.online/login
2. Complete the login process with your credentials
3. After successful login, you will receive a JWT token
4. Add the token to the MCP server header with the following format:
   Authorization: Bearer <JWT>

Example:
   Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
        """

        return {
            "warning": warning_message.strip(),
            "instructions": login_instructions.strip(),
            "login_url": "https://famvest.online/login"
        }


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