# OpenGiraffe / Private

个人开发仓库，整合多个小型项目到同一个 FastAPI 后端。

> 这是 `opengiraffe.me` 站点的私有项目集合，多个项目共享一个后端服务。

## 包含项目

| 项目 | 说明 |
|------|------|
| **AI Chat API** | 兼容 OpenAI 格式的 AI 聊天 API，支持流式输出 |
| **AI Chat UI** | Gradio 网页聊天界面 |
| **Trip Diary** | 旅行手账 — 环渤海湾旅行可视化 |

## 项目结构

```
private/
├── src/                     # 核心代码
│   ├── agents/              # AI 代理模块
│   ├── api/                 # FastAPI API 实现
│   ├── common/              # 通用工具（日志、异常）
│   ├── config/              # 配置管理
│   ├── domain/              # 领域模型
│   ├── providers/           # AI 提供商（OpenAI 兼容）
│   ├── rag/                 # RAG 扩展
│   └── ui/                  # Gradio UI
├── frontend/                # 前端页面
│   └── trip/                # 旅行手账
│       ├── mini-trip.html          # 桌面版 2D 地图
│       └── mini-trip-mobile.html   # 移动版 3D 地球
├── static/                  # 静态资源
│   └── trip/                # 旅行手账资源
│       ├── earth.jpg
│       └── js/globe.gl.min.js
├── logs/                    # 日志文件
├── app.py                   # Gradio UI 入口（独立启动）
├── main.py                  # FastAPI 入口（整合所有服务）
├── requirements.txt         # Python 依赖
├── pyproject.toml           # 项目配置
├── .env.example             # 环境变量示例
└── README.md                # 本文件
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 到 `.env` 并配置你的 API 密钥：

```bash
cp .env.example .env
# 编辑 .env 文件
```

### 3. 启动服务

```bash
# 启动整合 FastAPI 服务（推荐，提供所有功能）
python main.py
```

服务启动后可访问本地：

| 路径 | 功能 |
|------|------|
| `/` | API 信息 |
| `/health` | 健康检查 |
| `/trip` | 旅行手账（桌面版 2D 地图） |
| `/mobile` / `/earth` | 旅行手账（3D 移动版地球） |
| `/points/earth` | 旅行手账（公网部署路径 opengiraffe.me） |
| `/static/*` | 静态资源 |
| `/points/static/*` | 静态资源（公网部署） |
| `/v1/chat/completions` | AI 聊天（非流式） |
| `/v1/chat/stream` | AI 聊天（流式 SSE） |
| `/docs` | OpenAPI 文档 |

### 4. 单独启动 Gradio UI

如果你想单独启动 AI 聊天界面：

```bash
python app.py
```

## 功能特性

- **AI 聊天应用**：基于 FastAPI + Gradio，支持 OpenAI 兼容接口，流式输出
- **旅行手账**：两种可视化方式，记录环渤海湾旅行
  - 桌面版：Leaflet 2D 交互式地图
  - 移动版：globe.gl 3D 地球可视化
- **统一后端**：一个 FastAPI 服务同时提供 API 和静态页面，结构清晰解耦
- **支持反代部署**：可直接部署在子路径（如 `https://domain/points/*`）

## 在线体验

- 🌍 **环渤海湾旅行 3D 地球** → https://www.opengiraffe.me/points/earth
- 🗺️ **环渤海湾旅行 2D 地图** → https://www.opengiraffe.me/points/trip

## 路由映射（公网部署）

当部署在 `opengiraffe.me` 反向代理后：

| 公网路径 | 后端路径 | 功能 |
|----------|----------|------|
| `/points/earth` | `/points/earth` | 3D 地球旅行手账 |
| `/points/trip` | `/points/trip` | 2D 地图旅行手账 |
| `/points/static/*` | `/points/static/*` | 静态资源 |
| `/points/chatbox/*` | （独立 Gradio） | AI 聊天界面 |

## License

个人私有项目
