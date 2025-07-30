#!/opt/homebrew/bin/python3.10
"""Test KEN-MCP tools directly"""

import asyncio
from mcp_generator import mcp

async def test_tools():
    """Test if tools are accessible"""
    print("Testing KEN-MCP tools...")
    
    # List all registered tools
    tools = list(mcp._tool_manager._tools.keys())
    print(f"Registered tools: {tools}")
    
    # Test if we can access the tool functions
    for tool_name, tool in mcp._tool_manager._tools.items():
        print(f"\nTool: {tool_name}")
        print(f"  Function: {tool.fn}")
        print(f"  Enabled: {tool.enabled}")

if __name__ == "__main__":
    asyncio.run(test_tools())