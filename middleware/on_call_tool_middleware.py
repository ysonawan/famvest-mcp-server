import httpx
from fastmcp.server.middleware import Middleware, MiddlewareContext
from fastmcp.exceptions import ToolError

class OnCallToolMiddleware(Middleware):
    async def on_call_tool(self, context: MiddlewareContext, call_next):
        # Skip authentication for login tool
        if context.message.name == "login":
            return await call_next(context)

        ctx = context.fastmcp_context
        session_id = ctx.get_state("session_id")
        if session_id:
            print(f"OnCallToolMiddleware - Retrieved session ID from state: {session_id}")
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"https://famvest.upvaly.com/rest/auth/mcp/token?session_id={session_id}"
                    )
                    print("OnCallToolMiddleware - Response status code:", response.status_code)

                    if response.status_code != 200:
                        raise ToolError("Please log in first using the login tool.")

                    data = response.json()
                    token = data.get("token")
                    print(f"Token successfully retrieved for session {session_id}")
                    # Store for token for downstream tools to use
                    ctx.set_state("authorization", f"Bearer {token}")
            except httpx.HTTPError as e:
                raise ToolError(f"Failed to fetch authentication token: {str(e)}")
            except Exception as e:
                raise ToolError(f"Unexpected error while fetching authentication token: {str(e)}")
        else:
            print("OnCallToolMiddleware - No session ID found in state")

        # Continue to tool
        return await call_next(context)