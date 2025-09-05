# AgentScope 项目部署与使用说明

## 环境要求

- **操作系统**：推荐 Linux 或 macOS，Windows 用户建议使用 WSL
- **Python 版本**：3.12
- **Node.js**：用于前端 Studio（建议 v18 及以上）
- **Git**：用于拉取子模块

## 目录结构

- `agent/`：核心 Python 入口
- `workspace/`：工作区，包含源码、构建、虚拟环境等
- `setup.sh`：一键环境搭建脚本
- `chat.sh`：一键启动脚本

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/你的仓库/AgentScopeDeploy.git
cd AgentScopeDeploy
```

### 2. 运行环境搭建脚本

确保你已安装 Python 3.12，并在项目根目录下执行：

```bash
bash setup.sh
```

该脚本会自动完成以下操作：

- 检查 Python 版本
- 初始化并拉取 `agentscope`、`agentscope-runtime`、`agentscope-studio` 子模块
- 创建 Python 虚拟环境并激活
- 配置 pip 镜像源（清华镜像）
- 安装后端依赖（含 sandbox 依赖）
- 安装并启动前端 Studio（默认 http://localhost:3000）
- 修复依赖冲突（如 mcp 版本）

### 3. 配置环境变量

在 `workspace/` 目录下创建 `.env` 文件，填写必要的环境变量。例如：

```
OPENAI_API_KEY=你的key
...
```

### 4. 启动聊天服务

```bash
bash chat.sh single   # 启动单智能体对话
bash chat.sh multi    # 启动多智能体对话
```

脚本会自动：

- 激活虚拟环境
- 检查/安装 agentscope 依赖
- 加载 `.env` 环境变量
- 启动对应 Python 入口

## 常见问题

- **Python 版本不符**：请确保本地 Python 版本为 3.12
- **依赖冲突**：脚本已自动修复 mcp 相关依赖，如遇其他问题可手动 pip install
- **前端无法访问**：请确保 Node.js 安装正常，且 `npm run dev` 已启动

## 参考

- [AgentScope 官方仓库](https://github.com/agentscope-ai/agentscope)
- [AgentScope Runtime](https://github.com/agentscope-ai/agentscope-runtime)
- [AgentScope Studio](https://github.com/agentscope-ai/agentscope-studio)

---

如需进一步定制或补充内容，请联系维护者。
