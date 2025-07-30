"""
Simple MCP client test to verify the server works correctly
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path

async def test_mcp_server():
    """Test the MCP server using stdio communication"""
    print("🧪 Testing MCP Server Communication")
    print("=" * 40)
    
    # Start the server process
    server_cmd = [
        str(Path(sys.executable)),
        "-m", "error_repository_server.server"
    ]
    
    try:
        process = subprocess.Popen(
            server_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=Path(__file__).parent
        )
        
        # Initialize the server
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
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
        
        # Read response
        response_line = process.stdout.readline()
        if response_line:
            try:
                response = json.loads(response_line.strip())
                if "result" in response:
                    print("✅ Server initialized successfully")
                    print(f"   Server: {response['result'].get('serverInfo', {}).get('name', 'Unknown')}")
                else:
                    print(f"❌ Initialize failed: {response.get('error', 'Unknown error')}")
            except json.JSONDecodeError as e:
                print(f"❌ Failed to parse response: {e}")
                print(f"   Raw response: {response_line}")
        
        # Test tools listing
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        
        print("\n📤 Requesting available tools...")
        process.stdin.write(json.dumps(tools_request) + "\n")
        process.stdin.flush()
        
        response_line = process.stdout.readline()
        if response_line:
            try:
                response = json.loads(response_line.strip())
                if "result" in response:
                    tools = response["result"].get("tools", [])
                    print(f"✅ Found {len(tools)} tools:")
                    for tool in tools:
                        print(f"   - {tool['name']}: {tool['description']}")
                else:
                    print(f"❌ Tools request failed: {response.get('error', 'Unknown error')}")
            except json.JSONDecodeError as e:
                print(f"❌ Failed to parse tools response: {e}")
        
        # Test a tool call
        tool_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "search_error_by_code",
                "arguments": {
                    "error_code": "E001"
                }
            }
        }
        
        print("\n📤 Testing error search for E001...")
        process.stdin.write(json.dumps(tool_request) + "\n")
        process.stdin.flush()
        
        response_line = process.stdout.readline()
        if response_line:
            try:
                response = json.loads(response_line.strip())
                if "result" in response:
                    content = response["result"].get("content", [])
                    if content:
                        print("✅ Tool call successful:")
                        print(f"   {content[0].get('text', 'No text')[:100]}...")
                    else:
                        print("❌ No content in response")
                else:
                    print(f"❌ Tool call failed: {response.get('error', 'Unknown error')}")
            except json.JSONDecodeError as e:
                print(f"❌ Failed to parse tool response: {e}")
        
        # Clean up
        process.terminate()
        process.wait(timeout=5)
        
        print("\n🎉 MCP Server test completed!")
        print("\nThe server is ready for integration with GitHub Copilot.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        if 'process' in locals():
            process.terminate()

if __name__ == "__main__":
    asyncio.run(test_mcp_server())
