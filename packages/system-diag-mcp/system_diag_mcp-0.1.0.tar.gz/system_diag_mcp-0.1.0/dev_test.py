#!/usr/bin/env python3
"""
Development script for testing the system diagnostics MCP server.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent / "src"))

from system_diag_mcp.server import mcp


async def test_tools():
    """Test available tools."""
    print("🔧 Testing FastMCP system diagnostics server...")
    
    # Test that tools are registered
    print(f"Found {len(mcp._tools)} tools:")
    for tool_name in mcp._tools.keys():
        print(f"  - {tool_name}")
    
    print("\n🧪 Testing core functionality...")
    
    # Test hostname
    print("\n📍 Testing get_hostname...")
    result = await mcp._tools["get_hostname"]()
    print(json.dumps(json.loads(result), indent=2))
    
    # Test system info
    print("\n💻 Testing get_sys_info...")
    result = await mcp._tools["get_sys_info"]()
    data = json.loads(result)
    print(f"Hostname: {data['hostname']}")
    print(f"Platform: {data['platform']}")
    print(f"CPU Count: {data['cpu_count']}")
    print(f"Memory Usage: {data['memory']['percent']}%")
    print(f"Disk Usage: {data['disk']['percent']:.1f}%")
    
    # Test uptime
    print("\n⏰ Testing get_uptime...")
    result = await mcp._tools["get_uptime"]()
    data = json.loads(result)
    print(f"System uptime: {data['uptime_formatted']}")
    
    # Test port check (on localhost:22 - likely to be SSH)
    print("\n🔌 Testing check_port (localhost:22)...")
    result = await mcp._tools["check_port"]("127.0.0.1", 22)
    data = json.loads(result)
    print(f"Port 22 status: {data.get('status', 'unknown')}")
    
    # Test memory check
    print("\n🧠 Testing check_memory...")
    result = await mcp._tools["check_memory"]()
    data = json.loads(result)
    print(f"Memory: {data['memory']['percent']}% used")
    print(f"Swap: {data['swap']['percent']}% used")
    
    # Test process list (top 5)
    print("\n📋 Testing list_processes (top 5 by CPU)...")
    result = await mcp._tools["list_processes"]("", "cpu")
    data = json.loads(result)
    for i, proc in enumerate(data[:5]):
        print(f"  {i+1}. {proc['name']} (PID: {proc['pid']}, CPU: {proc['cpu_percent']}%)")
    
    print("\n✅ All tests completed!")


if __name__ == "__main__":
    print("🚀 System Diagnostics MCP Server - Development Test")
    print("=" * 50)
    asyncio.run(test_tools())
