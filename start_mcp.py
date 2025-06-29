#!/usr/bin/env python3
"""
PromptLab MCP Server Startup Script
This script helps start the PromptLab MCP server with proper initialization
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from promptlab_server import main

def check_environment():
    """Check if the environment is properly configured"""
    print("🔍 Checking environment...")
    
    # Check if .env file exists
    if not Path('.env').exists():
        print("❌ .env file not found!")
        print("Please create a .env file with the following content:")
        print("""
GCP_PROJECT_ID="your-gcp-project-id"
GCP_LOCATION="us-central1"
MLFLOW_TRACKING_URI="http://127.0.0.1:5000"
""")
        return False
    
    # Check environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    gcp_project = os.getenv('GCP_PROJECT_ID')
    mlflow_uri = os.getenv('MLFLOW_TRACKING_URI')
    
    if not gcp_project:
        print("❌ GCP_PROJECT_ID not set in .env file")
        return False
    
    if not mlflow_uri:
        print("❌ MLFLOW_TRACKING_URI not set in .env file")
        return False
    
    print(f"✅ GCP Project: {gcp_project}")
    print(f"✅ MLflow URI: {mlflow_uri}")
    
    return True

def print_startup_info():
    """Print startup information"""
    print("🚀 PromptLab MCP Server")
    print("=" * 50)
    print("This is a Model Context Protocol (MCP) server for AI query enhancement.")
    print("\n📋 Features:")
    print("• Intelligent prompt matching using Gemini 2.5 Pro")
    print("• MLflow-based prompt template management")
    print("• Query optimization and enhancement")
    print("\n🔧 Available Tools:")
    print("• optimize_query - Enhance user queries with best-matched prompts")
    print("• list_prompts - List all available prompt templates")
    print("• reload_prompts - Reload prompts from MLflow registry")
    print("\n" + "=" * 50)

def print_usage_instructions():
    """Print usage instructions"""
    print("\n📖 Usage Instructions:")
    print("\n1. Make sure MLflow server is running:")
    print("   mlflow server --host 127.0.0.1 --port 5000")
    print("\n2. Register sample prompts (if not done already):")
    print("   python register_prompts.py register-samples")
    print("\n3. Add this server to your MCP client configuration:")
    print("   Use the mcp.json file provided in this directory")
    print("\n4. Connect from your MCP-compatible application")
    print("   (Claude Desktop, Cline, etc.)")
    print("\n" + "=" * 50)

async def start_server():
    """Start the MCP server"""
    print_startup_info()
    
    if not check_environment():
        print("\n❌ Environment check failed. Please fix the issues above.")
        sys.exit(1)
    
    print_usage_instructions()
    print("\n🎯 Starting PromptLab MCP Server...")
    print("💡 Tip: This server uses stdio transport - it communicates via stdin/stdout")
    print("🔄 Server is now ready to accept MCP requests...\n")
    
    # Start the main server
    await main()

if __name__ == "__main__":
    try:
        asyncio.run(start_server())
    except KeyboardInterrupt:
        print("\n👋 PromptLab MCP Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        sys.exit(1)