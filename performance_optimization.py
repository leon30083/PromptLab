#!/usr/bin/env python3
"""
性能优化建议和实现
"""

import asyncio
import time
import hashlib
from functools import lru_cache
from typing import Dict, Any, Optional
import json

class PerformanceOptimizer:
    """性能优化器"""
    
    def __init__(self):
        self.query_cache = {}
        self.cache_ttl = 300  # 5分钟缓存
        self.cache_timestamps = {}
        self.stats = {
            'cache_hits': 0,
            'cache_misses': 0,
            'total_queries': 0,
            'avg_response_time': 0
        }
    
    def _get_cache_key(self, query: str) -> str:
        """生成缓存键"""
        return hashlib.md5(query.encode()).hexdigest()
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """检查缓存是否有效"""
        if cache_key not in self.cache_timestamps:
            return False
        
        age = time.time() - self.cache_timestamps[cache_key]
        return age < self.cache_ttl
    
    def get_cached_result(self, query: str) -> Optional[Dict[str, Any]]:
        """获取缓存结果"""
        cache_key = self._get_cache_key(query)
        
        if cache_key in self.query_cache and self._is_cache_valid(cache_key):
            self.stats['cache_hits'] += 1
            return self.query_cache[cache_key]
        
        self.stats['cache_misses'] += 1
        return None
    
    def cache_result(self, query: str, result: Dict[str, Any]):
        """缓存结果"""
        cache_key = self._get_cache_key(query)
        self.query_cache[cache_key] = result
        self.cache_timestamps[cache_key] = time.time()
    
    def clear_expired_cache(self):
        """清理过期缓存"""
        current_time = time.time()
        expired_keys = [
            key for key, timestamp in self.cache_timestamps.items()
            if current_time - timestamp > self.cache_ttl
        ]
        
        for key in expired_keys:
            self.query_cache.pop(key, None)
            self.cache_timestamps.pop(key, None)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取性能统计"""
        total_requests = self.stats['cache_hits'] + self.stats['cache_misses']
        cache_hit_rate = (self.stats['cache_hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            **self.stats,
            'cache_hit_rate': f"{cache_hit_rate:.2f}%",
            'cache_size': len(self.query_cache)
        }

class AsyncBatchProcessor:
    """异步批处理器"""
    
    def __init__(self, batch_size: int = 5, timeout: float = 1.0):
        self.batch_size = batch_size
        self.timeout = timeout
        self.pending_requests = []
        self.processing = False
    
    async def add_request(self, request_data: Dict[str, Any]) -> Any:
        """添加请求到批处理队列"""
        future = asyncio.Future()
        self.pending_requests.append((request_data, future))
        
        if not self.processing:
            asyncio.create_task(self._process_batch())
        
        return await future
    
    async def _process_batch(self):
        """处理批次"""
        self.processing = True
        
        try:
            while self.pending_requests:
                # 等待批次填满或超时
                await asyncio.sleep(self.timeout)
                
                if not self.pending_requests:
                    break
                
                # 取出一批请求
                batch = self.pending_requests[:self.batch_size]
                self.pending_requests = self.pending_requests[self.batch_size:]
                
                # 并行处理批次
                tasks = []
                for request_data, future in batch:
                    task = self._process_single_request(request_data, future)
                    tasks.append(task)
                
                await asyncio.gather(*tasks, return_exceptions=True)
        
        finally:
            self.processing = False
    
    async def _process_single_request(self, request_data: Dict[str, Any], future: asyncio.Future):
        """处理单个请求"""
        try:
            # 这里应该是实际的处理逻辑
            result = await self._simulate_processing(request_data)
            future.set_result(result)
        except Exception as e:
            future.set_exception(e)
    
    async def _simulate_processing(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """模拟处理过程"""
        await asyncio.sleep(0.1)  # 模拟处理时间
        return {"processed": True, "data": request_data}

class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.metrics = {
            'request_count': 0,
            'total_response_time': 0,
            'error_count': 0,
            'slow_requests': 0
        }
        self.slow_threshold = 5.0  # 5秒阈值
    
    def record_request(self, response_time: float, success: bool = True):
        """记录请求指标"""
        self.metrics['request_count'] += 1
        self.metrics['total_response_time'] += response_time
        
        if not success:
            self.metrics['error_count'] += 1
        
        if response_time > self.slow_threshold:
            self.metrics['slow_requests'] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        if self.metrics['request_count'] == 0:
            return self.metrics
        
        avg_response_time = self.metrics['total_response_time'] / self.metrics['request_count']
        error_rate = (self.metrics['error_count'] / self.metrics['request_count']) * 100
        slow_request_rate = (self.metrics['slow_requests'] / self.metrics['request_count']) * 100
        
        return {
            **self.metrics,
            'avg_response_time': f"{avg_response_time:.3f}s",
            'error_rate': f"{error_rate:.2f}%",
            'slow_request_rate': f"{slow_request_rate:.2f}%"
        }

def create_optimized_server_config() -> Dict[str, Any]:
    """创建优化的服务器配置"""
    return {
        'cache': {
            'enabled': True,
            'ttl': 300,  # 5分钟
            'max_size': 1000
        },
        'batch_processing': {
            'enabled': True,
            'batch_size': 5,
            'timeout': 1.0
        },
        'monitoring': {
            'enabled': True,
            'slow_threshold': 5.0,
            'metrics_interval': 60
        },
        'optimization': {
            'async_processing': True,
            'connection_pooling': True,
            'request_timeout': 30.0
        }
    }

async def test_performance_optimizations():
    """测试性能优化"""
    print("🚀 测试性能优化功能...")
    
    # 测试缓存
    optimizer = PerformanceOptimizer()
    
    print("\n📋 测试查询缓存:")
    test_query = "写一篇关于AI的文章"
    
    # 第一次查询 (缓存未命中)
    start_time = time.time()
    cached_result = optimizer.get_cached_result(test_query)
    print(f"  缓存查询结果: {cached_result}")
    
    # 模拟处理并缓存结果
    result = {"status": "success", "matched_prompt": "essay_prompt"}
    optimizer.cache_result(test_query, result)
    
    # 第二次查询 (缓存命中)
    cached_result = optimizer.get_cached_result(test_query)
    print(f"  缓存命中结果: {cached_result}")
    
    print(f"  缓存统计: {optimizer.get_stats()}")
    
    # 测试批处理
    print("\n⚡ 测试批处理:")
    batch_processor = AsyncBatchProcessor(batch_size=3, timeout=0.5)
    
    # 并发发送多个请求
    tasks = []
    for i in range(5):
        task = batch_processor.add_request({"query": f"测试查询 {i}"})
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    print(f"  批处理结果: {len(results)} 个请求处理完成")
    
    # 测试性能监控
    print("\n📊 测试性能监控:")
    monitor = PerformanceMonitor()
    
    # 模拟一些请求
    monitor.record_request(0.1, True)   # 快速成功请求
    monitor.record_request(2.5, True)   # 正常请求
    monitor.record_request(6.0, True)   # 慢请求
    monitor.record_request(1.0, False)  # 失败请求
    
    print(f"  性能指标: {monitor.get_metrics()}")
    
    print("\n🎯 优化配置:")
    config = create_optimized_server_config()
    print(json.dumps(config, indent=2, ensure_ascii=False))
    
    print("\n✅ 性能优化测试完成!")

if __name__ == "__main__":
    asyncio.run(test_performance_optimizations())