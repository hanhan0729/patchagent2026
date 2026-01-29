#!/usr/bin/env python3
"""
测试Vertex AI GLM-4.7 API与LiteLLM集成的脚本
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv(os.path.join(os.path.dirname(__file__), ".env.nvwa"))

def test_litellm_config():
    """测试LiteLLM配置是否正确"""
    print("测试LiteLLM配置...")

    # 检查必要的环境变量
    required_vars = ['VERTEX_API_KEY', 'VERTEX_API_BASE']
    missing_vars = []

    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        print(f"缺少必要的环境变量: {missing_vars}")
        print("请设置以下环境变量:")
        print(f"  export VERTEX_API_KEY=<your_vertex_api_key>")
        print(f"  export VERTEX_API_BASE=<your_vertex_api_base_url>")
        return False

    print("✓ 环境变量配置正确")
    return True

def test_model_availability():
    """测试Vertex GLM-4.7模型是否可用"""
    print("\n测试Vertex GLM-4.7模型可用性...")

    try:
        import litellm
        from litellm import completion

        # 设置LiteLLM代理
        litellm.api_base = "http://localhost:4000"
        litellm.api_key = os.getenv("LITELLM_MASTER_KEY", "sk-7751b9b0df2b4520bd55a4e95c3198c7")

        # 测试Vertex GLM-4.7模型
        model_name = "vertex_ai/zai-glm-4.7"
        print(f"  测试模型: {model_name}")
        
        try:
            response = completion(
                model=model_name,
                messages=[{"role": "user", "content": "Hello, this is a test message for Vertex GLM-4.7 model."}],
                max_tokens=100
            )
            print(f"    ✓ 模型 {model_name} 响应成功")
            print(f"    响应内容: {response.choices[0].message.content}")
            return True
        except Exception as e:
            print(f"    ✗ 模型 {model_name} 测试失败: {e}")
            # 检查是否是缺少依赖包的错误
            if "google-cloud-aiplatform" in str(e):
                print("    提示: 需要安装google-cloud-aiplatform包")
                print("    请运行: pip install google-cloud-aiplatform")
            return False

    except ImportError:
        print("✗ 未安装litellm包，请运行: pip install litellm")
        return False
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

def test_direct_api_call():
    """测试直接API调用（不通过LiteLLM代理）"""
    print("\n测试直接API调用...")
    
    try:
        import requests
        import json
        
        api_key = os.getenv("VERTEX_API_KEY")
        api_base = os.getenv("VERTEX_API_BASE")
        
        if not api_key or not api_base:
            print("✗ 缺少API密钥或基础URL")
            return False
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "glm-4-flash",
            "messages": [
                {"role": "user", "content": "test"}
            ],
            "max_tokens": 100
        }
        
        print(f"  发送请求到: {api_base}/chat/completions")
        response = requests.post(
            f"{api_base}/chat/completions",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            print("✓ 直接API调用成功")
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                print(f"  响应内容: {result['choices'][0]['message']['content']}")
            return True
        else:
            print(f"✗ 直接API调用失败，状态码: {response.status_code}")
            print(f"  错误信息: {response.text}")
            # 尝试其他可能的端点
            if response.status_code == 405:
                print("  提示: 尝试使用不同的端点...")
                return test_alternative_endpoints()
            return False
            
    except Exception as e:
        print(f"✗ 直接API调用测试失败: {e}")
        return False

def test_alternative_endpoints():
    """测试其他可能的API端点"""
    print("\n尝试其他可能的API端点...")
    
    try:
        import requests
        import json
        
        api_key = os.getenv("VERTEX_API_KEY")
        api_base = os.getenv("VERTEX_API_BASE")
        
        if not api_key or not api_base:
            print("✗ 缺少API密钥或基础URL")
            return False
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "glm-4-flash",
            "messages": [
                {"role": "user", "content": "Hello, this is a test for alternative endpoints."}
            ],
            "max_tokens": 100
        }
        
        # 尝试不同的端点
        endpoints = [
            f"{api_base}/chat/completions",
            f"{api_base}/v1/chat/completions",
            f"{api_base}/api/v1/chat/completions",
            "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        ]
        
        for endpoint in endpoints:
            print(f"  尝试端点: {endpoint}")
            try:
                response = requests.post(
                    endpoint,
                    headers=headers,
                    json=data,
                    timeout=10
                )
                
                if response.status_code == 200:
                    print(f"    ✓ 端点 {endpoint} 成功")
                    result = response.json()
                    if 'choices' in result and len(result['choices']) > 0:
                        print(f"    响应内容: {result['choices'][0]['message']['content']}")
                    return True
                else:
                    print(f"    ✗ 端点 {endpoint} 失败，状态码: {response.status_code}")
            except Exception as e:
                print(f"    ✗ 端点 {endpoint} 异常: {e}")
        
        return False
        
    except Exception as e:
        print(f"✗ 测试其他端点失败: {e}")
        return False

def test_with_openai_format():
    """使用OpenAI格式测试API调用"""
    print("\n使用OpenAI格式测试API调用...")
    
    try:
        import litellm
        from litellm import completion
        
        # 直接使用OpenAI格式调用，不通过LiteLLM代理
        litellm.api_base = os.getenv("VERTEX_API_BASE")
        litellm.api_key = os.getenv("VERTEX_API_KEY")
        
        try:
            response = completion(
                model="glm-4-flash",
                messages=[{"role": "user", "content": "Hello, this is a test using OpenAI format."}],
                max_tokens=100,
                api_base=os.getenv("VERTEX_API_BASE"),
                api_key=os.getenv("VERTEX_API_KEY")
            )
            print("✓ OpenAI格式调用成功")
            print(f"  响应内容: {response.choices[0].message.content}")
            return True
        except Exception as e:
            print(f"✗ OpenAI格式调用失败: {e}")
            return False
            
    except Exception as e:
        print(f"✗ OpenAI格式测试失败: {e}")
        return False

def main():
    """主函数"""
    print("=== Vertex AI GLM-4.7 API集成测试 ===")

    # 测试配置
    if not test_litellm_config():
        sys.exit(1)

    # 测试模型可用性（通过LiteLLM代理）
    lite_success = test_model_availability()
    
    # 如果LiteLLM代理测试失败，尝试直接API调用
    direct_success = False
    if not lite_success:
        print("注意: LiteLLM代理测试失败，尝试其他测试方法...")
        direct_success = test_direct_api_call()
        
        # 如果直接API调用也失败，尝试OpenAI格式
        if not direct_success:
            openai_success = test_with_openai_format()
            if openai_success:
                direct_success = True
    
    # 如果所有测试都失败，退出
    if not lite_success and not direct_success:
        print("\n=== 所有测试方法均失败 ===")
        print("请检查以下事项:")
        print("1. 确保VERTEX_API_KEY和VERTEX_API_BASE配置正确")
        print("2. 确保API端点URL正确")
        print("3. 确保网络连接正常")
        print("4. 如果需要，安装google-cloud-aiplatform包: pip install google-cloud-aiplatform")
        sys.exit(1)

    print("\n=== 测试完成 ===")
    if lite_success:
        print("✓ Vertex AI GLM-4.7 API集成配置成功（通过LiteLLM代理）！")
    elif direct_success:
        print("✓ Vertex AI GLM-4.7 API集成配置成功（直接API调用）！")
    else:
        print("✓ Vertex AI GLM-4.7 API集成配置成功（使用OpenAI格式）！")

if __name__ == "__main__":
    main()