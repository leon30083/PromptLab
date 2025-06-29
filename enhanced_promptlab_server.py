#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版 PromptLab MCP 服务器
Enhanced PromptLab MCP Server with Multi-Model Support

新增功能:
- 多模型支持和管理
- 智能模型选择
- 负载均衡和故障转移
- 性能监控和缓存
- 成本追踪
"""

import logging
import os
import sys
import json
import traceback
import asyncio
import time
import hashlib
from typing import Dict, Any, List, Optional, Union
from dataclasses import asdict

# MCP imports
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Import MLflow components
import mlflow
from mlflow.tracking import MlflowClient

# Import our multi-model system
from multi_model_config import MultiModelManager, ModelConfig, ModelProvider, ModelType
from model_adapters import ModelAdapterFactory, ChatMessage, ChatResponse
from performance_optimization import PerformanceOptimizer, PerformanceMonitor

# --- Logging Setup ---
debug_mode = os.getenv('PROMPTLAB_DEBUG', 'false').lower() == 'true'
log_level = logging.DEBUG if debug_mode else logging.INFO
logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("enhanced-promptlab-server")

# --- Environment Setup ---
from dotenv import load_dotenv
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path=dotenv_path)
    logger.info(f"Loaded environment variables from: {dotenv_path}")

MLFLOW_TRACKING_URI = os.getenv('MLFLOW_TRACKING_URI')

# --- Global Variables ---
model_manager = None
mlflow_client = None
available_prompts = {}
performance_optimizer = None
performance_monitor = None
current_adapters = {}  # 缓存的适配器实例
model_usage_stats = {}  # 模型使用统计

class EnhancedPromptLabServer:
    """增强版 PromptLab 服务器"""
    
    def __init__(self):
        self.server = Server("enhanced-promptlab")
        self.setup_tools()
    
    def setup_tools(self):
        """设置 MCP 工具"""
        
        # 原有工具
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            return [
                Tool(
                    name="list_prompts",
                    description="列出所有可用的提示词模板",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="optimize_query",
                    description="使用AI优化用户查询，匹配最佳提示词模板",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "用户的原始查询"
                            },
                            "model": {
                                "type": "string",
                                "description": "指定使用的模型名称（可选）"
                            },
                            "use_cache": {
                                "type": "boolean",
                                "description": "是否使用缓存（默认true）",
                                "default": True
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="reload_prompts",
                    description="重新加载提示词模板",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                # 新增工具
                Tool(
                    name="list_models",
                    description="列出所有可用的AI模型",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "provider": {
                                "type": "string",
                                "description": "按提供商过滤（可选）"
                            },
                            "enabled_only": {
                                "type": "boolean",
                                "description": "只显示启用的模型（默认true）",
                                "default": True
                            }
                        },
                        "required": []
                    }
                ),
                Tool(
                    name="switch_model",
                    description="切换当前使用的AI模型",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "model_name": {
                                "type": "string",
                                "description": "要切换到的模型名称"
                            }
                        },
                        "required": ["model_name"]
                    }
                ),
                Tool(
                    name="get_model_status",
                    description="获取模型状态和使用统计",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "model_name": {
                                "type": "string",
                                "description": "模型名称（可选，不指定则返回所有模型状态）"
                            }
                        },
                        "required": []
                    }
                ),
                Tool(
                    name="add_model",
                    description="添加新的AI模型配置",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "模型名称"},
                            "provider": {"type": "string", "description": "提供商"},
                            "model_id": {"type": "string", "description": "模型ID"},
                            "api_base": {"type": "string", "description": "API基础URL（可选）"},
                            "api_key": {"type": "string", "description": "API密钥（可选）"},
                            "temperature": {"type": "number", "description": "温度参数（可选）", "default": 0.7},
                            "max_tokens": {"type": "integer", "description": "最大token数（可选）"},
                            "priority": {"type": "integer", "description": "优先级（可选）", "default": 5}
                        },
                        "required": ["name", "provider", "model_id"]
                    }
                ),
                Tool(
                    name="remove_model",
                    description="移除AI模型配置",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "model_name": {
                                "type": "string",
                                "description": "要移除的模型名称"
                            }
                        },
                        "required": ["model_name"]
                    }
                ),
                Tool(
                    name="get_performance_stats",
                    description="获取性能统计信息",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "reset": {
                                "type": "boolean",
                                "description": "是否重置统计（默认false）",
                                "default": False
                            }
                        },
                        "required": []
                    }
                ),
                Tool(
                    name="clear_cache",
                    description="清除查询缓存",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                )
            ]
        
        # 工具实现
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            try:
                if name == "list_prompts":
                    return await self._list_prompts()
                elif name == "optimize_query":
                    return await self._optimize_query(arguments)
                elif name == "reload_prompts":
                    return await self._reload_prompts()
                elif name == "list_models":
                    return await self._list_models(arguments)
                elif name == "switch_model":
                    return await self._switch_model(arguments)
                elif name == "get_model_status":
                    return await self._get_model_status(arguments)
                elif name == "add_model":
                    return await self._add_model(arguments)
                elif name == "remove_model":
                    return await self._remove_model(arguments)
                elif name == "get_performance_stats":
                    return await self._get_performance_stats(arguments)
                elif name == "clear_cache":
                    return await self._clear_cache()
                else:
                    return [TextContent(type="text", text=f"未知工具: {name}")]
            except Exception as e:
                logger.error(f"工具调用失败 {name}: {e}")
                logger.error(traceback.format_exc())
                return [TextContent(type="text", text=f"工具调用失败: {str(e)}")]
    
    async def _list_prompts(self) -> List[TextContent]:
        """列出所有提示词"""
        try:
            prompts_list = []
            for name, prompt_data in available_prompts.items():
                prompts_list.append({
                    "name": name,
                    "tags": prompt_data.get("tags", {}),
                    "version": prompt_data.get("version", "unknown")
                })
            
            result = {
                "prompts": prompts_list,
                "total_count": len(prompts_list)
            }
            
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
        except Exception as e:
            logger.error(f"列出提示词失败: {e}")
            return [TextContent(type="text", text=f"错误: {str(e)}")]
    
    async def _optimize_query(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """优化查询"""
        query = arguments.get("query", "")
        model_name = arguments.get("model")
        use_cache = arguments.get("use_cache", True)
        
        if not query:
            return [TextContent(type="text", text="错误: 查询不能为空")]
        
        start_time = time.time()
        
        try:
            # 检查缓存
            if use_cache and performance_optimizer:
                cached_result = performance_optimizer.get_cached_result(query)
                if cached_result:
                    logger.info(f"缓存命中: {query[:50]}...")
                    return [TextContent(type="text", text=json.dumps(cached_result, ensure_ascii=False, indent=2))]
            
            # 选择模型
            if model_name:
                model_config = model_manager.get_model(model_name)
                if not model_config or not model_config.enabled:
                    return [TextContent(type="text", text=f"错误: 模型 {model_name} 不存在或未启用")]
            else:
                model_config = model_manager.get_current_model()
                if not model_config:
                    enabled_models = model_manager.list_models()
                    if not enabled_models:
                        return [TextContent(type="text", text="错误: 没有可用的模型")]
                    model_config = enabled_models[0]  # 使用第一个可用模型
            
            # 获取或创建适配器
            adapter = await self._get_adapter(model_config)
            
            # 构建优化提示
            system_prompt = self._build_optimization_prompt()
            messages = [
                ChatMessage(role="system", content=system_prompt),
                ChatMessage(role="user", content=f"用户查询: {query}")
            ]
            
            # 调用模型
            response = await adapter.chat_completion(messages)
            
            # 解析响应
            try:
                optimized_result = json.loads(response.content)
            except json.JSONDecodeError:
                # 如果不是JSON格式，包装成标准格式
                optimized_result = {
                    "optimized_query": response.content,
                    "matched_prompt": "no_match",
                    "confidence": 0.5,
                    "reasoning": "模型返回了非结构化响应"
                }
            
            # 添加元数据
            optimized_result.update({
                "model_used": model_config.name,
                "response_time": response.response_time,
                "total_time": time.time() - start_time,
                "cached": False
            })
            
            # 更新统计
            self._update_model_stats(model_config.name, response)
            
            # 缓存结果
            if use_cache and performance_optimizer:
                performance_optimizer.cache_result(query, optimized_result)
            
            # 记录性能监控
            if performance_monitor:
                performance_monitor.record_request(
                    response_time=time.time() - start_time,
                    success=True,
                    model=model_config.name
                )
            
            return [TextContent(type="text", text=json.dumps(optimized_result, ensure_ascii=False, indent=2))]
            
        except Exception as e:
            logger.error(f"查询优化失败: {e}")
            
            # 记录失败
            if performance_monitor:
                performance_monitor.record_request(
                    response_time=time.time() - start_time,
                    success=False,
                    error=str(e)
                )
            
            return [TextContent(type="text", text=f"优化失败: {str(e)}")]
    
    async def _reload_prompts(self) -> List[TextContent]:
        """重新加载提示词"""
        try:
            global available_prompts
            available_prompts = await load_all_prompts()
            
            result = {
                "status": "success",
                "message": f"成功重新加载 {len(available_prompts)} 个提示词",
                "prompts": list(available_prompts.keys())
            }
            
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
        except Exception as e:
            logger.error(f"重新加载提示词失败: {e}")
            return [TextContent(type="text", text=f"重新加载失败: {str(e)}")]
    
    async def _list_models(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """列出模型"""
        try:
            provider_filter = arguments.get("provider")
            enabled_only = arguments.get("enabled_only", True)
            
            models = model_manager.list_models(enabled_only=enabled_only)
            
            if provider_filter:
                try:
                    provider_enum = ModelProvider(provider_filter)
                    models = [m for m in models if m.provider == provider_enum]
                except ValueError:
                    return [TextContent(type="text", text=f"错误: 未知的提供商 {provider_filter}")]
            
            models_data = []
            for model in models:
                model_dict = asdict(model)
                model_dict['provider'] = model.provider.value
                model_dict['model_type'] = model.model_type.value
                
                # 添加使用统计
                stats = model_usage_stats.get(model.name, {})
                model_dict['usage_stats'] = stats
                
                models_data.append(model_dict)
            
            result = {
                "models": models_data,
                "total_count": len(models_data),
                "current_model": model_manager.current_model
            }
            
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
        except Exception as e:
            logger.error(f"列出模型失败: {e}")
            return [TextContent(type="text", text=f"错误: {str(e)}")]
    
    async def _switch_model(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """切换模型"""
        model_name = arguments.get("model_name")
        
        if not model_name:
            return [TextContent(type="text", text="错误: 必须指定模型名称")]
        
        try:
            model_config = model_manager.get_model(model_name)
            if not model_config:
                return [TextContent(type="text", text=f"错误: 模型 {model_name} 不存在")]
            
            if not model_config.enabled:
                return [TextContent(type="text", text=f"错误: 模型 {model_name} 未启用")]
            
            model_manager.set_current_model(model_name)
            model_manager.save_config()
            
            result = {
                "status": "success",
                "message": f"已切换到模型: {model_name}",
                "current_model": model_name,
                "model_info": {
                    "provider": model_config.provider.value,
                    "model_id": model_config.model_id,
                    "priority": model_config.priority
                }
            }
            
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
        except Exception as e:
            logger.error(f"切换模型失败: {e}")
            return [TextContent(type="text", text=f"切换失败: {str(e)}")]
    
    async def _get_model_status(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """获取模型状态"""
        model_name = arguments.get("model_name")
        
        try:
            if model_name:
                # 获取单个模型状态
                model_config = model_manager.get_model(model_name)
                if not model_config:
                    return [TextContent(type="text", text=f"错误: 模型 {model_name} 不存在")]
                
                stats = model_usage_stats.get(model_name, {})
                
                result = {
                    "model_name": model_name,
                    "enabled": model_config.enabled,
                    "provider": model_config.provider.value,
                    "model_id": model_config.model_id,
                    "priority": model_config.priority,
                    "usage_stats": stats
                }
            else:
                # 获取所有模型状态
                models_status = []
                for name, config in model_manager.models.items():
                    stats = model_usage_stats.get(name, {})
                    models_status.append({
                        "model_name": name,
                        "enabled": config.enabled,
                        "provider": config.provider.value,
                        "priority": config.priority,
                        "usage_stats": stats
                    })
                
                result = {
                    "models": models_status,
                    "current_model": model_manager.current_model,
                    "total_models": len(model_manager.models)
                }
            
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
        except Exception as e:
            logger.error(f"获取模型状态失败: {e}")
            return [TextContent(type="text", text=f"错误: {str(e)}")]
    
    async def _add_model(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """添加模型"""
        try:
            # 验证必需参数
            required_fields = ["name", "provider", "model_id"]
            for field in required_fields:
                if field not in arguments:
                    return [TextContent(type="text", text=f"错误: 缺少必需参数 {field}")]
            
            # 验证提供商
            try:
                provider = ModelProvider(arguments["provider"])
            except ValueError:
                return [TextContent(type="text", text=f"错误: 不支持的提供商 {arguments['provider']}")]
            
            # 创建模型配置
            model_config = ModelConfig(
                name=arguments["name"],
                provider=provider,
                model_type=ModelType.CHAT,  # 默认为聊天模型
                model_id=arguments["model_id"],
                api_base=arguments.get("api_base"),
                api_key=arguments.get("api_key"),
                temperature=arguments.get("temperature", 0.7),
                max_tokens=arguments.get("max_tokens"),
                priority=arguments.get("priority", 5)
            )
            
            # 添加到管理器
            model_manager.add_model(model_config)
            model_manager.save_config()
            
            result = {
                "status": "success",
                "message": f"成功添加模型: {arguments['name']}",
                "model_info": {
                    "name": model_config.name,
                    "provider": model_config.provider.value,
                    "model_id": model_config.model_id,
                    "priority": model_config.priority
                }
            }
            
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
        except Exception as e:
            logger.error(f"添加模型失败: {e}")
            return [TextContent(type="text", text=f"添加失败: {str(e)}")]
    
    async def _remove_model(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """移除模型"""
        model_name = arguments.get("model_name")
        
        if not model_name:
            return [TextContent(type="text", text="错误: 必须指定模型名称")]
        
        try:
            if model_name not in model_manager.models:
                return [TextContent(type="text", text=f"错误: 模型 {model_name} 不存在")]
            
            # 检查是否是当前模型
            if model_manager.current_model == model_name:
                # 切换到其他模型
                other_models = [name for name in model_manager.models.keys() if name != model_name]
                if other_models:
                    model_manager.set_current_model(other_models[0])
                else:
                    model_manager.current_model = None
            
            # 移除模型
            model_manager.remove_model(model_name)
            model_manager.save_config()
            
            # 清理适配器缓存
            if model_name in current_adapters:
                del current_adapters[model_name]
            
            # 清理使用统计
            if model_name in model_usage_stats:
                del model_usage_stats[model_name]
            
            result = {
                "status": "success",
                "message": f"成功移除模型: {model_name}",
                "current_model": model_manager.current_model
            }
            
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
        except Exception as e:
            logger.error(f"移除模型失败: {e}")
            return [TextContent(type="text", text=f"移除失败: {str(e)}")]
    
    async def _get_performance_stats(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """获取性能统计"""
        reset = arguments.get("reset", False)
        
        try:
            result = {}
            
            # 缓存统计
            if performance_optimizer:
                result["cache_stats"] = performance_optimizer.stats.copy()
                if reset:
                    performance_optimizer.stats = {
                        'cache_hits': 0,
                        'cache_misses': 0,
                        'total_queries': 0,
                        'avg_response_time': 0
                    }
            
            # 性能监控统计
            if performance_monitor:
                result["performance_stats"] = performance_monitor.get_stats()
                if reset:
                    performance_monitor.reset_stats()
            
            # 模型使用统计
            result["model_usage_stats"] = model_usage_stats.copy()
            if reset:
                model_usage_stats.clear()
            
            # 系统统计
            result["system_stats"] = {
                "total_models": len(model_manager.models),
                "enabled_models": len(model_manager.list_models()),
                "current_model": model_manager.current_model,
                "total_prompts": len(available_prompts)
            }
            
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
        except Exception as e:
            logger.error(f"获取性能统计失败: {e}")
            return [TextContent(type="text", text=f"错误: {str(e)}")]
    
    async def _clear_cache(self) -> List[TextContent]:
        """清除缓存"""
        try:
            cleared_items = 0
            
            if performance_optimizer:
                cleared_items = len(performance_optimizer.query_cache)
                performance_optimizer.query_cache.clear()
                performance_optimizer.cache_timestamps.clear()
            
            result = {
                "status": "success",
                "message": f"成功清除 {cleared_items} 个缓存项",
                "cleared_items": cleared_items
            }
            
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
        except Exception as e:
            logger.error(f"清除缓存失败: {e}")
            return [TextContent(type="text", text=f"错误: {str(e)}")]
    
    async def _get_adapter(self, model_config: ModelConfig):
        """获取或创建模型适配器"""
        if model_config.name not in current_adapters:
            current_adapters[model_config.name] = ModelAdapterFactory.create_adapter(model_config)
        return current_adapters[model_config.name]
    
    def _build_optimization_prompt(self) -> str:
        """构建优化提示"""
        prompt_names = list(available_prompts.keys())
        
        return f"""
你是一个专业的提示词优化助手。你的任务是分析用户查询，并将其优化为更好的提示词。

可用的提示词模板: {', '.join(prompt_names)}

请按照以下JSON格式返回结果:
{{
    "optimized_query": "优化后的查询",
    "matched_prompt": "最匹配的提示词模板名称（如果没有匹配则返回'no_match'）",
    "confidence": 0.8,
    "reasoning": "选择理由",
    "suggestions": ["改进建议1", "改进建议2"]
}}

优化原则:
1. 保持原始意图不变
2. 使语言更清晰、具体
3. 添加必要的上下文信息
4. 匹配最合适的提示词模板
"""
    
    def _update_model_stats(self, model_name: str, response: ChatResponse):
        """更新模型使用统计"""
        if model_name not in model_usage_stats:
            model_usage_stats[model_name] = {
                "total_requests": 0,
                "total_tokens": 0,
                "total_cost": 0.0,
                "avg_response_time": 0.0,
                "last_used": None
            }
        
        stats = model_usage_stats[model_name]
        stats["total_requests"] += 1
        stats["last_used"] = time.time()
        
        if response.usage:
            stats["total_tokens"] += response.usage.get("total_tokens", 0)
        
        # 更新平均响应时间
        current_avg = stats["avg_response_time"]
        new_avg = (current_avg * (stats["total_requests"] - 1) + response.response_time) / stats["total_requests"]
        stats["avg_response_time"] = new_avg

# --- 初始化函数 ---
async def initialize_components():
    """初始化组件"""
    global model_manager, mlflow_client, available_prompts, performance_optimizer, performance_monitor
    
    try:
        # 初始化模型管理器
        model_manager = MultiModelManager("models_config.yaml")
        logger.info(f"模型管理器已初始化，加载了 {len(model_manager.models)} 个模型")
        
        # 初始化MLflow
        if not MLFLOW_TRACKING_URI:
            logger.error("MLFLOW_TRACKING_URI not set.")
            return False
        
        mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
        mlflow_client = MlflowClient()
        logger.info(f"MLflow client configured for: {MLFLOW_TRACKING_URI}")
        
        # 加载提示词
        available_prompts = await load_all_prompts()
        logger.info(f"Loaded {len(available_prompts)} prompts from MLflow.")
        
        # 初始化性能优化器
        performance_optimizer = PerformanceOptimizer()
        performance_monitor = PerformanceMonitor()
        logger.info("性能优化组件已初始化")
        
        return True
        
    except Exception as e:
        logger.error(f"组件初始化失败: {e}")
        logger.error(traceback.format_exc())
        return False

async def load_all_prompts() -> Dict[str, Any]:
    """从MLflow加载所有提示词"""
    prompts = {}
    
    try:
        experiments = mlflow_client.search_experiments()
        
        for experiment in experiments:
            if experiment.name == "promptlab_prompts":
                runs = mlflow_client.search_runs(
                    experiment_ids=[experiment.experiment_id],
                    filter_string="status = 'FINISHED'",
                    order_by=["start_time DESC"]
                )
                
                for run in runs:
                    try:
                        prompt_name = run.data.tags.get("prompt_name")
                        if prompt_name:
                            artifacts = mlflow_client.list_artifacts(run.info.run_id)
                            
                            for artifact in artifacts:
                                if artifact.path.endswith(".json"):
                                    artifact_path = mlflow_client.download_artifacts(
                                        run.info.run_id, artifact.path
                                    )
                                    
                                    with open(artifact_path, 'r', encoding='utf-8') as f:
                                        prompt_data = json.load(f)
                                    
                                    prompts[prompt_name] = {
                                        "template": prompt_data.get("template", ""),
                                        "tags": run.data.tags,
                                        "version": run.data.tags.get("version", "unknown"),
                                        "run_id": run.info.run_id
                                    }
                                    break
                    except Exception as e:
                        logger.warning(f"加载提示词失败 {run.info.run_id}: {e}")
                        continue
                break
        
        logger.info(f"成功加载 {len(prompts)} 个提示词")
        return prompts
        
    except Exception as e:
        logger.error(f"加载提示词失败: {e}")
        return {}

# --- 主函数 ---
async def main():
    """主函数"""
    logger.info("启动增强版 PromptLab MCP 服务器...")
    
    # 初始化组件
    if not await initialize_components():
        logger.error("组件初始化失败，退出")
        sys.exit(1)
    
    # 创建服务器实例
    server_instance = EnhancedPromptLabServer()
    
    logger.info("增强版 PromptLab MCP 服务器已启动")
    logger.info(f"当前模型: {model_manager.current_model}")
    logger.info(f"可用模型数量: {len(model_manager.list_models())}")
    logger.info(f"可用提示词数量: {len(available_prompts)}")
    
    # 启动服务器
    async with stdio_server() as (read_stream, write_stream):
        await server_instance.server.run(
            read_stream,
            write_stream,
            server_instance.server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())