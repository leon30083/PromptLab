@echo off
chcp 65001 >nul
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║    🚀 Enhanced PromptLab MCP Server                          ║
echo ║                                                              ║
echo ║    多模型AI提示词优化平台                                      ║
echo ║    Multi-Model AI Prompt Optimization Platform              ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo 正在启动增强版 PromptLab 服务器...
echo.

cd /d "%~dp0"

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

REM 检查虚拟环境
if exist "venv\Scripts\activate.bat" (
    echo 🔧 激活虚拟环境...
    call venv\Scripts\activate.bat
)

REM 检查依赖
echo 🔍 检查依赖包...
python -c "import mcp, mlflow, langchain" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  缺少依赖包，正在安装...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ 依赖安装失败，请手动运行: pip install -r requirements.txt
        pause
        exit /b 1
    )
)

REM 启动服务器
echo ✅ 启动增强版服务器...
echo.
python start_enhanced_promptlab.py

echo.
echo 服务器已停止
pause