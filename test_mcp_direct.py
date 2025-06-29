#!/usr/bin/env python3
"""
直接测试MCP服务器功能
"""

import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_mcp_server():
    """测试MCP服务器的所有功能"""
    
    # 服务器参数
    server_params = StdioServerParameters(
        command="python",
        args=["promptlab_server.py"],
        env=None
    )
    
    print("🚀 启动MCP客户端测试...")
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                print("✅ MCP客户端连接成功")
                
                # 初始化
                await session.initialize()
                print("✅ MCP会话初始化成功")
                
                # 获取可用工具
                tools = await session.list_tools()
                print(f"\n📋 可用工具数量: {len(tools.tools)}")
                for tool in tools.tools:
                    print(f"  - {tool.name}: {tool.description}")
                
                print("\n" + "="*50)
                print("🧪 测试 1: list_prompts")
                print("="*50)
                
                try:
                    result = await session.call_tool("list_prompts", {})
                    print(f"✅ list_prompts 成功")
                    print(f"结果: {result.content[0].text}")
                except Exception as e:
                    print(f"❌ list_prompts 失败: {e}")
                
                print("\n" + "="*50)
                print("🧪 测试 2: optimize_query")
                print("="*50)
                
                try:
                    result = await session.call_tool("optimize_query", {
                        "query": "帮我写一个Python函数"
                    })
                    print(f"✅ optimize_query 成功")
                    print(f"结果: {result.content[0].text}")
                except Exception as e:
                    print(f"❌ optimize_query 失败: {e}")
                
                print("\n" + "="*50)
                print("🧪 测试 3: reload_prompts")
                print("="*50)
                
                try:
                    result = await session.call_tool("reload_prompts", {})
                    print(f"✅ reload_prompts 成功")
                    print(f"结果: {result.content[0].text}")
                except Exception as e:
                    print(f"❌ reload_prompts 失败: {e}")
                
                print("\n" + "="*50)
                print("🧪 测试 4: 再次测试 list_prompts (验证reload)")
                print("="*50)
                
                try:
                    result = await session.call_tool("list_prompts", {})
                    print(f"✅ list_prompts (after reload) 成功")
                    print(f"结果: {result.content[0].text}")
                except Exception as e:
                    print(f"❌ list_prompts (after reload) 失败: {e}")
                
    except Exception as e:
        print(f"❌ MCP客户端连接失败: {e}")
        return False
    
    print("\n🎉 所有MCP功能测试完成!")
    return True

if __name__ == "__main__":
    asyncio.run(test_mcp_server())