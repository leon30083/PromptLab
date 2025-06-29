#!/usr/bin/env python3

import asyncio
import json
import promptlab_server
from promptlab_server import initialize_components

async def test_mcp():
    output = []
    output.append("Testing MCP server components...")
    
    # Test initialization
    success = await initialize_components()
    output.append(f"Initialization success: {success}")
    
    # Check available prompts
    output.append(f"Available prompts count: {len(promptlab_server.available_prompts)}")
    output.append(f"Available prompts: {list(promptlab_server.available_prompts.keys())}")
    
    # Test each prompt
    for name, data in promptlab_server.available_prompts.items():
        output.append(f"\nPrompt: {name}")
        output.append(f"  Version: {data.get('version', 'unknown')}")
        output.append(f"  Template preview: {data.get('template', '')[:100]}...")
    
    # Write to file
    with open('test_output.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(output))
    
    print('Test completed. Results written to test_output.txt')

if __name__ == "__main__":
    asyncio.run(test_mcp())