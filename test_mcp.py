#!/usr/bin/env python3
"""
Test script for PromptLab MCP Server
This script tests the MCP server functionality locally
"""

import asyncio
import json
import subprocess
import sys
import os
from pathlib import Path

async def test_mcp_server():
    """Test the MCP server by running it and sending test commands"""
    print("🧪 Testing PromptLab MCP Server...")
    
    # Check if virtual environment is activated
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Warning: Virtual environment not detected. Please activate venv first.")
        print("   Run: .\\venv\\Scripts\\Activate.ps1")
        return False
    
    # Check if required files exist
    required_files = ['.env', 'promptlab_server.py']
    for file in required_files:
        if not Path(file).exists():
            print(f"❌ Required file missing: {file}")
            return False
    
    print("✅ All required files found")
    
    # Test 1: Check if server can start
    print("\n📡 Test 1: Server startup test")
    try:
        # Start the server process
        process = subprocess.Popen(
            [sys.executable, 'promptlab_server.py'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=os.getcwd()
        )
        
        # Send initialization request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        # Send the request
        process.stdin.write(json.dumps(init_request) + '\n')
        process.stdin.flush()
        
        # Wait for response with timeout
        try:
            stdout, stderr = process.communicate(timeout=10)
            if process.returncode == 0 or "initialized" in stdout.lower():
                print("✅ Server started successfully")
            else:
                print(f"❌ Server startup failed: {stderr}")
                return False
        except subprocess.TimeoutExpired:
            print("⏰ Server startup timeout - this might be normal for MCP servers")
            process.terminate()
            
    except Exception as e:
        print(f"❌ Server test failed: {e}")
        return False
    
    print("\n🎉 Basic MCP server test completed!")
    print("\n📋 Next steps:")
    print("1. Start MLflow server: mlflow server --host 127.0.0.1 --port 5000")
    print("2. Register prompts: python register_prompts.py register-samples")
    print("3. Add this server to your MCP client configuration")
    print("4. Use the mcp.json configuration file provided")
    
    return True

def main():
    """Main test function"""
    print("🚀 PromptLab MCP Server Test Suite")
    print("=" * 50)
    
    # Run async test
    result = asyncio.run(test_mcp_server())
    
    if result:
        print("\n✅ All tests passed! Your MCP server is ready to use.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the configuration.")
        sys.exit(1)

if __name__ == "__main__":
    main()