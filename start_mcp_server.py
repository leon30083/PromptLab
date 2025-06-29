#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PromptLab MCP Server 启动脚本
跨平台启动脚本，支持 Windows、Linux、macOS
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_banner():
    """打印启动横幅"""
    print("=" * 50)
    print("    PromptLab MCP Server 启动脚本")
    print("=" * 50)
    print()

def check_python_version():
    """检查Python版本"""
    print("[INFO] 检查Python版本...")
    version = sys.version_info
    print(f"[INFO] Python版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ 错误: 需要Python 3.8或更高版本")
        return False
    
    print("✅ Python版本检查通过")
    return True

def check_virtual_env():
    """检查虚拟环境"""
    print("[1/4] 检查虚拟环境...")
    
    venv_path = Path("venv")
    if platform.system() == "Windows":
        python_exe = venv_path / "Scripts" / "python.exe"
        activate_script = venv_path / "Scripts" / "Activate.ps1"
    else:
        python_exe = venv_path / "bin" / "python"
        activate_script = venv_path / "bin" / "activate"
    
    if not python_exe.exists():
        print("❌ 错误: 虚拟环境不存在")
        print("请先运行: python setup_and_start.py")
        return False, None
    
    print("✅ 虚拟环境检查通过")
    return True, str(python_exe)

def check_dependencies(python_exe):
    """检查依赖包"""
    print("[2/4] 检查依赖包...")
    
    try:
        # 检查核心依赖
        result = subprocess.run([
            python_exe, "-c", 
            "import mcp, langchain_google_vertexai, mlflow; print('所有依赖包已安装')"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            print("❌ 错误: 依赖包未正确安装")
            print(f"错误信息: {result.stderr}")
            print("请运行: pip install -r requirements.txt")
            return False
        
        print("✅ 依赖包检查通过")
        return True
        
    except subprocess.TimeoutExpired:
        print("❌ 错误: 依赖包检查超时")
        return False
    except Exception as e:
        print(f"❌ 错误: 依赖包检查失败 - {e}")
        return False

def check_server_file():
    """检查服务器文件"""
    print("[3/4] 检查服务器文件...")
    
    server_file = Path("promptlab_server.py")
    if not server_file.exists():
        print("❌ 错误: promptlab_server.py 文件不存在")
        return False
    
    print("✅ 服务器文件检查通过")
    return True

def start_server(python_exe):
    """启动MCP服务器"""
    print("[4/4] 启动 PromptLab MCP Server...")
    print()
    print("🚀 MCP Server 正在启动...")
    print("📝 使用 Ctrl+C 停止服务器")
    print("📋 服务器日志:")
    print("-" * 40)
    
    try:
        # 启动服务器
        process = subprocess.run([python_exe, "promptlab_server.py"])
        return process.returncode == 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️  服务器被用户中断")
        return True
    except Exception as e:
        print(f"\n❌ 服务器启动失败: {e}")
        return False

def main():
    """主函数"""
    print_banner()
    
    # 检查Python版本
    if not check_python_version():
        input("按回车键退出...")
        sys.exit(1)
    
    # 检查虚拟环境
    venv_ok, python_exe = check_virtual_env()
    if not venv_ok:
        input("按回车键退出...")
        sys.exit(1)
    
    # 检查依赖包
    if not check_dependencies(python_exe):
        input("按回车键退出...")
        sys.exit(1)
    
    # 检查服务器文件
    if not check_server_file():
        input("按回车键退出...")
        sys.exit(1)
    
    # 启动服务器
    success = start_server(python_exe)
    
    print("\n" + "=" * 40)
    if success:
        print("✅ 服务器已正常停止")
    else:
        print("❌ 服务器异常退出")
    
    input("按回车键退出...")

if __name__ == "__main__":
    main()