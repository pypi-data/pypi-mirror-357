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

def _escape_for_docstring(text: str) -> str:
    """Escape text to be safely used in Python docstrings"""
    # Replace all quotes to avoid any issues with docstring delimiters
    text = text.replace('"', "'")
    # Escape backslashes
    text = text.replace("\\", "\\\\")
    # Remove any trailing/leading whitespace that could cause issues
    text = text.strip()
    # Limit length to prevent extremely long docstrings
    if len(text) > 500:
        text = text[:497] + "..."
    return text

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
    
    # WebSocket/Real-time
    if any(word in req_lower for word in ["websocket", "real-time", "streaming", "live"]):
        deps.extend(["websockets", "asyncio"])
    
    # Authentication
    if any(word in req_lower for word in ["oauth", "auth", "login", "token"]):
        deps.extend(["authlib", "oauthlib"])
    
    # Social Media APIs
    if "discord" in req_lower:
        deps.append("discord.py")
    if "slack" in req_lower:
        deps.append("slack-sdk")
    if "github" in req_lower:
        deps.append("PyGithub")
    
    # Data Science/ML specific
    if any(word in req_lower for word in ["numpy", "pandas", "matplotlib", "chart"]):
        deps.extend(["numpy", "pandas", "matplotlib"])
    if any(word in req_lower for word in ["machine learning", "ml", "prediction", "model"]):
        deps.extend(["scikit-learn", "joblib"])
    
    # XML processing
    if "xml" in req_lower:
        deps.append("xmltodict")
    
    return list(set(deps))  # Remove duplicates

def _generate_tool_implementation(tool: Dict[str, Any]) -> str:
    """Generate implementation code for a tool based on its purpose"""
    tool_name = tool["name"]
    implementation_type = tool.get("implementation", "custom")
    
    # Generate boilerplate implementation with TODOs
    if implementation_type == "boilerplate":
        tool_desc = tool.get("description", "")
        return f'''    # TODO: Claude, implement this tool based on the requirements in the docstring above
    # Consider:
    # - What data sources or APIs might be needed
    # - What processing or transformations are required
    # - What error cases should be handled
    # - What progress updates would be helpful
    
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
            "description": {json.dumps(tool_desc)},
            "input": locals()  # Shows all parameters for debugging
        }}
        
        await ctx.info(f"{tool_name} completed")
        return result
        
    except Exception as e:
        # Always use ToolError for user-facing errors
        raise ToolError(f"{tool_name} error: {{str(e)}}")
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
    # Clean up requirements for description - remove newlines and excessive spaces
    clean_requirements = ' '.join(requirements.split())[:100]
    plan = {
        "description": f"MCP server for: {clean_requirements}{'...' if len(requirements) > 100 else ''}",
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
            "description": {json.dumps(tool_desc)},
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
        # Use current working directory
        base_path = Path.cwd() / safe_name
    
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
    
    # Generate server code with boilerplate structure
    server_code = f'''#!/usr/bin/env python3
"""
{plan.get('description', 'Generated MCP server')}
Generated by KEN-MCP on {datetime.now().strftime('%Y-%m-%d')}

TODO: Claude, please customize this MCP server based on these requirements:
{_escape_for_docstring(plan.get('original_requirements', 'No requirements provided'))}

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
    {_escape_for_docstring(plan.get('original_requirements', 'No requirements provided'))}
    
    TODO: Claude should update these instructions based on the actual implementation.
    """
)

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
        
        # Escape the description for safe use in docstring
        escaped_description = _escape_for_docstring(tool["description"])
        
        server_code += f'''
@mcp.tool
async def {tool["name"]}(
    ctx: Context,
{params_str}
) -> Dict[str, Any]:
    """{escaped_description}"""
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
                # Escape the description for safe use in docstring
                escaped_desc = _escape_for_docstring(desc)
                server_code += f'''
@mcp.resource("{uri}")
async def resource_{uri.split("://")[1].replace("/", "_").replace("{", "").replace("}", "")}() -> List[Dict[str, Any]]:
    """{escaped_desc}"""
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
            
            # Escape the description for safe use in docstring
            escaped_desc = _escape_for_docstring(desc)
            
            server_code += f'''
@mcp.prompt
def {prompt_name}({params_str}) -> str:
    """{escaped_desc}"""
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
    
    # Add automatically detected dependencies
    suggested_deps = _suggest_dependencies(plan.get('original_requirements', ''))
    for dep in suggested_deps:
        if dep not in dependencies:
            dependencies.append(dep)
    
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
    """Generate README.md and other documentation files"""
    await ctx.info("📚 Generating documentation...")
    
    # Create comprehensive README content here (truncated for brevity)
    readme_content = f"""# {project_name}

{plan.get('description', 'Generated MCP server')}

## TODO: Implementation Required

This is a boilerplate MCP server generated by KEN-MCP. Claude needs to customize it based on these requirements:

**Original Requirements:**
> {plan.get('original_requirements', 'No requirements provided')}

## Installation

```bash
pip install -e .
```

## Usage

Add to Claude Code:
```bash
claude mcp add {project_name} "python {project_path}/server.py"
```
"""
    
    (project_path / "README.md").write_text(readme_content)
    await ctx.info("✅ Generated documentation files")

async def _validate_project(project_path: Path, ctx: Context) -> Dict[str, Any]:
    """Validate the generated project"""
    await ctx.info("✔️ Validating project...")
    
    issues = []
    warnings = []
    
    # Check required files
    required_files = ["server.py", "README.md", "pyproject.toml", ".gitignore"]
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
    
    search_dir = Path(directory) if directory else Path.cwd()
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