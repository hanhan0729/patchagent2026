# Docker使用指南

本文档基于NVWA项目的Docker配置，详细介绍Docker的基本原理、使用方法以及项目中的具体应用。

## Docker简介

Docker是一个开源的容器化平台，它允许开发者将应用程序及其依赖打包到一个轻量级、可移植的容器中，然后在任何支持Docker的环境中运行。与虚拟机不同，Docker容器共享主机系统的内核，因此更加轻量和高效。

## Docker核心概念

### 1. 镜像（Image）
Docker镜像是一个只读的模板，包含了运行应用程序所需的所有内容（代码、运行时、库、环境变量和配置文件）。镜像是分层构建的，每一层代表Dockerfile中的一个指令。

### 2. 容器（Container）
容器是镜像的运行实例，是一个独立的、可执行的软件包。容器包含了应用程序及其所有依赖，确保应用在不同环境中都能一致地运行。

### 3. 仓库（Repository/Registry）
Docker仓库是存储和分发镜像的地方。Docker Hub是最常用的公共仓库，也可以搭建私有仓库。

### 4. Dockerfile
Dockerfile是一个文本文件，包含了一系列指令，用于构建Docker镜像。每条指令都会在镜像中创建一个新的层。

## NVWA项目中的Docker配置

### docker-compose.yml文件分析

```yaml
services:
  postgres:
    image: postgres:latest
    environment:
      POSTGRES_USER: root
      POSTGRES_PASSWORD: root
      POSTGRES_DB: litellm
    ports:
      - "5432:5432"
    restart: always
  litellm:
    image: ghcr.io/berriai/litellm-database:main-v1.35.10
    volumes:
      - .:/app
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - LITELLM_MASTER_KEY=${LITELLM_MASTER_KEY}
      - UI_USERNAME=${UI_USERNAME}
      - UI_PASSWORD=${UI_PASSWORD}
    ports:
      - "4000:4000"
    restart: always
    command: --config /app/litellm.yml --num_workers 8
    depends_on:
      - postgres
```

### 配置详解

1. **服务定义**：定义了两个服务 - PostgreSQL数据库和LiteLLM服务
2. **镜像使用**：
   - PostgreSQL使用官方最新镜像：`postgres:latest`
   - LiteLLM使用GitHub Container Registry中的特定版本镜像：`ghcr.io/berriai/litellm-database:main-v1.35.10`
3. **环境变量**：通过环境变量传递配置信息，提高安全性和灵活性
4. **端口映射**：将容器内部端口映射到主机端口，使服务可从外部访问
   - PostgreSQL：5432端口映射到主机的5432端口
   - LiteLLM：4000端口映射到主机的4000端口
5. **卷挂载**：将当前目录挂载到容器中，使配置文件可被容器访问
6. **依赖关系**：LiteLLM服务依赖于PostgreSQL服务，确保数据库先启动
7. **重启策略**：设置为always，确保服务异常退出后自动重启

### litellm.yml文件分析

```yaml
model_list:
  - model_name: gpt-3.5
    litellm_params:
      model: openai/gpt-3.5-turbo
      api_key: "os.environ/OPENAI_API_KEY"
  # ... 其他模型配置 ...

litellm_settings:
  drop_params: True

general_settings:
  master_key: "os.environ/LITELLM_MASTER_KEY"
  database_url: "postgresql://root:root@postgres:5432/litellm"
```

这个配置文件定义了LiteLLM服务可以访问的各种语言模型，包括OpenAI、Anthropic、Qwen等不同提供商的模型。注意数据库连接使用了服务名`postgres`作为主机名，这是Docker Compose的DNS解析功能。

## Docker网络

Docker提供了多种网络模式：
- **bridge**：默认网络模式，容器通过虚拟网桥连接
- **host**：容器共享主机的网络栈
- **none**：容器没有网络连接
- **container**：容器共享另一个容器的网络栈
- **自定义网络**：用户定义的网络，提供更好的隔离和DNS解析

在NVWA项目中，两个服务（postgres和litellm）会自动连接到同一个默认bridge网络，因此它们可以通过服务名相互访问（如litellm.yml中的`postgres:5432`）。

## Docker存储

Docker提供了多种存储选项：
- **卷（Volumes）**：由Docker管理的存储，数据持久化，适合生产环境
- **绑定挂载（Bind Mounts）**：将主机文件系统的目录挂载到容器中，适合开发环境
- **临时文件系统（tmpfs mounts）**：存储在内存中，适合敏感数据

NVWA项目中使用了绑定挂载（`.:/app`），将当前目录挂载到容器的/app目录，这样容器可以访问项目文件。

## Docker常用命令

```bash
# 镜像相关
docker pull <image>          # 拉取镜像
docker images                # 查看本地镜像
docker rmi <image>           # 删除镜像
docker build -t <name> .     # 构建镜像

# 容器相关
docker run <image>           # 运行容器
docker ps                    # 查看运行中的容器
docker ps -a                 # 查看所有容器
docker stop <container>      # 停止容器
docker start <container>     # 启动容器
docker rm <container>        # 删除容器
docker logs <container>      # 查看容器日志
docker exec -it <container> bash  # 进入容器

# Docker Compose相关
docker compose up -d         # 后台启动服务
docker compose down          # 停止并删除服务
docker compose logs          # 查看服务日志
docker compose ps            # 查看服务状态
```

## NVWA项目Docker使用步骤

根据README.md文件，NVWA项目的Docker使用步骤如下：

1. 设置环境变量：
```bash
export OPENAI_API_KEY=<your api key>
```

2. 启动PostgreSQL数据库：
```bash
docker compose up -d --build postgres
```

3. 启动LiteLLM服务：
```bash
docker compose up -d --build litellm
```

## Docker最佳实践

1. **使用多阶段构建**：减小镜像大小
2. **最小化镜像**：使用轻量级基础镜像（如Alpine）
3. **合理使用缓存**：优化Dockerfile指令顺序
4. **安全考虑**：不要在镜像中存储敏感信息
5. **资源限制**：为容器设置CPU和内存限制
6. **健康检查**：定义健康检查确保服务可用性
7. **日志管理**：合理配置日志驱动和轮转策略

## 故障排除

### 常见问题及解决方案

1. **容器无法启动**：
   - 检查日志：`docker compose logs <service>`
   - 检查端口冲突：`netstat -tlnp | grep <port>`

2. **数据库连接失败**：
   - 确保PostgreSQL服务已启动：`docker compose ps`
   - 检查网络连接：`docker network ls`

3. **环境变量未生效**：
   - 确保在启动服务前设置了环境变量
   - 检查.env文件是否存在且格式正确

4. **权限问题**：
   - 检查挂载目录的权限
   - 使用`docker exec -u root <container> <command>`以root身份执行命令

## 总结

通过Docker，NVWA项目实现了环境一致性、部署简化和资源隔离，大大提高了开发和运维效率。Docker Compose的使用使得多服务应用的部署变得简单可靠，只需几个命令即可启动完整的服务栈。