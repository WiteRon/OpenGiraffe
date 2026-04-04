# AI Chat App + Trip Diary

整合项目：AI 聊天应用 + 旅行手账，共享同一个 FastAPI 后端。

## 项目结构

```
private/
├── src/                    # AI 聊天应用核心代码
│   ├── agents/            # AI 代理模块
│   ├── api/               # FastAPI API 实现
│   ├── common/            # 通用工具（日志、异常）
│   ├── config/            # 配置管理
│   ├── domain/            # 领域模型
│   ├── providers/         # AI 提供商（OpenAI 兼容）
│   ├── rag/               # RAG 扩展
│   └── ui/                # Gradio UI
├── frontend/              # 前端页面
│   └── trip/              # 旅行手账
│       ├── mini-trip.html          # 桌面版 2D 地图
│       └── mini-trip-mobile.html   # 移动版 3D 地球
├── static/                # 静态资源
│   └── trip/              # 旅行手账资源
│       ├── earth.jpg
│       └── js/
├── logs/                  # 日志文件
├── app.py                 # Gradio UI 入口（独立启动）
├── main.py                # FastAPI 入口（整合所有服务）
├── requirements.txt       # 依赖
└── pyproject.toml         # 项目配置
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

服务启动后可访问：

- **旅行手账（桌面版）** → http://localhost:8000/trip
- **旅行手账（3D 移动版）** → http://localhost:8000/mobile
- **AI 聊天 API** → http://localhost:8000/v1/chat
- **健康检查** → http://localhost:8000/health
- **API 文档** → http://localhost:8000/docs

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

## 路由映射

| 路径 | 功能 |
|------|------|
| `/` | API 信息 |
| `/health` | 健康检查 |
| `/trip` | 旅行手账（桌面版） |
| `/mobile` | 旅行手账（3D 移动版） |
| `/static/*` | 静态资源 |
| `/v1/chat/completions` | AI 聊天（非流式） |
| `/v1/chat/stream` | AI 聊天（流式 SSE） |
| `/docs` | OpenAPI 文档 |
