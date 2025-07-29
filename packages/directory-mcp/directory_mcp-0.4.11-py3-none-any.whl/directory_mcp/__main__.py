"""Entry point for Directory MCP server."""
import asyncio
import sys
import os

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from .config import Config
from .server import run_server

def main():
    """Main entry point."""
    # Check configuration
    config = Config()
    
    # Prompt for API key if needed (only in interactive mode)
    if not config.is_configured:
        if sys.stdin.isatty():
            api_key = config.prompt_for_api_key()
            if not api_key:
                print("❌ API key is required to run Directory MCP")
                sys.exit(1)
        else:
            print("❌ GEMINI_API_KEY environment variable is required")
            print("Set it with: export GEMINI_API_KEY=your_api_key_here")
            sys.exit(1)
    
    # Run the MCP server
    try:
        run_server()
    except KeyboardInterrupt:
        print("\n👋 Directory MCP stopped")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()