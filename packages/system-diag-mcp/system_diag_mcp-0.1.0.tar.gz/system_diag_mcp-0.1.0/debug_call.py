#!/usr/bin/env python3
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
from system_diag_mcp.server import mcp

async def test():
    result = await mcp.call_tool('get_hostname', {})
    print(f'Type: {type(result)}')
    print(f'Value: {result}')

asyncio.run(test())
