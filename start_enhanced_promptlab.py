#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动增强版 PromptLab MCP 服务器
Enhanced PromptLab MCP Server Startup Script

功能:
- 环境检查和初始化
- 依赖验证
- 模型配置验证
- 服务器启动
- 健康检查
"""

import os
import sys
import json
import time
import asyncio
import logging
import subprocess
import webbrowser
from pathlib import Path
from typing import Dict, List, Optional

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("enhanced-promptlab-startup")

class EnhancedPromptLabStarter:
    """增强版 PromptLab 启动器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.env_file = self.project_root / '.env'
        self.models_config = self.project_root / 'models_config.yaml'
        self.server_script = self.project_root / 'enhanced_promptlab_server.py'
        self.ui_file = self.project_root / 'model_management_ui.html'
        
        self.required_packages = [
            'mcp',
            'mlflow',
            'langchain',
            'langchain-google-vertexai',
            'google-cloud-aiplatform',
            'python-dotenv',
            'pyyaml',
            'rich',
            'numpy',
            'pandas'
        ]
        
        self.optional_packages = {
            'openai': 'OpenAI模型支持',
            'anthropic': 'Anthropic Claude模型支持',
            'requests': 'HTTP请求支持',
            'aiohttp': '异步HTTP支持'
        }
    
    def print_banner(self):
        """打印启动横幅"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║    🚀 Enhanced PromptLab MCP Server                          ║
║                                                              ║
║    多模型AI提示词优化平台                                      ║
║    Multi-Model AI Prompt Optimization Platform              ║
║                                                              ║
║    版本: 2.0.0                                               ║
║    作者: PromptLab Team                                      ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def check_python_version(self) -> bool:
        """检查Python版本"""
        logger.info("检查Python版本...")
        
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            logger.error(f"Python版本过低: {version.major}.{version.minor}")
            logger.error("需要Python 3.8或更高版本")
            return False
        
        logger.info(f"✅ Python版本: {version.major}.{version.minor}.{version.micro}")
        return True
    
    def check_dependencies(self) -> bool:
        """检查依赖包"""
        logger.info("检查依赖包...")
        
        missing_packages = []
        optional_missing = []
        
        # 检查必需包
        for package in self.required_packages:
            try:
                # 特殊处理一些包名映射
                import_name = package.replace('-', '_')
                if package == 'google-cloud-aiplatform':
                    import_name = 'google.cloud.aiplatform'
                elif package == 'python-dotenv':
                    import_name = 'dotenv'
                elif package == 'pyyaml':
                    import_name = 'yaml'
                
                __import__(import_name)
                logger.info(f"✅ {package}")
            except ImportError:
                missing_packages.append(package)
                logger.warning(f"❌ {package} (必需)")
        
        # 检查可选包
        for package, description in self.optional_packages.items():
            try:
                __import__(package)
                logger.info(f"✅ {package} - {description}")
            except ImportError:
                optional_missing.append((package, description))
                logger.info(f"⚠️  {package} - {description} (可选)")
        
        if missing_packages:
            logger.error("缺少必需的依赖包:")
            for package in missing_packages:
                logger.error(f"  - {package}")
            logger.error("请运行: pip install -r requirements.txt")
            return False
        
        if optional_missing:
            logger.info("可选依赖包未安装:")
            for package, description in optional_missing:
                logger.info(f"  - {package}: {description}")
            logger.info("可以通过以下命令安装:")
            for package, _ in optional_missing:
                logger.info(f"  pip install {package}")
        
        return True
    
    def check_environment(self) -> bool:
        """检查环境配置"""
        logger.info("检查环境配置...")
        
        if not self.env_file.exists():
            logger.warning(f"环境文件不存在: {self.env_file}")
            self.create_default_env()
        
        # 加载环境变量
        try:
            from dotenv import load_dotenv
            load_dotenv(self.env_file)
            logger.info(f"✅ 环境文件已加载: {self.env_file}")
        except Exception as e:
            logger.error(f"加载环境文件失败: {e}")
            return False
        
        # 检查关键环境变量
        required_env_vars = ['MLFLOW_TRACKING_URI']
        missing_vars = []
        
        for var in required_env_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            logger.warning("缺少环境变量:")
            for var in missing_vars:
                logger.warning(f"  - {var}")
            logger.warning("请检查.env文件配置")
        
        return True
    
    def create_default_env(self):
        """创建默认环境文件"""
        logger.info("创建默认环境文件...")
        
        default_env = """
# PromptLab Environment Configuration

# GCP Configuration
GCP_PROJECT_ID=your-gcp-project-id
GCP_REGION=us-central1

# MLflow Configuration
MLFLOW_TRACKING_URI=http://localhost:5000

# Debug Mode
PROMPTLAB_DEBUG=true

# AI Model API Keys
# OpenAI API
# OPENAI_API_KEY=your_openai_api_key_here

# Anthropic Claude API
# ANTHROPIC_API_KEY=your_anthropic_api_key_here

# DeepSeek API
# DEEPSEEK_API_KEY=your_deepseek_api_key_here

# 阿里云通义千问 API
# QWEN_API_KEY=your_qwen_api_key_here

# 智谱AI API
# ZHIPU_API_KEY=your_zhipu_api_key_here
        """
        
        with open(self.env_file, 'w', encoding='utf-8') as f:
            f.write(default_env)
        
        logger.info(f"✅ 默认环境文件已创建: {self.env_file}")
        logger.info("请编辑.env文件，配置您的API密钥")
    
    def check_models_config(self) -> bool:
        """检查模型配置"""
        logger.info("检查模型配置...")
        
        if not self.models_config.exists():
            logger.error(f"模型配置文件不存在: {self.models_config}")
            return False
        
        try:
            import yaml
            with open(self.models_config, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # 验证配置结构
            if 'models' not in config:
                logger.error("模型配置文件缺少'models'部分")
                return False
            
            models_count = len(config['models'])
            enabled_count = sum(1 for model in config['models'].values() if model.get('enabled', False))
            
            logger.info(f"✅ 模型配置文件已加载")
            logger.info(f"  - 总模型数: {models_count}")
            logger.info(f"  - 启用模型数: {enabled_count}")
            logger.info(f"  - 当前模型: {config.get('current_model', 'None')}")
            
            if enabled_count == 0:
                logger.warning("⚠️  没有启用的模型，请检查配置")
            
            return True
            
        except Exception as e:
            logger.error(f"读取模型配置失败: {e}")
            return False
    
    def check_mlflow_server(self) -> bool:
        """检查MLflow服务器"""
        logger.info("检查MLflow服务器...")
        
        mlflow_uri = os.getenv('MLFLOW_TRACKING_URI', 'http://localhost:5000')
        
        try:
            import requests
            response = requests.get(f"{mlflow_uri}/health", timeout=5)
            if response.status_code == 200:
                logger.info(f"✅ MLflow服务器运行正常: {mlflow_uri}")
                return True
        except Exception:
            pass
        
        logger.warning(f"⚠️  MLflow服务器未运行: {mlflow_uri}")
        logger.info("尝试启动MLflow服务器...")
        
        return self.start_mlflow_server()
    
    def start_mlflow_server(self) -> bool:
        """启动MLflow服务器"""
        try:
            # 创建MLflow目录
            mlflow_dir = self.project_root / 'mlruns'
            mlflow_dir.mkdir(exist_ok=True)
            
            # 启动MLflow服务器
            cmd = [
                sys.executable, '-m', 'mlflow', 'server',
                '--backend-store-uri', f'file://{mlflow_dir}',
                '--default-artifact-root', f'file://{mlflow_dir}',
                '--host', '127.0.0.1',
                '--port', '5000'
            ]
            
            logger.info("启动MLflow服务器...")
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.project_root
            )
            
            # 等待服务器启动
            time.sleep(5)
            
            # 检查服务器是否启动成功
            if self.check_mlflow_health():
                logger.info("✅ MLflow服务器启动成功")
                return True
            else:
                logger.error("❌ MLflow服务器启动失败")
                return False
                
        except Exception as e:
            logger.error(f"启动MLflow服务器失败: {e}")
            return False
    
    def check_mlflow_health(self) -> bool:
        """检查MLflow健康状态"""
        mlflow_uri = os.getenv('MLFLOW_TRACKING_URI', 'http://localhost:5000')
        
        for i in range(10):  # 重试10次
            try:
                import requests
                response = requests.get(f"{mlflow_uri}/health", timeout=2)
                if response.status_code == 200:
                    return True
            except Exception:
                pass
            time.sleep(1)
        
        return False
    
    def start_server(self) -> bool:
        """启动增强版服务器"""
        logger.info("启动增强版PromptLab服务器...")
        
        if not self.server_script.exists():
            logger.error(f"服务器脚本不存在: {self.server_script}")
            return False
        
        try:
            # 设置环境变量
            env = os.environ.copy()
            env['PYTHONPATH'] = str(self.project_root)
            
            # 启动服务器
            cmd = [sys.executable, str(self.server_script)]
            
            logger.info(f"执行命令: {' '.join(cmd)}")
            logger.info(f"工作目录: {self.project_root}")
            
            process = subprocess.Popen(
                cmd,
                cwd=self.project_root,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            logger.info("✅ 服务器已启动")
            logger.info("服务器输出:")
            
            # 实时显示服务器输出
            try:
                for line in process.stdout:
                    print(f"[SERVER] {line.strip()}")
            except KeyboardInterrupt:
                logger.info("收到中断信号，正在关闭服务器...")
                process.terminate()
                process.wait()
                logger.info("服务器已关闭")
            
            return True
            
        except Exception as e:
            logger.error(f"启动服务器失败: {e}")
            return False
    
    def open_management_ui(self):
        """打开管理界面"""
        if self.ui_file.exists():
            logger.info("打开模型管理界面...")
            try:
                webbrowser.open(f"file://{self.ui_file.absolute()}")
                logger.info(f"✅ 管理界面已打开: {self.ui_file}")
            except Exception as e:
                logger.warning(f"无法自动打开管理界面: {e}")
                logger.info(f"请手动打开: {self.ui_file}")
        else:
            logger.warning("管理界面文件不存在")
    
    def show_startup_info(self):
        """显示启动信息"""
        info = """
╔══════════════════════════════════════════════════════════════╗
║                    🎉 启动成功！                              ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  📋 可用功能:                                                 ║
║    • 多模型AI支持 (OpenAI, Claude, Gemini等)                 ║
║    • 智能提示词优化                                           ║
║    • 性能监控和缓存                                           ║
║    • 成本追踪                                                ║
║    • Web管理界面                                             ║
║                                                              ║
║  🔧 管理命令:                                                 ║
║    • 查看模型: list_models                                   ║
║    • 切换模型: switch_model                                  ║
║    • 优化查询: optimize_query                               ║
║    • 性能统计: get_performance_stats                        ║
║                                                              ║
║  🌐 Web界面: model_management_ui.html                       ║
║  📊 MLflow: http://localhost:5000                           ║
║                                                              ║
║  按 Ctrl+C 停止服务器                                        ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(info)
    
    def run(self):
        """运行启动流程"""
        self.print_banner()
        
        logger.info("开始启动检查...")
        
        # 检查Python版本
        if not self.check_python_version():
            return False
        
        # 检查依赖
        if not self.check_dependencies():
            return False
        
        # 检查环境
        if not self.check_environment():
            return False
        
        # 检查模型配置
        if not self.check_models_config():
            return False
        
        # 检查MLflow服务器
        if not self.check_mlflow_server():
            logger.warning("MLflow服务器未运行，某些功能可能受限")
        
        # 显示启动信息
        self.show_startup_info()
        
        # 打开管理界面
        self.open_management_ui()
        
        # 启动服务器
        return self.start_server()

def main():
    """主函数"""
    try:
        starter = EnhancedPromptLabStarter()
        success = starter.run()
        
        if not success:
            logger.error("启动失败")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("\n用户中断，退出程序")
        sys.exit(0)
    except Exception as e:
        logger.error(f"启动过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()