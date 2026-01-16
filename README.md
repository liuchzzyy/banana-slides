<div align="center">

<img width="256" src="https://github.com/user-attachments/assets/6f9e4cf9-912d-4faa-9d37-54fb676f547e">

*Vibe your PPT like vibing code.*

**[English](#english) | [中文](#chinese)**

<p>

[![GitHub Stars](https://img.shields.io/github/stars/Anionex/banana-slides?style=square)](https://github.com/Anionex/banana-slides/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/Anionex/banana-slides?style=square)](https://github.com/Anionex/banana-slides/network)
[![GitHub Watchers](https://img.shields.io/github/watchers/Anionex/banana-slides?style=square)](https://github.com/Anionex/banana-slides/watchers)

[![Version](https://img.shields.io/badge/version-v1.0.0-4CAF50.svg)](https://github.com/Anionex/banana-slides)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![GitHub issues](https://img.shields.io/github/issues-raw/Anionex/banana-slides)](https://github.com/Anionex/banana-slides/issues)
[![GitHub pull requests](https://img.shields.io/github/issues-pr-raw/Anionex/banana-slides)](https://github.com/Anionex/banana-slides/pulls)

</p>

<b>🍌 Banana Slides - AI-powered CLI PPT generator</b>
<br>
<b> Generate complete PPT presentations from ideas/outlines/page descriptions, auto-extract charts, achieve true "Vibe PPT"</b>
<br>
<b>🎯 Lower the barrier to PPT creation, enabling everyone to quickly create beautiful and professional presentations</b>

<br>

*If this project is useful to you, welcome to star🌟 &  fork🍴*

<br>

</p>

</div>

<a id="english"></a>

## ✨ Project Overview

Banana Slides is a command-line tool that uses AI to quickly generate professional PPT presentations.

**Core Features:**
- 🚀 **Simple & Efficient**: Generate complete PPT with a single command
- 🎨 **AI-Powered**: Based on OpenAI-compatible API, supporting various AI models
- 📊 **Smart Generation**: Automatically generates outlines, page content, and images
- 💾 **Format Support**: Export to PPTX or PDF format
- 🔧 **Flexible Config**: Custom templates, languages, page count, and more

## 🎨 Example Results

<div align="center">

| | |
|:---:|:---:|
| <img src="https://github.com/user-attachments/assets/d58ce3f7-bcec-451d-a3b9-ca3c16223644" width="500" alt="Example 3"> | <img src="https://github.com/user-attachments/assets/c64cd952-2cdf-4a92-8c34-0322cbf3de4e" width="500" alt="Example 2"> |
| **Software Development Best Practices** | **DeepSeek-V3.2 Tech Demo** |
| <img src="https://github.com/user-attachments/assets/383eb011-a167-4343-99eb-e1d0568830c7" width="500" alt="Example 4"> | <img src="https://github.com/user-attachments/assets/1a63afc9-ad05-4755-8480-fc4aa64987f1" width="500" alt="Example 1"> |
| **Smart Production Line Equipment R&D** | **Evolution of Money: From Shells to Paper** |

</div>

More examples available at <a href="https://github.com/Anionex/banana-slides/issues/2">Use Cases</a>

## 📦 Installation

### Requirements

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) - Python package manager
- OpenAI-compatible API Key

### 1. Clone Repository

```bash
git clone https://github.com/Anionex/banana-slides
cd banana-slides
```

### 2. Install Dependencies

This project uses [uv](https://github.com/astral-sh/uv) for Python dependency management.

```bash
uv sync
```

This automatically installs all dependencies from `pyproject.toml`.

### 3. Configure Environment Variables

Copy environment variable template:

```bash
cp .env.example .env
```

Edit `.env` file and configure your API key and models:

```env
# OpenAI-compatible configuration
OPENAI_API_KEY=your-api-key-here
OPENAI_API_BASE=https://api.openai.com/v1

# Or use third-party compatible services (e.g., AIHubMix)
# OPENAI_API_BASE=https://aihubmix.com/v1

# AI model configuration
TEXT_MODEL=gpt-4
IMAGE_MODEL=dall-e-3

# Output language
OUTPUT_LANGUAGE=zh

# Concurrency configuration
MAX_DESCRIPTION_WORKERS=5
MAX_IMAGE_WORKERS=8
```

**Recommended: Get API key from AIHubMix**: <a href="https://aihubmix.com/?aff=17EC">https://aihubmix.com/?aff=17EC</a>

## 🚀 Usage

### Basic Usage

**Generate PPT from an idea:**

```bash
uv run banana-slides create --prompt "Generate a PPT about climate change impact" --output climate.pptx
```

**Specify output format (PPTX or PDF):**

```bash
uv run banana-slides create --prompt "Product introduction" --format pdf --output product.pdf
```

**Use a template image to control style:**

```bash
uv run banana-slides create --prompt "Technical proposal report" --template ./template.png --output tech.pptx
```

**Specify page count and language:**

```bash
uv run banana-slides create --prompt "Market analysis report" --pages 15 --language en --output market.pptx
```

### Export Existing Projects

If you've generated a project before, you can re-export it by project ID:

```bash
# Export as PPTX
uv run banana-slides export abc123 --format pptx --output presentation.pptx

# Export as PDF
uv run banana-slides export abc123 --format pdf --output presentation.pdf
```

### Configuration Management

**View current configuration:**

```bash
uv run banana-slides config show
```

**Set configuration values:**

```bash
uv run banana-slides config set TEXT_MODEL gpt-4
uv run banana-slides config set IMAGE_MODEL dall-e-3
```

**Validate configuration and API connection:**

```bash
uv run banana-slides config validate
```

### Check Status

**View running tasks and recent projects:**

```bash
uv run banana-slides status
```

## 📋 Command Reference

### `banana-slides create`

Generate PPT from a prompt.

**Parameters:**
- `--prompt, -p` (required): PPT generation prompt (idea/description)
- `--output, -o`: Output file path (default: {project_name}.pptx)
- `--format, -f`: Output format (pptx or pdf, default: pptx)
- `--template, -t`: Template image file path (for style reference)
- `--language, -l`: Output language (zh/en/ja/auto, default: auto)
- `--pages, -n`: Number of pages (optional)

### `banana-slides export`

Export existing project to PPTX or PDF.

**Parameters:**
- `project_id` (required): Project ID
- `--format, -f`: Output format (pptx or pdf, default: pptx)
- `--output, -o`: Output file path (default: project_{id}.{format})

### `banana-slides config`

Manage configuration (settings in .env file).

**Subcommands:**

- `show`: Display current configuration
- `set KEY VALUE`: Set a configuration value
- `validate`: Validate configuration and test API connection

### `banana-slides status`

Display running tasks and recent projects.

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)

1. **Configure Environment Variables**

Edit `.env` file (refer to `.env.example`)

2. **Start Services**

```bash
docker compose up -d
```

3. **Use CLI in Container**

```bash
# Enter container
docker compose exec backend bash

# Use CLI
banana-slides create --prompt "Generate PPT" --output output.pptx
```

4. **View Logs**

```bash
docker compose logs -f backend
```

5. **Stop Services**

```bash
docker compose down
```

## 🔧 Configuration

### AI Model Configuration

Banana Slides uses OpenAI-compatible API interfaces, supporting the following services:

- **Official OpenAI**: `https://api.openai.com/v1`
- **AIHubMix** (recommended): `https://aihubmix.com/v1`
- **Other compatible services**: Any service compatible with OpenAI API format

**Environment Variables:**

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | API Key | `sk-...` |
| `OPENAI_API_BASE` | API Base URL | `https://api.openai.com/v1` |
| `TEXT_MODEL` | Text Model | `gpt-4`, `gpt-3.5-turbo` |
| `IMAGE_MODEL` | Image Model | `dall-e-3`, `dall-e-2` |

### Other Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `OUTPUT_LANGUAGE` | Output language (zh/en/ja/auto) | `zh` |
| `MAX_DESCRIPTION_WORKERS` | Description generation concurrency | `5` |
| `MAX_IMAGE_WORKERS` | Image generation concurrency | `8` |
| `DEFAULT_ASPECT_RATIO` | Image aspect ratio (16:9/4:3/1:1) | `16:9` |
| `DEFAULT_RESOLUTION` | Image resolution (2K/1K/SD) | `2K` |

## 🤝 Contributing

Contributions are welcome via [Issues](https://github.com/Anionex/banana-slides/issues) and [Pull Requests](https://github.com/Anionex/banana-slides/pulls)!

## 📄 License

This project is open-sourced under CC BY-NC-SA 4.0 license.

## 📈 Project Statistics

<a href="https://www.star-history.com/#Anionex/banana-slides&type=Timeline&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=Anionex/banana-slides&type=Timeline&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=Anionex/banana-slides&type=Timeline&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=Anionex/banana-slides&type=Timeline&legend=top-left" />
 </picture>
</a>

## 🙏 Acknowledgments

- Project contributors: [![Contributors](https://contrib.rocks/image?repo=Anionex/banana-slides)](https://github.com/Anionex/banana-slides/graphs/contributors)
- [Linux.do](https://linux.do/): A new ideal community

---

<a id="chinese"></a>

## ✨ 项目简介

Banana Slides 是一个命令行工具，通过 AI 驱动快速生成专业的 PPT 演示文稿。

**核心特性：**
- 🚀 **简单高效**：一条命令即可生成完整 PPT
- 🎨 **AI 驱动**：基于 OpenAI 兼容接口，支持多种 AI 模型
- 📊 **智能生成**：自动生成大纲、页面内容和配图
- 💾 **格式支持**：导出 PPTX 或 PDF 格式
- 🔧 **灵活配置**：支持自定义模板、语言、页数等参数

## 🎨 结果案例

<div align="center">

| | |
|:---:|:---:|
| <img src="https://github.com/user-attachments/assets/d58ce3f7-bcec-451d-a3b9-ca3c16223644" width="500" alt="案例3"> | <img src="https://github.com/user-attachments/assets/c64cd952-2cdf-4a92-8c34-0322cbf3de4e" width="500" alt="案例2"> |
| **软件开发最佳实践** | **DeepSeek-V3.2技术展示** |
| <img src="https://github.com/user-attachments/assets/383eb011-a167-4343-99eb-e1d0568830c7" width="500" alt="案例4"> | <img src="https://github.com/user-attachments/assets/1a63afc9-ad05-4755-8480-fc4aa64987f1" width="500" alt="案例1"> |
| **预制菜智能产线装备研发和产业化** | **钱的演变：从贝壳到纸币的旅程** |

</div>

更多案例可见 <a href="https://github.com/Anionex/banana-slides/issues/2">使用案例</a>

## 📦 安装

### 环境要求

- Python 3.10 或更高版本
- [uv](https://github.com/astral-sh/uv) - Python 包管理器
- OpenAI 兼容的 API Key

### 1. 克隆代码仓库

```bash
git clone https://github.com/Anionex/banana-slides
cd banana-slides
```

### 2. 安装依赖

本项目使用 [uv](https://github.com/astral-sh/uv) 管理 Python 依赖。

```bash
uv sync
```

这将根据 `pyproject.toml` 自动安装所有依赖。

### 3. 配置环境变量

复制环境变量模板：

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置你的 API 密钥和模型：

```env
# OpenAI 兼容配置
OPENAI_API_KEY=your-api-key-here
OPENAI_API_BASE=https://api.openai.com/v1

# 或者使用第三方兼容接口（如 AIHubMix）
# OPENAI_API_BASE=https://aihubmix.com/v1

# AI 模型配置
TEXT_MODEL=gpt-4
IMAGE_MODEL=dall-e-3

# 输出语言
OUTPUT_LANGUAGE=zh

# 并发配置
MAX_DESCRIPTION_WORKERS=5
MAX_IMAGE_WORKERS=8
```

**推荐使用 AIHubMix 获取 API 密钥：** <a href="https://aihubmix.com/?aff=17EC">https://aihubmix.com/?aff=17EC</a>

## 🚀 使用方法

### 基本用法

**从想法生成 PPT：**

```bash
uv run banana-slides create --prompt "生成一个关于气候变化影响的PPT" --output climate.pptx
```

**指定输出格式（PPTX 或 PDF）：**

```bash
uv run banana-slides create --prompt "产品介绍" --format pdf --output product.pdf
```

**使用模板图片控制风格：**

```bash
uv run banana-slides create --prompt "技术方案汇报" --template ./template.png --output tech.pptx
```

**指定页数和语言：**

```bash
uv run banana-slides create --prompt "市场分析报告" --pages 15 --language en --output market.pptx
```

### 导出已有项目

如果之前生成了项目，可以通过项目 ID 重新导出：

```bash
# 导出为 PPTX
uv run banana-slides export abc123 --format pptx --output presentation.pptx

# 导出为 PDF
uv run banana-slides export abc123 --format pdf --output presentation.pdf
```

### 配置管理

**查看当前配置：**

```bash
uv run banana-slides config show
```

**设置配置项：**

```bash
uv run banana-slides config set TEXT_MODEL gpt-4
uv run banana-slides config set IMAGE_MODEL dall-e-3
```

**验证配置和 API 连接：**

```bash
uv run banana-slides config validate
```

### 查看状态

**查看运行中的任务和最近项目：**

```bash
uv run banana-slides status
```

## 📋 命令详解

### `banana-slides create`

从提示词生成 PPT。

**参数：**
- `--prompt, -p` (必需): PPT 生成提示词（想法/描述）
- `--output, -o`: 输出文件路径（默认：{项目名称}.pptx）
- `--format, -f`: 输出格式（pptx 或 pdf，默认：pptx）
- `--template, -t`: 模板图片文件路径（用于风格参考）
- `--language, -l`: 输出语言（zh/en/ja/auto，默认：auto）
- `--pages, -n`: 页数（可选）

### `banana-slides export`

导出已有项目到 PPTX 或 PDF。

**参数：**
- `project_id` (必需): 项目 ID
- `--format, -f`: 输出格式（pptx 或 pdf，默认：pptx）
- `--output, -o`: 输出文件路径（默认：project_{id}.{format}）

### `banana-slides config`

管理配置（.env 文件中的设置）。

**子命令：**

- `show`: 显示当前配置
- `set KEY VALUE`: 设置配置项
- `validate`: 验证配置并测试 API 连接

### `banana-slides status`

显示运行中的任务和最近项目。

## 🔧 配置说明

### AI 模型配置

Banana Slides 使用 OpenAI 兼容的 API 接口，支持以下服务：

- **OpenAI 官方**：`https://api.openai.com/v1`
- **AIHubMix**（推荐）：`https://aihubmix.com/v1`
- **其他兼容接口**：任何兼容 OpenAI API 格式的服务

**环境变量：**

| 变量 | 说明 | 示例 |
|------|------|------|
| `OPENAI_API_KEY` | API 密钥 | `sk-...` |
| `OPENAI_API_BASE` | API 基础地址 | `https://api.openai.com/v1` |
| `TEXT_MODEL` | 文本模型 | `gpt-4`, `gpt-3.5-turbo` |
| `IMAGE_MODEL` | 图片模型 | `dall-e-3`, `dall-e-2` |

### 其他配置

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `OUTPUT_LANGUAGE` | 输出语言（zh/en/ja/auto） | `zh` |
| `MAX_DESCRIPTION_WORKERS` | 描述生成并发数 | `5` |
| `MAX_IMAGE_WORKERS` | 图片生成并发数 | `8` |
| `DEFAULT_ASPECT_RATIO` | 图片比例（16:9/4:3/1:1） | `16:9` |
| `DEFAULT_RESOLUTION` | 图片分辨率（2K/1K/SD） | `2K` |

## 📁 项目结构

```
banana-slides/
├── banana_slides/              # 核心代码
│   ├── cli.py                  # CLI 入口
│   ├── config.py               # 配置管理
│   ├── models/                 # 数据模型
│   ├── services/               # 服务层
│   ├── core/                   # 核心逻辑
│   ├── migrations/             # 数据库迁移
│   └── utils/                  # 工具函数
├── pyproject.toml              # 项目配置
├── uv.lock                     # 依赖锁定
├── .env.example                # 环境变量模板
└── README.md                   # 本文件
```

## 🏗️ 架构设计

Banana Slides 使用多智能体系统处理复杂的 PPT 生成任务：

- **Plan Agent**: 分析用户请求，创建可执行的任务列表
- **Explore Agent**: 导航代码库，查找相关模式和实现
- **Librarian Agent**: 搜索外部文档，获取最佳实践
- **Oracle Agent**: 负责架构决策和代码质量审查

此工作流支持并行处理，为 PPT 生成的不同方面提供专业支持。

## 🤝 贡献指南

欢迎通过 [Issue](https://github.com/Anionex/banana-slides/issues) 和 [Pull Request](https://github.com/Anionex/banana-slides/pulls) 为本项目贡献力量！

## 📄 许可证

本项目采用 CC BY-NC-SA 4.0 协议进行开源。

可自由用于个人学习、研究、试验、教育或非营利科研活动等非商业用途。

任何商业使用均需取得商业授权。

## 📈 项目统计

<a href="https://www.star-history.com/#Anionex/banana-slides&type=Timeline&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=Anionex/banana-slides&type=Timeline&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=Anionex/banana-slides&type=Timeline&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=Anionex/banana-slides&type=Timeline&legend=top-left" />
 </picture>
</a>

## 🙏 致谢

- 项目贡献者们：[![Contributors](https://contrib.rocks/image?repo=Anionex/banana-slides)](https://github.com/Anionex/banana-slides/graphs/contributors)
- [Linux.do](https://linux.do/): 新的理想型社区
