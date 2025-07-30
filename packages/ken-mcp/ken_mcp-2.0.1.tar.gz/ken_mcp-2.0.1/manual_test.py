#!/usr/bin/env python3.10
"""Manual test for MCP generation with .env support"""

import asyncio
import os
import sys
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def main():
    print("Testing MCP generator...")
    
    # Import the functions we need
    try:
        from mcp_generator import _create_project_structure
        
        class TestContext:
            async def info(self, msg):
                print(f"[INFO] {msg}")
                
        ctx = TestContext()
        
        # Create project structure
        project_path = await _create_project_structure("api-test", "test_output", ctx)
        
        # Check if .env.example was created
        env_file = project_path / ".env.example"
        if env_file.exists():
            print(f"\n✅ SUCCESS: .env.example created at {env_file}")
            print("\n--- .env.example content ---")
            print(env_file.read_text()[:500] + "..." if len(env_file.read_text()) > 500 else env_file.read_text())
        else:
            print(f"\n❌ FAILED: .env.example not found at {env_file}")
            
        # Check gitignore
        gitignore = project_path / ".gitignore"
        if gitignore.exists() and ".env" in gitignore.read_text():
            print("\n✅ SUCCESS: .gitignore includes .env")
        else:
            print("\n❌ FAILED: .gitignore missing or doesn't include .env")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())