#!/usr/bin/env python3
"""
直接测试Qwen API集成，绕过LiteLLM代理
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv(os.path.join(os.path.dirname(__file__), ".env.nvwa"))

# 测试直接调用OpenAI客户端
def test_direct_qwen():
    """直接测试Qwen API"""
    print("=== 直接测试Qwen API集成 ===")
    
    # 检查必要的环境变量
    required_vars = ['QWEN_API_KEY', 'QWEN_API_BASE']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"缺少必要的环境变量: {missing_vars}")
        return False
    
    print("✓ 环境变量配置正确")
    
    try:
        from openai import OpenAI
        
        # 创建OpenAI客户端
        client = OpenAI(
            api_key=os.getenv("QWEN_API_KEY"),
            base_url=os.getenv("QWEN_API_BASE")
        )
        
        print("✓ OpenAI客户端创建成功")
        
        # 测试对话
        print("  测试qwen-turbo模型...")
        response = client.chat.completions.create(
            model="qwen-turbo",
            messages=[{"role": "user", "content": "Hello, this is a test."}],
            max_tokens=50
        )
        
        print(f"  ✓ API调用成功，响应: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

def test_monkey_agent():
    """测试MonkeyOpenAIAgent类"""
    print("\n=== 测试MonkeyOpenAIAgent类 ===")
    
    try:
        # 将nvwa目录添加到Python路径
        sys.path.insert(0, os.path.dirname(__file__))
        
        from nvwa.agent.monkey.openai import MonkeyOpenAIAgent
        from nvwa.context import ContextManager
        from nvwa.sky.task import PatchTask
        
        print("✓ 成功导入所需类")
        
        # 创建PatchTask实例
        from nvwa.parser.sanitizer import Sanitizer
        patch_task = PatchTask(
            project="test_project",
            tag="test_tag",
            sanitizer=Sanitizer.AddressSanitizer,
            skip_setup=True
        )
        print("✓ PatchTask实例创建成功")
        
        # 创建ContextManager实例
        context_manager = ContextManager(patch_task)
        print("✓ ContextManager实例创建成功")
        
        # 创建MonkeyOpenAIAgent实例
        agent = MonkeyOpenAIAgent(context_manager)
        print("✓ MonkeyOpenAIAgent实例创建成功")
        
        # 测试调用
        print("  测试agent调用...")
        response = agent.invoke("Hello, this is a test.")
        print(f"  ✓ agent调用成功，响应: {response}")
        return True
        
    except Exception as e:
        print(f"✗ MonkeyOpenAIAgent测试失败: {e}")
        return False

def main():
    """主函数"""
    # 测试直接API调用
    success1 = test_direct_qwen()
    
    # 测试MonkeyOpenAIAgent类
    success2 = test_monkey_agent()
    
    if success1 and success2:
        print("\n=== 测试完成 ===")
        print("Qwen API集成测试全部通过！")
        return True
    else:
        print("\n=== 测试失败 ===")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)