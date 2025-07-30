#!/usr/bin/env python3.10
"""
KEN-MCP: Universal MCP Server Generator
Generates MCP servers for ANY purpose based on natural language requirements
"""

from fastmcp import FastMCP, Context
from fastmcp.exceptions import ToolError
from pydantic import Field
from typing import Annotated, Optional, List, Dict, Any
import json
import os
from datetime import datetime
from pathlib import Path
import re

# Initialize the MCP server
mcp = FastMCP(name="KEN-MCP 🏗️")

# ============================================
# MAIN TOOL - Generate complete MCP server
# ============================================

@mcp.tool
async def generate_mcp_server(
    ctx: Context,
    requirements: Annotated[str, Field(description="Natural language description of desired MCP functionality")],
    project_name: Annotated[str, Field(description="Name for the MCP project (e.g., 'todo-manager')")],
    output_dir: Annotated[Optional[str], Field(description="Directory to create the project in")] = None,
    include_resources: Annotated[bool, Field(description="Whether to include MCP resources")] = True,
    include_prompts: Annotated[bool, Field(description="Whether to include MCP prompts")] = True,
    python_version: Annotated[str, Field(description="Minimum Python version required")] = "3.10",
    additional_dependencies: Annotated[Optional[List[str]], Field(description="Additional Python packages to include")] = None
) -> Dict[str, Any]:
    """Generate a complete MCP server from requirements. Works for ANY type of MCP - not just APIs!
    
    Examples:
    - "I want an MCP that manages todo lists"
    - "Create an MCP for tracking my daily habits" 
    - "Build an MCP that can analyze text files"
    - "I need an MCP that interfaces with YouTube API"
    """
    await ctx.info(f"🚀 Starting MCP generation for: {project_name}")
    
    try:
        # Step 1: Analyze requirements and plan the MCP
        await ctx.report_progress(10, 100, "Analyzing requirements...")
        plan = await _analyze_and_plan(requirements, ctx, include_resources, include_prompts)
        
        # Step 2: Create project structure
        await ctx.report_progress(30, 100, "Creating project structure...")
        project_path = await _create_project_structure(project_name, output_dir, ctx)
        
        # Step 3: Generate server code
        await ctx.report_progress(50, 100, "Generating server code...")
        await _generate_server_code(project_path, plan, ctx, python_version, additional_dependencies)
        
        # Step 4: Generate documentation
        await ctx.report_progress(70, 100, "Creating documentation...")
        await _generate_documentation(project_path, plan, project_name, ctx)
        
        # Step 5: Validate project
        await ctx.report_progress(90, 100, "Validating project...")
        validation = await _validate_project(project_path, ctx)
        
        await ctx.report_progress(100, 100, "Generation complete!")
        
        return {
            "success": True,
            "project_path": str(project_path),
            "project_name": project_name,
            "tools_generated": len(plan.get("tools", [])),
            "resources_generated": len(plan.get("resources", [])),
            "prompts_generated": len(plan.get("prompts", [])),
            "validation": validation,
            "next_steps": [
                f"1. cd {project_path}",
                f"2. pip install -e .",
                f"3. python server.py",
                f"4. Add to Claude Desktop config as shown in README.md"
            ]
        }
        
    except Exception as e:
        raise ToolError(f"Failed to generate MCP server: {str(e)}")

# ============================================
# HELPER FUNCTIONS
# ============================================

def _extract_key_concepts(requirements: str) -> List[str]:
    """Extract key concepts from requirements for Claude's reference"""
    concepts = []
    req_lower = requirements.lower()
    
    # Common domains
    if any(word in req_lower for word in ["recipe", "cook", "ingredient", "meal"]):
        concepts.append("cooking/recipes")
    if any(word in req_lower for word in ["task", "todo", "project", "deadline"]):
        concepts.append("task management")
    if any(word in req_lower for word in ["monitor", "track", "watch", "alert"]):
        concepts.append("monitoring/tracking")
    if any(word in req_lower for word in ["api", "endpoint", "rest", "http"]):
        concepts.append("API integration")
    if any(word in req_lower for word in ["file", "document", "pdf", "csv"]):
        concepts.append("file processing")
    if any(word in req_lower for word in ["database", "sql", "query", "table"]):
        concepts.append("database operations")
    
    # Actions
    if "create" in req_lower or "add" in req_lower:
        concepts.append("creation operations")
    if "search" in req_lower or "find" in req_lower:
        concepts.append("search functionality")
    if "update" in req_lower or "edit" in req_lower:
        concepts.append("update operations")
    if "delete" in req_lower or "remove" in req_lower:
        concepts.append("deletion operations")
    
    return concepts if concepts else ["general purpose"]

def _suggest_tool_names(requirements: str, index: int) -> List[str]:
    """Suggest possible tool names based on requirements"""
    req_lower = requirements.lower()
    suggestions = []
    
    # Based on common patterns
    if index == 0:  # First tool - usually create/add
        if "recipe" in req_lower:
            suggestions = ["add_recipe", "create_recipe", "save_recipe"]
        elif "task" in req_lower or "todo" in req_lower:
            suggestions = ["create_task", "add_todo", "new_task"]
        elif "monitor" in req_lower:
            suggestions = ["start_monitor", "add_monitor", "track_item"]
        else:
            suggestions = ["create_item", "add_entry", "initialize"]
    elif index == 1:  # Second tool - usually read/list
        if "recipe" in req_lower:
            suggestions = ["list_recipes", "search_recipes", "get_recipe"]
        elif "task" in req_lower:
            suggestions = ["list_tasks", "get_tasks", "show_todos"]
        else:
            suggestions = ["list_items", "search_data", "query_items"]
    elif index == 2:  # Third tool - usually update/process
        if "recipe" in req_lower:
            suggestions = ["update_recipe", "rate_recipe", "categorize_recipe"]
        elif "task" in req_lower:
            suggestions = ["complete_task", "update_task", "mark_done"]
        else:
            suggestions = ["update_item", "process_data", "modify_entry"]
    
    return suggestions if suggestions else [f"tool_{index + 1}", f"operation_{index + 1}"]

def _suggest_dependencies(requirements: str) -> List[str]:
    """Suggest potential Python dependencies based on requirements"""
    deps = []
    req_lower = requirements.lower()
    
    # API/HTTP
    if any(word in req_lower for word in ["api", "http", "rest", "webhook", "endpoint"]):
        deps.extend(["httpx", "requests"])
    
    # Web scraping
    if any(word in req_lower for word in ["scrape", "web", "html", "crawl"]):
        deps.extend(["beautifulsoup4", "requests", "lxml"])
    
    # Data processing
    if "csv" in req_lower or "excel" in req_lower or "data" in req_lower:
        deps.extend(["pandas", "openpyxl"])
    
    # Database
    if any(word in req_lower for word in ["database", "sql", "postgres", "mysql"]):
        deps.extend(["sqlalchemy", "psycopg2", "pymysql"])
    
    # File formats
    if "pdf" in req_lower:
        deps.append("pypdf2")
    if "image" in req_lower:
        deps.append("pillow")
    if "markdown" in req_lower:
        deps.append("markdown")
    
    # Crypto/Finance
    if any(word in req_lower for word in ["crypto", "bitcoin", "ethereum", "price"]):
        deps.extend(["ccxt", "yfinance"])
    
    # ML/AI
    if any(word in req_lower for word in ["classify", "predict", "analyze", "nlp"]):
        deps.extend(["scikit-learn", "nltk", "spacy"])
    
    return list(set(deps))  # Remove duplicates

def _generate_tool_implementation(tool: Dict[str, Any]) -> str:
    """Generate implementation code for a tool based on its purpose"""
    tool_name = tool["name"]
    implementation_type = tool.get("implementation", "custom")
    
    # Generate boilerplate implementation with TODOs
    if implementation_type == "boilerplate":
        tool_desc = tool.get("description", "")
        return f'''    """
    {tool_desc}
    
    Claude: Please implement this tool based on the user's requirements.
    Consider:
    - What data sources or APIs might be needed
    - What processing or transformations are required
    - What error cases should be handled
    - What progress updates would be helpful
    """
    try:
        # FastMCP Context Methods Reference:
        # - await ctx.info("message") - Log information
        # - await ctx.report_progress(current, total, "message") - Show progress
        # - await ctx.read_resource("uri") - Read from a resource
        
        await ctx.info(f"Starting {tool_name}...")
        
        # TODO: Add parameter validation
        # Example patterns:
        # if not input_data:
        #     raise ToolError("input_data is required")
        # 
        # if not isinstance(input_data, str):
        #     raise ToolError("input_data must be a string")
        #
        # if len(input_data) > 1000:
        #     raise ToolError("input_data too long (max 1000 chars)")
        
        # TODO: Implement the main functionality
        # Common patterns by use case:
        #
        # For data storage:
        #   storage_dir = Path.home() / ".mcp_data" / "{tool_name}"
        #   storage_dir.mkdir(parents=True, exist_ok=True)
        #
        # For API calls:
        #   import httpx
        #   async with httpx.AsyncClient() as client:
        #       response = await client.get(url)
        #
        # For file processing:
        #   from pathlib import Path
        #   file = Path(file_path)
        #   if not file.exists():
        #       raise ToolError(f"File not found: {{file_path}}")
        
        # TODO: Add progress updates for long operations
        # await ctx.report_progress(25, 100, "Loading data...")
        # await ctx.report_progress(50, 100, "Processing...")
        # await ctx.report_progress(75, 100, "Finalizing...")
        
        # TODO: Return appropriate result
        # Success pattern:
        # return {{
        #     "success": True,
        #     "data": processed_data,
        #     "count": len(results),
        #     "message": "Operation completed successfully"
        # }}
        
        result = {{
            "status": "not_implemented",
            "message": f"TODO: Implement {tool_name}",
            "tool": "{tool_name}",
            "description": "{tool_desc}",
            "input": locals()  # Shows all parameters for debugging
        }}
        
        await ctx.info(f"{tool_name} completed")
        return result
        
    except Exception as e:
        # Always use ToolError for user-facing errors
        raise ToolError(f"{tool_name} error: {{str(e)}}")
'''
    
    # Generate implementation based on tool name and description
    # The current LLM will understand the context and generate appropriate code
    
    # Web scraping implementation
    elif "scrape" in tool_name or "url" in tool_name:
        return '''    try:
        import requests
        from bs4 import BeautifulSoup
        import markdownify
        
        await ctx.info(f"Fetching content from {url}...")
        
        # Validate URL
        if not url.startswith(('http://', 'https://')):
            raise ToolError("URL must start with http:// or https://")
        
        # Fetch the content
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract specific content if selector provided
        if selector:
            content = soup.select(selector)
            if not content:
                raise ToolError(f"No content found for selector: {selector}")
            soup = BeautifulSoup(str(content), 'html.parser')
        
        # Convert to requested format
        if format == "markdown":
            result_text = markdownify.markdownify(str(soup), heading_style="ATX")
        elif format == "text":
            result_text = soup.get_text(separator='\\n', strip=True)
        else:  # json
            result_text = {"html": str(soup), "text": soup.get_text()}
        
        return {
            "success": True,
            "url": url,
            "content": result_text,
            "format": format
        }
        
    except requests.RequestException as e:
        raise ToolError(f"Failed to fetch URL: {str(e)}")
    except Exception as e:
        raise ToolError(f"Failed to process content: {str(e)}")
'''
    
    # Task/todo management implementation
    elif any(word in tool_name for word in ["task", "todo", "create_task", "list_tasks", "complete_task"]):
        if "create" in tool_name:
            return '''    try:
        from datetime import datetime
        import json
        from pathlib import Path
        import uuid
        
        await ctx.info(f"Creating new task: {title}")
        
        # Create task storage directory if needed
        task_dir = Path.home() / ".mcp_tasks"
        task_dir.mkdir(exist_ok=True)
        
        # Generate task ID
        task_id = str(uuid.uuid4())[:8]
        
        # Create task object
        task = {
            "id": task_id,
            "title": title,
            "description": description,
            "priority": priority,
            "deadline": deadline,
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        
        # Save task
        task_file = task_dir / f"{task_id}.json"
        task_file.write_text(json.dumps(task, indent=2))
        
        return {
            "success": True,
            "task_id": task_id,
            "task": task,
            "message": f"Task '{title}' created successfully"
        }
        
    except Exception as e:
        raise ToolError(f"Failed to create task: {str(e)}")
'''
        elif "list" in tool_name:
            return '''    try:
        import json
        from pathlib import Path
        
        await ctx.info("Listing tasks...")
        
        task_dir = Path.home() / ".mcp_tasks"
        if not task_dir.exists():
            return {"success": True, "tasks": [], "count": 0}
        
        tasks = []
        for task_file in task_dir.glob("*.json"):
            try:
                task = json.loads(task_file.read_text())
                
                # Apply filters
                if status and status != "all" and task.get("status") != status:
                    continue
                if priority and task.get("priority") != priority:
                    continue
                
                tasks.append(task)
            except Exception:
                continue
        
        # Sort by creation date
        tasks.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        return {
            "success": True,
            "tasks": tasks,
            "count": len(tasks)
        }
        
    except Exception as e:
        raise ToolError(f"Failed to list tasks: {str(e)}")
'''
        elif "complete" in tool_name:
            return '''    try:
        import json
        from pathlib import Path
        from datetime import datetime
        
        await ctx.info(f"Completing task {task_id}...")
        
        task_dir = Path.home() / ".mcp_tasks"
        task_file = task_dir / f"{task_id}.json"
        
        if not task_file.exists():
            raise ToolError(f"Task {task_id} not found")
        
        # Load and update task
        task = json.loads(task_file.read_text())
        task["status"] = "completed"
        task["completed_at"] = datetime.now().isoformat()
        
        # Save updated task
        task_file.write_text(json.dumps(task, indent=2))
        
        return {
            "success": True,
            "task_id": task_id,
            "task": task,
            "message": f"Task '{task['title']}' marked as completed"
        }
        
    except Exception as e:
        raise ToolError(f"Failed to complete task: {str(e)}")
'''
    
    # File processing implementation
    elif "file" in tool_name or "process" in tool_name:
        return '''    try:
        from pathlib import Path
        import json
        
        await ctx.info(f"Processing file: {file_path}")
        
        file = Path(file_path)
        if not file.exists():
            raise ToolError(f"File not found: {file_path}")
        
        # Perform operation based on type
        if operation == "analyze":
            stats = {
                "name": file.name,
                "size": file.stat().st_size,
                "modified": file.stat().st_mtime,
                "type": file.suffix,
                "lines": len(file.read_text().splitlines()) if file.suffix in ['.txt', '.py', '.js', '.md'] else None
            }
            return {"success": True, "file": file_path, "analysis": stats}
            
        elif operation == "convert":
            content = file.read_text()
            # Simple conversion logic
            if output_format == "json" and file.suffix == ".txt":
                lines = content.splitlines()
                return {"success": True, "content": {"lines": lines, "count": len(lines)}}
            else:
                return {"success": True, "content": content, "format": output_format or file.suffix}
                
        else:
            return {"success": True, "file": file_path, "operation": operation, "status": "completed"}
            
    except Exception as e:
        raise ToolError(f"Failed to process file: {str(e)}")
'''
    
    # API request implementation
    elif "api" in tool_name or "request" in tool_name:
        return '''    try:
        import requests
        import json
        
        await ctx.info(f"Making {method} request to {url}")
        
        # Validate URL
        if not url.startswith(('http://', 'https://')):
            raise ToolError("URL must start with http:// or https://")
        
        # Make request
        response = requests.request(
            method=method,
            url=url,
            headers=headers or {},
            json=data if data else None,
            timeout=30
        )
        
        # Parse response
        try:
            response_data = response.json()
        except:
            response_data = response.text
        
        return {
            "success": response.ok,
            "status_code": response.status_code,
            "url": url,
            "method": method,
            "response": response_data
        }
        
    except requests.RequestException as e:
        raise ToolError(f"API request failed: {str(e)}")
    except Exception as e:
        raise ToolError(f"Failed to process request: {str(e)}")
'''
    
    # Default fallback implementation
    return _generate_fallback_implementation(tool)

async def _analyze_and_plan(requirements: str, ctx: Context, include_resources: bool = True, include_prompts: bool = True) -> Dict[str, Any]:
    """Create a generic boilerplate plan that Claude can customize
    
    This generates a flexible structure with placeholder tools, resources, and prompts
    that Claude will implement based on the specific requirements.
    """
    await ctx.info("📋 Creating boilerplate structure for Claude to customize...")
    
    # Create a generic plan with placeholders
    plan = {
        "description": f"MCP server for: {requirements[:100]}{'...' if len(requirements) > 100 else ''}",
        "tools": [
            {
                "name": "tool_one",
                "description": f"Primary tool - TODO: Implement based on requirements: {requirements}",
                "parameters": [
                    {"name": "input_data", "type": "str", "description": "Main input parameter"},
                    {"name": "options", "type": "Optional[Dict[str, Any]]", "description": "Additional options", "default": None}
                ],
                "implementation": "boilerplate"
            },
            {
                "name": "tool_two", 
                "description": f"Secondary tool - TODO: Implement based on requirements: {requirements}",
                "parameters": [
                    {"name": "param1", "type": "str", "description": "First parameter"},
                    {"name": "param2", "type": "Optional[int]", "description": "Optional second parameter", "default": None}
                ],
                "implementation": "boilerplate"
            },
            {
                "name": "tool_three",
                "description": f"Additional tool - TODO: Implement or remove based on requirements: {requirements}",
                "parameters": [
                    {"name": "data", "type": "Any", "description": "Input data"}
                ],
                "implementation": "boilerplate"
            }
        ],
        "resources": [],
        "prompts": [],
        "dependencies": ["pathlib", "json", "typing"],
        "original_requirements": requirements
    }
    
    # Add placeholder resources if requested
    if include_resources:
        plan["resources"].extend([
            {
                "uri_pattern": "data://items",
                "description": "TODO: List of items - implement based on requirements",
                "implementation": "boilerplate"
            },
            {
                "uri_pattern": "resource://config", 
                "description": "TODO: Configuration data - implement based on requirements",
                "implementation": "boilerplate"
            },
            {
                "uri_pattern": "data://status",
                "description": "TODO: Status information - implement or remove based on requirements",
                "implementation": "boilerplate"
            }
        ])
    
    # Add placeholder prompts if requested
    if include_prompts:
        plan["prompts"].extend([
            {
                "name": "help",
                "description": "TODO: Generate contextual help based on requirements",
                "parameters": [{"name": "topic", "type": "Optional[str]", "default": None}]
            },
            {
                "name": "assistant",
                "description": "TODO: Assistant prompt - customize based on requirements", 
                "parameters": [{"name": "query", "type": "str"}]
            }
        ])
    
    await ctx.info(f"✅ Boilerplate plan created with {len(plan['tools'])} placeholder tools")
    return plan


def _generate_fallback_implementation(tool: Dict[str, Any]) -> str:
    """Generate simple fallback implementation when AI is not available"""
    tool_name = tool["name"]
    tool_desc = tool.get("description", "")
    parameters = tool.get("parameters", [])
    
    # Generate parameter validation
    param_validation = ""
    for param in parameters:
        param_name = param["name"]
        param_type = param.get("type", "str")
        if param_type == "str" and "url" in param_name.lower():
            param_validation += f'''
        # Validate {param_name}
        if not {param_name} or not isinstance({param_name}, str):
            raise ToolError(f"Invalid {param_name}: must be a valid string")
        
        if "{param_name}" == "url" and not ({param_name}.startswith("http://") or {param_name}.startswith("https://")):
            raise ToolError(f"Invalid URL: {{{param_name}}} must start with http:// or https://")
'''
    
    return f'''    try:
        from datetime import datetime
        import json
        {param_validation}
        
        await ctx.info(f"Executing {tool_name}...")
        
        # Implementation based on tool purpose
        result = {{
            "tool": "{tool_name}",
            "description": "{tool_desc}",
            "status": "success",
            "message": "Tool executed successfully",
            "timestamp": datetime.now().isoformat()
        }}
        
        # Add input parameters to result
        for param_name, param_value in locals().items():
            if param_name not in ['ctx', 'result'] and not param_name.startswith('_'):
                result[f"input_{{param_name}}"] = param_value
        
        return result
        
    except Exception as e:
        raise ToolError(f"Failed to execute {tool_name}: {{str(e)}}")
'''

async def _create_project_structure(project_name: str, output_dir: Optional[str], ctx: Context) -> Path:
    """Create project directory and basic files"""
    await ctx.info("📁 Creating project structure...")
    
    # Sanitize project name
    safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', project_name.lower())
    
    # Determine output directory
    if output_dir:
        base_path = Path(output_dir) / safe_name
    else:
        base_path = Path.home() / "mcp_generated_servers" / safe_name
    
    # Create directories
    base_path.mkdir(parents=True, exist_ok=True)
    
    # Create .gitignore
    gitignore_content = """__pycache__/
*.py[cod]
.env
.venv/
venv/
*.log
.DS_Store
"""
    (base_path / ".gitignore").write_text(gitignore_content)
    
    # Create .env file with common placeholders
    env_content = """# Environment variables for MCP server
# Copy this file to .env and fill in your actual values

# API Keys
# OPENAI_API_KEY=your_openai_api_key_here
# ANTHROPIC_API_KEY=your_anthropic_api_key_here
# GOOGLE_API_KEY=your_google_api_key_here

# Database Configuration
# DATABASE_URL=postgresql://user:password@localhost:5432/dbname
# REDIS_URL=redis://localhost:6379

# External Service URLs
# API_BASE_URL=https://api.example.com
# WEBHOOK_URL=https://your-webhook-endpoint.com

# Authentication
# AUTH_TOKEN=your_auth_token_here
# CLIENT_ID=your_client_id_here
# CLIENT_SECRET=your_client_secret_here

# Feature Flags
# DEBUG_MODE=false
# ENABLE_LOGGING=true

# Rate Limiting
# RATE_LIMIT_REQUESTS=100
# RATE_LIMIT_WINDOW=3600

# Custom Configuration
# Add your own environment variables below:
"""
    (base_path / ".env.example").write_text(env_content)
    
    # Create __init__.py
    (base_path / "__init__.py").write_text('"""Generated MCP server package"""')
    
    await ctx.info(f"✅ Created project at: {base_path}")
    return base_path

async def _generate_server_code(project_path: Path, plan: Dict[str, Any], ctx: Context, python_version: str = "3.10", additional_dependencies: Optional[List[str]] = None) -> None:
    """Generate the server.py file"""
    await ctx.info("💻 Generating server code...")
    
    # Add required imports based on tool implementations
    imports = [
        "from fastmcp import FastMCP, Context",
        "from fastmcp.exceptions import ToolError", 
        "from typing import Dict, List, Any, Optional",
        "from pathlib import Path",
        "import json",
        "import os"
    ]
    
    # Check if we need environment variables
    requirements = plan.get('original_requirements', '')
    needs_env = any(keyword in requirements.lower() for keyword in ["api", "key", "token", "auth", "database", "url", "webhook"])
    if needs_env:
        imports.append("from dotenv import load_dotenv")
    
    # Check what additional imports we need
    has_subprocess = any(t.get("implementation") in ["subprocess_command", "mixed"] for t in plan.get("tools", []))
    has_git = any("git" in t.get("name", "") for t in plan.get("tools", []))
    
    if has_subprocess:
        imports.extend(["import subprocess", "import shlex", "import platform"])
    if has_git and "gitpython" in plan.get("dependencies", []):
        imports.append("from git import Repo")
    
    # Generate server code with boilerplate structure
    server_code = f'''#!/usr/bin/env python3
"""
{plan.get('description', 'Generated MCP server')}
Generated by KEN-MCP on {datetime.now().strftime('%Y-%m-%d')}

TODO: Claude, please customize this MCP server based on these requirements:
{plan.get('original_requirements', 'No requirements provided')}

Instructions:
1. Rename the placeholder tools to match the actual functionality needed
2. Update tool descriptions and parameters based on requirements
3. Implement the actual logic in each tool function
4. Add/remove tools, resources, and prompts as needed
5. Update dependencies in pyproject.toml if additional packages are required
"""

{chr(10).join(imports)}

{"# Load environment variables" + chr(10) + "load_dotenv()" + chr(10) + chr(10) if needs_env else ""}# Initialize the MCP server
mcp = FastMCP(
    name="{project_path.name}",
    instructions="""
    {plan.get('description', 'MCP server implementation')}
    
    Original Requirements:
    {plan.get('original_requirements', 'No requirements provided')}
    
    TODO: Claude should update these instructions based on the actual implementation.
    """
)

'''
    
    # Add helper functions if needed
    if has_subprocess:
        server_code += '''
def run_command(command: str, directory: str = ".") -> Dict[str, Any]:
    """Run a shell command and return results"""
    try:
        if platform.system() == "Windows":
            shell = True
            args = command
        else:
            shell = False
            args = shlex.split(command)
        
        result = subprocess.run(
            args,
            cwd=directory,
            capture_output=True,
            text=True,
            shell=shell,
            timeout=30
        )
        
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Command timed out after 30 seconds"}
    except Exception as e:
        return {"success": False, "error": str(e)}

'''
    
    # Add tools from plan with implementations
    for tool in plan.get("tools", []):
        # Build parameter list
        params = []
        param_defaults = []
        for param in tool.get("parameters", []):
            p_name = param["name"]
            p_type = param.get("type", "str")
            p_default = param.get("default")
            
            if p_default is not None:
                if p_default == "None" or p_type.startswith("Optional"):
                    param_defaults.append(f"    {p_name}: {p_type} = None,")
                elif isinstance(p_default, str) and p_default != "None":
                    param_defaults.append(f"    {p_name}: {p_type} = \"{p_default}\",")
                else:
                    param_defaults.append(f"    {p_name}: {p_type} = {p_default},")
            else:
                params.append(f"    {p_name}: {p_type},")
        
        # Parameters with no defaults first, then those with defaults
        all_params = params + param_defaults
        params_str = "\n".join(all_params) if all_params else ""
        
        # Generate implementation based on metadata
        implementation = _generate_tool_implementation(tool)
        
        # Clean up any trailing commas in parameters
        if params_str and params_str.endswith(','):
            params_str = params_str[:-1]
        
        server_code += f'''
@mcp.tool
async def {tool["name"]}(
    ctx: Context,
{params_str}
) -> Dict[str, Any]:
    """{tool["description"]}"""
{implementation}
'''
    
    # Add resources from plan
    if plan.get("resources"):
        server_code += "\n# Resources - TODO: Claude, implement these based on requirements\n"
        for resource in plan["resources"]:
            uri = resource.get("uri_pattern", "resource://unknown")
            desc = resource.get("description", "Resource description")
            impl_type = resource.get("implementation", "custom")
            
            if impl_type == "boilerplate":
                server_code += f'''
@mcp.resource("{uri}")
async def resource_{uri.split("://")[1].replace("/", "_").replace("{", "").replace("}", "")}() -> List[Dict[str, Any]]:
    """{desc}"""
    # TODO: Implement this resource based on requirements
    # Consider what data should be exposed here
    return [{{
        "status": "not_implemented", 
        "message": "TODO: Implement resource for {uri}",
        "description": "{desc}"
    }}]
'''
    
    # Add prompts from plan
    if plan.get("prompts"):
        server_code += "\n# Prompts - TODO: Claude, implement these based on requirements\n"
        for prompt in plan["prompts"]:
            prompt_name = prompt.get("name", "unknown")
            desc = prompt.get("description", "Prompt description")
            params = prompt.get("parameters", [])
            
            # Build prompt parameters
            prompt_params = []
            for param in params:
                p_name = param.get("name", "param")
                p_type = param.get("type", "str")
                p_default = param.get("default")
                if p_default is not None:
                    prompt_params.append(f"{p_name}: {p_type} = {repr(p_default)}")
                else:
                    prompt_params.append(f"{p_name}: {p_type}")
            
            params_str = ", ".join(prompt_params)
            
            server_code += f'''
@mcp.prompt
def {prompt_name}({params_str}) -> str:
    """{desc}"""
    # TODO: Implement this prompt based on requirements
    # Return a string that will be converted to a user message
    # or return a PromptMessage object for more control
    return f"TODO: Implement {prompt_name} prompt - {{locals()}}"
'''
    
    # Add main block
    server_code += '''

if __name__ == "__main__":
    mcp.run()
'''
    
    # Write server file
    server_path = project_path / "server.py"
    server_path.write_text(server_code)
    os.chmod(server_path, 0o755)
    
    # Create pyproject.toml
    dependencies = ["fastmcp>=0.1.0"]
    
    # Add dependencies from plan (excluding standard library modules)
    stdlib_modules = {"pathlib", "json", "typing", "os", "datetime", "subprocess", "shlex", "platform"}
    for dep in plan.get("dependencies", []):
        if dep not in stdlib_modules and dep not in dependencies:
            dependencies.append(dep)
    
    if additional_dependencies:
        dependencies.extend(additional_dependencies)
    
    # Add python-dotenv if environment variables are likely needed
    requirements = plan.get('original_requirements', '')
    if any(keyword in requirements.lower() for keyword in ["api", "key", "token", "auth", "database", "url", "webhook"]):
        if "python-dotenv" not in dependencies:
            dependencies.append("python-dotenv")
    
    pyproject_content = f"""[project]
name = "{project_path.name}"
version = "0.1.0"
description = "{plan.get('description', 'Generated MCP server')}"
readme = "README.md"
requires-python = ">={python_version}"
dependencies = {json.dumps(dependencies)}

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["."]
"""
    (project_path / "pyproject.toml").write_text(pyproject_content)
    
    await ctx.info("✅ Generated server.py and pyproject.toml")

async def _generate_documentation(project_path: Path, plan: Dict[str, Any], project_name: str, ctx: Context) -> None:
    """Generate README.md and mcp.md"""
    await ctx.info("📚 Generating documentation...")
    
    # Generate README.md with complete setup instructions
    readme_content = f"""# {project_name}

{plan.get('description', 'Generated MCP server')}

## TODO: Implementation Required

This is a boilerplate MCP server generated by KEN-MCP. Claude needs to customize it based on these requirements:

**Original Requirements:**
> {plan.get('original_requirements', 'No requirements provided')}

### Implementation Checklist

- [ ] Update tool names and implementations in `server.py`
- [ ] Implement resource handlers if needed
- [ ] Customize prompt templates
- [ ] Update dependencies in `pyproject.toml`
- [ ] Update this README with actual functionality
- [ ] Test all tools with MCP Inspector

## Prerequisites

Before you begin, ensure you have the following installed:

1. **Python 3.10 or higher**
   ```bash
   python --version  # Should show Python 3.10+
   ```

2. **pip (Python package installer)**
   ```bash
   pip --version
   ```

3. **Node.js** (required for npx commands)
   ```bash
   node --version  # Should show v16 or higher
   npm --version
   ```

If any of these are missing:
- Python: Download from [python.org](https://python.org)
- Node.js: Download from [nodejs.org](https://nodejs.org)

## Installation

1. **Clone or download this MCP server folder**

2. **Set up environment variables (if needed)**
   ```bash
   cd {project_path.name}
   cp .env.example .env
   # Edit .env and add your API keys and configuration
   ```

3. **Install Python dependencies**
   ```bash
   pip install -e .
   ```

   Or using a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   pip install -e .
   ```

## Configuration

### Option 1: Claude Code

Add this server to Claude Code using the CLI:

```bash
# Add as a local project server (recommended for development)
claude mcp add {project_name} "python {project_path}/server.py"

# Or add as a user server (available across all projects)
claude mcp add {project_name} "python {project_path}/server.py" --user

# List configured servers to verify
claude mcp list
```

**Important**: Restart Claude Code after adding the server for changes to take effect.

### Option 2: Claude Desktop

1. **Find your configuration file**:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\\Claude\\claude_desktop_config.json`

2. **Edit the configuration file** and add your server:
   ```json
   {{
     "mcpServers": {{
       "{project_name}": {{
         "command": "python",
         "args": ["{project_path}/server.py"]
       }}
     }}
   }}
   ```

   If you already have other servers, add this one to the existing `mcpServers` object:
   ```json
   {{
     "mcpServers": {{
       "existing-server": {{ ... }},
       "{project_name}": {{
         "command": "python",
         "args": ["{project_path}/server.py"]
       }}
     }}
   }}
   ```

3. **Restart Claude Desktop completely** (quit and reopen)

4. **Verify the server is loaded**: Look for the 🔌 icon in the bottom of your chat interface

## Testing Your Server

### 1. Test with the included harness
```bash
python test_server.py
```

### 2. Test with MCP Inspector
```bash
npx @modelcontextprotocol/inspector python server.py
```
This opens an interactive testing interface in your browser.

## Usage

Once configured, you can use your MCP server in Claude:
- Tools will appear in the available tools list
- Resources can be accessed using their URIs
- Prompts will be available as slash commands

## Troubleshooting

### Server not appearing in Claude
1. **Verify the server runs without errors**:
   ```bash
   python server.py
   ```
   It should output: "Server running on stdio"

2. **Check configuration**:
   - Claude Code: Run `claude mcp list` to see configured servers
   - Claude Desktop: Verify the JSON configuration is valid

3. **Restart Claude completely**:
   - Claude Code: Close and reopen the application
   - Claude Desktop: Quit (not just close) and restart

4. **Check logs**:
   - Claude Code: Check terminal output for errors
   - Claude Desktop: Check the logs in the app's developer console

### Common Issues
- **"ModuleNotFoundError: No module named 'fastmcp'"**: Run `pip install -e .` in the project directory
- **"No such file or directory"**: Use absolute paths in configuration
- **Server not updating**: Always restart Claude after configuration changes

## Features (TO BE IMPLEMENTED)

### Tools
"""
    
    for tool in plan.get("tools", []):
        readme_content += f"\n#### `{tool['name']}`\n{tool['description']}\n"
        if tool.get("parameters"):
            readme_content += "\nParameters:\n"
            for param in tool["parameters"]:
                readme_content += f"- `{param['name']}` ({param['type']}): {param['description']}\n"
    
    if plan.get("resources"):
        readme_content += "\n### Resources\n"
        for resource in plan["resources"]:
            readme_content += f"\n- `{resource['uri_pattern']}`: {resource['description']}\n"
    
    if plan.get("prompts"):
        readme_content += "\n### Prompts\n"
        for prompt in plan["prompts"]:
            readme_content += f"\n- `{prompt['name']}`: {prompt['description']}\n"
    
    readme_content += f"""

## License

MIT

---
Generated by KEN-MCP on {datetime.now().strftime('%Y-%m-%d')}
"""
    
    (project_path / "README.md").write_text(readme_content)
    
    # Generate mcp.md with implementation notes
    mcp_content = f"""# {project_name} MCP Documentation

## Overview
{plan.get('description', 'Generated MCP server')}

## Implementation Status: BOILERPLATE

This is a boilerplate MCP server that requires implementation by Claude.

### Original Requirements
```
{plan.get('original_requirements', 'No requirements provided')}
```

### Current Status
- ✅ Basic structure generated
- ⚠️  Tool implementations are placeholders
- ⚠️  Resources need actual data sources
- ⚠️  Prompts need customization
- ❌ Not ready for production use

### Architecture
- Built with FastMCP framework
- Provides {len(plan.get('tools', []))} placeholder tools
- Includes {len(plan.get('resources', []))} placeholder resources
- Offers {len(plan.get('prompts', []))} placeholder prompt templates

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
Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    (project_path / "mcp.md").write_text(mcp_content)
    
    # Generate CLAUDE_IMPLEMENTATION_GUIDE.md
    claude_guide = f"""# Claude Implementation Guide

This guide helps Claude implement the MCP server based on the requirements.

## Original Requirements
```
{plan.get('original_requirements', 'No requirements provided')}
```

## FastMCP Quick Reference

### Essential Patterns

#### 1. Basic Tool Structure
```python
@mcp.tool
async def tool_name(ctx: Context, param1: str, param2: Optional[int] = None) -> Dict[str, Any]:
    \"\"\"Tool description\"\"\"
    # Logging
    await ctx.info("Starting tool execution...")
    
    # Progress reporting
    await ctx.report_progress(50, 100, "Processing...")
    
    # Error handling
    if not param1:
        raise ToolError("param1 is required")
    
    # Return structured data
    return {{"status": "success", "data": result}}
```

#### 2. Resource Patterns
```python
# Static resource
@mcp.resource("data://items")
def get_items() -> List[Dict[str, Any]]:
    return [{{"id": 1, "name": "Item 1"}}]

# Dynamic resource with parameters
@mcp.resource("data://items/{{item_id}}")
async def get_item(item_id: str) -> Dict[str, Any]:
    # Fetch and return specific item
    return {{"id": item_id, "name": f"Item {{item_id}}"}}
```

#### 3. Prompt Patterns
```python
@mcp.prompt
def help_prompt(topic: str) -> str:
    return f"Please explain {{topic}} in detail"

# Or return PromptMessage for more control
from fastmcp.prompts import PromptMessage
@mcp.prompt
def advanced_prompt(query: str) -> PromptMessage:
    return PromptMessage(role="user", content=query)
```

## Implementation Examples by Domain

### Environment Variables
```python
# Using environment variables for API keys and configuration
import os

# Get API key with fallback
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ToolError("OPENAI_API_KEY not found in environment variables")

# Get configuration with defaults
base_url = os.getenv("API_BASE_URL", "https://api.example.com")
timeout = int(os.getenv("REQUEST_TIMEOUT", "30"))
debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
```

### Data Management (Database/Storage)
```python
@mcp.tool
async def create_item(ctx: Context, name: str, description: str = "") -> Dict[str, Any]:
    \"\"\"Create a new item\"\"\"
    import json
    from pathlib import Path
    import uuid
    
    # Generate ID
    item_id = str(uuid.uuid4())[:8]
    
    # Create item
    item = {{
        "id": item_id,
        "name": name,
        "description": description,
        "created_at": datetime.now().isoformat()
    }}
    
    # Save to file (or database)
    storage_dir = Path.home() / ".mcp_data" / "items"
    storage_dir.mkdir(parents=True, exist_ok=True)
    
    item_file = storage_dir / f"{{item_id}}.json"
    item_file.write_text(json.dumps(item, indent=2))
    
    await ctx.info(f"Created item {{item_id}}")
    return {{"success": True, "item": item}}
```

### API Integration
```python
@mcp.tool
async def fetch_data(ctx: Context, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
    \"\"\"Fetch data from API\"\"\"
    import httpx
    import os
    
    # Get API key from environment
    api_key = os.getenv("API_KEY")
    if not api_key:
        raise ToolError("API_KEY not found in environment variables")
    
    headers = {{
        "Authorization": f"Bearer {{api_key}}",
        "Content-Type": "application/json"
    }}
    
    base_url = os.getenv("API_BASE_URL", "https://api.example.com")
    full_url = f"{{base_url}}{{endpoint}}"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(full_url, params=params, headers=headers)
        response.raise_for_status()
        
    return {{"status": "success", "data": response.json()}}
```

### File Processing
```python
@mcp.tool
async def process_file(ctx: Context, file_path: str) -> Dict[str, Any]:
    \"\"\"Process a file\"\"\"
    from pathlib import Path
    
    file = Path(file_path)
    if not file.exists():
        raise ToolError(f"File not found: {{file_path}}")
    
    # Process based on file type
    if file.suffix == ".json":
        import json
        data = json.loads(file.read_text())
        return {{"type": "json", "data": data}}
    elif file.suffix in [".txt", ".md"]:
        content = file.read_text()
        return {{"type": "text", "content": content, "lines": len(content.splitlines())}}
    else:
        return {{"type": "binary", "size": file.stat().st_size}}
```

## Common Patterns to Implement

### 1. CRUD Operations
- Create: Add new items with validation
- Read: Fetch single or multiple items
- Update: Modify existing items
- Delete: Remove items with confirmation

### 2. Search and Filter
```python
@mcp.tool
async def search_items(ctx: Context, query: str, filters: Optional[Dict] = None) -> List[Dict]:
    # Implement search logic
    results = []
    # ... search implementation
    return results
```

### 3. Batch Operations
```python
@mcp.tool
async def batch_process(ctx: Context, items: List[str]) -> Dict[str, Any]:
    results = []
    total = len(items)
    
    for i, item in enumerate(items):
        await ctx.report_progress(i, total, f"Processing {{item}}")
        # Process item
        results.append(processed_item)
    
    return {{"processed": len(results), "results": results}}
```

## Error Handling Best Practices

1. **User-Friendly Errors**
```python
if not valid_input:
    raise ToolError("Please provide a valid input. Example: 'hello world'")
```

2. **Detailed Logging**
```python
try:
    result = await process_data()
except Exception as e:
    await ctx.info(f"Error details: {{str(e)}}")
    raise ToolError("Failed to process data. Please try again.")
```

3. **Validation**
```python
# Type validation
if not isinstance(data, dict):
    raise ToolError("Data must be a dictionary")

# Range validation
if value < 0 or value > 100:
    raise ToolError("Value must be between 0 and 100")
```

## Testing Your Implementation

1. **Use the test harness** (test_server.py)
2. **Test with MCP Inspector**:
   ```bash
   npx @modelcontextprotocol/inspector python server.py
   ```

3. **Common test cases**:
   - Valid inputs
   - Invalid inputs
   - Edge cases (empty, null, very large)
   - Error conditions

## Checklist for Implementation

- [ ] Rename tools to match actual functionality
- [ ] Update all descriptions
- [ ] Add proper parameter validation
- [ ] Implement core logic
- [ ] Add error handling
- [ ] Include progress updates for long operations
- [ ] Test each tool thoroughly
- [ ] Update dependencies if needed
- [ ] Update README with real examples

## Need Help?

Refer to:
- FastMCP Documentation: https://github.com/jlowin/fastmcp
- MCP Protocol: https://modelcontextprotocol.io
- Example implementations in this guide

---
Generated for Claude by KEN-MCP
"""
    
    (project_path / "CLAUDE_IMPLEMENTATION_GUIDE.md").write_text(claude_guide)
    
    await ctx.info("✅ Generated README.md, mcp.md, and CLAUDE_IMPLEMENTATION_GUIDE.md")
    
    # Generate requirements.json for structured analysis
    requirements_data = {
        "original_request": plan.get('original_requirements', ''),
        "generated_at": datetime.now().isoformat(),
        "project_name": project_name,
        "analysis": {
            "description": plan.get('description', ''),
            "key_concepts": _extract_key_concepts(plan.get('original_requirements', '')),
            "suggested_tools": [
                {
                    "placeholder": tool['name'],
                    "description": tool['description'],
                    "suggested_names": _suggest_tool_names(plan.get('original_requirements', ''), i)
                }
                for i, tool in enumerate(plan.get('tools', []))
            ],
            "suggested_resources": [
                {
                    "uri": res['uri_pattern'],
                    "description": res['description']
                }
                for res in plan.get('resources', [])
            ],
            "potential_dependencies": _suggest_dependencies(plan.get('original_requirements', ''))
        },
        "implementation_hints": {
            "data_storage": "Consider using JSON files, SQLite, or external APIs",
            "error_handling": "Use ToolError for all user-facing errors",
            "testing": "Test with MCP Inspector and the provided test harness",
            "security": "Validate all inputs, sanitize file paths, handle auth if needed"
        }
    }
    
    (project_path / "requirements.json").write_text(json.dumps(requirements_data, indent=2))
    await ctx.info("✅ Generated requirements.json for structured analysis")
    
    # Generate test harness
    test_harness = f'''#!/usr/bin/env python3
"""
Test harness for {project_name} MCP server
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
        print(f"[INFO] {{message}}")
    
    async def report_progress(self, current: int, total: int, message: str):
        print(f"[PROGRESS {{current}}/{{total}}] {{message}}")
    
    async def read_resource(self, uri: str):
        print(f"[RESOURCE] Reading: {{uri}}")
        return []  # Mock empty resource

async def test_tools():
    """Test all tools in the server"""
    ctx = TestContext()
    
    print("=" * 60)
    print(f"Testing {project_name} MCP Server")
    print("=" * 60)
    
    # Get all tools
    tools = [item for item in dir(mcp) if hasattr(getattr(mcp, item), '__tool__')]
    
    print(f"\\nFound {{len(tools)}} tools to test:\\n")
    
    for tool_name in tools:
        tool_func = getattr(mcp, tool_name)
        print(f"\\nTesting tool: {{tool_name}}")
        print("-" * 40)
        
        try:
            # TODO: Claude should customize these test inputs based on actual tool parameters
            # Example test cases:
            
            if tool_name == "tool_one":
                result = await tool_func(ctx, input_data="test data", options={{"test": True}})
            elif tool_name == "tool_two":
                result = await tool_func(ctx, param1="test", param2=42)
            elif tool_name == "tool_three":
                result = await tool_func(ctx, data="test")
            else:
                print(f"No test case defined for {{tool_name}}")
                continue
            
            print(f"Result: {{result}}")
            
        except Exception as e:
            print(f"Error: {{type(e).__name__}}: {{e}}")
        
        print("-" * 40)

async def test_resources():
    """Test all resources in the server"""
    print("\\n" + "=" * 60)
    print("Testing Resources")
    print("=" * 60)
    
    # Get all resources
    resources = [item for item in dir(mcp) if hasattr(getattr(mcp, item), '__resource__')]
    
    print(f"\\nFound {{len(resources)}} resources\\n")
    
    for resource_name in resources:
        resource_func = getattr(mcp, resource_name)
        print(f"\\nTesting resource: {{resource_name}}")
        
        try:
            result = await resource_func() if asyncio.iscoroutinefunction(resource_func) else resource_func()
            print(f"Result: {{result}}")
        except Exception as e:
            print(f"Error: {{type(e).__name__}}: {{e}}")

async def test_prompts():
    """Test all prompts in the server"""
    print("\\n" + "=" * 60)
    print("Testing Prompts")
    print("=" * 60)
    
    # Get all prompts
    prompts = [item for item in dir(mcp) if hasattr(getattr(mcp, item), '__prompt__')]
    
    print(f"\\nFound {{len(prompts)}} prompts\\n")
    
    for prompt_name in prompts:
        prompt_func = getattr(mcp, prompt_name)
        print(f"\\nTesting prompt: {{prompt_name}}")
        
        try:
            # TODO: Customize test inputs for prompts
            if "topic" in prompt_func.__code__.co_varnames:
                result = prompt_func(topic="test topic")
            elif "query" in prompt_func.__code__.co_varnames:
                result = prompt_func(query="test query")
            else:
                result = prompt_func()
            
            print(f"Result: {{result}}")
        except Exception as e:
            print(f"Error: {{type(e).__name__}}: {{e}}")

async def main():
    """Run all tests"""
    await test_tools()
    await test_resources()
    await test_prompts()
    
    print("\\n" + "=" * 60)
    print("Testing complete!")
    print("=" * 60)
    print("\\nNote: These are placeholder tests. Claude should update them")
    print("based on the actual tool implementations.")

if __name__ == "__main__":
    asyncio.run(main())
'''
    
    test_file = project_path / "test_server.py"
    test_file.write_text(test_harness)
    os.chmod(test_file, 0o755)
    
    await ctx.info("✅ Generated test_server.py test harness")

async def _validate_project(project_path: Path, ctx: Context) -> Dict[str, Any]:
    """Validate the generated project"""
    await ctx.info("✔️ Validating project...")
    
    issues = []
    warnings = []
    
    # Check required files
    required_files = [
        "server.py", 
        "README.md", 
        "mcp.md", 
        "pyproject.toml", 
        ".gitignore",
        "CLAUDE_IMPLEMENTATION_GUIDE.md",
        "requirements.json",
        "test_server.py"
    ]
    for file in required_files:
        if not (project_path / file).exists():
            issues.append(f"Missing required file: {file}")
    
    # Check Python syntax
    server_file = project_path / "server.py"
    if server_file.exists():
        try:
            import ast
            ast.parse(server_file.read_text())
        except SyntaxError as e:
            issues.append(f"Syntax error in server.py: {e}")
    
    # Check for common issues
    if server_file.exists():
        content = server_file.read_text()
        if "TODO" in content or "FIXME" in content:
            warnings.append("Server code contains TODO/FIXME comments")
        if not "if __name__ == '__main__':" in content:
            warnings.append("Missing main execution block")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
        "files_checked": len(required_files)
    }


# ============================================
# ADDITIONAL TOOLS
# ============================================

@mcp.tool
async def analyze_requirements(
    ctx: Context,
    requirements: Annotated[str, Field(description="Natural language description to analyze")]
) -> Dict[str, Any]:
    """Analyze requirements and suggest an implementation plan without generating code"""
    await ctx.info("🔍 Analyzing requirements...")
    
    plan = await _analyze_and_plan(requirements, ctx)
    
    return {
        "description": plan.get("description"),
        "suggested_tools": len(plan.get("tools", [])),
        "suggested_resources": len(plan.get("resources", [])),
        "suggested_prompts": len(plan.get("prompts", [])),
        "dependencies": plan.get("dependencies", []),
        "plan_details": plan
    }

@mcp.tool
async def list_generated_servers(
    ctx: Context,
    directory: Annotated[Optional[str], Field(description="Directory to search in")] = None
) -> List[Dict[str, Any]]:
    """List all previously generated MCP servers"""
    await ctx.info("📋 Listing generated servers...")
    
    search_dir = Path(directory) if directory else Path.home() / "mcp_generated_servers"
    servers = []
    
    if search_dir.exists():
        for project_dir in search_dir.iterdir():
            if project_dir.is_dir() and (project_dir / "server.py").exists():
                try:
                    readme_path = project_dir / "README.md"
                    description = "No description available"
                    if readme_path.exists():
                        lines = readme_path.read_text().split('\n')
                        for line in lines[1:10]:  # Check first few lines
                            if line.strip() and not line.startswith('#'):
                                description = line.strip()
                                break
                    
                    servers.append({
                        "name": project_dir.name,
                        "path": str(project_dir),
                        "description": description,
                        "created": datetime.fromtimestamp(project_dir.stat().st_ctime).isoformat()
                    })
                except Exception:
                    pass
    
    return sorted(servers, key=lambda x: x["created"], reverse=True)

# ============================================
# MAIN
# ============================================

if __name__ == "__main__":
    mcp.run()