###!/usr/bin/env python3
"""
测试Qwen API与LiteLLM集成的脚本
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv(os.path.join(os.path.dirname(__file__), ".env.nvwa"))

# 测试LiteLLM配置
def test_litellm_config():
    """测试LiteLLM配置是否正确"""
    print("测试LiteLLM配置...")
    
    # 检查必要的环境变量
    required_vars = ['QWEN_API_KEY', 'QWEN_API_BASE']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"缺少必要的环境变量: {missing_vars}")
        print("请设置以下环境变量:")
        print(f"  export QWEN_API_KEY=<your_qwen_api_key>")
        print(f"  export QWEN_API_BASE=<your_qwen_api_base_url>")
        return False
    
    print("✓ 环境变量配置正确")
    return True

def test_model_availability():
    """测试Qwen模型是否可用"""
    print("\n测试Qwen模型可用性...")
    
    try:
        import litellm
        from litellm import completion
        
        # 设置LiteLLM代理
        litellm.api_base = "http://localhost:4000"
        litellm.api_key = os.getenv("LITELLM_MASTER_KEY", "sk-7751b9b0df2b4520bd55a4e95c3198c7")
        
        # 测试Qwen模型
        qwen_models = ["dashscope/qwen-turbo", "dashscope/qwen-plus", "dashscope/qwen-max"]
        
        for model in qwen_models:
            print(f"  测试模型: {model}")
            try:
                response = completion(
                    model=model,
                    messages=[{"role": "user", "content": "Hello, this is a test."}],
                    max_tokens=50
                )
                print(f"    ✓ 模型 {model} 响应成功")
            except Exception as e:
                print(f"    ✗ 模型 {model} 测试失败: {e}")
                
    except ImportError:
        print("✗ 未安装litellm包，请运行: pip install litellm")
        return False
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False
    
    return True

def main():
    """主函数"""
    print("=== Qwen API集成测试 ===")
    
    # 测试配置
    if not test_litellm_config():
        sys.exit(1)
    
    # 测试模型可用性
    if not test_model_availability():
        sys.exit(1)
    
    print("\n=== 测试完成 ===")
    print("Qwen API集成配置成功！")

if __name__ == "__main__":
    main()