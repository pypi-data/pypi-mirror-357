#!/usr/bin/env python3
"""
Simple validation script to test MCP server functionality without stdio.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent / "src"))

from system_diag_mcp.server import mcp


async def test_server_creation():
    """Test that the server can be created."""
    print("🔧 Testing FastMCP server creation...")
    print(f"Server name: {mcp.name}")
    print(f"Server type: {type(mcp).__name__}")
    
    # Test that tools are registered
    tools = await mcp.list_tools()
    print(f"Found {len(tools)} tools:")
    for tool in tools[:10]:  # Show first 10 tools
        print(f"  - {tool.name}: {tool.description}")
    
    if len(tools) > 10:
        print(f"  ... and {len(tools) - 10} more tools")
    
    return True


async def test_tool_execution():
    """Test executing tools directly."""
    print("\n💻 Testing tool execution...")
    
    try:
        # Import the tool functions directly
        from system_diag_mcp.server import get_hostname, get_sys_info, check_port
        
        # Test hostname tool
        result = await get_hostname()
        data = json.loads(result)
        print(f"✅ get_hostname: {data['hostname']}")
        
        # Test system info
        result = await get_sys_info()
        data = json.loads(result)
        print(f"✅ get_sys_info: {data['platform']} - {data['cpu_count']} CPUs")
        
        # Test port check
        result = await check_port("127.0.0.1", 22)
        data = json.loads(result)
        print(f"✅ check_port: localhost:22 is {data.get('status', 'unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Tool execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run validation tests."""
    print("🚀 System Diagnostics MCP Server - Validation Test")
    print("=" * 60)
    
    try:
        # Test server creation
        success = await test_server_creation()
        if not success:
            print("❌ Server creation test failed")
            return 1
            
        # Test tool execution
        success = await test_tool_execution()
        if not success:
            print("❌ Tool execution test failed")
            return 1
            
        print("\n✅ All validation tests passed!")
        print("\n📝 To use this server with Claude Desktop, add this to your config:")
        print(json.dumps({
            "mcpServers": {
                "system-diag": {
                    "command": "system-diag-mcp"
                }
            }
        }, indent=2))
        
        return 0
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
