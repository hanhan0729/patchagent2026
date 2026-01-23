#!/usr/bin/env python3
"""
直接测试Qwen API的脚本
"""

import os
import sys
from dotenv import load_dotenv
import requests
import json

# 加载环境变量
load_dotenv(os.path.join(os.path.dirname(__file__), "patchagent", ".env.nvwa"))

def test_qwen_api_direct():
    """直接测试Qwen API"""
    print("=== 直接测试Qwen API ===")
    
    # 获取环境变量
    api_key = os.getenv('QWEN_API_KEY')
    api_base = os.getenv('QWEN_API_BASE')
    
    if not api_key or not api_base:
        print("✗ 缺少必要的环境变量")
        print("请确保设置了QWEN_API_KEY和QWEN_API_BASE")
        return False
    
    print(f"✓ API密钥已配置: {api_key[:10]}...")
    print(f"✓ API基础URL: {api_base}")
    
    # 测试API端点
    url = f"{api_base}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # 测试数据
    data = {
        "model": "qwen-turbo",
        "messages": [
            {"role": "user", "content": "你好，这是一个测试。你叫什么名字"}
        ],
        "max_tokens": 50
    }
    
    try:
        print("\n发送请求到Qwen API...")
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("✓ Qwen API响应成功！")
            print(f"响应内容: {result['choices'][0]['message']['content'][:100]}...")
            return True
        else:
            print(f"✗ API请求失败，状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ 请求异常: {e}")
        return False
    except Exception as e:
        print(f"✗ 未知错误: {e}")
        return False

def main():
    """主函数"""
    if test_qwen_api_direct():
        print("\n=== 测试成功 ===")
        print("Qwen API可以直接访问！")
    else:
        print("\n=== 测试失败 ===")
        print("Qwen API访问存在问题")
        sys.exit(1)

if __name__ == "__main__":
    main()