from fastmcp.server.dependencies import get_http_headers
from fastmcp.server.middleware import Middleware, MiddlewareContext
from fastmcp.exceptions import ToolError

class BearerAuthMiddleware(Middleware):
    async def on_call_tool(self, context: MiddlewareContext, call_next):
        headers = get_http_headers()

        auth = headers.get("authorization")
        if not auth or not auth.startswith("Bearer "):
            raise ToolError("Unauthorized")

        # Continue to tool
        return await call_next(context)