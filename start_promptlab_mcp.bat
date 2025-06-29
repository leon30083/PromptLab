@echo off
chcp 65001 >nul
echo ========================================
echo    PromptLab MCP Server 启动脚本
echo ========================================
echo.

echo [1/4] 检查虚拟环境...
if not exist "venv\Scripts\python.exe" (
    echo ❌ 错误: 虚拟环境不存在，请先运行 setup_and_start.py
    pause
    exit /b 1
)

echo [2/4] 激活虚拟环境...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ 错误: 无法激活虚拟环境
    pause
    exit /b 1
)

echo [3/4] 检查依赖包...
python -c "import mcp, langchain_google_vertexai, mlflow" 2>nul
if errorlevel 1 (
    echo ❌ 错误: 依赖包未正确安装，请运行: pip install -r requirements.txt
    pause
    exit /b 1
)

echo [4/4] 启动 PromptLab MCP Server...
echo.
echo 🚀 MCP Server 正在启动...
echo 📝 使用 Ctrl+C 停止服务器
echo.
python promptlab_server.py

echo.
echo 服务器已停止
pause