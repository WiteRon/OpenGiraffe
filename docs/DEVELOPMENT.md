# Travelbook 开发文档

这份文档对应当前仓库里已经可运行的 Travelbook 版本。

当前目标很明确：

- 用单个 FastAPI 服务承载页面和 API
- 用 MySQL 保存旅行记录
- 用 `/admin` 录入数据
- 用 `/mobile` 展示 3D 地球和地点详情
- AI 能力暂时保留接口位置，但不是当前运行主线

## 1. 项目结构

项目里目前有两条线：

1. Travelbook 主线
- `main.py`
- `src/`
- `admin.html`
- `mini-trip-mobile.html`
- `static/`

2. 历史/备用内容
- `app.py`
- `src/ui/gradio_app.py`
- `backend/`
- `mini-trip.html`
- `yang-trip/`

当前开发时，优先围绕 Travelbook 主线改动，不建议再把主业务逻辑放回 `backend/` 或 Gradio 页面。

## 2. 当前架构

### 后端

- `main.py`
  启动主 FastAPI 服务

- `src/api/server.py`
  提供页面路由和数据 API

- `src/container.py`
  负责装配配置、数据库访问和可选的 chat provider

- `src/config/settings.py`
  从环境变量和 `.env` 读取配置

- `src/repositories/entry_repository.py`
  直接访问 MySQL 里的 `entries` 表

- `src/domain/entry.py`
  定义 `EntryCreate`、`EntryUpdate`、`EntryResponse`、`LocationResponse`

### 前端

- `admin.html`
  轻量录入页，用于新增旅行记录和查看最近记录

- `mini-trip-mobile.html`
  3D 地球页
  页面启动后请求 `/locations`
  点击城市后请求 `/entries`

### 数据库

主表只有一张：

- `entries`

表里关键字段：

- `destination`
- `entry_date`
- `entry_type`
- `country`
- `city`
- `lat`
- `lng`
- `title`
- `content`

地球标点依赖：

- `city`
- `lat`
- `lng`

如果这三个字段不完整，记录会保存成功，但不会出现在 `/locations`，也不会显示在地球上。

## 3. 页面与 API 的关系

### 页面路由

- `/health`
  健康检查

- `/admin`
  录入和查看最近记录

- `/mobile`
  3D 地球页面

### 数据接口

- `GET /locations`
  返回地球仪标点所需的聚合地点数据

- `GET /entries`
  返回旅行记录列表，可按 `destination/city/country/entry_date` 过滤

- `GET /entries/{id}`
  返回单条记录

- `POST /entries`
  新建记录

- `PUT /entries/{id}`
  更新记录

- `DELETE /entries/{id}`
  删除记录

### 关键数据流

1. 用户在 `/admin` 填写表单
2. 页面调用 `POST /entries`
3. 后端写入 MySQL `entries`
4. `/mobile` 页面加载时调用 `GET /locations`
5. 点击某个地点后调用 `GET /entries?...`

## 4. 本地开发

建议使用项目自己的虚拟环境，不要污染系统环境。

```bash
cd /path/to/OpenGiraffe
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

创建 `.env`：

```env
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=traveluser
DB_PASSWORD=你的数据库密码
DB_NAME=travelbook

API_KEY=
BASE_URL=https://ark.cn-beijing.volces.com/api/coding/v3
MODEL=minimax-m2.5
```

启动：

```bash
./scripts/run_api.sh
```

开发时常用页面：

- `http://127.0.0.1:8000/admin`
- `http://127.0.0.1:8000/mobile`

## 5. 已知取舍

### 1. AI 依赖已做成可选

当前线上主服务不强依赖：

- `gradio`
- `openai`

这是为了让老环境和轻量服务器先把旅行网站跑起来。

如果后面要恢复 `app.py` 或正式接 AI，再单独补相关依赖。

### 2. 经纬度暂时手填

当前 `/admin` 不会自动根据城市名补经纬度。

所以新增能在地球上显示的记录时，必须填写：

- `city`
- `lat`
- `lng`

后续最值得做的优化之一，就是自动地理编码。

### 3. 移动页的编辑能力是轻量实现

`/mobile` 里的编辑和删除使用的是浏览器原生 `prompt/confirm`。

这样实现简单、资源轻，但体验还不算最终形态。

## 6. 常见问题

### `/locations` 返回 `[]`

通常不是后端坏了，而是数据库里没有满足条件的记录。

必须至少满足：

- `city` 不为空
- `lat` 不为空
- `lng` 不为空

### `/mobile` 打开没有点

先访问：

- `/locations`

如果这里是空数组，地球不会有标点。

### `/mobile` 白屏

优先检查：

- `/static/earth.jpg`
- `/static/js/globe.gl.min.js`

其次看浏览器 Console 是否有前端报错。

### MySQL 能保存记录，但地球没有显示

最常见原因就是：

- 记录里没有 `lat/lng`

### 线上依赖安装失败

这台服务器的软件源比较老，所以当前依赖已经收敛到较低版本。

如果要继续升级依赖，先确认服务器 Python 版本和镜像源能力。

## 7. 下一步建议

当前如果继续开发，优先级建议是：

1. `/admin` 自动补经纬度
2. `/mobile` 做更友好的编辑表单，而不是 `prompt`
3. 按 `destination` 或时间筛选地点
4. 接入 AI 总结或问答

## 8. 提交建议

提交前建议至少检查：

1. `/health` 正常
2. `/admin` 可以新增中文记录
3. `/locations` 返回非空地点数据
4. `/mobile` 能看到地球
5. 点击地点后能查看、编辑、删除记录
