#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型适配器系统
Model Adapters System

统一不同模型提供商的API接口，提供一致的调用方式
"""

import os
import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, AsyncGenerator, Union
from dataclasses import dataclass
import json
import time
from enum import Enum

# 导入各种客户端库
try:
    import openai
except ImportError:
    openai = None

try:
    from langchain_google_vertexai import ChatVertexAI
    from langchain_core.messages import HumanMessage, SystemMessage
except ImportError:
    ChatVertexAI = None

try:
    import anthropic
except ImportError:
    anthropic = None

try:
    import httpx
except ImportError:
    httpx = None

from multi_model_config import ModelConfig, ModelProvider, ModelType

logger = logging.getLogger(__name__)

@dataclass
class ChatMessage:
    """统一的聊天消息格式"""
    role: str  # system, user, assistant
    content: str
    name: Optional[str] = None
    function_call: Optional[Dict[str, Any]] = None

@dataclass
class ChatResponse:
    """统一的聊天响应格式"""
    content: str
    model: str
    usage: Optional[Dict[str, int]] = None
    finish_reason: Optional[str] = None
    response_time: float = 0.0
    provider: str = ""

class ModelAdapter(ABC):
    """模型适配器基类"""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.client = None
        self._initialize_client()
    
    @abstractmethod
    def _initialize_client(self):
        """初始化客户端"""
        pass
    
    @abstractmethod
    async def chat_completion(self, messages: List[ChatMessage], **kwargs) -> ChatResponse:
        """聊天完成"""
        pass
    
    @abstractmethod
    async def stream_chat_completion(self, messages: List[ChatMessage], **kwargs) -> AsyncGenerator[str, None]:
        """流式聊天完成"""
        pass
    
    def _resolve_api_key(self, api_key: str) -> str:
        """解析API密钥（支持环境变量）"""
        if api_key and api_key.startswith('${') and api_key.endswith('}'):
            env_var = api_key[2:-1]
            return os.getenv(env_var, '')
        return api_key or ''
    
    def _prepare_messages(self, messages: List[ChatMessage]) -> List[Dict[str, str]]:
        """准备消息格式"""
        return [{'role': msg.role, 'content': msg.content} for msg in messages]

class OpenAIAdapter(ModelAdapter):
    """OpenAI适配器"""
    
    def _initialize_client(self):
        if not openai:
            raise ImportError("请安装 openai 库: pip install openai")
        
        api_key = self._resolve_api_key(self.config.api_key)
        
        if self.config.provider == ModelProvider.OPENAI_COMPATIBLE:
            # 第三方OpenAI兼容API
            self.client = openai.AsyncOpenAI(
                api_key=api_key,
                base_url=self.config.api_base,
                timeout=self.config.timeout
            )
        else:
            # 官方OpenAI API
            self.client = openai.AsyncOpenAI(
                api_key=api_key,
                timeout=self.config.timeout
            )
        
        logger.info(f"OpenAI客户端已初始化: {self.config.name}")
    
    async def chat_completion(self, messages: List[ChatMessage], **kwargs) -> ChatResponse:
        start_time = time.time()
        
        try:
            openai_messages = self._prepare_messages(messages)
            
            response = await self.client.chat.completions.create(
                model=self.config.model_id,
                messages=openai_messages,
                temperature=kwargs.get('temperature', self.config.temperature),
                max_tokens=kwargs.get('max_tokens', self.config.max_tokens),
                **self.config.extra_params
            )
            
            response_time = time.time() - start_time
            
            return ChatResponse(
                content=response.choices[0].message.content,
                model=response.model,
                usage={
                    'prompt_tokens': response.usage.prompt_tokens,
                    'completion_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens
                } if response.usage else None,
                finish_reason=response.choices[0].finish_reason,
                response_time=response_time,
                provider=self.config.provider.value
            )
            
        except Exception as e:
            logger.error(f"OpenAI API调用失败: {e}")
            raise
    
    async def stream_chat_completion(self, messages: List[ChatMessage], **kwargs) -> AsyncGenerator[str, None]:
        try:
            openai_messages = self._prepare_messages(messages)
            
            stream = await self.client.chat.completions.create(
                model=self.config.model_id,
                messages=openai_messages,
                temperature=kwargs.get('temperature', self.config.temperature),
                max_tokens=kwargs.get('max_tokens', self.config.max_tokens),
                stream=True,
                **self.config.extra_params
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"OpenAI流式API调用失败: {e}")
            raise

class VertexAIAdapter(ModelAdapter):
    """Google Vertex AI适配器"""
    
    def _initialize_client(self):
        if not ChatVertexAI:
            raise ImportError("请安装 langchain-google-vertexai 库")
        
        project_id = os.getenv('GCP_PROJECT_ID')
        location = os.getenv('GCP_LOCATION', 'us-central1')
        
        if not project_id:
            raise ValueError("请设置 GCP_PROJECT_ID 环境变量")
        
        self.client = ChatVertexAI(
            project=project_id,
            location=location,
            model_name=self.config.model_id,
            temperature=self.config.temperature,
            max_output_tokens=self.config.max_tokens,
            convert_system_message_to_human=True
        )
        
        logger.info(f"Vertex AI客户端已初始化: {self.config.name}")
    
    async def chat_completion(self, messages: List[ChatMessage], **kwargs) -> ChatResponse:
        start_time = time.time()
        
        try:
            # 转换消息格式
            langchain_messages = []
            for msg in messages:
                if msg.role == 'system':
                    langchain_messages.append(SystemMessage(content=msg.content))
                elif msg.role == 'user':
                    langchain_messages.append(HumanMessage(content=msg.content))
                # assistant消息在Vertex AI中通常不需要显式添加
            
            response = await self.client.ainvoke(langchain_messages)
            response_time = time.time() - start_time
            
            return ChatResponse(
                content=response.content,
                model=self.config.model_id,
                usage=None,  # Vertex AI不直接提供token使用信息
                finish_reason="stop",
                response_time=response_time,
                provider=self.config.provider.value
            )
            
        except Exception as e:
            logger.error(f"Vertex AI API调用失败: {e}")
            raise
    
    async def stream_chat_completion(self, messages: List[ChatMessage], **kwargs) -> AsyncGenerator[str, None]:
        try:
            # 转换消息格式
            langchain_messages = []
            for msg in messages:
                if msg.role == 'system':
                    langchain_messages.append(SystemMessage(content=msg.content))
                elif msg.role == 'user':
                    langchain_messages.append(HumanMessage(content=msg.content))
            
            async for chunk in self.client.astream(langchain_messages):
                if hasattr(chunk, 'content') and chunk.content:
                    yield chunk.content
                    
        except Exception as e:
            logger.error(f"Vertex AI流式API调用失败: {e}")
            raise

class AnthropicAdapter(ModelAdapter):
    """Anthropic Claude适配器"""
    
    def _initialize_client(self):
        if not anthropic:
            raise ImportError("请安装 anthropic 库: pip install anthropic")
        
        api_key = self._resolve_api_key(self.config.api_key)
        
        self.client = anthropic.AsyncAnthropic(
            api_key=api_key,
            timeout=self.config.timeout
        )
        
        logger.info(f"Anthropic客户端已初始化: {self.config.name}")
    
    async def chat_completion(self, messages: List[ChatMessage], **kwargs) -> ChatResponse:
        start_time = time.time()
        
        try:
            # Anthropic需要分离system消息
            system_message = ""
            user_messages = []
            
            for msg in messages:
                if msg.role == 'system':
                    system_message = msg.content
                else:
                    user_messages.append({
                        'role': msg.role,
                        'content': msg.content
                    })
            
            response = await self.client.messages.create(
                model=self.config.model_id,
                system=system_message if system_message else None,
                messages=user_messages,
                temperature=kwargs.get('temperature', self.config.temperature),
                max_tokens=kwargs.get('max_tokens', self.config.max_tokens or 4096),
                **self.config.extra_params
            )
            
            response_time = time.time() - start_time
            
            return ChatResponse(
                content=response.content[0].text,
                model=response.model,
                usage={
                    'prompt_tokens': response.usage.input_tokens,
                    'completion_tokens': response.usage.output_tokens,
                    'total_tokens': response.usage.input_tokens + response.usage.output_tokens
                },
                finish_reason=response.stop_reason,
                response_time=response_time,
                provider=self.config.provider.value
            )
            
        except Exception as e:
            logger.error(f"Anthropic API调用失败: {e}")
            raise
    
    async def stream_chat_completion(self, messages: List[ChatMessage], **kwargs) -> AsyncGenerator[str, None]:
        try:
            # Anthropic需要分离system消息
            system_message = ""
            user_messages = []
            
            for msg in messages:
                if msg.role == 'system':
                    system_message = msg.content
                else:
                    user_messages.append({
                        'role': msg.role,
                        'content': msg.content
                    })
            
            async with self.client.messages.stream(
                model=self.config.model_id,
                system=system_message if system_message else None,
                messages=user_messages,
                temperature=kwargs.get('temperature', self.config.temperature),
                max_tokens=kwargs.get('max_tokens', self.config.max_tokens or 4096),
                **self.config.extra_params
            ) as stream:
                async for text in stream.text_stream:
                    yield text
                    
        except Exception as e:
            logger.error(f"Anthropic流式API调用失败: {e}")
            raise

class OllamaAdapter(ModelAdapter):
    """Ollama本地模型适配器"""
    
    def _initialize_client(self):
        if not httpx:
            raise ImportError("请安装 httpx 库: pip install httpx")
        
        self.base_url = self.config.api_base or "http://localhost:11434"
        self.client = httpx.AsyncClient(timeout=self.config.timeout)
        
        logger.info(f"Ollama客户端已初始化: {self.config.name}")
    
    async def chat_completion(self, messages: List[ChatMessage], **kwargs) -> ChatResponse:
        start_time = time.time()
        
        try:
            ollama_messages = self._prepare_messages(messages)
            
            payload = {
                "model": self.config.model_id,
                "messages": ollama_messages,
                "stream": False,
                "options": {
                    "temperature": kwargs.get('temperature', self.config.temperature),
                    "num_predict": kwargs.get('max_tokens', self.config.max_tokens),
                    **self.config.extra_params
                }
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/chat",
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            response_time = time.time() - start_time
            
            return ChatResponse(
                content=result['message']['content'],
                model=result['model'],
                usage=None,  # Ollama不提供详细的token使用信息
                finish_reason="stop",
                response_time=response_time,
                provider=self.config.provider.value
            )
            
        except Exception as e:
            logger.error(f"Ollama API调用失败: {e}")
            raise
    
    async def stream_chat_completion(self, messages: List[ChatMessage], **kwargs) -> AsyncGenerator[str, None]:
        try:
            ollama_messages = self._prepare_messages(messages)
            
            payload = {
                "model": self.config.model_id,
                "messages": ollama_messages,
                "stream": True,
                "options": {
                    "temperature": kwargs.get('temperature', self.config.temperature),
                    "num_predict": kwargs.get('max_tokens', self.config.max_tokens),
                    **self.config.extra_params
                }
            }
            
            async with self.client.stream(
                "POST",
                f"{self.base_url}/api/chat",
                json=payload
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line:
                        try:
                            chunk = json.loads(line)
                            if 'message' in chunk and 'content' in chunk['message']:
                                yield chunk['message']['content']
                        except json.JSONDecodeError:
                            continue
                            
        except Exception as e:
            logger.error(f"Ollama流式API调用失败: {e}")
            raise

class ModelAdapterFactory:
    """模型适配器工厂"""
    
    _adapters = {
        ModelProvider.OPENAI: OpenAIAdapter,
        ModelProvider.OPENAI_COMPATIBLE: OpenAIAdapter,
        ModelProvider.GOOGLE_VERTEX: VertexAIAdapter,
        ModelProvider.ANTHROPIC: AnthropicAdapter,
        ModelProvider.OLLAMA: OllamaAdapter,
    }
    
    @classmethod
    def create_adapter(cls, config: ModelConfig) -> ModelAdapter:
        """创建模型适配器"""
        adapter_class = cls._adapters.get(config.provider)
        
        if not adapter_class:
            raise ValueError(f"不支持的模型提供商: {config.provider}")
        
        return adapter_class(config)
    
    @classmethod
    def register_adapter(cls, provider: ModelProvider, adapter_class: type):
        """注册自定义适配器"""
        cls._adapters[provider] = adapter_class
        logger.info(f"已注册适配器: {provider.value} -> {adapter_class.__name__}")

# 使用示例
if __name__ == "__main__":
    import asyncio
    from multi_model_config import MultiModelManager
    
    async def test_adapters():
        # 加载模型配置
        manager = MultiModelManager()
        
        # 测试消息
        messages = [
            ChatMessage(role="system", content="你是一个有用的AI助手。"),
            ChatMessage(role="user", content="请简单介绍一下人工智能。")
        ]
        
        # 测试每个启用的模型
        for model_config in manager.list_models():
            try:
                print(f"\n=== 测试模型: {model_config.name} ===")
                
                # 创建适配器
                adapter = ModelAdapterFactory.create_adapter(model_config)
                
                # 测试聊天完成
                response = await adapter.chat_completion(messages)
                
                print(f"响应时间: {response.response_time:.2f}秒")
                print(f"内容: {response.content[:100]}...")
                
                if response.usage:
                    print(f"Token使用: {response.usage}")
                
            except Exception as e:
                print(f"模型 {model_config.name} 测试失败: {e}")
    
    # 运行测试
    # asyncio.run(test_adapters())
    print("模型适配器系统已就绪")
    print("支持的提供商:", [p.value for p in ModelAdapterFactory._adapters.keys()])