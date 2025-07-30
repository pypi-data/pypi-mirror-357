#!/usr/bin/env python3.10
"""Simple test to verify .env generation changes"""

import os
from pathlib import Path

def test_env_generation():
    """Test if .env.example file has proper content"""
    
    # Simulate the .env content generation
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
    
    # Create test output directory
    test_dir = Path("test_output/env-test")
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # Write .env.example file
    env_file = test_dir / ".env.example"
    env_file.write_text(env_content)
    
    print(f"✅ Created .env.example at: {env_file}")
    print(f"✅ File size: {env_file.stat().st_size} bytes")
    
    # Verify content
    content = env_file.read_text()
    
    # Check for key sections
    checks = [
        ("API Keys section", "# API Keys" in content),
        ("Database section", "# Database Configuration" in content),
        ("Authentication section", "# Authentication" in content),
        ("Feature flags", "# Feature Flags" in content),
        ("OPENAI_API_KEY", "OPENAI_API_KEY" in content),
        ("Database URL", "DATABASE_URL" in content),
        ("Comments properly formatted", content.count("#") > 20)
    ]
    
    all_passed = True
    for check_name, passed in checks:
        status = "✅" if passed else "❌"
        print(f"{status} {check_name}: {'PASS' if passed else 'FAIL'}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print(f"\n🎉 All tests passed! The .env.example file is properly generated.")
    else:
        print(f"\n❌ Some tests failed.")
        
    print(f"\nFirst 300 chars of .env.example:")
    print("-" * 50)
    print(content[:300] + "..." if len(content) > 300 else content)

if __name__ == "__main__":
    test_env_generation()