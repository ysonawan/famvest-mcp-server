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
    async def get_stock_holdings():
        """
        Retrieve current stock holdings from your Famvest portfolio.
        Returns a list of all stocks currently held in the account with quantity and value information.
        """
        return await make_api_call("/rest/v1/holdings?type=stocks")

    @mcp.tool()
    async def get_mutual_fund_holdings():
        """
        Retrieve current mutual fund holdings from your Famvest portfolio.
        Returns a list of all mutual funds currently held in the account with quantity and value information.
        """
        return await make_api_call("/rest/v1/holdings?type=mf")

    @mcp.tool()
    async def get_positions():
        """
        Retrieve current positions and open trades from your Famvest account.
        Returns information about active positions including entry price, current price, and profit/loss.
        """
        return await make_api_call("/rest/v1/positions")

    @mcp.tool()
    async def check_health():
        """
        Check Famvest application health and status.
        Returns health information about the Famvest service.
        """
        return await make_api_call("/rest/v1/health")

    @mcp.tool()
    async def get_orders():
        """
        List recent orders and their status from your Famvest account.
        Returns a list of all recent orders with details including status and execution information.
        """
        return await make_api_call("/rest/v1/orders")

    @mcp.tool()
    async def get_mf_orders():
        """
        List mutual fund orders from your Famvest account.
        Returns a list of all mutual fund orders with their current status.
        """
        return await make_api_call("/rest/v1/mf/orders")

    @mcp.tool()
    async def get_mf_sips():
        """
        Get mutual fund SIPs (Systematic Investment Plans) from your Famvest account.
        Returns a list of all active and past SIP investments with details.
        """
        return await make_api_call("/rest/v1/mf/sips")

    @mcp.tool()
    async def get_gainers_losers(timeframe: str = "3M"):
        """
        Identify top gainers and losers in your portfolio for a specific timeframe.

        Args:
            timeframe: Time period for analysis (1D, 1W, 1M, 3M, 6M, 1Y). Defaults to 3M.

        Returns:
            List of top performing and underperforming holdings within the specified timeframe.
        """
        return await make_api_call(f"/rest/v1/holdings/gainers-losers?timeframe={timeframe}")

    @mcp.tool()
    async def get_funds():
        """
        Retrieve available funds and account balances from your Famvest account.
        Returns information about total funds, available balance, and utilization.
        """
        return await make_api_call("/rest/v1/funds")

    @mcp.tool()
    async def search_instruments(tradingSymbol: str = "", instrumentToken: int = 0, exchange: str = ""):
        """
        Search for trading instruments by trading symbol, instrument token, or exchange.

        Args:
            tradingSymbol: Search by trading symbol (e.g., "RELIANCE")
            instrumentToken: Search by instrument token (numeric identifier)
            exchange: Filter by exchange (e.g., "NSE", "BSE")

        Returns:
            List of matching trading instruments with details like name, type, and exchange.
        """
        params = []
        if tradingSymbol:
            params.append(f"tradingSymbol={tradingSymbol}")
        if instrumentToken > 0:
            params.append(f"instrumentToken={instrumentToken}")
        if exchange:
            params.append(f"exchange={exchange}")

        query = f"?{'&'.join(params)}" if params else ""
        return await make_api_call(f"/rest/v1/instruments{query}")

    @mcp.tool()
    async def get_account_profiles():
        """
        List linked trading accounts associated with your Famvest profile.
        Returns information about all connected trading accounts.
        """
        return await make_api_call("/rest/v1/accounts/profiles")

    @mcp.tool()
    async def get_user_profile():
        """
        Get your logged-in user profile information from Famvest.
        Returns personal details, preferences, and account settings for the authenticated user.
        """
        return await make_api_call("/rest/v1/users/profile")

    @mcp.tool()
    async def get_market_timings(date: str = ""):
        """
        Get market timings for a specific date.

        Args:
            date: Date for which to retrieve market timings (optional)

        Returns:
            Market open and close timings for the specified or current date.
        """
        query = f"?date={date}" if date else ""
        return await make_api_call(f"/rest/v1/market/timings{query}")

    @mcp.tool()
    async def get_market_holidays():
        """
        Get a list of market holidays.
        Returns all upcoming and historical market holidays for trading schedule planning.
        """
        return await make_api_call("/rest/v1/market/holidays")

    @mcp.tool()
    async def get_schedulers():
        """
        Admin API - Get schedulers with status and last execution time.
        Returns information about all scheduled jobs including their status and execution history.
        """
        return await make_api_call("/rest/v1/admin/schedulers")

    @mcp.tool()
    async def get_all_application_users():
        """
        Admin API - Get all application users.
        Returns a list of all users in the Famvest application with their details.
        """
        return await make_api_call("/rest/v1/admin/users")

    @mcp.tool()
    async def get_ipos():
        """
        Get IPOs (Initial Public Offerings) - both closed and open.
        Returns a list of all IPOs with their status, details, and dates.
        """
        return await make_api_call("/rest/v1/ipos")

    @mcp.tool()
    async def get_ipo_applications():
        """
        Get your IPO applications and their status.
        Returns a list of all IPO applications you have submitted with current status.
        """
        return await make_api_call("/rest/v1/ipos/applications")
