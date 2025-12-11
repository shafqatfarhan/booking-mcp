"""
Entry point for the Booking.com MCP server.

This module initializes and starts the FastMCP server, providing
API tools and endpoints to interact with Booking.com's APIs.
"""

from mcp_server import app, run_server 

if __name__ == "__main__":
    run_server()
