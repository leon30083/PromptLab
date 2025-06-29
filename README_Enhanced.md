# Enhanced PromptLab MCP Server

🚀 **多模型AI提示词优化平台** | **Multi-Model AI Prompt Optimization Platform**

## 📋 项目简介

Enhanced PromptLab 是一个基于 MCP (Model Context Protocol) 标准的增强版AI提示词优化平台，支持多种AI模型提供商，提供智能提示词优化、性能监控、成本追踪等功能。

### ✨ 核心特性

- 🤖 **多模型支持**: 支持 OpenAI、Claude、Gemini、DeepSeek、通义千问等主流AI模型
- 🔄 **智能切换**: 自动模型选择和负载均衡
- ⚡ **性能优化**: 查询缓存、响应时间优化
- 📊 **监控追踪**: MLflow集成，完整的性能和成本监控
- 🎯 **提示词优化**: 智能提示词分析和优化建议
- 🌐 **Web管理**: 可视化模型管理界面
- 🔒 **安全可靠**: API密钥安全管理，故障转移机制

## 🏗️ 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   MCP Client    │────│ Enhanced Server │────│  Model Adapters │
│   (Trae AI)     │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                       ┌─────────────────┐    ┌─────────────────┐
                       │  Performance    │    │   AI Models     │
                       │   Monitor       │    │  (Multi-vendor) │
                       └─────────────────┘    └─────────────────┘
                                │
                       ┌─────────────────┐
                       │     MLflow      │
                       │   Tracking      │
                       └─────────────────┘
```

## 🚀 快速开始

### 1. 环境要求

- Python 3.8+
- Windows/Linux/macOS
- 8GB+ RAM (推荐)

### 2. 一键启动

#### Windows 用户
```bash
# 方式1: 批处理文件
start_enhanced.bat

# 方式2: PowerShell脚本
.\start_enhanced.ps1

# 方式3: Python脚本
python start_enhanced_promptlab.py
```

#### Linux/macOS 用户
```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务器
python start_enhanced_promptlab.py
```

### 3. 配置API密钥

编辑 `.env` 文件，添加您的API密钥：

```env
# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic Claude API
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# DeepSeek API
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# 阿里云通义千问 API
QWEN_API_KEY=your_qwen_api_key_here

# 智谱AI API
ZHIPU_API_KEY=your_zhipu_api_key_here
```

## 🛠️ 功能详解

### MCP 工具列表

| 工具名称 | 功能描述 | 参数 |
|---------|---------|------|
| `list_models` | 查看所有可用模型 | 无 |
| `switch_model` | 切换当前使用的模型 | `model_name` |
| `get_model_status` | 获取模型状态信息 | `model_name` (可选) |
| `add_model` | 添加新的模型配置 | `config` |
| `remove_model` | 移除模型配置 | `model_name` |
| `optimize_query` | 优化用户查询 | `query`, `task_type`, `model_name` (可选) |
| `list_prompts` | 查看提示词模板 | 无 |
| `reload_prompts` | 重新加载提示词模板 | 无 |
| `get_performance_stats` | 获取性能统计 | 无 |
| `clear_cache` | 清除缓存 | 无 |

### 模型支持

#### 🤖 支持的AI模型

| 提供商 | 模型 | 类型 | 状态 |
|-------|------|------|------|
| **Google** | Gemini 2.5 Pro | 多模态 | ✅ |
| **OpenAI** | GPT-4o, GPT-4o Mini | 文本 | ✅ |
| **Anthropic** | Claude 3.5 Sonnet, Claude 3 Haiku | 文本 | ✅ |
| **DeepSeek** | DeepSeek Chat, DeepSeek Coder | 文本/代码 | ✅ |
| **阿里云** | 通义千问 Max, Plus | 中文优化 | ✅ |
| **智谱AI** | GLM-4 Plus, GLM-4 Flash | 中文优化 | ✅ |
| **Ollama** | Llama 3.1, Qwen 2.5 | 本地部署 | ✅ |

#### 🎯 模型组配置

- **编程专用**: DeepSeek Coder, GPT-4o
- **推理分析**: Claude 3.5 Sonnet, Gemini 2.5 Pro
- **中文优化**: 通义千问, GLM-4, Qwen 2.5
- **经济实惠**: GPT-4o Mini, Claude 3 Haiku
- **本地模型**: Ollama Llama 3.1, Qwen 2.5
- **多模态**: Gemini 2.5 Pro

### 性能优化

#### 🚀 缓存机制
- **查询缓存**: 5分钟TTL，提高响应速度
- **结果缓存**: 智能缓存策略，减少API调用
- **性能监控**: 实时响应时间和成功率统计

#### 📊 监控指标
- 请求总数和成功率
- 平均响应时间
- 缓存命中率
- 模型使用统计
- 成本追踪

## 🌐 Web管理界面

访问 `model_management_ui.html` 获得可视化管理体验：

- 📊 **模型概览**: 实时状态监控
- ⚙️ **模型配置**: 添加/编辑/删除模型
- 📈 **性能监控**: 图表化性能数据
- 🔧 **系统设置**: 全局配置管理

## 📁 项目结构

```
PromptLab/
├── 📄 enhanced_promptlab_server.py    # 增强版MCP服务器
├── 📄 multi_model_config.py           # 多模型配置管理
├── 📄 model_adapters.py               # 模型适配器
├── 📄 performance_optimization.py     # 性能优化模块
├── 📄 models_config.yaml              # 模型配置文件
├── 📄 advanced_prompts.json           # 提示词模板
├── 📄 .env                            # 环境变量配置
├── 📄 requirements.txt                # 依赖包列表
├── 🚀 start_enhanced_promptlab.py     # 启动脚本
├── 🚀 start_enhanced.bat              # Windows启动脚本
├── 🚀 start_enhanced.ps1              # PowerShell启动脚本
├── 🌐 model_management_ui.html        # Web管理界面
└── 📚 README_Enhanced.md              # 本文档
```

## 🔧 高级配置

### 模型配置示例

```yaml
models:
  gpt-4o:
    provider: openai
    model_id: gpt-4o
    api_base: https://api.openai.com/v1
    enabled: true
    priority: 1
    temperature: 0.7
    max_tokens: 4096
    cost_per_1k_tokens: 0.03
    
  claude-3.5-sonnet:
    provider: anthropic
    model_id: claude-3-5-sonnet-20241022
    api_base: https://api.anthropic.com
    enabled: true
    priority: 2
    temperature: 0.7
    max_tokens: 4096
    cost_per_1k_tokens: 0.015
```

### 环境变量配置

```env
# 基础配置
GCP_PROJECT_ID=your-gcp-project
GCP_REGION=us-central1
MLFLOW_TRACKING_URI=http://localhost:5000

# 调试模式
PROMPTLAB_DEBUG=true

# 性能配置
CACHE_TTL=300
MAX_RETRIES=3
TIMEOUT=30

# 负载均衡
LOAD_BALANCING=true
FAILOVER_ENABLED=true
```

## 📊 使用示例

### 1. 查看可用模型

```python
# MCP客户端调用
result = await client.call_tool("list_models")
print(result)
```

### 2. 切换模型

```python
# 切换到GPT-4o
result = await client.call_tool("switch_model", {
    "model_name": "gpt-4o"
})
```

### 3. 优化查询

```python
# 优化编程相关查询
result = await client.call_tool("optimize_query", {
    "query": "如何实现一个高效的排序算法？",
    "task_type": "code",
    "model_name": "deepseek-coder"  # 可选
})
```

### 4. 获取性能统计

```python
# 查看性能数据
stats = await client.call_tool("get_performance_stats")
print(f"缓存命中率: {stats['cache_hit_rate']}%")
print(f"平均响应时间: {stats['avg_response_time']}ms")
```

## 🔍 故障排除

### 常见问题

#### 1. 依赖安装失败
```bash
# 升级pip
python -m pip install --upgrade pip

# 清除缓存重新安装
pip cache purge
pip install -r requirements.txt
```

#### 2. API密钥配置错误
- 检查 `.env` 文件格式
- 确认API密钥有效性
- 验证API配额和权限

#### 3. MLflow服务器启动失败
```bash
# 手动启动MLflow
mlflow server --backend-store-uri file://./mlruns --default-artifact-root file://./mlruns --host 127.0.0.1 --port 5000
```

#### 4. 模型调用失败
- 检查网络连接
- 验证API密钥
- 查看模型配置
- 检查API配额

### 日志调试

启用调试模式：
```env
PROMPTLAB_DEBUG=true
```

查看详细日志：
```bash
python start_enhanced_promptlab.py --log-level DEBUG
```

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [MCP (Model Context Protocol)](https://github.com/modelcontextprotocol) - 核心协议支持
- [LangChain](https://github.com/langchain-ai/langchain) - AI应用框架
- [MLflow](https://github.com/mlflow/mlflow) - 机器学习生命周期管理
- 所有AI模型提供商的API支持

## 📞 支持

如有问题或建议，请：

1. 查看 [FAQ](FAQ.md)
2. 提交 [Issue](https://github.com/your-repo/issues)
3. 加入讨论 [Discussions](https://github.com/your-repo/discussions)

---

**Enhanced PromptLab** - 让AI提示词优化更简单、更智能、更高效！ 🚀