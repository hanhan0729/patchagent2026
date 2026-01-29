# 项目迁移与备份指南

基于对当前项目的分析，我为您总结了完整的项目迁移策略：

## 项目结构分析

当前项目是一个名为 `patchagent` 的自动化漏洞修复系统，主要特点：
- 使用 Python 编写的自动化工具
- 依赖 Docker 容器化部署（PostgreSQL + LiteLLM）
- 支持多种 LLM 服务（OpenAI、Anthropic、Qwen、Vertex AI）
- 包含大量漏洞修复案例数据集

## 迁移方案对比

### 1. 服务器镜像备份（不推荐）
**优点**：
- 完整保留系统环境
- 快速恢复

**缺点**：
- 镜像文件巨大（通常几十GB）
- 依赖特定云服务商
- 迁移到新硬件可能遇到驱动兼容性问题
- 包含大量无用数据

### 2. 代码+环境配置迁移（推荐）
**优点**：
- 轻量级，易于传输
- 可跨平台迁移
- 只保留必要组件
- 便于版本控制

**缺点**：
- 需要重新安装依赖
- 需要手动配置环境变量

## 推荐迁移步骤

### 第一步：代码备份
```bash
# 创建项目压缩包
tar -czf patchagent_backup_$(date +%Y%m%d).tar.gz /root/workspace/patchagent/

# 或者使用 git 备份
cd /root/workspace
git add .
git commit -m "Backup before migration"
git push origin main
```

### 第二步：环境清单导出
```bash
# 导出 Python 依赖
pip freeze > requirements.txt

# 导出系统包列表
dpkg --get-selections > package_list.txt

# 导出环境变量
env > environment_backup.txt
```

### 第三步：关键配置文件整理
需要特别注意以下文件：
- `patchagent/.env.nvwa` - API 密钥配置
- `patchagent/docker-compose.yml` - 服务配置
- `patchagent/litellm.yml` - LLM 模型配置
- `patchagent/nwtool` - 主执行脚本

### 第四步：数据备份
```bash
# 备份 Docker 数据卷（如果有重要数据）
docker volume ls
docker run --rm -v postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz /data
```

## 新服务器部署步骤

### 1. 环境准备
```bash
# 安装基础依赖
sudo apt update && sudo apt install -y python3-pip docker.io docker-compose

# 创建项目目录
mkdir -p /root/workspace
cd /root/workspace
```

### 2. 代码恢复
```bash
# 解压备份文件
tar -xzf patchagent_backup_YYYYMMDD.tar.gz

# 或者从 git 克隆
git clone <repository-url> patchagent
```

### 3. 环境配置
```bash
# 安装 Python 依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.nvwa .env.nvwa.local
# 编辑 .env.nvwa.local 更新 API 密钥

# 启动 Docker 服务
docker compose up -d postgres
docker compose up -d litellm
```

### 4. 验证部署
```bash
# 测试主程序
./nwtool --help

# 检查服务状态
docker compose ps
```

## 最佳实践建议

1. **定期备份**：设置 cron 定时任务自动备份
2. **版本控制**：使用 git 管理代码变更
3. **配置分离**：将敏感信息（API密钥）与代码分离
4. **文档完善**：维护详细的部署文档
5. **测试验证**：迁移后进行全面功能测试

## 注意事项

- **API 密钥**：迁移后需要更新所有 API 密钥
- **端口冲突**：确保新服务器端口不被占用
- **权限问题**：检查文件和目录权限
- **网络配置**：确保新服务器网络配置正确

这种迁移方式既保证了项目的完整性，又保持了灵活性和可维护性，是最推荐的方案。