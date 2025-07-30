# Claude Implementation Guide

This guide helps Claude implement the MCP server based on the requirements.

## Original Requirements
```
Create an MCP that analyzes text files and documents. It should be able to read various file types (txt, md, py, js, etc.), count words, lines, and characters, extract keywords, analyze sentiment, and generate summaries. The MCP should also be able to find similar files based on content analysis and provide file statistics.
```

## FastMCP Quick Reference

### Essential Patterns

#### 1. Basic Tool Structure
```python
@mcp.tool
async def tool_name(ctx: Context, param1: str, param2: Optional[int] = None) -> Dict[str, Any]:
    """Tool description"""
    # Logging
    await ctx.info("Starting tool execution...")
    
    # Progress reporting
    await ctx.report_progress(50, 100, "Processing...")
    
    # Error handling
    if not param1:
        raise ToolError("param1 is required")
    
    # Return structured data
    return {"status": "success", "data": result}
```

#### 2. Resource Patterns
```python
# Static resource
@mcp.resource("data://items")
def get_items() -> List[Dict[str, Any]]:
    return [{"id": 1, "name": "Item 1"}]

# Dynamic resource with parameters
@mcp.resource("data://items/{item_id}")
async def get_item(item_id: str) -> Dict[str, Any]:
    # Fetch and return specific item
    return {"id": item_id, "name": f"Item {item_id}"}
```

#### 3. Prompt Patterns
```python
@mcp.prompt
def help_prompt(topic: str) -> str:
    return f"Please explain {topic} in detail"

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
    """Create a new item"""
    import json
    from pathlib import Path
    import uuid
    
    # Generate ID
    item_id = str(uuid.uuid4())[:8]
    
    # Create item
    item = {
        "id": item_id,
        "name": name,
        "description": description,
        "created_at": datetime.now().isoformat()
    }
    
    # Save to file (or database)
    storage_dir = Path.home() / ".mcp_data" / "items"
    storage_dir.mkdir(parents=True, exist_ok=True)
    
    item_file = storage_dir / f"{item_id}.json"
    item_file.write_text(json.dumps(item, indent=2))
    
    await ctx.info(f"Created item {item_id}")
    return {"success": True, "item": item}
```

### API Integration
```python
@mcp.tool
async def fetch_data(ctx: Context, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
    """Fetch data from API"""
    import httpx
    import os
    
    # Get API key from environment
    api_key = os.getenv("API_KEY")
    if not api_key:
        raise ToolError("API_KEY not found in environment variables")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    base_url = os.getenv("API_BASE_URL", "https://api.example.com")
    full_url = f"{base_url}{endpoint}"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(full_url, params=params, headers=headers)
        response.raise_for_status()
        
    return {"status": "success", "data": response.json()}
```

### File Processing
```python
@mcp.tool
async def process_file(ctx: Context, file_path: str) -> Dict[str, Any]:
    """Process a file"""
    from pathlib import Path
    
    file = Path(file_path)
    if not file.exists():
        raise ToolError(f"File not found: {file_path}")
    
    # Process based on file type
    if file.suffix == ".json":
        import json
        data = json.loads(file.read_text())
        return {"type": "json", "data": data}
    elif file.suffix in [".txt", ".md"]:
        content = file.read_text()
        return {"type": "text", "content": content, "lines": len(content.splitlines())}
    else:
        return {"type": "binary", "size": file.stat().st_size}
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
        await ctx.report_progress(i, total, f"Processing {item}")
        # Process item
        results.append(processed_item)
    
    return {"processed": len(results), "results": results}
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
    await ctx.info(f"Error details: {str(e)}")
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
