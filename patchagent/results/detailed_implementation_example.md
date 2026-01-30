# NVWA 工具详细实现流程

本文档详细描述了 NVWA 工具的实现流程，包括报告读取与清理、LLM 交互控制、验证过程等关键环节。

## 1. 报告读取与清理流程

### 1.1 报告读取

NVWA 工具从 `skyset` 目录中读取 AddressSanitizer 报告，这些报告位于各项目的特定标签目录下：

```
skyset/
├── hunspell/
│   ├── 6291cac-heap_buffer_overflow_b/
│   │   ├── report.txt          # 原始 ASAN 报告
│   │   ├── immutable/          # 项目代码
│   │   └── exp.sh              # 复现脚本
```

报告读取过程由 [`PatchTask.__init__()`](patchagent/nvwa/sky/task.py:35) 方法触发，通过以下步骤：

1. 检查项目目录结构完整性
2. 如果不存在报告文件，则执行构建和测试流程生成报告
3. 使用 [`parse()`](patchagent/nvwa/parser/__init__.py) 函数解析报告内容

### 1.2 报告解析与清理

报告解析由 [`AddressSanitizerReport.parse()`](patchagent/nvwa/parser/address.py:85) 方法完成，主要步骤：

1. **错误类型识别**：通过正则表达式匹配识别错误类型（如 heap-buffer-overflow、use-after-free 等）
2. **堆栈跟踪提取**：解析 ASAN 报告的堆栈跟踪信息
3. **附加信息提取**：提取内存大小、偏移量等关键信息
4. **清理与标准化**：移除无关信息，生成结构化报告

```python
# 报告解析示例
def parse_header(lines: List[str], additional_info: Dict[str, Any]) -> CWE:
    line = lines.pop(0)
    if double_free_header.match(line):
        additional_info["name"] = "double-free"
        return CWE.USE_AFTER_FREE
    # ... 其他错误类型识别
```

### 1.3 报告摘要生成

清理后的报告通过 [`summary`](patchagent/nvwa/parser/address.py:200) 属性生成人类可读的摘要：

```python
@property
def summary(self) -> str:
    # 生成包含错误描述、堆栈跟踪和修复建议的摘要
    summary = f"The sanitizer detected a {error_type} error. It means that {self.ERROR_DESCRIPTIONS[error_type]}."
    # 添加堆栈信息、内存信息等
    return summary
```

## 2. LLM 交互控制机制

### 2.1 代理架构

NVWA 使用多代理架构，主要组件包括：

- **MonkeyOpenAIAgent**：主要的 LLM 交互代理
- **DefaultPolicy**：策略管理器，协调多个代理
- **工具系统**：viewcode、locate、validate 三个核心工具

### 2.2 代理初始化

[`MonkeyOpenAIAgent.__init__()`](patchagent/nvwa/agent/monkey/openai.py:20) 初始化过程：

```python
def __init__(self, context_manager: ContextManager, model: str = "qwen-turbo", ...):
    # 配置 LLM 连接（支持 OpenAI 和 Qwen API）
    self.qwen_api_key = os.getenv("QWEN_API_KEY")
    self.qwen_api_base = os.getenv("QWEN_API_BASE")
    
    # 初始化 LLM 客户端
    if self.qwen_api_key and self.qwen_api_base:
        self.llm = ChatOpenAI(model=self.model, api_key=self.qwen_api_key, base_url=self.qwen_api_base)
    else:
        self.llm = ChatOpenAI(model=self.model)
```

### 2.3 工具系统集成

代理通过 LangChain 工具系统提供三种核心功能：

#### 2.3.1 代码查看工具 (viewcode)

由 [`create_viewcode_tool()`](patchagent/nvwa/proxy/default.py:5) 创建：

```python
def create_viewcode_tool(context: Context, auto_hint: bool = False) -> StructuredTool:
    def viewcode(path: str, start_line: int, end_line: int) -> str:
        # 读取并格式化代码片段
        lines = lsp.viewcode(context.task, path, start_line, end_line)
        # 添加行号和上下文信息
        return formatted_code
    return StructuredTool.from_function(viewcode)
```

#### 2.3.2 符号定位工具 (locate)

由 [`create_locate_tool()`](patchagent/nvwa/proxy/default.py:20) 创建：

```python
def create_locate_tool(context: Context, auto_hint: bool = False) -> StructuredTool:
    def locate(symbol: str) -> str:
        # 使用 clang 索引查找符号定义
        locations = lsp.locate_symbol(context.task, symbol)
        return formatted_locations
    return StructuredTool.from_function(locate)
```

#### 2.3.3 补丁验证工具 (validate)

由 [`create_validate_tool()`](patchagent/nvwa/proxy/default.py:35) 创建：

```python
def create_validate_tool(context: Context, auto_hint: bool = False) -> StructuredTool:
    def validate(patch: str) -> str:
        # 应用补丁并运行测试
        ret, report = context.task.validate(patch_path)
        return validation_result
    return StructuredTool.from_function(validate)
```

### 2.4 提示工程

系统使用精心设计的提示模板：

- **系统提示**：[MONKEY_SYSTEM_PROMPT_TEMPLATE](patchagent/nvwa/agent/monkey/prompt.py)
- **用户提示**：[MONKEY_USER_PROMPT_TEMPLATE](patchagent/nvwa/agent/monkey/prompt.py)

提示包含：
- 任务描述和安全研究的重要性
- 工具使用说明
- 补丁格式规范
- 错误报告和堆栈跟踪

## 3. 验证过程

### 3.1 验证流程

验证过程由 [`validate()`](patchagent/nvwa/proxy/internal.py:135) 函数实现：

```python
def validate(context: Context, patch: str, auto_hint=False) -> tuple[dict, str]:
    # 1. 限制连续验证尝试次数
    num_tries = 0
    for tool_call in reversed(context.tool_calls):
        if tool_call["name"] != "validate":
            break
        num_tries += 1
    if num_tries >= MAX_VALIDATION_TRIES:
        return error_message
    
    # 2. 补丁格式修正
    patch, _ = revise_patch(patch, context.task.immutable_project_path)
    
    # 3. 临时文件创建
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write(patch)
    
    # 4. 构建和测试
    ret, report = context.task.validate(f.name)
    
    # 5. 结果分析
    header = "Congratulations! The patch is correct!" if ret else "Sorry, the patch is incorrect."
    return {"patch": patch}, result
```

### 3.2 构建与测试

[`PatchTask.validate()`](patchagent/nvwa/sky/task.py:95) 方法执行：

1. **构建阶段**：应用补丁并编译项目
2. **测试阶段**：运行复现脚本验证修复
3. **报告解析**：检查是否仍存在 ASAN 错误
4. **功能测试**：确保补丁不破坏正常功能

```python
def validate(self, patch_path: str) -> tuple[bool, str]:
    # 构建项目
    ret, report = self.build(patch_path=patch_path)
    if not ret:
        return False, report
    
    # 运行测试
    ret, report = self.test(patch=True)
    
    # 解析新的 ASAN 报告
    sanitizer_report = parse(report, self.sanitizer)
    if sanitizer_report is None:
        # 无 ASAN 错误，检查功能测试
        if self.test_functional(patch_path=patch_path)["result"] != "passed":
            return False, "Functional test failed"
        return True, ""
    
    return False, sanitizer_report.summary
```

### 3.3 错误处理与反馈

系统提供详细的错误反馈：

- **构建错误**：编译失败信息
- **测试错误**：运行时错误信息
- **ASAN 错误**：新的或残留的内存错误
- **功能错误**：功能测试失败信息

## 4. 工作流程总结

### 4.1 完整流程图

```
开始
  ↓
读取项目配置 (project, tag)
  ↓
检查报告文件存在？
  ├── 否 → 构建项目 → 运行测试 → 生成报告
  ↓
解析 ASAN 报告
  ↓
初始化 PatchTask
  ↓
创建策略 (DefaultPolicy)
  ↓
生成代理序列 (MonkeyOpenAIAgent)
  ↓
对于每个代理：
  ├── 设置上下文
  ├── 配置工具 (viewcode, locate, validate)
  ├── 运行 LLM 交互
  └── 记录结果
  ↓
验证补丁
  ├── 成功 → 保存补丁
  └── 失败 → 继续下一个代理
  ↓
结束
```

### 4.2 关键设计特点

1. **多代理策略**：通过多个不同参数的代理增加成功概率
2. **工具链集成**：结合代码查看、符号定位和验证工具
3. **渐进式修复**：利用历史错误案例避免重复错误
4. **自动验证**：集成构建和测试流程确保补丁质量
5. **多模型支持**：支持 OpenAI 和 Qwen 等多种 LLM

### 4.3 使用示例

```bash
# 基本使用
./nwtool --project hunspell --tag 6291cac-heap_buffer_overflow_b --model qwen-turbo

# 高级选项
./nwtool --project mruby --tag 55b5261-null_pointer_deref \
         --model gpt-4-turbo \
         --log_path ./results \
         --thershold 15 \
         --reset
```

## 5. 实际案例分析

以 hunspell 项目的 `6291cac-heap_buffer_overflow_b` 为例：

1. **错误识别**：heap-buffer-overflow，访问越界
2. **定位问题**：`affixmgr.cxx:1874` 的字符串访问
3. **分析原因**：缺少边界检查
4. **生成补丁**：添加 `i < word.length()` 检查
5. **验证成功**：补丁通过构建、测试和功能验证

这个案例展示了系统从错误报告到成功补丁的完整流程，证明了 NVWA 工具在自动化漏洞修复方面的有效性。