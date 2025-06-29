#!/usr/bin/env python3
"""
PromptLab Setup and Start Script
This script helps users set up and start the PromptLab MCP server
"""

import os
import sys
import subprocess
import time
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm

console = Console()

def print_banner():
    """Print the PromptLab banner"""
    banner = """
    ██████╗ ██████╗  ██████╗ ███╗   ███╗██████╗ ████████╗██╗      █████╗ ██████╗ 
    ██╔══██╗██╔══██╗██╔═══██╗████╗ ████║██╔══██╗╚══██╔══╝██║     ██╔══██╗██╔══██╗
    ██████╔╝██████╔╝██║   ██║██╔████╔██║██████╔╝   ██║   ██║     ███████║██████╔╝
    ██╔═══╝ ██╔══██╗██║   ██║██║╚██╔╝██║██╔═══╝    ██║   ██║     ██╔══██║██╔══██╗
    ██║     ██║  ██║╚██████╔╝██║ ╚═╝ ██║██║        ██║   ███████╗██║  ██║██████╔╝
    ╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝╚═╝        ╚═╝   ╚══════╝╚═╝  ╚═╝╚═════╝ 
    
    🤖 MCP Server for AI Query Enhancement with Gemini 2.5 Pro
    """
    console.print(Panel(banner, style="bold blue"))

def check_python_version():
    """Check if Python version is 3.12+"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 12):
        console.print("❌ Python 3.12+ is required. Current version: {}.{}.{}".format(
            version.major, version.minor, version.micro), style="bold red")
        return False
    console.print(f"✅ Python {version.major}.{version.minor}.{version.micro}", style="bold green")
    return True

def check_virtual_env():
    """Check if virtual environment is activated"""
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        console.print("⚠️  Virtual environment not detected", style="bold yellow")
        if Confirm.ask("Do you want to create and activate a virtual environment?"):
            return setup_virtual_env()
        return False
    console.print("✅ Virtual environment activated", style="bold green")
    return True

def setup_virtual_env():
    """Set up virtual environment"""
    try:
        console.print("🔧 Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        
        # Provide activation instructions
        console.print("\n📋 Virtual environment created successfully!")
        console.print("Please activate it manually and run this script again:")
        if os.name == 'nt':  # Windows
            console.print("   .\\venv\\Scripts\\Activate.ps1", style="bold cyan")
        else:  # Linux/Mac
            console.print("   source venv/bin/activate", style="bold cyan")
        return False
    except subprocess.CalledProcessError:
        console.print("❌ Failed to create virtual environment", style="bold red")
        return False

def install_dependencies():
    """Install required dependencies"""
    try:
        console.print("📦 Installing dependencies...")
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Installing packages...", total=None)
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                capture_output=True,
                text=True
            )
            progress.remove_task(task)
        
        if result.returncode == 0:
            console.print("✅ Dependencies installed successfully", style="bold green")
            return True
        else:
            console.print(f"❌ Failed to install dependencies: {result.stderr}", style="bold red")
            return False
    except Exception as e:
        console.print(f"❌ Error installing dependencies: {e}", style="bold red")
        return False

def check_env_file():
    """Check and create .env file if needed"""
    env_path = Path('.env')
    if not env_path.exists():
        console.print("⚠️  .env file not found", style="bold yellow")
        if Confirm.ask("Do you want to create a .env file?"):
            return create_env_file()
        return False
    
    console.print("✅ .env file found", style="bold green")
    return True

def create_env_file():
    """Create .env file with user input"""
    console.print("\n🔧 Creating .env file...")
    
    gcp_project = Prompt.ask("Enter your GCP Project ID")
    gcp_location = Prompt.ask("Enter GCP Location", default="us-central1")
    mlflow_uri = Prompt.ask("Enter MLflow Tracking URI", default="http://127.0.0.1:5000")
    
    env_content = f"""GCP_PROJECT_ID="{gcp_project}"
GCP_LOCATION="{gcp_location}"
MLFLOW_TRACKING_URI="{mlflow_uri}"
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        console.print("✅ .env file created successfully", style="bold green")
        return True
    except Exception as e:
        console.print(f"❌ Failed to create .env file: {e}", style="bold red")
        return False

def check_gcp_auth():
    """Check Google Cloud authentication"""
    try:
        result = subprocess.run(
            ["gcloud", "auth", "application-default", "print-access-token"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            console.print("✅ Google Cloud authentication verified", style="bold green")
            return True
        else:
            console.print("⚠️  Google Cloud authentication needed", style="bold yellow")
            if Confirm.ask("Do you want to authenticate with Google Cloud?"):
                return setup_gcp_auth()
            return False
    except FileNotFoundError:
        console.print("❌ Google Cloud CLI not found. Please install it first.", style="bold red")
        console.print("Visit: https://cloud.google.com/sdk/docs/install")
        return False

def setup_gcp_auth():
    """Set up Google Cloud authentication"""
    try:
        console.print("🔧 Setting up Google Cloud authentication...")
        subprocess.run(["gcloud", "auth", "application-default", "login"], check=True)
        console.print("✅ Google Cloud authentication completed", style="bold green")
        return True
    except subprocess.CalledProcessError:
        console.print("❌ Failed to authenticate with Google Cloud", style="bold red")
        return False

def start_mlflow_server():
    """Start MLflow server"""
    console.print("\n🚀 Starting MLflow server...")
    console.print("💡 MLflow will run in the background. You can access it at http://127.0.0.1:5000")
    
    try:
        # Start MLflow server in background
        process = subprocess.Popen(
            ["mlflow", "server", "--host", "127.0.0.1", "--port", "5000"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        # Wait a bit for server to start
        time.sleep(3)
        
        # Check if process is still running
        if process.poll() is None:
            console.print("✅ MLflow server started successfully", style="bold green")
            return True
        else:
            console.print("❌ MLflow server failed to start", style="bold red")
            return False
    except FileNotFoundError:
        console.print("❌ MLflow not found. Please install it: pip install mlflow", style="bold red")
        return False

def register_sample_prompts():
    """Register sample prompts"""
    console.print("\n📝 Registering sample prompts...")
    try:
        result = subprocess.run(
            [sys.executable, "register_prompts.py", "register-samples"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            console.print("✅ Sample prompts registered successfully", style="bold green")
            return True
        else:
            console.print(f"❌ Failed to register prompts: {result.stderr}", style="bold red")
            return False
    except Exception as e:
        console.print(f"❌ Error registering prompts: {e}", style="bold red")
        return False

def test_mcp_server():
    """Test the MCP server"""
    console.print("\n🧪 Testing MCP server...")
    try:
        result = subprocess.run(
            [sys.executable, "test_mcp.py"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            console.print("✅ MCP server test passed", style="bold green")
            return True
        else:
            console.print(f"⚠️  MCP server test had issues: {result.stderr}", style="bold yellow")
            return True  # Continue anyway
    except Exception as e:
        console.print(f"❌ Error testing MCP server: {e}", style="bold red")
        return False

def print_final_instructions():
    """Print final setup instructions"""
    instructions = """
🎉 PromptLab MCP Server Setup Complete!

📋 Next Steps:

1. Add PromptLab to your MCP client configuration:
   • For Claude Desktop: Add the server config to claude_desktop_config.json
   • For Cline: Use the provided mcp.json file
   • For other clients: Use the MCP configuration provided

2. Restart your MCP client to load the new server

3. Start using PromptLab tools:
   • optimize_query - Enhance your queries
   • list_prompts - See available templates
   • reload_prompts - Refresh prompt cache

🔧 Manual Start Commands (if needed):
   • MLflow: mlflow server --host 127.0.0.1 --port 5000
   • MCP Server: python promptlab_server.py
   • Test: python test_mcp.py

📖 For detailed documentation, see README.md
    """
    console.print(Panel(instructions, style="bold green"))

def main():
    """Main setup function"""
    print_banner()
    
    console.print("\n🔍 Checking system requirements...\n")
    
    # Check all requirements
    checks = [
        ("Python version", check_python_version),
        ("Virtual environment", check_virtual_env),
        ("Dependencies", install_dependencies),
        ("Environment file", check_env_file),
        ("Google Cloud auth", check_gcp_auth),
    ]
    
    for name, check_func in checks:
        console.print(f"\n🔍 Checking {name}...")
        if not check_func():
            console.print(f"\n❌ Setup failed at: {name}", style="bold red")
            console.print("Please fix the issue and run the script again.")
            sys.exit(1)
    
    # Start services
    console.print("\n🚀 Starting services...")
    
    if not start_mlflow_server():
        console.print("⚠️  MLflow server failed to start, but continuing...", style="bold yellow")
    
    time.sleep(2)  # Wait for MLflow to be ready
    
    if not register_sample_prompts():
        console.print("⚠️  Failed to register sample prompts, but continuing...", style="bold yellow")
    
    if not test_mcp_server():
        console.print("⚠️  MCP server test failed, but setup is complete", style="bold yellow")
    
    print_final_instructions()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n👋 Setup cancelled by user", style="bold yellow")
    except Exception as e:
        console.print(f"\n❌ Unexpected error: {e}", style="bold red")
        sys.exit(1)