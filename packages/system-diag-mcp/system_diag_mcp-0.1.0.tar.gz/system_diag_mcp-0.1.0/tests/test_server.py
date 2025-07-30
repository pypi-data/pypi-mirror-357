"""Tests for the system diagnostics MCP server."""

import asyncio
import json
import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from system_diag_mcp.server import (
    mcp, run_command, get_hostname, get_sys_info, check_port, 
    list_processes, check_memory, list_network_interfaces
)


@pytest.mark.asyncio
async def test_available_tools():
    """Test that tools are available in the FastMCP server."""
    tools = await mcp.list_tools()
    assert len(tools) == 27
    
    tool_names = [tool.name for tool in tools]
    
    # Check some key tools
    assert "get_hostname" in tool_names
    assert "get_sys_info" in tool_names
    assert "check_port" in tool_names
    assert "list_processes" in tool_names


def test_run_command():
    """Test the run_command helper function."""
    # Test successful command
    result = run_command(["echo", "hello"])
    assert result["success"] is True
    assert result["stdout"] == "hello"
    assert result["returncode"] == 0
    
    # Test command that doesn't exist
    result = run_command(["nonexistent_command"])
    assert result["success"] is False
    assert result["returncode"] != 0


@pytest.mark.asyncio
async def test_get_hostname():
    """Test the get_hostname tool."""
    result = await get_hostname()
    data = json.loads(result)
    assert "hostname" in data
    assert "fqdn" in data


@pytest.mark.asyncio
async def test_get_sys_info():
    """Test the get_sys_info tool."""
    result = await get_sys_info()
    data = json.loads(result)
    assert "hostname" in data
    assert "platform" in data
    assert "cpu_count" in data
    assert "memory" in data
    assert "disk" in data


@pytest.mark.asyncio
async def test_check_port():
    """Test the check_port tool."""
    # Test checking a likely closed port (using a valid port number)
    result = await check_port("127.0.0.1", 9999)
    data = json.loads(result)
    assert "host" in data
    assert "port" in data
    assert "status" in data


@pytest.mark.asyncio
async def test_list_processes():
    """Test the list_processes tool."""
    result = await list_processes()
    data = json.loads(result)
    assert isinstance(data, list)
    if len(data) > 0:
        process = data[0]
        assert "pid" in process
        assert "name" in process


@pytest.mark.asyncio
async def test_check_memory():
    """Test the check_memory tool."""
    result = await check_memory()
    data = json.loads(result)
    assert "memory" in data
    assert "swap" in data
    assert "total" in data["memory"]
    assert "used" in data["memory"]


@pytest.mark.asyncio
async def test_list_network_interfaces():
    """Test the list_network_interfaces tool."""
    result = await list_network_interfaces()
    data = json.loads(result)
    assert isinstance(data, dict)
    # Should have at least loopback interface
    assert len(data) > 0


if __name__ == "__main__":
    pytest.main([__file__])
