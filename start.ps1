# PromptLab 一键启动脚本
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║    🚀 PromptLab 一键启动                                      ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# 切换到脚本目录
Set-Location $PSScriptRoot

# 检查Python
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ 未找到Python，请先安装Python 3.8+" -ForegroundColor Red
        Read-Host "按Enter键退出"
        exit 1
    }
    Write-Host "✅ Python检查通过: $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "❌ Python检查失败" -ForegroundColor Red
    Read-Host "按Enter键退出"
    exit 1
}

# 激活虚拟环境（如果存在）
$venvPath = Join-Path $PSScriptRoot "venv\Scripts\Activate.ps1"
if (Test-Path $venvPath) {
    Write-Host "🔧 激活虚拟环境..." -ForegroundColor Yellow
    try {
        & $venvPath
        Write-Host "✅ 虚拟环境已激活" -ForegroundColor Green
    }
    catch {
        Write-Host "⚠️  虚拟环境激活失败，使用系统Python" -ForegroundColor Yellow
    }
}
else {
    Write-Host "ℹ️  未找到虚拟环境，使用系统Python" -ForegroundColor Blue
}

# 安装依赖（如果需要）
Write-Host "🔍 检查依赖..." -ForegroundColor Yellow
if (Test-Path "requirements.txt") {
    try {
        pip install -r requirements.txt --quiet
        Write-Host "✅ 依赖检查完成" -ForegroundColor Green
    }
    catch {
        Write-Host "⚠️  依赖安装可能有问题，但继续启动" -ForegroundColor Yellow
    }
}
else {
    Write-Host "⚠️  未找到requirements.txt" -ForegroundColor Yellow
}

# 启动服务器
Write-Host "" 
Write-Host "🚀 启动PromptLab服务器..." -ForegroundColor Cyan
Write-Host ""

try {
    python start_enhanced_promptlab.py
}
catch {
    Write-Host "❌ 启动失败: $($_.Exception.Message)" -ForegroundColor Red
}
finally {
    Write-Host ""
    Write-Host "服务器已停止" -ForegroundColor Yellow
    Read-Host "按Enter键退出"
}