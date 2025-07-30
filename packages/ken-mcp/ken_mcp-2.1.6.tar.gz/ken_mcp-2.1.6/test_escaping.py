#!/usr/bin/env python3

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

# Test the function
test_string = r'Handle paths like C:\Users\Test\file.txt and quotes "test"'
escaped = _escape_for_docstring(test_string)
print('Original:', repr(test_string))
print('Escaped:', repr(escaped))

# Test in a docstring
try:
    docstring_test = f'''"""
    Test requirements: {escaped}
    """'''
    print("Docstring test successful:")
    print(docstring_test)
    
    # Try to compile it
    compile(docstring_test, '<string>', 'eval')
    print("✅ Compilation successful!")
except SyntaxError as e:
    print(f"❌ Syntax error: {e}")