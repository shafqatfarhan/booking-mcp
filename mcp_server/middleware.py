import logging

from fastmcp.server.middleware import Middleware, MiddlewareContext

logger = logging.getLogger(__name__)


class AuthMiddleware(Middleware):
    async def on_call_tool(self, context: MiddlewareContext, call_next):
        ctx = context.fastmcp_context
        logger.info("--- AuthMiddleware called ---")

        if ctx.request_context:
            # MCP session available - can access session-specific attributes
            logger.info(f"cls:AuthMiddleware - Request ID: {ctx.request_id}, session ID: {ctx.session_id}")

        # call_next is a callable; subscripting it raises "'method' object is not subscriptable"
        response = await call_next(context)
        logger.info(f"cls:AuthMiddleware - Response: {response.structured_content}")
        return response
