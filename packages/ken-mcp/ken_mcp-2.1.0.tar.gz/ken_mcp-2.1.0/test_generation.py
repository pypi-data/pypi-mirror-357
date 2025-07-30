#!/usr/bin/env python3.10
"""Test script to generate an MCP server using KEN-MCP"""

import asyncio
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mcp_generator import _analyze_and_plan, _create_project_structure, _generate_server_code, _generate_documentation, _validate_project

class TestContext:
    """Test context for running tools"""
    
    async def info(self, message: str):
        print(f"[INFO] {message}")
    
    async def report_progress(self, current: int, total: int, message: str):
        print(f"[PROGRESS] {current}/{total}: {message}")

async def test_generation():
    ctx = TestContext()
    requirements = "I want to track my daily habits like exercise, reading, meditation"
    project_name = "habit-tracker"
    output_dir = "./test_output"
    python_version = "3.10"
    additional_dependencies = None
    
    try:
        # Step 1: Analyze requirements
        print("[PROGRESS] 10/100: Analyzing requirements...")
        plan = await _analyze_and_plan(requirements, ctx, True, True)
        
        # Step 2: Create project structure
        print("[PROGRESS] 30/100: Creating project structure...")
        project_path = await _create_project_structure(project_name, output_dir, ctx)
        
        # Step 3: Generate server code
        print("[PROGRESS] 50/100: Generating server code...")
        await _generate_server_code(project_path, plan, ctx, python_version, additional_dependencies)
        
        # Step 4: Generate documentation
        print("[PROGRESS] 70/100: Creating documentation...")
        await _generate_documentation(project_path, plan, project_name, ctx)
        
        # Step 5: Validate project
        print("[PROGRESS] 90/100: Validating project...")
        validation = await _validate_project(project_path, ctx)
        
        print("[PROGRESS] 100/100: Generation complete!")
        
        result = {
            "success": True,
            "project_path": str(project_path),
            "project_name": project_name,
            "tools_generated": len(plan.get("tools", [])),
            "resources_generated": len(plan.get("resources", [])),
            "prompts_generated": len(plan.get("prompts", [])),
            "validation": validation
        }
        
        print("\n=== Generation Result ===")
        print(json.dumps(result, indent=2))
        
        # List generated files
        if result['success']:
            print(f"\n=== Generated Files in {result['project_path']} ===")
            project_path = result['project_path']
            for root, dirs, files in os.walk(project_path):
                level = root.replace(project_path, '').count(os.sep)
                indent = ' ' * 2 * level
                print(f"{indent}{os.path.basename(root)}/")
                sub_indent = ' ' * 2 * (level + 1)
                for file in files:
                    print(f"{sub_indent}{file}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_generation())