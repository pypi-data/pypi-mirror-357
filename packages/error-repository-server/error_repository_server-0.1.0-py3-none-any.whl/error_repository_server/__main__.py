"""
Main entry point for the Error Repository MCP Server
"""

from .server import main

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
