"""Entry point for Directory MCP server."""
import sys
import os

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from .server import run_server

def main():
    """Main entry point."""
    # Run the MCP server directly
    # Configuration checking is now handled in server.py
    run_server()

if __name__ == "__main__":
    main()