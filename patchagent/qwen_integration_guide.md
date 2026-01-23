# Qwen API集成与实验复现指南

本指南将帮助您使用Qwen API在NVWA工具中复现实验。

## 1. 环境准备

### 1.1 获取Qwen API凭证

1. 访问阿里云DashScope控制台: https://dashscope.console.aliyun.com/
2. 创建API密钥
3. 记录您的API密钥和基础URL

### 1.2 配置环境变量

编辑`.env.nvwa`文件，添加您的Qwen API配置：

```bash
# Qwen API配置
QWEN_API_KEY=your_qwen_api_key_here
QWEN_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
```

或者通过命令行设置：

```bash
export QWEN_API_KEY=your_qwen_api_key_here
export QWEN_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
```

## 2. 启动服务

### 2.1 启动PostgreSQL和LiteLLM

```bash
# 启动PostgreSQL和LiteLLM服务
docker compose up -d
```

### 2.2 验证服务状态

```bash
# 检查服务是否正常运行
docker compose ps

# 测试LiteLLM API
curl http://localhost:4000/models
```

## 3. 使用Qwen API运行实验

### 3.1 基本用法

使用`nwtool`脚本运行实验，指定Qwen模型：

```bash
# 使用qwen-turbo模型
./nwtool --project mruby --tag 55b5261-null_pointer_deref --model qwen-turbo

# 使用qwen-plus模型
./nwtool --project mruby --tag 55b5261-null_pointer_deref --model qwen-plus

# 使用qwen-max模型
./nwtool --project mruby --tag 55b5261-null_pointer_deref --model qwen-max
```

### 3.2 支持的Qwen模型

- `qwen-turbo`: 速度快，成本低，适合快速实验
- `qwen-plus`: 性能平衡，适合大多数场景
- `qwen-max`: 性能最强，适合复杂漏洞修复

### 3.3 完整命令示例

```bash
# 设置环境变量
export QWEN_API_KEY=sk-your-api-key
export QWEN_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1

# 启动服务
docker compose up -d

# 运行漏洞修复实验
./nwtool --project mruby --tag 55b5261-null_pointer_deref --model qwen-turbo --temperature 0.7 --max-rounds 10
```

## 4. 高级配置

### 4.1 自定义温度参数

```bash
# 较低温度，更确定性输出
./nwtool --project mruby --tag 55b5261-null_pointer_deref --model qwen-turbo --temperature 0.3

# 较高温度，更多样化输出
./nwtool --project mruby --tag 55b5261-null_pointer_deref --model qwen-turbo --temperature 0.9
```

### 4.2 调整迭代轮次

```bash
# 增加迭代轮次
./nwtool --project mruby --tag 55b5261-null_pointer_deref --model qwen-turbo --max-rounds 15
```

## 5. 故障排除

### 5.1 常见问题

1. **API连接失败**
   - 检查`QWEN_API_KEY`是否正确设置
   - 确认`QWEN_API_BASE`URL是否正确
   - 检查网络连接

2. **LiteLLM服务未启动**
   - 运行`docker compose up -d`启动服务
   - 检查`docker compose ps`查看服务状态

3. **模型不可用**
   - 确认LiteLLM配置中的模型名称是否正确
   - 检查Qwen API权限是否包含相应模型

### 5.2 调试命令

```bash
# 测试LiteLLM连接
curl -H "Authorization: Bearer sk-1234" http://localhost:4000/models

# 测试Qwen API直接调用
curl -H "Authorization: Bearer $QWEN_API_KEY" \
     -H "Content-Type: application/json" \
     $QWEN_API_BASE/models
```

## 6. 性能优化建议

1. **选择合适的模型**
   - 快速测试：使用`qwen-turbo`
   - 生产环境：使用`qwen-plus`或`qwen-max`

2. **调整参数**
   - 温度：0.7-0.8平衡创造性和准确性
   - 最大轮次：10-15轮通常足够

3. **批量处理**
   - 对于多个漏洞，可以并行运行多个实例

## 7. 测试验证

运行集成测试脚本验证配置：

```bash
python3 test_qwen_integration.py
```

## 8. 实验结果

实验结果将保存在`results/`目录下，包括：
- 修复的代码文件
- 修复过程的日志
- 性能评估报告

查看结果：

```bash
ls -la results/
cat results/latest.log
```

## 9. 下一步

成功复现实验后，您可以：
1. 尝试不同的Qwen模型比较效果
2. 调整参数优化修复质量
3. 扩展到其他项目的漏洞修复
4. 分析修复结果并改进策略