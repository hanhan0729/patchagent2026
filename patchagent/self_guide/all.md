# PatchAgent 项目架构详解

## 项目概述

PatchAgent是一个自动化漏洞修复系统，它使用大型语言模型(LLM)来分析代码中的安全漏洞并生成修复补丁。该项目已经从GPT API迁移到Qwen API，通过兼容OpenAI的接口实现。系统采用Docker容器化部署，包含PostgreSQL数据库、LiteLLM代理服务和PatchAgent核心服务。

## 整体架构

项目采用模块化设计，主要包含以下组件：

1. **数据库层**: PostgreSQL存储LiteLLM的日志和配置
2. **API代理层**: LiteLLM提供统一的LLM API接口
3. **核心引擎**: PatchAgent执行漏洞分析和修复
4. **任务管理**: SkySet任务系统管理漏洞修复任务
5. **代理系统**: MonkeyOpenAIAgent智能代理执行修复策略
6. **工具链**: 代码查看、定位和验证工具

## Docker容器架构

### PostgreSQL容器
- **镜像**: postgres:latest
- **端口**: 5432:5432
- **数据库**: litellm
- **用户**: root/root
- **作用**: 存储LiteLLM的日志、模型配置和请求记录

### LiteLLM容器
- **镜像**: ghcr.io/berriai/litellm-database:main-v1.35.10
- **端口**: 4000:4000
- **配置**: 通过litellm.yml配置文件
- **依赖**: 依赖于PostgreSQL容器
- **作用**: 提供统一的LLM API接口，支持多种模型提供商

### PatchAgent容器（隐式）
- **基础**: 基于Python环境
- **入口**: nwtool脚本
- **依赖**: 需要访问LiteLLM API和项目源代码
- **作用**: 执行漏洞分析、修复生成和验证

## 代码修改位置说明

当前修改的代码位于 `/root/workspace/patchagent/` 目录中，这是PatchAgent项目的源代码目录，**不是在Docker容器内**。具体说明如下：

### 1. 当前工作环境
- **物理位置**: `/root/workspace/patchagent/`
- **访问方式**: 通过主机文件系统直接访问
- **修改方式**: 直接在主机上编辑源代码文件

### 2. 与Docker容器的关系
- **PostgreSQL容器**: 独立运行，提供数据库服务
- **LiteLLM容器**: 独立运行，提供LLM API代理服务
- **PatchAgent代码**: 在主机上运行，通过API调用访问容器服务

### 3. 运行时架构
```
主机环境 (/root/workspace/patchagent/)
├── PatchAgent源代码 (正在修改)
├── nwtool (主执行脚本)
├── .env.nvwa (环境配置)
├── litellm.yml (模型配置)
└── Docker容器
    ├── PostgreSQL容器 (postgres:latest)
    └── LiteLLM容器 (ghcr.io/berriai/litellm-database:main-v1.35.10)
```

### 4. 代码修改的影响
- **即时生效**: 修改后的代码可以直接在主机上运行
- **无需重启容器**: PostgreSQL和LiteLLM容器保持独立运行
- **API调用**: PatchAgent通过HTTP API与LiteLLM容器通信

### 5. 部署流程
1. **修改代码**: 在 `/root/workspace/patchagent/` 目录中直接编辑
2. **运行PatchAgent**: 执行 `./nwtool` 脚本
3. **API通信**: PatchAgent通过 `http://localhost:4000` 访问LiteLLM服务
4. **数据库连接**: LiteLLM通过 `postgres:5432` 访问PostgreSQL服务

## 详细组件实现

### 1. LiteLLM配置与模型支持

LiteLLm.yml配置了多种模型：

```yaml
model_list:
  - model_name: gpt-3.5
    litellm_params:
      model: openai/gpt-3.5-turbo
      api_key: "os.environ/OPENAI_API_KEY"
  - model_name: qwen-turbo
    litellm_params:
      model: dashscope/qwen-turbo
      api_key: "os.environ/QWEN_API_KEY"
      api_base: "os.environ/QWEN_API_BASE"
  # ... 其他模型配置
```

支持的模型包括：
- OpenAI系列: GPT-3.5, GPT-4, GPT-4o等
- Anthropic系列: Claude-3-haiku, Claude-3-sonnet, Claude-3-opus
- 阿里云Qwen系列: qwen-turbo, qwen-plus, qwen-max
- Vertex AI GLM系列: vertex-glm-4.7

### 2. 环境配置

.env.nvwa文件包含所有必要的API密钥和配置：

```bash
# Qwen API Configuration
QWEN_API_KEY=sk-...
QWEN_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1

# Vertex AI GLM-4.7 Configuration
VERTEX_API_KEY=...
VERTEX_API_BASE=https://open.bigmodel.cn/api/paas/v4

# OpenAI API Configuration
OPENAI_API_KEY=sk-...

# LiteLLM Configuration
LITELLM_CONFIG_PATH=./litellm.yml

# NVWA Configuration
NVWA_LOG_LEVEL=INFO
NVWA_MAX_ITERATIONS=5
NVWA_TIMEOUT=500
```

### 3. 任务启动流程

通过主工具 nwtool 启动：

```bash
# 基本用法
./nwtool --project hunspell --tag 74b08bf-heap_buffer_overflow_a --model qwen-turbo

# 批量处理模式
./nwtool --log_path ./archives/gpt-4 --model gpt-4

# Tmux多会话模式
./nwtool --tmux --max_sessions 5 --project mruby --tag 55b5261-null_pointer_deref
```

### 4. 核心执行引擎

#### 4.1 MonkeyOpenAIAgent架构

MonkeyOpenAIAgent是核心执行引擎，负责与LLM交互：

```python
class MonkeyOpenAIAgent(BaseAgent):
    def __init__(
        self,
        context_manager: ContextManager,
        model: str = "qwen-turbo",
        temperature: float = 1,
        auto_hint: bool = False,
        counterexample_num: int = 3,
        locate_tool: bool = True,
        max_iterations: int = 30,
    ):
        # 初始化LLM客户端
        self.qwen_api_key = os.getenv("QWEN_API_KEY")
        self.qwen_api_base = os.getenv("QWEN_API_BASE")
        
        self.llm = ChatOpenAI(
            temperature=self.temperature,
            model=self.model,
            api_key=self.qwen_api_key,
            base_url=self.qwen_api_base
        )
```

#### 4.2 工具链系统

工具链包含三个核心工具：

1. **viewcode工具**: 查看代码片段
2. **locate工具**: 定位符号定义
3. **validate工具**: 验证修复补丁

```python
lc_tools = [
    create_viewcode_tool(context, auto_hint=self.auto_hint),
    create_validate_tool(context, auto_hint=self.auto_hint),
    create_locate_tool(context, auto_hint=self.auto_hint)
]
```

### 5. 修复策略实现

#### 5.1 多温度采样策略

```python
# 使用不同温度参数生成多样化修复
temperatures = [0.0, 0.3, 0.7, 1.0]
for temperature in temperatures:
    agent = MonkeyOpenAIAgent(
        context_manager=context_manager,
        model=model,
        temperature=temperature,
        auto_hint=True
    )
```

#### 5.2 错误案例学习机制

系统会记录之前的错误修复尝试，避免重复相同的错误：

```python
def get_previous_error_cases(self):
    error_cases = []
    for context in self.context_manager.contexts:
        for tool_call in context.tool_calls:
            if tool_call["name"] == "validate":
                error_cases.append(f"Error case: \n{tool_call['args']['patch']}")
    
    # 随机采样部分错误案例
    error_cases = random.sample(error_cases, min(self.counterexample_num, len(error_cases)))
    return "\n".join(error_cases)
```

### 6. 代码分析工具

#### 6.1 LSP集成

系统集成了LSP（Language Server Protocol）来提供代码智能：

- **clangd**: C/C++代码分析和导航
- **ctags**: 符号定义和引用查找
- **悬停信息**: 提供符号定义和文档

#### 6.2 代码查看工具

```python
def viewcode(context: Context, path: str, start_line: int, end_line: int, auto_hint=False):
    # 获取代码片段
    lines = lsp.viewcode(context.task, path, start_line, end_line)
    
    # 添加行号
    code = "".join(f"{start_line + i}| {line}" for i, line in enumerate(lines))
    
    # 可选：添加悬停提示
    if auto_hint:
        hints = lsp.hover(context.task, path, line, column)
    
    return code
```

#### 6.3 符号定位工具

```python
def locate(context: Context, symbol: str, auto_hint=False):
    # 快速路径：直接符号查找
    fast_path_locations = lsp.locate_symbol(context.task, symbol)
    
    # 备选路径：基于栈跟踪的符号查找
    for stack in context.task.sanitizer_report.get_all_stacktrace():
        # 在栈跟踪中查找符号
        if symbol == extract_cpp_function_name(frame[0]):
            # 查找定义位置
            location = lsp.find_definition(context.task, path, line, column)
    
    return locations
```

### 7. 补丁验证系统

#### 7.1 补丁格式规范（Git Diff格式详解）

系统要求补丁遵循标准的git diff格式，这是版本控制系统中用于表示代码变更的标准格式。具体格式要求如下：

**基本结构**：
```diff
--- a/原始文件路径
+++ b/修改后文件路径
@@ -起始行号,删除行数 +起始行号,添加行数 @@
 上下文行
-删除的行
+添加的行
 上下文行
```

**格式规则详解**：

1. **文件头信息**：
   - `--- a/文件名`：表示修改前的文件（a代表ancestor）
   - `+++ b/文件名`：表示修改后的文件（b代表new）

2. **块头信息**（Hunk Header）：
   - `@@ -起始行号,删除行数 +起始行号,添加行数 @@`
   - 减号部分表示原始文件的信息
   - 加号部分表示修改后文件的信息
   - 例如：`@@ -869,7 +869,7 @@` 表示从第869行开始，原始文件有7行，修改后也有7行

3. **行类型标识**：
   - 空格开头的行：上下文行，保持不变
   - 减号开头的行：被删除的行
   - 加号开头的行：新增的行
   - 每行的开头标识符（+、-、空格）必须位于行首

4. **上下文要求**：
   - 每个变更块前后必须至少有3行上下文
   - 上下文帮助定位变更位置，确保补丁应用到正确位置

**实际示例**：
```diff
--- a/src/OT/Layout/GDEF/GDEF.hh
+++ b/src/OT/Layout/GDEF/GDEF.hh
@@ -869,7 +869,7 @@ struct GDEF
         return v;

     v = table->get_glyph_props (glyph);
-      if (likely (table)) // Don't try setting if we are the null instance!
+      if (likely (table.get_blob ())) // Don't try setting if we are the null instance!
     glyph_props_cache.set (glyph, v);

     return v;
```

**验证工具如何处理**：
1. 解析diff格式，提取文件路径和变更内容
2. 根据行号信息定位到源代码的相应位置
3. 应用补丁到临时文件
4. 编译并运行测试验证修复效果
5. 返回验证结果（成功/失败）和详细报告

#### 7.2 验证流程

```python
def validate(context: Context, patch: str, auto_hint=False):
    # 修订补丁格式
    patch, fixed = revise_patch(patch, context.task.immutable_project_path)
    
    # 临时保存补丁
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write(patch)
    
    # 执行验证
    ret, report = context.task.validate(f.name)
    
    # 返回结果
    if ret:
        return "Congratulations! The patch is correct!"
    else:
        return f"Sorry, the patch is incorrect.\nValidation report:\n{report}"
```

### 8. 上下文管理系统

#### 8.1 ContextManager

ContextManager负责管理任务执行的历史记录：

```python
class ContextManager:
    def __init__(self, task, load_context=True, path=None):
        self.task = task
        self.contexts = []
        self.path = path
        
        if load_context and path:
            self.load_context()
    
    def new_context(self):
        context = Context(self.task)
        self.contexts.append(context)
        return context
    
    def save_context(self):
        # 保存上下文到文件
        pass
```

#### 8.2 上下文持久化

系统会将每次修复尝试的上下文保存到文件，以便后续分析：

```python
# 保存LLM响应和工具调用
context.add_llm_response(response)
context.add_tool_call(tool_name, args, result)

# 保存到文件
context_manager.save_context()
```

### 9. 任务管理系统

#### 9.1 PatchTask定义

```python
class PatchTask:
    def __init__(self, project, tag):
        self.project = project
        self.tag = tag
        self.sanitizer_report = None
        self.immutable_project_path = None
    
    def setup(self):
        # 设置构建环境
        # 解析sanitizer报告
        # 准备项目源码
        pass
    
    def validate(self, patch_file):
        # 应用补丁
        # 编译项目
        # 运行测试
        # 返回验证结果
        pass
```

#### 9.2 SkySet集成

系统集成了SkySet数据集来管理漏洞修复任务：

```python
def get_all_task(project=None, tag=None, skip_linux=False, skip_extractfix=False):
    # 从SkySet获取任务列表
    tasks = []
    # 过滤条件
    return tasks

def make_task(project, tag):
    # 创建PatchTask实例
    return PatchTask(project, tag)
```

### 10. 执行流程详解（含代码文件映射）

#### 10.1 初始化阶段

**涉及文件**：
- `nwtool`：主入口脚本
- `nvwa/sky/task.py`：PatchTask类定义
- `nvwa/sky/utils.py`：任务工具函数
- `nvwa/context.py`：ContextManager类

**执行流程**：
1. **命令行解析**（nwtool）：
   ```python
   # 解析命令行参数
   parser = argparse.ArgumentParser(description="Nvwa Patch Tool")
   parser.add_argument("--project", type=str, help="project name")
   parser.add_argument("--tag", type=str, help="tag name")
   parser.add_argument("--model", type=str, default="gpt-4", help="model name")
   ```

2. **任务创建**（nvwa/sky/utils.py）：
   ```python
   # 从SkySet获取任务
   all_task = get_all_task(project=args.project, tag=args.tag, ...)
   ```

3. **PatchTask初始化**（nvwa/sky/task.py）：
   ```python
   # 创建PatchTask实例
   task = PatchTask(project, tag)
   
   # setup()方法执行以下操作：
   # - 检查任务目录是否存在
   # - 检查构建脚本是否存在
   # - 检查测试脚本是否存在
   # - 检查POC文件是否存在
   # - 如果缺少报告文件，则执行构建和测试
   # - 解析sanitizer报告
   ```

4. **上下文管理器初始化**（nvwa/context.py）：
   ```python
   # 创建ContextManager
   cm = ContextManager(task, load_context=True, path=args.log_path)
   ```

#### 10.2 分析阶段

**涉及文件**：
- `nvwa/parser/`：报告解析模块
- `nvwa/agent/monkey/openai.py`：MonkeyOpenAIAgent
- `nvwa/proxy/`：工具创建模块

**执行流程**：
1. **报告解析**（nvwa/parser/）：
   ```python
   # 解析sanitizer报告
   self.sanitizer_report = parse(self.report, self.sanitizer)
   # 提取栈跟踪、错误类型、内存地址等关键信息
   ```

2. **代理初始化**（nvwa/agent/monkey/openai.py）：
   ```python
   # 创建MonkeyOpenAIAgent
   agent = MonkeyOpenAIAgent(context_manager, model=model, ...)
   # 设置LLM客户端（OpenAI兼容接口）
   # 配置工具链（viewcode、locate、validate）
   ```

3. **工具链创建**（nvwa/proxy/default.py）：
   ```python
   # 创建工具实例
   lc_tools = [
       create_viewcode_tool(context, auto_hint=self.auto_hint),
       create_validate_tool(context, auto_hint=self.auto_hint),
       create_locate_tool(context, auto_hint=self.auto_hint)
   ]
   ```

#### 10.3 修复阶段

**涉及文件**：
- `nvwa/agent/monkey/openai.py`：核心代理逻辑
- `nvwa/policy/default.py`：修复策略
- `nvwa/proxy/internal.py`：工具实现

**执行流程**：
1. **策略应用**（nvwa/policy/default.py）：
   ```python
   # DefaultPolicy._agent_generator()生成多个代理实例
   # 使用不同的温度参数和配置组合
   for i in range(self.MONKEYOPENAI_ITERATION_NUM):
       yield MonkeyOpenAIAgent(..., temperature=i * (1 / (self.MONKEYOPENAI_ITERATION_NUM - 1)), ...)
   ```

2. **LLM交互**（nvwa/agent/monkey/openai.py）：
   ```python
   # 构建提示词
   self.prompt = ChatPromptTemplate.from_messages([
       ("system", MONKEY_SYSTEM_PROMPT_TEMPLATE),
       ("user", MONKEY_USER_PROMPT_TEMPLATE),
       MessagesPlaceholder(variable_name="agent_scratchpad"),
   ])
   
   # 执行AgentExecutor
   self.agent_executor.invoke({})
   ```

3. **工具调用**（nvwa/proxy/internal.py）：
   ```python
   # viewcode工具：查看代码片段
   def viewcode(context: Context, path: str, start_line: int, end_line: int, auto_hint=False):
       lines = lsp.viewcode(context.task, path, start_line, end_line)
       return formatted_code
   
   # locate工具：定位符号
   def locate(context: Context, symbol: str, auto_hint=False):
       locations = lsp.locate_symbol(context.task, symbol)
       return locations
   
   # validate工具：验证补丁
   def validate(context: Context, patch: str, auto_hint=False):
       ret, report = context.task.validate(patch_file)
       return result_message
   ```

4. **错误案例学习**：
   ```python
   # 从历史上下文中提取错误案例
   def get_previous_error_cases(self):
       error_cases = []
       for context in self.context_manager.contexts:
           for tool_call in context.tool_calls:
               if tool_call["name"] == "validate":
                   error_cases.append(f"Error case: \n{tool_call['args']['patch']}")
       return "\n".join(error_cases)
   ```

#### 10.4 验证阶段

**涉及文件**：
- `nvwa/sky/task.py`：PatchTask验证方法
- `skyset_tools`：SkySet工具集
- `nvwa/parser/`：报告解析

**执行流程**：
1. **补丁应用**（nvwa/sky/task.py）：
   ```python
   # PatchTask.validate()方法
   def validate(self, patch_path: str) -> tuple[bool, str]:
       # 1. 使用补丁重新构建项目
       ret, report = self.build(patch_path=patch_path)
       if not ret:
           return False, report
       
       # 2. 运行测试
       ret, report = self.test(patch=True)
       
       # 3. 解析新的sanitizer报告
       sanitizer_report = parse(report, self.sanitizer)
       if sanitizer_report is None:
           # 没有检测到sanitizer错误，检查功能测试
           if self.test_functional(patch_path=patch_path)["result"] != "passed":
               return False, "Functional test failed"
           return True, ""
       
       # 4. 仍然有sanitizer错误，返回失败
       return False, sanitizer_report.summary
   ```

2. **构建和测试**（通过skyset_tools）：
   ```python
   # 调用SkySet工具集
   # build(): 使用AddressSanitizer编译项目
   # test(): 运行POC触发漏洞
   # test_functional(): 运行功能测试确保修复不破坏正常功能
   ```

3. **结果评估**：
   ```python
   # 在DefaultPolicy.apply()中评估结果
   # 如果验证成功，设置task.patch
   # 如果验证失败，继续下一个代理实例
   ```

### 11. 错误处理与恢复

#### 11.1 API错误处理

```python
try:
    self._apply()
except openai.APIError as e:
    log.error(f"OpenAI API error: {e}")
except httpx.RemoteProtocolError as e:
    log.error(f"HTTPX error: {e}")
except Exception as e:
    log.error(f"Unknown Error: {e}")
```

#### 11.2 补丁修订机制

```python
def revise_patch(patch: str, project_path: str):
    # 自动修正补丁中的行号偏移
    # 确保补丁能够正确应用到目标文件
    return revised_patch, is_fixed
```

### 12. 部署与运行

#### 12.1 Docker部署 vs 直接运行的实现区别

**Docker部署实现特点**：

1. **服务隔离**：
   - PostgreSQL、LiteLLM和PatchAgent分别运行在独立的容器中
   - 通过Docker网络进行通信
   - 服务间依赖通过`depends_on`配置管理

2. **环境一致性**：
   - 所有依赖项都打包在容器中
   - 避免"在我机器上能运行"的问题
   - 确保开发、测试、生产环境一致性

3. **持久化存储**：
   - PostgreSQL数据通过Docker卷持久化
   - LiteLLM日志和配置存储在容器内
   - 需要显式配置卷映射以持久化数据

4. **网络配置**：
   - 容器间通过Docker网络通信
   - LiteLLM服务通过`http://litellm:4000`访问
   - PostgreSQL通过`postgres:5432`访问

5. **资源限制**：
   - 可以为每个容器设置CPU和内存限制
   - 便于资源管理和监控

**直接运行实现特点**：

1. **本地依赖**：
   - 需要本地安装PostgreSQL
   - 需要本地Python环境和依赖包
   - 需要手动配置环境变量

2. **服务集成**：
   - 所有服务在同一主机上运行
   - 通过localhost或127.0.0.1进行通信
   - 服务启动顺序需要手动管理

3. **配置灵活性**：
   - 更容易修改配置文件进行调试
   - 可以直接访问日志文件和调试信息
   - 便于开发和测试阶段的快速迭代

4. **资源使用**：
   - 共享主机资源，无隔离
   - 可能受到主机上其他进程影响
   - 资源使用更灵活但难以精确控制

#### 12.2 Docker部署

```bash
# 启动PostgreSQL数据库
docker compose up -d --build postgres

# 启动LiteLLM服务
docker compose up -d --build litellm

# 运行PatchAgent（在主机上）
./nwtool --project hunspell --tag 74b08bf-heap_buffer_overflow_a --model qwen-turbo
```

**Docker部署的配置要点**：
- LiteLLM容器需要挂载litellm.yml配置文件
- PostgreSQL容器需要配置数据库连接
- PatchAgent需要配置指向Docker容器的API端点

#### 12.3 直接运行

```bash
# 设置环境变量
export OPENAI_API_KEY=your_api_key
export QWEN_API_KEY=your_qwen_key

# 启动本地PostgreSQL（如果未运行）
pg_ctl start

# 启动本地LiteLLM服务
litellm --config ./litellm.yml --port 4000

# 运行修复任务
./nwtool --project mruby --tag 55b5261-null_pointer_deref --model qwen-turbo
```

**直接运行的配置要点**：
- 需要手动启动PostgreSQL服务
- 需要手动启动LiteLLM服务
- API端点配置为localhost:4000
- 环境变量直接在主机上设置

### 13. 监控与日志

#### 13.1 日志系统

```python
from nvwa.logger import log

# 不同级别的日志
log.info("Information message")
log.error("Error message")
log.purple("Important message")
```

#### 13.2 执行跟踪

系统会记录每次修复尝试的详细过程，包括：
- LLM交互记录
- 工具调用历史
- 补丁生成过程
- 验证结果

### 14. 扩展与定制

#### 14.1 添加新模型

在litellm.yml中添加新模型配置：

```yaml
- model_name: new-model
  litellm_params:
    model: provider/model-name
    api_key: "os.environ/API_KEY"
```

#### 14.2 自定义修复策略

创建新的Policy类：

```python
class CustomPolicy(BasePolicy):
    def apply(self, context_manager):
        # 自定义修复逻辑
        pass
```

#### 14.3 添加新工具

创建新的工具函数并集成到代理中：

```python
def create_custom_tool(context):
    def custom_function(param):
        # 工具实现
        pass
    return StructuredTool.from_function(custom_function)
```

## 总结

PatchAgent是一个完整的自动化漏洞修复系统，通过Docker容器化部署，集成了PostgreSQL数据库、LiteLLM代理和核心修复引擎。系统采用模块化设计，支持多种LLM模型，具备强大的代码分析能力和智能修复策略。通过详细的执行流程和完善的错误处理机制，能够有效地自动化漏洞修复过程。

当前修改的代码位于主机文件系统的 `/root/workspace/patchagent/` 目录中，**不是在Docker容器内**。PatchAgent源代码在主机上运行，通过API调用与独立的PostgreSQL和LiteLLM容器进行通信。这种架构提供了灵活性，允许直接修改和测试代码，同时利用容器化服务提供稳定的数据库和LLM代理功能。

Docker部署提供了更好的服务隔离和环境一致性，适合生产环境；而直接运行提供了更高的灵活性和调试便利性，适合开发和测试阶段。两种部署方式在API端点配置、服务管理和资源控制方面存在显著差异，但核心修复逻辑保持一致。

补丁格式遵循标准的git diff格式，这是版本控制系统中用于表示代码变更的标准格式，确保了补丁的标准化和可验证性。