# PromptLab MCP Server 启动脚本 (PowerShell)
# 编码: UTF-8

# 设置控制台编码
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    PromptLab MCP Server 启动脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查当前目录
$currentDir = Get-Location
Write-Host "[INFO] 当前目录: $currentDir" -ForegroundColor Yellow

# 步骤1: 检查虚拟环境
Write-Host "[1/4] 检查虚拟环境..." -ForegroundColor Green
if (-not (Test-Path "venv\Scripts\python.exe")) {
    Write-Host "❌ 错误: 虚拟环境不存在" -ForegroundColor Red
    Write-Host "请先运行: python setup_and_start.py" -ForegroundColor Yellow
    Read-Host "按任意键退出"
    exit 1
}
Write-Host "✅ 虚拟环境检查通过" -ForegroundColor Green

# 步骤2: 激活虚拟环境
Write-Host "[2/4] 激活虚拟环境..." -ForegroundColor Green
try {
    & ".\venv\Scripts\Activate.ps1"
    Write-Host "✅ 虚拟环境已激活" -ForegroundColor Green
} catch {
    Write-Host "❌ 错误: 无法激活虚拟环境" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Read-Host "按任意键退出"
    exit 1
}

# 步骤3: 检查依赖包
Write-Host "[3/4] 检查依赖包..." -ForegroundColor Green
try {
    & python -c "import mcp, langchain_google_vertexai, mlflow; print('所有依赖包已安装')"
    Write-Host "✅ 依赖包检查通过" -ForegroundColor Green
} catch {
    Write-Host "❌ 错误: 依赖包未正确安装" -ForegroundColor Red
    Write-Host "请运行: pip install -r requirements.txt" -ForegroundColor Yellow
    Read-Host "按任意键退出"
    exit 1
}

# 步骤4: 启动服务器
Write-Host "[4/4] 启动 PromptLab MCP Server..." -ForegroundColor Green
Write-Host ""
Write-Host "🚀 MCP Server 正在启动..." -ForegroundColor Cyan
Write-Host "📝 使用 Ctrl+C 停止服务器" -ForegroundColor Yellow
Write-Host "📋 服务器日志:" -ForegroundColor Magenta
Write-Host ""

try {
    & python promptlab_server.py
} catch {
    Write-Host "❌ 服务器启动失败" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
} finally {
    Write-Host ""
    Write-Host "服务器已停止" -ForegroundColor Yellow
    Read-Host "按任意键退出"
}