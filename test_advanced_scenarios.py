#!/usr/bin/env python3
"""
高级场景和边界情况测试
"""

import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_advanced_scenarios():
    """测试高级场景和边界情况"""
    
    server_params = StdioServerParameters(
        command="python",
        args=["promptlab_server.py"],
        env=None
    )
    
    print("🔬 启动高级场景测试...")
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                print("\n" + "="*60)
                print("🧪 测试 1: optimize_query - 各种查询类型")
                print("="*60)
                
                test_queries = [
                    "写一篇关于人工智能的文章",
                    "给老板发邮件请假",
                    "解释什么是机器学习",
                    "写一个科幻小说",
                    "创建一个Python函数",
                    "这是一个完全不相关的查询，应该没有匹配",
                    "",  # 空查询
                    "a" * 1000,  # 超长查询
                ]
                
                for i, query in enumerate(test_queries, 1):
                    try:
                        result = await session.call_tool("optimize_query", {"query": query})
                        response = json.loads(result.content[0].text)
                        print(f"  {i}. 查询: '{query[:50]}{'...' if len(query) > 50 else ''}'")
                        print(f"     状态: {response.get('status', 'unknown')}")
                        if response.get('matched_prompt'):
                            print(f"     匹配: {response['matched_prompt']['name']}")
                        print(f"     相似度: {response.get('similarity_score', 'N/A')}")
                        print()
                    except Exception as e:
                        print(f"  {i}. 查询失败: {e}")
                
                print("\n" + "="*60)
                print("🧪 测试 2: 并发请求测试")
                print("="*60)
                
                # 并发测试
                concurrent_tasks = []
                for i in range(5):
                    task = session.call_tool("list_prompts", {})
                    concurrent_tasks.append(task)
                
                try:
                    results = await asyncio.gather(*concurrent_tasks)
                    print(f"✅ 并发请求成功: {len(results)} 个请求同时完成")
                except Exception as e:
                    print(f"❌ 并发请求失败: {e}")
                
                print("\n" + "="*60)
                print("🧪 测试 3: 错误处理测试")
                print("="*60)
                
                # 测试无效工具调用
                try:
                    await session.call_tool("invalid_tool", {})
                    print("❌ 应该抛出错误但没有")
                except Exception as e:
                    print(f"✅ 正确处理无效工具: {type(e).__name__}")
                
                # 测试无效参数
                try:
                    await session.call_tool("optimize_query", {"invalid_param": "test"})
                    print("❌ 应该抛出错误但没有")
                except Exception as e:
                    print(f"✅ 正确处理无效参数: {type(e).__name__}")
                
                print("\n" + "="*60)
                print("🧪 测试 4: 性能测试")
                print("="*60)
                
                import time
                
                # 测试响应时间
                start_time = time.time()
                for i in range(10):
                    await session.call_tool("list_prompts", {})
                end_time = time.time()
                
                avg_time = (end_time - start_time) / 10
                print(f"✅ 平均响应时间: {avg_time:.3f} 秒 (10次调用)")
                
                # 测试大量查询优化
                start_time = time.time()
                for i in range(5):
                    await session.call_tool("optimize_query", {
                        "query": f"测试查询 {i}: 写一篇关于技术的文章"
                    })
                end_time = time.time()
                
                avg_optimize_time = (end_time - start_time) / 5
                print(f"✅ 查询优化平均时间: {avg_optimize_time:.3f} 秒 (5次调用)")
                
                print("\n" + "="*60)
                print("🧪 测试 5: 数据一致性测试")
                print("="*60)
                
                # 多次调用list_prompts，确保结果一致
                results = []
                for i in range(3):
                    result = await session.call_tool("list_prompts", {})
                    response = json.loads(result.content[0].text)
                    results.append(response['count'])
                
                if len(set(results)) == 1:
                    print(f"✅ 数据一致性测试通过: 所有调用返回 {results[0]} 个提示词")
                else:
                    print(f"❌ 数据一致性测试失败: 返回值不一致 {results}")
                
    except Exception as e:
        print(f"❌ 高级测试失败: {e}")
        return False
    
    print("\n🎉 所有高级场景测试完成!")
    return True

if __name__ == "__main__":
    asyncio.run(test_advanced_scenarios())