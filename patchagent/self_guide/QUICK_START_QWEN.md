# Qwen API快速开始指南

## 1分钟快速迁移

### 1. 获取API密钥
从阿里云DashScope控制台获取API密钥。

### 2. 配置环境变量
```bash
# 编辑.env.nvwa文件
echo "QWEN_API_KEY=your_real_api_key_here" >> .env.nvwa
echo "QWEN_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1" >> .env.nvwa
```

### 3. 测试配置
```bash
# 加载环境变量并运行测试
source .env.nvwa
python3 test_monkey_openai_agent.py
```

### 4. 开始使用
```bash
# 使用Qwen API运行漏洞修复
./nwtool --model qwen-turbo --task hunspell:74b08bf-heap_buffer_overflow_a
```

## 验证成功标志

✅ 环境变量已设置  
✅ API连接测试通过  
✅ 代理创建成功  
✅ 漏洞修复任务可正常运行  

## 故障排除

如果遇到401错误，说明API密钥无效，请检查：
1. API密钥是否正确
2. 账户是否有DashScope权限
3. 网络连接是否正常

## 更多详情
参考完整迁移指南：`../gpt_to_qwen_migration_guide.md`