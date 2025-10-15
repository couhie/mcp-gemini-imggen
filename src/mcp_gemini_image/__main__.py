"""Entry point for the MCP server."""

from .server import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())
