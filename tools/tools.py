import httpx
from fastmcp.exceptions import ToolError
from fastmcp import Context

# -------------------------
# COMMON API HELPER
# -------------------------
async def make_api_call(ctx: Context, endpoint: str, method: str = "GET"):
    """
    Common helper function for making authenticated API calls to Famvest.

    Args:
        ctx: FastMCP context for state management
        endpoint: The API endpoint path (e.g., "/rest/v1/holdings")
        method: HTTP method (GET, POST, etc.)

    Returns:
        Parsed JSON response

    Raises:
        ToolError: If the API call fails
    """
    auth = ctx.get_state("authorization")

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
        Returns instructions for the user to complete the login process to allow mcp server to access user account data via API.
        """
        from fastmcp.server.dependencies import get_context

        ctx = get_context()
        session_id = ctx.session_id

        warning_message = """
        IMPORTANT: Please display this warning to the user before proceeding:
        ⚠️ WARNING: AI systems are unpredictable and non-deterministic. By continuing, you agree to interact with your Famvest account via AI at your own risk.
        """
        login_instructions = """
        Login to Famvest
        Please follow these steps:
        1. Click the login link below or open it in your browser
        2. Complete the login process with your Famvest credentials
        3. After successful login, return here and you can start using your account with Famvest
        """
        return {
            "warning": warning_message.strip(),
            "instructions": login_instructions.strip(),
            "login_url": f"https://famvest.online/login?source=mcp&session_id={session_id}",
            "note_for_llm": "Convert the login_url into a markdown link [Login to Famvest](url) to hide the session_id and source parameters from the user interface"
        }


    @mcp.tool()
    async def get_stock_holdings():
        """
        Retrieve current stock holdings from your Famvest portfolio.
        Returns a list of all stocks currently held in the account with quantity and value information.
        """
        from fastmcp.server.dependencies import get_context
        ctx = get_context()
        return await make_api_call(ctx, "/rest/v1/holdings?type=stocks")

    @mcp.tool()
    async def get_mutual_fund_holdings():
        """
        Retrieve current mutual fund holdings from your Famvest portfolio.
        Returns a list of all mutual funds currently held in the account with quantity and value information.
        """
        from fastmcp.server.dependencies import get_context
        ctx = get_context()
        return await make_api_call(ctx, "/rest/v1/holdings?type=mf")

    @mcp.tool()
    async def get_positions():
        """
        Retrieve current positions and open trades from your Famvest account.
        Returns information about active positions including entry price, current price, and profit/loss.
        """
        from fastmcp.server.dependencies import get_context
        ctx = get_context()
        return await make_api_call(ctx, "/rest/v1/positions")

    @mcp.tool()
    async def check_health():
        """
        Check Famvest application health and status.
        Returns health information about the Famvest service.
        """
        from fastmcp.server.dependencies import get_context
        ctx = get_context()
        return await make_api_call(ctx, "/rest/v1/health")

    @mcp.tool()
    async def get_orders():
        """
        List recent orders and their status from your Famvest account.
        Returns a list of all recent orders with details including status and execution information.
        """
        from fastmcp.server.dependencies import get_context
        ctx = get_context()
        return await make_api_call(ctx, "/rest/v1/orders")

    @mcp.tool()
    async def get_mf_orders():
        """
        List mutual fund orders from your Famvest account.
        Returns a list of all mutual fund orders with their current status.
        """
        from fastmcp.server.dependencies import get_context
        ctx = get_context()
        return await make_api_call(ctx, "/rest/v1/mf/orders")

    @mcp.tool()
    async def get_mf_sips():
        """
        Get mutual fund SIPs (Systematic Investment Plans) from your Famvest account.
        Returns a list of all active and past SIP investments with details.
        """
        from fastmcp.server.dependencies import get_context
        ctx = get_context()
        return await make_api_call(ctx, "/rest/v1/mf/sips")

    @mcp.tool()
    async def get_gainers_losers(timeframe: str = "3M"):
        """
        Identify top gainers and losers in your portfolio for a specific timeframe.

        Args:
            timeframe: Time period for analysis (1D, 1W, 1M, 3M, 6M, 1Y). Defaults to 3M.

        Returns:
            List of top performing and underperforming holdings within the specified timeframe.
        """
        from fastmcp.server.dependencies import get_context
        ctx = get_context()
        return await make_api_call(ctx, f"/rest/v1/holdings/gainers-losers?timeframe={timeframe}")

    @mcp.tool()
    async def get_funds():
        """
        Retrieve available funds and account balances from your Famvest account.
        Returns information about total funds, available balance, and utilization.
        """
        from fastmcp.server.dependencies import get_context
        ctx = get_context()
        return await make_api_call(ctx, "/rest/v1/funds")

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
        from fastmcp.server.dependencies import get_context
        ctx = get_context()
        params = []
        if tradingSymbol:
            params.append(f"tradingSymbol={tradingSymbol}")
        if instrumentToken > 0:
            params.append(f"instrumentToken={instrumentToken}")
        if exchange:
            params.append(f"exchange={exchange}")

        query = f"?{'&'.join(params)}" if params else ""
        return await make_api_call(ctx, f"/rest/v1/instruments{query}")

    @mcp.tool()
    async def get_account_profiles():
        """
        List linked trading accounts associated with your Famvest profile.
        Returns information about all connected trading accounts.
        """
        from fastmcp.server.dependencies import get_context
        ctx = get_context()
        return await make_api_call(ctx, "/rest/v1/accounts/profiles")

    @mcp.tool()
    async def get_user_profile():
        """
        Get your logged-in user profile information from Famvest.
        Returns personal details, preferences, and account settings for the authenticated user.
        """
        from fastmcp.server.dependencies import get_context
        ctx = get_context()
        return await make_api_call(ctx, "/rest/v1/users/profile")

    @mcp.tool()
    async def get_market_timings(date: str = ""):
        """
        Get market timings for a specific date.

        Args:
            date: Date for which to retrieve market timings (optional)

        Returns:
            Market open and close timings for the specified or current date.
        """
        from fastmcp.server.dependencies import get_context
        ctx = get_context()
        query = f"?date={date}" if date else ""
        return await make_api_call(ctx, f"/rest/v1/market/timings{query}")

    @mcp.tool()
    async def get_market_holidays():
        """
        Get a list of market holidays.
        Returns all upcoming and historical market holidays for trading schedule planning.
        """
        from fastmcp.server.dependencies import get_context
        ctx = get_context()
        return await make_api_call(ctx, "/rest/v1/market/holidays")

    @mcp.tool()
    async def get_schedulers():
        """
        Admin API - Get schedulers with status and last execution time.
        Returns information about all scheduled jobs including their status and execution history.
        """
        from fastmcp.server.dependencies import get_context
        ctx = get_context()
        return await make_api_call(ctx, "/rest/v1/admin/schedulers")

    @mcp.tool()
    async def get_all_application_users():
        """
        Admin API - Get all application users.
        Returns a list of all users in the Famvest application with their details.
        """
        from fastmcp.server.dependencies import get_context
        ctx = get_context()
        return await make_api_call(ctx, "/rest/v1/admin/users")

    @mcp.tool()
    async def get_ipos():
        """
        Get IPOs (Initial Public Offerings) - both closed and open.
        Returns a list of all IPOs with their status, details, and dates.
        """
        from fastmcp.server.dependencies import get_context
        ctx = get_context()
        return await make_api_call(ctx, "/rest/v1/ipos")

    @mcp.tool()
    async def get_ipo_applications():
        """
        Get your IPO applications and their status.
        Returns a list of all IPO applications you have submitted with current status.
        """
        from fastmcp.server.dependencies import get_context
        ctx = get_context()
        return await make_api_call(ctx, "/rest/v1/ipos/applications")
