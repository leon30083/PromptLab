#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多模型接入配置管理系统
Multi-Model Integration Configuration Management System

支持的模型提供商:
- OpenAI (官方和第三方兼容API)
- Google Vertex AI (Gemini)
- Anthropic Claude
- Azure OpenAI
- 本地模型 (Ollama, LocalAI等)
- 自定义API端点
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import yaml
from pathlib import Path

logger = logging.getLogger(__name__)

class ModelProvider(Enum):
    """模型提供商枚举"""
    OPENAI = "openai"
    OPENAI_COMPATIBLE = "openai_compatible"  # 第三方OpenAI格式API
    GOOGLE_VERTEX = "google_vertex"
    ANTHROPIC = "anthropic"
    AZURE_OPENAI = "azure_openai"
    OLLAMA = "ollama"
    LOCAL_AI = "local_ai"
    CUSTOM = "custom"

class ModelType(Enum):
    """模型类型枚举"""
    CHAT = "chat"
    COMPLETION = "completion"
    EMBEDDING = "embedding"
    IMAGE = "image"
    MULTIMODAL = "multimodal"

@dataclass
class ModelConfig:
    """单个模型配置"""
    name: str                    # 模型名称
    provider: ModelProvider      # 提供商
    model_type: ModelType        # 模型类型
    model_id: str               # 模型ID/名称
    api_base: Optional[str] = None       # API基础URL
    api_key: Optional[str] = None        # API密钥
    api_version: Optional[str] = None    # API版本
    max_tokens: Optional[int] = None     # 最大token数
    temperature: float = 0.7             # 温度参数
    timeout: int = 30                    # 超时时间(秒)
    retry_count: int = 3                 # 重试次数
    enabled: bool = True                 # 是否启用
    priority: int = 1                    # 优先级(1-10, 数字越小优先级越高)
    cost_per_1k_tokens: float = 0.0      # 每1K token成本
    rate_limit: Optional[int] = None     # 速率限制(请求/分钟)
    extra_params: Dict[str, Any] = None  # 额外参数
    
    def __post_init__(self):
        if self.extra_params is None:
            self.extra_params = {}

@dataclass
class ModelGroup:
    """模型组配置(用于负载均衡和故障转移)"""
    name: str
    models: List[str]  # 模型名称列表
    strategy: str = "round_robin"  # 策略: round_robin, priority, random
    enabled: bool = True
    description: str = ""

class MultiModelManager:
    """多模型管理器"""
    
    def __init__(self, config_file: str = "models_config.yaml"):
        self.config_file = Path(config_file)
        self.models: Dict[str, ModelConfig] = {}
        self.groups: Dict[str, ModelGroup] = {}
        self.current_model: Optional[str] = None
        self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        if not self.config_file.exists():
            logger.warning(f"配置文件 {self.config_file} 不存在，创建默认配置")
            self.create_default_config()
            return
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            
            # 加载模型配置
            for model_data in config_data.get('models', []):
                model_config = ModelConfig(
                    name=model_data['name'],
                    provider=ModelProvider(model_data['provider']),
                    model_type=ModelType(model_data['model_type']),
                    model_id=model_data['model_id'],
                    api_base=model_data.get('api_base'),
                    api_key=model_data.get('api_key'),
                    api_version=model_data.get('api_version'),
                    max_tokens=model_data.get('max_tokens'),
                    temperature=model_data.get('temperature', 0.7),
                    timeout=model_data.get('timeout', 30),
                    retry_count=model_data.get('retry_count', 3),
                    enabled=model_data.get('enabled', True),
                    priority=model_data.get('priority', 1),
                    cost_per_1k_tokens=model_data.get('cost_per_1k_tokens', 0.0),
                    rate_limit=model_data.get('rate_limit'),
                    extra_params=model_data.get('extra_params', {})
                )
                self.models[model_config.name] = model_config
            
            # 加载模型组配置
            for group_data in config_data.get('groups', []):
                group = ModelGroup(
                    name=group_data['name'],
                    models=group_data['models'],
                    strategy=group_data.get('strategy', 'round_robin'),
                    enabled=group_data.get('enabled', True),
                    description=group_data.get('description', '')
                )
                self.groups[group.name] = group
            
            # 设置当前模型
            self.current_model = config_data.get('current_model')
            
            logger.info(f"成功加载 {len(self.models)} 个模型配置和 {len(self.groups)} 个模型组")
            
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            self.create_default_config()
    
    def create_default_config(self):
        """创建默认配置"""
        default_models = [
            ModelConfig(
                name="gemini-2.5-pro",
                provider=ModelProvider.GOOGLE_VERTEX,
                model_type=ModelType.CHAT,
                model_id="gemini-2.5-pro",
                temperature=0.1,
                priority=1,
                cost_per_1k_tokens=0.002
            ),
            ModelConfig(
                name="gpt-4o",
                provider=ModelProvider.OPENAI,
                model_type=ModelType.CHAT,
                model_id="gpt-4o",
                api_key="${OPENAI_API_KEY}",
                temperature=0.7,
                priority=2,
                cost_per_1k_tokens=0.03
            ),
            ModelConfig(
                name="claude-3.5-sonnet",
                provider=ModelProvider.ANTHROPIC,
                model_type=ModelType.CHAT,
                model_id="claude-3-5-sonnet-20241022",
                api_key="${ANTHROPIC_API_KEY}",
                temperature=0.7,
                priority=3,
                cost_per_1k_tokens=0.015
            ),
            ModelConfig(
                name="deepseek-chat",
                provider=ModelProvider.OPENAI_COMPATIBLE,
                model_type=ModelType.CHAT,
                model_id="deepseek-chat",
                api_base="https://api.deepseek.com/v1",
                api_key="${DEEPSEEK_API_KEY}",
                temperature=0.7,
                priority=4,
                cost_per_1k_tokens=0.0014
            ),
            ModelConfig(
                name="qwen-max",
                provider=ModelProvider.OPENAI_COMPATIBLE,
                model_type=ModelType.CHAT,
                model_id="qwen-max",
                api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
                api_key="${QWEN_API_KEY}",
                temperature=0.7,
                priority=5,
                cost_per_1k_tokens=0.008
            ),
            ModelConfig(
                name="ollama-llama3.1",
                provider=ModelProvider.OLLAMA,
                model_type=ModelType.CHAT,
                model_id="llama3.1:8b",
                api_base="http://localhost:11434",
                temperature=0.7,
                priority=6,
                cost_per_1k_tokens=0.0,
                enabled=False  # 默认禁用，需要本地安装Ollama
            )
        ]
        
        default_groups = [
            ModelGroup(
                name="primary_chat",
                models=["gemini-2.5-pro", "gpt-4o", "claude-3.5-sonnet"],
                strategy="priority",
                description="主要聊天模型组，按优先级故障转移"
            ),
            ModelGroup(
                name="cost_effective",
                models=["deepseek-chat", "qwen-max"],
                strategy="round_robin",
                description="成本效益模型组，轮询负载均衡"
            )
        ]
        
        # 保存默认配置
        for model in default_models:
            self.models[model.name] = model
        
        for group in default_groups:
            self.groups[group.name] = group
        
        self.current_model = "gemini-2.5-pro"
        self.save_config()
    
    def save_config(self):
        """保存配置到文件"""
        config_data = {
            'current_model': self.current_model,
            'models': [asdict(model) for model in self.models.values()],
            'groups': [asdict(group) for group in self.groups.values()]
        }
        
        # 转换枚举为字符串
        for model_data in config_data['models']:
            model_data['provider'] = model_data['provider'].value
            model_data['model_type'] = model_data['model_type'].value
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(config_data, f, default_flow_style=False, 
                         allow_unicode=True, sort_keys=False)
            logger.info(f"配置已保存到 {self.config_file}")
        except Exception as e:
            logger.error(f"保存配置失败: {e}")
    
    def add_model(self, model_config: ModelConfig):
        """添加模型配置"""
        self.models[model_config.name] = model_config
        logger.info(f"已添加模型: {model_config.name}")
    
    def remove_model(self, model_name: str):
        """移除模型配置"""
        if model_name in self.models:
            del self.models[model_name]
            logger.info(f"已移除模型: {model_name}")
        else:
            logger.warning(f"模型不存在: {model_name}")
    
    def get_model(self, model_name: str) -> Optional[ModelConfig]:
        """获取模型配置"""
        return self.models.get(model_name)
    
    def list_models(self, enabled_only: bool = True) -> List[ModelConfig]:
        """列出所有模型"""
        models = list(self.models.values())
        if enabled_only:
            models = [m for m in models if m.enabled]
        return sorted(models, key=lambda x: x.priority)
    
    def get_models_by_provider(self, provider: ModelProvider) -> List[ModelConfig]:
        """按提供商获取模型"""
        return [m for m in self.models.values() if m.provider == provider and m.enabled]
    
    def get_models_by_type(self, model_type: ModelType) -> List[ModelConfig]:
        """按类型获取模型"""
        return [m for m in self.models.values() if m.model_type == model_type and m.enabled]
    
    def set_current_model(self, model_name: str):
        """设置当前模型"""
        if model_name in self.models:
            self.current_model = model_name
            logger.info(f"当前模型已设置为: {model_name}")
        else:
            logger.error(f"模型不存在: {model_name}")
    
    def get_current_model(self) -> Optional[ModelConfig]:
        """获取当前模型配置"""
        if self.current_model:
            return self.models.get(self.current_model)
        return None
    
    def validate_config(self) -> List[str]:
        """验证配置"""
        errors = []
        
        for name, model in self.models.items():
            if not model.model_id:
                errors.append(f"模型 {name} 缺少 model_id")
            
            if model.provider in [ModelProvider.OPENAI, ModelProvider.ANTHROPIC, ModelProvider.OPENAI_COMPATIBLE]:
                if not model.api_key:
                    errors.append(f"模型 {name} 缺少 api_key")
            
            if model.provider == ModelProvider.OPENAI_COMPATIBLE:
                if not model.api_base:
                    errors.append(f"模型 {name} 缺少 api_base")
        
        return errors
    
    def get_config_summary(self) -> Dict[str, Any]:
        """获取配置摘要"""
        enabled_models = [m for m in self.models.values() if m.enabled]
        
        provider_counts = {}
        for model in enabled_models:
            provider = model.provider.value
            provider_counts[provider] = provider_counts.get(provider, 0) + 1
        
        return {
            'total_models': len(self.models),
            'enabled_models': len(enabled_models),
            'current_model': self.current_model,
            'provider_distribution': provider_counts,
            'total_groups': len(self.groups),
            'config_file': str(self.config_file)
        }

# 使用示例
if __name__ == "__main__":
    # 创建模型管理器
    manager = MultiModelManager()
    
    # 打印配置摘要
    summary = manager.get_config_summary()
    print("=== 模型配置摘要 ===")
    for key, value in summary.items():
        print(f"{key}: {value}")
    
    # 列出所有启用的模型
    print("\n=== 启用的模型 ===")
    for model in manager.list_models():
        print(f"- {model.name} ({model.provider.value}) - 优先级: {model.priority}")
    
    # 验证配置
    errors = manager.validate_config()
    if errors:
        print("\n=== 配置错误 ===")
        for error in errors:
            print(f"- {error}")
    else:
        print("\n✅ 配置验证通过")