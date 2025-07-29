"""Entry point for Directory MCP server."""
import asyncio
import sys
from .config import Config
from .server import run_server

def main():
    """Main entry point."""
    # Check configuration
    config = Config()
    
    # Prompt for API key if needed
    if not config.is_configured:
        api_key = config.prompt_for_api_key()
        if not api_key:
            print("❌ API key is required to run Directory MCP")
            sys.exit(1)
    
    # Run the MCP server
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        print("\n👋 Directory MCP stopped")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()