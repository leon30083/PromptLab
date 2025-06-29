#!/usr/bin/env pwsh
# Enhanced PromptLab MCP Server PowerShell Startup Script
# 增强版 PromptLab MCP 服务器 PowerShell 启动脚本

# 设置控制台编码为UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# 显示启动横幅
function Show-Banner {
    Write-Host ""
    Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║                                                              ║" -ForegroundColor Cyan
    Write-Host "║    🚀 Enhanced PromptLab MCP Server                          ║" -ForegroundColor Cyan
    Write-Host "║                                                              ║" -ForegroundColor Cyan
    Write-Host "║    多模型AI提示词优化平台                                      ║" -ForegroundColor Cyan
    Write-Host "║    Multi-Model AI Prompt Optimization Platform              ║" -ForegroundColor Cyan
    Write-Host "║                                                              ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
}

# 检查Python版本
function Test-PythonVersion {
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ 错误: 未找到Python，请先安装Python 3.8+" -ForegroundColor Red
            return $false
        }
        
        $versionMatch = $pythonVersion -match "Python (\d+)\.(\d+)"
        if ($versionMatch) {
            $major = [int]$matches[1]
            $minor = [int]$matches[2]
            
            if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 8)) {
                Write-Host "❌ Python版本过低: $pythonVersion" -ForegroundColor Red
                Write-Host "需要Python 3.8或更高版本" -ForegroundColor Red
                return $false
            }
        }
        
        Write-Host "✅ Python版本检查通过: $pythonVersion" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "❌ Python版本检查失败: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# 检查并激活虚拟环境
function Enable-VirtualEnvironment {
    $venvPath = Join-Path $PSScriptRoot "venv"
    $activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
    
    if (Test-Path $activateScript) {
        Write-Host "🔧 激活虚拟环境..." -ForegroundColor Yellow
        try {
            & $activateScript
            Write-Host "✅ 虚拟环境已激活" -ForegroundColor Green
            return $true
        }
        catch {
            Write-Host "⚠️  虚拟环境激活失败: $($_.Exception.Message)" -ForegroundColor Yellow
            return $false
        }
    }
    else {
        Write-Host "ℹ️  未找到虚拟环境，使用系统Python" -ForegroundColor Blue
        return $true
    }
}

# 检查依赖包
function Test-Dependencies {
    Write-Host "🔍 检查依赖包..." -ForegroundColor Yellow
    
    $requiredPackages = @('mcp', 'mlflow', 'langchain', 'pyyaml', 'python-dotenv')
    $missingPackages = @()
    
    foreach ($package in $requiredPackages) {
        $checkCmd = "python -c \"import $($package.Replace('-', '_'))\""
        $result = Invoke-Expression $checkCmd 2>&1
        
        if ($LASTEXITCODE -ne 0) {
            $missingPackages += $package
            Write-Host "❌ $package" -ForegroundColor Red
        }
        else {
            Write-Host "✅ $package" -ForegroundColor Green
        }
    }
    
    if ($missingPackages.Count -gt 0) {
        Write-Host "⚠️  缺少依赖包，正在安装..." -ForegroundColor Yellow
        
        $requirementsFile = Join-Path $PSScriptRoot "requirements.txt"
        if (Test-Path $requirementsFile) {
            try {
                pip install -r $requirementsFile
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "✅ 依赖包安装成功" -ForegroundColor Green
                    return $true
                }
                else {
                    Write-Host "❌ 依赖包安装失败" -ForegroundColor Red
                    return $false
                }
            }
            catch {
                Write-Host "❌ 依赖包安装失败: $($_.Exception.Message)" -ForegroundColor Red
                return $false
            }
        }
        else {
            Write-Host "❌ 未找到requirements.txt文件" -ForegroundColor Red
            return $false
        }
    }
    else {
        Write-Host "✅ 所有依赖包已安装" -ForegroundColor Green
        return $true
    }
}

# 检查配置文件
function Test-Configuration {
    Write-Host "🔧 检查配置文件..." -ForegroundColor Yellow
    
    $envFile = Join-Path $PSScriptRoot ".env"
    $modelsConfig = Join-Path $PSScriptRoot "models_config.yaml"
    $serverScript = Join-Path $PSScriptRoot "enhanced_promptlab_server.py"
    
    $allExists = $true
    
    if (-not (Test-Path $envFile)) {
        Write-Host "⚠️  .env文件不存在" -ForegroundColor Yellow
    }
    else {
        Write-Host "✅ .env文件存在" -ForegroundColor Green
    }
    
    if (-not (Test-Path $modelsConfig)) {
        Write-Host "❌ models_config.yaml文件不存在" -ForegroundColor Red
        $allExists = $false
    }
    else {
        Write-Host "✅ models_config.yaml文件存在" -ForegroundColor Green
    }
    
    if (-not (Test-Path $serverScript)) {
        Write-Host "❌ enhanced_promptlab_server.py文件不存在" -ForegroundColor Red
        $allExists = $false
    }
    else {
        Write-Host "✅ enhanced_promptlab_server.py文件存在" -ForegroundColor Green
    }
    
    return $allExists
}

# 启动MLflow服务器
function Start-MLflowServer {
    Write-Host "🔍 检查MLflow服务器..." -ForegroundColor Yellow
    
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:5000/health" -TimeoutSec 5 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ MLflow服务器已运行" -ForegroundColor Green
            return $true
        }
    }
    catch {
        # MLflow服务器未运行，尝试启动
    }
    
    Write-Host "🚀 启动MLflow服务器..." -ForegroundColor Yellow
    
    $mlrunsDir = Join-Path $PSScriptRoot "mlruns"
    if (-not (Test-Path $mlrunsDir)) {
        New-Item -ItemType Directory -Path $mlrunsDir -Force | Out-Null
    }
    
    try {
        $mlflowArgs = @(
            "-m", "mlflow", "server",
            "--backend-store-uri", "file:///$($mlrunsDir.Replace('\', '/'))",
            "--default-artifact-root", "file:///$($mlrunsDir.Replace('\', '/'))",
            "--host", "127.0.0.1",
            "--port", "5000"
        )
        
        $mlflowProcess = Start-Process -FilePath "python" -ArgumentList $mlflowArgs -WindowStyle Hidden -PassThru
        
        # 等待服务器启动
        Start-Sleep -Seconds 5
        
        # 检查服务器是否启动成功
        for ($i = 1; $i -le 10; $i++) {
            try {
                $response = Invoke-WebRequest -Uri "http://localhost:5000/health" -TimeoutSec 2 -ErrorAction SilentlyContinue
                if ($response.StatusCode -eq 200) {
                    Write-Host "✅ MLflow服务器启动成功" -ForegroundColor Green
                    return $true
                }
            }
            catch {
                Start-Sleep -Seconds 1
            }
        }
        
        Write-Host "⚠️  MLflow服务器启动超时" -ForegroundColor Yellow
        return $false
    }
    catch {
        Write-Host "❌ MLflow服务器启动失败: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# 启动增强版服务器
function Start-EnhancedServer {
    Write-Host "🚀 启动增强版PromptLab服务器..." -ForegroundColor Cyan
    Write-Host ""
    
    $serverScript = Join-Path $PSScriptRoot "start_enhanced_promptlab.py"
    
    try {
        # 设置工作目录
        Set-Location $PSScriptRoot
        
        # 启动服务器
        python $serverScript
    }
    catch {
        Write-Host "❌ 服务器启动失败: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
    finally {
        Write-Host ""
        Write-Host "服务器已停止" -ForegroundColor Yellow
    }
    
    return $true
}

# 显示使用说明
function Show-Usage {
    Write-Host ""
    Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║                    📋 使用说明                               ║" -ForegroundColor Green
    Write-Host "╠══════════════════════════════════════════════════════════════╣" -ForegroundColor Green
    Write-Host "║                                                              ║" -ForegroundColor Green
    Write-Host "║  🔧 配置文件:                                                 ║" -ForegroundColor Green
    Write-Host "║    • .env - 环境变量和API密钥                                ║" -ForegroundColor Green
    Write-Host "║    • models_config.yaml - 模型配置                          ║" -ForegroundColor Green
    Write-Host "║                                                              ║" -ForegroundColor Green
    Write-Host "║  🌐 Web界面:                                                 ║" -ForegroundColor Green
    Write-Host "║    • model_management_ui.html - 模型管理界面                ║" -ForegroundColor Green
    Write-Host "║    • http://localhost:5000 - MLflow界面                     ║" -ForegroundColor Green
    Write-Host "║                                                              ║" -ForegroundColor Green
    Write-Host "║  📋 MCP工具:                                                 ║" -ForegroundColor Green
    Write-Host "║    • list_models - 查看可用模型                             ║" -ForegroundColor Green
    Write-Host "║    • switch_model - 切换模型                                ║" -ForegroundColor Green
    Write-Host "║    • optimize_query - 优化查询                              ║" -ForegroundColor Green
    Write-Host "║    • get_performance_stats - 性能统计                       ║" -ForegroundColor Green
    Write-Host "║                                                              ║" -ForegroundColor Green
    Write-Host "║  按 Ctrl+C 停止服务器                                        ║" -ForegroundColor Green
    Write-Host "║                                                              ║" -ForegroundColor Green
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Green
    Write-Host ""
}

# 主函数
function Main {
    try {
        # 显示横幅
        Show-Banner
        
        Write-Host "开始启动检查..." -ForegroundColor Cyan
        Write-Host ""
        
        # 检查Python版本
        if (-not (Test-PythonVersion)) {
            Write-Host "启动失败：Python版本检查未通过" -ForegroundColor Red
            Read-Host "按Enter键退出"
            exit 1
        }
        
        # 激活虚拟环境
        Enable-VirtualEnvironment | Out-Null
        
        # 检查依赖
        if (-not (Test-Dependencies)) {
            Write-Host "启动失败：依赖检查未通过" -ForegroundColor Red
            Read-Host "按Enter键退出"
            exit 1
        }
        
        # 检查配置
        if (-not (Test-Configuration)) {
            Write-Host "启动失败：配置文件检查未通过" -ForegroundColor Red
            Read-Host "按Enter键退出"
            exit 1
        }
        
        # 启动MLflow服务器
        Start-MLflowServer | Out-Null
        
        # 显示使用说明
        Show-Usage
        
        # 启动增强版服务器
        Start-EnhancedServer
        
    }
    catch {
        Write-Host "启动过程中发生错误: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host $_.ScriptStackTrace -ForegroundColor Red
        Read-Host "按Enter键退出"
        exit 1
    }
}

# 运行主函数
Main