# 易图代码生成 MPC Server

易图代码生成服务：支持识别设计图或 UI 效果图中的参数与字段，可用于生成代码提示词（Prompt）或直接提取界面内容。

## Authors

深圳市易图资讯股份有限公司

## 功能特点

- 支持图像加表实体直接生成创建 api 的提示词
- 使用 Anthropic Claude Vision、OpenAI GPT-4 Vision 或 Cloudflare Workers AI llava-1.5-7b-hf 进行图像描述
- 方便集成到 Claude Desktop、Cursor 及其他兼容 MCP 的客户端
- 支持 uvx 安装
- 支持多种图像格式（JPEG、PNG、GIF、WebP）
- 可配置主用和备用服务提供商
- 支持 Base64 及文件形式的图像输入
- 可选的 Tesseract OCR 文本提取功能

## 运行环境要求

- Python 3.8 及以上版本

[//]: # (- Tesseract OCR（可选）— 文本提取功能需要)

[//]: # (  - Windows：从 [UB-Mannheim/tesseract]&#40;https://github.com/UB-Mannheim/tesseract/wiki&#41; 下载并安装)

[//]: # (  - Linux：`sudo apt-get install tesseract-ocr`)

[//]: # (  - macOS：`brew install tesseract`)

## 安装

### 选项 1：使用 uvx（推荐用于 Trae、Claude Desktop 和 Cursor）

1. 安装 [uv](https://github.com/astral-sh/uv) 包管理器：

```bash
pip install uv
```

2. 使用 uvx 安装该包：

```bash
uvx install szetop-backend-gen-mcp
```

3. 按照“配置”部分的说明创建并配置你的环境文件

### 选项 2：从源码安装

1. 克隆仓库：

```bash
git clone http://localhost:3000/root/yt_mcp_services.git
cd szetop-trae-dev
```

2. 创建并配置你的环境文件：

```bash
cp .env.example .env
# 使用你的 API 密钥和偏好设置编辑 .env 文件
```

3. 构建项目：

```bash
pip install -e .
```

## 集成

### Claude Desktop 集成

1. 打开 **Claude** > **Settings（设置）** > **Developer（开发者）** > **Edit Config（编辑配置）** > \*
   \*claude_desktop_config.json\*\*
2. 添加带有内联环境变量的配置：

```json
{
  "mcpServers": {
    "szetop-backend-gen-mcp": {
      "command": "uvx",
      "args": ["szetop-backend-gen-mcp"]
    }
  }
}
```

### Cursor 集成

打开 Cursor Settings（设置） > MCP，并粘贴包含环境变量的命令：

```
VISION_PROVIDER=openai OPENAI_API_KEY=your-api-key OPENAI_MODEL=gpt-4o uvx szetop-mcp-dev
```

## 使用方法

### 直接运行服务端

如果使用 pip/uvx 安装：

```bash
szetop-trae-dev
```

从源码目录运行：

```bash
python -m etop_mcp_dev.server
```

使用 MCP Inspector 以开发模式启动：

```bash
npx @modelcontextprotocol/inspector szetop-trae-dev
```

### 可用工具

1. `generate_code_list_prompt`

   - **用途**：从 UI 设计图或原型图中生成构建列表页（含分页查询接口）所需的提示词（prompt），用于自动生成 Java 代码。
   - **输入**：图像文件的路径、涉及的实体类
   - **输出**：生成列表页接口的提示词
   - **适用场景**：用于具有文件系统访问权限的本地开发

2. `describe_image`

   - **用途**：分析直接上传到聊天界面的图像
   - **输入**：Base64 编码的图像数据
   - **输出**：图像的详细描述
   - **适用场景**：适用于上传至 Claude、Cursor 或其他聊天界面的图像

3. `describe_image_from_file`

   - **用途**：处理来自文件系统的本地图像文件
   - **输入**：图像文件的路径
   - **输出**：图像的详细描述
   - **适用场景**：用于具有文件系统访问权限的本地开发

4. `describe_image_from_url`
   - **用途**：分析来自网页 URL 的图像，无需手动下载
   - **输入**：公开可访问图像的 URL
   - **输出**：图像的详细描述
   - **适用场景**：适用于网页图像、截图或任何具有公共 URL 的图像
   - **注意**：使用类似浏览器的请求头以避免速率限制

### 环境配置

- `ANTHROPIC_API_KEY`：你的 Anthropic API 密钥。
- `OPENAI_API_KEY`：你的 OpenAI API 密钥。
- `CLOUDFLARE_API_KEY`：你的 Cloudflare API 密钥。
- `CLOUDFLARE_ACCOUNT_ID`：你的 Cloudflare 账户 ID。
- `VISION_PROVIDER`：主要图像识别提供商（`anthropic`、`openai` 或 `cloudflare`）。
- `FALLBACK_PROVIDER`：可选的备用提供商。
- `LOG_LEVEL`：日志级别（DEBUG、INFO、WARNING、ERROR）。
- `ENABLE_OCR`：启用 Tesseract OCR 文本识别（`true` 或 `false`）。
- `TESSERACT_CMD`：可选的 Tesseract 可执行文件路径。
- `OPENAI_MODEL`：OpenAI 模型（默认：`gpt-4o-mini`）。可使用 OpenRouter 格式指定其他模型（例如：  
  `anthropic/claude-3.5-sonnet:beta`）。
- `OPENAI_BASE_URL`：OpenAI API 的自定义基础 URL（可选）。设置为 `https://openrouter.ai/api/v1` 以使用 OpenRouter。
- `OPENAI_TIMEOUT`：OpenAI API 请求的自定义超时时间（秒， 可选）。
- `CLOUDFLARE_MODEL`：Cloudflare Workers AI 模型（默认：`@cf/llava-hf/llava-1.5-7b-hf`）。
- `CLOUDFLARE_MAX_TOKENS`：生成的最大 token 数（默认：`512`）。
- `CLOUDFLARE_TIMEOUT`：Cloudflare API 请求的超时时间（秒，默认：`60`）。

### 使用 OpenRouter

OpenRouter 允许你通过 OpenAI API 格式访问多种模型。使用 OpenRouter，请按照以下步骤操作：

1. 从 OpenRouter 获取一个 OpenAI API 密钥。
2. 在你的 `.env` 文件中，将 `OPENAI_API_KEY` 设置为你的 OpenRouter API 密钥。
3. 将 `OPENAI_BASE_URL` 设置为 `https://openrouter.ai/api/v1`。
4. 将 `OPENAI_MODEL` 设置为所需模型，使用 OpenRouter 格式（例如：`anthropic/claude-3.5-sonnet:beta`）。
5. 将 `VISION_PROVIDER` 设置为 `openai`。

### 默认模型

- Anthropic：`claude-3.5-sonnet-beta`
- OpenAI：`gpt-4o-mini`
- Cloudflare Workers AI：`@cf/llava-hf/llava-1.5-7b-hf`
- OpenRouter：在 `OPENAI_MODEL` 中使用 `anthropic/claude-3.5-sonnet:beta` 格式

## 开发

### 开发环境搭建指南

#### 设置开发环境

1. 克隆仓库：

```bash
git clone http://localhost:3000/root/yt_mcp_services.git
cd szetop-trae-dev
```

2. 使用 uv 进行设置（推荐）：

```bash
# Install uv if not installed
pip install uv

# Create virtual environment and install deps
uv venv
uv venv activate
uv pip install -e .
uv pip install -e ".[dev]"
```

```bash
# 备选 pip 设置方法：
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
# Or alternatively:
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

3. 配置环境：

```bash
cp .env.example .env
# 编辑 .env 文件，填写你的 API 密钥
```

#### VS Code / DevContainer 开发

1. 安装带有 Remote Containers 扩展的 VS Code
2. 在 VS Code 中打开项目文件夹
3. 出现提示时点击 “Reopen in Container（在容器中重新打开）”
4. devcontainer 将构建完成并打开，所有依赖已安装

#### 本地测试你的修改

1. 以开发模式运行 MCP 服务器：

```bash
# 如果还没安装 MCP Inspector，请先安装
npm install -g @modelcontextprotocol/inspector

# 使用 Inspector 启动服务器
npx @modelcontextprotocol/inspector szetop-trae-dev
```

2. Inspector 提供一个 Web 界面（通常在 http://localhost:3000），你可以在这里：

   - 发送请求给你的工具
   - 查看请求/响应日志
   - 调试实现中的问题

3. 测试特定工具：
   - 对于 `describe_image`：提供 base64 编码的图像
   - 对于 `describe_image_from_file`：提供本地图像文件路径
   - 对于 `describe_image_from_url`：提供图像的 URL
   - 对于 `generate_code_list_prompt`：提供本地图像文件路径和实体类定义

#### 集成到 Claude Desktop 进行测试

1. 临时修改 Claude Desktop 配置，使用你的开发版本：

```json
{
  "mcpServers": {
    "image-recognition": {
      "command": "python",
      "args": ["-m", "backend_gen_server.server"],
      "cwd": "/path/to/your/szetop-trae-dev",
      "env": {
        "VISION_PROVIDER": "openai",
        "OPENAI_API_KEY": "your-api-key",
        "OPENAI_MODEL": "gpt-4o"
      }
    }
  }
}
```

2. 重启 Claude Desktop 以应用更改
3. 通过上传图片或提供图片 URL 在对话中进行测试

### 运行测试

运行全部测试：

```bash
run.bat test
```

运行指定测试套件：

```bash
run.bat test server
run.bat test anthropic
run.bat test openai
```
