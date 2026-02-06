from fastmcp.server.middleware import Middleware, MiddlewareContext

class OnRequestMiddleware(Middleware):
    async def on_request(self, context: MiddlewareContext, call_next):
        ctx = context.fastmcp_context
        if ctx.request_context:
            # MCP session available
            session_id = ctx.session_id
            request_id = ctx.request_id
            print(f"OnRequestMiddleware - Session ID: {session_id}, Request ID: {request_id}")

            # Store for session id for downstream tools/middlewares to use
            ctx.set_state("session_id", session_id)
        else:
            # Session not yet established (e.g., during initialization)
            print("OnRequestMiddleware - No session context available, skipping")

        # Continue
        return await call_next(context)