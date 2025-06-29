# 终端管理规则 - Terminal Management Rules

## 问题描述 (Problem Description)

在使用AI助手进行项目开发时，当需要启动持续运行的服务器（如MLflow、Web服务器等）时，AI助手只能同时在一个终端运行命令。如果AI助手启动了需要持续运行的服务，该终端将被占用，无法执行后续命令。

## 解决方案 (Solution)

### 规则1：持续服务的处理方式

**当需要启动持续运行的服务时，AI助手应该：**

1. **不直接启动服务** - 避免使用 `blocking=false` 启动持续服务
2. **提供启动命令** - 明确告知用户需要手动运行的命令
3. **指导用户操作** - 提示用户在专门的终端窗口中运行
4. **检查服务状态** - 使用适当的方法验证服务是否正常运行

### 规则2：命令分类

#### 需要用户手动启动的服务类型：
- **Web服务器** (如 `mlflow server`, `uvicorn`, `flask run`)
- **数据库服务** (如 `redis-server`, `mongodb`)
- **开发服务器** (如 `npm start`, `python manage.py runserver`)
- **监控服务** (如 `prometheus`, `grafana-server`)
- **消息队列** (如 `rabbitmq-server`, `kafka`)

#### AI助手可以直接运行的命令：
- **短期任务** (如安装依赖、文件操作、测试)
- **一次性脚本** (如数据迁移、初始化脚本)
- **状态检查** (如 `curl` 健康检查、`ps` 进程查看)

### 规则3：标准操作流程

#### 步骤1：识别服务类型
```
如果命令需要持续运行 → 使用手动启动流程
如果命令是短期任务 → AI助手直接执行
```

#### 步骤2：手动启动流程
```markdown
## 🚀 启动 [服务名称]

请在**新的终端窗口**中运行以下命令：

```bash
[具体命令]
```

**启动步骤：**
1. 打开新的终端/命令提示符窗口
2. 导航到项目目录：`cd [项目路径]`
3. 激活虚拟环境（如需要）：`[激活命令]`
4. 运行上述命令
5. 保持该终端窗口打开

**验证服务状态：**
- 访问：[服务URL]
- 或运行：[状态检查命令]
```

#### 步骤3：状态验证
AI助手使用以下方法检查服务状态：
- HTTP请求检查 (`curl` 或类似工具)
- 进程检查 (`ps` 或 `tasklist`)
- 端口检查 (`netstat` 或 `ss`)
- 日志文件检查

### 规则4：实施示例

#### ❌ 错误做法：
```python
# AI助手直接启动服务（会占用终端）
run_command("mlflow", ["server", "--host", "127.0.0.1"], blocking=False)
```

#### ✅ 正确做法：
```markdown
## 🚀 启动 MLflow 服务器

请在**新的终端窗口**中运行以下命令：

```bash
mlflow server --host 127.0.0.1 --port 5000
```

**启动步骤：**
1. 打开新的终端窗口
2. 导航到项目目录：`cd e:\User\MCP\PromptLab`
3. 激活虚拟环境：`.\venv\Scripts\Activate.ps1`
4. 运行上述命令
5. 保持终端窗口打开

**验证服务：**
访问 http://127.0.0.1:5000 确认服务正常运行
```

然后AI助手执行状态检查：
```python
# 检查服务状态
run_command("curl", ["-s", "http://127.0.0.1:5000/health"], blocking=True)
```

### 规则5：状态检查方法

#### Web服务检查：
```bash
# HTTP状态检查
curl -s -o /dev/null -w "%{http_code}" http://localhost:5000

# 或使用Python
python -c "import requests; print(requests.get('http://localhost:5000').status_code)"
```

#### 进程检查：
```bash
# Windows
tasklist | findstr "mlflow"

# Linux/Mac
ps aux | grep mlflow
```

#### 端口检查：
```bash
# Windows
netstat -an | findstr :5000

# Linux/Mac
ss -tlnp | grep :5000
```

### 规则6：用户指导模板

```markdown
## 🔧 多终端工作流程

为了正常运行项目，您需要同时使用多个终端窗口：

### 终端1：[服务名称]
```bash
[启动命令]
```
**状态：** 保持运行，不要关闭

### 终端2：AI助手操作
```bash
[后续命令]
```
**状态：** 用于AI助手执行其他任务

### 验证所有服务正常：
- [ ] [服务1] 运行在 [URL/端口]
- [ ] [服务2] 运行在 [URL/端口]
- [ ] 所有依赖服务已启动
```

## 实施要点 (Implementation Points)

1. **明确区分** 持续服务和短期任务
2. **提供完整指导** 包括路径、环境、验证步骤
3. **使用状态检查** 确认服务正常运行
4. **保持一致性** 所有类似服务使用相同的处理方式
5. **用户友好** 提供清晰的步骤和验证方法

## 适用场景 (Use Cases)

- MCP工具开发和部署
- Web应用开发
- 微服务架构项目
- 数据科学项目（Jupyter、MLflow等）
- 任何需要多个持续服务的项目

---

**注意：** 此规则确保AI助手能够有效管理多个服务，同时保持终端可用性，提高开发效率。