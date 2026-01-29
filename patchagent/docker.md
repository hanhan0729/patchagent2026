# Docker使用指南（简化版）

本文档帮助您理解NVWA项目中Docker的使用，用简单易懂的方式解释Docker的基本概念和实际操作。

## 什么是Docker？

想象Docker就像一个"软件盒子"，它把应用程序和所有需要的东西（代码、库、配置等）打包在一起。这样无论在谁电脑上运行，效果都一样，不会出现"在我电脑上是好的"这种问题。

## Docker核心概念（用简单的话解释）

### 1. 镜像（Image）
就像软件的"安装包"，包含了运行应用所需的一切。比如"PostgreSQL镜像"就是一个包含了PostgreSQL数据库的安装包。

### 2. 容器（Container）
就是运行中的"软件盒子"。你可以把它想象成一个轻量级的虚拟机，但启动更快、占用资源更少。

### 3. docker-compose.yml
这是一个"说明书"，告诉Docker如何同时运行多个服务。在NVWA项目中，我们需要同时运行数据库和LiteLLM服务。

## NVWA项目的Docker配置详解

让我们看看项目中的docker-compose.yml文件：

```yaml
services:
  postgres:  # 数据库服务
    image: postgres:latest  # 使用最新的PostgreSQL镜像
    environment:  # 设置数据库的用户名、密码和数据库名
      POSTGRES_USER: root
      POSTGRES_PASSWORD: root
      POSTGRES_DB: litellm
    ports:  # 把容器的5432端口映射到电脑的5432端口
      - "5432:5432"
    restart: always  # 如果服务挂了，自动重启

  litellm:  # LiteLLM服务
    image: ghcr.io/berriai/litellm-database:main-v1.35.10  # 使用特定版本的LiteLLM镜像
    volumes:  # 把当前文件夹挂载到容器里，方便访问配置文件
      - .:/app
    environment:  # 从环境变量读取API密钥等信息
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - LITELLM_MASTER_KEY=${LITELLM_MASTER_KEY}
      - UI_USERNAME=${UI_USERNAME}
      - UI_PASSWORD=${UI_PASSWORD}
    ports:  # 把容器的4000端口映射到电脑的4000端口
      - "4000:4000"
    restart: always  # 自动重启
    command: --config /app/litellm.yml --num_workers 8  # 启动命令
    depends_on:  # 等数据库启动后再启动这个服务
      - postgres
```

## 如何启动NVWA项目？

只需要两条命令：

```bash
# 第一步：启动数据库
docker compose up -d --build postgres

# 第二步：启动LiteLLM服务  
docker compose up -d --build litellm
```

然后你就可以通过 http://localhost:4000 访问LiteLLM的界面了。

## Docker常用命令（日常使用中会用到的）

```bash
# 查看正在运行的服务
docker compose ps

# 查看服务日志（如果出问题了，用这个看错误信息）
docker compose logs postgres  # 只看数据库日志
docker compose logs litellm   # 只看LiteLLM日志
docker compose logs           # 看所有服务的日志

# 停止所有服务
docker compose down

# 重启某个服务
docker compose restart postgres
```

## 环境变量设置

在启动服务前，需要设置一些环境变量：

```bash
# 设置你的API密钥
export OPENAI_API_KEY="你的OpenAI API密钥"
export ANTHROPIC_API_KEY="你的Anthropic API密钥"
export LITELLM_MASTER_KEY="设置一个管理密码"
export UI_USERNAME="设置登录用户名"
export UI_PASSWORD="设置登录密码"
```

## 实际使用场景示例

### 场景1：第一次启动项目
```bash
# 1. 设置环境变量
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export LITELLM_MASTER_KEY="mysecretkey"
export UI_USERNAME="admin"
export UI_PASSWORD="mypassword"

# 2. 启动服务
docker compose up -d --build postgres
docker compose up -d --build litellm

# 3. 检查是否正常运行
docker compose ps
```

### 场景2：查看日志排错
```bash
# 如果服务不正常，查看日志
docker compose logs

# 只看最近10行日志
docker compose logs --tail=10
```

### 场景3：重启服务
```bash
# 重启数据库
docker compose restart postgres

# 重启LiteLLM
docker compose restart litellm

# 或者直接停止再启动
docker compose down
docker compose up -d
```

## 常见问题解决

### 问题1：端口被占用
如果启动时报错说端口被占用，可以：
```bash
# 查看哪个程序占用了5432端口
lsof -i :5432

# 或者换一个端口，修改docker-compose.yml
# 把 "5432:5432" 改成 "5433:5432"
```

### 问题2：容器启动后立即退出
```bash
# 查看详细日志
docker compose logs <服务名>

# 进入容器内部查看
docker compose exec <服务名> bash
```

### 问题3：数据库连接失败
```bash
# 确保数据库服务已启动
docker compose ps

# 检查数据库日志
docker compose logs postgres
```

## 实用小技巧

1. **给容器起个容易记的名字**：
   ```bash
   docker compose --project-name mynvwa up -d
   ```

2. **只启动一个服务**：
   ```bash
   docker compose up -d postgres  # 只启动数据库
   ```

3. **查看服务资源使用情况**：
   ```bash
   docker stats
   ```

4. **清理不用的镜像和容器**：
   ```bash
   docker system prune -a  # 清理所有不用的镜像、容器等
   ```

## Docker vs 传统安装方式的对比

| 传统方式 | Docker方式 |
|---------|-----------|
| 需要手动安装PostgreSQL | 一行命令启动 |
| 需要配置环境 | 自动配置 |
| 可能版本冲突 | 隔离环境，不会冲突 |
| 卸载麻烦 | 一键删除 |
| 迁移困难 | 打包带走 |

## 总结

Docker让NVWA项目的部署变得简单：
1. 不需要手动安装和配置各种软件
2. 环境一致，不会出现"在我电脑上能跑"的问题
3. 一键启动和停止所有服务
4. 容易迁移和分享

只需要记住几个常用命令，就可以轻松管理整个项目环境。