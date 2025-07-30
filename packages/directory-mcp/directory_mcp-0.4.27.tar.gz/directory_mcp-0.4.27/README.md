# Directory MCP

A complete knowledge graph for your people, companies, channels, and projects.

## Features

- 🧠 **Smart Understanding**: Gemini embeddings understand "backend team Discord" or "John from Anthropic"
- 🔗 **Rich Relationships**: Track who works where, who's on what project, who's in which channels
- 🚀 **Zero Setup**: SQLite database created automatically
- 🔄 **Auto Updates**: Always get the latest version with `uvx`
- 🎯 **Powerful Queries**: Find connections, traverse relationships, discover patterns

## Quick Start

```bash
# Run it!
uvx directory-mcp

# First run prompts for Gemini API key (get free at https://makersuite.google.com/app/apikey)
# Configure Claude Code and restart
```

## Installation

```bash
# Install via pip
pip install directory-mcp

# Or run directly with uvx
uvx directory-mcp

# Configure in Claude Code
# Add to ~/.claude.json:
{
  "mcpServers": {
    "directory": {
      "type": "stdio",
      "command": "uvx",
      "args": ["directory-mcp"],
      "env": {
        "GEMINI_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

## Example Usage

### Creating Entities
```
"Create John Doe who works as Senior Engineer at Anthropic, email john@anthropic.com, discord john#1234"
"Create a Slack channel called #backend-team for Anthropic's backend project"
"Add John to the #backend-team channel as an admin"
```

### Finding People
```
"Find all Python developers at Anthropic"
"Who's on the AI safety project?"
"Find people in the London office"
"Who works with Sarah on any projects?"
```

### Finding Channels
```
"What's the Discord channel for the frontend team?"
"Find all project channels for the Q1 launch"
"Show me all the Slack channels John is in"
```

### Understanding Relationships
```
"How are John and Sarah connected?"
"Show me John's full network"
"Who's on the backend team and what channels are they in?"
"Find all channels and people for the AI safety project"
```

## Development

```bash
# Clone the repository
git clone https://github.com/markov-ai/directory-mcp.git
cd directory-mcp

# Install in development mode
pip install -e .

# Run tests
pytest tests/
```

## License

MIT License - see LICENSE file for details