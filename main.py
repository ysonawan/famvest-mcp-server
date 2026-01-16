import logging
from fastmcp import FastMCP

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

mcp = FastMCP("My MCP Server")

@mcp.tool
def greet(name: str) -> str:
    return f"Hello, {name}!"

if __name__ == "__main__":
    try:
        logger.info("Starting MCP server on port 8002 with streamable-http transport")
        mcp.run(transport="streamable-http", port=8002)
    except KeyboardInterrupt:
        logger.info("MCP server interrupted by user")
    except Exception as e:
        logger.critical("MCP server encountered a critical error", exc_info=True)
        raise