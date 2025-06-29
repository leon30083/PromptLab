import mlflow
import logging
import traceback

# 设置详细日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 设置MLflow URI
mlflow.set_tracking_uri('http://127.0.0.1:5000')

print("=== 调试提示词加载 ===")

# 测试已知的提示词
known_prompts = {
    "essay_prompt": "9",
    "email_prompt": "9", 
    "technical_prompt": "9",
    "creative_prompt": "9",
    "test_prompt": "1"
}

for name, version in known_prompts.items():
    try:
        print(f"\n尝试加载: {name} 版本 {version}")
        prompt = mlflow.genai.load_prompt(f"prompts:/{name}/{version}")
        print(f"✓ 成功加载: {prompt.name}")
        print(f"  模板长度: {len(prompt.template)}")
        print(f"  版本: {getattr(prompt, 'version', 'unknown')}")
        print(f"  标签: {getattr(prompt, 'tags', {})}")
    except Exception as e:
        print(f"✗ 加载失败: {name} - {str(e)}")
        traceback.print_exc()

print("\n=== 调试完成 ===")

# 将结果写入文件
with open('debug_output.txt', 'w', encoding='utf-8') as f:
    f.write("调试结果已保存到此文件\n")