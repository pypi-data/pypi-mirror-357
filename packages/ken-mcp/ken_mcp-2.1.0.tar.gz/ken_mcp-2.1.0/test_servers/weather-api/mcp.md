# weather-api MCP Documentation

## Overview
MCP server for: Build an MCP that interfaces with weather APIs to provide weather information. It should fetch curre...

## Implementation Status: BOILERPLATE

This is a boilerplate MCP server that requires implementation by Claude.

### Original Requirements
```
Build an MCP that interfaces with weather APIs to provide weather information. It should fetch current weather, forecasts, weather alerts, and historical weather data. The MCP should support multiple locations, different units (metric/imperial), and provide weather-based recommendations. Include functionality to cache API responses and handle rate limiting gracefully.
```

### Current Status
- ✅ Basic structure generated
- ⚠️  Tool implementations are placeholders
- ⚠️  Resources need actual data sources
- ⚠️  Prompts need customization
- ❌ Not ready for production use

### Architecture
- Built with FastMCP framework
- Provides 3 placeholder tools
- Includes 3 placeholder resources
- Offers 2 placeholder prompt templates

### Implementation Guide for Claude

1. **Tools**: Each tool has a TODO comment explaining what needs to be implemented
2. **Resources**: Update to expose actual data based on requirements
3. **Prompts**: Customize to generate appropriate messages
4. **Dependencies**: Add any required packages to pyproject.toml

### Error Handling
- All tools use ToolError for user-facing errors
- TODO: Add specific validation based on requirements
- TODO: Handle edge cases specific to the use case

### Testing
Test each tool using the MCP Inspector:
```bash
npx @modelcontextprotocol/inspector python server.py
```

Note: Tools will return "not_implemented" status until Claude completes the implementation.

---
Generated on 2025-06-25 14:10:41
