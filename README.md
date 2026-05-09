# 基于 LangChain 的智能扫地机器人客服系统

本项目是一个面向毕业设计场景的智能客服系统，主要围绕扫地机器人/扫拖一体机器人的使用咨询、知识库问答、环境适配建议和个性化使用报告生成展开。系统使用 Streamlit 提供聊天界面，使用 LangChain Agent 完成工具调用与推理，使用 Chroma 构建本地知识库向量检索，使用 MySQL 保存用户、设备、使用记录、聊天会话、工具调用日志和报告数据。

## 系统功能

- 智能客服问答：回答扫地机器人选购、维护、故障排查、使用建议等问题。
- RAG 知识库检索：从 `data/` 目录下的 txt/pdf 知识文件中检索参考资料并总结回答。
- 个性化报告生成：根据用户、设备和月度使用记录生成扫地机器人使用情况报告。
- 工具调用记录：记录 Agent 调用的工具、参数、结果和成功状态。
- 会话与消息保存：保存用户和智能客服的聊天会话与消息内容。
- 数据可迁移初始化：通过 `data/mysql_seed.json` 在新电脑上恢复 MySQL 演示数据。

## 技术栈

- Python
- Streamlit
- LangChain / LangGraph
- ChromaDB
- DashScope 通义千问兼容 OpenAI 接口
- MySQL
- PyMySQL

## 项目目录说明

```text
app.py                          Streamlit 前端入口
agent/react_agent.py             LangChain Agent 创建与流式执行
agent/tools/agent_tools.py       Agent 可调用工具
agent/tools/middleware.py        工具监控、日志记录、动态提示词切换
rag/vector_store.py              Chroma 向量库构建与检索器创建
rag/rag_service.py               RAG 检索总结服务
model/factory.py                 大模型与 Embedding 模型工厂
utils/db_handler.py              MySQL 连接、查询、会话/消息/日志/报告写入
utils/file_handler.py            txt/pdf 加载、文件 MD5 计算
utils/config_handler.py          YAML 配置加载
utils/prompt_loader.py           Prompt 文件加载
config/                          系统配置文件
prompts/                         主提示词、RAG 提示词、报告提示词
data/                            知识库原始资料和 MySQL 初始化 JSON
scripts/                         数据库建表、导入、导出、演示数据脚本
word/                            毕业设计文档和图片素材
```

## 完整运行链路

### 普通知识问答链路

1. 用户在 `app.py` 的 Streamlit 聊天框输入问题。
2. 页面调用 `ReactAgent.execute_stream()`。
3. Agent 根据 `prompts/main_prompt.txt` 判断是否需要工具。
4. 若需要专业知识，Agent 调用 `rag_summarize` 工具。
5. `rag_summarize` 进入 `rag/rag_service.py`。
6. RAG 服务通过 `rag/vector_store.py` 从 Chroma 向量库检索相关知识片段。
7. 检索结果和用户问题一起交给模型总结。
8. 回答以流式形式返回前端。
9. 若 MySQL 可用，系统会保存聊天消息和工具调用日志。

### 使用报告生成链路

1. 用户输入“生成我的本月扫地机器人使用报告”等请求。
2. Agent 根据主提示词识别为报告场景。
3. 按流程调用 `get_user_id`、`get_current_month`、`fill_context_for_report`、`fetch_external_data`。
4. `fill_context_for_report` 会通过中间件设置 `report=True`。
5. `report_prompt_switch` 将系统提示词切换为 `prompts/report_prompt.txt`。
6. `fetch_external_data` 优先从 MySQL 查询 `usage_records`，失败时回退到 `data/external/records.csv`。
7. Agent 结合使用记录和必要的 RAG 保养建议生成 Markdown 报告。
8. 报告返回前端，并在 MySQL 可用时保存到 `report_records`。

## 数据库说明

系统使用 MySQL 数据库 `agent_project`，包含 8 张主要数据表：

```text
users               用户表
devices             设备表
usage_records       月度使用记录表
knowledge_files     知识文件记录表
chat_sessions       聊天会话表
chat_messages       聊天消息表
tool_call_logs      Agent 工具调用日志表
report_records      报告归档表
```

建表 SQL 位于：

```text
scripts/create_usage_records_mysql.sql
```

可迁移 MySQL 初始化数据位于：

```text
data/mysql_seed.json
```

该 JSON 文件包含演示用用户、设备、使用记录、知识文件、会话、消息、工具调用日志和报告数据。另一台电脑首次运行时可以通过导入该文件恢复一致的数据库数据。

## Chroma 向量库说明

`chroma_db/` 是本地向量库目录，不提交到 Git。另一台电脑拉取项目后，需要根据 `data/` 目录下的知识文件重新构建。

`md5.text` 是本地知识文件去重记录，也不提交到 Git。运行向量库构建脚本时会自动生成。

相关配置位于：

```text
config/chroma.yml
```

知识库原始资料位于：

```text
data/
```

只要 `data/` 文件、切分参数和 Embedding 模型一致，重建出的 Chroma 知识库在系统使用上可以保持一致。

## 第一次拉取项目后的初始化步骤

以下命令以 Windows PowerShell 为例。

### 1. 安装依赖

```powershell
pip install -r requirements.txt
```

如果你使用 Anaconda 中的 Python，也可以写成：

```powershell
E:\Anaconda\python.exe -m pip install -r requirements.txt
```

### 2. 配置环境变量

系统需要 DashScope API Key 和 MySQL 密码。

```powershell
$env:DASHSCOPE_API_KEY="你的DashScope API Key"
$env:MYSQL_PASSWORD="你的MySQL root密码"
```

如果 DashScope 兼容接口地址需要自定义，可以额外设置：

```powershell
$env:DASHSCOPE_COMPATIBLE_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
```

### 3. 启动 MySQL

确保本机 MySQL 已启动，并且 `config/db.yml` 中的配置可以连接：

```yaml
mysql:
  host: localhost
  port: 3306
  database: agent_project
  user: root
  password_env: MYSQL_PASSWORD
```

### 4. 导入 MySQL 初始化数据

首次运行时，执行：

```powershell
python scripts/import_mysql_seed_json.py
```

该脚本会：

- 创建数据库 `agent_project`
- 创建 8 张系统数据表
- 清空这些表中的旧数据
- 从 `data/mysql_seed.json` 导入一致的演示数据

如果使用 Anaconda：

```powershell
E:\Anaconda\python.exe scripts/import_mysql_seed_json.py
```

### 5. 重建 Chroma 向量库

首次运行时，执行：

```powershell
python rag/vector_store.py
```

该脚本会读取 `data/` 下的 txt/pdf 知识文件，切分文本，调用 Embedding 模型，并生成本地 `chroma_db/` 向量库和 `md5.text` 去重记录。

如果使用 Anaconda：

```powershell
E:\Anaconda\python.exe rag/vector_store.py
```

### 6. 启动系统

```powershell
streamlit run app.py
```

如果使用 Anaconda：

```powershell
E:\Anaconda\Scripts\streamlit.exe run app.py
```

启动后浏览器访问 Streamlit 显示的本地地址即可。

## 常用数据脚本

### 从当前 MySQL 导出演示数据 JSON

```powershell
python scripts/export_mysql_seed_json.py
```

用于把当前 MySQL 的系统数据导出到：

```text
data/mysql_seed.json
```

### 从 JSON 导入 MySQL

```powershell
python scripts/import_mysql_seed_json.py
```

用于在新电脑或空数据库中恢复一致的数据。

### 从 CSV 和模拟规则初始化数据库

```powershell
python scripts/import_records_to_mysql.py
python scripts/seed_demo_runtime_data.py
```

这两个脚本主要用于开发阶段重新生成基础演示数据。日常迁移更推荐使用 `import_mysql_seed_json.py`。

## 运行测试建议

启动系统后，可以测试以下问题：

```text
小户型适合什么扫地机器人？
我所在的城市适合拖地模式吗？
生成我的本月扫地机器人使用报告
养宠家庭主刷缠绕严重怎么办？
机器人清扫时经常迷路怎么办？
```

这些问题可以覆盖知识库问答、天气工具、报告生成、外部使用记录查询和 RAG 保养建议等核心链路。

## 常见问题

### 1. MySQL 连接失败

检查：

- MySQL 服务是否启动
- `config/db.yml` 中的 host、port、user 是否正确
- 是否设置了 `$env:MYSQL_PASSWORD`
- root 密码是否与环境变量一致

### 2. 生成报告时查不到数据

本项目演示月份配置在：

```text
config/agent.yml
```

默认：

```yaml
demo_month: 2025-07
```

如果要临时指定月份，可以设置：

```powershell
$env:AGENT_DEMO_MONTH="2025-07"
```

### 3. RAG 问答没有知识库结果

检查是否已经执行：

```powershell
python rag/vector_store.py
```

同时确认 `chroma_db/` 是否已经生成。

### 4. 新电脑拉取项目后不要复制旧的 md5.text

`md5.text` 是本地向量库导入状态文件，不应该随仓库迁移。新电脑应该重新运行 `python rag/vector_store.py` 生成自己的 `md5.text` 和 `chroma_db/`。

### 5. 日志、缓存、向量库为什么不提交

以下目录或文件属于本地运行产物，已在 `.gitignore` 中忽略：

```text
logs/
chroma_db/
.playwright-cli/
md5.text
__pycache__/
```

它们可以在本机运行时自动生成，不需要提交到远程仓库。
