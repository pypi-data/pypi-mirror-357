#!/usr/bin/env python3
"""
Test the MCP server using stdin/stdout communication.
"""

import json
import subprocess
import sys
import time

def test_mcp_communication():
    """Test MCP protocol communication."""
    print("🔧 Testing MCP stdio communication...")
    
    # Start the server process
    process = subprocess.Popen(
        ["python3", "-m", "system_diag_mcp.server"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd="/home/lavi.sidana/Workspace/public_html/system-diag-mcp"
    )
    
    try:
        # Send initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-06-18",
                "capabilities": {
                    "tools": {}
                },
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        print("📤 Sending initialize request...")
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()
        
        # Wait for response with timeout
        start_time = time.time()
        timeout = 5  # 5 seconds timeout
        
        output_lines = []
        while time.time() - start_time < timeout:
            if process.poll() is not None:
                # Process has terminated
                break
                
            # Try to read a line
            try:
                process.stdout.settimeout(0.1)
                line = process.stdout.readline()
                if line:
                    output_lines.append(line.strip())
                    print(f"📥 Received: {line.strip()}")
                    
                    # Try to parse as JSON
                    try:
                        response = json.loads(line.strip())
                        if response.get("id") == 1:
                            print("✅ Received initialize response!")
                            return True
                    except json.JSONDecodeError:
                        continue
            except:
                time.sleep(0.1)
                continue
        
        print("⏰ Timeout waiting for response")
        return False
        
    except Exception as e:
        print(f"❌ Error during communication: {e}")
        return False
        
    finally:
        # Clean up process
        try:
            process.terminate()
            process.wait(timeout=2)
        except:
            process.kill()


def test_executable():
    """Test that the executable can be found and started."""
    print("🚀 Testing system-diag-mcp executable...")
    
    try:
        # Test that the command exists
        result = subprocess.run(
            ["which", "system-diag-mcp"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            print(f"✅ Executable found at: {result.stdout.strip()}")
            
            # Test starting the server briefly
            process = subprocess.Popen(
                ["system-diag-mcp"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            time.sleep(1)  # Give it a moment to start
            
            if process.poll() is None:
                print("✅ Server process started successfully")
                process.terminate()
                process.wait(timeout=2)
                return True
            else:
                stderr = process.stderr.read()
                print(f"❌ Server process exited immediately: {stderr}")
                return False
                
        else:
            print("❌ Executable not found in PATH")
            return False
            
    except Exception as e:
        print(f"❌ Error testing executable: {e}")
        return False


def main():
    """Run MCP communication tests."""
    print("🧪 System Diagnostics MCP Server - Communication Test")
    print("=" * 60)
    
    success = True
    
    # Test executable
    if not test_executable():
        print("❌ Executable test failed")
        success = False
    
    # Test MCP communication
    if not test_mcp_communication():
        print("❌ MCP communication test failed")
        success = False
    
    if success:
        print("\n✅ All communication tests passed!")
        print("\n🎉 Your MCP server is ready to use!")
        print("\n📋 Installation complete. To use with Claude Desktop:")
        print("1. Copy the configuration from validate.py output")
        print("2. Add it to your Claude Desktop config file")
        print("3. Restart Claude Desktop")
    else:
        print("\n❌ Some tests failed. Check the output above.")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
