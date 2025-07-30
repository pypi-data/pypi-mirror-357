#!/usr/bin/env python3.10
"""
KEN-MCP Server
This file runs the MCP Generator server defined in mcp_generator.py
"""

from mcp_generator import mcp

if __name__ == "__main__":
    mcp.run()