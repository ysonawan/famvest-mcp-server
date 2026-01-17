import httpx
from fastmcp.exceptions import ToolError
from fastmcp.server.dependencies import get_http_headers

# -------------------------
# COMMON API HELPER
# -------------------------
async def make_api_call(endpoint: str, method: str = "GET"):
    """
    Common helper function for making authenticated API calls to Famvest.

    Args:
        endpoint: The API endpoint path (e.g., "/rest/v1/holdings")
        method: HTTP method (GET, POST, etc.)

    Returns:
        Parsed JSON response

    Raises:
        ToolError: If the API call fails
    """
    headers = get_http_headers()
    auth = headers.get("authorization")

    async with httpx.AsyncClient(timeout=10) as client:
        url = f"https://famvest.online{endpoint}"

        if method == "GET":
            response = await client.get(
                url,
                headers={
                    "Authorization": auth,
                    "Accept": "application/json",
                },
            )
        else:
            raise ToolError(f"Unsupported HTTP method: {method}")

        if response.status_code != 200:
            raise ToolError(response.text)

        return response.json()

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
        IMPORTANT: Please display this warning to the user before proceeding:
        ⚠️ WARNING: AI systems are unpredictable and non-deterministic. By continuing, you agree to interact with your Famvest account via AI at your own risk.
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
        """
        Retrieve current holdings from your Famvest portfolio.
        Returns a list of all securities currently held in the account with quantity and value information.
        """
        return await make_api_call("/rest/v1/holdings")

    @mcp.tool()
    async def get_positions():
        """
        Retrieve current positions and open trades from your Famvest account.
        Returns information about active positions including entry price, current price, and profit/loss.
        """
        return await make_api_call("/rest/v1/positions")
