# Ken-MCP Commands

## Installation
Add ken-mcp server to Claude Code:
```bash
claude mcp add ken-mcp python3.10 server.py
```

## Development
Test the server directly:
```bash
python3.10 server.py
```

Install project dependencies:
```bash
python3.10 -m pip install -e .
```

## Generator Updates
The MCP generator has been enhanced to:
- Remove hardcoded templates and predefined patterns
- Use AI-powered requirement analysis (with fallback)
- Generate custom tool implementations based on user needs
- Support web scraping, API calls, data processing, and generic tools
- Create actual functional code instead of generic placeholders

## Generated MCP Servers
Web scraper MCP location:
```bash
/Users/kenkai/mcp_generated_servers/web-scraper-mcp
```

Add generated servers to Claude Code:
```bash
claude mcp add web-scraper-mcp python3.10 /Users/kenkai/mcp_generated_servers/web-scraper-mcp/server.py
```