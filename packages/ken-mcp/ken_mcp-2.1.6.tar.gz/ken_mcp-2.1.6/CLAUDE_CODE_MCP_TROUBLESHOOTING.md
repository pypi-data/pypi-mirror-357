# Claude Code MCP Troubleshooting Guide

## When User Reports MCP "Failed" Status

When a user reports that an MCP shows as "Failed" in Claude Code, follow this systematic troubleshooting process:

### Initial Assessment

1. **Check current MCP status**:
```bash
claude mcp list
```
Look for the MCP in question. It will show either:
- `✓ mcp-name    Active    python3 /path/to/server.py`
- `✗ mcp-name    Failed    python3 /path/to/server.py`

2. **Gather system information**:
```bash
# System details
echo "=== System Information ==="
uname -a
echo "Operating System: $(uname -s)"
echo "Architecture: $(uname -m)"
echo ""

# Check Python availability comprehensively
echo "=== Python Installation Analysis ==="
which python 2>/dev/null && python --version 2>/dev/null || echo "❌ python: not found"
which python3 2>/dev/null && python3 --version 2>/dev/null || echo "❌ python3: not found"

# Check specific Python versions
for version in 3.8 3.9 3.10 3.11 3.12; do
    cmd="python${version}"
    if which "$cmd" >/dev/null 2>&1; then
        echo "✅ $cmd: $($cmd --version 2>/dev/null)"
    else
        echo "❌ $cmd: not found"
    fi
done

# Check common Python locations if not in PATH
echo ""
echo "=== Checking Common Python Locations ==="
for path in /usr/bin/python3 /usr/local/bin/python3 /opt/homebrew/bin/python3 /usr/bin/python /usr/local/bin/python; do
    if [ -x "$path" ]; then
        echo "✅ Found: $path ($($path --version 2>/dev/null))"
    else
        echo "❌ Not found: $path"
    fi
done

# Package manager info
echo ""
echo "=== Package Manager Information ==="
which pip 2>/dev/null && echo "✅ pip: $(pip --version)" || echo "❌ pip: not found"
which pip3 2>/dev/null && echo "✅ pip3: $(pip3 --version)" || echo "❌ pip3: not found"
which pipx 2>/dev/null && echo "✅ pipx: $(pipx --version)" || echo "❌ pipx: not found"

# Check current directory and find MCPs
echo ""
echo "=== Current Location ==="
pwd
echo ""
echo "=== Looking for MCP servers ==="
find . -name "server.py" -type f 2>/dev/null | head -10
```

### Step-by-Step Troubleshooting

#### Step 1: Test the MCP Standalone

**ALWAYS test the MCP manually first before making any changes to Claude Code configuration:**

```bash
# Navigate to the MCP directory
cd /path/to/mcp-directory

# Test with python3 (most common)
python3 server.py

# Expected output: "Server started on stdio"
# If you see this, the MCP itself works!
```

**Common errors and their meanings:**
- `ModuleNotFoundError: No module named 'fastmcp'` → Dependencies not installed
- `python3: command not found` → Python not in PATH or not installed
- `No such file or directory` → Wrong path to server.py
- `SyntaxError` → Python version mismatch or code error

#### Step 2: Fix Dependencies

If you see import errors:

```bash
# Install dependencies in the MCP directory
cd /path/to/mcp-directory
python3 -m pip install -e .

# Verify installation
python3 -m pip list | grep fastmcp
# Should show: fastmcp 0.1.0 or higher

# Test again
python3 server.py
# Should now show: "Server started on stdio"
```

#### Step 3: Update Claude Code Configuration

Once the MCP works standalone, update Claude Code:

```bash
# Remove the failed MCP
claude mcp remove mcp-name

# IMPORTANT: Inform the user they need to exit and restart Claude Code
echo "Please EXIT Claude Code completely and restart it:"
echo "1. Type 'exit' or press Ctrl+C to exit this Claude Code session"
echo "2. Run 'claude' in your terminal to start a new Claude Code session"
echo "3. Come back here when you've restarted"
# Wait for user confirmation before proceeding
```

After user confirms restart:

```bash
# Get system-specific information
echo "=== System Information ==="
uname -a
echo ""
echo "=== Python Versions Available ==="
which python 2>/dev/null && python --version 2>/dev/null || echo "python: not found"
which python3 2>/dev/null && python3 --version 2>/dev/null || echo "python3: not found"
which python3.8 2>/dev/null && python3.8 --version 2>/dev/null || echo "python3.8: not found"
which python3.9 2>/dev/null && python3.9 --version 2>/dev/null || echo "python3.9: not found"
which python3.10 2>/dev/null && python3.10 --version 2>/dev/null || echo "python3.10: not found"
which python3.11 2>/dev/null && python3.11 --version 2>/dev/null || echo "python3.11: not found"
which python3.12 2>/dev/null && python3.12 --version 2>/dev/null || echo "python3.12: not found"
echo ""

# Find the exact Python path that works
PYTHON_CMD=$(which python3 2>/dev/null || which python 2>/dev/null || echo "")
if [ -z "$PYTHON_CMD" ]; then
    echo "❌ No Python found in PATH. Checking common locations..."
    for path in /usr/bin/python3 /usr/local/bin/python3 /opt/homebrew/bin/python3 /usr/bin/python /usr/local/bin/python; do
        if [ -x "$path" ]; then
            echo "✅ Found Python at: $path"
            PYTHON_CMD="$path"
            break
        fi
    done
fi

if [ -n "$PYTHON_CMD" ]; then
    echo "✅ Using Python: $PYTHON_CMD"
    echo "Version: $($PYTHON_CMD --version)"
    
    # Add the MCP with the correct command
    claude mcp add mcp-name "$PYTHON_CMD /absolute/path/to/server.py"
else
    echo "❌ No usable Python found. Please install Python 3.8+ first."
    exit 1
fi

# IMPORTANT: Request another restart with clear instructions
echo ""
echo "🔄 IMPORTANT: Please EXIT and restart Claude Code again:"
echo "1. Type 'exit' or press Ctrl+C to exit this Claude Code session"
echo "2. Run 'claude' in your terminal to start a new Claude Code session"
echo "3. Come back here when you've restarted so we can verify the MCP is working"
```

After user confirms second restart:

```bash
# Verify the MCP is now active
claude mcp list
# Should show: ✓ mcp-name    Active
```

### Alternative Solutions

#### If Python3 Command Not Found

Try these alternatives in order:

```bash
# Option 1: Try python instead of python3
claude mcp remove mcp-name
echo "Please EXIT Claude Code (type 'exit' or Ctrl+C) and restart with 'claude'"
# Wait for user confirmation
claude mcp add mcp-name "python /path/to/server.py"
echo "Please EXIT Claude Code (type 'exit' or Ctrl+C) and restart with 'claude'"
# Wait for user confirmation

# Option 2: Use full path from system analysis
# Based on the system information gathered above, use the specific Python found
PYTHON_PATH=$(which python3 2>/dev/null || echo "/usr/bin/python3")
claude mcp remove mcp-name
echo "Please EXIT Claude Code (type 'exit' or Ctrl+C) and restart with 'claude'"
# Wait for user confirmation
claude mcp add mcp-name "$PYTHON_PATH /path/to/server.py"
echo "Please EXIT Claude Code (type 'exit' or Ctrl+C) and restart with 'claude'"
# Wait for user confirmation

# Option 3: Try version-specific Python based on what was found
# Use the highest version Python that was detected in the system analysis
for version in python3.12 python3.11 python3.10 python3.9 python3.8; do
    if which "$version" >/dev/null 2>&1; then
        echo "Trying with $version..."
        claude mcp remove mcp-name
        echo "Please EXIT Claude Code (type 'exit' or Ctrl+C) and restart with 'claude'"
        # Wait for user confirmation
        claude mcp add mcp-name "$version /path/to/server.py"
        echo "Please EXIT Claude Code (type 'exit' or Ctrl+C) and restart with 'claude'"
        # Wait for user confirmation
        break
    fi
done
```

#### If Dependencies Keep Failing

Create a virtual environment:

```bash
cd /path/to/mcp-directory

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .

# Get the venv Python path
which python
# Example: /path/to/mcp-directory/venv/bin/python

# Update Claude Code to use venv Python
claude mcp remove mcp-name
echo "Please EXIT Claude Code (type 'exit' or Ctrl+C) and restart with 'claude'"
# Wait for user confirmation
claude mcp add mcp-name "/path/to/mcp-directory/venv/bin/python /path/to/server.py"
echo "Please EXIT Claude Code (type 'exit' or Ctrl+C) and restart with 'claude'"
# Wait for user confirmation
```

### Common Issues Checklist

Before each configuration change, check:

1. **File exists and is readable**:
```bash
ls -la /path/to/server.py
# Should show the file with read permissions
```

2. **Python can run the file**:
```bash
cd /path/to/mcp-directory
python3 server.py
# Should output: "Server started on stdio"
```

3. **Dependencies are installed**:
```bash
python3 -m pip list | grep fastmcp
# Should list fastmcp
```

4. **Path is absolute**:
```bash
# Bad: server.py, ./server.py, ~/mcp/server.py
# Good: /Users/username/mcp/server.py, /home/username/mcp/server.py
```

### Important Reminders for Users

Always inform the user:

1. **After EVERY claude mcp add/remove command**, they MUST restart Claude Code:
   ```
   "Please restart Claude Code now by running the command: claude"
   "Press Enter when you've restarted Claude Code..."
   ```

2. **The "Failed" status is generic** - we need to test manually to find the real issue

3. **Python environment matters** - the Python that Claude Code uses must have all dependencies

4. **Use absolute paths** - never use relative paths or ~ in the command

5. **Order matters**:
   - First: Fix the MCP so it runs standalone
   - Second: Remove from Claude Code and restart
   - Third: Add to Claude Code with correct command and restart
   - Fourth: Verify it's active

### Sample Troubleshooting Dialogue

```
Claude: I see the MCP is showing as "Failed". Let me help you troubleshoot this systematically. First, let me gather information about your system and check the current MCP status:

[Run: claude mcp list]

Claude: I can see your-mcp is marked as Failed. Let me analyze your system to understand what might be causing this:

[Run the comprehensive system analysis commands from above]

Claude: Based on the system analysis, I can see you have:
- Operating System: Linux x86_64
- ✅ python3: Python 3.11.2 at /usr/bin/python3
- ✅ pip3: pip 22.0.2
- ❌ python3.10: not found (this explains the issue - your MCP requires Python 3.10+)

Let me test if the MCP itself works with the available Python:

[Run: cd /path/to/your-mcp && /usr/bin/python3 server.py]

Claude: I see the error is "ModuleNotFoundError: No module named 'fastmcp'". Let me install the dependencies using your system's Python:

[Run: cd /path/to/your-mcp && /usr/bin/python3 -m pip install -e .]

Claude: Great! Dependencies are installed. Let me test again:

[Run: /usr/bin/python3 server.py]

Claude: Perfect! The MCP is working standalone with "/usr/bin/python3". Now we need to update Claude Code. First, I'll remove the failed MCP:

[Run: claude mcp remove your-mcp]

Claude: **Important**: Please EXIT Claude Code completely and restart it:
1. Type 'exit' or press Ctrl+C to exit this Claude Code session
2. Run 'claude' in your terminal to start a new Claude Code session  
3. Let me know when you've restarted so we can continue

[User confirms restart]

Claude: Thank you! Now I'll add the MCP back using the exact Python path that works on your system:

[Run: claude mcp add your-mcp "/usr/bin/python3 /absolute/path/to/server.py"]

Claude: **Important**: Please EXIT and restart Claude Code one more time:
1. Type 'exit' or press Ctrl+C to exit this Claude Code session
2. Run 'claude' in your terminal to start a new Claude Code session
3. This final restart will activate the MCP

[User confirms restart]

Claude: Excellent! Let me verify the MCP is now active:

[Run: claude mcp list]

Claude: ✅ Success! Your MCP is now showing as Active with the correct Python path. 

**Summary of what we fixed:**
- Issue: Wrong Python command and missing dependencies
- Solution: Used system-specific Python path "/usr/bin/python3" and installed fastmcp
- Your system: Linux with Python 3.11.2 
- MCP now active and ready to use!
```

### Error-Specific Solutions

#### "This environment is externally managed"

```bash
# Option 1: Use pipx
pipx install -e /path/to/mcp-directory

# Option 2: Use venv (recommended)
cd /path/to/mcp-directory
python3 -m venv venv
source venv/bin/activate
pip install -e .
# Then use venv/bin/python in Claude Code

# Option 3: Force install (not recommended)
python3 -m pip install --break-system-packages -e .
```

#### "Permission denied"

```bash
# Make file executable
chmod +x /path/to/server.py

# Check ownership
ls -la /path/to/server.py

# If needed, fix ownership
sudo chown $USER:$USER /path/to/server.py
```

#### "No module named 'dotenv'"

```bash
# The MCP needs python-dotenv
cd /path/to/mcp-directory
python3 -m pip install python-dotenv
```

### Final Verification

Always end troubleshooting with:

```bash
# Confirm MCP is active
claude mcp list
# Should show: ✓ mcp-name    Active

# Test the MCP works in Claude
echo "Try using the MCP tools in Claude Code now. For example, if it's a todo MCP, try creating a todo item."
```

## Remember

1. **Test manually first** - always run `python3 server.py` before changing Claude Code config
2. **Restart after every change** - `claude mcp add/remove` requires restart with `claude` command
3. **Use absolute paths** - no relative paths or shortcuts
4. **Fix dependencies first** - the MCP must work standalone before adding to Claude Code
5. **Be patient with users** - they may not be familiar with command line or Python

## Quick Reference Commands

```bash
# Check MCP status
claude mcp list

# Test MCP manually
cd /path/to/mcp && python3 server.py

# Install dependencies
cd /path/to/mcp && python3 -m pip install -e .

# Remove MCP (then restart)
claude mcp remove mcp-name

# Add MCP (then restart)
claude mcp add mcp-name "python3 /absolute/path/to/server.py"

# Restart Claude Code
claude
```