#!/usr/bin/env python3
"""
Test harness for todo-manager MCP server
This allows you to test your tools without using MCP Inspector
"""

import asyncio
import sys
from pathlib import Path

# Add the project directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Import your server
from server import mcp

# Mock Context for testing
class TestContext:
    async def info(self, message: str):
        print(f"[INFO] {message}")
    
    async def report_progress(self, current: int, total: int, message: str):
        print(f"[PROGRESS {current}/{total}] {message}")
    
    async def read_resource(self, uri: str):
        print(f"[RESOURCE] Reading: {uri}")
        return []  # Mock empty resource

async def test_tools():
    """Test all tools in the server"""
    ctx = TestContext()
    
    print("=" * 60)
    print(f"Testing todo-manager MCP Server")
    print("=" * 60)
    
    # Get all tools
    tools = [item for item in dir(mcp) if hasattr(getattr(mcp, item), '__tool__')]
    
    print(f"\nFound {len(tools)} tools to test:\n")
    
    for tool_name in tools:
        tool_func = getattr(mcp, tool_name)
        print(f"\nTesting tool: {tool_name}")
        print("-" * 40)
        
        try:
            # TODO: Claude should customize these test inputs based on actual tool parameters
            # Example test cases:
            
            if tool_name == "tool_one":
                result = await tool_func(ctx, input_data="test data", options={"test": True})
            elif tool_name == "tool_two":
                result = await tool_func(ctx, param1="test", param2=42)
            elif tool_name == "tool_three":
                result = await tool_func(ctx, data="test")
            else:
                print(f"No test case defined for {tool_name}")
                continue
            
            print(f"Result: {result}")
            
        except Exception as e:
            print(f"Error: {type(e).__name__}: {e}")
        
        print("-" * 40)

async def test_resources():
    """Test all resources in the server"""
    print("\n" + "=" * 60)
    print("Testing Resources")
    print("=" * 60)
    
    # Get all resources
    resources = [item for item in dir(mcp) if hasattr(getattr(mcp, item), '__resource__')]
    
    print(f"\nFound {len(resources)} resources\n")
    
    for resource_name in resources:
        resource_func = getattr(mcp, resource_name)
        print(f"\nTesting resource: {resource_name}")
        
        try:
            result = await resource_func() if asyncio.iscoroutinefunction(resource_func) else resource_func()
            print(f"Result: {result}")
        except Exception as e:
            print(f"Error: {type(e).__name__}: {e}")

async def test_prompts():
    """Test all prompts in the server"""
    print("\n" + "=" * 60)
    print("Testing Prompts")
    print("=" * 60)
    
    # Get all prompts
    prompts = [item for item in dir(mcp) if hasattr(getattr(mcp, item), '__prompt__')]
    
    print(f"\nFound {len(prompts)} prompts\n")
    
    for prompt_name in prompts:
        prompt_func = getattr(mcp, prompt_name)
        print(f"\nTesting prompt: {prompt_name}")
        
        try:
            # TODO: Customize test inputs for prompts
            if "topic" in prompt_func.__code__.co_varnames:
                result = prompt_func(topic="test topic")
            elif "query" in prompt_func.__code__.co_varnames:
                result = prompt_func(query="test query")
            else:
                result = prompt_func()
            
            print(f"Result: {result}")
        except Exception as e:
            print(f"Error: {type(e).__name__}: {e}")

async def main():
    """Run all tests"""
    await test_tools()
    await test_resources()
    await test_prompts()
    
    print("\n" + "=" * 60)
    print("Testing complete!")
    print("=" * 60)
    print("\nNote: These are placeholder tests. Claude should update them")
    print("based on the actual tool implementations.")

if __name__ == "__main__":
    asyncio.run(main())
