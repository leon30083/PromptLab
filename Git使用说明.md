# Git 使用说明 - PromptLab MCP Server

## 📋 项目概述

本项目是一个基于 Model Context Protocol (MCP) 的 AI 提示词管理工具，提供智能提示词优化、模板管理和多模态支持功能。

## 🗂️ 仓库结构

```
PromptLab/
├── 📁 核心文件
│   ├── promptlab_server.py      # MCP 服务器主程序
│   ├── promptlab_client.py      # 客户端示例
│   ├── requirements.txt         # Python 依赖包
│   └── pyproject.toml          # 项目配置
│
├── 📁 配置文件
│   ├── mcp.json                # 通用 MCP 配置
│   ├── mcp_trae.json           # Trae AI 专用配置
│   └── advanced_prompts.json   # 高级提示词模板
│
├── 📁 启动脚本
│   ├── start_mcp_server.py     # 跨平台启动脚本（推荐）
│   ├── start_promptlab_mcp.ps1 # PowerShell 启动脚本
│   ├── start_promptlab_mcp.bat # 批处理启动脚本
│   ├── setup_and_start.py      # 自动安装和启动
│   └── test_mcp.py             # MCP 服务器测试
│
├── 📁 工具脚本
│   ├── register_prompts.py     # 注册示例提示词
│   └── start_mcp.py           # 简单启动脚本
│
├── 📁 文档
│   ├── README.md               # 项目说明
│   ├── 使用说明.md             # 详细使用说明
│   ├── 快速启动指南.md         # 快速上手指南
│   ├── 启动脚本说明.md         # 启动脚本对比
│   ├── terminal_management_rules.md # 终端管理规则
│   └── 测试流程.md             # 测试流程说明
│
└── 📁 其他
    ├── .gitignore              # Git 忽略文件
    ├── LICENSE                 # 开源许可证
    ├── promptlab_architecture.png # 架构图
    └── venv/                   # 虚拟环境（不提交）
```

## 🚀 Git 工作流程

### 初始设置

```bash
# 克隆仓库
git clone <repository-url>
cd PromptLab

# 配置用户信息（首次使用）
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

### 日常开发流程

#### 1. 检查状态
```bash
# 查看当前状态
git status

# 查看文件差异
git diff
```

#### 2. 添加文件
```bash
# 添加特定文件
git add filename.py

# 添加所有修改的文件
git add .

# 添加所有 Python 文件
git add *.py

# 添加文档文件
git add *.md
```

#### 3. 提交更改
```bash
# 提交更改（推荐使用描述性消息）
git commit -m "feat: 添加新的启动脚本和使用说明"

# 或者使用详细提交消息
git commit -m "feat: 添加跨平台启动脚本

- 新增 start_mcp_server.py 跨平台启动脚本
- 添加 PowerShell 和批处理启动脚本
- 创建详细的中文使用说明文档
- 优化错误处理和用户体验"
```

#### 4. 推送到远程仓库
```bash
# 推送到主分支
git push origin main

# 或推送到其他分支
git push origin feature-branch
```

### 分支管理

#### 创建和切换分支
```bash
# 创建新分支
git branch feature/new-feature

# 切换到分支
git checkout feature/new-feature

# 创建并切换到新分支（一步完成）
git checkout -b feature/new-feature
```

#### 合并分支
```bash
# 切换到主分支
git checkout main

# 合并功能分支
git merge feature/new-feature

# 删除已合并的分支
git branch -d feature/new-feature
```

## 📝 提交消息规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

### 提交类型
- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码格式化（不影响功能）
- `refactor`: 代码重构
- `test`: 添加或修改测试
- `chore`: 构建过程或辅助工具的变动

### 示例
```bash
# 新功能
git commit -m "feat: 添加 MLflow 集成支持"

# 修复 bug
git commit -m "fix: 修复 numpy 版本兼容性问题"

# 文档更新
git commit -m "docs: 更新安装说明和故障排除指南"

# 代码重构
git commit -m "refactor: 优化启动脚本的错误处理逻辑"

# 配置更改
git commit -m "chore: 更新依赖包版本"
```

## 🔍 .gitignore 配置

项目已配置 `.gitignore` 文件，自动忽略以下内容：

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# 虚拟环境
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# 操作系统
.DS_Store
Thumbs.db

# 日志文件
*.log

# 环境变量
.env
.env.local
.env.*.local

# MLflow
mlruns/
mlartifacts/

# 临时文件
*.tmp
*.temp
*.bak
```

## 🔄 常用 Git 命令

### 查看历史
```bash
# 查看提交历史
git log

# 查看简洁的提交历史
git log --oneline

# 查看图形化分支历史
git log --graph --oneline --all
```

### 撤销操作
```bash
# 撤销工作区的修改
git checkout -- filename.py

# 撤销暂存区的文件
git reset HEAD filename.py

# 撤销最后一次提交（保留修改）
git reset --soft HEAD~1

# 撤销最后一次提交（丢弃修改）
git reset --hard HEAD~1
```

### 远程仓库操作
```bash
# 查看远程仓库
git remote -v

# 添加远程仓库
git remote add origin <repository-url>

# 获取远程更新
git fetch origin

# 拉取并合并远程更新
git pull origin main
```

## 🚨 注意事项

### 不要提交的文件
- **虚拟环境** (`venv/`, `env/`)
- **编译文件** (`__pycache__/`, `*.pyc`)
- **敏感信息** (API 密钥、密码)
- **大型二进制文件** (除非必要)
- **IDE 配置文件** (`.vscode/`, `.idea/`)
- **操作系统文件** (`.DS_Store`, `Thumbs.db`)

### 最佳实践
1. **频繁提交**: 小而频繁的提交比大而稀少的提交更好
2. **描述性消息**: 提交消息要清楚描述做了什么
3. **测试后提交**: 确保代码能正常运行再提交
4. **使用分支**: 为新功能创建独立分支
5. **定期同步**: 定期从远程仓库拉取更新

## 🔧 Git 配置优化

### 全局配置
```bash
# 设置默认编辑器
git config --global core.editor "code --wait"

# 设置默认分支名
git config --global init.defaultBranch main

# 启用颜色输出
git config --global color.ui auto

# 设置推送策略
git config --global push.default simple
```

### 别名设置
```bash
# 常用别名
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.unstage 'reset HEAD --'
git config --global alias.last 'log -1 HEAD'
git config --global alias.visual '!gitk'
```

## 📞 故障排除

### 常见问题

#### 1. 推送被拒绝
```bash
# 先拉取远程更新
git pull origin main
# 解决冲突后再推送
git push origin main
```

#### 2. 合并冲突
```bash
# 查看冲突文件
git status
# 手动编辑冲突文件
# 标记冲突已解决
git add conflicted-file.py
# 完成合并
git commit
```

#### 3. 误提交敏感信息
```bash
# 从历史中完全删除文件
git filter-branch --force --index-filter \
'git rm --cached --ignore-unmatch sensitive-file.txt' \
--prune-empty --tag-name-filter cat -- --all
```

### 获取帮助
```bash
# 查看命令帮助
git help <command>
git <command> --help

# 例如
git help commit
git push --help
```

---

**💡 提示**: 定期备份重要代码，使用 Git 进行版本控制是最佳实践！